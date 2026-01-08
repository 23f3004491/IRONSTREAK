from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum


class TargetStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    targets = relationship("Target", back_populates="user")


class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_text = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    duration_in_days = Column(Integer, nullable=False)
    status = Column(Enum(TargetStatus), default=TargetStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    locked = Column(Boolean, default=True)

    user = relationship("User", back_populates="targets")
    checkins = relationship("DailyCheckin", back_populates="target", cascade="all, delete")
    streak = relationship("Streak", back_populates="target", uselist=False, cascade="all, delete")


class DailyCheckin(Base):
    __tablename__ = "daily_checkins"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    completed = Column(Boolean, default=True)
    completed_at = Column(DateTime, default=datetime.utcnow)

    target = relationship("Target", back_populates="checkins")


class Streak(Base):
    __tablename__ = "streaks"

    target_id = Column(Integer, ForeignKey("targets.id"), primary_key=True)
    current_streak = Column(Integer, default=0)
    last_completed_date = Column(Date, nullable=True)

    target = relationship("Target", back_populates="streak")
