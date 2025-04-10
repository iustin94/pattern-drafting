"""
Short sleeve block implementation with improved support for curved hems.

This module provides an implementation of the short sleeve block that properly
supports creating mirrored hems for curved edges.
"""
from typing import Dict, Any, Optional, List, Tuple
import math

from patterns.pattern_engine.src.PatternBuilder import PatternBuilder
from patterns.pattern_engine.src.tshirt.TShirtBlock import BaseSleeveBlock


class ShortSleeveBlock(BaseSleeveBlock):
    """
    Short sleeve block with curved hem support.

    This implementation creates explicit curve segments that can be properly
    mirrored by the HemFeature.
    """

    SHORT_SLEEVE_LENGTH = 25

    def __init__(
            self,
            builder: PatternBuilder,
            measurements: Dict[str, float],
            ease_fitting: bool = False
    ):
        """
        Initialize a short sleeve block.

        Args:
            builder: The pattern builder instance
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        super().__init__(builder, measurements, "Short Sleeve", ease_fitting)

    def _sleeve_length(self) -> float:
        """
        Calculate short sleeve length.

        Returns:
            Short sleeve length
        """
        return self.SHORT_SLEEVE_LENGTH

    def _create_sleeve_body(self):
        """
        Create short sleeve specific elements with proper curve support.

        This implementation creates an explicit curved bottom edge that can be
        properly mirrored by the HemFeature.
        """
        # Calculate short sleeve bottom width using the armhole dimensions
        sleeve_bottom = math.sqrt((self.armhole_length + 2.5) ** 2 - self.half_scye_depth ** 2) - 4

        # Create point 21 at the sleeve bottom
        self.builder.add_point("21", sleeve_bottom, self._sleeve_length())

        # Get points 18 and 21 for the curved edge
        point_18 = self.builder.current_piece.get_point("18")
        point_21 = self.builder.current_piece.get_point("21")

        # Calculate a good control point position for the curve
        # We'll place it at 40% of the way from point 18 to point 21,
        # and offset it below the direct line
        control_x = point_18.x + (point_21.x - point_18.x) * 0.4
        distance = math.sqrt((point_21.x - point_18.x) ** 2 + (point_21.y - point_18.y) ** 2)

        # Add a control point for the curve with a good offset for a natural sleeve shape
        curve_offset = distance * 0.15  # 15% of the distance for a natural curve
        control_y = point_18.y + (point_21.y - point_18.y) * 0.4 + curve_offset

        self.builder.add_point("18_21_control", control_x, control_y)

        # Create a curve with the explicit control point
        # This approach better supports the hem feature's ability to mirror curves
        self.builder.add_bezier_curve_with_reference("18", "21", "18_21_control", curve_offset)