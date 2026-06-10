from datetime import datetime, date
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.task import Task, TaskLog, Difficulty
from models.mood import MoodLevel
from models.streak import Streak

MOOD_TO_DIFFICULTY = {
    MoodLevel.LOW: Difficulty.EASY,
    MoodLevel.MEDIUM: Difficulty.MEDIUM,
    MoodLevel.HIGH: Difficulty.HARD,
}

FALLBACK_TASKS = {
    MoodLevel.LOW: [
        "Take 5 deep breaths",
        "Drink a glass of water",
        "Write one thing you're grateful for",
    ],
    MoodLevel.MEDIUM: [
        "Review your to-do list",
        "Reply to pending messages",
        "Do a 10-minute walk",
    ],
    MoodLevel.HIGH: [
        "Tackle your most important project",
        "Learn something new for 30 minutes",
        "Plan your week ahead",
    ],
}


async def create_task(user_id: int, title: str, difficulty: Difficulty, db: AsyncSession) -> Task:
    task = Task(user_id=user_id, title=title, difficulty=difficulty)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks(user_id: int, db: AsyncSession) -> list[Task]:
    result = await db.execute(select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc()))
    return result.scalars().all()


async def get_task(task_id: int, user_id: int, db: AsyncSession) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


async def update_task(task_id: int, user_id: int, title: str | None, difficulty: Difficulty | None, db: AsyncSession) -> Task:
    task = await get_task(task_id, user_id, db)
    if title is not None:
        task.title = title
    if difficulty is not None:
        task.difficulty = difficulty
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(task_id: int, user_id: int, db: AsyncSession) -> dict:
    task = await get_task(task_id, user_id, db)
    await db.delete(task)
    await db.commit()
    return {"detail": "Task deleted"}


async def complete_task(task_id: int, user_id: int, db: AsyncSession) -> dict:
    task = await get_task(task_id, user_id, db)
    if task.is_completed:
        raise HTTPException(status_code=400, detail="Task already completed")

    task.is_completed = True
    log = TaskLog(user_id=user_id, task_id=task_id)
    db.add(log)

    await _update_streak(user_id, db)
    await db.commit()
    return {"detail": "Task completed", "task_id": task_id}


async def recommend_tasks(user_id: int, mood: MoodLevel, db: AsyncSession) -> dict:
    target_difficulty = MOOD_TO_DIFFICULTY[mood]
    result = await db.execute(
        select(Task)
        .where(Task.user_id == user_id, Task.difficulty == target_difficulty, Task.is_completed == False)
        .order_by(Task.created_at.asc())
        .limit(5)
    )
    tasks = result.scalars().all()

    return {
        "mood": mood,
        "recommended_difficulty": target_difficulty,
        "tasks": tasks if tasks else [],
        "fallback_suggestions": [] if tasks else FALLBACK_TASKS[mood],
    }


async def _update_streak(user_id: int, db: AsyncSession):
    result = await db.execute(select(Streak).where(Streak.user_id == user_id))
    streak = result.scalar_one_or_none()
    today = date.today()

    if not streak:
        db.add(Streak(user_id=user_id, current_streak=1, last_active_date=today))
        return

    if streak.last_active_date == today:
        return
    elif streak.last_active_date and (today - streak.last_active_date).days == 1:
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    streak.last_active_date = today
