from sqlalchemy import (
    Column, DateTime, ForeignKey, Enum as SAEnum,
    String, UniqueConstraint, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum
from core.database import Base


class MoodLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Mood(Base):
    __tablename__ = "moods"
    __table_args__ = (
        Index("ix_moods_user_id", "user_id"),
        Index("ix_moods_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mood_level = Column(SAEnum(MoodLevel), nullable=False)
    note = Column(String(500), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="moods")
