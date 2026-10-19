import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from .database import engine, Base, SessionLocal
from .seed.demo_data import seed_database
from .routers.api import router as api_router

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed idempotent demo patients
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="SwasthyaLoop Backend API & Clinical Portal",
    description="AI-assisted chronic-care follow-up engine with deterministic rules and constrained summaries.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for cross-origin or local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Disable caching on all API and static requests to prevent stale browser state
@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Include core REST API router first
app.include_router(api_router)

from fastapi.responses import FileResponse

# Explicit portal routes for distinct Doctor and Patient interfaces
@app.get("/doctor")
async def get_doctor_portal():
    return FileResponse(os.path.join(STATIC_DIR, "doctor.html"))

@app.get("/patient")
async def get_patient_portal():
    return FileResponse(os.path.join(STATIC_DIR, "patient.html"))

# Mount static web portal at root so opening http://localhost:8000 loads the full dashboard
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
