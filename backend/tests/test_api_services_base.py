"""
Unit tests for base service module (base.py).
Tests base service functionality, ServiceResult, and error handling.
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, InvalidPage, PageNotAnInteger
from django.db import transaction

from api.services.base import (
    BaseService,
    ServiceResult,
    ServiceError,
    ValidationServiceError,
    PermissionServiceError,
    NotFoundServiceError
)


@pytest.fixture
def base_service():
    """Create a BaseService instance for testing."""
    return BaseService()


@pytest.fixture
def django_user(db):
    """Create a real Django user for testing."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def django_superuser(db):
    """Create a real Django superuser for testing."""
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        is_superuser=True,
        is_staff=True
    )


class TestServiceError:
    """Tests for ServiceError exception classes."""
    
    def test_service_error_creation(self):
        """Test ServiceError creation with message."""
        error = ServiceError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None
        assert error.details == {}
    
    def test_service_error_with_code(self):
        """Test ServiceError creation with error code."""
        error = ServiceError("Test error", error_code="TEST_ERROR")
        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"
    
    def test_service_error_with_details(self):
        """Test ServiceError creation with details."""
        details = {"field": "email", "reason": "invalid"}
        error = ServiceError("Test error", details=details)
        assert error.details == details
    
    def test_validation_service_error(self):
        """Test ValidationServiceError creation."""
        error = ValidationServiceError("Validation failed")
        assert isinstance(error, ServiceError)
        assert error.message == "Validation failed"
    
    def test_permission_service_error(self):
        """Test PermissionServiceError creation."""
        error = PermissionServiceError("Permission denied")
        assert isinstance(error, ServiceError)
        assert error.message == "Permission denied"
    
    def test_not_found_service_error(self):
        """Test NotFoundServiceError creation."""
        error = NotFoundServiceError("Resource not found")
        assert isinstance(error, ServiceError)
        assert error.message == "Resource not found"


class TestServiceResult:
    """Tests for ServiceResult class."""
    
    def test_service_result_success_default(self):
        """Test ServiceResult.success() with default values."""
        result = ServiceResult.success()
        assert result.success is True
        assert result.data is None
        assert result.message is None
        assert result.error is None
    
    def test_service_result_success_with_data(self):
        """Test ServiceResult.success() with data."""
        data = {"key": "value"}
        result = ServiceResult.success(data=data, message="Success message")
        assert result.success is True
        assert result.data == data
        assert result.message == "Success message"
    
    def test_service_result_error(self):
        """Test ServiceResult.error() with ServiceError."""
        error = ValidationServiceError("Test error")
        result = ServiceResult.error(error)
        assert result.success is False
        assert result.error == error
        assert result.data is None
    
    def test_service_result_validation_error(self):
        """Test ServiceResult.validation_error()."""
        result = ServiceResult.validation_error("Validation failed", details={"field": "email"})
        assert result.success is False
        assert isinstance(result.error, ValidationServiceError)
        assert result.error.message == "Validation failed"
        assert result.error.details == {"field": "email"}
    
    def test_service_result_permission_error(self):
        """Test ServiceResult.permission_error()."""
        result = ServiceResult.permission_error("Permission denied")
        assert result.success is False
        assert isinstance(result.error, PermissionServiceError)
        assert result.error.message == "Permission denied"
    
    def test_service_result_not_found_error(self):
        """Test ServiceResult.not_found_error()."""
        result = ServiceResult.not_found_error("Resource not found")
        assert result.success is False
        assert isinstance(result.error, NotFoundServiceError)
        assert result.error.message == "Resource not found"
    
    def test_service_result_to_dict_success(self):
        """Test ServiceResult.to_dict() for success result."""
        result = ServiceResult.success(data={"key": "value"}, message="Success")
        result_dict = result.to_dict()
        
        assert result_dict['success'] is True
        assert result_dict['data'] == {"key": "value"}
        assert result_dict['message'] == "Success"
        assert 'error' not in result_dict
    
    def test_service_result_to_dict_error(self):
        """Test ServiceResult.to_dict() for error result."""
        error = ValidationServiceError("Test error", error_code="TEST_ERROR", details={"field": "email"})
        result = ServiceResult.error(error)
        result_dict = result.to_dict()
        
        assert result_dict['success'] is False
        assert result_dict['error']['message'] == "Test error"
        assert result_dict['error']['code'] == "TEST_ERROR"
        assert result_dict['error']['details'] == {"field": "email"}


class TestBaseService:
    """Tests for BaseService class."""
    
    def test_service_initialization(self, base_service):
        """Test service initialization."""
        assert base_service is not None
        assert base_service.logger is not None
    
    def test_log_info(self, base_service):
        """Test log_info method."""
        with patch.object(base_service.logger, 'info') as mock_info:
            base_service.log_info("Test info message", extra_key="extra_value")
            mock_info.assert_called_once_with("Test info message", extra={'extra_key': 'extra_value'})
    
    def test_log_warning(self, base_service):
        """Test log_warning method."""
        with patch.object(base_service.logger, 'warning') as mock_warning:
            base_service.log_warning("Test warning message")
            mock_warning.assert_called_once()
    
    def test_log_error(self, base_service):
        """Test log_error method."""
        with patch.object(base_service.logger, 'error') as mock_error:
            base_service.log_error("Test error message")
            mock_error.assert_called_once()
    
    def test_validate_user_permission_superuser(self, base_service, django_superuser):
        """Test validate_user_permission for superuser."""
        has_permission = base_service.validate_user_permission(
            django_superuser,
            "test_permission",
            resource=None
        )
        assert has_permission is True
    
    def test_validate_user_permission_staff(self, base_service, db):
        """Test validate_user_permission for staff user."""
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        has_permission = base_service.validate_user_permission(
            staff_user,
            "test_permission",
            resource=None
        )
        assert has_permission is True
    
    def test_validate_user_permission_regular_user(self, base_service, django_user):
        """Test validate_user_permission for regular user."""
        has_permission = base_service.validate_user_permission(
            django_user,
            "test_permission",
            resource=None
        )
        assert has_permission is False
    
    def test_check_user_permission_allowed(self, base_service, django_superuser):
        """Test check_user_permission for allowed user."""
        # Should not raise exception
        base_service.check_user_permission(
            django_superuser,
            "test_permission",
            resource=None
        )
    
    def test_check_user_permission_denied(self, base_service, django_user):
        """Test check_user_permission for denied user."""
        with pytest.raises(PermissionServiceError) as exc_info:
            base_service.check_user_permission(
                django_user,
                "test_permission",
                resource=None
            )
        assert "no tiene permisos" in str(exc_info.value)
    
    def test_validate_required_fields_success(self, base_service):
        """Test validate_required_fields with all fields present."""
        data = {
            'field1': 'value1',
            'field2': 'value2',
            'field3': 'value3'
        }
        required_fields = ['field1', 'field2']
        
        # Should not raise exception
        base_service.validate_required_fields(data, required_fields)
    
    def test_validate_required_fields_missing(self, base_service):
        """Test validate_required_fields with missing fields."""
        data = {'field1': 'value1'}
        required_fields = ['field1', 'field2', 'field3']
        
        with pytest.raises(ValidationServiceError) as exc_info:
            base_service.validate_required_fields(data, required_fields)
        
        assert "faltantes" in str(exc_info.value)
        assert exc_info.value.details['missing_fields'] == ['field2', 'field3']
    
    def test_validate_required_fields_none_value(self, base_service):
        """Test validate_required_fields with None value."""
        data = {'field1': 'value1', 'field2': None}
        required_fields = ['field1', 'field2']
        
        with pytest.raises(ValidationServiceError) as exc_info:
            base_service.validate_required_fields(data, required_fields)
        
        assert 'field2' in exc_info.value.details['missing_fields']
    
    def test_validate_field_values_type_success(self, base_service):
        """Test validate_field_values with correct types."""
        data = {'age': 25, 'name': 'John'}
        validations = {
            'age': {'type': int},
            'name': {'type': str}
        }
        
        # Should not raise exception
        base_service.validate_field_values(data, validations)
    
    def test_validate_field_values_type_error(self, base_service):
        """Test validate_field_values with wrong type."""
        data = {'age': 'not_a_number'}
        validations = {'age': {'type': int}}
        
        with pytest.raises(ValidationServiceError) as exc_info:
            base_service.validate_field_values(data, validations)
        
        assert "debe ser de tipo" in str(exc_info.value)
    
    def test_validate_field_values_range_success(self, base_service):
        """Test validate_field_values with valid range."""
        data = {'age': 25}
        validations = {'age': {'min': 18, 'max': 100}}
        
        # Should not raise exception
        base_service.validate_field_values(data, validations)
    
    def test_validate_field_values_range_too_small(self, base_service):
        """Test validate_field_values with value too small."""
        data = {'age': 15}
        validations = {'age': {'min': 18, 'max': 100}}
        
        with pytest.raises(ValidationServiceError) as exc_info:
            base_service.validate_field_values(data, validations)
        
        assert "mayor o igual" in str(exc_info.value)
    
    def test_validate_field_values_range_too_large(self, base_service):
        """Test validate_field_values with value too large."""
        data = {'age': 150}
        validations = {'age': {'min': 18, 'max': 100}}
        
        with pytest.raises(ValidationServiceError) as exc_info:
            base_service.validate_field_values(data, validations)
        
        assert "menor o igual" in str(exc_info.value)
    
    def test_validate_field_values_length_success(self, base_service):
        """Test validate_field_values with valid length."""
        data = {'username': 'testuser'}
        validations = {'username': {'min_length': 5, 'max_length': 20}}
        
        # Should not raise exception
        base_service.validate_field_values(data, validations)
    
    def test_validate_field_values_length_too_short(self, base_service):
        """Test validate_field_values with value too short."""
        data = {'username': 'abc'}
        validations = {'username': {'min_length': 5}}
        
        with pytest.raises(ValidationServiceError) as exc_info:
            base_service.validate_field_values(data, validations)
        
        assert "al menos" in str(exc_info.value)
    
    def test_validate_field_values_length_too_long(self, base_service):
        """Test validate_field_values with value too long."""
        data = {'username': 'a' * 30}
        validations = {'username': {'max_length': 20}}
        
        with pytest.raises(ValidationServiceError) as exc_info:
            base_service.validate_field_values(data, validations)
        
        assert "máximo" in str(exc_info.value)
    
    def test_execute_with_transaction_success(self, base_service):
        """Test execute_with_transaction with successful function."""
        def test_func(x, y):
            return x + y
        
        result = base_service.execute_with_transaction(test_func, 2, 3)
        assert result == 5
    
    def test_execute_with_transaction_error(self, base_service):
        """Test execute_with_transaction with function that raises exception."""
        def test_func():
            raise ValueError("Test error")
        
        with pytest.raises(ServiceError) as exc_info:
            base_service.execute_with_transaction(test_func)
        
        assert "Error en operación de base de datos" in str(exc_info.value)
    
    def test_paginate_results_success(self, base_service, db):
        """Test paginate_results with valid queryset."""
        # Create test users
        for i in range(25):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
        
        queryset = User.objects.all()
        result = base_service.paginate_results(queryset, page=1, page_size=10)
        
        assert 'results' in result
        assert 'pagination' in result
        assert len(result['results']) == 10
        assert result['pagination']['page'] == 1
        assert result['pagination']['per_page'] == 10
        assert result['pagination']['total'] == 25
        assert result['pagination']['pages'] == 3
        assert result['pagination']['has_next'] is True
        assert result['pagination']['has_previous'] is False
    
    def test_paginate_results_invalid_page(self, base_service, db):
        """Test paginate_results with invalid page number."""
        User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        
        queryset = User.objects.all()
        # Invalid page should default to page 1
        result = base_service.paginate_results(queryset, page=999, page_size=10)
        
        assert result['pagination']['page'] == 1
    
    def test_paginate_results_empty_queryset(self, base_service, db):
        """Test paginate_results with empty queryset."""
        queryset = User.objects.all()
        result = base_service.paginate_results(queryset, page=1, page_size=10)
        
        assert len(result['results']) == 0
        assert result['pagination']['total'] == 0
    
    @patch('api.services.base.ActivityLog')
    def test_create_audit_log_success(self, mock_activity_log, base_service, django_user):
        """Test create_audit_log with ActivityLog available."""
        mock_activity_log.objects.create = Mock()
        
        base_service.create_audit_log(
            user=django_user,
            action="test_action",
            resource_type="test_resource",
            resource_id=123,
            details={"key": "value"}
        )
        
        mock_activity_log.objects.create.assert_called_once()
        call_kwargs = mock_activity_log.objects.create.call_args[1]
        assert call_kwargs['user'] == django_user
        assert call_kwargs['action'] == "test_action"
        assert call_kwargs['resource_type'] == "test_resource"
        assert call_kwargs['resource_id'] == "123"
        assert call_kwargs['details'] == {"key": "value"}
    
    def test_create_audit_log_no_activity_log(self, base_service, django_user):
        """Test create_audit_log when ActivityLog is not available."""
        with patch('api.services.base.ActivityLog', None):
            with patch.object(base_service, 'log_debug') as mock_debug:
                base_service.create_audit_log(
                    user=django_user,
                    action="test_action",
                    resource_type="test_resource"
                )
                mock_debug.assert_called_once()
    
    def test_create_audit_log_exception(self, base_service, django_user):
        """Test create_audit_log when exception occurs."""
        with patch('api.services.base.ActivityLog') as mock_activity_log:
            mock_activity_log.objects.create.side_effect = Exception("Database error")
            
            with patch.object(base_service, 'log_warning') as mock_warning:
                # Should not raise exception, just log warning
                base_service.create_audit_log(
                    user=django_user,
                    action="test_action",
                    resource_type="test_resource"
                )
                mock_warning.assert_called_once()

