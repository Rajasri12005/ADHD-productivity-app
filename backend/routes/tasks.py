from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.security import get_current_user
from schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, RecommendationResponse
from services import (
    create_task, list_tasks, get_task,
    update_task, delete_task, complete_task,
    get_recommendations, update_streak,
)
from models.user import User
import uuid

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task_route(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task."""
    return create_task(
        current_user.id, payload.title, payload.difficulty, payload.description, db
    )


@router.get("", response_model=TaskListResponse)
def list_tasks_route(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all tasks for the current user, optionally filtered."""
    tasks = list_tasks(current_user.id, db, completed=completed)
    done = [t for t in tasks if t.is_completed]
    pending = [t for t in tasks if not t.is_completed]
    return {
        "tasks": tasks,
        "total": len(tasks),
        "completed": len(done),
        "pending": len(pending),
    }


# NOTE: /recommend must be BEFORE /{task_id} or FastAPI will treat "recommend" as a UUID
@router.get("/recommend", response_model=RecommendationResponse)
def recommend_tasks_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return mood-aware task recommendations with ADHD tips."""
    return get_recommendations(current_user.id, db)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_route(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_task(task_id, current_user.id, db)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task_route(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_task(
        task_id, current_user.id,
        payload.title, payload.description, payload.difficulty, db
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_route(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_task(task_id, current_user.id, db)


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task_route(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a task complete and update streak + achievements."""
    task = complete_task(task_id, current_user.id, db)
    update_streak(current_user.id, db)
    return task
