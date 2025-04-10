"""
Pattern Drafter with features support for pattern drafting.

This module provides an enhanced pattern drafter that supports applying features
to patterns during the drafting process.
"""
from typing import Dict, List, Any, Optional, Type, Union
from abc import ABC, abstractmethod

from patterns.pattern_engine.src.PatternBuilder import PatternBuilder
from patterns.pattern_engine.src.Pattern import Pattern
from patterns.pattern_engine.src.core.PatternFeature import PatternFeature, PatternFeatureRegistry


class PatternDrafter(ABC):
    """
    Enhanced pattern drafter with features support.

    This class extends the basic pattern drafter with the ability to apply
    features to patterns during the drafting process.
    """

    def __init__(
            self,
            measurements: Optional[Dict[str, float]] = None,
            features: Optional[List[PatternFeature]] = None
    ):
        """
        Initialize the pattern drafter.

        Args:
            measurements: Raw measurements dictionary
            features: List of features to apply to the pattern
        """
        self.measurements = measurements or {}
        self.features = features or []

    def add_feature(
            self,
            feature_type: Union[str, Type[PatternFeature]],
            **options
    ) -> 'PatternDrafter':
        """
        Add a features to this pattern drafter.

        Args:
            feature_type: Name of the features or features class
            **options: Options for the features

        Returns:
            Self for method chaining
        """
        if isinstance(feature_type, str):
            feature_class = PatternFeatureRegistry.get(feature_type)
            feature = feature_class(**options)
        else:
            feature = feature_type(**options)

        self.features.append(feature)
        return self

    def draft(self) -> Pattern:
        """
        Draft the pattern with all features applied.

        Returns:
            The complete pattern
        """
        # Create the base pattern
        pattern = self._create_base_pattern()

        # Apply each features
        builder = self.create_pattern(pattern.name)
        builder.pattern = pattern  # Use the existing pattern

        for feature in self.features:
            feature.apply(builder, pattern)

        return pattern

    @abstractmethod
    def _create_base_pattern(self) -> Pattern:
        """
        Create the base pattern before applying features.

        Returns:
            The base pattern

        Raises:
            NotImplementedError: If not implemented by subclasses
        """
        pass

    def create_pattern(self, name: str) -> PatternBuilder:
        """
        Create a new pattern builder with the current measurements.

        Args:
            name: Name for the pattern

        Returns:
            Configured PatternBuilder instance
        """
        builder = PatternBuilder(name)
        for name, value in self.measurements.items():
            builder.pattern.set_measurement(name, value)
        return builder