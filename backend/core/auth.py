# backend/core/auth.py

from fastapi import Header, HTTPException
from typing import Optional
from backend.models.user import User, Session


async def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    """
    Middleware to get current authenticated user from token.
    
    Usage in routes:
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user_id": user.user_id}
    """
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    # Validate token
    session = Session.get_by_token(token)
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get user
    user = User.get_by_id(session.user_id)
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user


async def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[User]:
    """
    Optional authentication - returns None if not authenticated.
    """
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None