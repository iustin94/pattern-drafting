"""
Pant specific measurement system.

This module provides a specialized measurement system for pants with
convenience methods for common pant measurements.
"""
from typing import Dict, List, Any, Optional

from patterns.pattern_engine.src.core.MeasurementSystem import MeasurementSystem
from patterns.pattern_engine.src.Point import Point


class PantMeasurements(MeasurementSystem):
    """
    Specialized measurement system for pants with convenience methods.

    This class encapsulates all measurement logic specific to pants,
    including ease calculations and derived measurements.
    """

    def __init__(self, measurements: Dict[str, float], ease_fitting: bool = False):
        """
        Initialize Pant measurements.

        Args:
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        super().__init__(measurements, ease_fitting)

        # Cache common measurements for quick access
        self.body_rise = self.get('body_rise', 0)
        self.inside_leg = self.get('inside_leg', 0)
        self.seat = self.get('seat_measurement', 0)
        self.waist = self.get('waist_measurement', 0)

    def get_required_fields(self) -> List[str]:
        """
        Return list of required measurement fields for pants.

        Returns:
            List of required measurement field names
        """
        return [
            'body_rise',
            'inside_leg',
            'seat_measurement',
            'waist_measurement'
        ]

    def get_waist_ease(self) -> float:
        """
        Get waist ease based on fitting preference.

        Returns:
            Appropriate waist ease
        """
        return 2 if self.ease_fitting else 1

    def get_hip_ease(self) -> float:
        """
        Get hip/seat ease based on fitting preference.

        Returns:
            Appropriate hip ease
        """
        return 4 if self.ease_fitting else 2

    def get_crotch_depth(self) -> float:
        """
        Calculate crotch depth with ease.

        Returns:
            Crotch depth with ease
        """
        return self.body_rise + (2 if self.ease_fitting else 1)

    def get_crotch_height(self) -> float:
        """
        Calculate crotch height.

        Returns:
            Crotch height
        """
        return self.body_rise + self.get_hip_ease()

    def get_front_rise(self) -> float:
        """
        Calculate front rise.

        Returns:
            Front rise measurement
        """
        return self.get_crotch_depth() * 0.45

    def get_back_rise(self) -> float:
        """
        Calculate back rise.

        Returns:
            Back rise measurement
        """
        return self.get_crotch_depth() * 0.55

    def get_leg_middle(self) -> float:
        """
        Calculate leg middle width.

        Returns:
            Leg middle width
        """
        return (self.seat / 4 / 2) + 1

    def get_knee_height(self) -> float:
        """
        Calculate knee height.

        Returns:
            Knee height
        """
        return self.body_rise + (self.inside_leg / 2)

    def get_leg_length(self) -> float:
        """
        Calculate total leg length.

        Returns:
            Total leg length
        """
        return self.body_rise + self.inside_leg

    def get_crotch_point(self) -> Point:
        """
        Calculate crotch point position.

        Returns:
            Point object representing crotch point
        """
        eighth_point = self.body_rise + (self.body_rise / 4) + (0.5 if self.ease_fitting else -0.5)
        return Point(eighth_point, self.get_crotch_height())