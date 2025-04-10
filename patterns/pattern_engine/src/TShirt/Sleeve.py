import numpy as np
from patterns.pattern_engine.src.Point import Point
from patterns.pattern_engine.src.TShirt.Base import BaseTShirtCalculations


class BaseSleeveBlock:
    """Base class for sleeve blocks with common construction logic."""

    DEFAULT_CURVE_MAGNITUDE = 3
    SHORT_SLEEVE_LENGTH = 25
    WRIST_EASE = 3.5
    SCYE_DEPTH_EASE = 2.5

    def __init__(self, builder, measurements, ease_fitting=False):
        self.builder = builder
        self.measurements = measurements
        self.ease_fitting = ease_fitting

        self.base_calc = BaseTShirtCalculations(measurements, ease_fitting)
        self.piece_name = "Sleeve"

        # Derived measurements
        self.armhole_length = self._calculate_armhole_length()
        self.half_scye_depth = (measurements["scye_depth"] + self.SCYE_DEPTH_EASE) / 2

    def _calculate_armhole_length(self) -> float:
        """Calculate armhole length between shoulder and underarm points."""
        p11 = self.base_calc.shoulder_point()
        p12 = self.base_calc.underarm_point()
        return np.hypot(p12.x - p11.x, p12.y - p11.y)


    def _create_base_points(self):
        """Create common sleeve block points with accurate geometry."""
        # Origin point
        self.builder.add_point("15", 0, 0)

        # Vertical measurements
        self.builder.add_point("16", 0, self.half_scye_depth)
        sleeve_length = self._sleeve_length()
        self.builder.add_point("17", 0, sleeve_length)

        # CORRECTED: Original diagonal calculation using Pythagorean theorem
        # armhole_length² = diagonal² + (half_scye_depth)²
        # => diagonal = sqrt(armhole_length² - (half_scye_depth)²)
        diagonal = np.sqrt(self.armhole_length ** 2 - self.half_scye_depth ** 2) + 2.5

        # Add critical points
        self.builder.add_point("18", diagonal, self.half_scye_depth)
        self.builder.add_point("19", diagonal, sleeve_length)

        # CORRECTED: Original 1/3 calculation for point 20
        point_18 = self.builder.current_piece.get_point("18")
        self.builder.add_point("20",
                               point_18.x - (point_18.x / self.DEFAULT_CURVE_MAGNITUDE),
                               point_18.y - (self.half_scye_depth / self.DEFAULT_CURVE_MAGNITUDE)
                               )

    def _sleeve_length(self) -> float:
        """Implement in subclasses for type-specific length calculation."""
        raise NotImplementedError

    def _create_sleeve_head_curve(self):
        """Create common sleeve head curve with configurable magnitude."""
        control_offset = self.armhole_length / self.DEFAULT_CURVE_MAGNITUDE
        self.builder.add_bezier_curve("18", "20", -0.75, 0.5)
        self.builder.add_bezier_curve("20", "15", 2, 0.5)

    def _create_sleeve_body(self):
        """Implement in subclasses for sleeve-type specific construction."""
        raise NotImplementedError

    def draft(self):
        """Main drafting template method."""
        self.builder.start_piece(self.piece_name)
        self._create_base_points()
        self._create_sleeve_head_curve()
        self._create_sleeve_body()
        self._add_common_paths()
        self.builder.end_piece()

    def _add_common_paths(self):
        """Add common path elements for all sleeves."""
        self.builder.add_line_path(["21", "17", "15"])
        self.builder.set_seam_allowance(1.0)


class LongSleeveBlock(BaseSleeveBlock):
    """Long sleeve block with tapered wrist."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.piece_name = "Long Sleeve"
        self.wrist_width = self.measurements["close_wrist"] / 2 + self.WRIST_EASE

    def _sleeve_length(self) -> float:
        return self.measurements["sleeve_length"]

    def _create_sleeve_body(self):
        """Create long sleeve specific elements."""
        self.builder.add_point("21", self.wrist_width, self._sleeve_length())
        self.builder.add_bezier_curve("18", "21", 2, 0.5)


class ShortSleeveBlock(BaseSleeveBlock):
    """Short sleeve block with curved hem."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.piece_name = "Short Sleeve"

    def _sleeve_length(self) -> float:
        return self.SHORT_SLEEVE_LENGTH


    def _create_sleeve_body(self):
        """Create short sleeve specific elements."""
        # CORRECTED: Original short sleeve bottom calculation
        sleeve_bottom = np.sqrt((self.armhole_length + 2.5) ** 2 - self.half_scye_depth ** 2) - 4
        self.builder.add_point("21", sleeve_bottom, self._sleeve_length())
        self.builder.add_bezier_curve("18", "21", 0.5, 0.5)