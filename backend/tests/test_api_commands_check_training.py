"""
Unit tests for check_training management command.
Tests Django management command for checking training job status.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from datetime import timedelta

from api.management.commands.check_training import Command


@pytest.fixture
def command():
    """Create a Command instance for testing."""
    return Command()


@pytest.fixture
def mock_training_job_model():
    """Mock TrainingJob model."""
    from unittest.mock import MagicMock
    
    class MockTrainingJob:
        objects = MagicMock()
        
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def get_job_type_display(self):
            return 'Modelo de Regresión'
    
    return MockTrainingJob


@pytest.mark.django_db
class TestCheckTrainingCommand:
    """Tests for check_training Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_handle_with_training_job_unavailable(self, mock_training_job_class, command):
        """Test handle when TrainingJob model is not available."""
        mock_training_job_class.return_value = None
        mock_training_job_class.__class__ = type(None)
        
        with pytest.raises(CommandError, match="TrainingJob no está disponible"):
            command.handle(status='all', job_id=None)
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_handle_single_job_exists(self, mock_training_job_class, command):
        """Test displaying details for a single job."""
        mock_job = MagicMock()
        mock_job.job_id = 'test-job-123'
        mock_job.job_type = 'regression'
        mock_job.status = 'running'
        mock_job.created_at = timezone.now() - timedelta(hours=2)
        mock_job.started_at = timezone.now() - timedelta(hours=2)
        mock_job.completed_at = None
        mock_job.created_by = MagicMock(username='testuser')
        mock_job.logs = 'Line 1\nLine 2\nLine 3'
        mock_job.progress_percentage = 50.0
        mock_job.get_job_type_display.return_value = 'Modelo de Regresión'
        
        mock_training_job_class.objects.get.return_value = mock_job
        
        command.handle(status='all', job_id='test-job-123')
        
        mock_training_job_class.objects.get.assert_called_once_with(job_id='test-job-123')
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_handle_single_job_not_found(self, mock_training_job_class, command):
        """Test handling when single job is not found."""
        from django.core.exceptions import ObjectDoesNotExist
        
        mock_training_job_class.DoesNotExist = ObjectDoesNotExist
        mock_training_job_class.objects.get.side_effect = ObjectDoesNotExist()
        
        with pytest.raises(CommandError, match="Job.*no encontrado"):
            command.handle(status='all', job_id='nonexistent-job')
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_display_running_jobs(self, mock_training_job_class, command):
        """Test displaying running jobs."""
        mock_job = MagicMock()
        mock_job.job_id = 'running-job-1'
        mock_job.job_type = 'regression'
        mock_job.created_at = timezone.now() - timedelta(hours=1)
        mock_job.progress_percentage = 75.0
        mock_job.get_job_type_display.return_value = 'Modelo de Regresión'
        
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = MagicMock(return_value=iter([mock_job]))
        mock_queryset.order_by.return_value = mock_queryset
        
        mock_training_job_class.objects.filter.return_value = mock_queryset
        
        command._display_running_jobs('running')
        
        mock_training_job_class.objects.filter.assert_called()
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_display_pending_jobs(self, mock_training_job_class, command):
        """Test displaying pending jobs."""
        mock_job = MagicMock()
        mock_job.job_id = 'pending-job-1'
        mock_job.job_type = 'regression'
        mock_job.created_at = timezone.now() - timedelta(minutes=30)
        mock_job.progress_percentage = None
        mock_job.get_job_type_display.return_value = 'Modelo de Regresión'
        
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = MagicMock(return_value=iter([mock_job]))
        mock_queryset.order_by.return_value = mock_queryset
        
        mock_training_job_class.objects.filter.return_value = mock_queryset
        
        command._display_pending_jobs('pending')
        
        mock_training_job_class.objects.filter.assert_called()
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_display_summary_all_statuses(self, mock_training_job_class, command):
        """Test displaying summary with all statuses."""
        mock_training_job_class.objects.filter.return_value.count.return_value = 0
        
        command._display_summary('all')
        
        assert mock_training_job_class.objects.filter.call_count >= 3
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_display_summary_specific_status(self, mock_training_job_class, command):
        """Test that summary is not displayed for specific status."""
        command._display_summary('running')
        
        mock_training_job_class.objects.filter.assert_not_called()
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_display_job_summary_with_progress(self, mock_training_job_class, command):
        """Test displaying job summary with progress."""
        mock_job = MagicMock()
        mock_job.job_id = 'test-job'
        mock_job.job_type = 'regression'
        mock_job.created_at = timezone.now() - timedelta(hours=2)
        mock_job.progress_percentage = 50.0
        mock_job.get_job_type_display.return_value = 'Modelo de Regresión'
        
        command._display_job_summary(mock_job, show_cancel=True)
        
        assert mock_job.job_id == 'test-job'
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_display_job_summary_without_progress(self, mock_training_job_class, command):
        """Test displaying job summary without progress."""
        mock_job = MagicMock()
        mock_job.job_id = 'test-job'
        mock_job.job_type = 'regression'
        mock_job.created_at = timezone.now() - timedelta(hours=1)
        mock_job.progress_percentage = None
        mock_job.get_job_type_display.return_value = 'Modelo de Regresión'
        
        command._display_job_summary(mock_job, show_cancel=False)
        
        assert mock_job.job_id == 'test-job'
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_display_job_details_complete(self, mock_training_job_class, command):
        """Test displaying complete job details."""
        mock_job = MagicMock()
        mock_job.job_id = 'complete-job'
        mock_job.job_type = 'regression'
        mock_job.status = 'completed'
        mock_job.created_at = timezone.now() - timedelta(hours=3)
        mock_job.started_at = timezone.now() - timedelta(hours=3)
        mock_job.completed_at = timezone.now() - timedelta(minutes=30)
        mock_job.created_by = MagicMock(username='testuser')
        mock_job.logs = 'Log line 1\nLog line 2\nLog line 3\nLog line 4\nLog line 5\nLog line 6'
        mock_job.progress_percentage = 100.0
        mock_job.get_job_type_display.return_value = 'Modelo de Regresión'
        
        command._display_job_details(mock_job)
        
        assert mock_job.job_id == 'complete-job'
        assert mock_job.status == 'completed'
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_display_job_details_without_optional_fields(self, mock_training_job_class, command):
        """Test displaying job details without optional fields."""
        mock_job = MagicMock()
        mock_job.job_id = 'simple-job'
        mock_job.job_type = 'regression'
        mock_job.status = 'pending'
        mock_job.created_at = timezone.now()
        mock_job.started_at = None
        mock_job.completed_at = None
        mock_job.created_by = None
        mock_job.logs = None
        mock_job.progress_percentage = None
        mock_job.get_job_type_display.return_value = 'Modelo de Regresión'
        
        command._display_job_details(mock_job)
        
        assert mock_job.job_id == 'simple-job'
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_error_handling_generic_exception(self, mock_training_job_class, command):
        """Test error handling for generic exceptions."""
        mock_training_job_class.objects.filter.side_effect = Exception("Database error")
        
        with pytest.raises(CommandError, match="Error al verificar entrenamientos"):
            command.handle(status='all', job_id=None)
    
    @patch('api.management.commands.check_training.TrainingJob')
    def test_filter_by_status_running(self, mock_training_job_class, command):
        """Test filtering by running status."""
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = False
        mock_queryset.order_by.return_value = mock_queryset
        mock_training_job_class.objects.filter.return_value = mock_queryset
        
        command._display_jobs_by_filter('running')
        
        mock_training_job_class.objects.filter.assert_called()

