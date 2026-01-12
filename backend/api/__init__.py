# backend/api/__init__.py

from fastapi import APIRouter
from backend.api.routes import scrape, process, agents, scheduler_control, reminder, auth

api_router = APIRouter(prefix="/api")

# ✅ Register all route modules
api_router.include_router(auth.router, tags=["Authentication"])  
api_router.include_router(agents.router, tags=["Agents"])
api_router.include_router(scrape.router, tags=["Scraping"])
api_router.include_router(process.router, tags=["Processing"])
api_router.include_router(reminder.router, tags=["Reminders"])
api_router.include_router(scheduler_control.router, tags=["Scheduler"])