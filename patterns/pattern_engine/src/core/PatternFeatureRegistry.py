"""
Pattern Feature registry for managing pattern features.

This module provides a registry for pattern features that can be applied
to patterns during the drafting process.
"""
from typing import Dict, Type, Any


class PatternFeatureRegistry:
    """
    Registry for available pattern features.

    This class maintains a global registry of feature types that can be
    looked up by name.
    """

    _features: Dict[str, Any] = {}

    @classmethod
    def register(cls, feature_name: str, feature_class: Any) -> None:
        """
        Register a pattern feature.

        Args:
            feature_name: Name to register the feature under
            feature_class: The feature class to register
        """
        cls._features[feature_name] = feature_class

    @classmethod
    def get(cls, feature_name: str) -> Any:
        """
        Get a feature class by name.

        Args:
            feature_name: Name of the feature to retrieve

        Returns:
            The feature class

        Raises:
            ValueError: If the feature name is not registered
        """
        if feature_name not in cls._features:
            raise ValueError(f"Unknown pattern feature: {feature_name}")
        return cls._features[feature_name]

    @classmethod
    def list_features(cls) -> Dict[str, Any]:
        """
        Get a dictionary of all registered features.

        Returns:
            Dictionary mapping feature names to feature classes
        """
        return cls._features.copy()


# Import and register features
from ..features.HemFeature import HemFeature

PatternFeatureRegistry.register("hem", HemFeature)