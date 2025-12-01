"""
Unit tests for auth_app models (EmailVerificationToken, UserProfile, PendingEmailVerification).
Tests cover model creation, properties, methods, expiration, and relationships.
"""
import pytest
import uuid
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

from auth_app.models import (
    EmailVerificationToken,
    UserProfile,
    PendingEmailVerification
)


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def inactive_user():
    """Create an inactive test user."""
    return User.objects.create_user(
        username='inactiveuser',
        email='inactive@example.com',
        password='testpass123',
        is_active=False
    )


class TestEmailVerificationToken:
    """Tests for EmailVerificationToken model."""
    
    def test_token_creation(self, user):
        """Test basic token creation."""
        token = EmailVerificationToken.objects.create(user=user)
        
        assert token.user == user
        assert token.token is not None
        assert isinstance(token.token, uuid.UUID)
        assert token.is_verified is False
        assert token.verified_at is None
        assert token.created_at is not None
    
    def test_token_str_representation(self, user):
        """Test string representation of token."""
        token = EmailVerificationToken.objects.create(user=user)
        
        expected = f"Token para {user.email} - Pendiente"
        assert str(token) == expected
        
        token.verify()
        expected_verified = f"Token para {user.email} - Verificado"
        assert str(token) == expected_verified
    
    def test_token_is_expired_property_not_verified(self, user):
        """Test is_expired property for unverified token."""
        token = EmailVerificationToken.objects.create(user=user)
        
        # Token just created should not be expired
        assert token.is_expired is False
    
    def test_token_is_expired_property_verified(self, user):
        """Test is_expired property for verified token."""
        token = EmailVerificationToken.objects.create(user=user)
        token.verify()
        
        # Verified tokens are never expired
        assert token.is_expired is False
    
    def test_token_is_expired_property_expired(self, user):
        """Test is_expired property for expired token."""
        token = EmailVerificationToken.objects.create(user=user)
        
        # Manually set created_at to past (more than 24 hours ago)
        token.created_at = timezone.now() - timedelta(hours=25)
        token.save()
        
        assert token.is_expired is True
    
    def test_token_expires_at_property(self, user):
        """Test expires_at property."""
        token = EmailVerificationToken.objects.create(user=user)
        
        expected_expires = token.created_at + timedelta(hours=24)
        assert token.expires_at == expected_expires
    
    def test_token_verify_method(self, user):
        """Test verify method."""
        token = EmailVerificationToken.objects.create(user=user)
        
        assert token.is_verified is False
        assert token.verified_at is None
        
        token.verify()
        
        assert token.is_verified is True
        assert token.verified_at is not None
        assert isinstance(token.verified_at, timezone.datetime)
    
    def test_token_verify_activates_user(self, inactive_user):
        """Test verify method activates inactive user."""
        token = EmailVerificationToken.objects.create(user=inactive_user)
        
        assert inactive_user.is_active is False
        
        token.verify()
        
        inactive_user.refresh_from_db()
        assert inactive_user.is_active is True
    
    def test_token_verify_does_not_deactivate_active_user(self, user):
        """Test verify method does not deactivate active user."""
        token = EmailVerificationToken.objects.create(user=user)
        
        assert user.is_active is True
        
        token.verify()
        
        user.refresh_from_db()
        assert user.is_active is True
    
    def test_token_create_for_user_creates_new_token(self, user):
        """Test create_for_user creates new token."""
        token = EmailVerificationToken.create_for_user(user)
        
        assert token is not None
        assert token.user == user
        assert token.is_verified is False
    
    def test_token_create_for_user_deletes_existing(self, user):
        """Test create_for_user deletes existing token."""
        old_token = EmailVerificationToken.objects.create(user=user)
        old_token_id = old_token.id
        
        new_token = EmailVerificationToken.create_for_user(user)
        
        # Old token should be deleted
        assert not EmailVerificationToken.objects.filter(id=old_token_id).exists()
        # New token should exist
        assert new_token.id != old_token_id
    
    def test_token_get_valid_token_valid(self, user):
        """Test get_valid_token returns valid token."""
        token = EmailVerificationToken.objects.create(user=user)
        
        retrieved = EmailVerificationToken.get_valid_token(token.token)
        
        assert retrieved is not None
        assert retrieved.id == token.id
    
    def test_token_get_valid_token_expired(self, user):
        """Test get_valid_token returns None for expired token."""
        token = EmailVerificationToken.objects.create(user=user)
        token.created_at = timezone.now() - timedelta(hours=25)
        token.save()
        
        retrieved = EmailVerificationToken.get_valid_token(token.token)
        
        assert retrieved is None
    
    def test_token_get_valid_token_not_found(self, user):
        """Test get_valid_token returns None for non-existent token."""
        fake_token = uuid.uuid4()
        
        retrieved = EmailVerificationToken.get_valid_token(fake_token)
        
        assert retrieved is None
    
    def test_token_one_to_one_relationship(self, user):
        """Test one-to-one relationship with User."""
        token = EmailVerificationToken.objects.create(user=user)
        
        # User should have access to token via related_name
        assert hasattr(user, 'auth_email_token')
        assert user.auth_email_token == token
    
    def test_token_unique_constraint(self, user):
        """Test that token field is unique."""
        token1 = EmailVerificationToken.objects.create(user=user)
        
        # Create another user and token
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        token2 = EmailVerificationToken.objects.create(user=user2)
        
        # Tokens should be different
        assert token1.token != token2.token


class TestUserProfile:
    """Tests for UserProfile model."""
    
    def test_profile_creation(self, user):
        """Test basic profile creation."""
        profile = UserProfile.objects.create(
            user=user,
            phone_number='+573001234567',
            region='Antioquia',
            municipality='Medellín',
            farm_name='Finca Test',
            years_experience=10,
            farm_size_hectares=5.5,
            preferred_language='es',
            email_notifications=True
        )
        
        assert profile.user == user
        assert profile.phone_number == '+573001234567'
        assert profile.region == 'Antioquia'
        assert profile.municipality == 'Medellín'
        assert profile.farm_name == 'Finca Test'
        assert profile.years_experience == 10
        assert profile.farm_size_hectares == 5.5
        assert profile.preferred_language == 'es'
        assert profile.email_notifications is True
        assert profile.created_at is not None
        assert profile.updated_at is not None
    
    def test_profile_str_representation(self, user):
        """Test string representation of profile."""
        user.first_name = 'John'
        user.last_name = 'Doe'
        user.save()
        
        profile = UserProfile.objects.create(user=user)
        
        assert str(profile) == 'Perfil de John Doe'
    
    def test_profile_str_representation_no_name(self, user):
        """Test string representation when user has no full name."""
        profile = UserProfile.objects.create(user=user)
        
        assert str(profile) == f'Perfil de {user.username}'
    
    def test_profile_full_name_property(self, user):
        """Test full_name property."""
        user.first_name = 'Jane'
        user.last_name = 'Smith'
        user.save()
        
        profile = UserProfile.objects.create(user=user)
        
        assert profile.full_name == 'Jane Smith'
    
    def test_profile_full_name_property_no_name(self, user):
        """Test full_name property when user has no full name."""
        profile = UserProfile.objects.create(user=user)
        
        assert profile.full_name == user.username
    
    def test_profile_role_property_superuser(self, user):
        """Test role property for superuser."""
        user.is_superuser = True
        user.save()
        
        profile = UserProfile.objects.create(user=user)
        
        assert profile.role == 'admin'
    
    def test_profile_role_property_analyst(self, user):
        """Test role property for analyst."""
        from django.contrib.auth.models import Group
        
        analyst_group, _ = Group.objects.get_or_create(name='analyst')
        user.groups.add(analyst_group)
        user.save()
        
        profile = UserProfile.objects.create(user=user)
        
        assert profile.role == 'analyst'
    
    def test_profile_role_property_farmer(self, user):
        """Test role property for farmer (default)."""
        profile = UserProfile.objects.create(user=user)
        
        assert profile.role == 'farmer'
    
    def test_profile_is_verified_property_with_token(self, user):
        """Test is_verified property when token exists."""
        profile = UserProfile.objects.create(user=user)
        token = EmailVerificationToken.objects.create(user=user)
        
        assert profile.is_verified is False
        
        token.verify()
        profile.refresh_from_db()
        
        assert profile.is_verified is True
    
    def test_profile_is_verified_property_no_token(self, user):
        """Test is_verified property when no token exists."""
        profile = UserProfile.objects.create(user=user)
        
        assert profile.is_verified is False
    
    def test_profile_is_verified_property_exception_handling(self, user):
        """Test is_verified property handles exceptions gracefully."""
        profile = UserProfile.objects.create(user=user)
        
        # Should not raise exception even if related objects don't exist
        result = profile.is_verified
        assert isinstance(result, bool)
    
    def test_profile_one_to_one_relationship(self, user):
        """Test one-to-one relationship with User."""
        profile = UserProfile.objects.create(user=user)
        
        # User should have access to profile via related_name
        assert hasattr(user, 'auth_profile')
        assert user.auth_profile == profile
    
    def test_profile_default_values(self, user):
        """Test profile default values."""
        profile = UserProfile.objects.create(user=user)
        
        assert profile.preferred_language == 'es'
        assert profile.email_notifications is True
    
    def test_profile_blank_fields(self, user):
        """Test that optional fields can be blank."""
        profile = UserProfile.objects.create(user=user)
        
        assert profile.phone_number == ''
        assert profile.region == ''
        assert profile.municipality == ''
        assert profile.farm_name == ''
        assert profile.years_experience is None
        assert profile.farm_size_hectares is None


class TestPendingEmailVerification:
    """Tests for PendingEmailVerification model."""
    
    def test_pending_verification_creation(self):
        """Test basic pending verification creation."""
        verification = PendingEmailVerification.objects.create(
            email='test@example.com',
            otp_code='123456',
            temp_data={'username': 'testuser', 'password': 'testpass'}
        )
        
        assert verification.email == 'test@example.com'
        assert verification.otp_code == '123456'
        assert verification.temp_data == {'username': 'testuser', 'password': 'testpass'}
        assert verification.created_at is not None
        assert verification.last_sent is not None
    
    def test_pending_verification_str_representation(self):
        """Test string representation of pending verification."""
        verification = PendingEmailVerification.objects.create(
            email='test@example.com',
            otp_code='123456'
        )
        
        assert str(verification) == 'OTP para test@example.com - 123456'
    
    def test_pending_verification_is_expired_fresh(self):
        """Test is_expired method for fresh verification."""
        verification = PendingEmailVerification.objects.create(
            email='test@example.com',
            otp_code='123456'
        )
        
        assert verification.is_expired() is False
    
    def test_pending_verification_is_expired_old(self):
        """Test is_expired method for old verification."""
        verification = PendingEmailVerification.objects.create(
            email='test@example.com',
            otp_code='123456'
        )
        
        # Manually set created_at to past (more than 10 minutes ago)
        verification.created_at = timezone.now() - timedelta(minutes=11)
        verification.save()
        
        assert verification.is_expired() is True
    
    def test_pending_verification_generate_code_static(self):
        """Test generate_code static method."""
        code = PendingEmailVerification.generate_code()
        
        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()
        assert 100000 <= int(code) <= 999999
    
    def test_pending_verification_generate_code_uniqueness(self):
        """Test that generate_code produces different codes."""
        codes = [PendingEmailVerification.generate_code() for _ in range(10)]
        
        # Should have some uniqueness (not all the same)
        assert len(set(codes)) > 1
    
    def test_pending_verification_unique_email(self):
        """Test that email field is unique."""
        PendingEmailVerification.objects.create(
            email='test@example.com',
            otp_code='123456'
        )
        
        # Should raise IntegrityError when trying to create duplicate
        with pytest.raises(Exception):  # IntegrityError or similar
            PendingEmailVerification.objects.create(
                email='test@example.com',
                otp_code='654321'
            )
    
    def test_pending_verification_temp_data_default(self):
        """Test that temp_data defaults to empty dict."""
        verification = PendingEmailVerification.objects.create(
            email='test@example.com',
            otp_code='123456'
        )
        
        assert verification.temp_data == {}
    
    def test_pending_verification_last_sent_updates(self):
        """Test that last_sent field updates on save."""
        verification = PendingEmailVerification.objects.create(
            email='test@example.com',
            otp_code='123456'
        )
        
        first_sent = verification.last_sent
        
        # Small delay
        import time
        time.sleep(0.01)
        
        verification.save()
        
        assert verification.last_sent > first_sent

