"""
Pant pattern drafter using the refactored pattern system.

This module provides an implementation of the PatternDrafter for pants
with support for features.
"""
from typing import Dict, List, Optional

from patterns.pattern_engine.src.core.PatternDrafter import PatternDrafter
from patterns.pattern_engine.src.core.Pattern import Pattern
from patterns.pattern_engine.src.pant.PantBlock import FrontPantBlock, BackPantBlock


class PantDrafter(PatternDrafter):
    """
    Pant pattern drafter with feature support.

    This class drafts complete pant patterns with options for ease fitting
    plus support for additional features.
    """

    def __init__(
            self,
            measurements: Optional[Dict[str, float]] = None,
            ease_fitting: bool = False,
            features: Optional[List] = None
    ):
        """
        Initialize the pant drafter.

        Args:
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
            features: List of features to apply
        """
        super().__init__(measurements, features)
        self.ease_fitting = ease_fitting

        # Validate measurements
        if not measurements:
            raise ValueError("No measurements provided")

    def _create_base_pattern(self) -> Pattern:
        """
        Create the base pant pattern before applying features.

        Returns:
            The base pant pattern
        """
        # Create pattern name
        pattern_type = "Easy Fitting" if self.ease_fitting else "Standard Fit"
        pattern_name = f"{pattern_type} Pants"

        # Create builder
        builder = self.create_pattern(pattern_name)

        # Create and draft the front piece
        front_block = FrontPantBlock(builder, self.measurements, self.ease_fitting)
        front_block.draft()

        # Create and draft the back piece
        back_block = BackPantBlock(builder, self.measurements, self.ease_fitting)
        back_block.draft()

        return builder.build()