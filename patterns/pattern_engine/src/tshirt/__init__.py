"""
T-Shirt pattern drafting module.

This package provides classes for drafting T-shirt patterns with various
options and features.
"""
from patterns.pattern_engine.src.tshirt.BaseTShirtBlock import BaseTShirtBlock
from patterns.pattern_engine.src.tshirt.TShirtMeasurements import TShirtMeasurements
from patterns.pattern_engine.src.tshirt.TShirtDrafter import TShirtDrafter
from patterns.pattern_engine.src.tshirt.ShortSleeveBlock import ShortSleeveBlock
from patterns.pattern_engine.src.tshirt.LongSleeveBlock import LongSleeveBlock
from patterns.pattern_engine.src.tshirt.FrontTShirtBlock import FrontTShirtBlock
from patterns.pattern_engine.src.tshirt.BackTShirtBlock import BackTShirtBlock
from patterns.pattern_engine.src.tshirt.BaseSleeveBlock import BaseSleeveBlock

__all__ = [
    'TShirtMeasurements',
    'BaseTShirtBlock',
    'FrontTShirtBlock',
    'BackTShirtBlock',
    'BaseSleeveBlock',
    'LongSleeveBlock',
    'ShortSleeveBlock',
    'TShirtDrafter',
]