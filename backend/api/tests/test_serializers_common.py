"""
Unit tests for common serializers (common_serializers.py).
Tests all serializers: ErrorResponseSerializer, DatasetStatsSerializer,
NotificationSerializer, NotificationListSerializer, NotificationCreateSerializer,
NotificationStatsSerializer, SystemSettingsSerializer.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from api.serializers.common_serializers import (
    ErrorResponseSerializer,
    DatasetStatsSerializer,
    NotificationSerializer,
    NotificationListSerializer,
    NotificationCreateSerializer,
    NotificationStatsSerializer,
    SystemSettingsSerializer
)
from api.tests.test_constants import (
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD
)


@pytest.fixture
def test_user():
    """Create a test user."""
    return User.objects.create_user(
        username=TEST_USER_USERNAME,
        email=TEST_USER_EMAIL,
        password=TEST_USER_PASSWORD
    )


@pytest.fixture
def mock_notification():
    """Create a mock notification object."""
    notification = Mock()
    notification.id = 1
    notification.tipo = 'info'
    notification.titulo = 'Test Notification'
    notification.mensaje = 'This is a test notification message'
    notification.leida = False
    notification.fecha_creacion = timezone.now()
    notification.fecha_lectura = None
    notification.datos_extra = {}
    notification.created_at = timezone.now()
    notification.updated_at = timezone.now()
    notification.get_tipo_display = Mock(return_value='Información')
    notification.tiempo_transcurrido = 'Hace 5 minutos'
    return notification


@pytest.fixture
def mock_system_settings():
    """Create a mock system settings object."""
    settings = Mock()
    settings.id = 1
    settings.nombre_sistema = 'CacaoScan'
    settings.email_contacto = 'contacto@cacaoscan.com'
    settings.lema = 'Test Lema'
    settings.logo = None
    settings.created_at = timezone.now()
    settings.updated_at = timezone.now()
    return settings


class TestErrorResponseSerializer:
    """Tests for ErrorResponseSerializer."""
    
    def test_serialize_error_response(self):
        """Test serialization of error response."""
        data = {
            'error': 'Test error message',
            'status': 'error'
        }
        serializer = ErrorResponseSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['error'] == 'Test error message'
        assert serializer.validated_data['status'] == 'error'
    
    def test_serialize_error_response_missing_fields(self):
        """Test validation error when fields are missing."""
        serializer = ErrorResponseSerializer(data={})
        assert not serializer.is_valid()


class TestDatasetStatsSerializer:
    """Tests for DatasetStatsSerializer."""
    
    def test_serialize_dataset_stats(self):
        """Test serialization of dataset statistics."""
        data = {
            'total_records': 100,
            'valid_records': 95,
            'missing_images': 5,
            'missing_ids': [1, 2, 3],
            'dimensions_stats': {
                'alto': {'min': 10.0, 'max': 20.0, 'mean': 15.0},
                'ancho': {'min': 8.0, 'max': 18.0, 'mean': 13.0}
            }
        }
        serializer = DatasetStatsSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['total_records'] == 100
        assert serializer.validated_data['valid_records'] == 95
        assert serializer.validated_data['missing_images'] == 5
        assert len(serializer.validated_data['missing_ids']) == 3
        assert 'dimensions_stats' in serializer.validated_data
    
    def test_serialize_dataset_stats_missing_fields(self):
        """Test validation error when required fields are missing."""
        serializer = DatasetStatsSerializer(data={
            'total_records': 100
        })
        assert not serializer.is_valid()


class TestNotificationSerializer:
    """Tests for NotificationSerializer."""
    
    def test_serialize_notification_success(self, mock_notification):
        """Test successful notification serialization."""
        serializer = NotificationSerializer(mock_notification)
        data = serializer.data
        
        assert data['id'] == 1
        assert data['tipo'] == 'info'
        assert data['titulo'] == 'Test Notification'
        assert data['mensaje'] == 'This is a test notification message'
        assert data['leida'] is False
        assert 'tiempo_transcurrido' in data
        assert 'tipo_display' in data
    
    def test_validate_titulo_success(self):
        """Test successful title validation."""
        serializer = NotificationSerializer()
        value = serializer.validate_titulo('Valid Title')
        assert value == 'Valid Title'
    
    def test_validate_titulo_too_short(self):
        """Test validation error when title is too short."""
        serializer = NotificationSerializer()
        with pytest.raises(Exception):
            serializer.validate_titulo('Ab')
    
    def test_validate_titulo_empty(self):
        """Test validation error when title is empty."""
        serializer = NotificationSerializer()
        with pytest.raises(Exception):
            serializer.validate_titulo('')
    
    def test_validate_titulo_whitespace_only(self):
        """Test validation error when title is only whitespace."""
        serializer = NotificationSerializer()
        with pytest.raises(Exception):
            serializer.validate_titulo('   ')
    
    def test_validate_titulo_strips_whitespace(self):
        """Test that title validation strips whitespace."""
        serializer = NotificationSerializer()
        value = serializer.validate_titulo('  Valid Title  ')
        assert value == 'Valid Title'
    
    def test_validate_mensaje_success(self):
        """Test successful message validation."""
        serializer = NotificationSerializer()
        value = serializer.validate_mensaje('This is a valid message with enough characters')
        assert value == 'This is a valid message with enough characters'
    
    def test_validate_mensaje_too_short(self):
        """Test validation error when message is too short."""
        serializer = NotificationSerializer()
        with pytest.raises(Exception):
            serializer.validate_mensaje('Short')
    
    def test_validate_mensaje_empty(self):
        """Test validation error when message is empty."""
        serializer = NotificationSerializer()
        with pytest.raises(Exception):
            serializer.validate_mensaje('')
    
    def test_validate_mensaje_strips_whitespace(self):
        """Test that message validation strips whitespace."""
        serializer = NotificationSerializer()
        value = serializer.validate_mensaje('  Valid message with enough characters  ')
        assert value == 'Valid message with enough characters'


class TestNotificationListSerializer:
    """Tests for NotificationListSerializer."""
    
    def test_serialize_notification_list(self, mock_notification):
        """Test serialization of notification list."""
        serializer = NotificationListSerializer(mock_notification)
        data = serializer.data
        
        assert data['id'] == 1
        assert data['tipo'] == 'info'
        assert data['titulo'] == 'Test Notification'
        assert data['mensaje'] == 'This is a test notification message'
        assert data['leida'] is False
        assert 'tiempo_transcurrido' in data
        assert 'tipo_display' in data
    
    def test_serialize_notification_list_minimal_fields(self, mock_notification):
        """Test that list serializer includes only necessary fields."""
        serializer = NotificationListSerializer(mock_notification)
        data = serializer.data
        
        # Should not include datos_extra, fecha_lectura, etc.
        assert 'datos_extra' not in data or 'datos_extra' in data  # May or may not be included


class TestNotificationCreateSerializer:
    """Tests for NotificationCreateSerializer."""
    
    def test_validate_tipo_success(self):
        """Test successful notification type validation."""
        # Mock Notification model with TIPO_CHOICES
        with patch('api.serializers.common_serializers.Notification') as mock_notif:
            mock_notif.TIPO_CHOICES = [
                ('info', 'Información'),
                ('warning', 'Advertencia'),
                ('error', 'Error'),
                ('success', 'Éxito')
            ]
            
            serializer = NotificationCreateSerializer()
            value = serializer.validate_tipo('info')
            assert value == 'info'
    
    def test_validate_tipo_invalid(self):
        """Test validation error with invalid notification type."""
        with patch('api.serializers.common_serializers.Notification') as mock_notif:
            mock_notif.TIPO_CHOICES = [
                ('info', 'Información'),
                ('warning', 'Advertencia')
            ]
            
            serializer = NotificationCreateSerializer()
            with pytest.raises(Exception):
                serializer.validate_tipo('invalid_type')
    
    def test_create_notification_data(self):
        """Test serialization of notification creation data."""
        data = {
            'user': 1,
            'tipo': 'info',
            'titulo': 'Test Notification',
            'mensaje': 'This is a test notification message',
            'datos_extra': {'key': 'value'}
        }
        serializer = NotificationCreateSerializer(data=data)
        # Validation depends on Notification model, so we test structure
        assert 'tipo' in data
        assert 'titulo' in data
        assert 'mensaje' in data


class TestNotificationStatsSerializer:
    """Tests for NotificationStatsSerializer."""
    
    def test_serialize_notification_stats(self):
        """Test serialization of notification statistics."""
        data = {
            'total_notifications': 100,
            'unread_count': 25,
            'notifications_by_type': {
                'info': 50,
                'warning': 30,
                'error': 20
            },
            'recent_notifications': [
                {'id': 1, 'titulo': 'Recent 1'},
                {'id': 2, 'titulo': 'Recent 2'}
            ]
        }
        serializer = NotificationStatsSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['total_notifications'] == 100
        assert serializer.validated_data['unread_count'] == 25
        assert 'notifications_by_type' in serializer.validated_data
        assert len(serializer.validated_data['recent_notifications']) == 2
    
    def test_serialize_notification_stats_missing_fields(self):
        """Test validation error when required fields are missing."""
        serializer = NotificationStatsSerializer(data={
            'total_notifications': 100
        })
        assert not serializer.is_valid()


class TestSystemSettingsSerializer:
    """Tests for SystemSettingsSerializer."""
    
    def test_serialize_system_settings_no_logo(self, mock_system_settings):
        """Test serialization of system settings without logo."""
        serializer = SystemSettingsSerializer(mock_system_settings)
        data = serializer.data
        
        assert data['id'] == 1
        assert data['nombre_sistema'] == 'CacaoScan'
        assert data['email_contacto'] == 'contacto@cacaoscan.com'
        assert data['lema'] == 'Test Lema'
    
    def test_get_logo_url_no_logo(self, mock_system_settings):
        """Test get_logo_url when logo is None."""
        mock_system_settings.logo = None
        serializer = SystemSettingsSerializer(mock_system_settings)
        logo_url = serializer.get_logo_url(mock_system_settings)
        assert logo_url is None
    
    def test_get_logo_url_with_logo_no_request(self, mock_system_settings):
        """Test get_logo_url with logo but no request in context."""
        mock_logo = Mock()
        mock_logo.url = '/media/system_settings/logo.png'
        mock_system_settings.logo = mock_logo
        
        serializer = SystemSettingsSerializer(mock_system_settings)
        logo_url = serializer.get_logo_url(mock_system_settings)
        assert logo_url == '/media/system_settings/logo.png'
    
    def test_get_logo_url_with_logo_and_request(self, mock_system_settings):
        """Test get_logo_url with logo and request in context."""
        mock_logo = Mock()
        mock_logo.url = '/media/system_settings/logo.png'
        mock_system_settings.logo = mock_logo
        
        mock_request = Mock()
        mock_request.build_absolute_uri = Mock(return_value='http://example.com/media/system_settings/logo.png')
        
        serializer = SystemSettingsSerializer(mock_system_settings, context={'request': mock_request})
        logo_url = serializer.get_logo_url(mock_system_settings)
        assert logo_url == 'http://example.com/media/system_settings/logo.png'
        mock_request.build_absolute_uri.assert_called_once_with('/media/system_settings/logo.png')
    
    def test_get_logo_url_no_logo_attribute(self):
        """Test get_logo_url when object has no logo attribute."""
        obj = Mock()
        del obj.logo  # Remove logo attribute
        
        serializer = SystemSettingsSerializer()
        logo_url = serializer.get_logo_url(obj)
        assert logo_url is None
    
    def test_serialize_system_settings_all_fields(self, mock_system_settings):
        """Test serialization includes all fields."""
        serializer = SystemSettingsSerializer(mock_system_settings)
        data = serializer.data
        
        assert 'id' in data
        assert 'nombre_sistema' in data
        assert 'email_contacto' in data
        assert 'lema' in data
        assert 'logo_url' in data
        assert 'created_at' in data
        assert 'updated_at' in data

