from patterns.pattern_engine.src.Point import Point


class Util:
    """Geometric utilities for pattern drafting"""

    @staticmethod
    def line_intersection(p1, p2, p3, p4):
        """
        Calculate intersection point between two lines
        Each line is tuple of two points (p1, p2)
        Returns Point or None if parallel
        """

        # Handle vertical lines
        if abs(p1.x - p2.x) < 1e-9:  # Line1 vertical
            if abs(p3.x - p4.x) < 1e-9:  # Both vertical
                return None
            # Line2 equation: y = m2x + b2
            m2 = (p4.y - p3.y) / (p4.x - p3.x)
            b2 = p3.y - m2 * p3.x
            x = p1.x
            y = m2 * x + b2
            return Point(x, y)

        # Handle horizontal lines
        if abs(p3.y - p4.y) < 1e-9:  # Line2 horizontal
            y = p3.y
            m1 = (p2.y - p1.y) / (p2.x - p1.x)
            b1 = p1.y - m1 * p1.x
            x = (y - b1) / m1
            return Point(x, y)

        # General case using matrix solution
        denom = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
        if abs(denom) < 1e-9:  # Lines parallel
            return None

        x_num = (p1.x * p2.y - p1.y * p2.x) * (p3.x - p4.x) - (p1.x - p2.x) * (p3.x * p4.y - p3.y * p4.x)
        y_num = (p1.x * p2.y - p1.y * p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x * p4.y - p3.y * p4.x)

        x = x_num / denom
        y = y_num / denom

        return Point(x, y)

    @staticmethod
    def reflect_vertical(point, mirror_x):
        """Reflect point across vertical line x=mirror_x"""
        return Point(2 * mirror_x - point.x, point.y)