from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from app.database.db import get_db  # Changed
from app.models.user_model import Location  # Changed

router = APIRouter(prefix="/locations", tags=["Locations"])

# Pydantic model for request/response
class LocationCreate(BaseModel):
    name: str
    area_acres: float
    region: str

class LocationResponse(BaseModel):
    id: int
    name: str
    area_acres: float
    region: str
    created_at: datetime

# Add a new location
@router.post("/add", response_model=LocationResponse)
def add_location(location: LocationCreate, db: Session = Depends(get_db)):
    new_location = Location(
        name=location.name,
        area_acres=location.area_acres,
        region=location.region
    )
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location

# Get all locations
@router.get("/all", response_model=List[LocationResponse])
def get_all_locations(db: Session = Depends(get_db)):
    locations = db.query(Location).all()
    return locations

# Get locations by region
@router.get("/region/{region}", response_model=List[LocationResponse])
def get_locations_by_region(region: str, db: Session = Depends(get_db)):
    locations = db.query(Location).filter(Location.region == region).all()
    return locations