"""
Tests for admin CRUD views.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from PIL import Image
import io

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_ADMIN_PASSWORD,
    TEST_ADMIN_USERNAME,
    TEST_ADMIN_EMAIL,
)
from images_app.models import CacaoImage, CacaoPrediction
from images_app.views.image.admin.crud_views import (
    AdminImageDetailView,
    AdminImageUpdateView,
    AdminImageDeleteView
)


class AdminImageDetailViewTest(APITestCase):
    """Tests for AdminImageDetailView."""
    
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
        
        self.test_image = self._create_test_image()
        self.cacao_image = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            finca='Test Finca',
            region='Test Region'
        )
        
        self.prediction = CacaoPrediction.objects.create(
            image=self.cacao_image,
            alto_mm=15.5,
            ancho_mm=12.3,
            grosor_mm=8.7,
            peso_g=1.2,
            confidence_alto=0.95,
            confidence_ancho=0.92,
            confidence_grosor=0.88,
            confidence_peso=0.90,
            processing_time_ms=1500,
            model_version='v1.0',
            device_used='cpu'
        )
    
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
    
    def test_get_image_detail_as_admin(self):
        """Test getting image detail as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = f'/api/v1/admin/images/{self.cacao_image.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('admin_info', response.data)
        self.assertIn('owner_info', response.data['admin_info'])
        self.assertIn('file_info', response.data['admin_info'])
    
    def test_get_image_detail_as_non_admin(self):
        """Test getting image detail as non-admin."""
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/v1/admin/images/{self.cacao_image.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_image_detail_not_found(self):
        """Test getting non-existent image detail."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/admin/images/99999/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_image_detail_unauthenticated(self):
        """Test getting image detail without authentication."""
        url = f'/api/v1/admin/images/{self.cacao_image.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('images_app.views.image.admin.crud_views.os.path.exists')
    def test_build_admin_info(self, mock_exists):
        """Test building admin info dictionary."""
        mock_exists.return_value = True
        
        view = AdminImageDetailView()
        admin_info = view._build_admin_info(self.cacao_image, self.admin_user)
        
        self.assertIn('owner_info', admin_info)
        self.assertIn('file_info', admin_info)
        self.assertIn('processing_info', admin_info)
        self.assertIn('access_info', admin_info)
        self.assertEqual(admin_info['access_info']['accessed_by_admin'], self.admin_user.username)


class AdminImageUpdateViewTest(APITestCase):
    """Tests for AdminImageUpdateView."""
    
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
        
        self.test_image = self._create_test_image()
        self.cacao_image = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=False,
            finca='Old Finca',
            region='Old Region'
        )
    
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
    
    def test_update_image_as_admin(self):
        """Test updating image as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = f'/api/v1/admin/images/{self.cacao_image.id}/'
        data = {
            'finca': 'New Finca',
            'region': 'New Region',
            'variedad': 'New Variedad',
            'notas': 'Admin notes',
            'processed': True
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('updated_fields', response.data)
        
        self.cacao_image.refresh_from_db()
        self.assertEqual(self.cacao_image.finca, 'New Finca')
        self.assertEqual(self.cacao_image.region, 'New Region')
        self.assertTrue(self.cacao_image.processed)
    
    def test_update_image_with_date(self):
        """Test updating image with fecha_cosecha."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = f'/api/v1/admin/images/{self.cacao_image.id}/'
        data = {
            'fecha_cosecha': '2024-01-15'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.cacao_image.refresh_from_db()
        self.assertIsNotNone(self.cacao_image.fecha_cosecha)
    
    def test_update_image_invalid_date(self):
        """Test updating image with invalid date."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = f'/api/v1/admin/images/{self.cacao_image.id}/'
        data = {
            'fecha_cosecha': 'invalid-date'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_image_with_admin_notes(self):
        """Test updating image with admin notes."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = f'/api/v1/admin/images/{self.cacao_image.id}/'
        data = {
            'admin_notes': 'This is an admin note'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.cacao_image.refresh_from_db()
        self.assertIn('ADMIN', self.cacao_image.notas)
        self.assertIn(self.admin_user.username, self.cacao_image.notas)
    
    def test_update_image_as_non_admin(self):
        """Test updating image as non-admin."""
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/v1/admin/images/{self.cacao_image.id}/'
        data = {'finca': 'New Finca'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_image_not_found(self):
        """Test updating non-existent image."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/admin/images/99999/'
        data = {'finca': 'New Finca'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AdminImageDeleteViewTest(APITestCase):
    """Tests for AdminImageDeleteView."""
    
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
        
        self.test_image = self._create_test_image()
        self.cacao_image = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True
        )
        
        self.prediction = CacaoPrediction.objects.create(
            image=self.cacao_image,
            alto_mm=15.5,
            ancho_mm=12.3,
            grosor_mm=8.7,
            peso_g=1.2,
            confidence_alto=0.95,
            confidence_ancho=0.92,
            confidence_grosor=0.88,
            confidence_peso=0.90,
            processing_time_ms=1500,
            model_version='v1.0',
            device_used='cpu'
        )
    
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
    
    def test_delete_image_as_admin(self):
        """Test deleting image as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        image_id = self.cacao_image.id
        url = f'/api/v1/admin/images/{image_id}/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('deleted_image', response.data)
        self.assertIn('deleted_prediction', response.data)
        self.assertFalse(CacaoImage.objects.filter(id=image_id).exists())
        self.assertFalse(CacaoPrediction.objects.filter(id=self.prediction.id).exists())
    
    def test_delete_image_as_non_admin(self):
        """Test deleting image as non-admin."""
        self.client.force_authenticate(user=self.user)
        
        url = f'/api/v1/admin/images/{self.cacao_image.id}/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_image_not_found(self):
        """Test deleting non-existent image."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/admin/images/99999/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_image_unauthenticated(self):
        """Test deleting image without authentication."""
        url = f'/api/v1/admin/images/{self.cacao_image.id}/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

