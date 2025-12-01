"""
Unit tests for create_admin_user management command.
Tests Django management command for creating or updating admin users.
"""
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.auth.models import User
from django.db import transaction

from api.management.commands.create_admin_user import Command


@pytest.fixture
def command():
    """Create a Command instance for testing."""
    return Command()


@pytest.mark.django_db
class TestCreateAdminUserCommand:
    """Tests for create_admin_user Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    def test_create_new_admin_user(self, command):
        """Test creating a new admin user."""
        username = 'newadmin'
        email = 'newadmin@test.com'
        password = 'adminpass123'
        
        assert not User.objects.filter(username=username).exists()
        
        command.handle(
            username=username,
            email=email,
            password=password,
            first_name='New',
            last_name='Admin',
            no_input=True
        )
        
        user = User.objects.get(username=username)
        assert user.email == email
        assert user.first_name == 'New'
        assert user.last_name == 'Admin'
        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.is_active is True
        assert user.check_password(password)
    
    def test_update_existing_user(self, command):
        """Test updating an existing user to admin."""
        username = 'existinguser'
        user = User.objects.create_user(
            username=username,
            email='old@test.com',
            password='oldpass',
            is_superuser=False,
            is_staff=False
        )
        
        new_email = 'new@test.com'
        new_password = 'newpass123'
        
        command.handle(
            username=username,
            email=new_email,
            password=new_password,
            first_name='Updated',
            last_name='User',
            no_input=True
        )
        
        user.refresh_from_db()
        assert user.email == new_email
        assert user.first_name == 'Updated'
        assert user.last_name == 'User'
        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.is_active is True
        assert user.check_password(new_password)
    
    def test_create_user_with_email_conflict(self, command):
        """Test creating user when email is already in use by different user."""
        existing_user = User.objects.create_user(
            username='existing',
            email='conflict@test.com',
            password='pass123'
        )
        
        with pytest.raises(CommandError, match="Email.*already in use"):
            command.handle(
                username='newuser',
                email='conflict@test.com',
                password='pass123',
                first_name='New',
                last_name='User',
                no_input=True
            )
    
    def test_create_user_with_default_values(self, command):
        """Test creating user with default argument values."""
        command.handle(no_input=True)
        
        user = User.objects.get(username='admin')
        assert user.email == 'admin@cacaoscan.com'
        assert user.first_name == 'Admin'
        assert user.last_name == 'User'
        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.is_active is True
        assert user.check_password('admin123')
    
    def test_create_user_custom_parameters(self, command):
        """Test creating user with custom parameters."""
        username = 'customadmin'
        email = 'custom@test.com'
        password = 'custompass123'
        first_name = 'Custom'
        last_name = 'Admin'
        
        command.handle(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            no_input=True
        )
        
        user = User.objects.get(username=username)
        assert user.email == email
        assert user.first_name == first_name
        assert user.last_name == last_name
        assert user.check_password(password)
    
    def test_update_user_preserves_existing_data(self, command):
        """Test that updating user preserves data when not explicitly changed."""
        username = 'preserveuser'
        original_email = 'original@test.com'
        user = User.objects.create_user(
            username=username,
            email=original_email,
            password='oldpass',
            first_name='Original',
            last_name='Name'
        )
        
        command.handle(
            username=username,
            email=original_email,
            password='newpass123',
            first_name='Updated',
            last_name='Name',
            no_input=True
        )
        
        user.refresh_from_db()
        assert user.email == original_email
        assert user.first_name == 'Updated'
        assert user.last_name == 'Name'
        assert user.check_password('newpass123')
    
    def test_call_command_via_call_command(self):
        """Test calling command via Django's call_command."""
        username = 'callcommanduser'
        
        call_command(
            'create_admin_user',
            '--username', username,
            '--email', 'call@test.com',
            '--password', 'callpass123',
            '--first-name', 'Call',
            '--last-name', 'Command',
            '--no-input'
        )
        
        user = User.objects.get(username=username)
        assert user.email == 'call@test.com'
        assert user.is_superuser is True
        assert user.is_staff is True
    
    def test_error_handling_on_exception(self, command):
        """Test error handling when exception occurs."""
        with pytest.raises(CommandError):
            # Force an error by using invalid data
            with transaction.atomic():
                # Create user first
                User.objects.create_user(
                    username='erroruser',
                    email='error@test.com',
                    password='pass123'
                )
                # Try to create with same username but different email
                # This should raise an error
                command.handle(
                    username='erroruser',
                    email='different@test.com',
                    password='pass123',
                    first_name='Error',
                    last_name='User',
                    no_input=True
                )

