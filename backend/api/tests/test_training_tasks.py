"""
Tests for training tasks.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.utils import timezone

from api.tasks.training_tasks import train_model_task, auto_train_model_task


@pytest.fixture
def mock_task():
    """Create a mock Celery task."""
    task = Mock()
    task.update_state = Mock()
    return task


@pytest.mark.django_db
class TestTrainingTasks:
    """Tests for training tasks."""
    
    def test_train_model_task_success(self, mock_task):
        """Test successful model training task."""
        with patch('api.tasks.training_tasks.TrainingJob') as mock_job_model:
            mock_job = Mock()
            mock_job.job_id = 'job_123'
            mock_job.status = 'pending'
            mock_job.update_progress = Mock()
            mock_job.mark_completed = Mock()
            mock_job.logs = ''
            mock_job.save = Mock()
            mock_job_model.objects.get.return_value = mock_job
            
            with patch('ml.pipeline.train_all.run_training_pipeline', return_value=True):
                with patch('ml.utils.paths.get_datasets_dir') as mock_get_dir:
                    from pathlib import Path
                    mock_path = Mock(spec=Path)
                    mock_path.exists.return_value = True
                    mock_get_dir.return_value = mock_path
                    
                    result = train_model_task(mock_task, 'job_123', {
                        'epochs': 150,
                        'batch_size': 16,
                        'learning_rate': 0.001
                    })
                    
                    assert result['status'] == 'completed'
                    assert result['job_id'] == 'job_123'
                    assert 'message' in result
                    assert mock_job.mark_completed.called
    
    def test_train_model_task_dataset_not_found(self, mock_task):
        """Test training task when dataset not found."""
        with patch('api.tasks.training_tasks.TrainingJob') as mock_job_model:
            mock_job = Mock()
            mock_job.job_id = 'job_123'
            mock_job.mark_failed = Mock()
            mock_job_model.objects.get.return_value = mock_job
            
            with patch('ml.utils.paths.get_datasets_dir') as mock_get_dir:
                from pathlib import Path
                mock_path = Mock(spec=Path)
                mock_path.exists.return_value = False
                mock_get_dir.return_value = mock_path
                
                result = train_model_task(mock_task, 'job_123', {})
                
                assert result['status'] == 'failed'
                assert 'error' in result
                assert mock_job.mark_failed.called
    
    def test_train_model_task_training_failed(self, mock_task):
        """Test training task when training fails."""
        with patch('api.tasks.training_tasks.TrainingJob') as mock_job_model:
            mock_job = Mock()
            mock_job.job_id = 'job_123'
            mock_job.update_progress = Mock()
            mock_job.mark_failed = Mock()
            mock_job_model.objects.get.return_value = mock_job
            
            with patch('ml.pipeline.train_all.run_training_pipeline', return_value=False):
                with patch('ml.utils.paths.get_datasets_dir') as mock_get_dir:
                    from pathlib import Path
                    mock_path = Mock(spec=Path)
                    mock_path.exists.return_value = True
                    mock_get_dir.return_value = mock_path
                    
                    result = train_model_task(mock_task, 'job_123', {})
                    
                    assert result['status'] == 'failed'
                    assert 'error' in result
                    assert mock_job.mark_failed.called
    
    def test_train_model_task_job_not_found(self, mock_task):
        """Test training task when job not found."""
        with patch('api.tasks.training_tasks.TrainingJob') as mock_job_model:
            # Create a proper DoesNotExist exception
            class MockDoesNotExist(Exception):
                pass
            mock_job_model.DoesNotExist = MockDoesNotExist
            mock_job_model.objects.get.side_effect = MockDoesNotExist()
            
            result = train_model_task(mock_task, 'job_123', {})
            
            assert result['status'] == 'failed'
            assert 'error' in result
            assert result['error'] == 'Job not found'
    
    def test_train_model_task_exception(self, mock_task):
        """Test training task with exception."""
        with patch('api.tasks.training_tasks.TrainingJob') as mock_job_model:
            mock_job = Mock()
            mock_job.job_id = 'job_123'
            mock_job.mark_failed = Mock()
            mock_job_model.objects.get.return_value = mock_job
            
            with patch('ml.utils.paths.get_datasets_dir', side_effect=Exception("Unexpected error")):
                result = train_model_task(mock_task, 'job_123', {})
                
                assert result['status'] == 'failed'
                assert 'error' in result
    
    def test_auto_train_model_task_success(self, mock_task):
        """Test successful auto training task."""
        with patch('ml.pipeline.train_all.run_training_pipeline', return_value=True):
            with patch('ml.utils.paths.get_datasets_dir') as mock_get_dir:
                from pathlib import Path
                mock_path = Mock(spec=Path)
                mock_path.exists.return_value = True
                mock_get_dir.return_value = mock_path
                
                with patch('pathlib.Path.rglob', return_value=['image1.bmp', 'image2.bmp']):
                    result = auto_train_model_task(mock_task, force=False, config=None)
                    
                    assert result['status'] == 'completed'
                    assert 'message' in result
    
    def test_auto_train_model_task_dataset_not_found(self, mock_task):
        """Test auto training task when dataset not found."""
        with patch('ml.utils.paths.get_datasets_dir') as mock_get_dir:
            from pathlib import Path
            mock_path = Mock(spec=Path)
            mock_path.exists.return_value = False
            mock_get_dir.return_value = mock_path
            
            result = auto_train_model_task(mock_task, force=False, config=None)
            
            assert result['status'] == 'skipped'
            assert 'message' in result
    
    def test_auto_train_model_task_no_images(self, mock_task):
        """Test auto training task when no images found."""
        with patch('ml.utils.paths.get_datasets_dir') as mock_get_dir:
            from pathlib import Path
            mock_path = Mock(spec=Path)
            mock_path.exists.return_value = True
            mock_get_dir.return_value = mock_path
            
            with patch('pathlib.Path.exists', return_value=False):
                with patch('pathlib.Path.rglob', return_value=[]):
                    result = auto_train_model_task(mock_task, force=False, config=None)
                    
                    assert result['status'] == 'skipped'
                    assert 'message' in result
    
    def test_auto_train_model_task_training_failed(self, mock_task):
        """Test auto training task when training fails."""
        with patch('ml.pipeline.train_all.run_training_pipeline', return_value=False):
            with patch('ml.utils.paths.get_datasets_dir') as mock_get_dir:
                from pathlib import Path
                mock_path = Mock(spec=Path)
                mock_path.exists.return_value = True
                mock_get_dir.return_value = mock_path
                
                with patch('pathlib.Path.rglob', return_value=['image1.bmp']):
                    result = auto_train_model_task(mock_task, force=False, config=None)
                    
                    assert result['status'] == 'failed'
                    assert 'message' in result
    
    def test_auto_train_model_task_with_config(self, mock_task):
        """Test auto training task with custom config."""
        custom_config = {
            'epochs': 200,
            'batch_size': 32,
            'learning_rate': 0.0005
        }
        
        with patch('ml.pipeline.train_all.run_training_pipeline', return_value=True) as mock_pipeline:
            with patch('ml.utils.paths.get_datasets_dir') as mock_get_dir:
                from pathlib import Path
                mock_path = Mock(spec=Path)
                mock_path.exists.return_value = True
                mock_get_dir.return_value = mock_path
                
                with patch('pathlib.Path.rglob', return_value=['image1.bmp']):
                    result = auto_train_model_task(mock_task, force=False, config=custom_config)
                    
                    assert result['status'] == 'completed'
                    # Verify config was passed
                    call_kwargs = mock_pipeline.call_args[1]
                    assert call_kwargs['epochs'] == 200
                    assert call_kwargs['batch_size'] == 32
    
    def test_auto_train_model_task_exception(self, mock_task):
        """Test auto training task with exception."""
        with patch('ml.utils.paths.get_datasets_dir', side_effect=Exception("Unexpected error")):
            result = auto_train_model_task(mock_task, force=False, config=None)
            
            assert result['status'] == 'failed'
            assert 'error' in result

