"""
Database models for the activity management system.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

# Association table for many-to-many relationship between activities and students
activity_participants = Table(
    'activity_participants',
    Base.metadata,
    Column('activity_id', Integer, ForeignKey('activity.id'), primary_key=True),
    Column('student_email', String, ForeignKey('student.email'), primary_key=True),
    Column('signup_date', DateTime, default=datetime.utcnow)
)


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
    
    # Relationship to students
    participants = relationship(
        "Student",
        secondary=activity_participants,
        backref="activities"
    )


class Student(Base):
    """Model for students."""
    __tablename__ = "student"

    email = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

