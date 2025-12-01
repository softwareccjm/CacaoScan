"""
Unit tests for ML incremental views.
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


class IncrementalTrainingStatusViewTest(APITestCase):
    """Tests for IncrementalTrainingStatusView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_incremental_training_status_requires_authentication(self):
        """Test that incremental training status requires authentication."""
        url = reverse('ml-incremental-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.incremental_views.analysis_service')
    def test_incremental_training_status_success(self, mock_service):
        """Test successful incremental training status retrieval."""
        mock_service.get_incremental_training_status.return_value = {
            'enabled': True,
            'pending_images': 10,
            'last_training': None
        }
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-incremental-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('enabled', response.data)


class IncrementalTrainingStartViewTest(APITestCase):
    """Tests for IncrementalTrainingStartView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_incremental_training_start_requires_authentication(self):
        """Test that incremental training start requires authentication."""
        url = reverse('ml-incremental-start')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.incremental_views.analysis_service')
    def test_incremental_training_start_success(self, mock_service):
        """Test successful incremental training start."""
        mock_service.start_incremental_training.return_value = {
            'success': True,
            'job_id': 'job-123'
        }
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-incremental-start')
        response = self.client.post(url, {
            'target': 'alto',
            'epochs': 10
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('job_id', response.data)


class IncrementalTrainingStopViewTest(APITestCase):
    """Tests for IncrementalTrainingStopView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_incremental_training_stop_requires_authentication(self):
        """Test that incremental training stop requires authentication."""
        url = reverse('ml-incremental-stop')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.incremental_views.analysis_service')
    def test_incremental_training_stop_success(self, mock_service):
        """Test successful incremental training stop."""
        mock_service.stop_incremental_training.return_value = {
            'success': True,
            'message': 'Training stopped'
        }
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-incremental-stop')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

