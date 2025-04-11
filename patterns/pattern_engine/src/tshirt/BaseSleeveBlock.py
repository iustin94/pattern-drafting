from typing import Dict

from patterns.pattern_engine.src.core.PatternBuilder import PatternBuilder
from patterns.pattern_engine.src.core.PatternBlock import PatternBlock
from patterns.pattern_engine.src.tshirt.TShirtMeasurements import TShirtMeasurements


class BaseSleeveBlock(PatternBlock):
    """Base class for sleeve blocks with common calculations."""

    DEFAULT_CURVE_MAGNITUDE = 3
    SCYE_DEPTH_EASE = 2.5

    def __init__(
            self,
            builder: PatternBuilder,
            measurements: Dict[str, float],
            piece_name: str,
            ease_fitting: bool = False
    ):
        """
        Initialize a sleeve block.

        Args:
            builder: The pattern builder instance
            measurements: Raw measurements dictionary
            piece_name: Name of the pattern piece
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        # Create measurement system before calling parent __init__
        # Then initialize the parent class
        super().__init__(builder, measurements, piece_name, ease_fitting)
        self.measurements_system = TShirtMeasurements(measurements, ease_fitting)


    def init_calculations(self):
        """Initialize calculated values for sleeve drafting."""
        self.scye_depth_with_ease = self.measurements_system.get_scye_depth_with_ease()
        self.half_scye_depth = self.scye_depth_with_ease / 2

        # Calculate armhole length between shoulder and underarm points
        shoulder_point = self.measurements_system.shoulder_point()
        underarm_point = self.measurements_system.underarm_point()

        dx = underarm_point.x - shoulder_point.x
        dy = underarm_point.y - shoulder_point.y
        self.armhole_length = (dx*dx + dy*dy) ** 0.5

    def _create_base_points(self):
        """Create common sleeve block points with accurate geometry."""
        # Origin point
        self.builder.add_point("15", 0, 0)

        # Vertical measurements
        self.builder.add_point("16", 0, self.half_scye_depth)

        sleeve_length = self._sleeve_length()
        self.builder.add_point("17", 0, sleeve_length)

        # Calculate diagonal using Pythagorean theorem
        # armhole_length² = diagonal² + (half_scye_depth)²
        diagonal = (self.armhole_length ** 2 - self.half_scye_depth ** 2) ** 0.5 + 2.5

        # Add critical points
        self.builder.add_point("18", diagonal, self.half_scye_depth)
        self.builder.add_point("19", diagonal, sleeve_length)

        # Calculate control point for sleeve head
        point_18 = self.builder.current_piece.get_point("18")
        self.builder.add_point(
            "20",
            point_18.x - (point_18.x / self.DEFAULT_CURVE_MAGNITUDE),
            point_18.y - (self.half_scye_depth / self.DEFAULT_CURVE_MAGNITUDE)
        )

    def _sleeve_length(self) -> float:
        """
        Calculate the sleeve length.

        Must be implemented by subclasses.

        Returns:
            Sleeve length
        """
        raise NotImplementedError("Subclasses must implement _sleeve_length()")

    def _create_sleeve_head_curve(self):
        """Create common sleeve head curve with configurable magnitude."""
        self.builder.add_bezier_curve("18", "20", -0.75, 0.5)
        self.builder.add_bezier_curve("20", "15", 2, 0.5)

    def _create_sleeve_body(self):
        """
        Create the sleeve body.

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _create_sleeve_body()")

    def _add_common_paths(self):
        """Add common path elements for all sleeves."""
        self.builder.set_seam_allowance(1.0)
        self.builder.add_line_path(["21", "17", "15"])

    def draft(self):
        """Draft the sleeve piece."""
        # Initialize calculations before drafting
        self.init_calculations()

        self.start_piece()
        self._create_base_points()
        self._create_sleeve_head_curve()
        self._create_sleeve_body()
        self._add_common_paths()
        self.end_piece()
