"""
Tests for image permission mixins.
"""
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
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
from images_app.models import CacaoImage
from images_app.views.image.mixins import ImagePermissionMixin


class ImagePermissionMixinTest(TestCase):
    """Tests for ImagePermissionMixin."""
    
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
        
        self.analyst_user = User.objects.create_user(
            username='analyst',
            email='analyst@example.com',
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
        )
        
        analyst_group, _ = Group.objects.get_or_create(name='analyst')
        self.analyst_user.groups.add(analyst_group)
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password=TEST_USER_PASSWORD  # noqa: S106  # NOSONAR - Test credential from constants
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
        
        self.mixin = ImagePermissionMixin()
    
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
    
    def test_can_access_image_owner(self):
        """Test that owner can access their image."""
        result = self.mixin.can_access_image(self.user, self.cacao_image)
        
        self.assertTrue(result)
    
    def test_can_access_image_admin(self):
        """Test that admin can access any image."""
        result = self.mixin.can_access_image(self.admin_user, self.cacao_image)
        
        self.assertTrue(result)
    
    def test_can_access_image_analyst(self):
        """Test that analyst can access any image."""
        result = self.mixin.can_access_image(self.analyst_user, self.cacao_image)
        
        self.assertTrue(result)
    
    def test_can_access_image_other_user(self):
        """Test that other user cannot access image."""
        result = self.mixin.can_access_image(self.other_user, self.cacao_image)
        
        self.assertFalse(result)
    
    def test_get_user_images_queryset_admin(self):
        """Test queryset for admin user."""
        queryset = self.mixin.get_user_images_queryset(self.admin_user)
        
        self.assertEqual(queryset.count(), CacaoImage.objects.count())
    
    def test_get_user_images_queryset_analyst(self):
        """Test queryset for analyst user."""
        queryset = self.mixin.get_user_images_queryset(self.analyst_user)
        
        self.assertEqual(queryset.count(), CacaoImage.objects.count())
    
    def test_get_user_images_queryset_regular_user(self):
        """Test queryset for regular user."""
        queryset = self.mixin.get_user_images_queryset(self.user)
        
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.cacao_image)
    
    def test_get_user_images_queryset_other_user(self):
        """Test queryset for other user."""
        queryset = self.mixin.get_user_images_queryset(self.other_user)
        
        self.assertEqual(queryset.count(), 0)

