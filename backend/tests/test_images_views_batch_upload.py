"""
Tests for batch upload views.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from PIL import Image
import io
import tempfile
import os

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_ADMIN_PASSWORD,
    TEST_ADMIN_USERNAME,
    TEST_ADMIN_EMAIL,
)
from images_app.views.image.batch.batch_upload_views import BatchAnalysisView
from fincas_app.models import Finca, Lote


class BatchAnalysisViewTest(APITestCase):
    """Tests for BatchAnalysisView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.view = BatchAnalysisView()
        self.view.request = Mock()
        self.view.request.user = self.admin_user
    
    def _create_test_image(self, name='test_image.jpg'):
        """Create test image file."""
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        return SimpleUploadedFile(
            name,
            img_io.getvalue(),
            content_type='image/jpeg'
        )
    
    def test_validate_batch_input_missing_name(self):
        """Test validation when name is missing."""
        data = {
            'farm': 'Test Farm',
            'genetics': 'Test Genetics',
            'collectionDate': '2024-01-01'
        }
        
        response = self.view._validate_batch_input(data)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_validate_batch_input_missing_farm(self):
        """Test validation when farm is missing."""
        data = {
            'name': 'Test Lote',
            'genetics': 'Test Genetics',
            'collectionDate': '2024-01-01'
        }
        
        response = self.view._validate_batch_input(data)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_validate_batch_input_missing_genetics(self):
        """Test validation when genetics is missing."""
        data = {
            'name': 'Test Lote',
            'farm': 'Test Farm',
            'collectionDate': '2024-01-01'
        }
        
        response = self.view._validate_batch_input(data)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_validate_batch_input_missing_collection_date(self):
        """Test validation when collection date is missing."""
        data = {
            'name': 'Test Lote',
            'farm': 'Test Farm',
            'genetics': 'Test Genetics'
        }
        
        response = self.view._validate_batch_input(data)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_validate_batch_input_valid(self):
        """Test validation with valid data."""
        data = {
            'name': 'Test Lote',
            'farm': 'Test Farm',
            'genetics': 'Test Genetics',
            'collectionDate': '2024-01-01'
        }
        
        response = self.view._validate_batch_input(data)
        
        self.assertIsNone(response)
    
    @patch('images_app.views.image.batch.batch_upload_views.settings')
    def test_save_images_temporarily_success(self, mock_settings):
        """Test successful temporary image saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_settings.MEDIA_ROOT = temp_dir
            
            images = [
                self._create_test_image('img1.jpg'),
                self._create_test_image('img2.jpg')
            ]
            
            images_data = self.view._save_images_temporarily(images, 1)
            
            self.assertEqual(len(images_data), 2)
            self.assertIn('file_name', images_data[0])
            self.assertIn('temp_path', images_data[0])
            self.assertTrue(os.path.exists(images_data[0]['temp_path']))
    
    @patch('images_app.views.image.batch.batch_upload_views.settings')
    def test_save_images_temporarily_exception(self, mock_settings):
        """Test temporary image saving with exception."""
        mock_settings.MEDIA_ROOT = '/invalid/path'
        
        images = [self._create_test_image()]
        
        images_data = self.view._save_images_temporarily(images, 1)
        
        self.assertEqual(len(images_data), 0)
    
    def test_parse_collection_date_valid(self):
        """Test parsing valid collection date."""
        date_str = '2024-01-15'
        result = self.view._parse_collection_date(date_str)
        
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)
    
    def test_parse_collection_date_invalid(self):
        """Test parsing invalid collection date."""
        from datetime import date
        
        date_str = 'invalid-date'
        result = self.view._parse_collection_date(date_str)
        
        self.assertEqual(result, date.today())
    
    def test_validate_finca_valid(self):
        """Test finca validation with valid finca."""
        finca = Finca.objects.create(
            nombre='Test Finca',
            agricultor=self.user,
            ubicacion='Test Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=1.0,
            activa=True
        )
        
        result_finca, error = self.view._validate_finca(finca)
        
        self.assertIsNotNone(result_finca)
        self.assertIsNone(error)
        self.assertEqual(result_finca.id, finca.id)
    
    def test_validate_finca_invalid(self):
        """Test finca validation with invalid finca."""
        result_finca, error = self.view._validate_finca(None)
        
        self.assertIsNone(result_finca)
        self.assertIsNone(error)
    
    def test_verify_table_consistency(self):
        """Test table consistency verification."""
        finca = Finca.objects.create(
            nombre='Test Finca',
            agricultor=self.user,
            ubicacion='Test Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=1.0,
            activa=True
        )
        
        result = self.view._verify_table_consistency(finca)
        
        self.assertTrue(result)
    
    def test_is_foreign_key_error_true(self):
        """Test foreign key error detection."""
        error = Exception("Foreign key constraint violation")
        
        result = self.view._is_foreign_key_error(error)
        
        self.assertTrue(result)
    
    def test_is_foreign_key_error_false(self):
        """Test foreign key error detection with non-FK error."""
        error = Exception("Some other error")
        
        result = self.view._is_foreign_key_error(error)
        
        self.assertFalse(result)
    
    @patch('images_app.views.image.batch.batch_upload_views.process_batch_analysis_task')
    def test_post_success(self, mock_task):
        """Test successful batch analysis POST."""
        self.client.force_authenticate(user=self.admin_user)
        
        mock_task_result = Mock()
        mock_task_result.id = 'test-task-id'
        mock_task.delay.return_value = mock_task_result
        
        images = [
            self._create_test_image('img1.jpg'),
            self._create_test_image('img2.jpg')
        ]
        
        data = {
            'name': 'Test Lote',
            'farm': 'Test Farm',
            'genetics': 'Test Genetics',
            'collectionDate': '2024-01-01',
            'images': images
        }
        
        response = self.client.post('/api/v1/analysis/batch/', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)
        self.assertIn('lote_id', response.data)
        mock_task.delay.assert_called_once()
    
    def test_post_validation_error(self):
        """Test POST with validation error."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'name': '',  # Missing required field
            'farm': 'Test Farm'
        }
        
        response = self.client.post('/api/v1/analysis/batch/', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_post_no_images(self):
        """Test POST without images."""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'name': 'Test Lote',
            'farm': 'Test Farm',
            'genetics': 'Test Genetics',
            'collectionDate': '2024-01-01'
        }
        
        response = self.client.post('/api/v1/analysis/batch/', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No se enviaron imágenes', str(response.data))
    
    def test_post_unauthenticated(self):
        """Test POST without authentication."""
        data = {
            'name': 'Test Lote',
            'farm': 'Test Farm',
            'genetics': 'Test Genetics',
            'collectionDate': '2024-01-01'
        }
        
        response = self.client.post('/api/v1/analysis/batch/', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('images_app.views.image.batch.batch_upload_views.Finca.objects')
    def test_get_or_create_finca_existing(self, mock_finca_manager):
        """Test getting existing finca."""
        finca = Finca(
            id=1,
            nombre='Test Farm',
            agricultor=self.admin_user
        )
        mock_finca_manager.filter.return_value.first.return_value = finca
        
        self.view.request.user = self.admin_user
        result = self.view._get_or_create_finca(
            self.view.request, 'Test Farm', 'Origin Place', 'Origin'
        )
        
        self.assertIsNotNone(result)
    
    def test_get_or_create_finca_new(self):
        """Test creating new finca."""
        self.view.request.user = self.admin_user
        
        result = self.view._get_or_create_finca(
            self.view.request, 'New Farm', 'Origin Place', 'Origin'
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.nombre, 'New Farm')
        self.assertEqual(result.agricultor, self.admin_user)

