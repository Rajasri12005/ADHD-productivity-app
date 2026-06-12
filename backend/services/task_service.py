import random
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.task import Task, TaskLog, Difficulty
from models.mood import Mood, MoodLevel
import uuid

# ─── ADHD-aware recommendation config ────────────────────────────────────────

MOOD_TO_DIFFICULTIES = {
    MoodLevel.LOW:    [Difficulty.EASY],
    MoodLevel.MEDIUM: [Difficulty.EASY, Difficulty.MEDIUM],
    MoodLevel.HIGH:   [Difficulty.MEDIUM, Difficulty.HARD],
}

FALLBACK_SUGGESTIONS = {
    MoodLevel.LOW: [
        "Drink a glass of water 💧",
        "Take 5 deep breaths 🧘",
        "Write one sentence about how you're feeling ✍️",
        "Step outside for 2 minutes 🌿",
        "Stretch your neck and shoulders 🤸",
    ],
    MoodLevel.MEDIUM: [
        "Review your task list and pick one small win ✅",
        "Reply to one pending message 📬",
        "Do a 10-minute tidy of your workspace 🧹",
        "Read for 15 minutes 📖",
        "Plan tomorrow's top 3 tasks 📋",
    ],
    MoodLevel.HIGH: [
        "Tackle your most important project 🚀",
        "Learn something new for 30 minutes 🎓",
        "Plan your week ahead 📅",
        "Start that task you've been avoiding 💪",
        "Have a productive deep-work session ⚡",
    ],
}

ADHD_TIPS = [
    "🎯 Body double: work alongside someone (video call counts).",
    "⏱️ Use a 25-min timer. Stop when it rings — no exceptions.",
    "📝 Brain-dump everything onto paper before starting.",
    "🔀 Switch tasks every 25 min if you feel stuck — momentum matters.",
    "🔕 Put your phone in another room, not just face-down.",
    "🌊 Ride the hyperfocus wave — schedule admin after, not during.",
    "✅ Break tasks into the smallest possible first step.",
    "💧 Dehydration tanks focus fast. Keep water visible on your desk.",
    "🏆 Celebrate small wins — dopamine fuels the next task.",
    "🎵 Try lo-fi music or white noise to boost concentration.",
]


# ─── CRUD ─────────────────────────────────────────────────────────────────────

def create_task(
    user_id: uuid.UUID,
    title: str,
    difficulty: Difficulty,
    description: Optional[str],
    db: Session,
) -> Task:
    task = Task(
        user_id=user_id,
        title=title.strip(),
        difficulty=difficulty,
        description=description,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(
    user_id: uuid.UUID,
    db: Session,
    completed: Optional[bool] = None,
) -> List[Task]:
    query = db.query(Task).filter(Task.user_id == user_id)
    if completed is not None:
        query = query.filter(Task.is_completed == completed)
    return query.order_by(Task.created_at.desc()).all()


def get_task(task_id: uuid.UUID, user_id: uuid.UUID, db: Session) -> Task:
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def update_task(
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    title: Optional[str],
    description: Optional[str],
    difficulty: Optional[Difficulty],
    db: Session,
) -> Task:
    task = get_task(task_id, user_id, db)
    if title is not None:
        task.title = title.strip()
    if description is not None:
        task.description = description
    if difficulty is not None:
        task.difficulty = difficulty
    db.commit()
    db.refresh(task)
    return task


def delete_task(task_id: uuid.UUID, user_id: uuid.UUID, db: Session) -> None:
    task = get_task(task_id, user_id, db)
    db.delete(task)
    db.commit()


def complete_task(task_id: uuid.UUID, user_id: uuid.UUID, db: Session) -> Task:
    task = get_task(task_id, user_id, db)
    if task.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already completed",
        )
    now = datetime.now(timezone.utc)
    task.is_completed = True
    task.completed_at = now

    log = TaskLog(user_id=user_id, task_id=task.id, completed_at=now)
    db.add(log)
    db.commit()
    db.refresh(task)
    return task


# ─── Recommendations ─────────────────────────────────────────────────────────

def get_recommendations(user_id: uuid.UUID, db: Session) -> dict:
    """
    Return personalised task recommendations based on today's mood and
    recent completion history. Falls back gracefully when no mood is logged.
    """
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Get today's mood
    latest_mood = (
        db.query(Mood)
        .filter(Mood.user_id == user_id, Mood.created_at >= today_start)
        .order_by(Mood.created_at.desc())
        .first()
    )

    adhd_tip = random.choice(ADHD_TIPS)

    if not latest_mood:
        # No mood today — recommend easy tasks or fallbacks
        tasks = (
            db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.is_completed == False,
                Task.difficulty == Difficulty.EASY,
            )
            .limit(5)
            .all()
        )
        return {
            "mood": None,
            "recommended_difficulty": "EASY",
            "tasks": tasks,
            "fallback_suggestions": FALLBACK_SUGGESTIONS[MoodLevel.LOW][:3],
            "adhd_tip": adhd_tip,
        }

    mood_level = latest_mood.mood_level
    difficulties = MOOD_TO_DIFFICULTIES[mood_level]

    # Get recently completed task IDs (last 7 days) to avoid re-recommending
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recently_completed_ids = {
        log.task_id
        for log in db.query(TaskLog)
        .filter(TaskLog.user_id == user_id, TaskLog.completed_at >= week_ago)
        .all()
    }

    tasks = (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.is_completed == False,
            Task.difficulty.in_(difficulties),
            Task.id.notin_(recently_completed_ids),
        )
        .order_by(Task.created_at.asc())
        .limit(5)
        .all()
    )

    # If still empty, relax the recently-completed filter
    if not tasks:
        tasks = (
            db.query(Task)
            .filter(
                Task.user_id == user_id,
                Task.is_completed == False,
                Task.difficulty.in_(difficulties),
            )
            .limit(5)
            .all()
        )

    return {
        "mood": mood_level,
        "recommended_difficulty": difficulties[0].value,
        "tasks": tasks,
        "fallback_suggestions": FALLBACK_SUGGESTIONS[mood_level][:3] if not tasks else [],
        "adhd_tip": adhd_tip,
    }
