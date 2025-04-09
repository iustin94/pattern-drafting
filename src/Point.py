import math
from dataclasses import dataclass

from typing import Tuple


@dataclass
class Point:
    """Represents a 2D point in the pattern."""
    x: float
    y: float

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
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def rotate(self, angle_deg, origin=None):
        """Rotate the point around an origin (default is origin (0,0))."""
        if origin is None:
            origin = Point(0, 0)

        angle_rad = math.radians(angle_deg)
        s, c = math.sin(angle_rad), math.cos(angle_rad)

        # Translate to origin
        translated = Point(self.x - origin.x, self.y - origin.y)

        # Rotate
        rotated_x = translated.x * c - translated.y * s
        rotated_y = translated.x * s + translated.y * c

        # Translate back
        return Point(rotated_x + origin.x, rotated_y + origin.y)

    def as_tuple(self) -> Tuple[float, float]:
        """Return the point as a tuple."""
        return (self.x, self.y)


