"""
Unit tests for regression evaluation module (evaluate.py).
Tests RegressionEvaluator, metrics computation, and model evaluation.
"""
import pytest
import torch
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from torch.utils.data import DataLoader, TensorDataset

from ml.regression.evaluate import (
    compute_regression_metrics,
    RegressionEvaluator,
    load_model_for_evaluation,
    evaluate_model_from_file
)
from ml.regression.models import TARGETS, TARGET_NAMES


@pytest.fixture
def sample_targets():
    """Create sample target values."""
    return np.array([20.0, 25.0, 30.0, 22.0, 28.0], dtype=np.float32)


@pytest.fixture
def sample_predictions():
    """Create sample prediction values."""
    return np.array([19.5, 25.2, 29.8, 22.1, 27.9], dtype=np.float32)


@pytest.fixture
def sample_model():
    """Create a simple mock model for testing."""
    model = Mock()
    model.eval = Mock()
    model.to = Mock(return_value=model)
    model.parameters = Mock(return_value=[torch.tensor([1.0])])
    return model


@pytest.fixture
def sample_dataloader(sample_targets):
    """Create a sample DataLoader for testing."""
    images = torch.randn(5, 3, 224, 224)
    targets = torch.tensor(sample_targets, dtype=torch.float32).unsqueeze(1)
    dataset = TensorDataset(images, targets)
    return DataLoader(dataset, batch_size=2, shuffle=False)


@pytest.fixture
def sample_multi_head_dataloader():
    """Create a sample multi-head DataLoader."""
    images = torch.randn(5, 3, 224, 224)
    targets_dict = {
        'alto': torch.tensor([20.0, 25.0, 30.0, 22.0, 28.0], dtype=torch.float32),
        'ancho': torch.tensor([12.0, 15.0, 18.0, 13.0, 16.0], dtype=torch.float32),
        'grosor': torch.tensor([8.0, 9.0, 10.0, 8.5, 9.5], dtype=torch.float32),
        'peso': torch.tensor([1.5, 1.8, 2.0, 1.6, 1.9], dtype=torch.float32)
    }
    
    class MultiHeadDataset:
        def __len__(self):
            return 5
        
        def __getitem__(self, idx):
            return images[idx], {k: v[idx] for k, v in targets_dict.items()}
    
    return DataLoader(MultiHeadDataset(), batch_size=2, shuffle=False)


class TestComputeRegressionMetrics:
    """Tests for compute_regression_metrics function."""
    
    def test_compute_metrics_basic(self, sample_targets, sample_predictions):
        """Test basic metrics computation."""
        metrics = compute_regression_metrics(sample_targets, sample_predictions)
        
        assert 'mae' in metrics
        assert 'mse' in metrics
        assert 'rmse' in metrics
        assert 'r2' in metrics
        assert 'mape' in metrics
        assert 'relative_error' in metrics
        assert 'n_samples' not in metrics  # Only added by evaluator
    
    def test_compute_metrics_all_positive(self, sample_targets, sample_predictions):
        """Test metrics with all positive values."""
        metrics = compute_regression_metrics(sample_targets, sample_predictions)
        
        assert metrics['mae'] >= 0
        assert metrics['mse'] >= 0
        assert metrics['rmse'] >= 0
        assert metrics['mape'] >= 0
        assert metrics['relative_error'] >= 0
    
    def test_compute_metrics_perfect_predictions(self):
        """Test metrics with perfect predictions."""
        targets = np.array([20.0, 25.0, 30.0], dtype=np.float32)
        predictions = np.array([20.0, 25.0, 30.0], dtype=np.float32)
        
        metrics = compute_regression_metrics(targets, predictions)
        
        assert metrics['mae'] == 0.0
        assert metrics['mse'] == 0.0
        assert metrics['rmse'] == 0.0
        assert metrics['r2'] == 1.0
    
    def test_compute_metrics_with_zeros(self):
        """Test metrics when targets contain zeros."""
        targets = np.array([0.0, 10.0, 20.0], dtype=np.float32)
        predictions = np.array([0.5, 10.5, 20.5], dtype=np.float32)
        
        metrics = compute_regression_metrics(targets, predictions)
        
        assert 'mae' in metrics
        assert 'mse' in metrics
        # MAPE should handle zeros correctly
        assert metrics['mape'] >= 0 or metrics['mape'] == 0.0
    
    def test_compute_metrics_all_zeros(self):
        """Test metrics when all targets are zero."""
        targets = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        predictions = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        
        metrics = compute_regression_metrics(targets, predictions)
        
        assert metrics['mape'] == 0.0
        assert metrics['relative_error'] == 0.0
    
    def test_compute_metrics_different_lengths(self):
        """Test that metrics raise error for different lengths."""
        targets = np.array([20.0, 25.0], dtype=np.float32)
        predictions = np.array([19.5, 25.2, 29.8], dtype=np.float32)
        
        with pytest.raises(ValueError):
            compute_regression_metrics(targets, predictions)
    
    def test_compute_metrics_empty_arrays(self):
        """Test metrics with empty arrays."""
        targets = np.array([], dtype=np.float32)
        predictions = np.array([], dtype=np.float32)
        
        # Should handle empty arrays gracefully
        metrics = compute_regression_metrics(targets, predictions)
        
        assert 'mae' in metrics
        assert 'mse' in metrics


class TestRegressionEvaluator:
    """Tests for RegressionEvaluator class."""
    
    def test_evaluator_initialization(self, sample_model, sample_dataloader):
        """Test RegressionEvaluator initialization."""
        evaluator = RegressionEvaluator(
            model=sample_model,
            test_loader=sample_dataloader,
            scalers=None,
            device=torch.device('cpu')
        )
        
        assert evaluator.model == sample_model
        assert evaluator.test_loader == sample_dataloader
        assert evaluator.device.type == 'cpu'
        assert evaluator.results == {}
        assert evaluator.predictions == {}
        assert evaluator.targets == {}
    
    def test_evaluator_initialization_with_scalers(
        self, sample_model, sample_dataloader
    ):
        """Test RegressionEvaluator initialization with scalers."""
        mock_scalers = Mock()
        evaluator = RegressionEvaluator(
            model=sample_model,
            test_loader=sample_dataloader,
            scalers=mock_scalers,
            device=torch.device('cpu')
        )
        
        assert evaluator.scalers == mock_scalers
    
    def test_evaluate_single_model_tensor_targets(
        self, sample_model, sample_dataloader
    ):
        """Test evaluate_single_model with tensor targets."""
        # Mock model forward
        sample_model.return_value = torch.tensor(
            [[19.5], [25.2], [29.8], [22.1], [27.9]], dtype=torch.float32
        )
        sample_model.side_effect = None
        sample_model.__call__ = Mock(return_value=torch.tensor(
            [[19.5], [25.2], [29.8], [22.1], [27.9]], dtype=torch.float32
        ))
        
        evaluator = RegressionEvaluator(
            model=sample_model,
            test_loader=sample_dataloader,
            scalers=None,
            device=torch.device('cpu')
        )
        
        metrics = evaluator.evaluate_single_model(target='alto', denormalize=False)
        
        assert 'mae' in metrics
        assert 'mse' in metrics
        assert 'rmse' in metrics
        assert 'r2' in metrics
        assert 'n_samples' in metrics
    
    def test_evaluate_single_model_dict_targets(
        self, sample_model, sample_multi_head_dataloader
    ):
        """Test evaluate_single_model with dictionary targets."""
        # Mock model forward
        sample_model.__call__ = Mock(return_value=torch.tensor(
            [[19.5], [25.2], [29.8], [22.1], [27.9]], dtype=torch.float32
        ))
        
        evaluator = RegressionEvaluator(
            model=sample_model,
            test_loader=sample_multi_head_dataloader,
            scalers=None,
            device=torch.device('cpu')
        )
        
        metrics = evaluator.evaluate_single_model(target='alto', denormalize=False)
        
        assert 'mae' in metrics
        assert 'n_samples' in metrics
    
    def test_evaluate_single_model_with_denormalization(
        self, sample_model, sample_dataloader
    ):
        """Test evaluate_single_model with denormalization."""
        mock_scalers = Mock()
        mock_scalers.inverse_transform = Mock(return_value={
            'alto': np.array([20.0, 25.0, 30.0, 22.0, 28.0], dtype=np.float32)
        })
        
        sample_model.__call__ = Mock(return_value=torch.tensor(
            [[0.1], [0.2], [0.3], [0.15], [0.25]], dtype=torch.float32
        ))
        
        evaluator = RegressionEvaluator(
            model=sample_model,
            test_loader=sample_dataloader,
            scalers=mock_scalers,
            device=torch.device('cpu')
        )
        
        metrics = evaluator.evaluate_single_model(target='alto', denormalize=True)
        
        assert 'mae' in metrics
        mock_scalers.inverse_transform.assert_called()
    
    def test_evaluate_single_model_denormalization_error(
        self, sample_model, sample_dataloader
    ):
        """Test evaluate_single_model handles denormalization errors."""
        mock_scalers = Mock()
        mock_scalers.inverse_transform = Mock(side_effect=Exception("Denorm error"))
        
        sample_model.__call__ = Mock(return_value=torch.tensor(
            [[0.1], [0.2], [0.3], [0.15], [0.25]], dtype=torch.float32
        ))
        
        evaluator = RegressionEvaluator(
            model=sample_model,
            test_loader=sample_dataloader,
            scalers=mock_scalers,
            device=torch.device('cpu')
        )
        
        # Should not raise, but log warning
        metrics = evaluator.evaluate_single_model(target='alto', denormalize=True)
        
        assert 'mae' in metrics
    
    def test_evaluate_multi_head_model(
        self, sample_model, sample_multi_head_dataloader
    ):
        """Test evaluate_multi_head_model."""
        # Mock model forward to return dict
        sample_model.__call__ = Mock(return_value={
            'alto': torch.tensor([[19.5], [25.2], [29.8], [22.1], [27.9]], dtype=torch.float32),
            'ancho': torch.tensor([[11.5], [14.8], [17.9], [12.8], [15.9]], dtype=torch.float32),
            'grosor': torch.tensor([[7.5], [8.8], [9.9], [8.2], [9.4]], dtype=torch.float32),
            'peso': torch.tensor([[1.4], [1.7], [1.9], [1.5], [1.8]], dtype=torch.float32)
        })
        
        evaluator = RegressionEvaluator(
            model=sample_model,
            test_loader=sample_multi_head_dataloader,
            scalers=None,
            device=torch.device('cpu')
        )
        
        results = evaluator.evaluate_multi_head_model(denormalize=False)
        
        assert isinstance(results, dict)
        for target in TARGETS:
            assert target in results
            assert 'mae' in results[target]
            assert 'r2' in results[target]
    
    def test_evaluate_multi_head_model_hybrid(
        self, sample_model, sample_multi_head_dataloader
    ):
        """Test evaluate_multi_head_model with hybrid model."""
        # Mock hybrid model (has pixel_features parameter)
        def hybrid_forward(images, pixel_features=None):
            return {
                'alto': torch.tensor([[19.5], [25.2]], dtype=torch.float32),
                'ancho': torch.tensor([[11.5], [14.8]], dtype=torch.float32),
                'grosor': torch.tensor([[7.5], [8.8]], dtype=torch.float32),
                'peso': torch.tensor([[1.4], [1.7]], dtype=torch.float32)
            }
        
        sample_model.__call__ = Mock(side_effect=hybrid_forward)
        sample_model.__class__.__name__ = "HybridCacaoRegression"
        
        # Create dataloader with pixel features
        images = torch.randn(2, 3, 224, 224)
        targets_dict = {
            'alto': torch.tensor([20.0, 25.0], dtype=torch.float32),
            'ancho': torch.tensor([12.0, 15.0], dtype=torch.float32),
            'grosor': torch.tensor([8.0, 9.0], dtype=torch.float32),
            'peso': torch.tensor([1.5, 1.8], dtype=torch.float32)
        }
        pixel_features = torch.randn(2, 10)
        
        class HybridDataset:
            def __len__(self):
                return 2
            
            def __getitem__(self, idx):
                return images[idx], {k: v[idx] for k, v in targets_dict.items()}, pixel_features[idx]
        
        hybrid_loader = DataLoader(HybridDataset(), batch_size=2, shuffle=False)
        
        evaluator = RegressionEvaluator(
            model=sample_model,
            test_loader=hybrid_loader,
            scalers=None,
            device=torch.device('cpu')
        )
        
        results = evaluator.evaluate_multi_head_model(denormalize=False)
        
        assert isinstance(results, dict)
        for target in TARGETS:
            assert target in results


class TestLoadModelForEvaluation:
    """Tests for load_model_for_evaluation function."""
    
    def test_load_model_success(self, tmp_path, sample_model):
        """Test successful model loading."""
        model_path = tmp_path / "model.pt"
        
        # Create a valid checkpoint
        checkpoint = {
            'model_state_dict': sample_model.state_dict() if hasattr(sample_model, 'state_dict') else {}
        }
        
        with patch('torch.load', return_value=checkpoint):
            with patch('ml.regression.evaluate.create_model', return_value=sample_model):
                loaded_model = load_model_for_evaluation(
                    model_path=model_path,
                    model_class=sample_model.__class__,
                    device=torch.device('cpu')
                )
                
                assert loaded_model is not None
    
    def test_load_model_weights_only_error(self, tmp_path, sample_model):
        """Test model loading when weights_only=True is not supported."""
        model_path = tmp_path / "model.pt"
        
        with patch('torch.load', side_effect=TypeError("weights_only not supported")):
            with pytest.raises(RuntimeError, match="no soporta weights_only=True"):
                load_model_for_evaluation(
                    model_path=model_path,
                    model_class=sample_model.__class__,
                    device=torch.device('cpu')
                )
    
    def test_load_model_invalid_checkpoint(self, tmp_path, sample_model):
        """Test model loading with invalid checkpoint format."""
        model_path = tmp_path / "model.pt"
        
        # Invalid checkpoint (not a dict with model_state_dict)
        invalid_checkpoint = "not a dict"
        
        with patch('torch.load', return_value=invalid_checkpoint):
            with pytest.raises(RuntimeError, match="Unexpected checkpoint format"):
                load_model_for_evaluation(
                    model_path=model_path,
                    model_class=sample_model.__class__,
                    device=torch.device('cpu')
                )


class TestEvaluateModelFromFile:
    """Tests for evaluate_model_from_file function."""
    
    def test_evaluate_model_from_file_single_target(
        self, tmp_path, sample_model, sample_dataloader
    ):
        """Test evaluate_model_from_file with single target."""
        model_path = tmp_path / "model.pt"
        
        with patch('ml.regression.evaluate.load_model_for_evaluation', return_value=sample_model):
            with patch.object(RegressionEvaluator, 'evaluate_single_model', return_value={'mae': 0.5, 'r2': 0.9}):
                results = evaluate_model_from_file(
                    model_path=model_path,
                    model_class=sample_model.__class__,
                    test_loader=sample_dataloader,
                    scalers=None,
                    device=torch.device('cpu'),
                    target='alto'
                )
                
                assert isinstance(results, dict)
                assert 'mae' in results
    
    def test_evaluate_model_from_file_multi_head(
        self, tmp_path, sample_model, sample_multi_head_dataloader
    ):
        """Test evaluate_model_from_file without target (multi-head)."""
        model_path = tmp_path / "model.pt"
        
        with patch('ml.regression.evaluate.load_model_for_evaluation', return_value=sample_model):
            with patch.object(RegressionEvaluator, 'evaluate_multi_head_model', return_value={
                'alto': {'mae': 0.5, 'r2': 0.9},
                'ancho': {'mae': 0.3, 'r2': 0.95}
            }):
                results = evaluate_model_from_file(
                    model_path=model_path,
                    model_class=sample_model.__class__,
                    test_loader=sample_multi_head_dataloader,
                    scalers=None,
                    device=torch.device('cpu'),
                    target=None
                )
                
                assert isinstance(results, dict)

