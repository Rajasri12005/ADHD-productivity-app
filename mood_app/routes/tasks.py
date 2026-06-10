from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from database import get_db
from models import User, Task, TaskLog, Mood
from models.mood import MoodLevel
from models.task import Difficulty
from schemas import TaskCreate, TaskUpdate, TaskResponse
from services import get_current_user, update_streak

router = APIRouter(prefix="/tasks", tags=["tasks"])

FALLBACK_TASKS = [
    {"title": "Take a 5-minute walk", "difficulty": Difficulty.EASY},
    {"title": "Drink a glass of water", "difficulty": Difficulty.EASY},
    {"title": "Write 3 things you're grateful for", "difficulty": Difficulty.EASY},
]

@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = Task(user_id=current_user.id, title=payload.title, difficulty=payload.difficulty)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("", response_model=List[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Task).filter(Task.user_id == current_user.id).order_by(Task.created_at.desc()).all()

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if payload.title is not None:
        task.title = payload.title
    if payload.difficulty is not None:
        task.difficulty = payload.difficulty
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()

@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.is_completed:
        raise HTTPException(status_code=400, detail="Task already completed")

    task.is_completed = True
    log = TaskLog(user_id=current_user.id, task_id=task.id)
    db.add(log)
    db.commit()

    update_streak(db, current_user.id)
    db.refresh(task)
    return task

@router.get("/recommend", response_model=List[TaskResponse])
def recommend_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(timezone.utc).date()
    latest_mood = (
        db.query(Mood)
        .filter(Mood.user_id == current_user.id)
        .order_by(Mood.created_at.desc())
        .first()
    )

    mood_to_difficulty = {
        MoodLevel.LOW: [Difficulty.EASY],
        MoodLevel.MEDIUM: [Difficulty.MEDIUM],
        MoodLevel.HIGH: [Difficulty.HARD, Difficulty.MEDIUM],
    }

    if not latest_mood or latest_mood.created_at.date() != today:
        # No mood today — return easy tasks or fallback
        tasks = (
            db.query(Task)
            .filter(Task.user_id == current_user.id, Task.is_completed == False, Task.difficulty == Difficulty.EASY)
            .limit(5)
            .all()
        )
        if not tasks:
            # Return fallback virtual tasks (not persisted)
            return [
                Task(title=t["title"], difficulty=t["difficulty"], is_completed=False, created_at=datetime.now(timezone.utc))
                for t in FALLBACK_TASKS
            ]
        return tasks

    difficulties = mood_to_difficulty[latest_mood.mood_level]
    tasks = (
        db.query(Task)
        .filter(Task.user_id == current_user.id, Task.is_completed == False, Task.difficulty.in_(difficulties))
        .order_by(Task.difficulty.desc())
        .limit(5)
        .all()
    )
    return tasks
