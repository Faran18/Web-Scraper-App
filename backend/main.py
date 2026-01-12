# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import api_router
from backend.core.scheduler import start_scheduler, stop_scheduler
from backend.models import init_database
from backend.models.user import Session  # ✅ NEW

app = FastAPI(
    title="WebScraper AI Agent API",
    description="Multi-agent web scraping with LLM processing, auto-monitoring, and email notifications",
    version="2.0.0"
)

# ✅ CORS middleware - Must be added BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


# ✅ Startup event - Initialize database and scheduler
@app.on_event("startup")
def startup_event():
    """Initialize the application on startup"""
    print("\n" + "="*60)
    print("🚀 Starting WebScraper AI Agent API")
    print("="*60)
    
    # Initialize database tables
    print("\n📦 Initializing database...")
    init_database()
    
    # ✅ NEW: Clean up expired sessions
    print("🧹 Cleaning up expired sessions...")
    expired = Session.cleanup_expired()
    if expired > 0:
        print(f"   Removed {expired} expired session(s)")
    
    # Start background scheduler
    print("\n⏰ Starting scheduler...")
    start_scheduler()
    
    print("\n✅ Application started successfully!")
    print("📖 API Documentation: http://127.0.0.1:8000/docs")
    print("="*60 + "\n")


# ✅ Shutdown event - Clean up resources
@app.on_event("shutdown")
def shutdown_event():
    """Clean up on application shutdown"""
    print("\n🛑 Shutting down application...")
    stop_scheduler()
    print("✅ Application shutdown complete\n")


# Root endpoint
@app.get("/")
def root():
    """API health check"""
    return {
        "message": "WebScraper AI Agent API is running!",
        "version": "2.0.0",
        "docs": "/docs",
        "features": [
            "User authentication",  # ✅ NEW
            "Multi-agent management",
            "Multi-page web scraping",
            "AI-powered chat interface",
            "Auto-monitoring with custom intervals",
            "Change detection with AI summaries",
            "Email notifications"
        ]
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """Detailed health check"""
    from backend.core.scheduler import scheduler
    from backend.models.agent import Agent
    
    try:
        agents = Agent.get_all()
        active_agents = [a for a in agents if a.status == 'active']
        
        return {
            "status": "healthy",
            "database": "connected",
            "scheduler": "running" if scheduler.running else "stopped",
            "scheduled_jobs": len(scheduler.get_jobs()) if scheduler.running else 0,
            "total_agents": len(agents),
            "active_agents": len(active_agents)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }