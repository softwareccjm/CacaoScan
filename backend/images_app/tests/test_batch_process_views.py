"""
Tests for batch process views helper class.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date

from images_app.views.image.batch.batch_process_views import BatchImageProcessor
from api.models import Finca, Lote, CacaoImage
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
)


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username=TEST_USER_USERNAME,
        email='test@example.com',
        password=TEST_USER_PASSWORD
    )


@pytest.fixture
def finca(user):
    """Create a test finca."""
    return Finca.objects.create(
        nombre='Test Finca',
        user=user,
        departamento='Test Department',
        municipio='Test Municipality'
    )


@pytest.fixture
def lote(finca):
    """Create a test lote."""
    return Lote.objects.create(
        nombre='Test Lote',
        finca=finca,
        fecha_cosecha=date.today(),
        variedad='Test Variety'
    )


@pytest.fixture
def mock_image_file():
    """Create a mock image file."""
    return SimpleUploadedFile(
        'test_image.jpg',
        b'fake image content',
        content_type='image/jpeg'
    )


@pytest.fixture
def mock_request(user):
    """Create a mock request object."""
    request = Mock()
    request.user = user
    return request


@pytest.fixture
def mock_predictor():
    """Create a mock predictor."""
    predictor = MagicMock()
    predictor.models_loaded = True
    predictor.predict.return_value = {
        'alto_mm': 20.5,
        'ancho_mm': 15.3,
        'grosor_mm': 10.2,
        'peso_g': 1.5,
        'confidences': {
            'alto': 0.9,
            'ancho': 0.85,
            'grosor': 0.88,
            'peso': 0.92
        }
    }
    return predictor


@pytest.mark.django_db
class TestBatchImageProcessor:
    """Tests for BatchImageProcessor class."""

    @patch('images_app.views.image.batch.batch_process_views.load_image_for_prediction')
    @patch('images_app.views.image.batch.batch_process_views.process_image_prediction')
    @patch('images_app.views.image.batch.batch_process_views.CacaoImage')
    def test_process_single_image_success(
        self,
        mock_cacao_image_class,
        mock_process_prediction,
        mock_load_image,
        mock_request,
        mock_image_file,
        lote,
        mock_predictor
    ):
        """Test processing a single image successfully."""
        # Setup mocks
        mock_cacao_image = Mock()
        mock_cacao_image.id = 1
        mock_cacao_image.save = Mock()
        mock_cacao_image_class.return_value = mock_cacao_image
        
        mock_pil_image = Mock()
        mock_load_image.return_value = mock_pil_image
        
        mock_process_prediction.return_value = (
            {
                'success': True,
                'prediction_id': 1,
                'image_id': 1
            },
            None
        )
        
        result = BatchImageProcessor._process_single_image(
            mock_request,
            mock_image_file,
            lote,
            0,
            mock_predictor
        )
        
        assert result['success'] is True
        assert 'image_id' in result
        mock_cacao_image.save.assert_called_once()
        mock_process_prediction.assert_called_once()

    @patch('images_app.views.image.batch.batch_process_views.CacaoImage')
    def test_process_single_image_predictor_not_loaded(
        self,
        mock_cacao_image_class,
        mock_request,
        mock_image_file,
        lote
    ):
        """Test processing image when predictor is not loaded."""
        mock_cacao_image = Mock()
        mock_cacao_image.id = 1
        mock_cacao_image.save = Mock()
        mock_cacao_image_class.return_value = mock_cacao_image
        
        predictor = Mock()
        predictor.models_loaded = False
        
        result = BatchImageProcessor._process_single_image(
            mock_request,
            mock_image_file,
            lote,
            0,
            predictor
        )
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Modelos ML no disponibles' in result['error']

    @patch('images_app.views.image.batch.batch_process_views.load_image_for_prediction')
    @patch('images_app.views.image.batch.batch_process_views.process_image_prediction')
    @patch('images_app.views.image.batch.batch_process_views.CacaoImage')
    def test_process_single_image_prediction_error(
        self,
        mock_cacao_image_class,
        mock_process_prediction,
        mock_load_image,
        mock_request,
        mock_image_file,
        lote,
        mock_predictor
    ):
        """Test processing image when prediction fails."""
        mock_cacao_image = Mock()
        mock_cacao_image.id = 1
        mock_cacao_image.save = Mock()
        mock_cacao_image_class.return_value = mock_cacao_image
        
        mock_pil_image = Mock()
        mock_load_image.return_value = mock_pil_image
        
        mock_process_prediction.return_value = (
            {
                'success': False,
                'error': 'Prediction failed'
            },
            'Prediction error'
        )
        
        result = BatchImageProcessor._process_single_image(
            mock_request,
            mock_image_file,
            lote,
            0,
            mock_predictor
        )
        
        assert result['success'] is False
        assert 'error' in result

    @patch('images_app.views.image.batch.batch_process_views.CacaoImage')
    def test_process_single_image_exception(
        self,
        mock_cacao_image_class,
        mock_request,
        mock_image_file,
        lote
    ):
        """Test processing image when exception occurs."""
        mock_cacao_image_class.side_effect = Exception('Database error')
        
        result = BatchImageProcessor._process_single_image(
            mock_request,
            mock_image_file,
            lote,
            0,
            None
        )
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Database error' in result['error']

    @patch('images_app.views.image.batch.batch_process_views.BatchImageProcessor._process_single_image')
    @patch('images_app.views.image.batch.batch_process_views.get_predictor')
    def test_process_images_batch_success(
        self,
        mock_get_predictor,
        mock_process_single,
        mock_request,
        mock_image_file,
        lote,
        mock_predictor
    ):
        """Test processing batch of images successfully."""
        mock_get_predictor.return_value = (mock_predictor, None)
        mock_process_single.return_value = {
            'success': True,
            'image_id': 1
        }
        
        images = [mock_image_file, mock_image_file]
        results = BatchImageProcessor.process_images_batch(
            mock_request,
            images,
            lote
        )
        
        assert len(results) == 2
        assert all(result['success'] for result in results)
        assert mock_process_single.call_count == 2

    @patch('images_app.views.image.batch.batch_process_views.BatchImageProcessor._process_single_image')
    @patch('images_app.views.image.batch.batch_process_views.get_predictor')
    def test_process_images_batch_predictor_error(
        self,
        mock_get_predictor,
        mock_process_single,
        mock_request,
        mock_image_file,
        lote
    ):
        """Test processing batch when predictor fails to load."""
        mock_get_predictor.return_value = (None, {'error': 'Predictor error'})
        mock_process_single.return_value = {
            'success': False,
            'error': 'Modelos ML no disponibles'
        }
        
        images = [mock_image_file]
        results = BatchImageProcessor.process_images_batch(
            mock_request,
            images,
            lote
        )
        
        assert len(results) == 1
        assert results[0]['success'] is False

    def test_calculate_stats_success(self):
        """Test calculating statistics from results."""
        results = [
            {
                'success': True,
                'prediction': {
                    'alto_mm': 20.5,
                    'ancho_mm': 15.3,
                    'peso_g': 1.5
                }
            },
            {
                'success': True,
                'prediction': {
                    'alto_mm': 25.0,
                    'ancho_mm': 16.0,
                    'peso_g': 2.0
                }
            },
            {
                'success': False,
                'error': 'Processing error'
            }
        ]
        
        stats = BatchImageProcessor.calculate_stats(results)
        
        assert stats is not None
        # Stats should contain information about successful and failed predictions

    def test_calculate_stats_empty_results(self):
        """Test calculating statistics with empty results."""
        results = []
        
        stats = BatchImageProcessor.calculate_stats(results)
        
        assert stats is not None

    def test_calculate_stats_all_failed(self):
        """Test calculating statistics when all predictions fail."""
        results = [
            {
                'success': False,
                'error': 'Error 1'
            },
            {
                'success': False,
                'error': 'Error 2'
            }
        ]
        
        stats = BatchImageProcessor.calculate_stats(results)
        
        assert stats is not None

    @patch('images_app.views.image.batch.batch_process_views.BatchImageProcessor._process_single_image')
    @patch('images_app.views.image.batch.batch_process_views.get_predictor')
    def test_process_images_batch_empty_images(
        self,
        mock_get_predictor,
        mock_process_single,
        mock_request,
        lote,
        mock_predictor
    ):
        """Test processing batch with empty images list."""
        mock_get_predictor.return_value = (mock_predictor, None)
        
        images = []
        results = BatchImageProcessor.process_images_batch(
            mock_request,
            images,
            lote
        )
        
        assert len(results) == 0
        assert mock_process_single.call_count == 0

    @patch('images_app.views.image.batch.batch_process_views.load_image_for_prediction')
    @patch('images_app.views.image.batch.batch_process_views.process_image_prediction')
    @patch('images_app.views.image.batch.batch_process_views.CacaoImage')
    def test_process_single_image_prediction_exception(
        self,
        mock_cacao_image_class,
        mock_process_prediction,
        mock_load_image,
        mock_request,
        mock_image_file,
        lote,
        mock_predictor
    ):
        """Test processing image when prediction raises exception."""
        mock_cacao_image = Mock()
        mock_cacao_image.id = 1
        mock_cacao_image.save = Mock()
        mock_cacao_image_class.return_value = mock_cacao_image
        
        mock_pil_image = Mock()
        mock_load_image.return_value = mock_pil_image
        
        mock_process_prediction.side_effect = Exception('Prediction exception')
        
        result = BatchImageProcessor._process_single_image(
            mock_request,
            mock_image_file,
            lote,
            0,
            mock_predictor
        )
        
        assert result['success'] is False
        assert 'error' in result
        assert 'image_id' in result

