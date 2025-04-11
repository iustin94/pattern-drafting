"""
Pattern Feature system for adding functionality to patterns.

This module provides a framework for creating and applying features like hems,
pockets, collars, etc. to pattern blocks using a composition approach.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type

from .PatternBuilder import PatternBuilder
from .Pattern import Pattern


class PatternFeature(ABC):
    """
    Base class for pattern features that can be applied to pattern blocks.

    Pattern features use the Decorator pattern to add functionality to existing
    pattern blocks without modifying their core implementation.
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """
        Initialize the pattern features.

        Args:
            options: Optional configuration for the features
        """
        self.options = options or {}

    @abstractmethod
    def apply(self, builder: PatternBuilder, pattern: Pattern) -> None:
        """
        Apply this features to a pattern.

        Args:
            builder: The PatternBuilder instance
            pattern: The pattern to modify
        """
        pass