"""
Pattern features for the pattern drafting system.

This package provides various features that can be applied to patterns,
such as hems, pockets, collars, etc.
"""

from patterns.pattern_engine.src.features.HemFeature import HemFeature

# Make sure features are registered
from patterns.pattern_engine.src.features.HemFeature import PatternFeatureRegistry

__all__ = [
    'HemFeature',
]