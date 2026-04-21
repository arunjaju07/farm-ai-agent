import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/upload", tags=["Upload"])

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

class UploadResponse(BaseModel):
    url: str
    public_id: str
    resource_type: str

@router.post("/photo", response_model=UploadResponse)
async def upload_photo(file: UploadFile = File(...)):
    """Upload a photo to Cloudinary"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            await file.read(),
            folder="farm_tasks/photos",
            resource_type="image"
        )
        
        return UploadResponse(
            url=result['secure_url'],
            public_id=result['public_id'],
            resource_type="image"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio", response_model=UploadResponse)
async def upload_audio(file: UploadFile = File(...)):
    """Upload an audio recording to Cloudinary"""
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be audio")
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            await file.read(),
            folder="farm_tasks/audio",
            resource_type="auto"
        )
        
        return UploadResponse(
            url=result['secure_url'],
            public_id=result['public_id'],
            resource_type="audio"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Upload a video to Cloudinary"""
    try:
        # Validate file type
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be video")
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            await file.read(),
            folder="farm_tasks/videos",
            resource_type="video"
        )
        
        return UploadResponse(
            url=result['secure_url'],
            public_id=result['public_id'],
            resource_type="video"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))