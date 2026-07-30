from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..database.db import SessionLocal
from ..models.user_model import User
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

# ========== MODELS ==========
class UserCreate(BaseModel):
    name: str
    role: str
    phone: str
    username: str
    password: str
    language: str = "english"
    region: str
    permissions: Optional[Dict[str, Any]] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    language: Optional[str] = None
    region: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None

# ========== ENDPOINTS ==========

@router.post("/add-user")
async def add_user(user: UserCreate):
    """Create a new user with permissions"""
    db = SessionLocal()
    try:
        # Check if username exists
        existing = db.query(User).filter(User.username == user.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create new user
        new_user = User(
            name=user.name,
            role=user.role,
            phone=user.phone,
            username=user.username,
            password=user.password,
            language=user.language,
            region=user.region,
            permissions=json.dumps(user.permissions) if user.permissions else None
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "message": "User created successfully", 
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "role": new_user.role,
                "username": new_user.username,
                "phone": new_user.phone,
                "region": new_user.region,
                "language": new_user.language,
                "permissions": json.loads(new_user.permissions) if new_user.permissions else {}
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/users")
async def get_all_users():
    """Get all users with permissions"""
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.id).all()
        
        # Convert to dict with permissions parsed
        result = []
        for user in users:
            result.append({
                "id": user.id,
                "name": user.name,
                "role": user.role,
                "phone": user.phone,
                "username": user.username,
                "language": user.language,
                "region": user.region,
                "permissions": json.loads(user.permissions) if user.permissions else {},
                "created_at": user.created_at
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/user/{user_id}")
async def get_user(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # ✅ ADD THIS DEBUG LOG
        permissions_data = json.loads(user.permissions) if user.permissions else {}
        print(f"🔍 DEBUG - User {user_id} permissions: {permissions_data}")
        print(f"🔍 DEBUG - Type: {type(permissions_data)}")
        
        return {
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "phone": user.phone,
            "username": user.username,
            "language": user.language,
            "region": user.region,
            "permissions": permissions_data,
            "created_at": user.created_at
        }
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.put("/user/update/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    """Update user details including permissions"""
    db = SessionLocal()
    try:
        # Check if user exists
        existing = db.query(User).filter(User.id == user_id).first()
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields
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
            existing.permissions = json.dumps(user.permissions)
        
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
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/test-permissions")
async def test_permissions():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 12).first()
        return {
            "has_permissions_column": hasattr(user, 'permissions'),
            "permissions_value": user.permissions if hasattr(user, 'permissions') else "NO COLUMN",
            "user_id": user.id,
            "user_name": user.name
        }
    finally:
        db.close()

@router.delete("/user/delete/{user_id}")
async def delete_user(user_id: int):
    """Delete a user"""
    db = SessionLocal()

    try:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Prevent deleting the last admin
        if user.role == "admin":
            admin_count = db.query(User).filter(User.role == "admin").count()

            if admin_count <= 1:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot delete the last admin."
                )

        # Delete user
        db.delete(user)
        db.commit()

        return {
            "message": "User deleted successfully"
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Cannot delete this user because they are assigned to one or more tasks. Please reassign or delete those tasks first."
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user {user_id}: {e}")

        raise HTTPException(
            status_code=500,
            detail="Failed to delete user."
        )

    finally:
        db.close()