"""
Tests for admin email views.
Covers EmailStatusView, SendTestEmailView, SendBulkNotificationView, EmailTemplatePreviewView, and EmailLogsView.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from api.views.admin.email_views import (
    EmailStatusView,
    SendTestEmailView,
    SendBulkNotificationView,
    EmailTemplatePreviewView,
    EmailLogsView
)


@pytest.fixture
def admin_user(db):
    """Create admin user for tests."""
    return User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='testpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.mark.django_db
class TestEmailStatusView:
    """Tests for EmailStatusView."""
    
    def test_email_status_requires_admin(self, api_client):
        """Test that non-admin users cannot access."""
        response = api_client.get('/api/v1/admin/emails/status/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('api.views.admin.email_views.settings')
    @patch('api.views.admin.email_views.email_service')
    def test_email_status_success(self, mock_email_service, mock_settings, api_client, admin_user):
        """Test getting email status successfully."""
        mock_settings.EMAIL_NOTIFICATIONS_ENABLED = True
        mock_settings.EMAIL_HOST_USER = 'test@test.com'
        mock_settings.EMAIL_HOST_PASSWORD = 'password'
        mock_settings.SENDGRID_API_KEY = 'key123'
        mock_settings.EMAIL_NOTIFICATION_TYPES = ['welcome', 'reset']
        mock_settings.DEFAULT_FROM_EMAIL = 'noreply@test.com'
        mock_settings.EMAIL_HOST = 'smtp.test.com'
        mock_settings.EMAIL_PORT = 587
        
        mock_email_service.smtp_backend = MagicMock()
        mock_email_service.sendgrid_client = MagicMock()
        
        api_client.force_authenticate(user=admin_user)
        
        view = EmailStatusView()
        request = Mock()
        request.user = admin_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'data' in response.data
        assert response.data['data']['email_enabled'] is True
    
    @patch('api.views.admin.email_views.settings')
    def test_email_status_exception(self, mock_settings, api_client, admin_user):
        """Test exception handling in email status."""
        mock_settings.EMAIL_NOTIFICATIONS_ENABLED = True
        mock_settings.__getattr__ = Mock(side_effect=Exception("Config error"))
        
        api_client.force_authenticate(user=admin_user)
        
        view = EmailStatusView()
        request = Mock()
        request.user = admin_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data


@pytest.mark.django_db
class TestSendTestEmailView:
    """Tests for SendTestEmailView."""
    
    def test_send_test_email_requires_admin(self, api_client):
        """Test that non-admin users cannot send test emails."""
        response = api_client.post('/api/v1/admin/emails/test/', {})
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_send_test_email_missing_email(self, api_client, admin_user):
        """Test sending test email without email address."""
        api_client.force_authenticate(user=admin_user)
        
        view = SendTestEmailView()
        request = Mock()
        request.user = admin_user
        request.data = {}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    @patch('api.views.admin.email_views.send_custom_email')
    def test_send_test_email_success(self, mock_send_email, api_client, admin_user):
        """Test sending test email successfully."""
        mock_send_email.return_value = {
            'success': True,
            'backend_used': 'SMTP',
            'timestamp': '2024-01-01T00:00:00'
        }
        
        api_client.force_authenticate(user=admin_user)
        
        view = SendTestEmailView()
        request = Mock()
        request.user = admin_user
        request.data = {'to_email': 'test@test.com', 'use_sendgrid': False}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        mock_send_email.assert_called_once()
    
    @patch('api.views.admin.email_views.send_custom_email')
    def test_send_test_email_failure(self, mock_send_email, api_client, admin_user):
        """Test sending test email failure."""
        mock_send_email.return_value = {
            'success': False,
            'error': 'SMTP connection failed'
        }
        
        api_client.force_authenticate(user=admin_user)
        
        view = SendTestEmailView()
        request = Mock()
        request.user = admin_user
        request.data = {'to_email': 'test@test.com'}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data


@pytest.mark.django_db
class TestSendBulkNotificationView:
    """Tests for SendBulkNotificationView."""
    
    def test_send_bulk_notification_requires_admin(self, api_client):
        """Test that non-admin users cannot send bulk notifications."""
        response = api_client.post('/api/v1/admin/emails/bulk/', {})
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_send_bulk_notification_missing_type(self, api_client, admin_user):
        """Test sending bulk notification without notification type."""
        api_client.force_authenticate(user=admin_user)
        
        view = SendBulkNotificationView()
        request = Mock()
        request.user = admin_user
        request.data = {}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_send_bulk_notification_missing_emails(self, api_client, admin_user):
        """Test sending bulk notification without email list."""
        api_client.force_authenticate(user=admin_user)
        
        view = SendBulkNotificationView()
        request = Mock()
        request.user = admin_user
        request.data = {'notification_type': 'welcome'}
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    @patch('api.views.admin.email_views.send_bulk_email_notification')
    def test_send_bulk_notification_success(self, mock_send_bulk, api_client, admin_user):
        """Test sending bulk notification successfully."""
        mock_send_bulk.return_value = {
            'total_emails': 2,
            'successful': 2,
            'failed': 0,
            'batches_processed': 1,
            'errors': []
        }
        
        api_client.force_authenticate(user=admin_user)
        
        view = SendBulkNotificationView()
        request = Mock()
        request.user = admin_user
        request.data = {
            'notification_type': 'welcome',
            'user_emails': ['test1@test.com', 'test2@test.com']
        }
        
        response = view.post(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        mock_send_bulk.assert_called_once()


@pytest.mark.django_db
class TestEmailTemplatePreviewView:
    """Tests for EmailTemplatePreviewView."""
    
    def test_template_preview_requires_admin(self, api_client):
        """Test that non-admin users cannot preview templates."""
        response = api_client.get('/api/v1/admin/emails/templates/preview/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_template_preview_missing_type(self, api_client, admin_user):
        """Test previewing template without template type."""
        api_client.force_authenticate(user=admin_user)
        
        view = EmailTemplatePreviewView()
        request = Mock()
        request.user = admin_user
        request.query_params = {}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    @patch('api.views.admin.email_views.email_notification_service')
    def test_template_preview_success(self, mock_email_service, api_client, admin_user):
        """Test previewing template successfully."""
        mock_email_service.email_service._render_template.return_value = (
            '<html>Test</html>',
            'Test text'
        )
        mock_email_service._get_default_subject.return_value = 'Test Subject'
        
        api_client.force_authenticate(user=admin_user)
        
        view = EmailTemplatePreviewView()
        request = Mock()
        request.user = admin_user
        request.query_params = {'template_type': 'welcome'}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'html_content' in response.data['data']


@pytest.mark.django_db
class TestEmailLogsView:
    """Tests for EmailLogsView."""
    
    def test_email_logs_requires_admin(self, api_client):
        """Test that non-admin users cannot access email logs."""
        response = api_client.get('/api/v1/admin/emails/logs/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_email_logs_success(self, api_client, admin_user):
        """Test getting email logs successfully."""
        api_client.force_authenticate(user=admin_user)
        
        view = EmailLogsView()
        request = Mock()
        request.user = admin_user
        request.query_params = {}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'data' in response.data
        assert 'total_emails' in response.data['data']

