"""
T-Shirt specific measurement system.

This module provides a specialized measurement system for T-shirts with
convenience methods for common T-shirt measurements.
"""
from typing import Dict, List, Any, Optional

from patterns.pattern_engine.src.core.MeasurementSystem import MeasurementSystem
from patterns.pattern_engine.src.Point import Point


class TShirtMeasurements(MeasurementSystem):
    """
    Specialized measurement system for T-shirts with convenience methods.

    This class encapsulates all measurement logic specific to T-shirts,
    including ease calculations and derived measurements.
    """

    def __init__(self, measurements: Dict[str, float], ease_fitting: bool = False):
        """
        Initialize T-Shirt measurements.

        Args:
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        super().__init__(measurements, ease_fitting)

        # Cache common measurements for quick access
        self.chest = self.get('chest', 0)
        self.half_back = self.get('half_back', 0)
        self.back_neck_to_waist = self.get('back_neck_to_waist', 0)
        self.scye_depth = self.get('scye_depth', 0)
        self.neck_size = self.get('neck_size', 0)
        self.sleeve_length = self.get('sleeve_length', 0)
        self.close_wrist = self.get('close_wrist', 0)
        self.finished_length = self.get('finished_length', 0)

    def get_required_fields(self) -> List[str]:
        """
        Return list of required measurement fields for T-shirts.

        Returns:
            List of required measurement field names
        """
        return [
            'chest',
            'half_back',
            'back_neck_to_waist',
            'scye_depth',
            'neck_size',
            'sleeve_length',
            'close_wrist',
            'finished_length'
        ]

    def get_scye_depth_with_ease(self) -> float:
        """
        Get scye depth with appropriate ease.

        Returns:
            Scye depth with ease applied
        """
        ease = 2.5 if self.ease_fitting else 1
        return self.scye_depth + ease

    def get_half_back_with_ease(self) -> float:
        """
        Get half back with appropriate ease.

        Returns:
            Half back with ease applied
        """
        ease = 2 if self.ease_fitting else 1
        return self.half_back + ease

    def get_chest_with_ease(self) -> float:
        """
        Get chest with appropriate ease.

        Returns:
            Chest with ease applied
        """
        ease = 4 if self.ease_fitting else 2.5
        return self.chest / 4 + ease

    def get_shoulder_height(self) -> float:
        """
        Calculate shoulder height.

        Returns:
            Shoulder height
        """
        return self.get_scye_depth_with_ease() / 2 / 4

    def get_shoulder_width(self) -> float:
        """
        Calculate shoulder width.

        Returns:
            Shoulder width
        """
        return self.get_half_back_with_ease() + 0.75

    def get_underarm_width(self) -> float:
        """
        Calculate underarm width.

        Returns:
            Underarm width
        """
        return self.get_chest_with_ease()

    def get_underarm_height(self) -> float:
        """
        Calculate underarm height.

        Returns:
            Underarm height
        """
        return self.get_scye_depth_with_ease()

    def shoulder_point(self) -> Point:
        """
        Get shoulder point coordinates.

        Returns:
            Point object for shoulder point
        """
        return Point(self.get_shoulder_width(), self.get_shoulder_height())

    def underarm_point(self) -> Point:
        """
        Get underarm point coordinates.

        Returns:
            Point object for underarm point
        """
        return Point(self.get_underarm_width(), self.get_underarm_height())