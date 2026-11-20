import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activities(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return test_activities


@pytest.fixture
def client(activities):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client, activities):
    # Arrange
    expected_activities = activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_student_to_activity(client, activities):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_student(client, activities):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "new@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_student_from_activity(client, activities):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_returns_not_found_for_unregistered_student(client):
    # Arrange
    email = "not-registered@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": "new@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
