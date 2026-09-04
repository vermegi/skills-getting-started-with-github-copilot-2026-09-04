from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index():
    # Arrange
    
    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seeded_activities():
    # Arrange
    expected_activity_count = 9

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    returned_activities = response.json()
    assert len(returned_activities) == expected_activity_count
    assert returned_activities["Chess Club"] == {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "waitlist": [],
    }


def test_signup_adds_student_to_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "alex@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}",
        "status": "registered",
    }
    assert email in activities[activity_name]["participants"]


def test_signup_for_unknown_activity_returns_not_found():
    # Arrange
    activity_name = "Robotics Club"
    email = "alex@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_duplicate_student_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unregister_removes_student_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}",
        "status": "unregistered",
    }
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_unknown_activity_returns_not_found():
    # Arrange
    activity_name = "Robotics Club"
    email = "alex@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_student_not_signed_up_returns_not_found():
    # Arrange
    activity_name = "Chess Club"
    email = "alex@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}


def test_signup_when_activity_is_full_adds_student_to_waitlist():
    # Arrange
    activity_name = "Chess Club"
    activity = activities[activity_name]
    activity["participants"] = [
        f"student{index}@mergington.edu" for index in range(activity["max_participants"])
    ]
    email = "alex@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"{activity_name} is full. Added {email} to the waitlist",
        "status": "waitlisted",
        "waitlist_position": 1,
    }
    assert email not in activity["participants"]
    assert activity["waitlist"] == [email]


def test_signup_duplicate_waitlisted_student_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    activity = activities[activity_name]
    activity["participants"] = [
        f"student{index}@mergington.edu" for index in range(activity["max_participants"])
    ]
    email = "alex@mergington.edu"
    activity["waitlist"] = [email]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already on the waitlist for this activity"}
    assert activity["waitlist"] == [email]


def test_unregister_auto_enrolls_first_waitlisted_student():
    # Arrange
    activity_name = "Chess Club"
    activity = activities[activity_name]
    activity["participants"] = [
        f"student{index}@mergington.edu" for index in range(activity["max_participants"])
    ]
    activity["waitlist"] = ["alex@mergington.edu", "bella@mergington.edu"]
    email = activity["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": (
            f"Unregistered {email} from {activity_name}. "
            "alex@mergington.edu was moved from the waitlist to the participants"
        ),
        "status": "unregistered",
        "promoted": "alex@mergington.edu",
    }
    assert email not in activity["participants"]
    assert "alex@mergington.edu" in activity["participants"]
    assert activity["waitlist"] == ["bella@mergington.edu"]


def test_unregister_removes_waitlisted_student():
    # Arrange
    activity_name = "Chess Club"
    activity = activities[activity_name]
    email = "alex@mergington.edu"
    activity["waitlist"] = [email]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from the waitlist for {activity_name}",
        "status": "waitlist_removed",
    }
    assert activity["waitlist"] == []
