from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database.db import SessionLocal, get_db
from app.models.user_model import Location
from app.models.zone_model import Zone


router = APIRouter(prefix="/locations", tags=["Locations"])

# Pydantic model for request/response
class LocationCreate(BaseModel):
    name: str
    area_acres: float
    region: str
    layout_url: Optional[str] = None

class LocationResponse(BaseModel):
    id: int
    name: str
    area_acres: float
    region: str
    layout_url: Optional[str] = None
    created_at: datetime

# Add a new location
@router.post("/add", response_model=LocationResponse)
def add_location(location: LocationCreate, db: Session = Depends(get_db)):
    new_location = Location(
        name=location.name,
        area_acres=location.area_acres,
        region=location.region,
        layout_url=location.layout_url
    )
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location

# Get all locations (WITH layout_url)
@router.get("/all")
def get_all_locations(db: Session = Depends(get_db)):
    locations = db.query(Location).all()
    return [
        {
            "id": loc.id,
            "name": loc.name,
            "area_acres": loc.area_acres,
            "region": loc.region,
            "layout_url": loc.layout_url,
            "created_at": loc.created_at
        }
        for loc in locations
    ]

# Get single location
@router.get("/{location_id}")
def get_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    return {
        "id": location.id,
        "name": location.name,
        "area_acres": location.area_acres,
        "region": location.region,
        "layout_url": location.layout_url,
        "created_at": location.created_at
    }

# Get locations by region
@router.get("/region/{region}")
def get_locations_by_region(region: str, db: Session = Depends(get_db)):
    locations = db.query(Location).filter(Location.region == region).all()
    return [
        {
            "id": loc.id,
            "name": loc.name,
            "area_acres": loc.area_acres,
            "region": loc.region,
            "layout_url": loc.layout_url,
            "created_at": loc.created_at
        }
        for loc in locations
    ]

@router.put("/update/{location_id}")
def update_location(location_id: int, location: LocationCreate, db: Session = Depends(get_db)):
    existing = db.query(Location).filter(Location.id == location_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Location not found")
    
    existing.name = location.name
    existing.area_acres = location.area_acres
    existing.region = location.region
    existing.layout_url = location.layout_url
    
    db.commit()
    db.refresh(existing)
    return {"message": "Location updated successfully", "location": existing}

@router.delete("/delete/{location_id}")
def delete_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Delete all zones belonging to this location
    db.query(Zone).filter(Zone.location_id == location_id).delete()
    
    db.delete(location)
    db.commit()
    return {"message": "Location and all its zones deleted successfully"}