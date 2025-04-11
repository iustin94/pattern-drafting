"""
Hem Feature implementation for pattern drafting.

This module provides a HemFeature class that adds hems to pattern pieces,
correctly mirroring the original edge geometry for any edge of the pattern.
"""
from typing import Dict, List, Optional
import math

from patterns.pattern_engine.src.core.PatternFeature import PatternFeature, PatternFeatureRegistry
from patterns.pattern_engine.src.core.PatternBuilder import PatternBuilder
from patterns.pattern_engine.src.core.Pattern import Pattern
from patterns.pattern_engine.src.core.PatternPiece import PatternPiece
from patterns.pattern_engine.src.core.Point import Point
from patterns.pattern_engine.src.core.Line import Line
from patterns.pattern_engine.src.core.Curve import Curve, CurveWithPeak


class HemFeature(PatternFeature):
    """
    Feature that adds a hem to pattern pieces.

    This feature adds a hem to specified edges of pattern pieces by properly
    mirroring the edge geometry and connecting edges, regardless of orientation.
    """

    def __init__(
        self,
        hem_width: float = 2.0,
        fold_line: bool = True,
        piece_names: Optional[List[str]] = None,
        edge_names: Optional[List[str]] = None,  # New parameter for specific edges
        **kwargs
    ):
        """
        Initialize the hem feature.

        Args:
            hem_width: Width of the hem in cm
            fold_line: Whether to add a fold line
            piece_names: Names of pieces to apply the hem to (None for all)
            edge_names: Names of specific edges to hem (None for all edges)
            **kwargs: Additional options
        """
        super().__init__(kwargs)
        self.hem_width = hem_width
        self.fold_line = fold_line
        self.piece_names = piece_names
        self.edge_names = edge_names

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

        # Build a graph of connected segments
        segment_graph = self._build_segment_graph(piece)

        # If no segments found, we can't add a hem
        if not segment_graph:
            builder.current_piece = current_piece
            return

        # Process each segment in the graph
        self._process_hem_segments(builder, piece, segment_graph)

        # Add fold line if requested
        if self.fold_line:
            self._add_fold_lines(builder, piece, segment_graph)

        # Restore original working piece
        builder.current_piece = current_piece

    def _add_fold_lines(self, builder: PatternBuilder, piece: PatternPiece, graph: Dict) -> None:
        fold_segments = []
        for segment_data in graph["segments"].values():
            if segment_data["hem_added"]:
                # Use the original segment as the fold line
                fold_segments.append(segment_data["segment"])
        piece.fold_segments = fold_segments  # Replace with your framework's fold line logic

    def _build_segment_graph(self, piece: PatternPiece) -> Dict:
        """
        Build a graph of connected segments in the pattern piece using its paths.

        Args:
            piece: The pattern piece containing paths and points.

        Returns:
            Dictionary with segment info and connections.
        """
        segments = {}
        points = {name: {'point': point, 'connected_segments': []} for name, point in piece.points.items()}

        segment_id = 0
        for path_idx, path in enumerate(piece.paths):
            for segment_idx, segment in enumerate(path):
                if not (hasattr(segment, 'start') and hasattr(segment, 'end')):
                    continue  # Skip if segment doesn't have start/end points

                # Find names for the segment's endpoints
                start_name = self._find_point_name(segment.start, points)
                end_name = self._find_point_name(segment.end, points)

                if not (start_name and end_name):
                    continue  # Skip segments without both endpoints in named points

                # Apply edge filtering if edge_names is specified
                if self.edge_names is not None:
                    edge = f"{start_name}_{end_name}"
                    reverse_edge = f"{end_name}_{start_name}"
                    if edge not in self.edge_names and reverse_edge not in self.edge_names:
                        continue

                # Register the segment
                segment_key = f"segment_{segment_id}"
                segments[segment_key] = {
                    'segment': segment,
                    'start_name': start_name,
                    'end_name': end_name,
                    'start_point': segment.start,
                    'end_point': segment.end,
                    'is_curve': isinstance(segment, Curve),
                    'path_idx': path_idx,
                    'segment_idx': segment_idx,
                    'hem_added': False
                }
                segment_id += 1

                # Update connections in points
                points[start_name]['connected_segments'].append(segment_key)
                points[end_name]['connected_segments'].append(segment_key)

        return {'segments': segments, 'points': points}

    def _find_point_name(self, target_point, points_dict: Dict) -> Optional[str]:
        """
        Find the name of a point in points_dict within a tolerance of 0.01.

        Args:
            target_point: The point to find.
            points_dict: Dictionary of named points.

        Returns:
            Name of the matching point or None if not found.
        """
        name = None
        for point_name, data in points_dict.items():
            point = data['point']
            if (abs(point.x - target_point.x) < 0.01 and
                    abs(point.y - target_point.y) < 0.01):
                name = point_name  # Last match in iteration order is kept
        return name

    def _process_hem_segments(self, builder: PatternBuilder, piece: PatternPiece, graph: Dict) -> None:
        """
        Process each segment to add a hem.

        Args:
            builder: The PatternBuilder instance
            piece: The pattern piece
            graph: The segment graph
        """
        segments = graph['segments']
        points = graph['points']

        # Create hem for each segment
        for segment_key, segment_data in segments.items():
            if segment_data['hem_added']:
                continue

            # Mark segment as having been processed
            segment_data['hem_added'] = True

            # Get the segment and its endpoints
            segment = segment_data['segment']
            start_name = segment_data['start_name']
            end_name = segment_data['end_name']
            start_point = segment_data['start_point']
            end_point = segment_data['end_point']

            # Find connecting segments at each endpoint
            start_connected = self._find_connecting_segments(segment_key, start_name, points, segments)
            end_connected = self._find_connecting_segments(segment_key, end_name, points, segments)

            # Create hem based on segment type and connections
            if segment_data['is_curve']:
                self._add_curved_hem(builder, piece, segment, start_name, end_name,
                                     start_point, end_point, start_connected, end_connected)
            else:
                self._add_straight_hem(builder, piece, segment, start_name, end_name,
                                      start_point, end_point, start_connected, end_connected)

    def _find_connecting_segments(self, current_segment: str, point_name: str,
                                  points: Dict, segments: Dict) -> List[Dict]:
        """
        Find segments that connect to a specific point, excluding the current segment.

        Args:
            current_segment: Key of the current segment
            point_name: Name of the connection point
            points: Dictionary of points data
            segments: Dictionary of segments data

        Returns:
            List of connecting segment data
        """
        connected = []

        # Get all segments connected to this point
        for segment_key in points[point_name]['connected_segments']:
            if segment_key != current_segment:
                connected.append(segments[segment_key])

        return connected

    def _add_straight_hem(self, builder: PatternBuilder, piece: PatternPiece,
                          segment: Line, start_name: str, end_name: str,
                          start_point: Point, end_point: Point,
                          start_connected: List[Dict], end_connected: List[Dict]) -> None:
        """
        Add a straight hem with appropriate mirroring of connected edges.

        Args:
            builder: The PatternBuilder instance
            piece: The pattern piece
            segment: The line segment to hem
            start_name: Name of start point
            end_name: Name of end point
            start_point: Start point of segment
            end_point: End point of segment
            start_connected: Segments connected to start point
            end_connected: Segments connected to end point
        """
        # Calculate normal vector (perpendicular to the segment)
        dx = end_point.x - start_point.x
        dy = end_point.y - start_point.y

        # Length of the segment
        length = math.sqrt(dx*dx + dy*dy)
        if length < 0.0001:  # Avoid division by zero
            return

        # Calculate unit normal vector
        normal_x = dy / length
        normal_y = -dx / length

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

        # Get actual hem points
        start_hem_point = piece.get_point(start_hem_name)
        end_hem_point = piece.get_point(end_hem_name)

        # Add connection lines
        builder.add_line_path([start_name, start_hem_name])
        builder.add_line_path([end_name, end_hem_name])

        # Now handle the connecting edges
        self._mirror_connected_edges(builder, piece,
                                    start_point, start_hem_point, start_connected,
                                    normal_x, normal_y, start_name)

        self._mirror_connected_edges(builder, piece,
                                    end_point, end_hem_point, end_connected,
                                    normal_x, normal_y, end_name)

        # Add the bottom hem line
        builder.add_line_path([start_hem_name, end_hem_name])

    def _mirror_connected_edges(self, builder: PatternBuilder, piece: PatternPiece,
                               corner_point: Point, hem_point: Point, connected_segments: List[Dict],
                               normal_x: float, normal_y: float, corner_name: str) -> None:
        """
        Mirror connecting edges at corners to create proper hem transitions.

        Args:
            builder: The PatternBuilder instance
            piece: The pattern piece
            corner_point: The corner point
            hem_point: The corresponding hem point
            connected_segments: List of segments connected to this corner
            normal_x, normal_y: Normal vector components
            corner_name: Name of the corner point
        """
        if not connected_segments:
            return

        # For each connecting segment, create a mirrored version
        for connected in connected_segments:
            other_end = connected['end_name'] if connected['start_name'] == corner_name else connected['start_name']
            other_point = connected['end_point'] if connected['start_name'] == corner_name else connected['start_point']

            # Create a vector for the connected edge
            edge_dx = other_point.x - corner_point.x
            edge_dy = other_point.y - corner_point.y

            # Mirror this vector across the normal
            # Project the edge vector onto the normal
            dot_product = edge_dx * normal_x + edge_dy * normal_y

            # Calculate mirrored vector components
            mirrored_dx = edge_dx - 2 * dot_product * normal_x
            mirrored_dy = edge_dy - 2 * dot_product * normal_y

            # Calculate the mirrored end point
            mirrored_end_x = hem_point.x + mirrored_dx
            mirrored_end_y = hem_point.y + mirrored_dy

            # Add the mirrored point and connection
            mirrored_end_name = f"{corner_name}_{other_end}_mirror"
            builder.add_point(mirrored_end_name, mirrored_end_x, mirrored_end_y)

            # Add the connecting line
            builder.add_line_path([f"{corner_name}_hem", mirrored_end_name])

            # If the connected segment is a curve, mirror it properly
            if connected['is_curve'] and isinstance(connected['segment'], Curve):
                # Inside _mirror_connected_edges method:
                self._mirror_curve(builder, piece, connected['segment'], corner_point, hem_point,
                                   other_point, mirrored_end_name, normal_x, normal_y, corner_name)

    def _mirror_curve(self, builder: PatternBuilder, piece: PatternPiece,
                      curve: Curve, corner_point: Point, hem_point: Point,
                      other_point: Point, mirrored_end_name: str,
                      normal_x: float, normal_y: float, corner_name: str) -> None:
        """
        Mirror a curve for a curved corner of a hem.

        Args:
            builder: The PatternBuilder instance
            piece: The pattern piece
            curve: The curve to mirror
            corner_point: The corner point
            hem_point: The corresponding hem point
            other_point: The other end of the original curve
            mirrored_end_name: Name of the mirrored end point
            normal_x, normal_y: Normal vector components
            corner_name: Name of the corner point
        """
        # If this is a quadratic Bezier curve with a control point
        if hasattr(curve, 'control_point'):
            control_point = curve.control_point

            # Calculate midpoint of the original curve
            original_midpoint = Point(
                (corner_point.x + 2 * control_point.x + other_point.x) / 4,
                (corner_point.y + 2 * control_point.y + other_point.y) / 4
            )

            # Calculate tangent at midpoint (direction of the original curve)
            tangent_x = other_point.x - corner_point.x
            tangent_y = other_point.y - corner_point.y

            # Calculate normal direction (perpendicular to tangent)
            mid_normal_x = -tangent_y
            mid_normal_y = tangent_x
            norm = math.sqrt(mid_normal_x ** 2 + mid_normal_y ** 2)
            if norm > 0.0001:
                mid_normal_x /= norm
                mid_normal_y /= norm
            else:
                mid_normal_x, mid_normal_y = normal_x, normal_y  # Fallback to original normal

            # Offset midpoint by hem width
            midpoint_hem = Point(
                original_midpoint.x + mid_normal_x * self.hem_width,
                original_midpoint.y + mid_normal_y * self.hem_width
            )

            # Calculate mirrored control point using the midpoint offset
            # The new curve should pass through midpoint_hem
            start_hem = hem_point
            end_hem = piece.get_point(mirrored_end_name)

            # Formula for quadratic Bezier control point to pass through midpoint_hem:
            # midpoint_hem = (start_hem + 2*control_hem + end_hem)/4
            # Solving for control_hem: control_hem = (4*midpoint_hem - start_hem - end_hem)/2
            control_hem_x = (4 * midpoint_hem.x - start_hem.x - end_hem.x) / 2
            control_hem_y = (4 * midpoint_hem.y - start_hem.y - end_hem.y) / 2

            control_hem_name = f"{corner_name}_control_mirror"
            builder.add_point(control_hem_name, control_hem_x, control_hem_y)

            # Create the mirrored curve using the calculated control point
            builder.add_bezier_curve_with_reference(
                f"{corner_name}_hem", mirrored_end_name,
                control_hem_name, curve.max_deviation(corner_point, other_point)
            )
        elif isinstance(curve, CurveWithPeak) and hasattr(curve, 'peak_value'):
            # For CurveWithPeak, create a mirrored curve with negative peak value
            peak_value = curve.peak_value
            inflection_point = curve.inflection_point if hasattr(curve, 'inflection_point') else 0.5
            builder.add_bezier_curve(f"{corner_name}_hem", mirrored_end_name,
                                     -peak_value, inflection_point)
        else:
            # Fallback for other curve types
            builder.add_line_path([f"{corner_name}_hem", mirrored_end_name])

    def _add_curved_hem(
            self,
            builder: PatternBuilder,
            piece: PatternPiece,
            curve: Curve,
            start_name: str,
            end_name: str,
            start_point: Point,
            end_point: Point,
            start_connected: List[Dict],
            end_connected: List[Dict]
    ) -> None:
        """
        Add a curved hem that mirrors the original curve's shape.

        Args:
            builder: PatternBuilder instance
            piece: Pattern piece to modify
            curve: Original curve segment to hem
            start_name: Name of the start point
            end_name: Name of the end point
            start_point: Start point of the curve
            end_point: End point of the curve
            start_connected: Segments connected to the start point
            end_connected: Segments connected to the end point
        """
        if not hasattr(curve, "control_point"):
            # Fallback to straight hem if no control point (e.g., basic Line)
            self._add_straight_hem(
                builder, piece, curve, start_name, end_name,
                start_point, end_point, start_connected, end_connected
            )
            return

            # Calculate average normal direction for the entire curve
            dx = end_point.x - start_point.x
            dy = end_point.y - start_point.y
            avg_normal = Point(-dy, dx).normalize()  # Perpendicular to overall direction

            # Offset start and end points
            start_hem_name = f"{start_name}_hem"
            end_hem_name = f"{end_name}_hem"
            builder.add_point(start_hem_name,
                              start_point.x + avg_normal.x * self.hem_width,
                              start_point.y + avg_normal.y * self.hem_width)
            builder.add_point(end_hem_name,
                              end_point.x + avg_normal.x * self.hem_width,
                              end_point.y + avg_normal.y * self.hem_width)

            # Offset control point by the same normal
            control_hem = Point(
                curve.control_point.x + avg_normal.x * self.hem_width,
                curve.control_point.y + avg_normal.y * self.hem_width
            )
            control_hem_name = f"{start_name}_{end_name}_control_hem"
            builder.add_point(control_hem_name, control_hem.x, control_hem.y)

            # Add the curved hem
            builder.add_bezier_curve(start_hem_name, end_hem_name, control_hem_name)

    def _create_hem_point(
            self,
            builder: PatternBuilder,
            piece: PatternPiece,
            original_point: Point,
            normal: Point,
            point_name: str,
            suffix: str
    ) -> Point:
        """Create a hem point offset from the original point."""
        hem_name = f"{point_name}_hem_{suffix}"
        builder.add_point(
            hem_name,
            original_point.x + normal.x * self.hem_width,
            original_point.y + normal.y * self.hem_width
        )
        return piece.get_point(hem_name)

    def _adjust_normal_direction(
            self,
            point: Point,
            midpoint: Point,
            normal: Point
    ) -> Point:
        """Ensure normal points outward relative to the curve."""
        # Vector from point to midpoint
        to_mid = Point(midpoint.x - point.x, midpoint.y - point.y)
        dot = to_mid.x * normal.x + to_mid.y * normal.y
        return normal if dot > 0 else normal * -1  # Flip direction if inward

# Register this feature with the registry
PatternFeatureRegistry.register("hem", HemFeature)
