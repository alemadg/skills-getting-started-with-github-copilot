from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static index.html"""
    # Arrange - nothing special needed

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test retrieving all activities"""
    # Arrange - nothing special needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

    # Check activity structure
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange
    activity = "Programming Class"
    email = "test_signup@mergington.edu"

    # Ensure not already signed up (clean up)
    response = client.get("/activities")
    data = response.json()
    if email in data[activity]["participants"]:
        client.delete(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity}" == data["message"]

    # Verify added to participants
    response = client.get("/activities")
    data = response.json()
    assert email in data[activity]["participants"]


def test_signup_activity_not_found():
    """Test signup for non-existent activity"""
    # Arrange
    activity = "Nonexistent Activity"
    email = "test@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]


def test_signup_already_signed_up():
    """Test signup when student is already signed up"""
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already in initial data

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up" == data["detail"]


def test_delete_success():
    """Test successful unregistration from an activity"""
    # Arrange
    activity = "Gym Class"
    email = "test_delete@mergington.edu"

    # First sign up
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Unregistered {email} from {activity}" == data["message"]

    # Verify removed from participants
    response = client.get("/activities")
    data = response.json()
    assert email not in data[activity]["participants"]


def test_delete_activity_not_found():
    """Test delete from non-existent activity"""
    # Arrange
    activity = "Nonexistent Activity"
    email = "test@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]


def test_delete_not_signed_up():
    """Test delete when student is not signed up"""
    # Arrange
    activity = "Chess Club"
    email = "not_signed_up@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student not signed up" == data["detail"]