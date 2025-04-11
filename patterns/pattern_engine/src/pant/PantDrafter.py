"""
Pant pattern drafter with hem feature support.

This module extends the PantDrafter to add specific support for the hem feature.
"""
from typing import Dict, List, Optional, Union

from patterns.pattern_engine.src.core.PatternDrafter import PatternDrafter
from patterns.pattern_engine.src.core.Pattern import Pattern
from patterns.pattern_engine.src.features.HemFeature import HemFeature


class PantDrafterWithHem(PantDrafter):
    """
    Extended pant pattern drafter with integrated hem feature support.

    This class extends the base PantDrafter to provide specialized
    handling for hem features in pants.
    """

    def __init__(
            self,
            measurements: Optional[Dict[str, float]] = None,
            ease_fitting: bool = False,
            features: Optional[List] = None,
            hem_width: float = 2.0,
            include_hem: bool = True
    ):
        """
        Initialize the pant drafter with hem support.

        Args:
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
            features: List of additional features to apply
            hem_width: Width of the hem in cm
            include_hem: Whether to include the hem feature
        """
        # Initialize with base features
        self.hem_width = hem_width
        self.include_hem = include_hem
        
        # Create features list if not provided
        if features is None:
            features = []
            
        # Add hem feature if requested
        if include_hem:
            hem_feature = HemFeature(
                hem_width=hem_width,
                fold_line=True,
                piece_names=["Front", "Back"]
            )
            features.append(hem_feature)
            
        # Initialize parent class
        super().__init__(measurements, ease_fitting, features)

    def create_pattern(self, name: str, pants_length: Optional[str] = None) -> Pattern:
        """
        Create a complete pant pattern with hem.

        Args:
            name: Name of the pattern
            pants_length: Optional length style (full, capri, shorts)

        Returns:
            Completed pattern with hem
        """
        # Modify pattern name based on hem inclusion
        if self.include_hem:
            name = f"{name} with {self.hem_width}cm Hem"
            
        # Create the base pattern
        pattern = super()._create_base_pattern()
        
        # Apply any features not already applied
        self._apply_features(pattern)
        
        return pattern


# Example usage:
if __name__ == "__main__":
    # Sample measurements (in cm)
    measurements = {
        'waist_measurement': 80,
        'seat_measurement': 98,
        'inside_leg': 76,
        'body_rise': 28
    }
    
    # Create a pant pattern with hem
    drafter = PantDrafterWithHem(
        measurements=measurements,
        ease_fitting=True,
        hem_width=3.0
    )
    
    pattern = drafter.create_pattern("Classic Pants")
    
    # Further processing...