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
    }


def test_get_analytics_returns_capacity_metrics_for_each_activity():
    # Act
    response = client.get("/activities/analytics")

    # Assert
    assert response.status_code == 200
    analytics = response.json()
    assert analytics["Chess Club"] == {
        "utilization_percentage": 16.67,
        "remaining_seats": 10,
        "total_participants": 2,
    }
    assert analytics["Programming Class"] == {
        "utilization_percentage": 10.0,
        "remaining_seats": 18,
        "total_participants": 2,
    }
    assert analytics["Basketball Team"] == {
        "utilization_percentage": 0.0,
        "remaining_seats": 15,
        "total_participants": 0,
    }


def test_get_analytics_alias_returns_same_metrics():
    # Act
    response = client.get("/analytics")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"]["remaining_seats"] == 10


def test_signup_adds_student_to_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "alex@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
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
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
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