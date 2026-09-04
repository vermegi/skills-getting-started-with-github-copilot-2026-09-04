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


def get_activity(activity_name: str):
    """Return the activity or raise a 404 when it does not exist."""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activities[activity_name]


def is_participant(activity, email: str) -> bool:
    return email in activity["participants"]


def is_waitlisted(activity, email: str) -> bool:
    return email in activity["waitlist"]


def activity_is_full(activity) -> bool:
    return len(activity["participants"]) >= activity["max_participants"]


def add_to_activity(activity, email: str) -> None:
    activity["participants"].append(email)


def add_to_waitlist(activity, email: str) -> None:
    activity["waitlist"].append(email)


def remove_from_activity(activity, email: str) -> None:
    activity["participants"].remove(email)


def remove_from_waitlist(activity, email: str) -> None:
    activity["waitlist"].remove(email)


def promote_first_waitlisted(activity):
    """Move the first waitlisted student into the activity and return their email."""
    if not activity["waitlist"] or activity_is_full(activity):
        return None

    promoted_email = activity["waitlist"].pop(0)
    add_to_activity(activity, promoted_email)
    return promoted_email


def registered_message(activity_name: str, email: str):
    return {"message": f"Signed up {email} for {activity_name}", "status": "registered"}


def waitlisted_message(activity, activity_name: str, email: str):
    return {
        "message": f"{activity_name} is full. Added {email} to the waitlist",
        "status": "waitlisted",
        "waitlist_position": len(activity["waitlist"]),
    }


def waitlist_removed_message(activity_name: str, email: str):
    return {
        "message": f"Removed {email} from the waitlist for {activity_name}",
        "status": "waitlist_removed",
    }


def unregistered_message(activity_name: str, email: str, promoted_email):
    message = f"Unregistered {email} from {activity_name}"
    response = {"message": message, "status": "unregistered"}

    if promoted_email:
        response["message"] = (
            f"{message}. {promoted_email} was moved from the waitlist to the participants"
        )
        response["promoted"] = promoted_email

    return response


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity, or add them to the waitlist if it is full"""
    activity = get_activity(activity_name)

    if is_participant(activity, email):
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    if is_waitlisted(activity, email):
        raise HTTPException(status_code=400, detail="Student already on the waitlist for this activity")

    if activity_is_full(activity):
        add_to_waitlist(activity, email)
        return waitlisted_message(activity, activity_name, email)

    add_to_activity(activity, email)
    return registered_message(activity_name, email)


@app.delete("/activities/{activity_name}/participants")
def unregister_from_activity(activity_name: str, email: str):
    """Remove a student from an activity or its waitlist.

    When a participant leaves a full activity, the first waitlisted student is
    automatically enrolled.
    """
    activity = get_activity(activity_name)

    if is_waitlisted(activity, email):
        remove_from_waitlist(activity, email)
        return waitlist_removed_message(activity_name, email)

    if not is_participant(activity, email):
        raise HTTPException(status_code=404, detail="Student is not signed up for this activity")

    remove_from_activity(activity, email)
    promoted_email = promote_first_waitlisted(activity)
    return unregistered_message(activity_name, email, promoted_email)
