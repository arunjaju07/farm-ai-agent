from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.routers import (
    auth_router, user_router, location_router, 
    task_router, zone_router, upload_router, issue_router
)
from app.scheduler import start_scheduler

app = FastAPI(title="Farm AI Agent")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS, JS)
static_path = Path(__file__).parent / "templates" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Include routers
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(location_router.router)
app.include_router(task_router.router)
app.include_router(zone_router.router)
app.include_router(upload_router.router)
app.include_router(issue_router.router)

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    with open(templates_path / "index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Start background scheduler when app starts
@app.on_event("startup")
async def startup_event():
    start_scheduler()
    print("✅ Farm AI Agent started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    print("Farm AI Agent shutting down...")