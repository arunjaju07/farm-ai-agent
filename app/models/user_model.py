from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from app.database.db import Base  # Changed from 'database.db' to 'app.database.db'

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    language = Column(String, nullable=True)
    region = Column(String, nullable=True)  # 👈 ADD THIS
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    area_acres = Column(Float, nullable=False)
    region = Column(String, nullable=False)
    layout_url = Column(String, nullable=True)  # ← ADD THIS LINE
    created_at = Column(DateTime(timezone=True), server_default=func.now())