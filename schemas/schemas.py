from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from models.mood import MoodLevel
from models.task import Difficulty
import uuid


# ─── Shared Response Envelope ─────────────────────────────────────────────────

class APIResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


# ─── Auth ─────────────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    username: Optional[str]
    created_at: datetime


# ─── Mood ─────────────────────────────────────────────────────────────────────

class MoodCreate(BaseModel):
    mood_level: MoodLevel
    note: Optional[str] = None


class MoodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mood_level: MoodLevel
    note: Optional[str]
    created_at: datetime


class MoodHistoryResponse(BaseModel):
    moods: List[MoodResponse]
    total: int


# ─── Task ─────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty: Difficulty = Difficulty.MEDIUM

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        if len(v) > 500:
            raise ValueError("Title too long (max 500 chars)")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[Difficulty] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty")
        return v


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: Optional[str]
    difficulty: Difficulty
    is_completed: bool
    created_at: datetime
    completed_at: Optional[datetime]


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    completed: int
    pending: int


# ─── Streak & Achievements ────────────────────────────────────────────────────

class StreakResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    current_streak: int
    longest_streak: int
    last_active_date: Optional[date]
    total_tasks_completed: int


class AchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    badge_key: str
    label: str
    description: Optional[str]
    earned_at: datetime


# ─── Analytics ────────────────────────────────────────────────────────────────

class DailyStats(BaseModel):
    date: date
    tasks_completed: int
    mood: Optional[str]


class WeeklyAnalytics(BaseModel):
    week_start: date
    week_end: date
    total_completed: int
    daily_breakdown: List[DailyStats]
    top_difficulty: Optional[str]
    mood_summary: dict


class MonthlyAnalytics(BaseModel):
    month: int
    year: int
    total_completed: int
    daily_breakdown: List[DailyStats]
    mood_trend: List[dict]
    completion_trend: List[dict]


class MoodTrend(BaseModel):
    date: date
    mood_level: str
    tasks_completed: int


# ─── Recommendations ─────────────────────────────────────────────────────────

class RecommendationResponse(BaseModel):
    mood: Optional[str]
    recommended_difficulty: Optional[str]
    tasks: List[TaskResponse]
    fallback_suggestions: List[str]
    adhd_tip: str
