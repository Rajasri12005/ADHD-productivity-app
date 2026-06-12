from datetime import date, datetime, timezone, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from models.task import TaskLog, Task, Difficulty
from models.mood import Mood, MoodLevel
import uuid


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _logs_in_range(user_id: uuid.UUID, start: datetime, end: datetime, db: Session):
    return (
        db.query(TaskLog)
        .filter(
            TaskLog.user_id == user_id,
            TaskLog.completed_at >= start,
            TaskLog.completed_at < end,
        )
        .all()
    )


def _moods_in_range(user_id: uuid.UUID, start: datetime, end: datetime, db: Session):
    return (
        db.query(Mood)
        .filter(
            Mood.user_id == user_id,
            Mood.created_at >= start,
            Mood.created_at < end,
        )
        .order_by(Mood.created_at.asc())
        .all()
    )


def _build_daily_stats(logs, moods, start_date: date, num_days: int) -> List[dict]:
    # Map date → count
    completion_by_day: dict[date, int] = {}
    for log in logs:
        d = log.completed_at.date()
        completion_by_day[d] = completion_by_day.get(d, 0) + 1

    # Map date → last mood
    mood_by_day: dict[date, str] = {}
    for mood in moods:
        d = mood.created_at.date()
        mood_by_day[d] = mood.mood_level.value

    result = []
    for i in range(num_days):
        d = start_date + timedelta(days=i)
        result.append({
            "date": d.isoformat(),
            "tasks_completed": completion_by_day.get(d, 0),
            "mood": mood_by_day.get(d),
        })
    return result


# ─── Weekly Analytics ────────────────────────────────────────────────────────

def get_weekly_analytics(user_id: uuid.UUID, db: Session) -> dict:
    today = date.today()
    # Go back to last Monday
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=7)

    start_dt = datetime.combine(week_start, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_dt = datetime.combine(week_end, datetime.min.time()).replace(tzinfo=timezone.utc)

    logs = _logs_in_range(user_id, start_dt, end_dt, db)
    moods = _moods_in_range(user_id, start_dt, end_dt, db)

    daily = _build_daily_stats(logs, moods, week_start, 7)

    # Difficulty breakdown
    task_ids = [log.task_id for log in logs]
    diff_counts = {"EASY": 0, "MEDIUM": 0, "HARD": 0}
    if task_ids:
        tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
        for t in tasks:
            diff_counts[t.difficulty.value] = diff_counts.get(t.difficulty.value, 0) + 1

    top_difficulty = max(diff_counts, key=diff_counts.get) if any(diff_counts.values()) else None

    # Mood summary
    mood_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for m in moods:
        mood_counts[m.mood_level.value] += 1

    return {
        "week_start": week_start.isoformat(),
        "week_end": (week_end - timedelta(days=1)).isoformat(),
        "total_completed": len(logs),
        "daily_breakdown": daily,
        "top_difficulty": top_difficulty,
        "mood_summary": mood_counts,
        "difficulty_breakdown": diff_counts,
    }


# ─── Monthly Analytics ───────────────────────────────────────────────────────

def get_monthly_analytics(user_id: uuid.UUID, db: Session, month: int = 0, year: int = 0) -> dict:
    today = date.today()
    if month == 0:
        month = today.month
    if year == 0:
        year = today.year

    # First and last day of the month
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1)
    else:
        month_end = date(year, month + 1, 1)

    num_days = (month_end - month_start).days

    start_dt = datetime.combine(month_start, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_dt = datetime.combine(month_end, datetime.min.time()).replace(tzinfo=timezone.utc)

    logs = _logs_in_range(user_id, start_dt, end_dt, db)
    moods = _moods_in_range(user_id, start_dt, end_dt, db)

    daily = _build_daily_stats(logs, moods, month_start, num_days)

    mood_trend = [
        {"date": m.created_at.date().isoformat(), "mood_level": m.mood_level.value}
        for m in moods
    ]

    # Running completion total
    running = 0
    completion_trend = []
    for d in daily:
        running += d["tasks_completed"]
        completion_trend.append({
            "date": d["date"],
            "cumulative_completed": running,
            "daily_completed": d["tasks_completed"],
        })

    return {
        "month": month,
        "year": year,
        "total_completed": len(logs),
        "daily_breakdown": daily,
        "mood_trend": mood_trend,
        "completion_trend": completion_trend,
    }


# ─── Streak History ──────────────────────────────────────────────────────────

def get_activity_heatmap(user_id: uuid.UUID, db: Session, days: int = 90) -> List[dict]:
    """Return per-day task completion count for the last N days (heatmap data)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    logs = (
        db.query(TaskLog)
        .filter(TaskLog.user_id == user_id, TaskLog.completed_at >= cutoff)
        .all()
    )

    counts: dict[str, int] = {}
    for log in logs:
        d = log.completed_at.date().isoformat()
        counts[d] = counts.get(d, 0) + 1

    result = []
    for i in range(days):
        d = (date.today() - timedelta(days=days - 1 - i)).isoformat()
        result.append({"date": d, "count": counts.get(d, 0)})
    return result


# ─── Dashboard Summary ───────────────────────────────────────────────────────

def get_dashboard_summary(user_id: uuid.UUID, db: Session) -> dict:
    """Quick numbers for the dashboard header."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    today_completed = (
        db.query(TaskLog)
        .filter(
            TaskLog.user_id == user_id,
            TaskLog.completed_at >= today_start,
            TaskLog.completed_at < today_end,
        )
        .count()
    )

    total_pending = (
        db.query(Task)
        .filter(Task.user_id == user_id, Task.is_completed == False)
        .count()
    )

    today_mood = (
        db.query(Mood)
        .filter(
            Mood.user_id == user_id,
            Mood.created_at >= today_start,
            Mood.created_at < today_end,
        )
        .order_by(Mood.created_at.desc())
        .first()
    )

    return {
        "today_completed": today_completed,
        "total_pending": total_pending,
        "today_mood": today_mood.mood_level.value if today_mood else None,
    }
