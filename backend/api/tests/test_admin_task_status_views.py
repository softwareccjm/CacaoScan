"""
Tests for admin task status views.
Covers TaskStatusView.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from celery.result import AsyncResult

from api.views.admin.task_status_views import TaskStatusView


@pytest.fixture
def authenticated_user(db):
    """Create authenticated user for tests."""
    return User.objects.create_user(
        username='user',
        email='user@test.com',
        password='testpass123'
    )


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.mark.django_db
class TestTaskStatusView:
    """Tests for TaskStatusView."""
    
    def test_task_status_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/admin/tasks/status/task-id-123/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.admin.task_status_views.AsyncResult')
    def test_task_status_pending(self, mock_async_result, api_client, authenticated_user):
        """Test getting status of pending task."""
        mock_result = MagicMock()
        mock_result.state = 'PENDING'
        mock_async_result.return_value = mock_result
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = TaskStatusView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request, task_id='task-123')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'PENDING'
        assert 'message' in response.data
        assert 'Tarea pendiente' in response.data['message']
    
    @patch('api.views.admin.task_status_views.AsyncResult')
    def test_task_status_progress(self, mock_async_result, api_client, authenticated_user):
        """Test getting status of task in progress."""
        mock_result = MagicMock()
        mock_result.state = 'PROGRESS'
        mock_result.info = {'progress': 50, 'current': 10, 'total': 20}
        mock_async_result.return_value = mock_result
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = TaskStatusView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request, task_id='task-123')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'PROGRESS'
        assert 'progress' in response.data
    
    @patch('api.views.admin.task_status_views.AsyncResult')
    def test_task_status_success(self, mock_async_result, api_client, authenticated_user):
        """Test getting status of successful task."""
        mock_result = MagicMock()
        mock_result.state = 'SUCCESS'
        mock_result.result = {'result': 'Task completed'}
        mock_async_result.return_value = mock_result
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = TaskStatusView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request, task_id='task-123')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'SUCCESS'
        assert 'result' in response.data
        assert 'message' in response.data
    
    @patch('api.views.admin.task_status_views.AsyncResult')
    def test_task_status_failure(self, mock_async_result, api_client, authenticated_user):
        """Test getting status of failed task."""
        mock_result = MagicMock()
        mock_result.state = 'FAILURE'
        mock_result.info = 'Task failed with error'
        mock_async_result.return_value = mock_result
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = TaskStatusView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request, task_id='task-123')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'FAILURE'
        assert 'error' in response.data
        assert 'message' in response.data
    
    @patch('api.views.admin.task_status_views.AsyncResult')
    def test_task_status_unknown(self, mock_async_result, api_client, authenticated_user):
        """Test getting status of task with unknown state."""
        mock_result = MagicMock()
        mock_result.state = 'UNKNOWN_STATE'
        mock_async_result.return_value = mock_result
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = TaskStatusView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request, task_id='task-123')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'UNKNOWN_STATE'
        assert 'message' in response.data
    
    @patch('api.views.admin.task_status_views.AsyncResult')
    def test_task_status_exception(self, mock_async_result, api_client, authenticated_user):
        """Test exception handling in task status."""
        mock_async_result.side_effect = Exception("Celery connection error")
        
        api_client.force_authenticate(user=authenticated_user)
        
        view = TaskStatusView()
        request = Mock()
        request.user = authenticated_user
        
        response = view.get(request, task_id='task-123')
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data

