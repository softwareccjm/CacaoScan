"""
Unit tests for ML metrics analysis views.
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


class ModelMetricsStatsViewTest(APITestCase):
    """Tests for ModelMetricsStatsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_metrics_stats_requires_authentication(self):
        """Test that metrics stats requires authentication."""
        url = reverse('ml-metrics-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_analysis_views.ModelMetrics')
    def test_metrics_stats_success(self, mock_metrics):
        """Test successful metrics stats retrieval."""
        mock_metrics.objects.count.return_value = 10
        mock_metrics.objects.filter.return_value.count.return_value = 5
        mock_metrics.objects.values.return_value.annotate.return_value = []
        mock_metrics.objects.aggregate.return_value = {'avg_r2': 0.85}
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-metrics-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_models', response.data['data'])


class ModelPerformanceTrendViewTest(APITestCase):
    """Tests for ModelPerformanceTrendView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_performance_trend_requires_authentication(self):
        """Test that performance trend requires authentication."""
        url = reverse('ml-performance-trend')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_analysis_views.ModelMetrics')
    def test_performance_trend_success(self, mock_metrics):
        """Test successful performance trend retrieval."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value.order_by.return_value = []
        mock_metrics.objects.filter.return_value = mock_queryset
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-performance-trend')
        response = self.client.get(url, {
            'model_name': 'test_model',
            'target': 'alto'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BestModelsViewTest(APITestCase):
    """Tests for BestModelsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_best_models_requires_authentication(self):
        """Test that best models requires authentication."""
        url = reverse('ml-best-models')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_analysis_views.ModelMetrics')
    def test_best_models_success(self, mock_metrics):
        """Test successful best models retrieval."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value.order_by.return_value = []
        mock_metrics.objects.filter.return_value = mock_queryset
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-best-models')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('best_models', response.data['data'])


class ProductionModelsViewTest(APITestCase):
    """Tests for ProductionModelsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_production_models_requires_authentication(self):
        """Test that production models requires authentication."""
        url = reverse('ml-production-models')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_analysis_views.ModelMetrics')
    def test_production_models_success(self, mock_metrics):
        """Test successful production models retrieval."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = []
        mock_metrics.objects.filter.return_value = mock_queryset
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-production-models')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('production_models', response.data['data'])

