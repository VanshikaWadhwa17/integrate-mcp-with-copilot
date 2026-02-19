"""
Initialize the database with sample data.

Run this script to set up the database with the initial activities and participants.
"""

from database import engine, SessionLocal, init_db
from models import Base, Activity, Student, activity_participants
import os

# Initialize database schema
init_db()

# Create a session
db = SessionLocal()

# Clear existing data (optional - for fresh start)
db.query(Activity).delete()
db.query(Student).delete()
db.commit()

# Sample activities data
sample_activities = [
    {
        "name": "Chess Club",
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    {
        "name": "Programming Class",
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    {
        "name": "Gym Class",
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    {
        "name": "Soccer Team",
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    {
        "name": "Basketball Team",
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    {
        "name": "Art Club",
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    {
        "name": "Drama Club",
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    {
        "name": "Math Club",
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    {
        "name": "Debate Team",
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
]

# Insert activities and participants
for activity_data in sample_activities:
    # Create activity
    activity = Activity(
        name=activity_data["name"],
        description=activity_data["description"],
        schedule=activity_data["schedule"],
        max_participants=activity_data["max_participants"]
    )
    db.add(activity)
    db.flush()  # Flush to get the activity ID

    # Create students and associate them
    for email in activity_data["participants"]:
        # Check if student already exists
        student = db.query(Student).filter(Student.email == email).first()
        if not student:
            student = Student(email=email)
            db.add(student)
            db.flush()

        # Associate student with activity
        if student not in activity.participants:
            activity.participants.append(student)  # type: ignore

db.commit()
db.close()

print("Database initialized successfully with sample data!")
