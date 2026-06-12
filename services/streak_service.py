from datetime import date, timedelta, datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from models.streak import Streak, Achievement
from models.task import TaskLog
import uuid

# ─── Badge definitions ────────────────────────────────────────────────────────

BADGES = [
    {
        "key": "first_task",
        "label": "First Step 🌱",
        "description": "Completed your very first task.",
        "check": lambda streak, total: total >= 1,
    },
    {
        "key": "streak_3",
        "label": "On a Roll 🔥",
        "description": "Maintained a 3-day streak.",
        "check": lambda streak, total: streak.current_streak >= 3,
    },
    {
        "key": "streak_7",
        "label": "Week Warrior ⚡",
        "description": "Maintained a 7-day streak.",
        "check": lambda streak, total: streak.current_streak >= 7,
    },
    {
        "key": "streak_30",
        "label": "Unstoppable 🏆",
        "description": "Maintained a 30-day streak.",
        "check": lambda streak, total: streak.current_streak >= 30,
    },
    {
        "key": "tasks_10",
        "label": "Getting Things Done ✅",
        "description": "Completed 10 tasks total.",
        "check": lambda streak, total: total >= 10,
    },
    {
        "key": "tasks_50",
        "label": "Productivity Pro 💼",
        "description": "Completed 50 tasks total.",
        "check": lambda streak, total: total >= 50,
    },
    {
        "key": "tasks_100",
        "label": "Century Club 💯",
        "description": "Completed 100 tasks total.",
        "check": lambda streak, total: total >= 100,
    },
]


# ─── Streak helpers ───────────────────────────────────────────────────────────

def get_or_create_streak(user_id: uuid.UUID, db: Session) -> Streak:
    streak = db.query(Streak).filter(Streak.user_id == user_id).first()
    if not streak:
        streak = Streak(user_id=user_id, current_streak=0, longest_streak=0)
        db.add(streak)
        db.commit()
        db.refresh(streak)
    return streak


def update_streak(user_id: uuid.UUID, db: Session) -> Streak:
    """Called after a task is completed. Advances streak if needed."""
    today = date.today()
    streak = get_or_create_streak(user_id, db)

    # Count total completed tasks
    total = db.query(TaskLog).filter(TaskLog.user_id == user_id).count()
    streak.total_tasks_completed = total

    if streak.last_active_date == today:
        # Already counted today — just update total and check badges
        db.commit()
        _check_and_award_badges(user_id, streak, total, db)
        return streak

    if streak.last_active_date == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    streak.last_active_date = today
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)

    db.commit()
    db.refresh(streak)

    _check_and_award_badges(user_id, streak, total, db)
    return streak


def get_streak(user_id: uuid.UUID, db: Session) -> Streak:
    return get_or_create_streak(user_id, db)


# ─── Achievement helpers ──────────────────────────────────────────────────────

def _check_and_award_badges(
    user_id: uuid.UUID, streak: Streak, total: int, db: Session
) -> None:
    existing_keys = {
        a.badge_key
        for a in db.query(Achievement).filter(Achievement.user_id == user_id).all()
    }

    for badge in BADGES:
        if badge["key"] in existing_keys:
            continue
        if badge["check"](streak, total):
            achievement = Achievement(
                user_id=user_id,
                badge_key=badge["key"],
                label=badge["label"],
                description=badge["description"],
            )
            db.add(achievement)

    db.commit()


def get_achievements(user_id: uuid.UUID, db: Session) -> List[Achievement]:
    return (
        db.query(Achievement)
        .filter(Achievement.user_id == user_id)
        .order_by(Achievement.earned_at.asc())
        .all()
    )
