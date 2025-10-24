"""
Tests para servicios de CacaoScan.
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
import io
from PIL import Image

from api.services import (
    AuthenticationService, AnalysisService, ImageService,
    FincaService, LoteService, ReportService,
    ValidationServiceError, PermissionServiceError, NotFoundServiceError, ServiceError
)


class AuthenticationServiceTest(TestCase):
    """
    Tests para AuthenticationService.
    """
    
    def setUp(self):
        self.service = AuthenticationService()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_validate_email_valid(self):
        """Test validación de email válido."""
        self.assertTrue(self.service.validate_email('test@example.com'))
    
    def test_validate_email_invalid(self):
        """Test validación de email inválido."""
        with self.assertRaises(ValidationServiceError):
            self.service.validate_email('invalid-email')
    
    def test_validate_required_fields_success(self):
        """Test validación de campos requeridos exitosa."""
        data = {'field1': 'value1', 'field2': 'value2'}
        required = ['field1', 'field2']
        self.service.validate_required_fields(data, required)
        # No debe lanzar excepción
    
    def test_validate_required_fields_missing(self):
        """Test validación de campos requeridos faltantes."""
        data = {'field1': 'value1'}
        required = ['field1', 'field2']
        with self.assertRaises(ValidationServiceError) as context:
            self.service.validate_required_fields(data, required)
        
        self.assertEqual(context.exception.error_code, 'missing_required_fields')
        self.assertIn('field2', context.exception.details['missing_fields'])
    
    @patch('api.services.auth_service.User.objects.create_user')
    def test_register_user_success(self, mock_create_user):
        """Test registro de usuario exitoso."""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.email = 'test@example.com'
        mock_create_user.return_value = mock_user
        
        with patch('api.services.auth_service.RefreshToken') as mock_refresh:
            mock_token = MagicMock()
            mock_token.access_token = {'exp': 1234567890}
            mock_refresh.for_user.return_value = mock_token
            
            with patch('api.services.auth_service.EmailVerificationToken') as mock_verification:
                mock_verification.create_for_user.return_value = MagicMock(token='test-token')
                
                user, tokens = self.service.register_user(self.user_data)
                
                self.assertEqual(user, mock_user)
                self.assertIn('access', tokens)
                self.assertIn('refresh', tokens)
    
    def test_register_user_password_mismatch(self):
        """Test registro con contraseñas que no coinciden."""
        data = self.user_data.copy()
        data['password_confirm'] = 'different_password'
        
        with self.assertRaises(ValidationServiceError) as context:
            self.service.register_user(data)
        
        self.assertEqual(context.exception.error_code, 'password_mismatch')
    
    def test_register_user_password_too_short(self):
        """Test registro con contraseña muy corta."""
        data = self.user_data.copy()
        data['password'] = '123'
        data['password_confirm'] = '123'
        
        with self.assertRaises(ValidationServiceError) as context:
            self.service.register_user(data)
        
        self.assertEqual(context.exception.error_code, 'password_too_short')


class AnalysisServiceTest(TestCase):
    """
    Tests para AnalysisService.
    """
    
    def setUp(self):
        self.service = AnalysisService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_validate_image_file_success(self):
        """Test validación de archivo de imagen exitosa."""
        # Crear imagen PIL en memoria
        image = Image.new('RGB', (100, 100), color='red')
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)
        
        # Crear archivo mock
        mock_file = MagicMock()
        mock_file.content_type = 'image/jpeg'
        mock_file.size = len(image_bytes.getvalue())
        mock_file.read.return_value = image_bytes.getvalue()
        mock_file.seek.return_value = None
        
        result = self.service.file_service.validate_image_file(mock_file)
        
        self.assertTrue(result['valid'])
        self.assertEqual(result['content_type'], 'image/jpeg')
    
    def test_validate_image_file_invalid_type(self):
        """Test validación de archivo con tipo inválido."""
        mock_file = MagicMock()
        mock_file.content_type = 'text/plain'
        mock_file.size = 1024
        
        with self.assertRaises(ValidationServiceError) as context:
            self.service.file_service.validate_image_file(mock_file)
        
        self.assertEqual(context.exception.error_code, 'invalid_file_type')
    
    def test_validate_image_file_too_large(self):
        """Test validación de archivo demasiado grande."""
        mock_file = MagicMock()
        mock_file.content_type = 'image/jpeg'
        mock_file.size = 25 * 1024 * 1024  # 25MB
        
        with self.assertRaises(ValidationServiceError) as context:
            self.service.file_service.validate_image_file(mock_file)
        
        self.assertEqual(context.exception.error_code, 'file_too_large')


class FincaServiceTest(TestCase):
    """
    Tests para FincaService.
    """
    
    def setUp(self):
        self.service = FincaService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.finca_data = {
            'nombre': 'Finca Test',
            'ubicacion': 'Ubicación Test',
            'municipio': 'Municipio Test',
            'departamento': 'Departamento Test',
            'hectareas': 10.5
        }
    
    def test_create_finca_success(self):
        """Test creación de finca exitosa."""
        with patch('api.services.fincas_service.Finca.objects.create') as mock_create:
            mock_finca = MagicMock()
            mock_finca.id = 1
            mock_finca.nombre = 'Finca Test'
            mock_create.return_value = mock_finca
            
            result = self.service.create_finca(self.user, self.finca_data)
            
            self.assertEqual(result['nombre'], 'Finca Test')
            mock_create.assert_called_once()
    
    def test_create_finca_missing_fields(self):
        """Test creación de finca con campos faltantes."""
        incomplete_data = {'nombre': 'Finca Test'}
        
        with self.assertRaises(ValidationServiceError) as context:
            self.service.create_finca(self.user, incomplete_data)
        
        self.assertEqual(context.exception.error_code, 'missing_required_fields')
    
    def test_create_finca_invalid_hectareas(self):
        """Test creación de finca con hectáreas inválidas."""
        data = self.finca_data.copy()
        data['hectareas'] = -5  # Hectáreas negativas
        
        with self.assertRaises(ValidationServiceError) as context:
            self.service.create_finca(self.user, data)
        
        self.assertEqual(context.exception.error_code, 'invalid_hectareas')


class LoteServiceTest(TestCase):
    """
    Tests para LoteService.
    """
    
    def setUp(self):
        self.service = LoteService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.lote_data = {
            'finca_id': 1,
            'identificador': 'LOTE-001',
            'variedad': 'Criollo',
            'area_hectareas': 2.5
        }
    
    def test_create_lote_success(self):
        """Test creación de lote exitosa."""
        with patch('api.services.fincas_service.Finca.objects.get') as mock_finca_get:
            mock_finca = MagicMock()
            mock_finca.agricultor = self.user
            mock_finca_get.return_value = mock_finca
            
            with patch('api.services.fincas_service.Lote.objects.create') as mock_create:
                mock_lote = MagicMock()
                mock_lote.id = 1
                mock_lote.identificador = 'LOTE-001'
                mock_create.return_value = mock_lote
                
                result = self.service.create_lote(self.user, self.lote_data)
                
                self.assertEqual(result['identificador'], 'LOTE-001')
                mock_create.assert_called_once()
    
    def test_create_lote_finca_not_found(self):
        """Test creación de lote con finca inexistente."""
        with patch('api.services.fincas_service.Finca.objects.get') as mock_finca_get:
            from django.contrib.auth.models import User
            mock_finca_get.side_effect = User.DoesNotExist()
            
            with self.assertRaises(NotFoundServiceError) as context:
                self.service.create_lote(self.user, self.lote_data)
            
            self.assertEqual(context.exception.error_code, 'finca_not_found')


class ReportServiceTest(TestCase):
    """
    Tests para ReportService.
    """
    
    def setUp(self):
        self.service = ReportService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.report_data = {
            'tipo_reporte': 'analisis_mensual',
            'periodo_inicio': '2024-01-01T00:00:00Z',
            'periodo_fin': '2024-01-31T23:59:59Z',
            'titulo': 'Reporte Mensual'
        }
    
    def test_generate_report_success(self):
        """Test generación de reporte exitosa."""
        with patch('api.services.report_service.Reporte.objects.create') as mock_create:
            mock_reporte = MagicMock()
            mock_reporte.id = 1
            mock_reporte.titulo = 'Reporte Mensual'
            mock_create.return_value = mock_reporte
            
            with patch.object(self.service, '_generate_report_content') as mock_content:
                mock_content.return_value = b'PDF content'
                
                with patch.object(self.service, '_save_report_file') as mock_save:
                    mock_save.return_value = '/path/to/report.pdf'
                    
                    result = self.service.generate_analysis_report(self.user, self.report_data)
                    
                    self.assertEqual(result['titulo'], 'Reporte Mensual')
                    mock_create.assert_called_once()
    
    def test_generate_report_invalid_date_range(self):
        """Test generación de reporte con rango de fechas inválido."""
        data = self.report_data.copy()
        data['periodo_inicio'] = '2024-01-31T23:59:59Z'
        data['periodo_fin'] = '2024-01-01T00:00:00Z'  # Fecha fin antes que inicio
        
        with self.assertRaises(ValidationServiceError) as context:
            self.service.generate_analysis_report(self.user, data)
        
        self.assertEqual(context.exception.error_code, 'invalid_date_range')


class ServiceErrorTest(TestCase):
    """
    Tests para excepciones de servicios.
    """
    
    def test_service_error_creation(self):
        """Test creación de ServiceError."""
        error = ServiceError(
            message="Test error",
            error_code="test_error",
            details={"field": "value"}
        )
        
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.error_code, "test_error")
        self.assertEqual(error.details, {"field": "value"})
    
    def test_validation_service_error(self):
        """Test ValidationServiceError."""
        error = ValidationServiceError("Validation failed", "validation_error")
        
        self.assertIsInstance(error, ServiceError)
        self.assertEqual(error.message, "Validation failed")
        self.assertEqual(error.error_code, "validation_error")
    
    def test_permission_service_error(self):
        """Test PermissionServiceError."""
        error = PermissionServiceError("Access denied", "permission_denied")
        
        self.assertIsInstance(error, ServiceError)
        self.assertEqual(error.message, "Access denied")
        self.assertEqual(error.error_code, "permission_denied")
    
    def test_not_found_service_error(self):
        """Test NotFoundServiceError."""
        error = NotFoundServiceError("Resource not found", "not_found")
        
        self.assertIsInstance(error, ServiceError)
        self.assertEqual(error.message, "Resource not found")
        self.assertEqual(error.error_code, "not_found")


# Tests de integración
class ServiceIntegrationTest(TestCase):
    """
    Tests de integración entre servicios.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_auth_and_analysis_integration(self):
        """Test integración entre servicios de autenticación y análisis."""
        auth_service = AuthenticationService()
        analysis_service = AnalysisService()
        
        # Verificar que el usuario puede autenticarse
        try:
            user, tokens = auth_service.authenticate_user('testuser', 'testpass123')
            self.assertEqual(user, self.user)
            self.assertIn('access', tokens)
        except Exception as e:
            self.fail(f"Authentication failed: {e}")
        
        # Verificar que el servicio de análisis puede obtener estadísticas
        try:
            stats = analysis_service.get_analysis_statistics(self.user)
            self.assertIsInstance(stats, dict)
            self.assertIn('total_analyses', stats)
        except Exception as e:
            # Puede fallar si no hay análisis, pero no debe ser un error de servicio
            self.assertNotIsInstance(e, ServiceError)
