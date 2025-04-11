"""
Pant pattern blocks implementation using the refactored pattern system.

This module provides implementations of pant pattern blocks including
front and back pieces with a clean object-oriented approach.
"""
from typing import Dict

from patterns.pattern_engine.src.core.PatternBlock import PatternBlock
from patterns.pattern_engine.src.core.PatternBuilder import PatternBuilder
from patterns.pattern_engine.src.pant.PantMeasurements import PantMeasurements
from patterns.pattern_engine.src.core.Point import Point
from patterns.pattern_engine.src.core.Util import Util


class BasePantBlock(PatternBlock):
    """
    Base class for pant pattern blocks with shared functionality.

    This class provides common methods and calculations used by all pant
    pattern pieces.
    """

    def __init__(
            self,
            builder: PatternBuilder,
            measurements: Dict[str, float],
            piece_name: str,
            ease_fitting: bool = False
    ):
        """
        Initialize a pant pattern block.

        Args:
            builder: The pattern builder instance
            measurements: Raw measurements dictionary
            piece_name: Name of the pattern piece
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        # Create measurement system before calling parent __init__
        self.measurements_system = PantMeasurements(measurements, ease_fitting)

        # Initialize the parent class
        super().__init__(builder, measurements, piece_name, ease_fitting)

        # Store common values used across methods
        self.seat_width = self.measurements_system.seat / 4

    def add_common_points(self):
        """Add points common to all pant blocks."""
        # FRONT SECTION CONSTRUCTION
        # 0 - Starting point
        self.builder.add_point("0", 0, 0)

        # 0-1: Body rise + ease
        crotch_height = self.measurements_system.get_crotch_height()
        self.builder.add_point("1", 0, crotch_height)

        # 1-2: Inside leg measurement
        leg_length = self.measurements_system.get_leg_length()
        self.builder.add_point("2", 0, leg_length)

        # 1-3: 1/2 inside leg
        knee_height = self.measurements_system.get_knee_height()
        self.builder.add_point("3", 0, knee_height)

        # 1-4: 1/4 seat + ease
        self.builder.add_point("4", self.seat_width, crotch_height)
        self.builder.add_point("5", self.seat_width, 0)
        self.builder.add_point("6", self.seat_width - 1, 0)

        # Crotch point
        crotch_point = self.measurements_system.get_crotch_point()
        self.builder.add_point("8", crotch_point.x, crotch_point.y)

        # Leg middle point
        leg_middle = self.measurements_system.get_leg_middle()
        self.builder.add_point("9", leg_middle, crotch_height)

        # Knee middle point
        self.builder.add_point("10", leg_middle, knee_height)

        # Bottom leg points
        self.builder.add_point("11", leg_middle, leg_length)
        self.builder.add_point("12", leg_middle - (self.seat_width / 3) - 1, leg_length)
        self.builder.add_point("13", leg_middle + (self.seat_width / 3) + 1, leg_length)


class FrontPantBlock(BasePantBlock):
    """Front piece of the pant block."""

    def __init__(
            self,
            builder: PatternBuilder,
            measurements: Dict[str, float],
            ease_fitting: bool = False
    ):
        """
        Initialize a front pant block.

        Args:
            builder: The pattern builder instance
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        super().__init__(builder, measurements, "Front", ease_fitting)

    def draft(self):
        """Draft the front piece of the pant."""
        # Initialize calculations
        self.init_calculations()

        # Start the piece
        self.start_piece()

        # Add common points
        self.add_common_points()

        # Existing construction code
        self.builder.add_line_path(["0", "1"])
        self.builder.add_point("7", self.seat_width,
                               self.measurements_system.body_rise - (self.measurements_system.body_rise / 4))
        self.builder.add_line_path(["6", "7"])
        self.builder.add_line_path(["0", "6"])
        self.builder.add_bezier_curve_with_reference("7", "8", "4", 3.25)
        self.builder.add_line_path(["13", "11", "12"])
        self.builder.add_line_path(["1", "12"])

        point14 = Util.line_intersection(
            self.builder.current_piece.get_point("1"),
            self.builder.current_piece.get_point("12"),
            self.builder.current_piece.get_point("3"),
            self.builder.current_piece.get_point("10")
        )

        if not point14:
            raise Exception("Lines 1-12 and 3-10 don't intersect")

        self.builder.add_point("14", point14.x, point14.y)

        # Calculate point 15 using reflection
        point10 = self.builder.current_piece.get_point("10")
        point15 = Util.reflect_vertical(point14, point10.x)
        self.builder.add_point("15", point15.x, point15.y)

        self.builder.add_line_path(["13", "15"])
        self.builder.add_bezier_curve("15", "8", -1, 0.5)

        # Set seam allowance
        self.builder.set_seam_allowance(1.0)

        # Finish the piece
        self.end_piece()


class BackPantBlock(BasePantBlock):
    """Back piece of the pant block."""

    def __init__(
            self,
            builder: PatternBuilder,
            measurements: Dict[str, float],
            ease_fitting: bool = False
    ):
        """
        Initialize a back pant block.

        Args:
            builder: The pattern builder instance
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        super().__init__(builder, measurements, "Back", ease_fitting)

    def draft(self):
        """Draft the back piece of the pant."""
        # Initialize calculations
        self.init_calculations()

        # Start the piece
        self.start_piece()

        # Add common points
        self.add_common_points()

        # BACK SECTION CONSTRUCTION
        # Starting from front point 6
        # 6-16: 5cm
        point_6 = self.builder.current_piece.get_point("6")
        self.builder.add_point("16", point_6.x - 5, point_6.y)

        # 16-17: 4cm
        point_16 = self.builder.current_piece.get_point("16")
        self.builder.add_point("17", point_16.x, point_16.y - 4)

        # 0-18: 4cm (5cm with ease)
        self.builder.add_point("18", -(5 if self.ease_fitting else 4), 0)

        point_4 = self.builder.current_piece.get_point("4")
        point_8 = self.builder.current_piece.get_point("8")
        crotch_ease = 1 if self.ease_fitting else 0.5
        point_19 = Point(point_4.x, point_4.y / 2)
        point_20 = Point(point_8.x + (abs(point_8.x) - abs(point_4.x)) + crotch_ease, point_4.y)

        self.builder.add_point("19", point_19.x, point_19.y)
        self.builder.add_point("20", point_20.x, point_20.y)
        self.builder.add_point("21", point_20.x, point_20.y + 1)

        crotch_curve_distance = 6 if self.ease_fitting else 5.5
        self.builder.add_bezier_curve_with_reference("19", "21", "4", crotch_curve_distance)

        point_12 = self.builder.current_piece.get_point("12")
        point_13 = self.builder.current_piece.get_point("13")
        self.builder.add_point("22", point_12.x - 1, point_12.y)
        self.builder.add_point("24", point_13.x + 1, point_13.y)

        point_23 = Util.line_intersection(
            self.builder.current_piece.get_point("18"),
            self.builder.current_piece.get_point("22"),
            self.builder.current_piece.get_point("3"),
            self.builder.current_piece.get_point("10")
        )

        if not point_23:
            raise Exception("Lines 18-22 and 3-10 don't intersect")

        point_10 = self.builder.current_piece.get_point("10")
        self.builder.add_point("23", point_23.x, point_23.y)

        point_25 = Util.reflect_vertical(point_23, point_10.x)
        self.builder.add_point("25", point_25.x, point_25.y)

        self.builder.add_line_path(["25", "24", "22", "18", "17", "19"])
        self.builder.add_bezier_curve("21", "25", 2, 0.5)

        # Set seam allowance
        self.builder.set_seam_allowance(1.0)

        # Finish the piece
        self.end_piece()