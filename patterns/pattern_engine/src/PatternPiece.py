from dataclasses import dataclass, field
from typing import Union, List, Optional, Tuple, Dict

from matplotlib import pyplot as plt
from matplotlib.patches import Polygon

from patterns.pattern_engine.src.CurveWithPeak import CurveWithPeak, CurveWithReference, Curve
from patterns.pattern_engine.src.Line import Line
from patterns.pattern_engine.src.Point import Point


@dataclass
class PatternPiece:
    """Represents a piece of a pattern with path and properties."""
    name: str
    points: Dict[str, Point] = field(default_factory=dict)
    paths: List[List[Union[Line, CurveWithPeak]]] = field(default_factory=list)
    seam_allowance: float = 0.0
    mirror: bool = False
    fold_line: Optional[Line] = None

    def add_point(self, name: str, point: Point) -> None:
        """Add a named point to the pattern piece."""
        self.points[name] = point

    def get_point(self, name: str) -> Point:
        """Get a point by name."""
        if name not in self.points:
            raise KeyError(f"Point '{name}' not found in pattern piece '{self.name}'")
        return self.points[name]

    def add_path(self, path: List[Union[Line, CurveWithPeak, CurveWithReference]]) -> None:
        """Add a path (outline or internal line) to the pattern piece."""
        self.paths.append(path)

    def get_bounding_box(self) -> Tuple[Point, Point]:
        """Return the bounding box of the pattern piece as (min_point, max_point)."""
        if not self.points:
            return Point(0, 0), Point(0, 0)

        x_values = [p.x for p in self.points.values()]
        y_values = [p.y for p in self.points.values()]

        return Point(min(x_values), min(y_values)), Point(max(x_values), max(y_values))

    def get_all_points(self) -> List[Point]:
        """Return all points in the pattern piece, including those in paths."""
        result = list(self.points.values())

        for path in self.paths:
            for segment in path:
                if isinstance(segment, Line):
                    result.extend([segment.start, segment.end])
                elif isinstance(segment, Curve):
                    result.extend(segment.points)

        return result

    def render(self, ax=None, color='black', fill=False, alpha=0.2):
        """Render the pattern piece on a matplotlib axis."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
            standalone = True
        else:
            standalone = False

        # Plot named points
        for name, point in self.points.items():
            ax.plot(point.x, point.y, 'o', markersize=4)
            ax.text(point.x, point.y, name, fontsize=8)

        # Plot paths
        for path in self.paths:
            path_points = []

            for segment in path:
                if isinstance(segment, Line):
                    line_points = [segment.start.as_tuple(), segment.end.as_tuple()]
                    ax.plot([p[0] for p in line_points], [p[1] for p in line_points], '-', color=color)
                    path_points.extend(line_points)
                elif isinstance(segment, Curve):
                    curve_points = segment.as_tuple_list()
                    ax.plot([p[0] for p in curve_points], [p[1] for p in curve_points], '-', color=color)
                    path_points.extend(curve_points)

            # Fill the path if requested
            if fill and len(path_points) > 2:
                polygon = Polygon(path_points, closed=True, fill=True, color=color, alpha=alpha)
                ax.add_patch(polygon)

        # Draw fold line if present
        if self.fold_line:
            ax.plot(
                [self.fold_line.start.x, self.fold_line.end.x],
                [self.fold_line.start.y, self.fold_line.end.y],
                '--', color='blue'
            )
            ax.text(
                self.fold_line.midpoint().x,
                self.fold_line.midpoint().y,
                "FOLD LINE",
                color='blue',
                fontsize=8
            )

        # Set equal aspect ratio
        ax.set_aspect('equal')
        ax.set_title(self.name)

        if standalone:
            plt.tight_layout()
            return fig
        return ax


