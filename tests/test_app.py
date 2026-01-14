from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_cycle():
    # Ensure test email not present
    activity = "Basketball Team"
    email = "tester@example.com"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Unregister
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_capacity_limit():
    """Test that signup is rejected when activity reaches max capacity"""
    activity = "Chess Club"
    # Save original participants
    original_participants = activities[activity]["participants"].copy()
    max_capacity = activities[activity]["max_participants"]
    
    # Fill activity to max capacity
    activities[activity]["participants"] = [f"student{i}@mergington.edu" for i in range(max_capacity)]
    
    # Try to add one more participant
    resp = client.post(f"/activities/{activity}/signup?email=overflow@example.com")
    assert resp.status_code == 400
    assert "maximum capacity" in resp.json()["detail"].lower()
    
    # Restore original participants
    activities[activity]["participants"] = original_participants

