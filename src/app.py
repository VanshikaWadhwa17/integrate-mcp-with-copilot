"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.

Features:
- Persistent SQLAlchemy database storage
- User authentication with JWT tokens
- Role-based access control (Student, Teacher, Admin)
- Activity management and signup
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.requests import Request
import os
from pathlib import Path
from sqlalchemy.orm import Session
from database import SessionLocal, init_db, get_db
from models import Activity, Student, User, UserRole, ActivityMembership, ActivityMembershipStatus
from auth import hash_password, verify_password, create_access_token, decode_token
from schemas import UserRegister, UserLogin, Token, UserResponse
import secrets
from datetime import datetime

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


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user from JWT token."""
    # Get token from Authorization header
    auth_header = request.headers.get("authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.replace("Bearer ", "")
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


# Authentication Endpoints

@app.post("/auth/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@app.post("/auth/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint (token invalidation handled on client-side)."""
    return {"message": "Successfully logged out"}


@app.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


# Activity Endpoints


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with their participants."""
    activities_list = db.query(Activity).all()
    result = {}
    for activity in activities_list:
        memberships = db.query(ActivityMembership).filter(
            ActivityMembership.activity_id == activity.id
        ).all()

        participant_entries = []
        for m in memberships:
            participant_entries.append({
                "student_email": m.student_email,
                "signup_date": m.signup_date,
                "status": m.status.value,
                "withdrawn_date": m.withdrawn_date,
                "notes": m.notes,
            })

        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": participant_entries
        }
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Sign up a student for an activity (requires authentication)"""
    # Find the activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if membership already exists
    existing = db.query(ActivityMembership).filter(
        (ActivityMembership.activity_id == activity.id) &
        (ActivityMembership.student_email == email)
    ).first()

    if existing and existing.status != ActivityMembershipStatus.WITHDRAWN:
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

    # Create membership record
    if existing and existing.status == ActivityMembershipStatus.WITHDRAWN:
        existing.status = ActivityMembershipStatus.ACTIVE
        existing.withdrawn_date = None
        existing.signup_date = datetime.utcnow()
        db.add(existing)
    else:
        membership = ActivityMembership(
            activity_id=activity.id,
            student_email=email,
            status=ActivityMembershipStatus.ACTIVE
        )
        db.add(membership)

    db.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Unregister a student from an activity (requires authentication)"""
    # Find the activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Find membership
    existing = db.query(ActivityMembership).filter(
        (ActivityMembership.activity_id == activity.id) &
        (ActivityMembership.student_email == email)
    ).first()

    if not existing or existing.status == ActivityMembershipStatus.WITHDRAWN:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Mark withdrawn
    existing.status = ActivityMembershipStatus.WITHDRAWN
    existing.withdrawn_date = datetime.utcnow()
    db.add(existing)
    db.commit()

    return {"message": f"Unregistered {email} from {activity_name}"}
