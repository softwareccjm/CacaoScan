"""
Factory pattern for creating regression models.

This module implements the Factory Method pattern to create different types
of regression models, improving code organization and extensibility.
"""
from abc import ABC, abstractmethod
from typing import Optional
import torch.nn as nn

from ...utils.logs import get_ml_logger
from .interfaces import ICreadorModelo

logger = get_ml_logger("cacaoscan.ml.regression.factories")


class CreadorModeloBase(ABC, ICreadorModelo):
    """
    Abstract base class for model creators.
    
    Each concrete creator handles the creation of a specific model type.
    This follows the Factory Method pattern and Open/Closed Principle.
    """
    
    @abstractmethod
    def create(
        self,
        model_type: str,
        num_outputs: int,
        pretrained: bool,
        dropout_rate: float,
        pixel_feature_dim: Optional[int],
        use_pixel_features: bool
    ) -> nn.Module:
        """
        Create a model instance.
        
        Args:
            model_type: Type of model backbone
            num_outputs: Number of output values
            pretrained: Whether to use pretrained weights
            dropout_rate: Dropout rate
            pixel_feature_dim: Dimension of pixel features (for hybrid models)
            use_pixel_features: Whether to use pixel features
            
        Returns:
            Created model instance
        """
        pass


class CreadorModeloHibrido(CreadorModeloBase):
    """Creator for hybrid models (ResNet18 + ConvNeXt + Pixel features)."""
    
    def create(
        self,
        model_type: str,
        num_outputs: int,
        pretrained: bool,
        dropout_rate: float,
        pixel_feature_dim: Optional[int],
        use_pixel_features: bool
    ) -> nn.Module:
        """Create a hybrid model."""
        from ..models import _create_hybrid_model
        
        logger.info("Creating hybrid model via CreadorModeloHibrido")
        return _create_hybrid_model(
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            pixel_feature_dim=pixel_feature_dim,
            use_pixel_features=use_pixel_features
        )


class CreadorModeloMultiHead(CreadorModeloBase):
    """Creator for multi-head models."""
    
    def create(
        self,
        model_type: str,
        num_outputs: int,
        pretrained: bool,
        dropout_rate: float,
        pixel_feature_dim: Optional[int],
        use_pixel_features: bool
    ) -> nn.Module:
        """Create a multi-head model."""
        from ..models import _create_multi_head_model
        
        logger.info("Creating multi-head model via MultiHeadModelCreator")
        return _create_multi_head_model(
            model_type=model_type,
            pretrained=pretrained,
            dropout_rate=dropout_rate
        )


class OptimizedModelCreator(ModelCreator):
    """Creator for optimized models."""
    
    def create(
        self,
        model_type: str,
        num_outputs: int,
        pretrained: bool,
        dropout_rate: float,
        pixel_feature_dim: Optional[int],
        use_pixel_features: bool
    ) -> Optional[nn.Module]:
        """Create an optimized model if available."""
        from ..models import _create_optimized_model
        
        logger.info("Creating optimized model via OptimizedModelCreator")
        return _create_optimized_model(
            model_type=model_type,
            num_outputs=num_outputs,
            pretrained=pretrained,
            dropout_rate=dropout_rate
        )


class StandardModelCreator(ModelCreator):
    """Creator for standard models (ResNet18, ConvNeXt, etc.)."""
    
    def create(
        self,
        model_type: str,
        num_outputs: int,
        pretrained: bool,
        dropout_rate: float,
        pixel_feature_dim: Optional[int],
        use_pixel_features: bool
    ) -> nn.Module:
        """Create a standard model."""
        from ..models import _create_standard_model
        
        logger.info("Creating standard model via StandardModelCreator")
        return _create_standard_model(
            model_type=model_type,
            num_outputs=num_outputs,
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            pixel_feature_dim=pixel_feature_dim,
            use_pixel_features=use_pixel_features
        )


class ModelFactory:
    """
    Factory for creating regression models.
    
    This factory uses the Strategy pattern to delegate model creation
    to specific creators based on the model configuration.
    """
    
    def __init__(self):
        """Initialize the factory with model creators."""
        self._hybrid_creator = HybridModelCreator()
        self._multi_head_creator = MultiHeadModelCreator()
        self._optimized_creator = OptimizedModelCreator()
        self._standard_creator = StandardModelCreator()
    
    def create_model(
        self,
        model_type: str = "resnet18",
        num_outputs: int = 1,
        pretrained: bool = True,
        dropout_rate: float = 0.3,
        multi_head: bool = False,
        hybrid: bool = False,
        use_pixel_features: bool = True,
        pixel_feature_dim: Optional[int] = None,
        use_optimized: bool = True
    ) -> nn.Module:
        """
        Create a regression model based on configuration.
        
        Args:
            model_type: Type of model backbone ("resnet18", "convnext_tiny", etc.)
            num_outputs: Number of output values (ignored if multi_head=True or hybrid=True)
            pretrained: Whether to use pretrained weights
            dropout_rate: Dropout rate
            multi_head: Whether to create a multi-head model
            hybrid: Whether to create a hybrid model
            use_pixel_features: Whether to use pixel features (only if hybrid=True)
            pixel_feature_dim: Dimension of pixel features
            use_optimized: Whether to try optimized models first
            
        Returns:
            Created model instance
        """
        # Priority 1: Hybrid models
        if hybrid:
            return self._hybrid_creator.create(
                model_type=model_type,
                num_outputs=num_outputs,
                pretrained=pretrained,
                dropout_rate=dropout_rate,
                pixel_feature_dim=pixel_feature_dim,
                use_pixel_features=use_pixel_features
            )
        
        # Priority 2: Multi-head models
        if multi_head:
            return self._multi_head_creator.create(
                model_type=model_type,
                num_outputs=num_outputs,
                pretrained=pretrained,
                dropout_rate=dropout_rate,
                pixel_feature_dim=pixel_feature_dim,
                use_pixel_features=use_pixel_features
            )
        
        # Priority 3: Optimized models (if enabled)
        if use_optimized:
            optimized_model = self._optimized_creator.create(
                model_type=model_type,
                num_outputs=num_outputs,
                pretrained=pretrained,
                dropout_rate=dropout_rate,
                pixel_feature_dim=pixel_feature_dim,
                use_pixel_features=use_pixel_features
            )
            if optimized_model is not None:
                return optimized_model
        
        # Priority 4: Standard models
        logger.info(f"Creating individual model (Backbone: {model_type}, Outputs: {num_outputs})")
        return self._standard_creator.create(
            model_type=model_type,
            num_outputs=num_outputs,
            pretrained=pretrained,
            dropout_rate=dropout_rate,
            pixel_feature_dim=pixel_feature_dim,
            use_pixel_features=use_pixel_features
        )


# Singleton instance
_factory_instance: Optional[ModelFactory] = None


def get_factory() -> ModelFactory:
    """Get the singleton factory instance."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = ModelFactory()
    return _factory_instance


def create_model(
    model_type: str = "resnet18",
    num_outputs: int = 1,
    pretrained: bool = True,
    dropout_rate: float = 0.3,
    multi_head: bool = False,
    hybrid: bool = False,
    use_pixel_features: bool = True,
    pixel_feature_dim: Optional[int] = None,
    use_optimized: bool = True
) -> nn.Module:
    """
    Convenience function to create a model using the factory.
    
    This function maintains backward compatibility with the original
    create_model function signature.
    
    Args:
        model_type: Type of model backbone
        num_outputs: Number of output values
        pretrained: Whether to use pretrained weights
        dropout_rate: Dropout rate
        multi_head: Whether to create a multi-head model
        hybrid: Whether to create a hybrid model
        use_pixel_features: Whether to use pixel features
        pixel_feature_dim: Dimension of pixel features
        use_optimized: Whether to try optimized models first
        
    Returns:
        Created model instance
    """
    factory = get_factory()
    return factory.create_model(
        model_type=model_type,
        num_outputs=num_outputs,
        pretrained=pretrained,
        dropout_rate=dropout_rate,
        multi_head=multi_head,
        hybrid=hybrid,
        use_pixel_features=use_pixel_features,
        pixel_feature_dim=pixel_feature_dim,
        use_optimized=use_optimized
    )

