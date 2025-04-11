"""
Pattern piece implementation using Shapely and Matplotlib.

This module replaces the original PatternPiece class with one based on Shapely
geometries and Matplotlib for rendering.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from shapely.geometry import LineString, Polygon as ShapelyPolygon
from shapely.ops import unary_union, polygonize

from .Point import Point
from .Line import Line
from .Curve import Curve


@dataclass
class PatternPiece:
    """
    Represents a piece of a pattern with paths and properties.

    This implementation uses Shapely geometries and Matplotlib for rendering.
    """
    name: str
    points: Dict[str, Point] = field(default_factory=dict)
    paths: List[List[Union[Line, Curve]]] = field(default_factory=list)
    seam_allowance: float = 0.0
    mirror: bool = False
    fold_line: Optional[Line] = None

    def __post_init__(self):
        """Initialize after dataclass fields have been set."""
        self._shapely_geometry = None
        self._polygon = None

    def add_point(self, name: str, point: Point) -> None:
        """Add a named point to the pattern piece."""
        self.points[name] = point
        # Invalidate cached geometry when points change
        self._shapely_geometry = None
        self._polygon = None

    def get_point(self, name: str) -> Point:
        """Get a point by name."""
        if name not in self.points:
            raise KeyError(f"Point '{name}' not found in pattern piece '{self.name}'")
        return self.points[name]

    def add_path(self, path: List[Union[Line, Curve]]) -> None:
        """Add a path (outline or internal line) to the pattern piece."""
        self.paths.append(path)
        # Invalidate cached geometry when paths change
        self._shapely_geometry = None
        self._polygon = None

    def get_bounding_box(self) -> Tuple[Point, Point]:
        """Return the bounding box of the pattern piece as (min_point, max_point)."""
        if not self.points:
            return Point(0, 0), Point(0, 0)

        # Use the polygon's bounds if available
        if self._get_polygon():
            bounds = self._get_polygon().bounds
            return Point(bounds[0], bounds[1]), Point(bounds[2], bounds[3])

        # Otherwise compute from points
        x_values = [p.x for p in self.points.values()]
        y_values = [p.y for p in self.points.values()]

        return Point(min(x_values), min(y_values)), Point(max(x_values), max(y_values))

    def _get_polygon(self) -> Optional[ShapelyPolygon]:
        """Get the Shapely polygon representing the pattern piece."""
        if self._polygon is not None:
            return self._polygon

        # Try to create a polygon from the paths
        # This assumes the paths form a closed shape
        if not self.paths:
            return None

        # Collect all linestrings from the paths
        linestrings = []
        for path in self.paths:
            for segment in path:
                if isinstance(segment, Line):
                    linestrings.append(LineString([segment.start.as_tuple(), segment.end.as_tuple()]))
                elif isinstance(segment, Curve):
                    linestrings.append(segment.shapely)

        # Try to create a polygon using shapely's polygonize function
        if linestrings:
            try:
                # Merge all linestrings
                merged = unary_union(linestrings)
                # Create polygons from the merged linestrings
                polygons = list(polygonize(merged))
                if polygons:
                    # Use the largest polygon as the main shape
                    self._polygon = max(polygons, key=lambda p: p.area)
                    return self._polygon
            except Exception as e:
                print(f"Warning: Could not create polygon for piece {self.name}: {e}")

        return None

    def get_area(self) -> float:
        """Calculate the area of the pattern piece."""
        polygon = self._get_polygon()
        if polygon:
            return polygon.area
        return 0

    def get_perimeter(self) -> float:
        """Calculate the perimeter of the pattern piece."""
        polygon = self._get_polygon()
        if polygon:
            return polygon.length
        return 0

    def add_seam_allowance(self, allowance: float = None) -> 'PatternPiece':
        """
        Create a new pattern piece with seam allowance added.

        Args:
            allowance: Seam allowance to add (uses self.seam_allowance if None)

        Returns:
            New PatternPiece with seam allowance
        """
        if allowance is None:
            allowance = self.seam_allowance

        if allowance <= 0:
            return self

        # Get the polygon representation of the pattern piece
        polygon = self._get_polygon()
        if not polygon:
            # If we can't create a polygon, return the original piece
            return self

        # Use Shapely's buffer to create the seam allowance
        # The join_style=2 creates mitered corners, resolution controls smoothness
        expanded_polygon = polygon.buffer(allowance, join_style=2, resolution=16)

        # Create a new pattern piece with the expanded polygon
        new_piece = PatternPiece(
            name=f"{self.name}_with_seam_allowance",
            seam_allowance=0,  # Seam allowance is already included
            mirror=self.mirror,
            fold_line=self.fold_line
        )

        # Copy the original points
        for name, point in self.points.items():
            new_piece.add_point(name, point)

        # Add seam allowance outline
        # Extract the exterior coordinates of the expanded polygon
        coords = list(expanded_polygon.exterior.coords)

        # Create points along the outline
        outer_points = []
        for i, (x, y) in enumerate(coords):
            point_name = f"sa_{i}"
            point = Point(x, y)
            new_piece.add_point(point_name, point)
            outer_points.append(point_name)

        # Create a path connecting these points
        if outer_points:
            new_path = []
            for i in range(len(outer_points) - 1):
                start = new_piece.get_point(outer_points[i])
                end = new_piece.get_point(outer_points[i + 1])
                new_path.append(Line(start, end))

            # Close the path by connecting the last point to the first
            start = new_piece.get_point(outer_points[-1])
            end = new_piece.get_point(outer_points[0])
            new_path.append(Line(start, end))

            new_piece.add_path(new_path)

        # Also add the original paths as construction lines
        for path in self.paths:
            new_piece.add_path(path)

        return new_piece

    def render(self, ax=None, color='black', fill=False, alpha=0.2, show_points=True,
               show_labels=True, show_seam_allowance=True, show_fold_line=True):
        """
        Render the pattern piece on a matplotlib axis.

        Args:
            ax: Matplotlib axis to render on (creates a new figure if None)
            color: Color for the pattern outline
            fill: Whether to fill the pattern piece
            alpha: Transparency for filled areas
            show_points: Whether to show points
            show_labels: Whether to show point labels
            show_seam_allowance: Whether to show seam allowance
            show_fold_line: Whether to show fold line

        Returns:
            Matplotlib figure if ax was None, otherwise the provided axis
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
            standalone = True
        else:
            standalone = False

        # Plot named points if requested
        if show_points:
            for name, point in self.points.items():
                ax.plot(point.x, point.y, 'o', markersize=4, color=color)
                if show_labels:
                    ax.text(point.x + 0.5, point.y + 0.5, name, fontsize=8, color=color,
                            ha='left', va='bottom')

        # Plot paths
        for path in self.paths:
            path_points = []

            for segment in path:
                if isinstance(segment, Line):
                    line_points = [segment.start.as_tuple(), segment.end.as_tuple()]
                    ax.plot([p[0] for p in line_points], [p[1] for p in line_points], '-',
                            color=color, linewidth=1.5)
                    path_points.extend(line_points)

                elif isinstance(segment, Curve):
                    # Get curve points and plot
                    curve_points = segment.as_tuple_list(30)  # Use more points for smoother curves
                    ax.plot([p[0] for p in curve_points], [p[1] for p in curve_points], '-',
                            color=color, linewidth=1.5)
                    path_points.extend(curve_points)

            # Fill the path if requested
            if fill and len(path_points) > 2:
                polygon = Polygon(path_points, closed=True, fill=True, color=color, alpha=alpha)
                ax.add_patch(polygon)

        # Add seam allowance if requested and available
        if show_seam_allowance and self.seam_allowance > 0:
            polygon = self._get_polygon()
            if polygon:
                # Create seam allowance polygon
                expanded = polygon.buffer(self.seam_allowance, join_style=2, resolution=16)

                # Get the coordinates of the exterior ring
                exterior_coords = list(expanded.exterior.coords)

                # Plot seam allowance outline
                x, y = zip(*exterior_coords)
                ax.plot(x, y, '--', color=color, linewidth=0.75, alpha=0.7)

                # Fill between original and expanded polygons if fill is True
                if fill:
                    # Create a polygon with a hole (the original shape)
                    # This creates a donut-shaped polygon representing just the seam allowance
                    seam_poly = Polygon(
                        exterior_coords,
                        closed=True,
                        fill=True,
                        color=color,
                        alpha=alpha/2  # Use half the alpha for seam allowance
                    )
                    ax.add_patch(seam_poly)

        # Draw fold line if present and requested
        if show_fold_line and self.fold_line:
            ax.plot(
                [self.fold_line.start.x, self.fold_line.end.x],
                [self.fold_line.start.y, self.fold_line.end.y],
                '--', color='blue', linewidth=1.5, alpha=0.7
            )

            # Add "FOLD LINE" text
            midpoint = self.fold_line.midpoint()
            ax.text(
                midpoint.x, midpoint.y + 1,  # Offset text slightly
                "FOLD LINE",
                color='blue', fontsize=8,
                ha='center', va='bottom'
            )

        # Set equal aspect ratio and title
        ax.set_aspect('equal')
        ax.set_title(self.name)

        # Auto-set axis limits based on the pattern piece bounding box
        min_point, max_point = self.get_bounding_box()
        padding = max(5, self.seam_allowance * 2)  # Add padding for seam allowance
        ax.set_xlim(min_point.x - padding, max_point.x + padding)
        ax.set_ylim(min_point.y - padding, max_point.y + padding)

        if standalone:
            plt.tight_layout()
            return fig
        return ax

    def export_svg(self, filename: str, add_seam_allowance: bool = True) -> str:
        """
        Export the pattern piece as an SVG file.

        Args:
            filename: Path to save the SVG file
            add_seam_allowance: Whether to include seam allowance in the SVG

        Returns:
            Path to the saved SVG file
        """
        fig, ax = plt.subplots(figsize=(10, 10))
        self.render(ax, fill=False, show_seam_allowance=add_seam_allowance)

        # Save as SVG
        fig.savefig(filename, format='svg', bbox_inches='tight')
        plt.close(fig)

        return filename

    def mirror_piece(self, mirror_x: float = 0) -> 'PatternPiece':
        """
        Create a mirrored version of this pattern piece.

        Args:
            mirror_x: X-coordinate of the vertical mirror line

        Returns:
            New PatternPiece that is a mirror of this piece
        """
        mirrored = PatternPiece(
            name=f"{self.name}_mirrored",
            seam_allowance=self.seam_allowance,
            mirror=not self.mirror  # Toggle mirror flag
        )

        # Mirror all points
        for name, point in self.points.items():
            mirrored_x = 2 * mirror_x - point.x
            mirrored_point = Point(mirrored_x, point.y)
            mirrored.add_point(name, mirrored_point)

        # Mirror all paths
        for path in self.paths:
            mirrored_path = []
            for segment in path:
                if isinstance(segment, Line):
                    start = mirrored.get_point(self._find_point_name(segment.start))
                    end = mirrored.get_point(self._find_point_name(segment.end))
                    mirrored_path.append(Line(start, end))
                elif isinstance(segment, Curve):
                    start = mirrored.get_point(self._find_point_name(segment.start_point))
                    end = mirrored.get_point(self._find_point_name(segment.end_point))
                    control = mirrored.get_point(self._find_point_name(segment.control_point))

                    if isinstance(segment, Curve.CurveWithPeak):
                        mirrored_path.append(Curve.CurveWithPeak(
                            start, end, segment.peak_value, segment.inflection_point
                        ))
                    elif isinstance(segment, Curve.CurveWithReference):
                        ref = mirrored.get_point(self._find_point_name(segment.reference_point))
                        mirrored_path.append(Curve.CurveWithReference(
                            start, end, ref, segment.target_distance
                        ))
                    else:
                        mirrored_path.append(Curve(start, end, control))

            mirrored.add_path(mirrored_path)

        # Mirror fold line if present
        if self.fold_line:
            start = mirrored.get_point(self._find_point_name(self.fold_line.start))
            end = mirrored.get_point(self._find_point_name(self.fold_line.end))
            mirrored.fold_line = Line(start, end)

        return mirrored

    def _find_point_name(self, point: Point) -> str:
        """Find the name of a point in this piece."""
        for name, p in self.points.items():
            if p.x == point.x and p.y == point.y:
                return name

        # If point not found, return a descriptive error
        raise ValueError(f"Point ({point.x}, {point.y}) not found in pattern piece {self.name}")