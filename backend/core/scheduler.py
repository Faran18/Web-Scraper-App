# backend/core/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import hashlib
from backend.models.agent import Agent, ScrapeConfig, ChangeHistory
from backend.utils.playwright_scraper import scrape_website, extract_text_from_html
from backend.core.vector_db import store_scraped_data
from backend.utils.email_sender import send_change_notification
from backend.core.llm_service import run_llm
from backend.models.agent import Subscription

scheduler = BackgroundScheduler()


# ========================================
# AGENT SCRAPING FUNCTIONS
# ========================================

def scrape_and_check_changes(config: ScrapeConfig):
    """
    Scrape a URL and check if content has changed.
    If changed, update vector DB and notify subscribers.
    """
    try:
        print(f"\n⏰ Scheduled scrape for agent {config.agent_id}")
        print(f"🔗 URL: {config.url}")
        
        agent = Agent.get_by_id(config.agent_id)
        if not agent or agent.status != 'active':
            print(f"⚠️ Agent inactive or not found, skipping")
            return
        
        # Scrape the URL
        html_content = scrape_website(config.url)
        new_text = extract_text_from_html(
            html_content,
            css_selector=config.css_selector,
            xpath=config.xpath
        )
        
        if not new_text.strip():
            print(f"⚠️ No content extracted")
            return
        
        # Calculate new content hash
        new_hash = hashlib.sha256(new_text.encode()).hexdigest()
        
        # Check if content changed
        if config.last_content_hash and config.last_content_hash != new_hash:
            print(f"🔔 Content changed detected!")
            
            # Get old content from vector DB for comparison
            from backend.core.vector_db import get_agent_collection
            collection = get_agent_collection(config.agent_id)
            old_data = collection.get(limit=1)
            old_text = old_data['documents'][0][0] if old_data['documents'] else ""
            
            # Generate change summary using LLM
            change_summary = generate_change_summary(old_text[:1500], new_text[:1500])
            
            # Store change history
            ChangeHistory.create(
                agent_id=config.agent_id,
                config_id=config.config_id,
                old_content=old_text,
                new_content=new_text,
                change_summary=change_summary
            )
            
            # Update vector DB with new content
            store_scraped_data(
                agent_id=config.agent_id,
                url=config.url,
                text=new_text,
                css_selector=config.css_selector,
                xpath=config.xpath
            )
            
            # Update config with new hash
            config.update(last_content_hash=new_hash)
            
            # Update agent
            agent.update(last_scraped=datetime.now().isoformat())
            
            # Notify subscribers
            subscribers = Subscription.get_by_agent(config.agent_id, active_only=True)
            
            if subscribers:
                print(f"📧 Notifying {len(subscribers)} subscribers")
                for sub in subscribers:
                    try:
                        send_change_notification(
                            email=sub.email,
                            agent_name=agent.name,
                            url=config.url,
                            change_summary=change_summary
                        )
                    except Exception as e:
                        print(f"❌ Failed to send email to {sub.email}: {e}")
            
            print(f"✅ Update complete")
        else:
            print(f"✓ No changes detected")
            config.update(last_content_hash=new_hash)
            agent.update(last_scraped=datetime.now().isoformat())
        
    except Exception as e:
        print(f"❌ Error during scheduled scrape: {e}")


def schedule_scrape_config(config: ScrapeConfig):
    """Schedule a scrape config for periodic execution"""
    job_id = f"scrape_{config.config_id}"
    
    # Remove existing job if any
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    
    # Add new job with dynamic interval
    scheduler.add_job(
        func=scrape_and_check_changes,
        trigger=IntervalTrigger(hours=config.scrape_interval_hours),
        args=[config],
        id=job_id,
        name=f"Scrape {config.url}",
        replace_existing=True
    )
    
    print(f"⏰ Scheduled: {config.url} (every {config.scrape_interval_hours}h)")


# ========================================
# REMINDER SCRAPING FUNCTIONS
# ========================================

def scrape_and_check_reminder(reminder):
    """
    Scrape a reminder URL and check if content has changed.
    If changed, send email notification.
    """
    from backend.models.reminder import Reminder, ReminderHistory
    
    try:
        print(f"\n⏰ Scheduled reminder check for {reminder.reminder_id}")
        print(f"🔗 URL: {reminder.url}")
        
        # Scrape the URL
        html_content = scrape_website(reminder.url)
        new_text = extract_text_from_html(
            html_content,
            css_selector=reminder.css_selector,
            xpath=reminder.xpath
        )
        
        if not new_text.strip():
            print(f"⚠️ No content extracted")
            return {"status": "no_content"}
        
        # Calculate new content hash
        new_hash = hashlib.sha256(new_text.encode()).hexdigest()
        
        # Check if content changed
        if reminder.last_content_hash and reminder.last_content_hash != new_hash:
            print(f"🔔 Content changed detected!")
            
            # Get old content from history for comparison
            old_history = ReminderHistory.get_by_reminder(reminder.reminder_id, limit=1)
            old_text = old_history[0].new_content_preview if old_history else ""
            
            # Generate change summary using LLM
            change_summary = generate_change_summary(old_text, new_text[:1500])
            
            # Store change history
            ReminderHistory.create(
                reminder_id=reminder.reminder_id,
                old_content=old_text,
                new_content=new_text[:500],
                change_summary=change_summary
            )
            
            # Update reminder with new hash
            reminder.update(
                last_content_hash=new_hash,
                last_scraped=datetime.now().isoformat()
            )
            
            # Send notification email
            try:
                send_change_notification(
                    email=reminder.email,
                    agent_name=f"Reminder: {reminder.url}",
                    url=reminder.url,
                    change_summary=change_summary
                )
                print(f"📧 Notification sent to {reminder.email}")
            except Exception as e:
                print(f"❌ Failed to send email: {e}")
            
            print(f"✅ Update complete")
            return {"status": "changed", "summary": change_summary}
        else:
            print(f"✓ No changes detected")
            reminder.update(
                last_content_hash=new_hash,
                last_scraped=datetime.now().isoformat()
            )
            return {"status": "no_change"}
        
    except Exception as e:
        print(f"❌ Error during reminder check: {e}")
        return {"status": "error", "error": str(e)}


def schedule_reminder(reminder):
    """Schedule a reminder for periodic execution"""
    job_id = f"reminder_{reminder.reminder_id}"
    
    # Remove existing job if any
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    
    # Add new job
    scheduler.add_job(
        func=scrape_and_check_reminder,
        trigger=IntervalTrigger(hours=reminder.interval_hours),
        args=[reminder],
        id=job_id,
        name=f"Reminder: {reminder.url}",
        replace_existing=True
    )
    
    print(f"⏰ Scheduled reminder: {reminder.url} (every {reminder.interval_hours}h)")


# ========================================
# SHARED FUNCTIONS
# ========================================

def generate_change_summary(old_content: str, new_content: str) -> str:
    """Use LLM to generate a summary of what changed"""
    try:
        prompt = f"""Compare these two versions of website content and summarize what changed.

OLD VERSION:
{old_content}

NEW VERSION:
{new_content}

Provide a concise summary (2-3 sentences) of the main changes. Focus on:
- New information added
- Information removed or changed
- Major updates

Summary:"""
        
        summary = run_llm(prompt, max_new_tokens=150)
        return summary.strip()
    except Exception as e:
        print(f"⚠️ Could not generate change summary: {e}")
        return "Content has been updated. Please check the website for details."


# ========================================
# SCHEDULER CONTROL
# ========================================

def start_scheduler():
    """Initialize and start the scheduler"""
    from backend.models.reminder import Reminder
    
    if scheduler.running:
        print("⚠️ Scheduler already running")
        return
    
    print("📅 Starting scheduler...")
    
    # Load all auto-scrape configs (agents)
    configs = ScrapeConfig.get_all_auto_scrape()
    print(f"📋 Found {len(configs)} auto-scrape configurations")
    
    for config in configs:
        agent = Agent.get_by_id(config.agent_id)
        if agent and agent.status == 'active':
            schedule_scrape_config(config)
    
    # Load all active reminders
    try:
        reminders = Reminder.get_all_active()
        print(f"📋 Found {len(reminders)} active reminders")
        
        for reminder in reminders:
            schedule_reminder(reminder)
    except Exception as e:
        print(f"⚠️ Could not load reminders: {e}")
    
    scheduler.start()
    print("✅ Scheduler started")


def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Scheduler stopped")


def get_scheduled_jobs():
    """Get list of all scheduled jobs"""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'job_id': job.id,
            'name': job.name,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None
        })
    return jobs