from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.security import get_current_user
from schemas import StreakResponse, AchievementResponse
from services import get_streak, get_achievements
from models.user import User

router = APIRouter(prefix="/streak", tags=["streak"])


@router.get("", response_model=StreakResponse)
def streak_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return current streak, longest streak, and totals."""
    return get_streak(current_user.id, db)


@router.get("/achievements", response_model=List[AchievementResponse])
def achievements_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all earned achievement badges."""
    return get_achievements(current_user.id, db)
