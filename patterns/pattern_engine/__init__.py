"""
Pattern drafting system for creating, manipulating, and rendering clothing patterns.

This module provides a foundation for defining, manipulating, and rendering
clothing patterns using a declarative approach.
"""

# Import core components
from patterns.pattern_engine.src.core import (
    MeasurementSystem,
    PatternBlock,
    GarmentBlock,
    PatternFeature,
    PatternFeatureRegistry,
    PatternDrafter
)

# Import features
from patterns.pattern_engine.src.features import HemFeature

# Import pattern specific modules
from patterns.pattern_engine.src.tshirt import (
    TShirtMeasurements,
    TShirtDrafter,
    BaseTShirtBlock,
    FrontTShirtBlock,
    BackTShirtBlock,
    BaseSleeveBlock,
    LongSleeveBlock,
    ShortSleeveBlock
)

from patterns.pattern_engine.src.pant import (
    PantMeasurements,
    PantDrafter,
    BasePantBlock,
    FrontPantBlock,
    BackPantBlock
)

__all__ = [
    # Core
    'MeasurementSystem',
    'PatternBlock',
    'GarmentBlock',
    'PatternFeature',
    'PatternFeatureRegistry',
    'PatternDrafter',
    
    # Features
    'HemFeature',
    
    # T-Shirt
    'TShirtMeasurements',
    'TShirtDrafter',
    'BaseTShirtBlock',
    'FrontTShirtBlock',
    'BackTShirtBlock',
    'BaseSleeveBlock',
    'LongSleeveBlock',
    'ShortSleeveBlock',
    
    # Pants
    'PantMeasurements',
    'PantDrafter',
    'BasePantBlock',
    'FrontPantBlock',
    'BackPantBlock'
]

__version__ = "0.2.0"