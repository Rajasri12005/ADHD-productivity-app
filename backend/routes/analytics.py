from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.security import get_current_user
from services import (
    get_weekly_analytics, get_monthly_analytics,
    get_activity_heatmap, get_dashboard_summary,
)
from models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/weekly")
def weekly_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Weekly productivity analytics (current calendar week).
    Includes daily breakdown, mood summary, and difficulty split.
    """
    return get_weekly_analytics(current_user.id, db)


@router.get("/monthly")
def monthly_analytics(
    month: int = Query(0, ge=0, le=12, description="0 = current month"),
    year: int = Query(0, ge=0, description="0 = current year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Monthly analytics including mood trend and cumulative completion trend.
    """
    return get_monthly_analytics(current_user.id, db, month=month, year=year)


@router.get("/heatmap")
def heatmap(
    days: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Activity heatmap data — per-day task completion counts for the last N days."""
    return get_activity_heatmap(current_user.id, db, days=days)


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Quick stats for the dashboard header card."""
    return get_dashboard_summary(current_user.id, db)
