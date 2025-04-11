import math

from typing import List

from .Curve import Curve, CurveWithPeak, CurveWithReference
from .Line import Line
from .Pattern import Pattern
from .PatternPiece import PatternPiece
from .Point import Point


class PatternBuilder:
    """Builder class for creating patterns declaratively."""

    def __init__(self, name: str):
        self.pattern = Pattern(name)
        self.current_piece: PatternPiece = None

    def add_measurements(self, **measurements) -> 'PatternBuilder':
        """Add multiple measurements to the pattern."""
        for name, value in measurements.items():
            self.pattern.set_measurement(name, value)
        return self

    def get_measurement(self, name: str) -> float:
        """Get a measurement value."""
        return self.pattern.get_measurement(name)

    # def start_piece(self, name: str) -> 'PatternBuilder':
    #     """Start defining a new pattern piece."""
    #     self.current_piece = PatternPiece(name)
    #     return self
    #
    # def end_piece(self) -> 'PatternBuilder':
    #     """Finish the current piece and add it to the pattern."""
    #     if self.current_piece is None:
    #         raise ValueError("No pattern piece is currently being defined")
    #
    #     self.pattern.add_piece(self.current_piece)
    #     self.current_piece = None
    #     return self

    def add_point(self, name: str, x: float, y: float) -> 'PatternBuilder':
        """Add a point with absolute coordinates."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        self.current_piece.add_point(name, Point(x, y))
        return self

    def add_point_relative(self, name: str, base_point_name: str, dx: float, dy: float) -> 'PatternBuilder':
        """Add a point relative to another point."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        base_point = self.current_piece.get_point(base_point_name)
        new_point = Point(base_point.x + dx, base_point.y + dy)
        self.current_piece.add_point(name, new_point)
        return self

    def add_point_polar(self, name: str, base_point_name: str, distance: float, angle_deg: float) -> 'PatternBuilder':
        """Add a point at a polar coordinate from another point."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        base_point = self.current_piece.get_point(base_point_name)
        angle_rad = math.radians(angle_deg)
        new_point = Point(
            base_point.x + distance * math.cos(angle_rad),
            base_point.y + distance * math.sin(angle_rad)
        )
        self.current_piece.add_point(name, new_point)
        return self

    def add_point_on_line(self, name: str, point1_name: str, point2_name: str, fraction: float) -> 'PatternBuilder':
        """Add a point on a line between two points at a specified fraction (0-1)."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        p1 = self.current_piece.get_point(point1_name)
        p2 = self.current_piece.get_point(point2_name)

        new_point = Point(
            p1.x + (p2.x - p1.x) * fraction,
            p1.y + (p2.y - p1.y) * fraction
        )
        self.current_piece.add_point(name, new_point)
        return self

    def add_point_perpendicular(self, name: str, line_start: str, line_end: str,
                                from_point: str, distance: float) -> 'PatternBuilder':
        """Add a point perpendicular to a line at a specified distance."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        p1 = self.current_piece.get_point(line_start)
        p2 = self.current_piece.get_point(line_end)
        p3 = self.current_piece.get_point(from_point)

        line = Line(p1, p2)
        direction = line.direction()
        perp_direction = Point(-direction.y, direction.x)

        new_point = Point(
            p3.x + perp_direction.x * distance,
            p3.y + perp_direction.y * distance
        )
        self.current_piece.add_point(name, new_point)
        return self

    def add_point_intersection(self, name: str,
                               line1_start: str, line1_end: str,
                               line2_start: str, line2_end: str) -> 'PatternBuilder':
        """Add a point at the intersection of two lines."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        p1 = self.current_piece.get_point(line1_start)
        p2 = self.current_piece.get_point(line1_end)
        p3 = self.current_piece.get_point(line2_start)
        p4 = self.current_piece.get_point(line2_end)

        # Line 1 is represented as p1 + t1 * (p2 - p1)
        # Line 2 is represented as p3 + t2 * (p4 - p3)
        # Solve for t1 and t2

        dx1 = p2.x - p1.x
        dy1 = p2.y - p1.y
        dx2 = p4.x - p3.x
        dy2 = p4.y - p3.y

        denominator = dx1 * dy2 - dy1 * dx2

        if abs(denominator) < 1e-10:
            raise ValueError("Lines are parallel, no intersection found")

        dx3 = p1.x - p3.x
        dy3 = p1.y - p3.y

        t1 = (dx2 * dy3 - dy2 * dx3) / denominator

        intersection = Point(
            p1.x + t1 * dx1,
            p1.y + t1 * dy1
        )

        self.current_piece.add_point(name, intersection)
        return self

    # def add_line_path(self, points: List[str]) -> 'PatternBuilder':
    #     """Add a path connecting points with straight lines."""
    #     if self.current_piece is None:
    #         raise ValueError("No pattern piece is currently being defined")
    #
    #     if len(points) < 2:
    #         raise ValueError("A line path must have at least 2 points")
    #
    #     path = []
    #     for i in range(len(points) - 1):
    #         start = self.current_piece.get_point(points[i])
    #         end = self.current_piece.get_point(points[i + 1])
    #         path.append(Line(start, end))
    #
    #     self.current_piece.add_path(path)
    #     return self
    #
    #
    # def add_bezier_curve(self,
    #                      start_point_name: str,
    #                      end_point_name: str,
    #                      peak_value: float,
    #                      inflection_point: float) -> 'PatternBuilder':
    #     """
    #     Add a Bezier curve segment to the current path.
    #
    #     :param curve_points: List of point names defining the curve
    #     :param peak_value: The maximum distance the curve deviates from a straight line (default: 2)
    #     :param inflection_point: The point (0-1) where the curve has maximum curvature (default: 0.5)
    #     """
    #     if self.current_piece is None:
    #         raise ValueError("No pattern piece is currently being defined")
    #
    #     start_point = self.current_piece.get_point(start_point_name)
    #     end_point = self.current_piece.get_point(end_point_name)
    #
    #     inflection_x = (start_point.x + end_point.x) * inflection_point
    #     inflection_y = (start_point.y + end_point.y) * inflection_point
    #     control_points = [Point(inflection_x, inflection_y)]
    #
    #     # Choose a control point based on the available points
    #     control_point = control_points[0] if control_points else None
    #
    #     # Create the curve
    #     if control_point:
    #         curve = CurveWithPeak(start_point, end_point, peak_value, inflection_point)
    #     else:
    #         # Fallback to a simple line if no control points
    #         curve = CurveWithPeak(start_point, end_point, 0, 0.5)
    #
    #     # Add the curve to the path
    #     path = [curve]
    #     self.current_piece.add_path(path)
    #     return self
    #
    # def add_bezier_curve_with_reference(self,
    #                                     start_point_name: str,
    #                                     end_point_name: str,
    #                                     reference_point_name: str, target_distance: float):
    #     """
    #     Add a Bezier curve segment with external refference point to the current path.
    #
    #     :param curve_points: List of point names defining the curve
    #     :param peak_value: The maximum distance the curve deviates from a straight line (default: 2)
    #     :param inflection_point: The point (0-1) where the curve has maximum curvature (default: 0.5)
    #     """
    #     if self.current_piece is None:
    #         raise ValueError("No pattern piece is currently being defined")
    #
    #     start_point = self.current_piece.get_point(start_point_name)
    #     end_point = self.current_piece.get_point(end_point_name)
    #     reference_point = self.current_piece.get_point(reference_point_name)
    #
    #     # Fallback to a simple line if no control points
    #     curve = CurveWithReference(start_point, end_point, reference_point, target_distance)
    #
    #     # Add the curve to the path
    #     path = [curve]
    #     self.current_piece.add_path(path)
    #     return self

    def start_piece(self, name: str) -> 'PatternBuilder':
        """Start defining a new pattern piece and initialize its path."""
        self.current_piece = PatternPiece(name)
        self.current_path = []  # Reset path for new piece
        return self

    def end_piece(self) -> 'PatternBuilder':
        """Finish the current piece, add accumulated path, and reset state."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        # Add the accumulated path to the piece
        if self.current_path:
            self.current_piece.add_path(self.current_path)

        self.pattern.add_piece(self.current_piece)
        self.current_piece = None
        self.current_path = []
        return self

    def add_line_path(self, points: List[str]) -> 'PatternBuilder':
        """Add a series of connected straight lines to the current path."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        if len(points) < 2:
            raise ValueError("A line path must have at least 2 points")

        # Create and append line segments to current path
        for i in range(len(points) - 1):
            start = self.current_piece.get_point(points[i])
            end = self.current_piece.get_point(points[i + 1])
            self.current_piece.add_path([Line(start, end)])

        return self

    def add_bezier_curve(self,
                         start_point_name: str,
                         end_point_name: str,
                         peak_value: float,
                         inflection_point: float) -> 'PatternBuilder':
        """Add a Bezier curve segment to the current path."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        # Create curve and add to current path
        start_point = self.current_piece.get_point(start_point_name)
        end_point = self.current_piece.get_point(end_point_name)
        curve = CurveWithPeak(start_point, end_point, peak_value, inflection_point)
        self.current_path.append(curve)
        return self

    def add_bezier_curve_with_reference(self,
                                        start_point_name: str,
                                        end_point_name: str,
                                        reference_point_name: str,
                                        target_distance: float) -> 'PatternBuilder':
        """Add a reference-controlled Bezier curve to the current path."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        # Create curve and add to current path
        start_point = self.current_piece.get_point(start_point_name)
        end_point = self.current_piece.get_point(end_point_name)
        reference_point = self.current_piece.get_point(reference_point_name)
        curve = CurveWithReference(start_point, end_point, reference_point, target_distance)
        self.current_path.append(curve)
        return self

    def set_fold_line(self, start_point: str, end_point: str) -> 'PatternBuilder':
        """Define a fold line for the current piece."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        start = self.current_piece.get_point(start_point)
        end = self.current_piece.get_point(end_point)

        self.current_piece.fold_line = Line(start, end)
        return self

    def set_seam_allowance(self, allowance: float) -> 'PatternBuilder':
        """Set the seam allowance for the current piece."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        self.current_piece.seam_allowance = allowance
        return self

    def set_mirror(self, mirror: bool = True) -> 'PatternBuilder':
        """Set whether the current piece should be mirrored."""
        if self.current_piece is None:
            raise ValueError("No pattern piece is currently being defined")

        self.current_piece.mirror = mirror
        return self

    def build(self) -> Pattern:
        """Build and return the complete pattern."""
        if self.current_piece is not None:
            self.end_piece()

        return self.pattern


