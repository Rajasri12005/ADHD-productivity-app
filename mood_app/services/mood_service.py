from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.mood import Mood, MoodLevel


async def log_mood(user_id: int, mood_level: MoodLevel, db: AsyncSession) -> Mood:
    mood = Mood(user_id=user_id, mood_level=mood_level)
    db.add(mood)
    await db.commit()
    await db.refresh(mood)
    return mood


async def get_today_mood(user_id: int, db: AsyncSession) -> Mood | None:
    today_start = datetime.combine(date.today(), datetime.min.time())
    result = await db.execute(
        select(Mood)
        .where(Mood.user_id == user_id, Mood.created_at >= today_start)
        .order_by(Mood.created_at.desc())
    )
    return result.scalar_one_or_none()
