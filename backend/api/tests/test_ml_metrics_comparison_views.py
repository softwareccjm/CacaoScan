"""
Unit tests for ML metrics comparison views.
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
)


class ModelComparisonViewTest(APITestCase):
    """Tests for ModelComparisonView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_model_comparison_requires_authentication(self):
        """Test that model comparison requires authentication."""
        url = reverse('ml-model-comparison')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_model_comparison_missing_parameters(self):
        """Test model comparison without required parameters."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-model-comparison')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('api.views.ml.metrics_comparison_views.ModelMetrics')
    def test_model_comparison_success(self, mock_metrics):
        """Test successful model comparison."""
        mock_model_a = Mock()
        mock_model_a.id = 1
        mock_model_a.r2_score = 0.85
        
        mock_model_b = Mock()
        mock_model_b.id = 2
        mock_model_b.r2_score = 0.90
        
        mock_metrics.objects.get.side_effect = [mock_model_a, mock_model_b]
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-model-comparison')
        response = self.client.get(url, {
            'model_a_id': 1,
            'model_b_id': 2
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('comparison_metrics', response.data['data'])
    
    @patch('api.views.ml.metrics_comparison_views.ModelMetrics')
    def test_model_comparison_not_found(self, mock_metrics):
        """Test model comparison with non-existent models."""
        mock_metrics.DoesNotExist = Exception
        mock_metrics.objects.get.side_effect = mock_metrics.DoesNotExist
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-model-comparison')
        response = self.client.get(url, {
            'model_a_id': 999,
            'model_b_id': 998
        })
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ModelComparisonBatchViewTest(APITestCase):
    """Tests for ModelComparisonBatchView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_model_comparison_batch_requires_authentication(self):
        """Test that model comparison batch requires authentication."""
        url = reverse('ml-model-comparison-batch')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_model_comparison_batch_missing_model_ids(self):
        """Test model comparison batch without model IDs."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-model-comparison-batch')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('api.views.ml.metrics_comparison_views.ModelMetrics')
    def test_model_comparison_batch_success(self, mock_metrics):
        """Test successful model comparison batch."""
        mock_models = [Mock(id=i, r2_score=0.8 + i * 0.01) for i in range(1, 4)]
        mock_metrics.objects.filter.return_value = mock_models
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-model-comparison-batch')
        response = self.client.post(url, {
            'model_ids': [1, 2, 3]
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('comparisons', response.data['data'])

