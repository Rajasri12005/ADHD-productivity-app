from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models  # ensure all models are registered

from routes import auth_router, mood_router, tasks_router, streak_router

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mood-Based Productivity API",
    description="Track your mood, manage tasks, and maintain streaks.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(mood_router)
app.include_router(tasks_router)
app.include_router(streak_router)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
