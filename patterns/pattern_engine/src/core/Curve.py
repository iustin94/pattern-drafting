"""
Curve implementation using Shapely.

This module replaces the original Curve classes with ones based on Shapely,
while maintaining the same interface for compatibility.
"""
import math
import numpy as np
from typing import Tuple, List

from shapely.geometry import LineString

from .Point import Point


class Curve:
    """
    Represents a quadratic Bezier curve using Shapely LineString approximation.

    This implementation approximates a quadratic Bezier curve with a Shapely
    LineString for compatibility with Shapely's geometric operations.
    """

    def __init__(self, start_point: Point, end_point: Point, control_point: Point):
        """Initialize a quadratic Bezier curve."""
        self.start_point = start_point
        self.end_point = end_point
        self.control_point = control_point

        # Create a discretized LineString to approximate the Bezier curve
        points = self.discretize(30)
        coords = [p.as_tuple() for p in points]
        self._shapely_curve = LineString(coords)

    @property
    def shapely(self) -> LineString:
        """Get the underlying Shapely geometry."""
        return self._shapely_curve

    def bezier_point(self, t: float) -> Point:
        """
        Return a point on the Bezier curve at parameter t (0-1).

        Uses quadratic Bezier curve formula.
        """
        x = (1 - t) ** 2 * self.start_point.x + \
            2 * (1 - t) * t * self.control_point.x + \
            t ** 2 * self.end_point.x

        y = (1 - t) ** 2 * self.start_point.y + \
            2 * (1 - t) * t * self.control_point.y + \
            t ** 2 * self.end_point.y

        return Point(x, y)

    @property
    def midpoint(self) -> Point:
        """Get the midpoint of the curve (t=0.5)"""
        return self.bezier_point(0.5)

    def discretize(self, num_points: int = 20) -> List[Point]:
        """
        Return a list of points that discretize the curve.

        Args:
            num_points: Number of points to generate along the curve

        Returns:
            List of points on the curve
        """
        return [self.bezier_point(t / (num_points - 1)) for t in range(num_points)]

    def as_tuple_list(self, num_points: int = 20) -> List[Tuple[float, float]]:
        """
        Return the curve as a list of tuples.

        Args:
            num_points: Number of points to generate along the curve

        Returns:
            List of (x, y) tuples representing points on the curve
        """
        return [p.as_tuple() for p in self.discretize(num_points)]

    def max_deviation(self, start_point: Point, end_point: Point) -> float:
        """
        Calculate the maximum deviation from the straight line.

        Returns:
            Maximum distance from the curve to the straight line
        """
        # Create a straight line between start and end points
        straight_line = LineString([start_point.as_tuple(), end_point.as_tuple()])

        # Check each point along the curve to find maximum distance
        max_dist = 0
        for t in np.linspace(0, 1, 100):
            point = self.bezier_point(t)
            dist = straight_line.distance(point.shapely)
            max_dist = max(max_dist, dist)

        return max_dist

    def length(self) -> float:
        """Calculate the length of the curve."""
        return self._shapely_curve.length

    def parallel_offset(self, distance: float, side: str = 'left') -> 'Curve':
        """
        Create a parallel curve offset by the specified distance.

        Args:
            distance: Distance to offset the curve
            side: 'left' or 'right' side of the curve

        Returns:
            New Curve object representing the offset curve
        """
        # Use Shapely's parallel_offset method on the LineString approximation
        offset_curve = self._shapely_curve.parallel_offset(distance, side, join_style=2)

        # Extract points from the offset curve to create control points
        if offset_curve.geom_type != 'LineString' or len(offset_curve.coords) < 3:
            # Fallback if Shapely's parallel_offset fails to give a good curve
            # This is a simple approximation that works for most cases
            normal_vec = self._compute_normal_vector(side)

            new_start = Point(
                self.start_point.x + normal_vec[0].x * distance,
                self.start_point.y + normal_vec[0].y * distance
            )

            new_control = Point(
                self.control_point.x + normal_vec[1].x * distance,
                self.control_point.y + normal_vec[1].y * distance
            )

            new_end = Point(
                self.end_point.x + normal_vec[2].x * distance,
                self.end_point.y + normal_vec[2].y * distance
            )
        else:
            # Use the offset curve to create a new Bezier curve
            coords = list(offset_curve.coords)

            # For a good Bezier approximation, we need to choose good control points
            # Simple approach: use the middle point as control point
            new_start = Point(coords[0][0], coords[0][1])
            new_end = Point(coords[-1][0], coords[-1][1])

            # Find the middle point (approximately)
            mid_idx = len(coords) // 2
            mid_point = Point(coords[mid_idx][0], coords[mid_idx][1])

            # Compute control point that would give this middle point
            # Using the formula for quadratic Bezier midpoint: midpoint = 0.25*start + 0.5*control + 0.25*end
            new_control = Point(
                2 * mid_point.x - 0.25 * new_start.x - 0.25 * new_end.x,
                2 * mid_point.y - 0.25 * new_start.y - 0.25 * new_end.y
            )

        return Curve(new_start, new_end, new_control)

    def _compute_normal_vector(self, side: str = 'left') -> List[Point]:
        """
        Compute normal vectors at the start, control, and end points.

        Args:
            side: 'left' or 'right' side of the curve

        Returns:
            List of normal vectors as Points
        """
        # Calculate tangent at the start point (t=0)
        t0_tangent = Point(
            2 * (self.control_point.x - self.start_point.x),
            2 * (self.control_point.y - self.start_point.y)
        )

        # Calculate tangent at the middle point (t=0.5)
        t05_tangent = Point(
            self.end_point.x - self.start_point.x,  # Simplified formula for t=0.5
            self.end_point.y - self.start_point.y
        )

        # Calculate tangent at the end point (t=1)
        t1_tangent = Point(
            2 * (self.end_point.x - self.control_point.x),
            2 * (self.end_point.y - self.control_point.y)
        )

        # Normalize and create normal vectors
        normals = []
        for tangent in [t0_tangent, t05_tangent, t1_tangent]:
            length = math.sqrt(tangent.x ** 2 + tangent.y ** 2)
            if length > 0.0001:
                # Normal vector (perpendicular to tangent)
                normal = Point(-tangent.y / length, tangent.x / length)

                # Flip direction if needed
                if side == 'right':
                    normal = Point(-normal.x, -normal.y)

                normals.append(normal)
            else:
                # If tangent is very small, just use a default normal
                normal = Point(0, 1) if side == 'left' else Point(0, -1)
                normals.append(normal)

        return normals


class CurveWithPeak(Curve):
    """
    Represents a curve defined by two points, with a specific peak offset.

    The curve will touch exactly the specified peak value offset from
    the straight line between start and end points.
    """

    def __init__(self, start_point: Point, end_point: Point, peak_value: float, inflection_point: float = 0.5):
        """
        Initialize the curve.

        Args:
            start_point: The starting point of the curve
            end_point: The ending point of the curve
            peak_value: The exact offset distance the curve will touch
            inflection_point: The point (0-1) where the curve has maximum curvature (default: 0.5)
        """
        if not (0 <= inflection_point <= 1):
            raise ValueError("Inflection point must be between 0 and 1")

        self.start_point = start_point
        self.end_point = end_point
        self.peak_value = peak_value
        self.inflection_point = inflection_point

        # Calculate the control point to achieve the specified peak
        control_point = self._calculate_precise_control_point()

        super().__init__(start_point, end_point, control_point)

    def _calculate_precise_control_point(self) -> Point:
        """
        Calculate the control point ensuring:
        1. A valid Bezier curve exists
        2. The curve touches the specified peak value
        3. The inflection point influences the curve's position
        """
        # Calculate the vector from start to end point
        dx = self.end_point.x - self.start_point.x
        dy = self.end_point.y - self.start_point.y

        # Calculate the midpoint
        midpoint_x = (self.start_point.x + self.end_point.x) / 2
        midpoint_y = (self.start_point.y + self.end_point.y) / 2

        # Find the perpendicular vector (rotate 90 degrees)
        perp_dx, perp_dy = -dy, dx

        # Normalize the perpendicular vector
        perp_length = math.sqrt(perp_dx ** 2 + perp_dy ** 2)
        if perp_length > 0:
            normalized_perp_x = perp_dx / perp_length
            normalized_perp_y = perp_dy / perp_length
        else:
            normalized_perp_x, normalized_perp_y = 0, 0

        # Map inflection point from [0, 1] to [-1, 1]
        position_shift = (self.inflection_point - 0.5) * 2

        # Calculate the control point
        # Ensure the control point is always outside the line connecting start and end
        control_x = midpoint_x + normalized_perp_x * self.peak_value * 2
        control_y = midpoint_y + normalized_perp_y * self.peak_value * 2

        # Apply additional shift based on inflection point
        shift_x = dx * position_shift * 0.5
        shift_y = dy * position_shift * 0.5

        # Adjust the control point with the shift
        control_x += shift_x
        control_y += shift_y

        return Point(control_x, control_y)


class CurveWithReference(Curve):
    """
    Represents a quadratic Bezier curve shaped to maintain a specific relationship
    to an external reference point.

    The curve is constructed such that its midpoint reaches the specified distance
    from the reference point along the line connecting the curve's midpoint to the reference.
    """

    def __init__(self, start_point: Point, end_point: Point, reference_point: Point, target_distance: float):
        """
        Initialize a curve between two points that curves relative to a reference point.

        Args:
            start_point: Starting point of the curve (A)
            end_point: Ending point of the curve (B)
            reference_point: External reference point (C) that influences the curve shape
            target_distance: Distance the curve's midpoint should maintain from C
        """
        self.start_point = start_point
        self.end_point = end_point
        self.reference_point = reference_point
        self.target_distance = target_distance

        # Calculate the control point to achieve the desired curve shape
        control_point = self._calculate_control_point()

        super().__init__(start_point, end_point, control_point)

    def _calculate_control_point(self) -> Point:
        """Calculate control point to achieve desired distance from reference point."""
        # Calculate midpoint between start and end
        midpoint = Point(
            (self.start_point.x + self.end_point.x) / 2,
            (self.start_point.y + self.end_point.y) / 2
        )

        # Vector from midpoint to reference point
        dx = self.reference_point.x - midpoint.x
        dy = self.reference_point.y - midpoint.y
        ref_distance = math.hypot(dx, dy)

        if ref_distance < 0.0001:
            raise ValueError("Reference point coincides with curve midpoint")

        # Calculate adjustment ratio based on target distance
        ratio = 1 - (self.target_distance / ref_distance)

        # Calculate desired curve midpoint position
        curve_mid = Point(
            midpoint.x + dx * ratio,
            midpoint.y + dy * ratio
        )

        # Calculate control point using Bezier midpoint formula:
        # curve_mid = 0.25*start + 0.5*control + 0.25*end
        control = Point(
            2 * curve_mid.x - 0.5 * self.start_point.x - 0.5 * self.end_point.x,
            2 * curve_mid.y - 0.5 * self.start_point.y - 0.5 * self.end_point.y
        )

        return control