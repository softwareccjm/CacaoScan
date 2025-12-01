"""
Tests for admin list views.
"""
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
from images_app.views.image.admin.list_views import AdminImagesListView


class AdminImagesListViewTest(APITestCase):
    """Tests for AdminImagesListView."""
    
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
        
        self.image1 = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test1.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=True,
            finca='Test Finca 1',
            region='Region 1',
            variedad='Variedad 1'
        )
        
        self.image2 = CacaoImage.objects.create(
            user=self.user,
            image=self.test_image,
            file_name='test2.jpg',
            file_size=2048,
            file_type='image/jpeg',
            processed=False,
            finca='Test Finca 2',
            region='Region 2',
            variedad='Variedad 2'
        )
        
        self.prediction = CacaoPrediction.objects.create(
            image=self.image1,
            alto_mm=15.5,
            ancho_mm=12.3,
            grosor_mm=8.7,
            peso_g=1.2,
            confidence_alto=0.95,
            confidence_ancho=0.92,
            confidence_grosor=0.88,
            confidence_peso=0.90,
            average_confidence=0.91,
            processing_time_ms=1500,
            model_version='v1.0',
            device_used='cpu'
        )
        
        self.view = AdminImagesListView()
    
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
    
    def test_apply_filters_user_id(self):
        """Test applying user_id filter."""
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, user_id=self.user.id)
        
        self.assertEqual(result.count(), 2)
        self.assertIn('user_id', filters_applied)
    
    def test_apply_filters_username(self):
        """Test applying username filter."""
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, username=TEST_USER_USERNAME)
        
        self.assertEqual(result.count(), 2)
        self.assertIn('username', filters_applied)
    
    def test_apply_filters_region(self):
        """Test applying region filter."""
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, region='Region 1')
        
        self.assertEqual(result.count(), 1)
        self.assertIn('region', filters_applied)
    
    def test_apply_filters_finca(self):
        """Test applying finca filter."""
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, finca='Test Finca 1')
        
        self.assertEqual(result.count(), 1)
        self.assertIn('finca', filters_applied)
    
    def test_apply_filters_processed_true(self):
        """Test applying processed filter (true)."""
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, processed='true')
        
        self.assertEqual(result.count(), 1)
        self.assertIn('processed', filters_applied)
        self.assertTrue(filters_applied['processed'])
    
    def test_apply_filters_processed_false(self):
        """Test applying processed filter (false)."""
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, processed='false')
        
        self.assertEqual(result.count(), 1)
        self.assertFalse(filters_applied['processed'])
    
    def test_apply_filters_has_prediction_true(self):
        """Test applying has_prediction filter (true)."""
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, has_prediction='true')
        
        self.assertEqual(result.count(), 1)
        self.assertTrue(filters_applied['has_prediction'])
    
    def test_apply_filters_has_prediction_false(self):
        """Test applying has_prediction filter (false)."""
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, has_prediction='false')
        
        self.assertEqual(result.count(), 1)
        self.assertFalse(filters_applied['has_prediction'])
    
    def test_apply_filters_search(self):
        """Test applying search filter."""
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, search='Variedad 1')
        
        self.assertEqual(result.count(), 1)
        self.assertIn('search', filters_applied)
    
    def test_apply_filters_date_from(self):
        """Test applying date_from filter."""
        from datetime import date
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, date_from=date.today())
        
        self.assertIn('date_from', filters_applied)
    
    def test_apply_filters_model_version(self):
        """Test applying model_version filter."""
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, model_version='v1.0')
        
        self.assertEqual(result.count(), 1)
        self.assertIn('model_version', filters_applied)
    
    def test_apply_filters_min_confidence(self):
        """Test applying min_confidence filter."""
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, min_confidence=0.9)
        
        self.assertIn('min_confidence', filters_applied)
    
    def test_apply_filters_max_confidence(self):
        """Test applying max_confidence filter."""
        queryset = CacaoImage.objects.all()
        filters_applied = {}
        
        result = self.view._apply_filters(queryset, filters_applied, max_confidence=0.95)
        
        self.assertIn('max_confidence', filters_applied)
    
    def test_get_list_as_admin(self):
        """Test getting image list as admin."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 2)
    
    def test_get_list_with_pagination(self):
        """Test getting list with pagination."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/'
        response = self.client.get(url, {'page': 1, 'page_size': 1})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('page', response.data)
        self.assertIn('total_pages', response.data)
    
    def test_get_list_with_filters(self):
        """Test getting list with filters."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/'
        response = self.client.get(url, {
            'region': 'Region 1',
            'processed': 'true'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIn('filters_applied', response.data)
    
    def test_get_list_as_non_admin(self):
        """Test getting list as non-admin."""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/v1/images/admin/images/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_list_unauthenticated(self):
        """Test getting list without authentication."""
        url = '/api/v1/images/admin/images/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_list_with_invalid_params(self):
        """Test getting list with invalid parameters."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = '/api/v1/images/admin/images/'
        response = self.client.get(url, {'page': 'invalid'})
        
        # Should handle gracefully or return 400
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

