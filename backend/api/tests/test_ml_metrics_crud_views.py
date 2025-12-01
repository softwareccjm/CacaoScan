"""
Unit tests for ML metrics CRUD views.
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


class ModelMetricsListViewTest(APITestCase):
    """Tests for ModelMetricsListView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_metrics_list_requires_authentication(self):
        """Test that metrics list requires authentication."""
        url = reverse('ml-metrics-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_crud_views.ModelMetrics')
    def test_metrics_list_success(self, mock_metrics):
        """Test successful metrics list retrieval."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = []
        mock_metrics.objects.all.return_value = mock_queryset
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-metrics-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    @patch('api.views.ml.metrics_crud_views.ModelMetrics')
    def test_metrics_list_with_filters(self, mock_metrics):
        """Test metrics list with filters."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = []
        mock_metrics.objects.all.return_value = mock_queryset
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-metrics-list')
        response = self.client.get(url, {
            'model_name': 'test_model',
            'target': 'alto'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ModelMetricsDetailViewTest(APITestCase):
    """Tests for ModelMetricsDetailView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_metrics_detail_requires_authentication(self):
        """Test that metrics detail requires authentication."""
        url = reverse('ml-metrics-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_crud_views.ModelMetrics')
    def test_metrics_detail_success(self, mock_metrics):
        """Test successful metrics detail retrieval."""
        mock_instance = Mock()
        mock_instance.id = 1
        mock_instance.model_name = 'test_model'
        mock_metrics.objects.get.return_value = mock_instance
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-metrics-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('model_name', response.data)
    
    @patch('api.views.ml.metrics_crud_views.ModelMetrics')
    def test_metrics_detail_not_found(self, mock_metrics):
        """Test metrics detail with non-existent metrics."""
        mock_metrics.DoesNotExist = Exception
        mock_metrics.objects.get.side_effect = mock_metrics.DoesNotExist
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-metrics-detail', kwargs={'pk': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ModelMetricsCreateViewTest(APITestCase):
    """Tests for ModelMetricsCreateView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_metrics_create_requires_authentication(self):
        """Test that metrics create requires authentication."""
        url = reverse('ml-metrics-create')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_crud_views.ModelMetrics')
    def test_metrics_create_success(self, mock_metrics):
        """Test successful metrics creation."""
        mock_instance = Mock()
        mock_instance.id = 1
        mock_metrics.objects.create.return_value = mock_instance
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-metrics-create')
        response = self.client.post(url, {
            'model_name': 'test_model',
            'model_type': 'regression',
            'target': 'alto',
            'version': '1.0.0',
            'metric_type': 'regression',
            'mae': 2.5,
            'mse': 6.25,
            'rmse': 2.5,
            'r2_score': 0.85,
            'dataset_size': 1000,
            'train_size': 700,
            'validation_size': 200,
            'test_size': 100,
            'epochs': 50,
            'batch_size': 32,
            'learning_rate': 0.001
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_metrics_create_validation_error(self):
        """Test metrics create with validation errors."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-metrics-create')
        response = self.client.post(url, {
            'model_name': 'test_model',
            'r2_score': 1.5  # Invalid: > 1
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ModelMetricsUpdateViewTest(APITestCase):
    """Tests for ModelMetricsUpdateView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_metrics_update_requires_authentication(self):
        """Test that metrics update requires authentication."""
        url = reverse('ml-metrics-update', kwargs={'pk': 1})
        response = self.client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_crud_views.ModelMetrics')
    def test_metrics_update_success(self, mock_metrics):
        """Test successful metrics update."""
        mock_instance = Mock()
        mock_instance.id = 1
        mock_metrics.objects.get.return_value = mock_instance
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-metrics-update', kwargs={'pk': 1})
        response = self.client.put(url, {
            'mae': 2.3,
            'r2_score': 0.87
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ModelMetricsDeleteViewTest(APITestCase):
    """Tests for ModelMetricsDeleteView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_metrics_delete_requires_authentication(self):
        """Test that metrics delete requires authentication."""
        url = reverse('ml-metrics-delete', kwargs={'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_crud_views.ModelMetrics')
    def test_metrics_delete_success(self, mock_metrics):
        """Test successful metrics deletion."""
        mock_instance = Mock()
        mock_instance.id = 1
        mock_metrics.objects.get.return_value = mock_instance
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-metrics-delete', kwargs={'pk': 1})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_instance.delete.assert_called_once()

