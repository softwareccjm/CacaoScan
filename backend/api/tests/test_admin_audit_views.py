"""
Tests for admin audit views.
Covers ActivityLogListView, LoginHistoryListView, and AuditStatsView.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from api.views.admin.audit_views import (
    ActivityLogListView,
    LoginHistoryListView,
    AuditStatsView
)
from audit.models import LoginHistory


@pytest.fixture
def admin_user(db):
    """Create admin user for tests."""
    user = User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='testpass123',
        is_staff=True,
        is_superuser=True
    )
    return user


@pytest.fixture
def regular_user(db):
    """Create regular user for tests."""
    user = User.objects.create_user(
        username='regular',
        email='regular@test.com',
        password='testpass123'
    )
    return user


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def activity_log_model():
    """Mock ActivityLog model."""
    from unittest.mock import MagicMock
    
    ActivityLog = MagicMock()
    ActivityLog.objects = MagicMock()
    ActivityLog.DoesNotExist = Exception
    
    return ActivityLog


@pytest.mark.django_db
class TestActivityLogListView:
    """Tests for ActivityLogListView."""
    
    def test_list_activity_logs_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/admin/audit/activity-logs/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_activity_logs_requires_admin(self, api_client, regular_user):
        """Test that non-admin users cannot access."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.get('/api/v1/admin/audit/activity-logs/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data
        assert 'No tienes permisos' in response.data['error']
    
    @patch('api.views.admin.audit_views.ActivityLog')
    def test_list_activity_logs_success_empty(self, mock_activity_log, api_client, admin_user):
        """Test listing activity logs when model is None."""
        mock_activity_log.return_value = None
        mock_activity_log.objects = None
        
        api_client.force_authenticate(user=admin_user)
        
        view = ActivityLogListView()
        request = Mock()
        request.user = admin_user
        request.GET = {}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == []
        assert response.data['count'] == 0
    
    @patch('api.views.admin.audit_views.ActivityLog')
    def test_list_activity_logs_with_filters(self, mock_activity_log, api_client, admin_user):
        """Test listing activity logs with filters."""
        # Create mock queryset
        mock_log = MagicMock()
        mock_log.id = 1
        mock_log.usuario = admin_user
        mock_log.accion = 'CREATE'
        mock_log.modelo = 'Finca'
        mock_log.objeto_id = 123
        mock_log.descripcion = 'Test description'
        mock_log.ip_address = '127.0.0.1'
        mock_log.timestamp = timezone.now()
        mock_log.datos_antes = None
        mock_log.datos_despues = {'field': 'value'}
        mock_log.get_accion_display.return_value = 'Crear'
        
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = [mock_log]
        
        mock_activity_log.objects.all.return_value = mock_queryset
        
        api_client.force_authenticate(user=admin_user)
        
        view = ActivityLogListView()
        request = Mock()
        request.user = admin_user
        request.GET = {
            'usuario': 'admin',
            'accion': 'CREATE',
            'modelo': 'Finca',
            'ip_address': '127.0.0.1'
        }
        
        with patch.object(view, 'paginate_queryset') as mock_paginate:
            mock_paginate.return_value = Mock(
                status_code=status.HTTP_200_OK,
                data={
                    'results': [{
                        'id': 1,
                        'usuario': 'admin',
                        'accion': 'CREATE'
                    }],
                    'count': 1
                }
            )
            response = view.get(request)
            assert response.status_code == status.HTTP_200_OK
    
    @patch('api.views.admin.audit_views.ActivityLog')
    def test_list_activity_logs_invalid_date_format(self, mock_activity_log, api_client, admin_user):
        """Test listing activity logs with invalid date format."""
        mock_queryset = MagicMock()
        mock_queryset.select_related.return_value = mock_queryset
        mock_activity_log.objects.all.return_value = mock_queryset
        
        api_client.force_authenticate(user=admin_user)
        
        view = ActivityLogListView()
        request = Mock()
        request.user = admin_user
        request.GET = {'fecha_desde': 'invalid-date'}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'Formato de fecha inválido' in response.data['error']
    
    @patch('api.views.admin.audit_views.ActivityLog')
    def test_list_activity_logs_exception_handling(self, mock_activity_log, api_client, admin_user):
        """Test exception handling in list activity logs."""
        mock_activity_log.objects.all.side_effect = Exception("Database error")
        
        api_client.force_authenticate(user=admin_user)
        
        view = ActivityLogListView()
        request = Mock()
        request.user = admin_user
        request.GET = {}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data


@pytest.mark.django_db
class TestLoginHistoryListView:
    """Tests for LoginHistoryListView."""
    
    def test_list_login_history_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/admin/audit/login-history/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_login_history_requires_admin(self, api_client, regular_user):
        """Test that non-admin users cannot access."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.get('/api/v1/admin/audit/login-history/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_login_history_success(self, api_client, admin_user, db):
        """Test listing login history successfully."""
        # Create test login history
        login_history = LoginHistory.objects.create(
            usuario=admin_user,
            ip_address='127.0.0.1',
            user_agent='Test Agent',
            login_time=timezone.now(),
            success=True
        )
        
        api_client.force_authenticate(user=admin_user)
        
        view = LoginHistoryListView()
        request = Mock()
        request.user = admin_user
        request.GET = {}
        
        with patch.object(view, 'paginate_queryset') as mock_paginate:
            mock_paginate.return_value = Mock(
                status_code=status.HTTP_200_OK,
                data={
                    'results': [{
                        'id': login_history.id,
                        'usuario': 'admin',
                        'ip_address': '127.0.0.1'
                    }],
                    'count': 1
                }
            )
            response = view.get(request)
            assert response.status_code == status.HTTP_200_OK
    
    def test_list_login_history_with_filters(self, api_client, admin_user, db):
        """Test listing login history with filters."""
        LoginHistory.objects.create(
            usuario=admin_user,
            ip_address='127.0.0.1',
            login_time=timezone.now(),
            success=True
        )
        
        api_client.force_authenticate(user=admin_user)
        
        view = LoginHistoryListView()
        request = Mock()
        request.user = admin_user
        request.GET = {
            'usuario': 'admin',
            'ip_address': '127.0.0.1',
            'success': 'true',
            'fecha_desde': '2024-01-01',
            'fecha_hasta': '2024-12-31'
        }
        
        with patch.object(view, 'paginate_queryset') as mock_paginate:
            mock_paginate.return_value = Mock(
                status_code=status.HTTP_200_OK,
                data={'results': [], 'count': 0}
            )
            response = view.get(request)
            assert response.status_code == status.HTTP_200_OK
    
    def test_list_login_history_invalid_date_format(self, api_client, admin_user):
        """Test listing login history with invalid date format."""
        api_client.force_authenticate(user=admin_user)
        
        view = LoginHistoryListView()
        request = Mock()
        request.user = admin_user
        request.GET = {'fecha_desde': 'invalid-date'}
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Formato de fecha inválido' in response.data['error']
    
    def test_list_login_history_exception_handling(self, api_client, admin_user):
        """Test exception handling in list login history."""
        api_client.force_authenticate(user=admin_user)
        
        view = LoginHistoryListView()
        request = Mock()
        request.user = admin_user
        request.GET = {}
        
        with patch('api.views.admin.audit_views.LoginHistory') as mock_login:
            mock_login.objects.all.side_effect = Exception("Database error")
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert 'error' in response.data


@pytest.mark.django_db
class TestAuditStatsView:
    """Tests for AuditStatsView."""
    
    def test_audit_stats_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/admin/audit/stats/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_audit_stats_requires_admin(self, api_client, regular_user):
        """Test that non-admin users cannot access."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.get('/api/v1/admin/audit/stats/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('api.views.admin.audit_views.ActivityLog')
    def test_audit_stats_success(self, mock_activity_log, api_client, admin_user, db):
        """Test getting audit stats successfully."""
        # Setup mocks
        mock_activity_log.objects.count.return_value = 10
        mock_activity_log.objects.filter.return_value.count.return_value = 5
        mock_activity_log.objects.values.return_value.annotate.return_value.values_list.return_value = [
            ('CREATE', 3),
            ('UPDATE', 2)
        ]
        
        # Create test login history
        LoginHistory.objects.create(
            usuario=admin_user,
            ip_address='127.0.0.1',
            login_time=timezone.now(),
            success=True
        )
        
        api_client.force_authenticate(user=admin_user)
        
        view = AuditStatsView()
        request = Mock()
        request.user = admin_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'activity_log' in response.data
        assert 'login_history' in response.data
        assert 'generated_at' in response.data
    
    @patch('api.views.admin.audit_views.ActivityLog')
    def test_audit_stats_exception_handling(self, mock_activity_log, api_client, admin_user):
        """Test exception handling in audit stats."""
        mock_activity_log.objects.count.side_effect = Exception("Database error")
        
        api_client.force_authenticate(user=admin_user)
        
        view = AuditStatsView()
        request = Mock()
        request.user = admin_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data

