from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import StreakResponse
from services import get_current_user, get_streak

router = APIRouter(prefix="/streak", tags=["streak"])

@router.get("", response_model=StreakResponse)
def streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_streak(db, current_user.id)
