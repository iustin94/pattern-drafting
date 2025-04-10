from typing import List, Tuple, Optional

from patterns.pattern_engine.src.Point import Point


class Line:
    """Represents a line segment between two points."""

    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

    def length(self) -> float:
        """Return the length of the line segment."""
        return self.start.distance_to(self.end)

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
        direction = self.direction()
        return Point(
            self.start.x + direction.x * distance,
            self.start.y + direction.y * distance
        )

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
        return Point(
            (self.start.x + self.end.x) / 2,
            (self.start.y + self.end.y) / 2
        )

    def as_tuple_list(self) -> List[Tuple[float, float]]:
        """Return the line as a list of tuples."""
        return [self.start.as_tuple(), self.end.as_tuple()]


