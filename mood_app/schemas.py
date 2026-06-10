from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from models.mood import MoodLevel
from models.task import Difficulty
import uuid

# Auth
class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Mood
class MoodCreate(BaseModel):
    mood_level: MoodLevel

class MoodResponse(BaseModel):
    id: uuid.UUID
    mood_level: MoodLevel
    created_at: datetime

    model_config = {"from_attributes": True}

# Task
class TaskCreate(BaseModel):
    title: str
    difficulty: Difficulty = Difficulty.MEDIUM

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    difficulty: Optional[Difficulty] = None

class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    difficulty: Difficulty
    is_completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}

# Streak
class StreakResponse(BaseModel):
    current_streak: int
    last_active_date: Optional[date]

    model_config = {"from_attributes": True}
