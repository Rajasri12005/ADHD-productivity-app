from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.streak import Streak


async def get_streak(user_id: int, db: AsyncSession) -> Streak | None:
    result = await db.execute(select(Streak).where(Streak.user_id == user_id))
    streak = result.scalar_one_or_none()
    if not streak:
        return {"user_id": user_id, "current_streak": 0, "last_active_date": None}
    return streak
