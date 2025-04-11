"""
T-Shirt pattern blocks implementation using the refactored pattern system.

This module provides implementations of T-shirt pattern blocks including
front, back, and sleeve pieces with a clean object-oriented approach.
"""

from patterns.pattern_engine.src.core.PatternBlock import PatternBlock


class BaseTShirtBlock(PatternBlock):
    """Base class for T-shirt blocks with shared point definitions."""

    def add_core_points(self):
        """Add essential construction points shared by all pieces."""
        # Vertical construction points
        self.builder.add_point("0", 0, 0)  # Origin
        self.builder.add_point("1", 0, self.measurements.get("back_neck_to_waist") + 1)
        self.builder.add_point("2", 0, self.measurements.get("finished_length"))
        self.builder.add_point("3", 0, self.measurements.with_ease("scye_depth"))

        # Horizontal construction points
        self.builder.add_point("8", self.measurements.with_ease("half_back"), self.measurements.with_ease("scye_depth"))
        self.builder.add_point("9", self.measurements.with_ease("half_back"), self.measurements.with_ease("scye_depth") / 2)
        self.builder.add_point("11", self.measurements.get("shoulder_width"), self.measurements.get("shoulder_height"))


