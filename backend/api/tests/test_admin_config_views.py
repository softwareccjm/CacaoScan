"""
Tests for admin config views.
Covers SystemSettingsView, SystemGeneralConfigView, SystemSecurityConfigView, SystemMLConfigView, and SystemInfoView.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from api.views.admin.config_views import (
    SystemSettingsView,
    SystemGeneralConfigView,
    SystemSecurityConfigView,
    SystemMLConfigView,
    SystemInfoView
)


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


@pytest.mark.django_db
class TestSystemSettingsView:
    """Tests for SystemSettingsView."""
    
    def test_get_settings_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/admin/config/settings/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_get_settings_success(self, mock_settings, api_client, admin_user):
        """Test getting system settings successfully."""
        mock_settings_instance = MagicMock()
        mock_settings_instance.nombre_sistema = 'CacaoScan'
        mock_settings_instance.email_contacto = 'test@test.com'
        mock_settings.get_singleton.return_value = mock_settings_instance
        
        api_client.force_authenticate(user=admin_user)
        
        view = SystemSettingsView()
        request = Mock()
        request.user = admin_user
        
        with patch('api.views.admin.config_views.SystemSettingsSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.data = {'nombre_sistema': 'CacaoScan'}
            mock_serializer.return_value = mock_serializer_instance
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_200_OK
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_get_settings_exception(self, mock_settings, api_client, admin_user):
        """Test exception handling in get settings."""
        mock_settings.get_singleton.side_effect = Exception("Database error")
        
        api_client.force_authenticate(user=admin_user)
        
        view = SystemSettingsView()
        request = Mock()
        request.user = admin_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_put_settings_requires_admin(self, mock_settings, api_client, regular_user):
        """Test that non-admin users cannot update settings."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.put('/api/v1/admin/config/settings/', {})
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_put_settings_success(self, mock_settings, api_client, admin_user):
        """Test updating system settings successfully."""
        mock_settings_instance = MagicMock()
        mock_settings.get_singleton.return_value = mock_settings_instance
        
        api_client.force_authenticate(user=admin_user)
        
        view = SystemSettingsView()
        request = Mock()
        request.user = admin_user
        request.data = {'nombre_sistema': 'New Name'}
        
        with patch('api.views.admin.config_views.SystemSettingsSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.is_valid.return_value = True
            mock_serializer_instance.data = {'nombre_sistema': 'New Name'}
            mock_serializer.return_value = mock_serializer_instance
            
            response = view.put(request)
            
            assert response.status_code == status.HTTP_200_OK
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_put_settings_invalid_data(self, mock_settings, api_client, admin_user):
        """Test updating settings with invalid data."""
        mock_settings_instance = MagicMock()
        mock_settings.get_singleton.return_value = mock_settings_instance
        
        api_client.force_authenticate(user=admin_user)
        
        view = SystemSettingsView()
        request = Mock()
        request.user = admin_user
        request.data = {}
        
        with patch('api.views.admin.config_views.SystemSettingsSerializer') as mock_serializer:
            mock_serializer_instance = MagicMock()
            mock_serializer_instance.is_valid.return_value = False
            mock_serializer_instance.errors = {'field': 'error'}
            mock_serializer.return_value = mock_serializer_instance
            
            response = view.put(request)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestSystemGeneralConfigView:
    """Tests for SystemGeneralConfigView."""
    
    def test_get_general_config_public_access(self, api_client):
        """Test that general config is publicly accessible."""
        view = SystemGeneralConfigView()
        request = Mock()
        request.build_absolute_uri = Mock(return_value='http://test.com/logo.png')
        
        with patch('api.views.admin.config_views.SystemSettings') as mock_settings:
            mock_settings_instance = MagicMock()
            mock_settings_instance.nombre_sistema = 'CacaoScan'
            mock_settings_instance.email_contacto = 'test@test.com'
            mock_settings_instance.lema = 'Test slogan'
            mock_settings_instance.logo = None
            mock_settings.get_singleton.return_value = mock_settings_instance
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_200_OK
            assert 'nombre_sistema' in response.data
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_get_general_config_no_settings(self, mock_settings, api_client):
        """Test getting general config when no settings exist."""
        mock_settings.get_singleton.return_value = None
        
        view = SystemGeneralConfigView()
        request = Mock()
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nombre_sistema'] == 'CacaoScan'
        assert response.data['email_contacto'] == 'contacto@cacaoscan.com'
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_get_general_config_exception(self, mock_settings, api_client):
        """Test exception handling returns default values."""
        mock_settings.get_singleton.side_effect = Exception("Database error")
        
        view = SystemGeneralConfigView()
        request = Mock()
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nombre_sistema'] == 'CacaoScan'
    
    def test_put_general_config_requires_admin(self, api_client, regular_user):
        """Test that non-admin users cannot update general config."""
        api_client.force_authenticate(user=regular_user)
        response = api_client.put('/api/v1/admin/config/general/', {})
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_put_general_config_success(self, mock_settings, api_client, admin_user):
        """Test updating general config successfully."""
        mock_settings_instance = MagicMock()
        mock_settings_instance.logo = None
        mock_settings.get_singleton.return_value = mock_settings_instance
        
        api_client.force_authenticate(user=admin_user)
        
        view = SystemGeneralConfigView()
        request = Mock()
        request.user = admin_user
        request.data = {'nombre_sistema': 'New Name'}
        request.build_absolute_uri = Mock(return_value='http://test.com/logo.png')
        
        response = view.put(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nombre_sistema'] == 'New Name'


@pytest.mark.django_db
class TestSystemSecurityConfigView:
    """Tests for SystemSecurityConfigView."""
    
    def test_get_security_config_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/admin/config/security/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_get_security_config_success(self, mock_settings, api_client, admin_user):
        """Test getting security config successfully."""
        mock_settings_instance = MagicMock()
        mock_settings_instance.recaptcha_enabled = True
        mock_settings_instance.session_timeout = 60
        mock_settings_instance.login_attempts = 5
        mock_settings_instance.two_factor_auth = False
        mock_settings.get_singleton.return_value = mock_settings_instance
        
        api_client.force_authenticate(user=admin_user)
        
        view = SystemSecurityConfigView()
        request = Mock()
        request.user = admin_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'recaptcha_enabled' in response.data
        assert response.data['recaptcha_enabled'] is True
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_get_security_config_no_settings(self, mock_settings, api_client, admin_user):
        """Test getting security config when no settings exist."""
        mock_settings.get_singleton.return_value = None
        
        api_client.force_authenticate(user=admin_user)
        
        view = SystemSecurityConfigView()
        request = Mock()
        request.user = admin_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['recaptcha_enabled'] is True
        assert response.data['session_timeout'] == 60
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_put_security_config_success(self, mock_settings, api_client, admin_user):
        """Test updating security config successfully."""
        mock_settings_instance = MagicMock()
        mock_settings_instance.recaptcha_enabled = True
        mock_settings_instance.session_timeout = 60
        mock_settings_instance.login_attempts = 5
        mock_settings_instance.two_factor_auth = False
        mock_settings.get_singleton.return_value = mock_settings_instance
        
        api_client.force_authenticate(user=admin_user)
        
        view = SystemSecurityConfigView()
        request = Mock()
        request.user = admin_user
        request.data = {'recaptcha_enabled': False}
        
        response = view.put(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['recaptcha_enabled'] is False


@pytest.mark.django_db
class TestSystemMLConfigView:
    """Tests for SystemMLConfigView."""
    
    def test_get_ml_config_requires_authentication(self, api_client):
        """Test that unauthenticated users cannot access."""
        response = api_client.get('/api/v1/admin/config/ml/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_get_ml_config_success(self, mock_settings, api_client, admin_user):
        """Test getting ML config successfully."""
        mock_settings_instance = MagicMock()
        mock_settings_instance.active_model = 'yolov8'
        mock_settings_instance.last_training = timezone.now()
        mock_settings.get_singleton.return_value = mock_settings_instance
        
        api_client.force_authenticate(user=admin_user)
        
        view = SystemMLConfigView()
        request = Mock()
        request.user = admin_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'active_model' in response.data
        assert response.data['active_model'] == 'yolov8'
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_get_ml_config_no_settings(self, mock_settings, api_client, admin_user):
        """Test getting ML config when no settings exist."""
        mock_settings.get_singleton.return_value = None
        
        api_client.force_authenticate(user=admin_user)
        
        view = SystemMLConfigView()
        request = Mock()
        request.user = admin_user
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['active_model'] == 'yolov8'
        assert response.data['last_training'] is None
    
    @patch('api.views.admin.config_views.SystemSettings')
    def test_put_ml_config_success(self, mock_settings, api_client, admin_user):
        """Test updating ML config successfully."""
        mock_settings_instance = MagicMock()
        mock_settings_instance.active_model = 'yolov8'
        mock_settings_instance.last_training = None
        mock_settings.get_singleton.return_value = mock_settings_instance
        
        api_client.force_authenticate(user=admin_user)
        
        view = SystemMLConfigView()
        request = Mock()
        request.user = admin_user
        request.data = {'active_model': 'yolov9'}
        
        response = view.put(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['active_model'] == 'yolov9'


@pytest.mark.django_db
class TestSystemInfoView:
    """Tests for SystemInfoView."""
    
    def test_get_system_info_public_access(self, api_client):
        """Test that system info is publicly accessible."""
        view = SystemInfoView()
        request = Mock()
        
        response = view.get(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'system' in response.data
        assert response.data['system'] == 'CacaoScan'
        assert 'version' in response.data
        assert 'status' in response.data
    
    def test_get_system_info_exception_handling(self, api_client):
        """Test exception handling returns minimal data."""
        view = SystemInfoView()
        request = Mock()
        
        with patch('api.views.admin.config_views.django') as mock_django:
            mock_django.get_version.side_effect = Exception("Error")
            
            response = view.get(request)
            
            assert response.status_code == status.HTTP_200_OK
            assert 'system' in response.data
            assert 'error' in response.data

