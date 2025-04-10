"""
T-Shirt pattern blocks implementation using the refactored pattern system.

This module provides implementations of T-shirt pattern blocks including
front, back, and sleeve pieces with a clean object-oriented approach.
"""
from typing import Dict, List, Any, Optional

from patterns.pattern_engine.src.core.PatternBlock import PatternBlock
from patterns.pattern_engine.src.PatternBuilder import PatternBuilder
from patterns.pattern_engine.src.tshirt.TShirtMeasurements import TShirtMeasurements
from patterns.pattern_engine.src.Point import Point
from patterns.pattern_engine.src.Line import Line


class BaseTShirtBlock(PatternBlock):
    """
    Base class for T-shirt pattern blocks with shared functionality.
    
    This class provides common methods and calculations used by all T-shirt
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
        Initialize a T-shirt pattern block.
        
        Args:
            builder: The pattern builder instance
            measurements: Raw measurements dictionary
            piece_name: Name of the pattern piece
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        # Create measurement system before calling parent __init__
        self.measurements_system = TShirtMeasurements(measurements, ease_fitting)
        
        # Then initialize the parent class
        super().__init__(builder, measurements, piece_name, ease_fitting)
    
    def add_common_points(self):
        """Add points common to all T-shirt blocks."""
        # Square down and across from 0
        self.builder.add_point("0", 0, 0)

        # 0–1 Back neck to waist plus 1cm; square across
        back_neck_to_waist = self.measurements_system.back_neck_to_waist
        self.builder.add_point("1", 0, back_neck_to_waist + 1)

        # 0–2 Finished length; square across
        finished_length = self.measurements_system.finished_length
        self.builder.add_point("2", 0, finished_length)
        
        underarm_width = self.measurements_system.get_underarm_width()
        self.builder.add_point("13", underarm_width, finished_length)

        # 0–3 Scye depth plus ease; square across
        scye_depth_with_ease = self.measurements_system.get_scye_depth_with_ease()
        self.builder.add_point("3", 0, scye_depth_with_ease)
        
        half_back_with_ease = self.measurements_system.get_half_back_with_ease()
        self.builder.add_point("8", half_back_with_ease, scye_depth_with_ease)

        # 0–4 1/2 measurement 0–3; square across
        self.builder.add_point("4", 0, scye_depth_with_ease / 2)
        self.builder.add_point("9", half_back_with_ease, scye_depth_with_ease / 2)

        # 0–5 1/4 measurement 0–4; square across
        shoulder_height = self.measurements_system.get_shoulder_height()
        self.builder.add_point("5", 0, shoulder_height)

        # Shoulder point and armhole
        self.builder.add_point("10", half_back_with_ease, shoulder_height)
        
        shoulder_width = self.measurements_system.get_shoulder_width()
        self.builder.add_point("11", shoulder_width, shoulder_height)
        
        underarm_height = self.measurements_system.get_underarm_height()
        self.builder.add_point("12", underarm_width, underarm_height)

        # 0–6 1/5 neck size minus 1cm; square up
        neck_size = self.measurements_system.neck_size
        self.builder.add_point("6", neck_size / 5 - 1, 0)
        
        # 6–7 1.5cm; for back neck curve
        self.builder.add_point("7", neck_size / 5 - 1, -1.5)
    
    def add_common_paths(self):
        """Add path segments common to all T-shirt blocks."""
        # Create armhole curve in two segments
        self.builder.add_bezier_curve("11", "9", 0.25, 0.3)
        self.builder.add_bezier_curve("9", "12", 2.5, 0.7)

        # Shoulder line
        self.builder.add_line_path(["7", "11"])

        # Set seam allowance
        self.builder.set_seam_allowance(1.0)


class FrontTShirtBlock(BaseTShirtBlock):
    """Front piece of the T-shirt block."""
    
    def __init__(
        self, 
        builder: PatternBuilder, 
        measurements: Dict[str, float], 
        ease_fitting: bool = False
    ):
        """
        Initialize a front T-shirt block.
        
        Args:
            builder: The pattern builder instance
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        super().__init__(builder, measurements, "Front", ease_fitting)
    
    def draft(self):
        """Draft the front piece of the T-shirt."""
        # Initialize calculations before drafting
        self.init_calculations()
        
        self.start_piece()

        # Add common points for the block
        self.add_common_points()

        # Add front-specific neck point
        # Point 14 is 1/5 neck size minus 2cm on the y-axis
        neck_size = self.measurements_system.neck_size
        self.builder.add_point("14", 0, neck_size / 5 - 2)

        # Create front-specific outline paths
        # Front neck curve from point 7 to point
        self.builder.add_bezier_curve("7", "14", -2.5, 0.5)

        # Side seam and bottom
        self.builder.add_line_path(["12", "13", "2", "14"])
        
        # Add common path elements
        self.add_common_paths()

        self.end_piece()


class BackTShirtBlock(BaseTShirtBlock):
    """Back piece of the T-shirt block."""
    
    def __init__(
        self, 
        builder: PatternBuilder, 
        measurements: Dict[str, float], 
        ease_fitting: bool = False
    ):
        """
        Initialize a back T-shirt block.
        
        Args:
            builder: The pattern builder instance
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        super().__init__(builder, measurements, "Back", ease_fitting)
    
    def draft(self):
        """Draft the back piece of the T-shirt."""
        # Initialize calculations before drafting
        self.init_calculations()
        
        self.start_piece()

        # Add common points for the block
        self.add_common_points()

        # Create back-specific outline paths
        # Back neck curve
        self.builder.add_bezier_curve("0", "7", 0.75, 0.8)
        
        # Side seam and bottom
        self.builder.add_line_path(["12", "13", "2", "0"])

        # Add common path elements
        self.add_common_paths()

        self.end_piece()


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
        self.measurements_system = TShirtMeasurements(measurements, ease_fitting)
        
        # Then initialize the parent class
        super().__init__(builder, measurements, piece_name, ease_fitting)
    
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
        self.builder.add_line_path(["21", "17", "15"])
        self.builder.set_seam_allowance(1.0)
    
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


class LongSleeveBlock(BaseSleeveBlock):
    """Long sleeve block with tapered wrist."""

    WRIST_EASE = 3.5
    
    def __init__(
        self, 
        builder: PatternBuilder, 
        measurements: Dict[str, float], 
        ease_fitting: bool = False
    ):
        """
        Initialize a long sleeve block.
        
        Args:
            builder: The pattern builder instance
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        super().__init__(builder, measurements, "Long Sleeve", ease_fitting)
    
    def init_calculations(self):
        """Initialize calculated values for long sleeve drafting."""
        super().init_calculations()
        self.wrist_width = self.measurements_system.close_wrist / 2 + self.WRIST_EASE
    
    def _sleeve_length(self) -> float:
        """
        Calculate long sleeve length.
        
        Returns:
            Sleeve length
        """
        return self.measurements_system.sleeve_length
    
    def _create_sleeve_body(self):
        """Create long sleeve specific elements."""
        self.builder.add_point("21", self.wrist_width, self._sleeve_length())
        self.builder.add_bezier_curve("18", "21", 2, 0.5)