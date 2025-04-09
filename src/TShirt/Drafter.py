from numpy.f2py.auxfuncs import throw_error

from src.Pattern import Pattern
from src.PatternDrafter import PatternDrafter
from src.TShirt.Body import FrontTShirtBlock, BackTShirtBlock
from src.TShirt.Sleeve import LongSleeveBlock, ShortSleeveBlock


class TShirtDrafter(PatternDrafter):
    """A pattern drafter for a basic tee shirt using the block classes."""

    def __init__(self, measurements=None, ease_fitting=False, short_sleeve=False):
        """
        Initialize the TShirtDrafter.
        
        Args:
            measurements: Dictionary of measurements
            ease_fitting: If True, use the measurements for easier fitting tee shirts or knitwear
            short_sleeve: If True, create a short sleeve version
        """
        super().__init__(measurements)
        self.ease_fitting = ease_fitting
        self.short_sleeve = short_sleeve

        # Set default measurements if not provided (size MEDIUM)
        if not measurements:
            raise Exception("No measurements provided")

    def draft(self) -> Pattern:
        """Draft a tee shirt pattern based on the provided instructions."""
        # Get measurements
        measurements = {name: value for name, value in self.measurements.items()}

        # Create a new pattern
        pattern_type = "Easy Fitting" if self.ease_fitting else "Close Fitting"
        sleeve_type = "Short Sleeve" if self.short_sleeve else "Long Sleeve"
        pattern_name = f"{pattern_type} T-Shirt ({sleeve_type})"
        builder = self.create_pattern(pattern_name)

        # Create and draft the front piece
        front_block = FrontTShirtBlock(builder, measurements, self.ease_fitting)
        front_block.draft()

        # Create and draft the back piece
        back_block = BackTShirtBlock(builder, measurements, self.ease_fitting)
        back_block.draft()

        # Create and draft the sleeve piece
        long_sleeve_block = LongSleeveBlock(builder, measurements, self.ease_fitting)
        long_sleeve_block.draft()
        
        # Create and draft the sleeve piece
        short_sleeve_block = ShortSleeveBlock(builder, measurements, self.ease_fitting)
        short_sleeve_block.draft()

        # Build the pattern
        return builder.build()
