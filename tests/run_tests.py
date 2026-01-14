#!/usr/bin/env python3
import json
import sys
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

results = []

def run_test_get_activities():
    try:
        resp = client.get('/activities')
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert 'Chess Club' in data
        return True, 'get_activities passed'
    except AssertionError as e:
        return False, f'get_activities failed: {e}'
    except Exception as e:
        return False, f'get_activities error: {e}'

def run_test_signup_and_unregister_cycle():
    activity = 'Basketball Team'
    email = 'tester@example.com'
    try:
        # Ensure clean state
        if email in activities[activity]['participants']:
            activities[activity]['participants'].remove(email)

        # Sign up
        resp = client.post(f"/activities/{activity}/signup?email={email}")
        if resp.status_code != 200:
            return False, f'signup failed status {resp.status_code} body={resp.text}'
        if email not in activities[activity]['participants']:
            return False, 'signup did not add email to participants'

        # Unregister
        resp = client.post(f"/activities/{activity}/unregister?email={email}")
        if resp.status_code != 200:
            return False, f'unregister failed status {resp.status_code} body={resp.text}'
        if email in activities[activity]['participants']:
            return False, 'unregister did not remove email from participants'

        return True, 'signup_and_unregister_cycle passed'
    except Exception as e:
        return False, f'signup_and_unregister_cycle error: {e}'

if __name__ == '__main__':
    tests = [
        ('get_activities', run_test_get_activities),
        ('signup_and_unregister_cycle', run_test_signup_and_unregister_cycle),
    ]
    summary = {'passed': 0, 'failed': 0, 'results': []}
    for name, fn in tests:
        ok, message = fn()
        summary['results'].append({'test': name, 'ok': ok, 'message': message})
        if ok:
            summary['passed'] += 1
        else:
            summary['failed'] += 1

    # Print JSON summary to stdout
    print(json.dumps(summary, indent=2))
    # Also write to file for inspection
    with open('tests/run_tests_output.json', 'w') as f:
        json.dump(summary, f, indent=2)
    # Exit with non-zero if any failed
    sys.exit(0 if summary['failed'] == 0 else 2)
