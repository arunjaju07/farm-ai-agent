from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import logging  # ← ADD THIS LINE

from app.database.db import SessionLocal, get_db
from app.models.user_model import User

router = APIRouter()
logger = logging.getLogger(__name__)

# ========== MODELS ==========
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    user_id: int
    name: str
    role: str
    region: str = None
    success: bool

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    language: Optional[str] = None
    region: Optional[str] = None
    permissions: Optional[Any] = None

# ========== ENDPOINTS ==========

@router.post("/login")
def login_user(login: LoginRequest):
    db = SessionLocal()
    try:
        # Find user by username
        user = db.query(User).filter(func.lower(User.username) == func.lower(login.username)).first()
        
        # Check if user exists and password matches
        if not user or user.password != login.password:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Login successful
        return {
            "message": f"Welcome back, {user.name}!",
            "user_id": user.id,
            "name": user.name,
            "role": user.role,
            "region": user.region,
            "success": True
        }
    finally:
        db.close()

@router.get("/user/{user_id}")
def get_user_info(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "phone": user.phone,
            "username": user.username,
            "language": user.language,
            "region": user.region,
            "permissions": json.loads(user.permissions) if user.permissions else {},
            "created_at": user.created_at
        }
    finally:
        db.close()

@router.put("/user/update/{user_id}")
def update_user_info(user_id: int, user: UserUpdate):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.id == user_id).first()
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.name is not None:
            existing.name = user.name
        if user.role is not None:
            existing.role = user.role
        if user.phone is not None:
            existing.phone = user.phone
        if user.username is not None:
            existing.username = user.username
        if user.password is not None and user.password.strip():
            existing.password = user.password
        if user.language is not None:
            existing.language = user.language
        if user.region is not None:
            existing.region = user.region
        if user.permissions is not None:
            if isinstance(user.permissions, dict):
                existing.permissions = json.dumps(user.permissions)
            else:
                existing.permissions = user.permissions
        
        db.commit()
        db.refresh(existing)
        
        return {
            "message": "User updated successfully",
            "user": {
                "id": existing.id,
                "name": existing.name,
                "role": existing.role,
                "username": existing.username,
                "phone": existing.phone,
                "region": existing.region,
                "language": existing.language,
                "permissions": json.loads(existing.permissions) if existing.permissions else {}
            }
        }
    finally:
        db.close()