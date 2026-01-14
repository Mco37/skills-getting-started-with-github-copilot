import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities state before each test"""
    # Save original state
    original_state = {}
    for activity_name, details in activities.items():
        original_state[activity_name] = details["participants"].copy()
    
    yield
    
    # Restore original state after test
    for activity_name, participants in original_state.items():
        activities[activity_name]["participants"] = participants


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success(client):
    activity = "Basketball Team"
    email = "newstudent@mergington.edu"
    
    # Ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)
    
    resp = client.post(
        f"/activities/{activity}/signup",
        json={"email": email}
    )
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate(client):
    """Test that duplicate signup returns 400 error"""
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already in the club
    
    resp = client.post(
        f"/activities/{activity}/signup",
        json={"email": email}
    )
    assert resp.status_code == 400
    assert "already signed up" in resp.json()["detail"].lower()


def test_signup_invalid_email_format(client):
    """Test that invalid email format returns 422 error"""
    activity = "Basketball Team"
    
    resp = client.post(
        f"/activities/{activity}/signup",
        json={"email": "not-an-email"}
    )
    assert resp.status_code == 422


def test_signup_wrong_domain(client):
    """Test that email from wrong domain returns 422 error"""
    activity = "Basketball Team"
    
    resp = client.post(
        f"/activities/{activity}/signup",
        json={"email": "student@otherschool.edu"}
    )
    assert resp.status_code == 422


def test_signup_at_capacity(client):
    """Test that signup fails when activity is at capacity"""
    activity = "Chess Club"
    # Fill to capacity (max_participants = 12)
    activities[activity]["participants"] = [
        f"student{i}@mergington.edu" for i in range(12)
    ]
    
    resp = client.post(
        f"/activities/{activity}/signup",
        json={"email": "newstudent@mergington.edu"}
    )
    assert resp.status_code == 400
    assert "maximum capacity" in resp.json()["detail"].lower()


def test_signup_nonexistent_activity(client):
    """Test signup for non-existent activity returns 404"""
    resp = client.post(
        "/activities/Nonexistent Club/signup",
        json={"email": "student@mergington.edu"}
    )
    assert resp.status_code == 404


def test_unregister_success(client):
    activity = "Basketball Team"
    email = "tester@mergington.edu"
    
    # Add email first
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)
    
    resp = client.post(
        f"/activities/{activity}/unregister",
        json={"email": email}
    )
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_not_registered(client):
    """Test that unregistering non-registered student returns 400 error"""
    activity = "Basketball Team"
    email = "notregistered@mergington.edu"
    
    # Ensure email is not in participants
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)
    
    resp = client.post(
        f"/activities/{activity}/unregister",
        json={"email": email}
    )
    assert resp.status_code == 400
    assert "not registered" in resp.json()["detail"].lower()


def test_unregister_nonexistent_activity(client):
    """Test unregister from non-existent activity returns 404"""
    resp = client.post(
        "/activities/Nonexistent Club/unregister",
        json={"email": "student@mergington.edu"}
    )
    assert resp.status_code == 404


def test_unregister_invalid_email(client):
    """Test that unregister with invalid email returns 422 error"""
    activity = "Basketball Team"
    
    resp = client.post(
        f"/activities/{activity}/unregister",
        json={"email": "invalid-email"}
    )
    assert resp.status_code == 422


def test_signup_and_unregister_cycle(client):
    """Test complete signup and unregister cycle"""
    activity = "Basketball Team"
    email = "cycletest@mergington.edu"
    
    # Ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)
    
    # Sign up
    resp = client.post(f"/activities/{activity}/signup", json={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]
    
    # Unregister
    resp = client.post(f"/activities/{activity}/unregister", json={"email": email})
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]
