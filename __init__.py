"""
Pattern Drafting System

A Python library for creating, manipulating, and rendering clothing patterns.
"""
from .Core import Point, Line, Curve, PatternPiece, Pattern
from .Core import PatternBuilder, PatternDrafter, Measurement
from .Core import PatternRenderer

__version__ = "0.1.0"
__all__ = [
    'Point', 'Line', 'Curve', 'PatternPiece', 'Pattern',
    'PatternBuilder', 'PatternDrafter', 'Measurement',
    'PatternRenderer'
]