from typing import Dict
from src.PatternBuilder import PatternBuilder


class PatternDrafter:
    """Helper class for implementing specific pattern drafting algorithms."""

    def __init__(self, measurements: Dict[str, float] = None):
        self.measurements = measurements or {}

    def set_measurement(self, name: str, value: float) -> None:
        """Set a measurement value."""
        self.measurements[name] = value

    def get_measurement(self, name: str, default: float = None) -> float:
        """Get a measurement value, with optional default."""
        if name not in self.measurements and default is None:
            raise KeyError(f"Measurement '{name}' not found")
        return self.measurements.get(name, default)

    def create_pattern(self, name: str) -> PatternBuilder:
        """Create a new pattern builder with the current measurements."""
        builder = PatternBuilder(name)
        for name, value in self.measurements.items():
            builder.pattern.set_measurement(name, value)
        return builder



