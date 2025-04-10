"""
Measurement System for pattern drafting.

This module provides a centralized system for managing, validating, and accessing
pattern measurements with proper ease calculation.
"""
from typing import Dict, List, Any, Optional, TypeVar, Generic, Union


class MeasurementSystem:
    """
    Central system for managing pattern measurements with validation.

    This base class provides shared functionality for all measurement types,
    including validation, ease calculation, and standardized access.
    """

    def __init__(self, measurements: Dict[str, float], ease_fitting: bool = False):
        """
        Initialize measurement system with raw measurements.

        Args:
            measurements: Dictionary of raw measurements
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        self.measurements = measurements.copy()
        self.ease_fitting = ease_fitting
        self.validate_measurements()

    def validate_measurements(self) -> None:
        """
        Ensure all required measurements exist.

        Raises:
            ValueError: If any required measurement is missing
        """
        required_fields = self.get_required_fields()
        missing = [field for field in required_fields if field not in self.measurements]
        if missing:
            raise ValueError(f"Missing required measurements: {', '.join(missing)}")

    def get_required_fields(self) -> List[str]:
        """
        Return list of required measurement fields.

        Override in subclasses to specify required measurements.

        Returns:
            List of required measurement field names
        """
        return []

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

    def with_ease(self, field: str, standard_ease: float, extra_ease: float = 0) -> float:
        """
        Return a measurement with ease applied.

        Args:
            field: Measurement field name
            standard_ease: Base ease to apply
            extra_ease: Additional ease to apply when ease_fitting is True

        Returns:
            Measurement value with appropriate ease
        """
        base_value = self.get(field, 0)
        ease = standard_ease + (extra_ease if self.ease_fitting else 0)
        return base_value + ease

    def as_dict(self) -> Dict[str, float]:
        """
        Return all measurements as a dictionary.

        Returns:
            Copy of all measurements
        """
        return self.measurements.copy()