"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "waitlist": []
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "waitlist": []
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "waitlist": []
    },
    "Basketball Team": {
        "description": "Practice basketball skills and compete in school games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": [],
        "waitlist": []
    },
    "Soccer Club": {
        "description": "Develop soccer skills and play friendly matches",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 22,
        "participants": [],
        "waitlist": []
    },
    "Art Club": {
        "description": "Explore drawing, painting, and other visual art techniques",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": [],
        "waitlist": []
    },
    "Drama Club": {
        "description": "Perform plays and build confidence through theater",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": [],
        "waitlist": []
    },
    "Debate Club": {
        "description": "Build research, public speaking, and critical thinking skills",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 16,
        "participants": [],
        "waitlist": []
    },
    "Science Club": {
        "description": "Conduct experiments and explore fascinating scientific topics",
        "schedule": "Fridays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": [],
        "waitlist": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity, or add them to the waitlist if it is full"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Validate student is not already waitlisted
    if email in activity["waitlist"]:
        raise HTTPException(status_code=400, detail="Student already on the waitlist for this activity")

    # Add the student to the waitlist when the activity is full
    if len(activity["participants"]) >= activity["max_participants"]:
        activity["waitlist"].append(email)
        return {
            "message": f"{activity_name} is full. Added {email} to the waitlist",
            "status": "waitlisted",
            "waitlist_position": len(activity["waitlist"]),
        }

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}", "status": "registered"}


@app.delete("/activities/{activity_name}/participants")
def unregister_from_activity(activity_name: str, email: str):
    """Remove a student from an activity or its waitlist.

    When a participant leaves a full activity, the first waitlisted student is
    automatically enrolled.
    """
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    participants = activity["participants"]
    waitlist = activity["waitlist"]

    if email in waitlist and email not in participants:
        waitlist.remove(email)
        return {
            "message": f"Removed {email} from the waitlist for {activity_name}",
            "status": "waitlist_removed",
        }

    if email not in participants:
        raise HTTPException(status_code=404, detail="Student is not signed up for this activity")

    participants.remove(email)

    response = {
        "message": f"Unregistered {email} from {activity_name}",
        "status": "unregistered",
    }

    # Auto-enroll the first waitlisted student, if any
    if waitlist and len(participants) < activity["max_participants"]:
        promoted_email = waitlist.pop(0)
        participants.append(promoted_email)
        response["promoted"] = promoted_email
        response["message"] += f". {promoted_email} was moved from the waitlist to the participants"

    return response
