"""TeamWeave FastAPI Application Entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.database import init_db, engine
from app.models import User
from app.routers import (
    auth, users, events, matching, teams, gamification, feedback, demo
)

app = FastAPI(
    title="TeamWeave API",
    description="Intelligent Skill-Based Team Formation Platform (Living Weave)",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(matching.router)
app.include_router(teams.router)
app.include_router(gamification.router)
app.include_router(feedback.router)
app.include_router(demo.router)


@app.on_event("startup")
def on_startup():
    """Initialize database tables and auto-seed demo data if empty."""
    init_db()
    with Session(engine) as session:
        # Check if users already exist
        user_count = session.exec(select(User)).first()
        if not user_count:
            print("Database empty. Auto-seeding initial demonstration dataset...")
            demo.seed_demo_data(session)


@app.get("/api/health")
def healthcheck():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "product": "TeamWeave",
        "codename": "Living Weave",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
