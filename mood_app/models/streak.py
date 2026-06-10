from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class Streak(Base):
    __tablename__ = "streaks"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    current_streak = Column(Integer, default=0)
    last_active_date = Column(Date, nullable=True)

    user = relationship("User", back_populates="streak")
