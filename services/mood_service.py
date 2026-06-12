from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.mood import Mood, MoodLevel
import uuid


def log_mood(user_id: uuid.UUID, mood_level: MoodLevel, note: Optional[str], db: Session) -> Mood:
    """
    Log today's mood. Only one entry allowed per UTC day — upsert behaviour:
    if a mood already exists for today, UPDATE it instead of creating a duplicate.
    """
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    existing = (
        db.query(Mood)
        .filter(
            Mood.user_id == user_id,
            Mood.created_at >= today_start,
            Mood.created_at < today_end,
        )
        .first()
    )

    if existing:
        existing.mood_level = mood_level
        existing.note = note
        db.commit()
        db.refresh(existing)
        return existing

    mood = Mood(user_id=user_id, mood_level=mood_level, note=note)
    db.add(mood)
    db.commit()
    db.refresh(mood)
    return mood


def get_today_mood(user_id: uuid.UUID, db: Session) -> Optional[Mood]:
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    return (
        db.query(Mood)
        .filter(
            Mood.user_id == user_id,
            Mood.created_at >= today_start,
            Mood.created_at < today_end,
        )
        .order_by(Mood.created_at.desc())
        .first()
    )


def get_mood_history(
    user_id: uuid.UUID,
    db: Session,
    limit: int = 30,
    offset: int = 0,
) -> tuple[List[Mood], int]:
    query = db.query(Mood).filter(Mood.user_id == user_id)
    total = query.count()
    moods = query.order_by(Mood.created_at.desc()).offset(offset).limit(limit).all()
    return moods, total


def get_mood_trend(user_id: uuid.UUID, db: Session, days: int = 30) -> List[dict]:
    """Return daily mood levels for the last `days` days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    moods = (
        db.query(Mood)
        .filter(Mood.user_id == user_id, Mood.created_at >= cutoff)
        .order_by(Mood.created_at.asc())
        .all()
    )
    return [
        {
            "date": m.created_at.date().isoformat(),
            "mood_level": m.mood_level,
        }
        for m in moods
    ]
