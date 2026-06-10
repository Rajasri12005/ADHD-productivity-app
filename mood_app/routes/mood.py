from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from database import get_db
from models import User, Mood
from schemas import MoodCreate, MoodResponse
from services import get_current_user

router = APIRouter(prefix="/mood", tags=["mood"])

@router.post("", response_model=MoodResponse, status_code=201)
def log_mood(
    payload: MoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mood = Mood(user_id=current_user.id, mood_level=payload.mood_level)
    db.add(mood)
    db.commit()
    db.refresh(mood)
    return mood

@router.get("/today", response_model=MoodResponse)
def get_today_mood(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(timezone.utc).date()
    mood = (
        db.query(Mood)
        .filter(Mood.user_id == current_user.id)
        .order_by(Mood.created_at.desc())
        .first()
    )
    if not mood or mood.created_at.date() != today:
        raise HTTPException(status_code=404, detail="No mood logged today")
    return mood
