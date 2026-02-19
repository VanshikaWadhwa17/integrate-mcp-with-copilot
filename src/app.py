"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.

Now using SQLAlchemy for persistent database storage instead of in-memory data.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from sqlalchemy.orm import Session
from database import SessionLocal, init_db, get_db
from models import Activity, Student, activity_participants

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize database on startup
try:
    init_db()
except:
    pass  # Database might already be initialized


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with their participants."""
    activities_list = db.query(Activity).all()
    result = {}
    for activity in activities_list:
        # Get participants for this activity
        participants = db.query(Student.email).join(
            activity_participants
        ).filter(
            activity_participants.c.activity_id == activity.id
        ).all()
        participant_emails = [p[0] for p in participants]
        
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": participant_emails
        }
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    # Find the activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if student is already signed up
    existing = db.query(activity_participants).filter(
        (activity_participants.c.activity_id == activity.id) &
        (activity_participants.c.student_email == email)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Create or find the student
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        student = Student(email=email)
        db.add(student)
        db.flush()

    # Add student to activity
    activity.participants.append(student)  # type: ignore
    db.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity"""
    # Find the activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if student is signed up
    existing = db.query(activity_participants).filter(
        (activity_participants.c.activity_id == activity.id) &
        (activity_participants.c.student_email == email)
    ).first()
    
    if not existing:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Find and remove the student
    student = db.query(Student).filter(Student.email == email).first()
    if student:
        activity.participants.remove(student)  # type: ignore
        db.commit()
    
    return {"message": f"Unregistered {email} from {activity_name}"}
