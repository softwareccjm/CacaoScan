"""
Unit tests for core models (TimeStampedModel, SystemSettings).
Tests cover model creation, properties, methods, and singleton pattern.
"""
import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError

from core.models import TimeStampedModel, SystemSettings


class TestTimeStampedModel:
    """Tests for TimeStampedModel abstract base class."""
    
    def test_timestamped_model_is_abstract(self):
        """Test that TimeStampedModel is abstract."""
        assert TimeStampedModel._meta.abstract is True
    
    def test_timestamped_model_has_created_at_field(self):
        """Test that TimeStampedModel has created_at field."""
        assert hasattr(TimeStampedModel, 'created_at')
    
    def test_timestamped_model_has_updated_at_field(self):
        """Test that TimeStampedModel has updated_at field."""
        assert hasattr(TimeStampedModel, 'updated_at')
    
    def test_timestamped_model_cannot_be_instantiated_directly(self):
        """Test that TimeStampedModel cannot be instantiated directly."""
        with pytest.raises(Exception):  # Should raise some error when trying to create
            TimeStampedModel.objects.create()


class TestSystemSettings:
    """Tests for SystemSettings model."""
    
    def test_system_settings_creation(self):
        """Test basic system settings creation."""
        settings = SystemSettings.objects.create(
            nombre_sistema='CacaoScan Test',
            email_contacto='test@cacaoscan.com',
            lema='Test lema'
        )
        
        assert settings.nombre_sistema == 'CacaoScan Test'
        assert settings.email_contacto == 'test@cacaoscan.com'
        assert settings.lema == 'Test lema'
        assert settings.recaptcha_enabled is True
        assert settings.session_timeout == 60
        assert settings.login_attempts == 5
        assert settings.two_factor_auth is False
        assert settings.active_model == 'yolov8'
        assert settings.created_at is not None
        assert settings.updated_at is not None
    
    def test_system_settings_default_values(self):
        """Test system settings default values."""
        settings = SystemSettings.objects.create()
        
        assert settings.nombre_sistema == 'CacaoScan'
        assert settings.email_contacto == 'contacto@cacaoscan.com'
        assert settings.lema == 'La mejor plataforma para el control de calidad del cacao'
        assert settings.recaptcha_enabled is True
        assert settings.session_timeout == 60
        assert settings.login_attempts == 5
        assert settings.two_factor_auth is False
        assert settings.active_model == 'yolov8'
    
    def test_system_settings_str_representation(self):
        """Test string representation of system settings."""
        settings = SystemSettings.objects.create(
            nombre_sistema='CacaoScan Pro'
        )
        
        assert str(settings) == 'Configuración de CacaoScan Pro'
    
    def test_system_settings_get_singleton_creates_new(self):
        """Test get_singleton creates new instance if none exists."""
        # Delete any existing instances
        SystemSettings.objects.all().delete()
        
        settings = SystemSettings.get_singleton()
        
        assert settings is not None
        assert isinstance(settings, SystemSettings)
        assert settings.pk == 1
    
    def test_system_settings_get_singleton_returns_existing(self):
        """Test get_singleton returns existing instance."""
        # Create an instance
        existing = SystemSettings.objects.create(
            nombre_sistema='Existing Settings',
            pk=1
        )
        
        settings = SystemSettings.get_singleton()
        
        assert settings.id == existing.id
        assert settings.nombre_sistema == 'Existing Settings'
    
    def test_system_settings_save_forces_pk_to_one(self):
        """Test that save method forces pk to 1."""
        settings = SystemSettings.objects.create(
            nombre_sistema='Test Settings'
        )
        
        # Try to change pk
        settings.pk = 999
        settings.save()
        
        # Should still be 1
        assert settings.pk == 1
    
    def test_system_settings_singleton_pattern(self):
        """Test that only one instance can exist (singleton pattern)."""
        # Delete any existing instances
        SystemSettings.objects.all().delete()
        
        # Create first instance
        settings1 = SystemSettings.objects.create(
            nombre_sistema='Settings 1',
            pk=1
        )
        
        # Try to create another with different pk
        settings2 = SystemSettings.objects.create(
            nombre_sistema='Settings 2',
            pk=2
        )
        
        # Save should force pk to 1
        settings2.save()
        assert settings2.pk == 1
        
        # Should only be one instance
        count = SystemSettings.objects.count()
        assert count == 1
    
    def test_system_settings_last_training_field(self):
        """Test last_training field can be null."""
        settings = SystemSettings.objects.create()
        
        assert settings.last_training is None
        
        # Set a training date
        training_date = timezone.now()
        settings.last_training = training_date
        settings.save()
        
        settings.refresh_from_db()
        assert settings.last_training is not None
    
    def test_system_settings_logo_field(self):
        """Test logo field can be null/blank."""
        settings = SystemSettings.objects.create()
        
        assert settings.logo.name == '' or settings.logo is None
    
    def test_system_settings_ordering(self):
        """Test that system settings are ordered by updated_at descending."""
        SystemSettings.objects.all().delete()
        
        settings1 = SystemSettings.objects.create(
            nombre_sistema='Settings 1',
            pk=1
        )
        
        # Small delay to ensure different timestamps
        import time
        time.sleep(0.01)
        
        settings1.nombre_sistema = 'Settings 1 Updated'
        settings1.save()
        
        settings = SystemSettings.objects.first()
        assert settings.nombre_sistema == 'Settings 1 Updated'
    
    def test_system_settings_configuration_fields(self):
        """Test all configuration fields."""
        settings = SystemSettings.objects.create(
            nombre_sistema='Test System',
            email_contacto='admin@test.com',
            lema='Test Lema',
            recaptcha_enabled=False,
            session_timeout=120,
            login_attempts=3,
            two_factor_auth=True,
            active_model='resnet18',
            last_training=timezone.now()
        )
        
        assert settings.nombre_sistema == 'Test System'
        assert settings.email_contacto == 'admin@test.com'
        assert settings.lema == 'Test Lema'
        assert settings.recaptcha_enabled is False
        assert settings.session_timeout == 120
        assert settings.login_attempts == 3
        assert settings.two_factor_auth is True
        assert settings.active_model == 'resnet18'
        assert settings.last_training is not None
    
    def test_system_settings_verbose_names(self):
        """Test verbose names are set correctly."""
        assert SystemSettings._meta.verbose_name == 'Configuración del Sistema'
        assert SystemSettings._meta.verbose_name_plural == 'Configuración del Sistema'

