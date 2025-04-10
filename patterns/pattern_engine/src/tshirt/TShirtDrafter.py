"""
T-Shirt pattern drafter using the refactored pattern system.

This module provides an implementation of the PatternDrafter for T-shirts
with support for features and different sleeve options.
"""
from typing import Dict, List, Any, Optional

from patterns.pattern_engine.src.core.PatternDrafter import PatternDrafter
from patterns.pattern_engine.src.Pattern import Pattern
from patterns.pattern_engine.src.tshirt.TShirtBlock import (
    FrontTShirtBlock, BackTShirtBlock, LongSleeveBlock
)
from patterns.pattern_engine.src.tshirt.ShortSleeveBlock import ShortSleeveBlock


class TShirtDrafter(PatternDrafter):
    """
    T-shirt pattern drafter with feature support.

    This class drafts complete T-shirt patterns with options for ease fitting
    and sleeve length, plus support for additional features.
    """

    def __init__(
            self,
            measurements: Optional[Dict[str, float]] = None,
            ease_fitting: bool = False,
            short_sleeve: bool = False,
            features: Optional[List] = None
    ):
        """
        Initialize the T-shirt drafter.

        Args:
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
            short_sleeve: Whether to create a short sleeve version
            features: List of features to apply
        """
        super().__init__(measurements, features)
        self.ease_fitting = ease_fitting
        self.short_sleeve = short_sleeve

        # Validate measurements
        if not measurements:
            raise ValueError("No measurements provided")

    def _create_base_pattern(self) -> Pattern:
        """
        Create the base T-shirt pattern before applying features.

        Returns:
            The base T-shirt pattern
        """
        # Create pattern name
        pattern_type = "Easy Fitting" if self.ease_fitting else "Close Fitting"
        sleeve_type = "Short Sleeve" if self.short_sleeve else "Long Sleeve"
        pattern_name = f"{pattern_type} T-Shirt ({sleeve_type})"

        # Create builder
        builder = self.create_pattern(pattern_name)

        # Create and draft the front piece
        front_block = FrontTShirtBlock(builder, self.measurements, self.ease_fitting)
        front_block.draft()

        # Create and draft the back piece
        back_block = BackTShirtBlock(builder, self.measurements, self.ease_fitting)
        back_block.draft()

        # Create and draft the appropriate sleeve piece
        if self.short_sleeve:
            sleeve_block = ShortSleeveBlock(builder, self.measurements, self.ease_fitting)
        else:
            sleeve_block = LongSleeveBlock(builder, self.measurements, self.ease_fitting)

        sleeve_block.draft()

        return builder.build()