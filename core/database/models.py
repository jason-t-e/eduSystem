from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Integer, Float, DateTime, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs

class Base(AsyncAttrs, DeclarativeBase):
    pass

class StudentModel(Base):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    target_exam: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    exam_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    learning_stage: Mapped[str] = mapped_column(String, default="NOVICE")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    student_id: Mapped[str] = mapped_column(String, ForeignKey("students.id"))
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    plan_json: Mapped[Dict[str, Any]] = mapped_column(JSON)

    events: Mapped[List["SessionEventModel"]] = relationship(back_populates="session")

class SessionEventModel(Base):
    __tablename__ = "session_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    event_type: Mapped[str] = mapped_column(String)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON)

    session: Mapped["SessionModel"] = relationship(back_populates="events")

class QuestionAttemptModel(Base):
    __tablename__ = "question_attempts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    student_id: Mapped[str] = mapped_column(String, ForeignKey("students.id"))
    concept_id: Mapped[str] = mapped_column(String)
    question_type: Mapped[str] = mapped_column(String)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    time_taken_seconds: Mapped[int] = mapped_column(Integer)
    confidence_level: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class IngestionLogModel(Base):
    __tablename__ = "ingestion_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(String)
    file_name: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    concepts_extracted: Mapped[int] = mapped_column(Integer, default=0)
    relations_extracted: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ImprovementProposalModel(Base):
    __tablename__ = "improvement_proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    concept_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    issue_type: Mapped[str] = mapped_column(String)  # e.g., LOW_CONFIDENCE, CONTRADICTS
    description: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="PENDING") # PENDING, RESOLVED, IGNORED
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
