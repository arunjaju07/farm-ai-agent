from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
import requests
import base64
import os

from app.database.db import SessionLocal
from app.models.grass_health_model import GrassHealthIssue
from app.models.grass_health_comment_model import GrassHealthComment
from app.models.user_model import User
from app.models.location_model import Location
from app.models.zone_model import Zone
router = APIRouter(prefix="/grass-health", tags=["Grass Health"])

# ============ HELPER FUNCTIONS ============

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ API ENDPOINTS ============

@router.post("/analyze")
async def analyze_grass_photo(file: UploadFile = File(...)):
    try:
        print("📸 Analyzing grass photo...")
        
        image_bytes = await file.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        mime_type = file.content_type
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        prompt = """You are an agricultural AI expert specializing in elephant grass (Napier grass). 

Analyze this photo and return ONLY valid JSON in this exact format, no other text:

{
    "disease_name": "None",
    "disease_details": "Primary concern is environmental stress",
    "confidence": 0.90,
    "growth_stage": "Mature/Senescent",
    "health_score": 60,
    "harvest_ready": true,
    "harvest_ready_text": "Yes (Immediate harvest recommended)",
    "plant_height_estimate": "1.5-1.8m",
    "environmental_stress": "Water stress or maturity",
    "recommended_action": "Prioritize immediate harvesting to capture remaining nutritional value; evaluate moisture levels and irrigation scheduling for the next growth cycle.",
    "worker_notes_guidance": "Focus on harvesting and next cycle planning"
}

For disease_name choose from: Rust, Leaf Spot, Smut, None, Unknown
For growth_stage choose from: Vegetative, Stem Elongation, Mature, Senescent, Post-Harvest Regrowth, Unknown
For harvest_ready use true or false
For health_score use 0-100 (0=poor, 100=excellent)

Return ONLY valid JSON, no other text or explanation."""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime_type, "data": base64_image}}
                ]
            }]
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        text_response = data["candidates"][0]["content"]["parts"][0]["text"]
        
        import re
        json_match = re.search(r'\{[\s\S]*\}', text_response)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(text_response)
        
        return {
            "success": True,
            "analysis": {
                "disease_name": result.get("disease_name", "Unknown"),
                "disease_details": result.get("disease_details", ""),
                "confidence": result.get("confidence", 0),
                "growth_stage": result.get("growth_stage", "Unknown"),
                "health_score": result.get("health_score", 50),
                "harvest_ready": result.get("harvest_ready", False),
                "harvest_ready_text": result.get("harvest_ready_text", ""),
                "plant_height_estimate": result.get("plant_height_estimate", "Unknown"),
                "environmental_stress": result.get("environmental_stress", ""),
                "recommended_action": result.get("recommended_action", "Monitor grass health"),
                "worker_notes_guidance": result.get("worker_notes_guidance", "")
            },
            "raw_response": result
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ REPORT ENDPOINTS ============

class GrassHealthReport(BaseModel):
    location_id: int
    zone_id: Optional[int] = None
    photo_urls: List[str]
    ai_disease: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_growth_stage: Optional[str] = None
    ai_plant_height: Optional[str] = None
    ai_harvest_ready: Optional[bool] = None
    ai_pest_damage: Optional[bool] = None
    ai_pest_type: Optional[str] = None
    ai_health_score: Optional[int] = None
    ai_recommendation: Optional[str] = None
    ai_full_response: Optional[dict] = None
    ai_disease_details: Optional[str] = None,
    ai_harvest_ready_text: Optional[str] = None,
    ai_environmental_stress: Optional[str] = None,
    ai_worker_notes_guidance: Optional[str] = None,
    worker_notes: Optional[str] = None,
    media_audio_url: Optional[str] = None,
    media_video_url: Optional[str] = None

@router.post("/report")
def report_grass_issue(report: GrassHealthReport, db: Session = Depends(get_db), user_id: int = None):
    """Create new active grass health issue"""
    # Get user_id from request (will be set by frontend)
    # In production, get from auth token
    
    new_issue = GrassHealthIssue(
        location_id=report.location_id,
        zone_id=report.zone_id,
        detected_by=user_id,
        photo_urls=report.photo_urls,
        ai_disease=report.ai_disease,
        ai_confidence=report.ai_confidence,
        ai_growth_stage=report.ai_growth_stage,
        ai_plant_height=report.ai_plant_height,
        ai_harvest_ready=report.ai_harvest_ready,
        ai_pest_damage=report.ai_pest_damage,
        ai_pest_type=report.ai_pest_type,
        ai_health_score=report.ai_health_score,
        ai_recommendation=report.ai_recommendation,
        ai_full_response=report.ai_full_response,
        ai_disease_details=report.ai_disease_details,
        ai_harvest_ready_text=report.ai_harvest_ready_text,
        ai_environmental_stress=report.ai_environmental_stress,
        ai_worker_notes_guidance=report.ai_worker_notes_guidance,
        worker_notes=report.worker_notes,
        media_audio_url=report.media_audio_url,
        media_video_url=report.media_video_url,
        status="active"
    )
    
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    
    return {"success": True, "message": "Issue reported successfully", "issue_id": new_issue.id}

@router.get("/issues/active")
def get_active_issues(db: Session = Depends(get_db), role: str = None, region: str = None, user_id: int = None):
    """Get active issues (filtered by role)"""
    query = db.query(GrassHealthIssue).filter(GrassHealthIssue.status.in_(["active", "in_progress"]))
    
    if role == "admin":
        # Admin sees all
        pass
    elif role == "supervisor" and region:
        # Supervisor sees only their region
        query = query.join(Location).filter(Location.region == region)
    elif role == "worker" and user_id:
        # Worker sees only their own reports
        query = query.filter(GrassHealthIssue.detected_by == user_id)
    
    issues = query.order_by(GrassHealthIssue.detected_at.desc()).all()
    return issues

@router.get("/issues/resolved")
def get_resolved_issues(db: Session = Depends(get_db), role: str = None, region: str = None, user_id: int = None):
    """Get resolved issues (filtered by role)"""
    query = db.query(GrassHealthIssue).filter(GrassHealthIssue.status == "resolved")
    
    if role == "admin":
        pass
    elif role == "supervisor" and region:
        query = query.join(Location).filter(Location.region == region)
    elif role == "worker" and user_id:
        query = query.filter(GrassHealthIssue.detected_by == user_id)
    
    issues = query.order_by(GrassHealthIssue.resolved_at.desc()).all()
    return issues

@router.get("/issues/{issue_id}")
def get_issue_detail(issue_id: int, db: Session = Depends(get_db)):
    """Get single issue details"""
    issue = db.query(GrassHealthIssue).filter(GrassHealthIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@router.put("/issues/{issue_id}/resolve")
def resolve_issue(issue_id: int, resolution_notes: str, resolved_by: int, db: Session = Depends(get_db)):
    """Mark issue as resolved"""
    issue = db.query(GrassHealthIssue).filter(GrassHealthIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    issue.status = "resolved"
    issue.resolved_by = resolved_by
    issue.resolved_at = datetime.now()
    issue.resolution_notes = resolution_notes
    
    db.commit()
    
    return {"success": True, "message": "Issue resolved successfully"}

@router.get("/locations")
def get_grass_locations(db: Session = Depends(get_db)):
    """Get locations for dropdown"""
    locations = db.query(Location).all()
    return locations

@router.get("/zones/{location_id}")
def get_grass_zones(location_id: int, db: Session = Depends(get_db)):
    """Get zones for dropdown"""
    zones = db.query(Zone).filter(Zone.location_id == location_id).all()
    return zones

# ============ COMMENT ENDPOINTS ============

class CommentCreate(BaseModel):
    issue_id: int
    user_role: Optional[str] = None  # ← ADD THIS
    user_id: Optional[int] = None     # ← ADD THIS
    comment_type: str = "comment"
    comment_text: Optional[str] = None
    photo_urls: Optional[List[str]] = []
    audio_url: Optional[str] = None
    video_url: Optional[str] = None

@router.post("/comments/add")
def add_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    # Get user_role from request instead of hardcoding
    user_role = comment.user_role if hasattr(comment, 'user_role') else "worker"
    user_id = comment.user_id if hasattr(comment, 'user_id') else None
    """Add comment to an issue"""
    try:
        # Get current user from request (you'll need to pass user_id from frontend)
        # For now, we'll use a placeholder - you should pass user_id in the request
        user_id = 1  # Temporary - FIX THIS
        user_role = "admin"  # Temporary - FIX THIS
        
        # Check if issue exists
        issue = db.query(GrassHealthIssue).filter(GrassHealthIssue.id == comment.issue_id).first()
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        new_comment = GrassHealthComment(
            issue_id=comment.issue_id,
            user_id=user_id,
            user_role=user_role,
            comment_type=comment.comment_type,
            comment_text=comment.comment_text,
            photo_urls=comment.photo_urls or [],
            audio_url=comment.audio_url,
            video_url=comment.video_url
        )
        
        db.add(new_comment)
        
        # If this is an instruction from admin, update issue status to 'in_progress'
        if comment.comment_type == "instruction" and user_role in ["admin", "supervisor"]:
            issue.status = "in_progress"
        
        db.commit()
        
        return {"success": True, "message": "Comment added", "comment_id": new_comment.id}
        
    except Exception as e:
        db.rollback()
        print(f"Error adding comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comments/{issue_id}")
def get_comments(issue_id: int, db: Session = Depends(get_db)):
    """Get all comments for an issue"""
    try:
        comments = db.query(GrassHealthComment).filter(
            GrassHealthComment.issue_id == issue_id
        ).order_by(GrassHealthComment.created_at.asc()).all()
        return comments
    except Exception as e:
        print(f"Error getting comments: {e}")
        raise HTTPException(status_code=500, detail=str(e))