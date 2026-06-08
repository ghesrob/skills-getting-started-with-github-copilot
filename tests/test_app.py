import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity_name in data
    assert isinstance(data[expected_activity_name]["participants"], list)
    assert data[expected_activity_name]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_signup_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_delete_nonexistent_signup_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up for this activity"
