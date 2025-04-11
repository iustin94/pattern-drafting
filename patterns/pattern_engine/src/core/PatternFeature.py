"""
Pattern Feature system for adding functionality to patterns.

This module provides a framework for creating and applying features like hems,
pockets, collars, etc. to pattern blocks using a composition approach.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type

from patterns.pattern_engine.src.core.PatternBuilder import PatternBuilder
from patterns.pattern_engine.src.core.Pattern import Pattern


class PatternFeature(ABC):
    """
    Base class for pattern features that can be applied to pattern blocks.

    Pattern features use the Decorator pattern to add functionality to existing
    pattern blocks without modifying their core implementation.
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """
        Initialize the pattern features.

        Args:
            options: Optional configuration for the features
        """
        self.options = options or {}

    @abstractmethod
    def apply(self, builder: PatternBuilder, pattern: Pattern) -> None:
        """
        Apply this features to a pattern.

        Args:
            builder: The PatternBuilder instance
            pattern: The pattern to modify
        """
        pass


class PatternFeatureRegistry:
    """
    Registry for available pattern features.

    This class maintains a global registry of features types that can be
    looked up by name.
    """

    _features: Dict[str, Type[PatternFeature]] = {}

    @classmethod
    def register(cls, feature_name: str, feature_class: Type[PatternFeature]) -> None:
        """
        Register a pattern features.

        Args:
            feature_name: Name to register the features under
            feature_class: The features class to register
        """
        cls._features[feature_name] = feature_class

    @classmethod
    def get(cls, feature_name: str) -> Type[PatternFeature]:
        """
        Get a features class by name.

        Args:
            feature_name: Name of the features to retrieve

        Returns:
            The features class

        Raises:
            ValueError: If the features name is not registered
        """
        if feature_name not in cls._features:
            raise ValueError(f"Unknown pattern features: {feature_name}")
        return cls._features[feature_name]