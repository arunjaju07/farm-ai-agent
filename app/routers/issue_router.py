from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database.db import get_db
from app.models.issue_model import Issue
from app.models.user_model import User

router = APIRouter(prefix="/issues", tags=["Issues"])

# Pydantic models
class IssueCreate(BaseModel):
    issue_type: str
    location_id: int
    description: Optional[str] = None
    reported_by: int
    photo_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None

class IssueResponse(BaseModel):
    id: int
    issue_type: str
    location_id: int
    description: Optional[str]
    reported_by: int
    status: str
    assigned_to: Optional[int]
    resolved_at: Optional[datetime]
    created_at: datetime

class IssueUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[int] = None

# Report a new issue (Worker)
@router.post("/report")
def report_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    new_issue = Issue(
        issue_type=issue.issue_type,
        location_id=issue.location_id,
        description=issue.description,
        reported_by=issue.reported_by,
        status="pending",
        photo_url=issue.photo_url,
        audio_url=issue.audio_url,
        video_url=issue.video_url
    )
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    return {"message": "Issue reported successfully", "issue_id": new_issue.id}

# Get all issues (Admin/Supervisor)
@router.get("/all")
def get_all_issues(db: Session = Depends(get_db)):
    issues = db.query(Issue).order_by(Issue.created_at.desc()).all()
    return [
        {
            "id": i.id,
            "issue_type": i.issue_type,
            "location_id": i.location_id,
            "description": i.description,
            "reported_by": i.reported_by,
            "status": i.status,
            "assigned_to": i.assigned_to,
            "resolved_at": i.resolved_at,
            "created_at": i.created_at
        }
        for i in issues
    ]

# Update issue status (Admin/Supervisor)
@router.put("/{issue_id}")
def update_issue(issue_id: int, update: IssueUpdate, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    if update.status:
        issue.status = update.status
        if update.status == "resolved":
            issue.resolved_at = datetime.now()
    
    if update.assigned_to:
        issue.assigned_to = update.assigned_to
    
    db.commit()
    return {"message": "Issue updated successfully"}

# Delete issue (Admin only)
@router.delete("/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    db.delete(issue)
    db.commit()
    return {"message": "Issue deleted successfully"}