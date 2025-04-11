"""
Pattern Block base classes for pattern drafting.

This module provides abstract base classes for pattern blocks with standardized
interfaces for drafting, point creation, and path generation.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from .MeasurementSystem import MeasurementSystem
from .PatternBuilder import PatternBuilder


class PatternBlock(ABC):
    """
    Abstract base class for pattern blocks.
    
    This provides a standardized interface and common functionality for all
    pattern blocks regardless of garment type.
    """
    
    def __init__(
        self, 
        builder: PatternBuilder, 
        measurements: Dict[str, float],
        piece_name: str,
        ease_fitting: bool = False
    ):
        """
        Initialize a pattern block.
        
        Args:
            builder: The pattern builder instance
            measurements: Raw measurements dictionary
            piece_name: Name of the pattern piece
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        self.builder = builder
        self.piece_name = piece_name
        self.ease_fitting = ease_fitting

        # Create measurement system if not already created by a subclass
        if not hasattr(self, 'measurements_system'):
            self.measurements_system = MeasurementSystem(measurements, ease_fitting)
        
        # Note: init_calculations() is no longer called from the constructor
        # Subclasses should call it explicitly when needed

    @property
    def measurements(self) -> MeasurementSystem:
        return self.measurements_system
    
    def init_calculations(self) -> None:
        """
        Initialize calculated values needed for drafting.
        
        Override in subclasses to pre-calculate values needed during drafting.
        """
        pass
    
    @abstractmethod
    def draft(self) -> None:
        """
        Draft the pattern piece.
        
        This method must be implemented by all subclasses to create the actual
        pattern piece with points and paths.
        """
        pass
    
    def add_common_points(self) -> None:
        """
        Add points common to this block type.
        
        Override in subclasses to define common points.
        """
        pass
    
    def add_common_paths(self) -> None:
        """
        Add paths common to this block type.
        
        Override in subclasses to define common paths.
        """
        pass
    
    def start_piece(self) -> None:
        """Start defining the pattern piece."""
        self.builder.start_piece(self.piece_name)
    
    def end_piece(self) -> None:
        """Finish the current piece and add it to the pattern."""
        self.builder.end_piece()
    
    def get_measurement(self, name: str, default: Any = None) -> Any:
        """
        Get a measurement with optional default.
        
        Args:
            name: Measurement name
            default: Default value if measurement doesn't exist
            
        Returns:
            Measurement value or default
        """
        return self.measurements_system.get(name, default)


class GarmentBlock(PatternBlock):
    """
    Base class for full garment pattern blocks.
    
    This class manages the creation of multiple pattern pieces that make up a
    complete garment.
    """
    
    def __init__(
        self, 
        builder: PatternBuilder, 
        measurements: Dict[str, float],
        ease_fitting: bool = False
    ):
        """
        Initialize a garment block.
        
        Args:
            builder: The pattern builder instance
            measurements: Raw measurements dictionary
            ease_fitting: Whether to use ease fitting (looser fit)
        """
        # Use a placeholder piece name for the parent class
        super().__init__(builder, measurements, "_garment", ease_fitting)
        
        # Initialize piece blocks
        self.piece_blocks: List[PatternBlock] = []
        self.create_piece_blocks()
    
    def create_piece_blocks(self) -> None:
        """
        Create the individual pattern piece blocks.
        
        Override in subclasses to define the pieces of the garment.
        """
        pass
    
    def draft(self) -> None:
        """
        Draft all pieces of the garment.
        
        This implementation drafts each piece block in sequence.
        """
        for block in self.piece_blocks:
            block.draft()