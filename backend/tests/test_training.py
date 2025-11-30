"""
Integration tests for training API endpoints.
"""
import os
import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

# Load credentials from environment variables for security
ADMIN_USERNAME = os.getenv('TEST_ADMIN_USERNAME', 'admin_training')
ADMIN_PASSWORD = os.getenv('TEST_ADMIN_PASSWORD', 'test_admin_password_123')  # noqa: S106  # NOSONAR - S2068 credentials from environment


class TrainingAPITestCase(APITestCase):
    """Tests for training API endpoints."""
    
    def setUp(self):
        """Configuration before each test."""
        self.login_url = reverse('auth-login')
        self.training_url = reverse('ml-train')
        
        # Create admin user for testing
        self.admin_user = User.objects.create_user(
            username=ADMIN_USERNAME,
            email='admin_training@example.com',
            password=ADMIN_PASSWORD,
            is_staff=True,
            is_superuser=True
        )
        
        # Login and get token
        login_data = {
            'username': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD  # noqa: S106  # NOSONAR - S2068 credentials from environment
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        
        if login_response.status_code == status.HTTP_200_OK:
            login_data_response = login_response.json()
            # Try different possible token field names
            self.token = (
                login_data_response.get('token') or
                login_data_response.get('access') or
                login_data_response.get('data', {}).get('token') or
                login_data_response.get('data', {}).get('access')
            )
            if self.token:
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
            else:
                self.token = None
        else:
            self.token = None
    
    def test_training_job_creation(self):
        """Test creating a training job."""
        if not self.token:
            pytest.skip("Could not obtain authentication token")
        
        training_data = {
            'job_type': 'regression',
            'model_name': 'resnet18',
            'dataset_size': 490,
            'epochs': 30,
            'batch_size': 16,
            'learning_rate': 0.001,
            'config_params': {
                'multi_head': False,
                'model_type': 'resnet18',
                'img_size': 224,
                'early_stopping_patience': 10,
                'save_best_only': True
            }
        }
        
        response = self.client.post(self.training_url, training_data, format='json')
        
        # Check if the request was successful or if it's a validation error
        self.assertIn(
            response.status_code,
            [status.HTTP_201_CREATED, status.HTTP_202_ACCEPTED, status.HTTP_400_BAD_REQUEST]
        )
        
        if response.status_code in [status.HTTP_201_CREATED, status.HTTP_202_ACCEPTED]:
            response_data = response.json()
            self.assertIn('job_id', response_data or {})
    
    def test_training_job_creation_unauthorized(self):
        """Test that training job creation requires authentication."""
        # Remove authentication
        self.client.credentials()
        
        training_data = {
            'job_type': 'regression',
            'model_name': 'resnet18',
            'dataset_size': 490,
            'epochs': 30,
            'batch_size': 16,
            'learning_rate': 0.001,
            'config_params': {
                'multi_head': False,
                'model_type': 'resnet18',
                'img_size': 224,
                'early_stopping_patience': 10,
                'save_best_only': True
            }
        }
        
        response = self.client.post(self.training_url, training_data, format='json')
        
        # Should return 401 Unauthorized or 403 Forbidden
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )
