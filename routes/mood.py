from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.security import get_current_user
from schemas import MoodCreate, MoodResponse, MoodHistoryResponse
from services import log_mood, get_today_mood, get_mood_history, get_mood_trend
from models.user import User

router = APIRouter(prefix="/mood", tags=["mood"])


@router.post("", response_model=MoodResponse, status_code=status.HTTP_200_OK)
def log_mood_route(
    payload: MoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Log today's mood. Upserts — calling multiple times on the same day
    updates the existing entry rather than creating duplicates.
    """
    return log_mood(current_user.id, payload.mood_level, payload.note, db)


@router.get("/today", response_model=MoodResponse)
def get_today_mood_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's mood entry. 404 if not yet logged."""
    mood = get_today_mood(current_user.id, db)
    if not mood:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No mood logged today")
    return mood


@router.get("/history", response_model=MoodHistoryResponse)
def mood_history_route(
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Paginated mood history, newest first."""
    moods, total = get_mood_history(current_user.id, db, limit=limit, offset=offset)
    return {"moods": moods, "total": total}


@router.get("/trend")
def mood_trend_route(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return daily mood levels for the last N days (for chart rendering)."""
    return get_mood_trend(current_user.id, db, days=days)
