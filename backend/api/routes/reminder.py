# backend/api/routes/reminder.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, EmailStr
import asyncio
import hashlib
from datetime import datetime
from backend.models.reminder import Reminder, ReminderHistory
from backend.utils.playwright_scraper import scrape_website, extract_text_from_html
from backend.core.scheduler import schedule_reminder

router = APIRouter()


class CreateReminderRequest(BaseModel):
    """Request body for creating a reminder"""
    url: HttpUrl
    email: EmailStr
    interval_hours: int = 24
    css_selector: str | None = None
    xpath: str | None = None


class UpdateReminderRequest(BaseModel):
    """Request body for updating a reminder"""
    url: HttpUrl | None = None
    email: EmailStr | None = None
    interval_hours: int | None = None
    css_selector: str | None = None
    xpath: str | None = None


@router.post("/reminders/create")
async def create_reminder(data: CreateReminderRequest):
    """
    Create a new standalone reminder.
    This will monitor the URL and send email notifications on changes.
    """
    try:
        # Validate interval
        if data.interval_hours < 1:
            raise HTTPException(
                status_code=400,
                detail="Interval must be at least 1 hour"
            )
        
        # Create reminder
        reminder = Reminder.create(
            url=str(data.url),
            email=data.email,
            interval_hours=data.interval_hours,
            css_selector=data.css_selector,
            xpath=data.xpath
        )
        
        print(f"✅ Created reminder: {reminder.reminder_id}")
        print(f"   URL: {reminder.url}")
        print(f"   Email: {reminder.email}")
        print(f"   Interval: {reminder.interval_hours}h")
        
        # Do initial scrape and store baseline
        try:
            html_content = await asyncio.to_thread(scrape_website, str(data.url))
            text = extract_text_from_html(
                html_content,
                css_selector=data.css_selector,
                xpath=data.xpath
            )
            
            if text:
                content_hash = hashlib.sha256(text.encode()).hexdigest()
                
                # ✅ Store initial content as baseline in history
                ReminderHistory.create(
                    reminder_id=reminder.reminder_id,
                    old_content="",  # No previous content
                    new_content=text[:500],  # Store preview
                    change_summary="Initial scrape - baseline created"
                )
                
                reminder.update(
                    last_content_hash=content_hash,
                    last_scraped=datetime.now().isoformat()
                )
                print(f"✅ Initial scrape completed, baseline saved")
        except Exception as e:
            print(f"⚠️ Initial scrape failed: {e}")
        
        # Schedule for monitoring
        schedule_reminder(reminder)
        
        # ✅ Send confirmation email
        try:
            from backend.utils.email_sender import send_reminder_confirmation
            send_reminder_confirmation(
                email=data.email,
                url=str(data.url),
                interval_hours=data.interval_hours
            )
            print(f"✅ Confirmation email sent to {data.email}")
        except Exception as e:
            print(f"⚠️ Could not send confirmation email: {e}")
            # Don't fail the whole request if email fails
        
        return {
            "message": "Reminder created successfully",
            "reminder": reminder.to_dict()
        }
        
    except Exception as e:
        print(f"❌ Error creating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reminders/list")
def list_reminders(active_only: bool = True):
    """Get all reminders"""
    try:
        reminders = Reminder.get_all(active_only=active_only)
        return {
            "count": len(reminders),
            "reminders": [r.to_dict() for r in reminders]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reminders/{reminder_id}")
def get_reminder(reminder_id: str):
    """Get reminder details with history"""
    try:
        reminder = Reminder.get_by_id(reminder_id)
        
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        # Get history
        history = ReminderHistory.get_by_reminder(reminder_id, limit=10)
        
        return {
            "reminder": reminder.to_dict(),
            "history": [h.to_dict() for h in history]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reminders/email/{email}")
def get_reminders_by_email(email: str):
    """Get all reminders for an email address"""
    try:
        reminders = Reminder.get_by_email(email)
        return {
            "email": email,
            "count": len(reminders),
            "reminders": [r.to_dict() for r in reminders]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/reminders/{reminder_id}")
def update_reminder(reminder_id: str, data: UpdateReminderRequest):
    """Update reminder details"""
    try:
        reminder = Reminder.get_by_id(reminder_id)
        
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        updates = {}
        if data.url is not None:
            updates['url'] = str(data.url)
        if data.email is not None:
            updates['email'] = data.email
        if data.interval_hours is not None:
            if data.interval_hours < 1:
                raise HTTPException(
                    status_code=400,
                    detail="Interval must be at least 1 hour"
                )
            updates['interval_hours'] = data.interval_hours
        if data.css_selector is not None:
            updates['css_selector'] = data.css_selector
        if data.xpath is not None:
            updates['xpath'] = data.xpath
        
        reminder.update(**updates)
        
        # Reschedule if interval changed
        if 'interval_hours' in updates:
            schedule_reminder(reminder)
        
        return {
            "message": "Reminder updated successfully",
            "reminder": reminder.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/reminders/{reminder_id}/toggle")
def toggle_reminder(reminder_id: str, is_active: bool):
    """Activate or deactivate a reminder"""
    try:
        reminder = Reminder.get_by_id(reminder_id)
        
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        reminder.update(is_active=1 if is_active else 0)
        
        # Schedule or unschedule
        if is_active:
            schedule_reminder(reminder)
        else:
            from backend.core.scheduler import scheduler
            job_id = f"reminder_{reminder_id}"
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
                print(f"🛑 Removed scheduled job: {job_id}")
        
        status = "activated" if is_active else "deactivated"
        
        return {
            "message": f"Reminder {status}",
            "reminder": reminder.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: str):
    """Delete a reminder"""
    try:
        reminder = Reminder.get_by_id(reminder_id)
        
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        # Remove from scheduler
        from backend.core.scheduler import scheduler
        job_id = f"reminder_{reminder_id}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        
        # Delete from database
        success = Reminder.delete(reminder_id)
        
        if success:
            return {
                "message": "Reminder deleted successfully",
                "deleted_reminder_id": reminder_id
            }
        else:
            raise HTTPException(status_code=404, detail="Reminder not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reminders/{reminder_id}/trigger")
async def trigger_reminder_now(reminder_id: str):
    """Manually trigger a reminder check now"""
    try:
        reminder = Reminder.get_by_id(reminder_id)
        
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        print(f"🔄 Manual trigger for reminder: {reminder_id}")
        
        # Scrape and check for changes
        from backend.core.scheduler import scrape_and_check_reminder
        result = await asyncio.to_thread(scrape_and_check_reminder, reminder)
        
        print(f"✅ Trigger result: {result}")
        
        # Return user-friendly message based on result
        if result.get("status") == "changed":
            message = "✅ Changes detected! Email notification sent."
        elif result.get("status") == "no_change":
            message = "✓ No changes detected. Content is the same."
        elif result.get("status") == "no_content":
            message = "⚠️ Could not extract content from the URL."
        elif result.get("status") == "error":
            message = f"❌ Error: {result.get('error', 'Unknown error')}"
        else:
            message = "✓ Check completed."
        
        return {
            "message": message,
            "result": result,
            "reminder": reminder.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error triggering reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))