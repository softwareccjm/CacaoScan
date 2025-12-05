"""
Tests for stats tasks.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from api.tasks.stats_tasks import calculate_admin_stats_task


@pytest.fixture
def mock_task():
    """Create a mock Celery task."""
    task = Mock()
    task.update_state = Mock()
    return task


@pytest.mark.django_db
class TestStatsTasks:
    """Tests for stats tasks."""
    
    def test_calculate_admin_stats_task_success(self, mock_task):
        """Test successful calculation of admin stats."""
        with patch('api.tasks.stats_tasks.StatsService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.get_all_stats.return_value = {
                'users': {'total': 10},
                'images': {'total': 20},
                'generated_at': '2024-01-01T00:00:00'
            }
            
            # Call the task with mock_task as self (bind=True)
            result = calculate_admin_stats_task(mock_task)
            
            assert result['status'] == 'completed'
            assert 'stats' in result
            assert mock_task.update_state.called
    
    def test_calculate_admin_stats_task_error(self, mock_task):
        """Test error handling in calculate_admin_stats_task."""
        with patch('api.tasks.stats_tasks.StatsService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            mock_service.get_all_stats.side_effect = Exception("Database error")
            mock_service.get_empty_stats.return_value = {
                'users': {'total': 0},
                'images': {'total': 0}
            }
            
            # Call the task with mock_task as self (bind=True)
            result = calculate_admin_stats_task(mock_task)
            
            assert result['status'] == 'error'
            assert 'stats' in result
            assert 'error' in result
            assert result['error'] == 'Database error'

