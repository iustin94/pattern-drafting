import math

from typing import Tuple, List

from src.Point import Point

class Curve:

    def __init__(self, start_point: Point, end_point: Point, control_point: Point):
        self.start_point = start_point
        self.end_point = end_point
        self.control_point = control_point

    def bezier_point(self, t: float) -> Point:
        """
        Return a point on the Bezier curve at parameter t (0-1).

        Uses quadratic Bezier curve formula.
        """
        return Point(
            (1 - t) ** 2 * self.start_point.x +
            2 * (1 - t) * t * self.control_point.x +
            t ** 2 * self.end_point.x,

            (1 - t) ** 2 * self.start_point.y +
            2 * (1 - t) * t * self.control_point.y +
            t ** 2 * self.end_point.y
        )

    @property
    def midpoint(self) -> Point:
        """Get the midpoint of the curve (t=0.5)"""
        return self.bezier_point(0.5)

    def discretize(self, num_points: int = 20) -> List[Point]:
        """
        Return a list of points that discretize the curve.

        :param num_points: Number of points to generate along the curve
        :return: List of points on the curve
        """
        return [self.bezier_point(t / (num_points - 1)) for t in range(num_points)]

    def as_tuple_list(self, num_points: int = 20) -> List[Tuple[float, float]]:
        """
        Return the curve as a list of tuples.

        :param num_points: Number of points to generate along the curve
        :return: List of (x, y) tuples representing points on the curve
        """
        return [p.as_tuple() for p in self.discretize(num_points)]

    def max_deviation(self, start_point: Point, end_point: Point) -> float:
        """
        Calculate the maximum deviation from the straight line.

        :return: Maximum distance from the curve to the straight line
        """
        # Discretize the curve and the straight line
        curve_points = self.discretize(100)

        # Create a straight line between start and end points
        def line_point(t):
            return Point(
                start_point.x + t * (end_point.x - start_point.x),
                start_point.y + t * (end_point.y - start_point.y)
            )

        # Calculate maximum distance
        max_dev = max(
            math.sqrt(
                (cp.x - line_point(i / 99).x) ** 2 +
                (cp.y - line_point(i / 99).y) ** 2
            )
            for i, cp in enumerate(curve_points)
        )

        return max_dev

class CurveWithPeak(Curve):
    """
    Represents a curve defined by two points, with a specific peak offset.

    The curve will touch exactly the specified peak value offset from
    the straight line between start and end points.
    """

    def __init__(self, start_point: Point, end_point: Point, peak_value: float, inflection_point: float = 0.5):
        """
        Initialize the curve.

        :param start_point: The starting point of the curve
        :param end_point: The ending point of the curve
        :param peak_value: The exact offset distance the curve will touch
        :param inflection_point: The point (0-1) where the curve has maximum curvature (default: 0.5)
        """
        if not (0 <= inflection_point <= 1):
            raise ValueError("Inflection point must be between 0 and 1")

        self.start_point = start_point
        self.end_point = end_point
        self.peak_value = peak_value
        self.inflection_point = inflection_point
        control_point = self._calculate_precise_control_point()

        super().__init__(start_point, end_point, control_point)

    def _calculate_precise_control_point(self):
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
        normalized_perp_x = perp_dx / perp_length
        normalized_perp_y = perp_dy / perp_length

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

    def __init__(self, start_point: Point, end_point: Point,
                 reference_point: Point, target_distance: float):
        """
        Initialize a curve between two points that curves relative to a reference point.

        :param start_point: Starting point of the curve (A)
        :param end_point: Ending point of the curve (B)
        :param reference_point: External reference point (C) that influences the curve shape
        :param target_distance: Distance the curve's midpoint should maintain from C
        """
        self.start_point = start_point
        self.end_point = end_point
        self.reference_point = reference_point
        self.target_distance = target_distance
        control_point = self._calculate_control_point()

        super().__init__(start_point, end_point, control_point)


    def _calculate_control_point(self):
        """Calculate control point to achieve desired distance from reference point"""
        # Calculate midpoint between start and end
        midpoint = Point(
            (self.start_point.x + self.end_point.x) / 2,
            (self.start_point.y + self.end_point.y) / 2
        )

        # Vector from midpoint to reference point
        dx = self.reference_point.x - midpoint.x
        dy = self.reference_point.y - midpoint.y
        ref_distance = math.hypot(dx, dy)

        if ref_distance == 0:
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
        return Point(
            2 * curve_mid.x - 0.5 * self.start_point.x - 0.5 * self.end_point.x,
            2 * curve_mid.y - 0.5 * self.start_point.y - 0.5 * self.end_point.y
        )