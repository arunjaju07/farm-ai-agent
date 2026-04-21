from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.database.db import SessionLocal
from app.models.user_model import User

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    role: str
    phone: str
    username: str
    password: str
    language: Optional[str] = None
    region: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    language: Optional[str] = None
    region: Optional[str] = None

# Add User
@router.post("/add-user")
def add_user(user: UserCreate):
    db = SessionLocal()
    
    # Check if username already exists
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = User(
        name=user.name,
        role=user.role,
        phone=user.phone,
        username=user.username,
        password=user.password,
        language=user.language,
        region=user.region
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    
    return {"message": "User added successfully", "user_id": new_user.id}

# Get all users
@router.get("/users")
def get_all_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    
    return [
        {
            "id": u.id,
            "name": u.name,
            "role": u.role,
            "phone": u.phone,
            "username": u.username,
            "language": u.language,
            "region": u.region,
            "created_at": u.created_at
        }
        for u in users
    ]

# Get single user
@router.get("/user/{user_id}")
def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "name": user.name,
        "role": user.role,
        "phone": user.phone,
        "username": user.username,
        "language": user.language,
        "region": user.region
    }

# Update user
@router.put("/user/update/{user_id}")
def update_user(user_id: int, user_update: UserUpdate):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.phone is not None:
        user.phone = user_update.phone
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.password is not None:
        user.password = user_update.password
    if user_update.language is not None:
        user.language = user_update.language
    if user_update.region is not None:
        user.region = user_update.region
    
    db.commit()
    db.close()
    
    return {"message": "User updated successfully"}

# Delete user
@router.delete("/user/delete/{user_id}")
def delete_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    db.close()
    
    return {"message": "User deleted successfully"}