"""
Unit tests for ML model views.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_ADMIN_USERNAME,
    TEST_ADMIN_EMAIL,
    TEST_ADMIN_PASSWORD,
)


class ModelsStatusViewTest(APITestCase):
    """Tests for ModelsStatusView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_models_status_requires_authentication(self):
        """Test that models status requires authentication."""
        url = reverse('ml-models-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.model_views.MLService')
    def test_models_status_success(self, mock_ml_service):
        """Test successful models status retrieval."""
        mock_service_instance = Mock()
        mock_service_instance.get_model_status.return_value = Mock(
            success=True,
            data={
                'status': 'loaded',
                'device': 'cpu',
                'model': 'HybridCacaoRegression',
                'model_details': {'version': '1.0.0'},
                'scalers': 'loaded'
            }
        )
        mock_ml_service.return_value = mock_service_instance
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-models-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'loaded')
    
    @patch('api.views.ml.model_views.MLService')
    def test_models_status_not_loaded(self, mock_ml_service):
        """Test models status when models are not loaded."""
        mock_service_instance = Mock()
        mock_service_instance.get_model_status.return_value = Mock(
            success=False,
            error=Mock(message='Models not loaded')
        )
        mock_ml_service.return_value = mock_service_instance
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-models-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('error', response.data)


class LoadModelsViewTest(APITestCase):
    """Tests for LoadModelsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )
    
    def test_load_models_requires_authentication(self):
        """Test that load models requires authentication."""
        url = reverse('ml-models-load')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_load_models_requires_admin(self):
        """Test that load models requires admin."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-models-load')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('api.views.ml.model_views.load_artifacts')
    @patch('api.views.ml.model_views.invalidate_models_status_cache')
    def test_load_models_success(self, mock_invalidate, mock_load):
        """Test successful model loading."""
        mock_load.return_value = True
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-models-load')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        mock_invalidate.assert_called_once()
    
    @patch('api.views.ml.model_views.load_artifacts')
    def test_load_models_failure(self, mock_load):
        """Test model loading failure."""
        mock_load.side_effect = Exception('Failed to load models')
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-models-load')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)


class UnloadModelsViewTest(APITestCase):
    """Tests for UnloadModelsView."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )
    
    def test_unload_models_requires_admin(self):
        """Test that unload models requires admin."""
        user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-models-unload')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('api.views.ml.model_views.get_predictor')
    @patch('api.views.ml.model_views.invalidate_models_status_cache')
    def test_unload_models_success(self, mock_invalidate, mock_get_predictor):
        """Test successful model unloading."""
        mock_predictor = Mock()
        mock_predictor.unload.return_value = True
        mock_get_predictor.return_value = mock_predictor
        
        token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-models-unload')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        mock_invalidate.assert_called_once()


class AutoTrainViewTest(APITestCase):
    """Tests for AutoTrainView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_auto_train_requires_authentication(self):
        """Test that auto train requires authentication."""
        url = reverse('ml-auto-train')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.model_views.MLService')
    def test_auto_train_success(self, mock_ml_service):
        """Test successful auto training."""
        mock_service_instance = Mock()
        mock_service_instance.start_auto_training.return_value = Mock(
            success=True,
            data={'job_id': 'job-123'}
        )
        mock_ml_service.return_value = mock_service_instance
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-auto-train')
        response = self.client.post(url, {
            'epochs': 50,
            'batch_size': 16,
            'learning_rate': 0.0001
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('job_id', response.data)
    
    def test_auto_train_invalid_config(self):
        """Test auto train with invalid configuration."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-auto-train')
        response = self.client.post(url, {
            'epochs': 501,  # Invalid: > 500
            'batch_size': 16,
            'learning_rate': 0.0001
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

