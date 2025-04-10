"""
Hem Feature implementation for pattern drafting.

This module provides a HemFeature class that adds hems to pattern pieces,
correctly mirroring the original edge geometry for both straight and curved edges.
"""
from typing import Dict, List, Any, Optional, Union, Set, Tuple
import math

from patterns.pattern_engine.src.core.PatternFeature import PatternFeature, PatternFeatureRegistry
from patterns.pattern_engine.src.PatternBuilder import PatternBuilder
from patterns.pattern_engine.src.Pattern import Pattern
from patterns.pattern_engine.src.PatternPiece import PatternPiece
from patterns.pattern_engine.src.Point import Point
from patterns.pattern_engine.src.Line import Line
from patterns.pattern_engine.src.CurveWithPeak import Curve, CurveWithPeak


class HemFeature(PatternFeature):
    """
    Feature that adds a hem to pattern pieces.
    
    This feature adds a hem to specified pattern pieces that properly mirrors
    the original edge geometry, and optionally adds a fold line.
    """
    
    def __init__(
        self,
        hem_width: float = 2.0,
        fold_line: bool = True,
        piece_names: Optional[List[str]] = None,
        bottom_tolerance: float = 3.0,  # Tolerance for identifying bottom edges
        **kwargs
    ):
        """
        Initialize the hem feature.
        
        Args:
            hem_width: Width of the hem in cm
            fold_line: Whether to add a fold line
            piece_names: Names of pieces to apply the hem to (None for all)
            bottom_tolerance: Tolerance for identifying bottom points
            **kwargs: Additional options
        """
        super().__init__(kwargs)
        self.hem_width = hem_width
        self.fold_line = fold_line
        self.piece_names = piece_names
        self.bottom_tolerance = bottom_tolerance
    
    def apply(self, builder: PatternBuilder, pattern: Pattern) -> None:
        """
        Apply hem to specified pieces in the pattern.
        
        Args:
            builder: The PatternBuilder instance
            pattern: The pattern to modify
        """
        # If no specific pieces are specified, apply to all
        piece_names = self.piece_names or list(pattern.pieces.keys())
        
        for piece_name in piece_names:
            if piece_name not in pattern.pieces:
                continue
                
            piece = pattern.pieces[piece_name]
            self._add_hem_to_piece(builder, piece)
    
    def _add_hem_to_piece(self, builder: PatternBuilder, piece: PatternPiece) -> None:
        """
        Add hem to a specific piece.
        
        Args:
            builder: The PatternBuilder instance
            piece: The pattern piece to modify
        """
        # Save the current working piece
        current_piece = builder.current_piece
        
        # Switch to the target piece
        builder.current_piece = piece
        
        # Get the bottom-most points and segments
        min_point, max_point = piece.get_bounding_box()
        max_y = max_point.y
        
        # Identify bottom segments and points
        bottom_points = {}
        bottom_segments = []
        
        # First, find points that are near the bottom
        for name, point in piece.points.items():
            if abs(point.y - max_y) <= self.bottom_tolerance:
                bottom_points[name] = point
        
        # Then identify segments connecting these points
        for path_idx, path in enumerate(piece.paths):
            for segment_idx, segment in enumerate(path):
                if hasattr(segment, 'start') and hasattr(segment, 'end'):
                    # Find the point names for this segment
                    start_name = None
                    end_name = None
                    
                    for name, point in bottom_points.items():
                        # Match segment endpoints to named points
                        if abs(segment.start.x - point.x) < 0.01 and abs(segment.start.y - point.y) < 0.01:
                            start_name = name
                        if abs(segment.end.x - point.x) < 0.01 and abs(segment.end.y - point.y) < 0.01:
                            end_name = name
                    
                    # If we found both endpoints and they're both bottom points
                    if start_name and end_name:
                        bottom_segments.append({
                            'segment': segment,
                            'start_name': start_name,
                            'end_name': end_name,
                            'is_curve': isinstance(segment, Curve)
                        })
        
        # If no bottom segments found, we can't add a hem
        if not bottom_segments:
            builder.current_piece = current_piece
            return
        
        # Process each bottom segment to create hem
        for segment_data in bottom_segments:
            segment = segment_data['segment']
            start_name = segment_data['start_name']
            end_name = segment_data['end_name']
            is_curve = segment_data['is_curve']
            
            start_point = piece.get_point(start_name)
            end_point = piece.get_point(end_name)
            
            # Create hem points for this segment
            if is_curve:
                # Handle curved segments
                self._add_curved_hem(builder, segment, start_point, end_point, start_name, end_name)
            else:
                # Handle straight segments
                self._add_straight_hem(builder, segment, start_point, end_point, start_name, end_name)
        
        # Add fold line if requested
        if self.fold_line:
            # Find all bottom point names
            all_bottom_names = set()
            for segment in bottom_segments:
                all_bottom_names.add(segment['start_name'])
                all_bottom_names.add(segment['end_name'])
            
            # Sort points by x-coordinate
            sorted_points = sorted(list(all_bottom_names), key=lambda name: piece.get_point(name).x)
            
            if len(sorted_points) >= 2:
                leftmost = sorted_points[0]
                rightmost = sorted_points[-1]
                fold_start = piece.get_point(leftmost)
                fold_end = piece.get_point(rightmost)
                piece.fold_line = Line(fold_start, fold_end)
        
        # Restore original working piece
        builder.current_piece = current_piece
    
    def _add_straight_hem(
        self, 
        builder: PatternBuilder, 
        segment: Line, 
        start_point: Point, 
        end_point: Point,
        start_name: str,
        end_name: str
    ) -> None:
        """
        Add a straight hem segment.
        
        Args:
            builder: The PatternBuilder instance
            segment: The line segment to add a hem to
            start_point: Start point of the segment
            end_point: End point of the segment
            start_name: Name of the start point
            end_name: Name of the end point
        """
        # Calculate normal vector (perpendicular to the segment)
        dx = end_point.x - start_point.x
        dy = end_point.y - start_point.y
        
        # Length of the segment
        length = math.sqrt(dx*dx + dy*dy)
        if length < 0.0001:  # Avoid division by zero
            # Default direction (downward)
            normal_x, normal_y = 0, 1
        else:
            # Calculate the normal vector, ensuring it points "downward"
            normal_x = dy / length
            normal_y = -dx / length
            
            # If this normal points upward, reverse it
            if normal_y < 0:
                normal_x = -normal_x
                normal_y = -normal_y
        
        # Create hem points
        start_hem_name = f"{start_name}_hem"
        end_hem_name = f"{end_name}_hem"
        
        builder.add_point(
            start_hem_name,
            start_point.x + normal_x * self.hem_width,
            start_point.y + normal_y * self.hem_width
        )
        
        builder.add_point(
            end_hem_name,
            end_point.x + normal_x * self.hem_width,
            end_point.y + normal_y * self.hem_width
        )
        
        # Add connection lines
        builder.add_line_path([start_name, start_hem_name])
        builder.add_line_path([end_name, end_hem_name])
        builder.add_line_path([start_hem_name, end_hem_name])
    
    def _add_curved_hem(
        self, 
        builder: PatternBuilder, 
        segment: Curve, 
        start_point: Point, 
        end_point: Point,
        start_name: str,
        end_name: str
    ) -> None:
        """
        Add a curved hem segment.
        
        Args:
            builder: The PatternBuilder instance
            segment: The curve segment to add a hem to
            start_point: Start point of the segment
            end_point: End point of the segment
            start_name: Name of the start point
            end_name: Name of the end point
        """
        # For a curved segment, we need to:
        # 1. Find the control point
        # 2. Create a new control point for the hem curve
        # 3. Create start and end points for the hem curve
        # 4. Add connection lines to the original curve
        
        # Add the hem points
        start_hem_name = f"{start_name}_hem"
        end_hem_name = f"{end_name}_hem"
        
        # For the start and end points, we use local normals at those points
        # Get local tangent at the start point (first derivative of the curve)
        if hasattr(segment, 'control_point'):
            # This is a quadratic Bezier curve
            control_point = segment.control_point
            
            # Calculate normals at start and end points
            # For start point:
            dx1 = control_point.x - start_point.x
            dy1 = control_point.y - start_point.y
            length1 = math.sqrt(dx1*dx1 + dy1*dy1)
            if length1 > 0.0001:
                # Normal at start point (rotate tangent 90 degrees)
                normal1_x = dy1 / length1
                normal1_y = -dx1 / length1
                
                # Make sure it points downward
                if normal1_y < 0:
                    normal1_x = -normal1_x
                    normal1_y = -normal1_y
            else:
                normal1_x, normal1_y = 0, 1  # Default direction
            
            # For end point:
            dx2 = end_point.x - control_point.x
            dy2 = end_point.y - control_point.y
            length2 = math.sqrt(dx2*dx2 + dy2*dy2)
            if length2 > 0.0001:
                # Normal at end point
                normal2_x = dy2 / length2
                normal2_y = -dx2 / length2
                
                # Make sure it points downward
                if normal2_y < 0:
                    normal2_x = -normal2_x
                    normal2_y = -normal2_y
            else:
                normal2_x, normal2_y = 0, 1  # Default direction
            
            # Create the hem points
            builder.add_point(
                start_hem_name,
                start_point.x + normal1_x * self.hem_width,
                start_point.y + normal1_y * self.hem_width
            )
            
            builder.add_point(
                end_hem_name,
                end_point.x + normal2_x * self.hem_width,
                end_point.y + normal2_y * self.hem_width
            )
            
            # Create a control point for the hem curve
            # We'll offset the original control point similarly
            # Average the normals from the endpoints
            avg_normal_x = (normal1_x + normal2_x) / 2
            avg_normal_y = (normal1_y + normal2_y) / 2
            
            control_hem_name = f"{start_name}_{end_name}_control_hem"
            builder.add_point(
                control_hem_name,
                control_point.x + avg_normal_x * self.hem_width,
                control_point.y + avg_normal_y * self.hem_width
            )
            
            # Add connection lines
            builder.add_line_path([start_name, start_hem_name])
            builder.add_line_path([end_name, end_hem_name])
            
            # Create curved hem using the new control point
            builder.add_bezier_curve(start_hem_name, end_hem_name, 
                                    -segment.peak_value if hasattr(segment, 'peak_value') else 2.0, 
                                    segment.inflection_point if hasattr(segment, 'inflection_point') else 0.5)
        else:
            # If we can't determine the control point, fall back to a straight hem
            self._add_straight_hem(builder, segment, start_point, end_point, start_name, end_name)


# Register this feature with the registry
PatternFeatureRegistry.register("hem", HemFeature)