"""
Line segment implementation using Shapely.

This module replaces the original Line class with one based on Shapely,
while maintaining the same interface for compatibility.
"""
from typing import List, Tuple, Optional

from shapely.geometry import LineString

from .Point import Point


class Line:
    """
    Represents a line segment between two points using Shapely.

    This implementation wraps a Shapely LineString while maintaining
    the same interface as the original Line class.
    """

    def __init__(self, start: Point, end: Point):
        """Initialize a line segment between two points."""
        self.start = start
        self.end = end
        self._shapely_line = LineString([start.as_tuple(), end.as_tuple()])

    @property
    def shapely(self) -> LineString:
        """Get the underlying Shapely geometry."""
        return self._shapely_line

    def length(self) -> float:
        """Return the length of the line segment."""
        return self._shapely_line.length

    def direction(self) -> Point:
        """Return the direction vector of the line."""
        length = self.length()
        if length == 0:
            return Point(0, 0)
        dx = (self.end.x - self.start.x) / length
        dy = (self.end.y - self.start.y) / length
        return Point(dx, dy)

    def point_at_distance(self, distance: float) -> Point:
        """Return a point at the specified distance from the start along the line."""
        if distance <= 0:
            return Point(self.start.x, self.start.y)
        if distance >= self.length():
            return Point(self.end.x, self.end.y)

        # Use Shapely's interpolate function
        shapely_point = self._shapely_line.interpolate(distance)
        return Point(shapely_point.x, shapely_point.y)

    def perpendicular(self, point: Optional[Point] = None, length: float = 1.0) -> 'Line':
        """Create a perpendicular line from the specified point (default is start)."""
        if point is None:
            point = self.start

        direction = self.direction()
        perp_direction = Point(-direction.y, direction.x)

        end_point = Point(
            point.x + perp_direction.x * length,
            point.y + perp_direction.y * length
        )

        return Line(point, end_point)

    def midpoint(self) -> Point:
        """Return the midpoint of the line segment."""
        shapely_point = self._shapely_line.interpolate(0.5, normalized=True)
        return Point(shapely_point.x, shapely_point.y)

    def as_tuple_list(self) -> List[Tuple[float, float]]:
        """Return the line as a list of tuples."""
        return [self.start.as_tuple(), self.end.as_tuple()]

    def parallel_offset(self, distance: float, side: str = 'left') -> 'Line':
        """
        Create a parallel line offset by the specified distance.

        Args:
            distance: Distance to offset the line
            side: 'left' or 'right' side of the line

        Returns:
            New Line object representing the offset line
        """
        # Use Shapely's parallel_offset method
        offset_line = self._shapely_line.parallel_offset(distance, side, join_style=2)

        # Create a new Line from the offset LineString
        coords = list(offset_line.coords)
        if len(coords) >= 2:
            if side == 'right':
                # For 'right' offsets, the direction is often reversed, so flip if needed
                if self.start.distance_to(Point(coords[0][0], coords[0][1])) > self.start.distance_to(
                        Point(coords[-1][0], coords[-1][1])):
                    coords.reverse()

            return Line(Point(coords[0][0], coords[0][1]), Point(coords[1][0], coords[1][1]))

        # Fallback if Shapely's parallel_offset fails
        dir_point = self.direction()
        perp_vec = Point(-dir_point.y, dir_point.x)

        if side == 'right':
            perp_vec = Point(-perp_vec.x, -perp_vec.y)

        new_start = Point(self.start.x + perp_vec.x * distance, self.start.y + perp_vec.y * distance)
        new_end = Point(self.end.x + perp_vec.x * distance, self.end.y + perp_vec.y * distance)

        return Line(new_start, new_end)

    def intersection(self, other: 'Line') -> Optional[Point]:
        """
        Calculate the intersection point with another line.

        Args:
            other: Another Line object

        Returns:
            Point of intersection or None if lines are parallel
        """
        # Use Shapely's intersection method
        intersection = self._shapely_line.intersection(other.shapely)

        # Check if there's a valid intersection point
        if intersection.is_empty:
            return None

        if intersection.geom_type == 'Point':
            return Point(intersection.x, intersection.y)

        # Fallback to manual calculation if Shapely gives unexpected result
        p1, p2 = self.start, self.end
        p3, p4 = other.start, other.end

        dx1 = p2.x - p1.x
        dy1 = p2.y - p1.y
        dx2 = p4.x - p3.x
        dy2 = p4.y - p3.y

        denominator = dx1 * dy2 - dy1 * dx2
        if abs(denominator) < 1e-10:
            return None  # Lines are parallel

        dx3 = p1.x - p3.x
        dy3 = p1.y - p3.y

        t1 = (dx2 * dy3 - dy2 * dx3) / denominator

        intersection_x = p1.x + t1 * dx1
        intersection_y = p1.y + t1 * dy1

        return Point(intersection_x, intersection_y)
