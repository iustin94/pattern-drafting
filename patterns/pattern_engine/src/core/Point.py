"""
Point class implementation using Shapely.

This module replaces the original Point class with one based on Shapely,
while maintaining the same interface for compatibility.
"""
import math
from typing import Tuple, Any

from shapely.geometry import Point as ShapelyPoint


class Point:
    """
    Represents a 2D point in the pattern using Shapely.

    This implementation wraps a Shapely Point while maintaining
    the same interface as the original Point class.
    """

    def __init__(self, x: float, y: float):
        """Initialize a 2D point."""
        self.x = x
        self.y = y
        self._shapely_point = ShapelyPoint(x, y)

    @property
    def shapely(self) -> ShapelyPoint:
        """Get the underlying Shapely point."""
        return self._shapely_point

    def __add__(self, other):
        """Add two points together."""
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Subtract one point from another."""
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        """Multiply point coordinates by a scalar."""
        return Point(self.x * scalar, self.y * scalar)

    def distance_to(self, other) -> float:
        """Calculate the distance between two points."""
        if isinstance(other, Point):
            return self._shapely_point.distance(other.shapely)
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def rotate(self, angle_deg, origin=None):
        """Rotate the point around an origin (default is origin (0,0))."""
        if origin is None:
            origin = Point(0, 0)

        # Use affine transformation for rotation
        angle_rad = math.radians(angle_deg)
        s, c = math.sin(angle_rad), math.cos(angle_rad)

        # Translate to origin
        translated_x = self.x - origin.x
        translated_y = self.y - origin.y

        # Rotate
        rotated_x = translated_x * c - translated_y * s
        rotated_y = translated_x * s + translated_y * c

        # Translate back
        return Point(rotated_x + origin.x, rotated_y + origin.y)

    def as_tuple(self) -> Tuple[float, float]:
        """Return the point as a tuple."""
        return (self.x, self.y)

    def __eq__(self, other):
        """Compare points for equality."""
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        """String representation of the point."""
        return f"Point({self.x}, {self.y})"