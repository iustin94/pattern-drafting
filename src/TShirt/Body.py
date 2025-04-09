import math

from src.Point import Point
from src.TShirt.Base import BaseTShirtCalculations


class BaseTShirtBlock:
    """Base class for T-shirt block pieces with common points and construction."""

    def __init__(self, builder, measurements, ease_fitting=False):
        """
        Initialize the base T-shirt block.
        
        Args:
            builder: The pattern builder
            measurements: Dictionary of measurements
            ease_fitting: If True, use the measurements for easier fitting
        """
        self.builder = builder
        self.measurements = measurements
        self.ease_fitting = ease_fitting

        # Extract needed measurements
        self.chest = measurements["chest"]
        self.half_back = measurements["half_back"]
        self.back_neck_to_waist = measurements["back_neck_to_waist"]
        self.scye_depth = measurements["scye_depth"]
        self.neck_size = measurements["neck_size"]
        self.finished_length = measurements["finished_length"]

        # Calculate ease values
        self.scye_depth_ease = 2.5 if ease_fitting else 1
        self.half_back_ease = 2 if ease_fitting else 1
        self.chest_ease = 4 if ease_fitting else 2.5
        
        self.base_calculations = BaseTShirtCalculations(measurements, ease_fitting)

    def add_common_points(self):
        """Add points common to all T-shirt block pieces."""
        # Square down and across from 0
        self.builder.add_point("0", 0, 0)

        # 0–1 Back neck to waist plus 1cm; square across
        self.builder.add_point("1", 0, self.back_neck_to_waist + 1)

        # 0–2 Finished length; square across
        self.builder.add_point("2", 0, self.finished_length)
        self.builder.add_point("13", self.chest / 4 + self.chest_ease, self.finished_length)

        # 0–3 Scye depth plus ease; square across
        self.builder.add_point("3", 0, self.scye_depth + self.scye_depth_ease)
        self.builder.add_point("8", self.half_back + self.half_back_ease, self.scye_depth + self.scye_depth_ease)

        # 0–4 1/2 measurement 0–3; square across
        self.builder.add_point("4", 0, (self.scye_depth + self.scye_depth_ease) / 2)
        self.builder.add_point("9", self.half_back + self.half_back_ease, (self.scye_depth + self.scye_depth_ease) / 2)

        # 0–5 1/4 measurement 0–4; square across
        self.builder.add_point("5", 0, self.base_calculations.get_shoulder_height())

        # Shoulder point and armhole
        self.builder.add_point("10", self.half_back + self.half_back_ease, self.base_calculations.get_shoulder_height())
        self.builder.add_point("11", self.base_calculations.get_shoulder_width(), self.base_calculations.get_shoulder_height())
        self.builder.add_point("12", self.base_calculations.get_underarm_width(), self.base_calculations.get_underarm_height())

        # 6–7 1.5cm; for back neck curve
        self.builder.add_point("7", self.neck_size / 5 - 1, -1.5)

        # Add point 6 and 7 exactly as in the back piece
        # 0–6 1/5 neck size minus 1cm; square up
        self.builder.add_point("6", self.neck_size / 5 - 1, 0)

    def get_shoulder_height(self):
        return (self.scye_depth + self.scye_depth_ease) / 2 / 4

    def add_common_paths(self):
        """Add path segments common to all T-shirt block pieces."""
        # Create armhole curve in two segments
        self.builder.add_bezier_curve("11", "9", 0.25, 0.3)
        self.builder.add_bezier_curve("9", "12", 2.5, 0.7)

        # Shoulder line
        self.builder.add_line_path(["7", "11"])

        # Set seam allowance
        self.builder.set_seam_allowance(1.0)


class BackTShirtBlock(BaseTShirtBlock):
    """Back piece of the T-shirt block."""

    def draft(self):
        """Draft the back piece of the T-shirt block."""
        self.builder.start_piece("Back")

        # Add common points for the block
        self.add_common_points()

        # Create back-specific outline paths
        # Back neck curve
        self.builder.add_bezier_curve("0", "7", 0.75, 0.8)
        
        # Side seam and bottom
        self.builder.add_line_path(["12", "13", "2", "0"])

        # Add common path elements
        self.add_common_paths()

        # End piece
        self.builder.end_piece()


class FrontTShirtBlock(BaseTShirtBlock):
    """Front piece of the T-shirt block."""

    def draft(self):
        """Draft the front piece of the T-shirt block."""
        self.builder.start_piece("Front")

        # Add common points for the block
        self.add_common_points()

        # Add front-specific neck points
        # Point 14 should have the formula applied to the Y coordinate, not X
        # Formula: 1/5 neck size minus 2cm
        # Point 14 should be on the Y-axis (X=0)
        self.builder.add_point("14", 0, self.neck_size / 5 - 2)  # On Y-axis, formula applied to Y

        # Create front-specific outline paths
        # Front neck curve from point 7 to point 14 (using the outward control point)
        self.builder.add_bezier_curve("7", "14", -2.5, 0.5)

        # Side seam and bottom
        self.builder.add_line_path(["12", "13", "2", "14"])
        
        # Add common path elements
        self.add_common_paths()

        # End piece
        self.builder.end_piece()

