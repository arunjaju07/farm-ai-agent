from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.database.db import engine, Base
from app.routers import user_router, location_router, auth_router, task_router, zone_router, upload_router, issue_router
from app.scheduler import start_scheduler
import os

app = FastAPI(title="Farm AI Agent", description="Multi-Location Farm Management System")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(user_router.router)
app.include_router(location_router.router)
app.include_router(auth_router.router)
app.include_router(task_router.router)
app.include_router(zone_router.router)  # 👈 NOW zone_router is imported above
app.include_router(upload_router.router)
app.include_router(issue_router.router)

start_scheduler()


# Serve HTML page
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/health")
def health():
    return {"status": "healthy"}