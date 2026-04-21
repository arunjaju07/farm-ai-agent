from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.db import SessionLocal, get_db
from app.models.user_model import User

router = APIRouter()

# Request model for login
class LoginRequest(BaseModel):
    username: str
    password: str

# Response model for login
class LoginResponse(BaseModel):
    message: str
    user_id: int
    name: str
    role: str
    success: bool

@router.post("/login")
def login_user(login: LoginRequest):
    db = SessionLocal()
    
    # Find user by username
    user = db.query(User).filter(User.username == login.username).first()
    
    # Check if user exists and password matches
    if not user or user.password != login.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Login successful
    return {
        "message": f"Welcome back, {user.name}!",
        "user_id": user.id,
        "name": user.name,
        "role": user.role,
        "success": True
    }

# Get user info (without password)
@router.get("/user/{user_id}")
def get_user_info(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "name": user.name,
        "role": user.role,
        "phone": user.phone,
        "username": user.username,
        "language": user.language
    }