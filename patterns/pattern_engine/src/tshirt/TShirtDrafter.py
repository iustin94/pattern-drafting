"""
T-Shirt pattern drafter using the Shapely-based pattern system.

This module provides an implementation of the PatternDrafter for T-shirts
with support for features and different sleeve options.
"""
from typing import Dict, List, Any, Optional

from ..core.Pattern import Pattern
from ..core.Point import Point
from ..core.PatternBuilder import PatternBuilder
from ..core.PatternFeatureRegistry import PatternFeatureRegistry


class TShirtMeasurements:
    """
    Specialized measurement system for T-shirts with convenience methods.
    """
    
    def __init__(self, measurements: Dict[str, float], ease_fitting: bool = False):
        """
        Initialize T-Shirt measurements.
        
        Args:
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        self.measurements = measurements
        self.ease_fitting = ease_fitting
        
        # Cache common measurements for quick access
        self.chest = self.get('chest', 0)
        self.half_back = self.get('half_back', 0)
        self.back_neck_to_waist = self.get('back_neck_to_waist', 0)
        self.scye_depth = self.get('scye_depth', 0)
        self.neck_size = self.get('neck_size', 0)
        self.sleeve_length = self.get('sleeve_length', 0)
        self.close_wrist = self.get('close_wrist', 0)
        self.finished_length = self.get('finished_length', 0)
    
    def get(self, name: str, default: Any = None) -> Any:
        """
        Get a measurement with optional default.
        
        Args:
            name: Measurement name
            default: Default value if measurement doesn't exist
            
        Returns:
            Measurement value or default
        """
        return self.measurements.get(name, default)
    
    def get_scye_depth_with_ease(self) -> float:
        """Get scye depth with appropriate ease."""
        ease = 2.5 if self.ease_fitting else 1
        return self.scye_depth + ease
    
    def get_half_back_with_ease(self) -> float:
        """Get half back with appropriate ease."""
        ease = 2 if self.ease_fitting else 1
        return self.half_back + ease
    
    def get_chest_with_ease(self) -> float:
        """Get chest with appropriate ease."""
        ease = 4 if self.ease_fitting else 2.5
        return self.chest / 4 + ease
    
    def get_shoulder_height(self) -> float:
        """Calculate shoulder height."""
        return self.get_scye_depth_with_ease() / 2 / 4
    
    def get_shoulder_width(self) -> float:
        """Calculate shoulder width."""
        return self.get_half_back_with_ease() + 0.75
    
    def get_underarm_width(self) -> float:
        """Calculate underarm width."""
        return self.get_chest_with_ease()
    
    def get_underarm_height(self) -> float:
        """Calculate underarm height."""
        return self.get_scye_depth_with_ease()
    
    def shoulder_point(self) -> Point:
        """Get shoulder point coordinates."""
        return Point(self.get_shoulder_width(), self.get_shoulder_height())
    
    def underarm_point(self) -> Point:
        """Get underarm point coordinates."""
        return Point(self.get_underarm_width(), self.get_underarm_height())


class TShirtDrafter:
    """
    T-shirt pattern drafter with feature support using Shapely.
    
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
        self.measurements = measurements or {}
        self.ease_fitting = ease_fitting
        self.short_sleeve = short_sleeve
        self.features = features or []
        
        # Create measurement system
        self.measurements_system = TShirtMeasurements(measurements, ease_fitting)
        
        # Validate measurements
        self._validate_measurements()
    
    def _validate_measurements(self) -> None:
        """Validate that required measurements are present."""
        required = [
            'chest',
            'half_back',
            'back_neck_to_waist',
            'scye_depth',
            'neck_size',
            'sleeve_length',
            'close_wrist',
            'finished_length'
        ]
        
        missing = [field for field in required if field not in self.measurements]
        if missing:
            raise ValueError(f"Missing required measurements: {', '.join(missing)}")
    
    def add_feature(self, feature_type: str, **options) -> 'TShirtDrafter':
        """
        Add a feature to this pattern drafter.
        
        Args:
            feature_type: Name of the feature
            **options: Options for the feature
            
        Returns:
            Self for method chaining
        """
        feature_class = PatternFeatureRegistry.get(feature_type)
        feature = feature_class(**options)
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
        
        # Apply each feature
        builder = self._create_pattern_builder(pattern.name)
        builder.pattern = pattern  # Use the existing pattern
        
        for feature in self.features:
            feature.apply(builder, pattern)
        
        return pattern
    
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
        builder = self._create_pattern_builder(pattern_name)
        
        # Draft the pattern pieces
        self._draft_front_piece(builder)
        self._draft_back_piece(builder)
        
        if self.short_sleeve:
            self._draft_short_sleeve(builder)
        else:
            self._draft_long_sleeve(builder)
        
        return builder.pattern
    
    def _create_pattern_builder(self, name: str) -> PatternBuilder:
        """Create a pattern builder with the measurements."""
        builder = PatternBuilder(name)
        
        # Add all measurements to the pattern
        for name, value in self.measurements.items():
            builder.pattern.set_measurement(name, value)
        
        return builder
    
    def _draft_front_piece(self, builder: PatternBuilder) -> None:
        """
        Draft the front piece of the T-shirt.
        
        Args:
            builder: The pattern builder
        """
        builder.start_piece("Front")
        
        # Add common points
        self._add_common_points(builder)
        
        # Add front-specific neck point
        neck_size = self.measurements_system.neck_size
        builder.add_point("14", 0, neck_size / 5 - 2)
        
        # Create front neck curve
        builder.add_bezier_curve("7", "14", -2.5, 0.5)
        
        # Create side seam and bottom
        builder.add_line_path(["12", "13", "2", "14"])
        
        # Add common path elements
        self._add_common_paths(builder)
        
        # Set seam allowance
        builder.set_seam_allowance(1.0)
        
        builder.end_piece()
    
    def _draft_back_piece(self, builder: PatternBuilder) -> None:
        """
        Draft the back piece of the T-shirt.
        
        Args:
            builder: The pattern builder
        """
        builder.start_piece("Back")
        
        # Add common points
        self._add_common_points(builder)
        
        # Create back neck curve
        builder.add_bezier_curve("0", "7", 0.75, 0.8)
        
        # Create side seam and bottom
        builder.add_line_path(["12", "13", "2", "0"])
        
        # Add common path elements
        self._add_common_paths(builder)
        
        # Set seam allowance
        builder.set_seam_allowance(1.0)
        
        builder.end_piece()
    
    def _draft_long_sleeve(self, builder: PatternBuilder) -> None:
        """
        Draft the long sleeve piece.
        
        Args:
            builder: The pattern builder
        """
        builder.start_piece("Long Sleeve")
        
        # Initialize calculations
        self._initialize_sleeve_calculations(builder)
        
        # Add the wrist point
        wrist_width = self.measurements_system.close_wrist / 2 + 3.5  # WRIST_EASE
        sleeve_length = self.measurements_system.sleeve_length
        builder.add_point("21", wrist_width, sleeve_length)
        
        # Create sleeve curves
        builder.add_bezier_curve("18", "21", 2, 0.5)
        builder.add_line_path(["21", "17", "15"])
        
        # Set seam allowance
        builder.set_seam_allowance(1.0)
        
        builder.end_piece()
    
    def _draft_short_sleeve(self, builder: PatternBuilder) -> None:
        """
        Draft the short sleeve piece.
        
        Args:
            builder: The pattern builder
        """
        builder.start_piece("Short Sleeve")
        
        # Initialize calculations
        self._initialize_sleeve_calculations(builder)
        
        # Calculate short sleeve parameters
        SHORT_SLEEVE_LENGTH = 25
        armhole_length = self._calculate_armhole_length()
        half_scye_depth = self.measurements_system.get_scye_depth_with_ease() / 2
        
        # Calculate sleeve bottom using Pythagorean theorem
        sleeve_bottom = ((armhole_length + 2.5) ** 2 - half_scye_depth ** 2) ** 0.5 - 4
        
        # Create sleeve bottom point
        builder.add_point("21", sleeve_bottom, SHORT_SLEEVE_LENGTH)
        
        # Create curved bottom edge with control point
        point_18 = builder.current_piece.get_point("18")
        point_21 = builder.current_piece.get_point("21")
        
        # Calculate control point for natural curve
        control_x = point_18.x + (point_21.x - point_18.x) * 0.4
        distance = point_18.distance_to(point_21)
        curve_offset = distance * 0.15
        control_y = point_18.y + (point_21.y - point_18.y) * 0.4 + curve_offset
        
        builder.add_point("18_21_control", control_x, control_y)
        
        # Create sleeve head curve
        self._create_sleeve_head_curve(builder)
        
        # Create curved bottom
        builder.add_bezier_curve("18", "21", curve_offset, 0.4)
        
        # Add remaining paths
        builder.add_line_path(["21", "17", "15"])
        
        # Set seam allowance
        builder.set_seam_allowance(1.0)
        
        builder.end_piece()
    
    def _add_common_points(self, builder: PatternBuilder) -> None:
        """
        Add points common to all T-shirt blocks.
        
        Args:
            builder: The pattern builder
        """
        # Starting point
        builder.add_point("0", 0, 0)
        
        # Basic body measurements
        back_neck_to_waist = self.measurements_system.back_neck_to_waist
        finished_length = self.measurements_system.finished_length
        builder.add_point("1", 0, back_neck_to_waist + 1)
        builder.add_point("2", 0, finished_length)
        
        # Width measurements
        underarm_width = self.measurements_system.get_underarm_width()
        builder.add_point("13", underarm_width, finished_length)
        
        # Armhole measurements
        scye_depth_with_ease = self.measurements_system.get_scye_depth_with_ease()
        builder.add_point("3", 0, scye_depth_with_ease)
        
        half_back_with_ease = self.measurements_system.get_half_back_with_ease()
        builder.add_point("8", half_back_with_ease, scye_depth_with_ease)
        
        # Mid-points and shoulder
        builder.add_point("4", 0, scye_depth_with_ease / 2)
        builder.add_point("9", half_back_with_ease, scye_depth_with_ease / 2)
        
        shoulder_height = self.measurements_system.get_shoulder_height()
        builder.add_point("5", 0, shoulder_height)
        
        builder.add_point("10", half_back_with_ease, shoulder_height)
        
        shoulder_width = self.measurements_system.get_shoulder_width()
        builder.add_point("11", shoulder_width, shoulder_height)
        
        underarm_height = self.measurements_system.get_underarm_height()
        builder.add_point("12", underarm_width, underarm_height)
        
        # Neck measurements
        neck_size = self.measurements_system.neck_size
        builder.add_point("6", neck_size / 5 - 1, 0)
        builder.add_point("7", neck_size / 5 - 1, -1.5)
    
    def _add_common_paths(self, builder: PatternBuilder) -> None:
        """
        Add path segments common to all T-shirt blocks.
        
        Args:
            builder: The pattern builder
        """
        # Create armhole curve in two segments
        builder.add_bezier_curve("11", "9", 0.25, 0.3)
        builder.add_bezier_curve("9", "12", 2.5, 0.7)
        
        # Shoulder line
        builder.add_line_path(["7", "11"])
    
    def _initialize_sleeve_calculations(self, builder: PatternBuilder) -> None:
        """
        Initialize calculations for sleeve drafting.
        
        Args:
            builder: The pattern builder
        """
        # Calculate half scye depth
        scye_depth_with_ease = self.measurements_system.get_scye_depth_with_ease()
        half_scye_depth = scye_depth_with_ease / 2
        
        # Calculate armhole length
        armhole_length = self._calculate_armhole_length()
        
        # Origin point
        builder.add_point("15", 0, 0)
        
        # Vertical measurements
        builder.add_point("16", 0, half_scye_depth)
        
        # Calculate sleeve length
        sleeve_length = self.measurements_system.sleeve_length
        if self.short_sleeve:
            sleeve_length = 25  # SHORT_SLEEVE_LENGTH
        
        builder.add_point("17", 0, sleeve_length)
        
        # Calculate diagonal using Pythagorean theorem
        # armhole_length² = diagonal² + (half_scye_depth)²
        diagonal = ((armhole_length + 2.5) ** 2 - half_scye_depth ** 2) ** 0.5
        
        # Add critical points
        builder.add_point("18", diagonal, half_scye_depth)
        builder.add_point("19", diagonal, sleeve_length)
        
        # Calculate control point for sleeve head
        point_18 = builder.current_piece.get_point("18")
        builder.add_point(
            "20",
            point_18.x - (point_18.x / 3),
            point_18.y - (half_scye_depth / 3)
        )
    
    def _create_sleeve_head_curve(self, builder: PatternBuilder) -> None:
        """
        Create sleeve head curve.
        
        Args:
            builder: The pattern builder
        """
        builder.add_bezier_curve("18", "20", -0.75, 0.5)
        builder.add_bezier_curve("20", "15", 2, 0.5)
    
    def _calculate_armhole_length(self) -> float:
        """
        Calculate armhole length between shoulder and underarm points.
        
        Returns:
            Armhole length
        """
        shoulder_point = self.measurements_system.shoulder_point()
        underarm_point = self.measurements_system.underarm_point()
        
        dx = underarm_point.x - shoulder_point.x
        dy = underarm_point.y - shoulder_point.y
        return (dx*dx + dy*dy) ** 0.5