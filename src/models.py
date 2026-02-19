"""
Database models for the activity management system.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many relationship between activities and students
activity_participants = Table(
    'activity_participants',
    Base.metadata,
    Column('activity_id', Integer, ForeignKey('activity.id'), primary_key=True),
    Column('student_email', String, ForeignKey('student.email'), primary_key=True),
    Column('signup_date', DateTime, default=datetime.utcnow)
)


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

