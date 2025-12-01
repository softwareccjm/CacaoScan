"""
Unit tests for ML calibration views.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
)


class CalibrationUploadViewTest(APITestCase):
    """Tests for calibration upload views."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_calibration_upload_requires_authentication(self):
        """Test that calibration upload requires authentication."""
        url = reverse('ml-calibration-upload')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_calibration_upload_missing_image(self):
        """Test calibration upload without image."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-calibration-upload')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_calibration_upload_invalid_file_type(self):
        """Test calibration upload with invalid file type."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        invalid_file = SimpleUploadedFile('test.txt', b'not an image', content_type='text/plain')
        url = reverse('ml-calibration-upload')
        response = self.client.post(url, {'image': invalid_file})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('api.views.ml.calibration_views.process_calibration_image')
    def test_calibration_upload_success(self, mock_process):
        """Test successful calibration upload."""
        mock_process.return_value = {
            'success': True,
            'pixel_calibration': {'width': 512, 'height': 512}
        }
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        image_file = SimpleUploadedFile('test.jpg', b'fake image content', content_type='image/jpeg')
        url = reverse('ml-calibration-upload')
        response = self.client.post(url, {'image': image_file})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pixel_calibration', response.data)


class CalibrationStatusViewTest(APITestCase):
    """Tests for calibration status views."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_calibration_status_requires_authentication(self):
        """Test that calibration status requires authentication."""
        url = reverse('ml-calibration-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.calibration_views.get_calibration_status')
    def test_calibration_status_success(self, mock_get_status):
        """Test successful calibration status retrieval."""
        mock_get_status.return_value = {
            'calibrated': True,
            'last_calibration': '2024-01-01T00:00:00Z'
        }
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-calibration-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('calibrated', response.data)

