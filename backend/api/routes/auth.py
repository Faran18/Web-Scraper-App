# backend/api/routes/auth.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from backend.models.user import User, Session
from backend.core.auth import get_current_user
from backend.models.password_reset import PasswordReset
from backend.utils.email_sender import send_password_reset_email
from backend.core.config import FRONTEND_BASE_URL

router = APIRouter()


class SignupRequest(BaseModel):
    """Request body for user registration"""
    email: EmailStr
    password: str
    full_name: str 


class LoginRequest(BaseModel):
    """Request body for login"""
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    """Request body for password change"""
    old_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    """Request body for forgetting password"""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Request body for resetting password"""
    token: str
    new_password: str


@router.post("/auth/signup")
async def signup(data: SignupRequest):
    try:
        if len(data.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

        if not data.full_name or not data.full_name.strip():
            raise HTTPException(status_code=400, detail="Full name is required")

        user = User.create(
            email=data.email,
            password=data.password,
            full_name=data.full_name.strip()
        )

        session = Session.create(user.user_id)

        return {
            "message": "User registered successfully",
            "user": user.to_dict(),
            "token": session.token,
            "expires_at": session.expires_at
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/login")
async def login(data: LoginRequest):
    try:
        user = User.authenticate(data.email, data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        session = Session.create(user.user_id)

        return {
            "message": "Login successful",
            "user": user.to_dict(),
            "token": session.token,
            "expires_at": session.expires_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/logout")
async def logout(user: User = Depends(get_current_user)):
    try:
        Session.delete_all_user_sessions(user.user_id)
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    return {"user": user.to_dict()}

@router.post("/auth/change-password")
async def change_password(data: ChangePasswordRequest, user: User = Depends(get_current_user)):
    try:
        if not User.verify_password(data.old_password, user.password_hash):
            raise HTTPException(status_code=401, detail="Current password is incorrect")

        if len(data.new_password) < 6:
            raise HTTPException(status_code=400, detail="New password must be at least 6 characters long")

        user.update(password=data.new_password)
        Session.delete_all_user_sessions(user.user_id)

        return {"message": "Password changed successfully. Please login again."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/auth/delete")
async def delete_account(user: User = Depends(get_current_user)):
    try:
        # Delete all sessions first
        Session.delete_all_user_sessions(user.user_id)

        # Soft-delete user
        user.update(is_active=0)

        return {"message": "Account deleted (deactivated) successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/sessions")
async def get_user_sessions(user: User = Depends(get_current_user)):
    """
    Get all active sessions for current user.
    """
    try:
        sessions = Session.get_by_user(user.user_id)
        
        return {
            "count": len(sessions),
            "sessions": [s.to_dict() for s in sessions]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    """
    Request password reset link via email.
    Always return success (avoid leaking whether email exists).
    """
    try:
        user = User.get_by_email(data.email)

        if user and user.is_active:
            reset = PasswordReset.create(user.user_id, expires_in_minutes=30)
            reset_link = f"{FRONTEND_BASE_URL}/reset-password?token={reset.token}"
            send_password_reset_email(user.email, reset_link)

        return {"message": "If your email exists, a reset link was sent."}

    except Exception as e:
        print(f"❌ forgot-password error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process request")


@router.post("/auth/reset-password")
async def reset_password(data: ResetPasswordRequest):
    """
    Reset password using token.
    """
    try:
        if len(data.new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

        reset = PasswordReset.get_by_token(data.token)
        if not reset or not reset.is_valid():
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user = User.get_by_id(reset.user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=400, detail="User not found or inactive")

        user.update(password=data.new_password)
        reset.mark_used()

        # force logout everywhere
        Session.delete_all_user_sessions(user.user_id)

        return {"message": "Password reset successfully. Please login again."}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ reset-password error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset password")
    
@router.delete("/auth/me", status_code=204)
async def delete_my_account(user: User = Depends(get_current_user)):
    """
    Permanently delete user and all related data
    """
    try:
        User.delete_completely(user.user_id)
        return
    except Exception as e:
        print("❌ Delete account error:", e)
        raise HTTPException(status_code=500, detail="Failed to delete account")
