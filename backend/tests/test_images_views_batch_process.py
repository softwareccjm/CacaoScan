"""
Tests for batch image processing views.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
)
from images_app.views.image.batch.batch_process_views import BatchImageProcessor
from images_app.models import CacaoImage
from fincas_app.models import Finca, Lote


class BatchImageProcessorTest(TestCase):
    """Tests for BatchImageProcessor."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        self.finca = Finca.objects.create(
            nombre='Test Finca',
            agricultor=self.user,
            ubicacion='Test Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=1.0,
            activa=True
        )
        
        self.lote = Lote.objects.create(
            finca=self.finca,
            identificador='Test Lote',
            variedad='Test Variedad',
            fecha_plantacion='2024-01-01',
            fecha_cosecha='2024-01-01',
            area_hectareas=0.1,
            estado='activo',
            activo=True
        )
        
        self.test_image = self._create_test_image()
        self.request = Mock()
        self.request.user = self.user
    
    def _create_test_image(self):
        """Create test image file."""
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        return SimpleUploadedFile(
            'test_image.jpg',
            img_io.getvalue(),
            content_type='image/jpeg'
        )
    
    @patch('images_app.views.image.batch.batch_process_views.get_predictor')
    @patch('images_app.views.image.batch.batch_process_views.load_image_for_prediction')
    @patch('images_app.views.image.batch.batch_process_views.process_image_prediction')
    def test_process_single_image_success(self, mock_process, mock_load, mock_get_predictor):
        """Test successful single image processing."""
        # Mock predictor
        mock_predictor = Mock()
        mock_predictor.models_loaded = True
        mock_get_predictor.return_value = (mock_predictor, None)
        
        # Mock image loading
        mock_pil_image = Image.new('RGB', (100, 100), color='red')
        mock_load.return_value = mock_pil_image
        
        # Mock prediction result
        mock_process.return_value = ({
            'success': True,
            'alto_mm': 15.5,
            'ancho_mm': 12.3,
            'grosor_mm': 8.7,
            'peso_g': 1.2
        }, None)
        
        result = BatchImageProcessor._process_single_image(
            self.request, self.test_image, self.lote, 0, mock_predictor
        )
        
        self.assertTrue(result['success'])
        self.assertIn('image_id', result)
        self.assertEqual(CacaoImage.objects.count(), 1)
    
    @patch('images_app.views.image.batch.batch_process_views.get_predictor')
    def test_process_single_image_no_predictor(self, mock_get_predictor):
        """Test processing when predictor is not available."""
        mock_get_predictor.return_value = (None, {'error': 'Models not loaded'})
        
        result = BatchImageProcessor._process_single_image(
            self.request, self.test_image, self.lote, 0, None
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Modelos ML no disponibles')
        self.assertEqual(CacaoImage.objects.count(), 1)
    
    @patch('images_app.views.image.batch.batch_process_views.get_predictor')
    @patch('images_app.views.image.batch.batch_process_views.load_image_for_prediction')
    @patch('images_app.views.image.batch.batch_process_views.process_image_prediction')
    def test_process_single_image_prediction_error(self, mock_process, mock_load, mock_get_predictor):
        """Test processing when prediction fails."""
        mock_predictor = Mock()
        mock_predictor.models_loaded = True
        mock_get_predictor.return_value = (mock_predictor, None)
        
        mock_pil_image = Image.new('RGB', (100, 100), color='red')
        mock_load.return_value = mock_pil_image
        
        mock_process.return_value = ({
            'success': False,
            'error': 'Prediction failed'
        }, 'Prediction error')
        
        result = BatchImageProcessor._process_single_image(
            self.request, self.test_image, self.lote, 0, mock_predictor
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch('images_app.views.image.batch.batch_process_views.get_predictor')
    def test_process_single_image_exception(self, mock_get_predictor):
        """Test processing when exception occurs."""
        mock_get_predictor.return_value = (None, None)
        
        # Create invalid image file to trigger exception
        invalid_image = SimpleUploadedFile(
            'test.txt',
            b'not an image',
            content_type='text/plain'
        )
        
        result = BatchImageProcessor._process_single_image(
            self.request, invalid_image, self.lote, 0, None
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch('images_app.views.image.batch.batch_process_views.get_predictor')
    @patch('images_app.views.image.batch.batch_process_views.load_image_for_prediction')
    @patch('images_app.views.image.batch.batch_process_views.process_image_prediction')
    def test_process_images_batch_success(self, mock_process, mock_load, mock_get_predictor):
        """Test successful batch processing."""
        mock_predictor = Mock()
        mock_predictor.models_loaded = True
        mock_get_predictor.return_value = (mock_predictor, None)
        
        mock_pil_image = Image.new('RGB', (100, 100), color='red')
        mock_load.return_value = mock_pil_image
        
        mock_process.return_value = ({
            'success': True,
            'alto_mm': 15.5
        }, None)
        
        images = [self.test_image, self._create_test_image()]
        results = BatchImageProcessor.process_images_batch(
            self.request, images, self.lote
        )
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r['success'] for r in results))
        self.assertEqual(CacaoImage.objects.count(), 2)
    
    @patch('images_app.views.image.batch.batch_process_views.get_predictor')
    def test_process_images_batch_no_predictor(self, mock_get_predictor):
        """Test batch processing when predictor is not available."""
        mock_get_predictor.return_value = (None, {'error': 'Models not loaded'})
        
        images = [self.test_image]
        results = BatchImageProcessor.process_images_batch(
            self.request, images, self.lote
        )
        
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0]['success'])
    
    @patch('images_app.views.image.batch.batch_process_views.calculate_prediction_statistics')
    def test_calculate_stats(self, mock_calc_stats):
        """Test statistics calculation."""
        mock_calc_stats.return_value = {
            'total': 2,
            'successful': 2,
            'failed': 0,
            'avg_alto_mm': 15.5
        }
        
        results = [
            {'success': True, 'alto_mm': 15.5},
            {'success': True, 'alto_mm': 16.0}
        ]
        
        stats = BatchImageProcessor.calculate_stats(results)
        
        self.assertIsNotNone(stats)
        mock_calc_stats.assert_called_once_with(results)

