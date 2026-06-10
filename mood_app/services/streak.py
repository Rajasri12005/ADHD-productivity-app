from datetime import date, timedelta
from sqlalchemy.orm import Session
from models import Streak
import uuid

def update_streak(db: Session, user_id: uuid.UUID):
    today = date.today()
    streak = db.query(Streak).filter(Streak.user_id == user_id).first()

    if not streak:
        streak = Streak(user_id=user_id, current_streak=1, last_active_date=today)
        db.add(streak)
    else:
        if streak.last_active_date == today:
            return streak  # already updated today
        elif streak.last_active_date == today - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1
        streak.last_active_date = today

    db.commit()
    db.refresh(streak)
    return streak

def get_streak(db: Session, user_id: uuid.UUID) -> Streak:
    streak = db.query(Streak).filter(Streak.user_id == user_id).first()
    if not streak:
        return Streak(user_id=user_id, current_streak=0, last_active_date=None)
    return streak
