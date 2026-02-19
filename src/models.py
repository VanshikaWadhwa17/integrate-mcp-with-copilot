"""
Database models for the activity management system.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role enumeration."""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    """Model for users (students, teachers, admins)."""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Integer, default=1)  # SQLite doesn't support Boolean
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Activity(Base):
    """Model for extracurricular activities."""
    __tablename__ = "activity"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    schedule = Column(String)
    max_participants = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to membership records
    memberships = relationship(
        "ActivityMembership",
        back_populates="activity",
        cascade="all, delete-orphan"
    )


class Student(Base):
    """Model for students."""
    __tablename__ = "student"

    email = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    memberships = relationship(
        "ActivityMembership",
        back_populates="student",
        cascade="all, delete-orphan"
    )


class ActivityMembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    WITHDRAWN = "withdrawn"


class ActivityMembership(Base):
    """Detailed membership tracking between Activity and Student."""
    __tablename__ = "activity_membership"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey('activity.id'), index=True)
    student_email = Column(String, ForeignKey('student.email'), index=True)
    signup_date = Column(DateTime, default=datetime.utcnow)
    withdrawn_date = Column(DateTime, nullable=True)
    status = Column(Enum(ActivityMembershipStatus), default=ActivityMembershipStatus.ACTIVE)
    notes = Column(String, nullable=True)

    activity = relationship("Activity", back_populates="memberships")
    student = relationship("Student", back_populates="memberships")

