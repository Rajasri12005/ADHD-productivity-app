from sqlalchemy import Column, Integer, Date, ForeignKey, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from core.database import Base


class Streak(Base):
    __tablename__ = "streaks"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_active_date = Column(Date, nullable=True)
    total_tasks_completed = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="streak")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    badge_key = Column(String(100), nullable=False)
    label = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    earned_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="achievements")
