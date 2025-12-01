"""
Unit tests for regression augmentation module (augmentation.py).
Tests data augmentation techniques: MixUp, CutMix, RandomErasing, and transforms.
"""
import pytest
import torch
import numpy as np
from PIL import Image
from pathlib import Path
from unittest.mock import patch, MagicMock

from ml.regression.augmentation import (
    MixUp,
    CutMix,
    RandomErasing,
    create_advanced_train_transform,
    create_advanced_val_transform,
    AugmentedDataset
)


@pytest.fixture
def sample_images():
    """Create sample image tensors for testing."""
    return torch.randn(4, 3, 224, 224)


@pytest.fixture
def sample_targets():
    """Create sample target tensors for testing."""
    return torch.tensor([20.0, 25.0, 30.0, 22.0], dtype=torch.float32)


@pytest.fixture
def sample_image_tensor():
    """Create a single image tensor for testing."""
    return torch.randn(3, 224, 224)


class TestMixUp:
    """Tests for MixUp augmentation."""
    
    def test_mixup_initialization(self):
        """Test MixUp initialization."""
        mixup = MixUp(alpha=0.4)
        assert mixup.alpha == 0.4
    
    def test_mixup_initialization_default(self):
        """Test MixUp initialization with default alpha."""
        mixup = MixUp()
        assert mixup.alpha == 0.4
    
    def test_mixup_call_no_augmentation(self, sample_images, sample_targets):
        """Test MixUp when random value > 0.5 (no augmentation)."""
        mixup = MixUp(alpha=0.4)
        
        with patch('torch.rand', return_value=torch.tensor([0.6])):
            mixed_images, mixed_targets = mixup(sample_images, sample_targets)
            
            assert torch.equal(mixed_images, sample_images)
            assert torch.equal(mixed_targets, sample_targets)
    
    def test_mixup_call_with_augmentation(self, sample_images, sample_targets):
        """Test MixUp when random value <= 0.5 (with augmentation)."""
        mixup = MixUp(alpha=0.4)
        
        with patch('torch.rand', return_value=torch.tensor([0.3])):
            mixed_images, mixed_targets = mixup(sample_images, sample_targets)
            
            assert mixed_images.shape == sample_images.shape
            assert mixed_targets.shape == sample_targets.shape
            assert not torch.equal(mixed_images, sample_images)
            assert not torch.equal(mixed_targets, sample_targets)
    
    def test_mixup_preserves_shape(self, sample_images, sample_targets):
        """Test that MixUp preserves tensor shapes."""
        mixup = MixUp(alpha=0.4)
        
        with patch('torch.rand', return_value=torch.tensor([0.3])):
            mixed_images, mixed_targets = mixup(sample_images, sample_targets)
            
            assert mixed_images.shape == sample_images.shape
            assert mixed_targets.shape == sample_targets.shape
    
    def test_mixup_different_alpha(self, sample_images, sample_targets):
        """Test MixUp with different alpha values."""
        for alpha in [0.2, 0.4, 0.6, 1.0]:
            mixup = MixUp(alpha=alpha)
            assert mixup.alpha == alpha


class TestCutMix:
    """Tests for CutMix augmentation."""
    
    def test_cutmix_initialization(self):
        """Test CutMix initialization."""
        cutmix = CutMix(alpha=1.0)
        assert cutmix.alpha == 1.0
    
    def test_cutmix_initialization_default(self):
        """Test CutMix initialization with default alpha."""
        cutmix = CutMix()
        assert cutmix.alpha == 1.0
    
    def test_cutmix_call_no_augmentation(self, sample_images, sample_targets):
        """Test CutMix when random value > 0.5 (no augmentation)."""
        cutmix = CutMix(alpha=1.0)
        
        with patch('torch.rand', return_value=torch.tensor([0.6])):
            mixed_images, mixed_targets = cutmix(sample_images, sample_targets)
            
            assert torch.equal(mixed_images, sample_images)
            assert torch.equal(mixed_targets, sample_targets)
    
    def test_cutmix_call_with_augmentation(self, sample_images, sample_targets):
        """Test CutMix when random value <= 0.5 (with augmentation)."""
        cutmix = CutMix(alpha=1.0)
        
        with patch('torch.rand', return_value=torch.tensor([0.3])):
            mixed_images, mixed_targets = cutmix(sample_images, sample_targets)
            
            assert mixed_images.shape == sample_images.shape
            assert mixed_targets.shape == sample_targets.shape
    
    def test_cutmix_preserves_shape(self, sample_images, sample_targets):
        """Test that CutMix preserves tensor shapes."""
        cutmix = CutMix(alpha=1.0)
        
        with patch('torch.rand', return_value=torch.tensor([0.3])):
            mixed_images, mixed_targets = cutmix(sample_images, sample_targets)
            
            assert mixed_images.shape == sample_images.shape
            assert mixed_targets.shape == sample_targets.shape
    
    def test_cutmix_different_image_sizes(self):
        """Test CutMix with different image sizes."""
        cutmix = CutMix(alpha=1.0)
        
        for h, w in [(224, 224), (256, 256), (128, 128)]:
            images = torch.randn(2, 3, h, w)
            targets = torch.tensor([20.0, 25.0], dtype=torch.float32)
            
            with patch('torch.rand', return_value=torch.tensor([0.3])):
                mixed_images, mixed_targets = cutmix(images, targets)
                
                assert mixed_images.shape == images.shape
                assert mixed_targets.shape == targets.shape


class TestRandomErasing:
    """Tests for RandomErasing augmentation."""
    
    def test_random_erasing_initialization(self):
        """Test RandomErasing initialization."""
        re = RandomErasing(probability=0.5, sl=0.02, sh=0.4, r1=0.3)
        assert re.probability == 0.5
        assert re.sl == 0.02
        assert re.sh == 0.4
        assert re.r1 == 0.3
    
    def test_random_erasing_initialization_default(self):
        """Test RandomErasing initialization with defaults."""
        re = RandomErasing()
        assert re.probability == 0.5
        assert re.sl == 0.02
        assert re.sh == 0.4
        assert re.r1 == 0.3
    
    def test_random_erasing_call_no_erasing(self, sample_image_tensor):
        """Test RandomErasing when random value > probability."""
        re = RandomErasing(probability=0.5)
        
        with patch('torch.rand', return_value=torch.tensor([0.6])):
            result = re(sample_image_tensor)
            assert torch.equal(result, sample_image_tensor)
    
    def test_random_erasing_call_with_erasing(self, sample_image_tensor):
        """Test RandomErasing when random value <= probability."""
        re = RandomErasing(probability=0.5)
        
        with patch('torch.rand', return_value=torch.tensor([0.3])):
            result = re(sample_image_tensor)
            
            assert result.shape == sample_image_tensor.shape
            assert result.dtype == sample_image_tensor.dtype
    
    def test_random_erasing_preserves_shape(self, sample_image_tensor):
        """Test that RandomErasing preserves tensor shape."""
        re = RandomErasing(probability=1.0)  # Always apply
        
        result = re(sample_image_tensor)
        
        assert result.shape == sample_image_tensor.shape
    
    def test_random_erasing_different_sizes(self):
        """Test RandomErasing with different image sizes."""
        re = RandomErasing(probability=1.0)
        
        for h, w in [(224, 224), (256, 256), (128, 128)]:
            image = torch.randn(3, h, w)
            result = re(image)
            
            assert result.shape == image.shape
    
    def test_random_erasing_probability_zero(self, sample_image_tensor):
        """Test RandomErasing with probability=0 (never erase)."""
        re = RandomErasing(probability=0.0)
        result = re(sample_image_tensor)
        
        assert torch.equal(result, sample_image_tensor)
    
    def test_random_erasing_probability_one(self, sample_image_tensor):
        """Test RandomErasing with probability=1.0 (always erase)."""
        re = RandomErasing(probability=1.0)
        result = re(sample_image_tensor)
        
        assert result.shape == sample_image_tensor.shape
        assert not torch.equal(result, sample_image_tensor)


class TestTransforms:
    """Tests for transform creation functions."""
    
    def test_create_advanced_train_transform(self):
        """Test creation of advanced training transforms."""
        transform = create_advanced_train_transform(img_size=224)
        
        assert transform is not None
        assert hasattr(transform, 'transforms')
        
        # Test that transform can be applied
        image = Image.new('RGB', (256, 256), color='red')
        result = transform(image)
        
        assert isinstance(result, torch.Tensor)
        assert result.shape == (3, 224, 224)
    
    def test_create_advanced_train_transform_different_size(self):
        """Test creation of training transforms with different size."""
        for img_size in [224, 256, 128]:
            transform = create_advanced_train_transform(img_size=img_size)
            
            image = Image.new('RGB', (300, 300), color='red')
            result = transform(image)
            
            assert result.shape == (3, img_size, img_size)
    
    def test_create_advanced_val_transform(self):
        """Test creation of advanced validation transforms."""
        transform = create_advanced_val_transform(img_size=224)
        
        assert transform is not None
        assert hasattr(transform, 'transforms')
        
        # Test that transform can be applied
        image = Image.new('RGB', (256, 256), color='red')
        result = transform(image)
        
        assert isinstance(result, torch.Tensor)
        assert result.shape == (3, 224, 224)
    
    def test_create_advanced_val_transform_different_size(self):
        """Test creation of validation transforms with different size."""
        for img_size in [224, 256, 128]:
            transform = create_advanced_val_transform(img_size=img_size)
            
            image = Image.new('RGB', (300, 300), color='red')
            result = transform(image)
            
            assert result.shape == (3, img_size, img_size)
    
    def test_train_transform_includes_normalization(self):
        """Test that training transform includes ImageNet normalization."""
        transform = create_advanced_train_transform(img_size=224)
        
        # Check that Normalize is in the transforms
        transform_names = [type(t).__name__ for t in transform.transforms]
        assert 'Normalize' in transform_names
    
    def test_val_transform_includes_normalization(self):
        """Test that validation transform includes ImageNet normalization."""
        transform = create_advanced_val_transform(img_size=224)
        
        # Check that Normalize is in the transforms
        transform_names = [type(t).__name__ for t in transform.transforms]
        assert 'Normalize' in transform_names


class TestAugmentedDataset:
    """Tests for AugmentedDataset class."""
    
    @pytest.fixture
    def sample_image_paths(self, tmp_path):
        """Create sample image paths for testing."""
        image_paths = []
        for i in range(5):
            img_path = tmp_path / f"image_{i}.png"
            img = Image.new('RGB', (224, 224), color=(i*50, i*50, i*50))
            img.save(img_path)
            image_paths.append(img_path)
        return image_paths
    
    @pytest.fixture
    def sample_targets_dict(self):
        """Create sample targets dictionary."""
        return {
            'alto': [20.0, 25.0, 30.0, 22.0, 28.0],
            'ancho': [12.0, 15.0, 18.0, 13.0, 16.0],
            'grosor': [8.0, 9.0, 10.0, 8.5, 9.5],
            'peso': [1.5, 1.8, 2.0, 1.6, 1.9]
        }
    
    def test_augmented_dataset_initialization(
        self, sample_image_paths, sample_targets_dict
    ):
        """Test AugmentedDataset initialization."""
        # Note: The class has a bug - it references self.target_name which doesn't exist
        # This test documents the current behavior
        dataset = AugmentedDataset(
            image_paths=sample_image_paths,
            targets=sample_targets_dict,
            transform=None,
            use_mixup=False,
            use_cutmix=False
        )
        
        assert len(dataset) == len(sample_image_paths)
        assert dataset.image_paths == sample_image_paths
        assert dataset.targets == sample_targets_dict
    
    def test_augmented_dataset_with_mixup(
        self, sample_image_paths, sample_targets_dict
    ):
        """Test AugmentedDataset with MixUp enabled."""
        dataset = AugmentedDataset(
            image_paths=sample_image_paths,
            targets=sample_targets_dict,
            transform=None,
            use_mixup=True,
            use_cutmix=False,
            mixup_alpha=0.4
        )
        
        assert dataset.use_mixup is True
        assert dataset.mixup is not None
        assert isinstance(dataset.mixup, MixUp)
    
    def test_augmented_dataset_with_cutmix(
        self, sample_image_paths, sample_targets_dict
    ):
        """Test AugmentedDataset with CutMix enabled."""
        dataset = AugmentedDataset(
            image_paths=sample_image_paths,
            targets=sample_targets_dict,
            transform=None,
            use_mixup=False,
            use_cutmix=True,
            cutmix_alpha=1.0
        )
        
        assert dataset.use_cutmix is True
        assert dataset.cutmix is not None
        assert isinstance(dataset.cutmix, CutMix)
    
    def test_augmented_dataset_with_both(
        self, sample_image_paths, sample_targets_dict
    ):
        """Test AugmentedDataset with both MixUp and CutMix enabled."""
        dataset = AugmentedDataset(
            image_paths=sample_image_paths,
            targets=sample_targets_dict,
            transform=None,
            use_mixup=True,
            use_cutmix=True,
            mixup_alpha=0.4,
            cutmix_alpha=1.0
        )
        
        assert dataset.use_mixup is True
        assert dataset.use_cutmix is True
        assert dataset.mixup is not None
        assert dataset.cutmix is not None

