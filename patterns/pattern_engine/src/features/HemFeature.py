"""
Hem Feature implementation for pattern drafting.

This module provides a HemFeature class that adds hems to pattern pieces,
correctly mirroring the original edge geometry for any edge of the pattern.
"""
from typing import Dict, List, Optional, Set, Tuple, Union
import math

from ..core.PatternFeatureRegistry import PatternFeatureRegistry
from ..core.PatternBuilder import PatternBuilder
from ..core.Pattern import Pattern
from ..core.PatternPiece import PatternPiece
from ..core.Point import Point
from ..core.Line import Line
from ..core.Curve import Curve, CurveWithPeak, CurveWithReference


class HemFeature:
    """
    Feature that adds a hem to pattern pieces.
    """

    def __init__(
            self,
            hem_width: float = 2.0,
            fold_line: bool = True,
            piece_names: Optional[List[str]] = None,
            bottom_tolerance: float = 3.0,  # Tolerance for identifying bottom edges
            **options
    ):
        """
        Initialize the hem feature.

        Args:
            hem_width: Width of the hem in cm
            fold_line: Whether to add a fold line
            piece_names: Names of pieces to apply the hem to (None for all)
            bottom_tolerance: Tolerance for identifying bottom points
            **options: Additional options
        """
        self.hem_width = hem_width
        self.fold_line = fold_line
        self.piece_names = piece_names
        self.bottom_tolerance = bottom_tolerance
        self.options = options

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

        # Identify bottom points that are near the bottom edge
        bottom_points = {}
        for name, point in piece.points.items():
            if abs(point.y - max_y) <= self.bottom_tolerance:
                bottom_points[name] = point

        # Create hem points for each bottom point
        for name, point in bottom_points.items():
            hem_point_name = f"{name}_hem"
            builder.add_point(
                hem_point_name,
                point.x,  # Same x-coordinate
                point.y + self.hem_width  # Offset y by hem width
            )

        # Now build a graph of all connections
        connections = {}
        for path in piece.paths:
            for segment in path:
                if hasattr(segment, 'start') and hasattr(segment, 'end'):
                    start_name = None
                    end_name = None
                    
                    for name, point in piece.points.items():
                        if segment.start.distance_to(point) < 0.01:
                            start_name = name
                        if segment.end.distance_to(point) < 0.01:
                            end_name = name
                    
                    if start_name and end_name:
                        # Store the connection
                        if start_name not in connections:
                            connections[start_name] = []
                        if end_name not in connections:
                            connections[end_name] = []
                        
                        # Each connection stores the segment and the point it connects to
                        connections[start_name].append({
                            'segment': segment,
                            'connects_to': end_name
                        })
                        
                        connections[end_name].append({
                            'segment': segment,
                            'connects_to': start_name
                        })

        # Find the bottom segments - segments where both endpoints are bottom points
        bottom_segments = []
        processed_pairs = set()
        
        for point_name in bottom_points:
            if point_name not in connections:
                continue
                
            for connection in connections[point_name]:
                other_point = connection['connects_to']
                
                if other_point in bottom_points:
                    # This is a bottom segment
                    pair = tuple(sorted([point_name, other_point]))
                    
                    if pair not in processed_pairs:
                        bottom_segments.append({
                            'start': point_name,
                            'end': other_point,
                            'segment': connection['segment']
                        })
                        processed_pairs.add(pair)

        # For each bottom point, find adjacent segments for mirroring
        for point_name in bottom_points:
            if point_name not in connections:
                continue
                
            # Get all connected points that are NOT bottom points
            adjacent_connections = [conn for conn in connections[point_name] 
                                    if conn['connects_to'] not in bottom_points]
            
            # If there are any adjacent connections, use the first one for mirroring
            if adjacent_connections:
                adjacent_segment = adjacent_connections[0]['segment']
                connects_to = adjacent_connections[0]['connects_to']
                
                # Add a mirrored connection between the point and its hem point
                self._add_mirrored_vertical_connection(
                    builder, 
                    point_name, 
                    f"{point_name}_hem", 
                    adjacent_segment, 
                    piece.get_point(point_name), 
                    piece.get_point(connects_to)
                )
            else:
                # No adjacent connections, just use a straight line
                builder.add_line_path([point_name, f"{point_name}_hem"])

        # Connect the hem points horizontally
        for segment in bottom_segments:
            start = segment['start']
            end = segment['end']
            original_segment = segment['segment']
            
            # Connect the corresponding hem points
            start_hem = f"{start}_hem"
            end_hem = f"{end}_hem"
            
            # Check if the original segment is a curve
            if isinstance(original_segment, Curve):
                if isinstance(original_segment, CurveWithPeak) and hasattr(original_segment, 'peak_value'):
                    # Mirror the bezier curve with the same parameters
                    peak_value = original_segment.peak_value
                    inflection = getattr(original_segment, 'inflection_point', 0.5)
                    builder.add_bezier_curve(start_hem, end_hem, peak_value, inflection)
                else:
                    # For other curve types, use a line as fallback
                    builder.add_line_path([start_hem, end_hem])
            else:
                # For straight segments, use a straight line
                builder.add_line_path([start_hem, end_hem])

        # Add fold line if requested
        if self.fold_line and bottom_points:
            # Sort points by x-coordinate
            sorted_points = sorted(list(bottom_points.keys()), 
                                  key=lambda name: piece.get_point(name).x)
            
            if len(sorted_points) >= 2:
                leftmost = sorted_points[0]
                rightmost = sorted_points[-1]
                fold_start = piece.get_point(leftmost)
                fold_end = piece.get_point(rightmost)
                piece.fold_line = Line(fold_start, fold_end)

        # Restore original working piece
        builder.current_piece = current_piece

    def _add_mirrored_vertical_connection(
            self,
            builder: PatternBuilder,
            original_point_name: str,
            hem_point_name: str,
            adjacent_segment,
            original_point: Point,
            adjacent_point: Point
    ) -> None:
        """
        Add a vertical connection that mirrors the properties of an adjacent segment.
        
        Args:
            builder: The PatternBuilder instance
            original_point_name: Name of the original point
            hem_point_name: Name of the hem point
            adjacent_segment: Segment to mirror
            original_point: The original point coordinates
            adjacent_point: The adjacent point coordinates
        """
        # Check if the adjacent segment is a curve
        if isinstance(adjacent_segment, Curve):
            if isinstance(adjacent_segment, CurveWithPeak) and hasattr(adjacent_segment, 'peak_value'):
                # Determine the direction of the curve
                # This helps us mirror properly
                dx = adjacent_point.x - original_point.x
                
                # Calculate an appropriate peak value for the mirrored vertical connection
                # For a proper mirror, we invert the sign if the curve is going leftward
                # The magnitude is scaled to work well for a vertical connection
                original_peak = adjacent_segment.peak_value
                
                # Adjust sign based on the horizontal direction of the original curve
                mirrored_peak = -original_peak if dx < 0 else original_peak
                
                # Get the inflection point or use default
                inflection = getattr(adjacent_segment, 'inflection_point', 0.5)
                
                # Create the bezier curve for the vertical connection
                builder.add_bezier_curve(original_point_name, hem_point_name, mirrored_peak, inflection)
                return
                
        # Default to a straight line if not a supported curve type
        builder.add_line_path([original_point_name, hem_point_name])


# Register this feature with a registry
PatternFeatureRegistry.register("hem", HemFeature)