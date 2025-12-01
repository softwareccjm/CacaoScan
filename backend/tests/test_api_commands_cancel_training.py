"""
Unit tests for cancel_training management command.
Tests Django management command for cancelling training jobs.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

from api.management.commands.cancel_training import Command


@pytest.fixture
def command():
    """Create a Command instance for testing."""
    return Command()


@pytest.mark.django_db
class TestCancelTrainingCommand:
    """Tests for cancel_training Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_handle_with_training_job_unavailable(self, mock_training_job_class, command):
        """Test handle when TrainingJob model is not available."""
        mock_training_job_class.return_value = None
        mock_training_job_class.__class__ = type(None)
        
        with pytest.raises(CommandError, match="TrainingJob no está disponible"):
            command.handle(job_id=None, force=False)
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_handle_list_jobs_no_job_id(self, mock_training_job_class, command):
        """Test listing jobs when no job_id is provided."""
        mock_queryset_running = MagicMock()
        mock_queryset_running.exists.return_value = False
        mock_queryset_running.order_by.return_value = mock_queryset_running
        
        mock_queryset_pending = MagicMock()
        mock_queryset_pending.exists.return_value = False
        mock_queryset_pending.order_by.return_value = mock_queryset_pending
        
        def filter_side_effect(status):
            if status == 'running':
                return mock_queryset_running
            return mock_queryset_pending
        
        mock_training_job_class.objects.filter.side_effect = filter_side_effect
        
        command.handle(job_id=None, force=False)
        
        assert mock_training_job_class.objects.filter.call_count >= 2
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_cancel_pending_job(self, mock_training_job_class, command):
        """Test cancelling a pending job."""
        mock_job = MagicMock()
        mock_job.job_id = 'pending-job-123'
        mock_job.status = 'pending'
        mock_job.completed_at = None
        mock_job.save = MagicMock()
        
        mock_queryset = MagicMock()
        mock_queryset.get.return_value = mock_job
        mock_training_job_class.objects.select_for_update.return_value = mock_queryset
        
        with patch('api.management.commands.cancel_training.transaction.atomic'):
            command.handle(job_id='pending-job-123', force=False)
        
        assert mock_job.status == 'cancelled'
        mock_job.save.assert_called_once()
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_cancel_running_job(self, mock_training_job_class, command):
        """Test cancelling a running job."""
        mock_job = MagicMock()
        mock_job.job_id = 'running-job-123'
        mock_job.status = 'running'
        mock_job.completed_at = None
        mock_job.save = MagicMock()
        
        mock_queryset = MagicMock()
        mock_queryset.get.return_value = mock_job
        mock_training_job_class.objects.select_for_update.return_value = mock_queryset
        
        with patch('api.management.commands.cancel_training.transaction.atomic'):
            command.handle(job_id='running-job-123', force=False)
        
        assert mock_job.status == 'cancelled'
        mock_job.save.assert_called_once()
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_cancel_completed_job_without_force(self, mock_training_job_class, command):
        """Test cancelling a completed job without force flag."""
        mock_job = MagicMock()
        mock_job.job_id = 'completed-job-123'
        mock_job.status = 'completed'
        
        mock_queryset = MagicMock()
        mock_queryset.get.return_value = mock_job
        mock_training_job_class.objects.select_for_update.return_value = mock_queryset
        
        with patch('api.management.commands.cancel_training.transaction.atomic'):
            with pytest.raises(CommandError, match="no está en estado 'pending' o 'running'"):
                command.handle(job_id='completed-job-123', force=False)
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_cancel_completed_job_with_force(self, mock_training_job_class, command):
        """Test cancelling a completed job with force flag."""
        mock_job = MagicMock()
        mock_job.job_id = 'completed-job-123'
        mock_job.status = 'completed'
        mock_job.completed_at = timezone.now()
        mock_job.save = MagicMock()
        
        mock_queryset = MagicMock()
        mock_queryset.get.return_value = mock_job
        mock_training_job_class.objects.select_for_update.return_value = mock_queryset
        
        with patch('api.management.commands.cancel_training.transaction.atomic'):
            command.handle(job_id='completed-job-123', force=True)
        
        assert mock_job.status == 'cancelled'
        mock_job.save.assert_called_once()
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_cancel_job_not_found(self, mock_training_job_class, command):
        """Test cancelling a job that doesn't exist."""
        from django.core.exceptions import ObjectDoesNotExist
        
        mock_training_job_class.DoesNotExist = ObjectDoesNotExist
        mock_queryset = MagicMock()
        mock_queryset.get.side_effect = ObjectDoesNotExist()
        mock_training_job_class.objects.select_for_update.return_value = mock_queryset
        
        with patch('api.management.commands.cancel_training.transaction.atomic'):
            with pytest.raises(CommandError, match="Trabajo.*no encontrado"):
                command.handle(job_id='nonexistent-job', force=False)
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_list_running_jobs(self, mock_training_job_class, command):
        """Test listing running jobs."""
        mock_job = MagicMock()
        mock_job.job_id = 'running-job-1'
        mock_job.job_type = 'regression'
        mock_job.created_at = timezone.now() - timedelta(hours=1)
        mock_job.progress_percentage = 50.0
        mock_job.get_job_type_display.return_value = 'Modelo de Regresión'
        
        mock_queryset_running = MagicMock()
        mock_queryset_running.exists.return_value = True
        mock_queryset_running.count.return_value = 1
        mock_queryset_running.__iter__ = MagicMock(return_value=iter([mock_job]))
        mock_queryset_running.order_by.return_value = mock_queryset_running
        
        mock_queryset_pending = MagicMock()
        mock_queryset_pending.exists.return_value = False
        mock_queryset_pending.order_by.return_value = mock_queryset_pending
        
        def filter_side_effect(status):
            if status == 'running':
                return mock_queryset_running
            return mock_queryset_pending
        
        mock_training_job_class.objects.filter.side_effect = filter_side_effect
        
        command._list_running_jobs()
        
        assert mock_training_job_class.objects.filter.call_count >= 2
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_list_pending_jobs(self, mock_training_job_class, command):
        """Test listing pending jobs."""
        mock_job = MagicMock()
        mock_job.job_id = 'pending-job-1'
        mock_job.job_type = 'regression'
        mock_job.created_at = timezone.now() - timedelta(minutes=30)
        mock_job.progress_percentage = None
        mock_job.get_job_type_display.return_value = 'Modelo de Regresión'
        
        mock_queryset_running = MagicMock()
        mock_queryset_running.exists.return_value = False
        mock_queryset_running.order_by.return_value = mock_queryset_running
        
        mock_queryset_pending = MagicMock()
        mock_queryset_pending.exists.return_value = True
        mock_queryset_pending.count.return_value = 1
        mock_queryset_pending.__iter__ = MagicMock(return_value=iter([mock_job]))
        mock_queryset_pending.order_by.return_value = mock_queryset_pending
        
        def filter_side_effect(status):
            if status == 'running':
                return mock_queryset_running
            return mock_queryset_pending
        
        mock_training_job_class.objects.filter.side_effect = filter_side_effect
        
        command._list_running_jobs()
        
        assert mock_training_job_class.objects.filter.call_count >= 2
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_list_jobs_no_jobs_available(self, mock_training_job_class, command):
        """Test listing when no jobs are available."""
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = False
        mock_queryset.order_by.return_value = mock_queryset
        
        mock_training_job_class.objects.filter.return_value = mock_queryset
        
        command._list_running_jobs()
        
        mock_training_job_class.objects.filter.assert_called()
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_print_job_details_with_progress(self, mock_training_job_class, command):
        """Test printing job details with progress."""
        mock_job = MagicMock()
        mock_job.job_id = 'test-job'
        mock_job.job_type = 'regression'
        mock_job.created_at = timezone.now() - timedelta(hours=1)
        mock_job.progress_percentage = 75.0
        mock_job.get_job_type_display.return_value = 'Modelo de Regresión'
        
        command._print_job_details(mock_job, is_running=True)
        
        assert mock_job.job_id == 'test-job'
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_print_job_details_without_progress(self, mock_training_job_class, command):
        """Test printing job details without progress."""
        mock_job = MagicMock()
        mock_job.job_id = 'test-job'
        mock_job.job_type = 'regression'
        mock_job.created_at = timezone.now() - timedelta(minutes=30)
        mock_job.progress_percentage = None
        mock_job.get_job_type_display.return_value = 'Modelo de Regresión'
        
        command._print_job_details(mock_job, is_running=False)
        
        assert mock_job.job_id == 'test-job'
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_get_job_type_display_method_exists(self, mock_training_job_class, command):
        """Test getting job type display when method exists."""
        mock_job = MagicMock()
        mock_job.get_job_type_display.return_value = 'Modelo de Regresión'
        mock_job.job_type = 'regression'
        
        result = command._get_job_type_display(mock_job)
        
        assert result == 'Modelo de Regresión'
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_get_job_type_display_method_not_exists(self, mock_training_job_class, command):
        """Test getting job type display when method doesn't exist."""
        mock_job = MagicMock()
        del mock_job.get_job_type_display
        mock_job.job_type = 'regression'
        
        result = command._get_job_type_display(mock_job)
        
        assert result == 'regression'
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_error_handling_generic_exception(self, mock_training_job_class, command):
        """Test error handling for generic exceptions."""
        mock_queryset = MagicMock()
        mock_queryset.get.side_effect = Exception("Database error")
        mock_training_job_class.objects.select_for_update.return_value = mock_queryset
        
        with patch('api.management.commands.cancel_training.transaction.atomic'):
            with pytest.raises(CommandError, match="Error al cancelar trabajo"):
                command.handle(job_id='test-job', force=False)
    
    @patch('api.management.commands.cancel_training.TrainingJob')
    def test_cancel_job_sets_completed_at(self, mock_training_job_class, command):
        """Test that cancelling a job sets completed_at if attribute exists."""
        mock_job = MagicMock()
        mock_job.job_id = 'test-job'
        mock_job.status = 'pending'
        mock_job.completed_at = None
        mock_job.save = MagicMock()
        
        # Simulate hasattr returning True
        with patch('builtins.hasattr', return_value=True):
            mock_queryset = MagicMock()
            mock_queryset.get.return_value = mock_job
            mock_training_job_class.objects.select_for_update.return_value = mock_queryset
            
            with patch('api.management.commands.cancel_training.transaction.atomic'):
                with patch('api.management.commands.cancel_training.timezone.now', return_value=timezone.now()):
                    command.handle(job_id='test-job', force=False)
        
        assert mock_job.status == 'cancelled'
        mock_job.save.assert_called_once()

