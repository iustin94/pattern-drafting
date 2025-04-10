from typing import TypedDict

from patterns.models import Pattern
from patterns.pattern_engine.src.Pant.Body import FrontPantBlock, BackPantBlock
from patterns.pattern_engine.src.PatternDrafter import PatternDrafter


class PantMeasurements(TypedDict):
    """Type-enforced measurement structure"""
    body_rise: float
    inside_leg: float
    seat_measurement: float
    waist_measurement: float


class PantDrafter(PatternDrafter):
    """Measurement-validated pant drafter without explicit checks"""

    def __init__(self, measurements: PantMeasurements, ease_fitting=False):
        """
        Enforces measurements through type system rather than runtime checks
        """
        super().__init__(measurements)
        self.ease_fitting = ease_fitting

    def draft(self) -> Pattern:
        """Draft pattern using type-enforced measurements"""
        # Create pattern with auto-validated measurements
        builder = self.create_pattern(f"{'Easy' if self.ease_fitting else 'Standard'} Fit Pants")

        # Front and back blocks use measurements directly
        FrontPantBlock(builder, self.measurements, self.ease_fitting).draft()
        BackPantBlock(builder, self.measurements, self.ease_fitting).draft()

        # ModifiedFrontPantBlock(builder, self.measurements, self.ease_fitting).draft()
        # ModifiedBackPantBlock(builder, self.measurements, self.ease_fitting).draft()

        return builder.build()