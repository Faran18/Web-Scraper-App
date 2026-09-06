# backend/api/routes/scrape.py

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel, HttpUrl
import asyncio
import hashlib
import uuid
from datetime import datetime
from backend.utils.playwright_scraper import scrape_website, extract_text_from_html
from backend.utils.multi_page_scraper import scrape_multiple_pages
from backend.core.vector_db import store_scraped_data
from backend.models.agent import Agent, ScrapeConfig
from backend.models.user import User
from backend.core.auth import get_current_user
from backend.core.limiter import limiter

router = APIRouter()

# GLOBAL guard: only one scrape job runs at a time, system-wide -- not
# per-agent. CPU on this box is a single shared resource (Render free
# tier), so two scrapes for two *different* agents running "concurrently"
# is exactly as harmful as two for the same one.
#
# IMPORTANT: this is a plain bool, not an asyncio.Lock(). It is set True
# right before a background thread starts, and set False ONLY inside that
# thread's own `finally` block once the real scraping work has actually
# finished. This is deliberate: Python threads cannot be forcibly killed,
# so if an outer async timeout gives up "waiting" on a stuck scrape, the
# real thread keeps running in the background regardless. An asyncio.Lock
# tied to the *waiting* coroutine would release the moment that coroutine
# gives up -- freeing up "capacity" for a second scrape to start while the
# first one is still genuinely running underneath, which is exactly the
# bug that caused two Chromium instances to run at once earlier. This flag
# only reflects whether the real work is actually still in flight.
_scrape_running = False

# In-memory job status store, keyed by a job_id we hand back to the client.
# Safe because this service runs WEB_CONCURRENCY=1 (single process) -- if
# this is ever scaled to multiple workers/instances, this needs to move to
# a shared store (e.g. Redis) instead.
_scrape_jobs: dict[str, dict] = {}


class ScrapeRequest(BaseModel):
    """Request body for scraping"""
    agent_id: str
    url: HttpUrl
    css_selector: str | None = None
    xpath: str | None = None
    multi_page: bool = False
    max_pages: int = 20
    auto_scrape: bool = False
    scrape_interval_hours: int = 24


def _sync_scrape_worker(job_id: str, data: ScrapeRequest):
    """
    The actual scrape work. Runs synchronously inside a background thread
    (via asyncio.to_thread) -- this function's own `finally` is the ONLY
    place `_scrape_running` gets cleared, guaranteeing the global guard
    stays held for as long as the real work is genuinely running, no
    matter what the async layer above decides to report to the user in
    the meantime.
    """
    global _scrape_running
    try:
        agent = Agent.get_by_id(data.agent_id)
        if not agent:
            raise RuntimeError(f"Agent not found: {data.agent_id}")

        print(f"🤖 Scraping for agent: {agent.name}")
        print(f"🔗 URL: {data.url}")
        print(f"📄 Multi-page: {data.multi_page}")

        existing_configs = ScrapeConfig.get_by_agent(data.agent_id)
        config_exists = any(c.url == str(data.url) for c in existing_configs)

        if not config_exists:
            is_primary = len(existing_configs) == 0
            config = ScrapeConfig.create(
                agent_id=data.agent_id,
                url=str(data.url),
                css_selector=data.css_selector,
                xpath=data.xpath,
                is_primary=is_primary,
                auto_scrape=data.auto_scrape,
                scrape_interval_hours=data.scrape_interval_hours
            )
            print(f"💾 Created scrape config (auto: {data.auto_scrape}, interval: {data.scrape_interval_hours}h)")
        else:
            config = next(c for c in existing_configs if c.url == str(data.url))
            config.update(
                auto_scrape=data.auto_scrape,
                scrape_interval_hours=data.scrape_interval_hours
            )

        pages_scraped = 1
        if data.multi_page:
            print(f"🕷️ Starting multi-page crawl (max: {data.max_pages} pages)")
            result = scrape_multiple_pages(
                str(data.url),
                data.max_pages,
                data.css_selector,
                data.xpath
            )
            combined_text = "\n\n=== PAGE SEPARATOR ===\n\n".join([
                f"[{p['title']}]\n{p['text']}" for p in result['pages']
            ])
            pages_scraped = result['total_pages']
            print(f"✅ Scraped {result['total_pages']} pages, {result['total_chars']:,} chars")
        else:
            html_content = scrape_website(str(data.url))
            combined_text = extract_text_from_html(
                html_content,
                css_selector=data.css_selector,
                xpath=data.xpath
            )
            print(f"📄 Extracted {len(combined_text)} characters")

        if not combined_text.strip():
            raise RuntimeError("No text extracted")

        content_hash = hashlib.sha256(combined_text.encode()).hexdigest()

        vector_result = store_scraped_data(
            agent_id=agent.agent_id,
            url=str(data.url),
            text=combined_text,
            css_selector=data.css_selector,
            xpath=data.xpath
        )

        config.update(last_content_hash=content_hash)
        agent.update(
            chunks_count=vector_result["chunks"],
            last_scraped=datetime.now().isoformat()
        )

        print(f"✅ Scraping complete")

        _scrape_jobs[job_id].update({
            "status": "done",
            "result": {
                "message": "Scraping successful",
                "agent": agent.to_dict(),
                "vector_db_result": vector_result,
                "pages_scraped": pages_scraped
            }
        })

    except Exception as e:
        print(f"❌ Error: {e}")
        _scrape_jobs[job_id].update({
            "status": "error",
            "detail": str(e)
        })
    finally:
        # This is the ONLY place this flag is cleared, and it only runs
        # once the real work (success or failure) has truly finished --
        # not when some outer async timeout stops waiting on it.
        _scrape_running = False


async def _run_scrape_job(job_id: str, data: ScrapeRequest):
    """
    Thin async wrapper: hands the real work off to a background thread.
    Deliberately has NO asyncio.wait_for/timeout here -- see the big
    comment on _scrape_running above for why that caused a real bug.
    The per-page timeout inside scrape_multiple_pages (20s) is what
    actually bounds how long a bad page can stall the crawl; there's no
    safe way to bound the *whole* job from the outside without either
    genuinely killing the thread (not possible in Python) or creating
    the same "reports done before it's actually done" bug again.
    """
    await asyncio.to_thread(_sync_scrape_worker, job_id, data)


@router.post("/scrape")
@limiter.limit("5/minute")
async def scrape_and_store(
    request: Request,
    data: ScrapeRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    """
    Kick off a scrape as a background job and return immediately.
    Poll GET /api/scrape/status/{job_id} for progress/result.
    """
    global _scrape_running

    agent = Agent.get_by_id(data.agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {data.agent_id}")

    if agent.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if _scrape_running:
        raise HTTPException(
            status_code=409,
            detail="A scrape is already running. Please wait for it to finish before starting another."
        )

    _scrape_running = True  # claimed here, released only inside _sync_scrape_worker's finally

    job_id = str(uuid.uuid4())
    _scrape_jobs[job_id] = {
        "status": "queued",
        "agent_id": data.agent_id,
        "detail": None,
        "result": None,
        "started_at": datetime.now().isoformat()
    }

    background_tasks.add_task(_run_scrape_job, job_id, data)

    return {"job_id": job_id, "status": "queued"}


@router.get("/scrape/status/{job_id}")
async def get_scrape_status(job_id: str, user: User = Depends(get_current_user)):
    """Poll this to find out when a background scrape job finishes."""
    job = _scrape_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    agent = Agent.get_by_id(job["agent_id"])
    if not agent or agent.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return job


@router.post("/scrape/refresh/{agent_id}")
@limiter.limit("5/minute")
async def refresh_agent_data(
    request: Request,
    agent_id: str,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    """Re-scrape primary URL for an agent"""
    agent = Agent.get_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if agent.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    configs = ScrapeConfig.get_by_agent(agent_id)
    primary = next((c for c in configs if c.is_primary), None)

    if not primary:
        raise HTTPException(status_code=404, detail="No scrape config found")

    return await scrape_and_store(
        request,
        ScrapeRequest(
            agent_id=agent_id,
            url=primary.url,
            css_selector=primary.css_selector,
            xpath=primary.xpath,
            multi_page=False,
            auto_scrape=primary.auto_scrape,
            scrape_interval_hours=primary.scrape_interval_hours
        ),
        background_tasks,
        user=user
    )