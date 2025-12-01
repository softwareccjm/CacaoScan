"""
Tests unitarios para core.utils.cache_helpers.

Cubre todas las funciones de manejo de caché:
- invalidate_cache_pattern
- invalidate_system_stats_cache
- invalidate_models_status_cache
- invalidate_dataset_validation_cache
- invalidate_latest_metrics_cache
- invalidate_user_related_cache
- invalidate_model_metrics_cache
- get_cache_key
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.cache import cache
from django.core.cache.backends.dummy import DummyCache

from core.utils.cache_helpers import (
    invalidate_cache_pattern,
    invalidate_system_stats_cache,
    invalidate_models_status_cache,
    invalidate_dataset_validation_cache,
    invalidate_latest_metrics_cache,
    invalidate_user_related_cache,
    invalidate_model_metrics_cache,
    get_cache_key
)


class CacheHelpersTestCase(TestCase):
    """Tests para funciones de cache helpers."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear cache before each test
        cache.clear()

    @patch('core.utils.cache_helpers.cache')
    @patch('core.utils.cache_helpers.logger')
    def test_invalidate_cache_pattern_with_exact_key(self, mock_logger, mock_cache):
        """Test invalidate_cache_pattern with exact key (no wildcard)."""
        pattern = 'test_key'
        
        invalidate_cache_pattern(pattern)
        
        mock_cache.delete.assert_called_once_with(pattern, version=None)
        mock_logger.info.assert_called_once_with(f"Cache invalidated for key: {pattern}")

    @patch('core.utils.cache_helpers.cache')
    @patch('core.utils.cache_helpers.logger')
    def test_invalidate_cache_pattern_with_wildcard(self, mock_logger, mock_cache):
        """Test invalidate_cache_pattern with wildcard pattern."""
        pattern = 'test_*'
        
        invalidate_cache_pattern(pattern)
        
        # With wildcard, delete is not called directly
        mock_logger.info.assert_called_once_with(f"Cache invalidation requested for pattern: {pattern}")

    @patch('core.utils.cache_helpers.cache')
    @patch('core.utils.cache_helpers.logger')
    def test_invalidate_cache_pattern_exception_handling(self, mock_logger, mock_cache):
        """Test invalidate_cache_pattern handles exceptions gracefully."""
        pattern = 'test_key'
        mock_cache.delete.side_effect = Exception("Cache error")
        
        invalidate_cache_pattern(pattern)
        
        mock_logger.warning.assert_called_once()
        error_message = mock_logger.warning.call_args[0][0]
        self.assertIn("Error invalidating cache pattern", error_message)
        self.assertIn(pattern, error_message)

    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_system_stats_cache(self, mock_invalidate):
        """Test invalidate_system_stats_cache calls correct patterns."""
        invalidate_system_stats_cache()
        
        expected_calls = [
            (('system_stats_*',),),
            (('dashboard_stats_*',),),
            (('admin_stats_*',),)
        ]
        
        self.assertEqual(mock_invalidate.call_count, 3)
        actual_calls = [call[0] for call in mock_invalidate.call_args_list]
        expected_patterns = [call[0][0] for call in expected_calls]
        actual_patterns = [call[0] for call in actual_calls]
        
        for pattern in expected_patterns:
            self.assertIn(pattern, actual_patterns)

    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_models_status_cache(self, mock_invalidate):
        """Test invalidate_models_status_cache."""
        invalidate_models_status_cache()
        
        mock_invalidate.assert_called_once_with('models_status_*')

    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_dataset_validation_cache(self, mock_invalidate):
        """Test invalidate_dataset_validation_cache."""
        invalidate_dataset_validation_cache()
        
        mock_invalidate.assert_called_once_with('dataset_validation_*')

    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_latest_metrics_cache(self, mock_invalidate):
        """Test invalidate_latest_metrics_cache."""
        invalidate_latest_metrics_cache()
        
        mock_invalidate.assert_called_once_with('latest_metrics_*')

    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_user_related_cache_with_user_id(self, mock_invalidate):
        """Test invalidate_user_related_cache with specific user_id."""
        user_id = 123
        
        invalidate_user_related_cache(user_id)
        
        expected_calls = [
            (f'user_stats_{user_id}_*',),
            (f'user_activity_{user_id}_*',)
        ]
        
        self.assertEqual(mock_invalidate.call_count, 2)
        actual_patterns = [call[0][0] for call in mock_invalidate.call_args_list]
        for expected_pattern, _ in expected_calls:
            self.assertIn(expected_pattern, actual_patterns)

    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_user_related_cache_without_user_id(self, mock_invalidate):
        """Test invalidate_user_related_cache without user_id."""
        invalidate_user_related_cache()
        
        expected_calls = [
            ('user_stats_*',),
            ('user_activity_*',)
        ]
        
        self.assertEqual(mock_invalidate.call_count, 2)
        actual_patterns = [call[0][0] for call in mock_invalidate.call_args_list]
        for expected_pattern, _ in expected_calls:
            self.assertIn(expected_pattern, actual_patterns)

    @patch('core.utils.cache_helpers.invalidate_latest_metrics_cache')
    @patch('core.utils.cache_helpers.invalidate_cache_pattern')
    def test_invalidate_model_metrics_cache(self, mock_invalidate, mock_invalidate_latest):
        """Test invalidate_model_metrics_cache calls both functions."""
        invalidate_model_metrics_cache()
        
        mock_invalidate_latest.assert_called_once()
        mock_invalidate.assert_called_once_with('model_metrics_*')

    def test_get_cache_key_with_prefix_only(self):
        """Test get_cache_key with only prefix."""
        result = get_cache_key('test_prefix')
        
        self.assertEqual(result, 'test_prefix')

    def test_get_cache_key_with_args(self):
        """Test get_cache_key with positional arguments."""
        result = get_cache_key('prefix', 'arg1', 'arg2', 'arg3')
        
        self.assertEqual(result, 'prefix:arg1:arg2:arg3')

    def test_get_cache_key_with_kwargs(self):
        """Test get_cache_key with keyword arguments."""
        result = get_cache_key('prefix', key1='value1', key2='value2')
        
        # kwargs should be sorted
        self.assertEqual(result, 'prefix:key1=value1:key2=value2')

    def test_get_cache_key_with_args_and_kwargs(self):
        """Test get_cache_key with both args and kwargs."""
        result = get_cache_key('prefix', 'arg1', 'arg2', key1='value1', key2='value2')
        
        # kwargs should be sorted, args come first
        self.assertEqual(result, 'prefix:arg1:arg2:key1=value1:key2=value2')

    def test_get_cache_key_with_special_characters(self):
        """Test get_cache_key handles special characters in values."""
        result = get_cache_key('prefix', 'arg with spaces', key='value:with:colons')
        
        self.assertIn('arg with spaces', result)
        self.assertIn('value:with:colons', result)

    def test_get_cache_key_kwargs_are_sorted(self):
        """Test get_cache_key sorts kwargs alphabetically."""
        result = get_cache_key('prefix', z_key='z_value', a_key='a_value', m_key='m_value')
        
        # Check that kwargs are in sorted order
        parts = result.split(':')
        kwargs_part = ':'.join([p for p in parts if '=' in p])
        self.assertEqual(kwargs_part, 'a_key=a_value:m_key=m_value:z_key=z_value')

