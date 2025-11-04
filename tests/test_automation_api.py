"""
Tests for automation API endpoints.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


@patch('src.services.automation_service.automation_service.batch_enroll_users')
def test_batch_enroll_users_success(mock_enroll):
    """Test batch enrollment endpoint."""
    mock_enroll.return_value = {
        'enrolled': ['user1@test.com', 'user2@test.com'],
        'unregistered': ['user3@test.com']
    }
    
    response = client.post(
        "/api/automation/enroll",
        json={
            "users": ["user1@test.com", "user2@test.com", "user3@test.com"],
            "course_id": "test-course",
            "headless": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert data['enrolled_count'] == 2
    assert data['unregistered_count'] == 1


@patch('src.services.automation_service.automation_service.batch_enroll_users')
def test_batch_enroll_users_failure(mock_enroll):
    """Test batch enrollment endpoint failure."""
    mock_enroll.side_effect = Exception("Enrollment failed")
    
    response = client.post(
        "/api/automation/enroll",
        json={
            "users": ["user1@test.com"],
            "course_id": "test-course",
            "headless": True
        }
    )
    
    assert response.status_code == 500


def test_batch_enroll_users_invalid_request():
    """Test batch enrollment with invalid request."""
    response = client.post(
        "/api/automation/enroll",
        json={
            "users": [],  # Empty users list
            "course_id": "test-course"
        }
    )
    
    assert response.status_code == 422  # Validation error


@patch('src.services.automation_service.automation_service.check_and_notify_helpdesk')
def test_notify_helpdesk_success(mock_notify):
    """Test helpdesk notification endpoint."""
    mock_notify.return_value = {
        'success': True,
        'tickets_count': 5,
        'tickets': [
            {'ticket_id': '1', 'owner': 'John Doe', 'time_open': '2 hours ago', 'state': 'open'}
        ],
        'analysis': {
            'within_6hrs': 3,
            'within_12hrs': 1,
            'within_24hrs': 1,
            'within_48hrs': 0,
            'by_owner': {'John Doe': 5}
        },
        'notification_sent': True,
        'email_sent': True
    }
    
    response = client.post("/api/automation/notify-helpdesk")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert data['tickets_count'] == 5
    assert 'analysis' in data


@patch('src.services.automation_service.automation_service.check_and_notify_helpdesk')
def test_notify_helpdesk_failure(mock_notify):
    """Test helpdesk notification failure."""
    mock_notify.side_effect = Exception("Helpdesk check failed")
    
    response = client.post("/api/automation/notify-helpdesk")
    
    assert response.status_code == 500


@patch('src.services.automation_service.automation_service.update_page')
def test_update_page_success(mock_update):
    """Test page update endpoint."""
    mock_update.return_value = True
    
    response = client.post(
        "/api/automation/update-page",
        json={
            "page_name": "test-page",
            "content": "New page content",
            "headless": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'message' in data


@patch('src.services.automation_service.automation_service.update_page')
def test_update_page_failure(mock_update):
    """Test page update failure."""
    mock_update.return_value = False
    
    response = client.post(
        "/api/automation/update-page",
        json={
            "page_name": "test-page",
            "content": "New content",
            "headless": True
        }
    )
    
    assert response.status_code == 500


@patch('src.services.automation_service.automation_service.update_page')
def test_update_page_exception(mock_update):
    """Test page update with exception."""
    mock_update.side_effect = Exception("Update failed")
    
    response = client.post(
        "/api/automation/update-page",
        json={
            "page_name": "test-page",
            "content": "New content",
            "headless": True
        }
    )
    
    assert response.status_code == 500
