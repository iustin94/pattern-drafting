"""
Technical pattern visualization module for rendering patterns with coordinates (fixed).
This module provides enhanced visualization with technical details like point coordinates.
"""
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon, FancyArrowPatch, Circle, Rectangle
from matplotlib.gridspec import GridSpec
from typing import List, Dict, Tuple, Optional, Union
import io
import os
from PIL import Image

from patterns.pattern_engine.src.CurveWithPeak import CurveWithPeak, Curve
from patterns.pattern_engine.src.Line import Line
from patterns.pattern_engine.src.Pattern import Pattern
from patterns.pattern_engine.src.PatternPiece import PatternPiece


class TechnicalPatternRenderer:
    """Technical renderer for pattern visualization with coordinate tables."""

    def __init__(self, pattern: Pattern):
        self.pattern = pattern
        self.colors = {
            'Back': 'blue',
            'Front': 'red',
            'Sleeve': 'green',
            'Short Sleeve': 'green',
            'grid_major': '#CCCCCC',
            'grid_minor': '#EEEEEE',
            'text': 'black'
        }

    def _create_coordinate_table(self, piece: PatternPiece):
        """Create a coordinate table for the given pattern piece."""
        point_data = []

        # Collect all named points and sort them
        points = sorted([(name, point) for name, point in piece.points.items()],
                        key=lambda x: int(x[0]) if x[0].isdigit() else float('inf'))

        for name, point in points:
            point_data.append((name, round(point.x, 1), round(point.y, 1)))

        return point_data

    def render_piece_with_coordinates(self, piece_name: str, filename: Optional[str] = None,
                                      show_points: bool = True, show_table: bool = True,
                                      show_grid: bool = True, title: Optional[str] = None):
        """Render a single pattern piece with coordinate table."""
        if piece_name not in self.pattern.pieces:
            raise ValueError(f"Pattern piece '{piece_name}' not found")

        piece = self.pattern.pieces[piece_name]
        color = self.colors.get(piece_name, 'black')

        # Create figure with coordinate table
        fig = plt.figure(figsize=(12, 10))

        if show_table:
            # Use a GridSpec with the correct number of columns
            gs = GridSpec(1, 2, figure=fig, width_ratios=[3, 1])
            ax = fig.add_subplot(gs[0, 0])
            table_ax = fig.add_subplot(gs[0, 1])
            table_ax.axis('off')
        else:
            ax = fig.add_subplot(111)

        # Get bounding box
        min_point, max_point = piece.get_bounding_box()

        # Add padding
        padding = 5
        min_point.x -= padding
        min_point.y -= padding
        max_point.x += padding
        max_point.y += padding

        # Round to nearest 5 for cleaner grid
        min_x = math.floor(min_point.x / 5) * 5
        max_x = math.ceil(max_point.x / 5) * 5
        min_y = math.floor(min_point.y / 5) * 5
        max_y = math.ceil(max_point.y / 5) * 5

        # Draw grid if requested
        if show_grid:
            # Draw minor grid (1 cm)
            minor_grid_size = 1
            x_minor_grid = np.arange(min_x, max_x + minor_grid_size, minor_grid_size)
            y_minor_grid = np.arange(min_y, max_y + minor_grid_size, minor_grid_size)

            for x in x_minor_grid:
                ax.axvline(x, color=self.colors['grid_minor'], linestyle='-', linewidth=0.5, alpha=0.7)
            for y in y_minor_grid:
                ax.axhline(y, color=self.colors['grid_minor'], linestyle='-', linewidth=0.5, alpha=0.7)

            # Draw major grid (5 cm)
            major_grid_size = 5
            x_major_grid = np.arange(min_x, max_x + major_grid_size, major_grid_size)
            y_major_grid = np.arange(min_y, max_y + major_grid_size, major_grid_size)

            for x in x_major_grid:
                ax.axvline(x, color=self.colors['grid_major'], linestyle='-', linewidth=0.8, alpha=0.8)
            for y in y_major_grid:
                ax.axhline(y, color=self.colors['grid_major'], linestyle='-', linewidth=0.8, alpha=0.8)

        # Plot paths with different styles based on piece type
        for path in piece.paths:
            path_points = []

            for segment in path:
                if isinstance(segment, Line):
                    line_points = [segment.start.as_tuple(), segment.end.as_tuple()]
                    ax.plot([p[0] for p in line_points], [p[1] for p in line_points], '-',
                            color=color, linewidth=2)
                    path_points.extend(line_points)
                elif isinstance(segment, Curve):
                    curve_points = segment.as_tuple_list(30)  # More points for smoother curves
                    ax.plot([p[0] for p in curve_points], [p[1] for p in curve_points], '-',
                            color=color, linewidth=2)
                    path_points.extend(curve_points)

        # Plot points with labels if requested
        if show_points:
            for name, point in piece.points.items():
                # Only show numeric points and a few key points to avoid clutter
                # Skip points that are likely control points (contain "control" in name)
                if (name.isdigit() or name in ['origin', 'center_waist']) and 'control' not in name.lower():
                    ax.plot(point.x, point.y, 'o', markersize=4, color=color)
                    ax.text(point.x + 0.5, point.y + 0.5, name, fontsize=8, color=color,
                            ha='left', va='bottom')

        # Add coordinate table if requested
        if show_table:
            point_data = self._create_coordinate_table(piece)

            # Create table text
            table_text = f"{piece_name} Pattern Coordinates:\n"
            table_text += "-" * 30 + "\n"
            table_text += "Point   X       Y\n"
            table_text += "-" * 30 + "\n"

            for name, x, y in point_data:
                table_text += f"{name:<8}{x:<8}{y:<8}\n"

            # Draw table as a box with text
            table_ax.text(0.05, 0.95, table_text, va='top', ha='left',
                          fontfamily='monospace', fontsize=9)

            # Add a box around the table
            table_ax.add_patch(Rectangle((0.01, 0.01), 0.98, 0.98, fill=False,
                                         edgecolor='black', linewidth=1))

        # Draw fold line if present
        if hasattr(piece, 'fold_line') and piece.fold_line:
            ax.plot(
                [piece.fold_line.start.x, piece.fold_line.end.x],
                [piece.fold_line.start.y, piece.fold_line.end.y],
                '--', color='blue', linewidth=1.5, alpha=0.7
            )

        # Set axis properties
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(max_y, min_y)  # Reverse Y axis to match pattern convention
        ax.set_xlabel('X coordinate (cm)')
        ax.set_ylabel('Y coordinate (cm)')
        ax.set_aspect('equal')

        # Set title
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"{piece_name} Pattern")

        plt.tight_layout()

        if filename:
            plt.savefig(filename, bbox_inches='tight', dpi=300)
            plt.close(fig)
            return None

        return fig

    def render_technical_view(self, filename: Optional[str] = None,
                              show_tables: bool = True, show_points: bool = True):
        """Render all pattern pieces with technical details."""
        # Sort pieces by type (body parts and sleeves are grouped)
        body_pieces = []
        sleeve_pieces = []
        other_pieces = []

        for name, piece in self.pattern.pieces.items():
            if "sleeve" in name.lower():
                sleeve_pieces.append(name)
            elif "bodice" in name.lower() or "back" in name.lower() or "front" in name.lower():
                body_pieces.append(name)
            else:
                other_pieces.append(name)

        # Create multiple figures
        figures = []

        # Body pieces in one figure
        if body_pieces:
            title = f"{self.pattern.name} Body Block"
            fig_body = self._render_piece_group(body_pieces, title, show_tables, show_points)
            figures.append((fig_body, "body_block"))

        # Sleeve pieces in one figure
        if sleeve_pieces:
            title = f"{self.pattern.name} Sleeve Block"
            fig_sleeve = self._render_piece_group(sleeve_pieces, title, show_tables, show_points)
            figures.append((fig_sleeve, "sleeve_block"))

        # Other pieces each in their own figure
        for name in other_pieces:
            title = f"{self.pattern.name} - {name}"
            fig = self.render_piece_with_coordinates(name, None, show_points, show_tables)
            figures.append((fig, name.lower().replace(" ", "_")))

        # Save figures if filename is provided
        if filename:
            base_filename, ext = os.path.splitext(filename)
            if not ext:
                ext = '.png'

            for fig, suffix in figures:
                output_filename = f"{base_filename}_{suffix}{ext}"
                fig.savefig(output_filename, bbox_inches='tight', dpi=300)
                plt.close(fig)

            return None

        return figures

    def _render_piece_group(self, piece_names, title, show_tables=True, show_points=True):
        """Render a group of related pieces in one figure."""
        fig = plt.figure(figsize=(12, 10))

        # FIX: Use GridSpec with the correct number of columns (2 instead of 4)
        if show_tables:
            gs = GridSpec(1, 2, figure=fig, width_ratios=[3, 1])
            ax = fig.add_subplot(gs[0, 0])
            table_ax = fig.add_subplot(gs[0, 1])
            table_ax.axis('off')
        else:
            ax = fig.add_subplot(111)

        # Calculate overall bounding box for all pieces
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')

        all_point_data = []

        # Collect all pattern pieces and their bounding boxes
        for name in piece_names:
            piece = self.pattern.pieces[name]
            piece_min, piece_max = piece.get_bounding_box()

            min_x = min(min_x, piece_min.x)
            min_y = min(min_y, piece_min.y)
            max_x = max(max_x, piece_max.x)
            max_y = max(max_y, piece_max.y)

            # Collect point data for table
            point_data = self._create_coordinate_table(piece)
            all_point_data.append((name, point_data))

        # Add padding
        padding = 5
        min_x -= padding
        min_y -= padding
        max_x += padding
        max_y += padding

        # Round to nearest 5 for cleaner grid
        min_x = math.floor(min_x / 5) * 5
        max_x = math.ceil(max_x / 5) * 5
        min_y = math.floor(min_y / 5) * 5
        max_y = math.ceil(max_y / 5) * 5

        # Draw grid
        # Minor grid (1 cm)
        minor_grid_size = 1
        x_minor_grid = np.arange(min_x, max_x + minor_grid_size, minor_grid_size)
        y_minor_grid = np.arange(min_y, max_y + minor_grid_size, minor_grid_size)

        for x in x_minor_grid:
            ax.axvline(x, color=self.colors['grid_minor'], linestyle='-', linewidth=0.5, alpha=0.7)
        for y in y_minor_grid:
            ax.axhline(y, color=self.colors['grid_minor'], linestyle='-', linewidth=0.5, alpha=0.7)

        # Major grid (5 cm)
        major_grid_size = 5
        x_major_grid = np.arange(min_x, max_x + major_grid_size, major_grid_size)
        y_major_grid = np.arange(min_y, max_y + major_grid_size, major_grid_size)

        for x in x_major_grid:
            ax.axvline(x, color=self.colors['grid_major'], linestyle='-', linewidth=0.8, alpha=0.8)
        for y in y_major_grid:
            ax.axhline(y, color=self.colors['grid_major'], linestyle='-', linewidth=0.8, alpha=0.8)

        # Plot each pattern piece
        legend_handles = []

        for name in piece_names:
            piece = self.pattern.pieces[name]
            color = self.colors.get(name, 'black')

            # Plot paths
            for path in piece.paths:
                path_points = []

                for segment in path:
                    if isinstance(segment, Line):
                        line_points = [segment.start.as_tuple(), segment.end.as_tuple()]
                        ax.plot([p[0] for p in line_points], [p[1] for p in line_points], '-',
                                color=color, linewidth=2)
                        path_points.extend(line_points)
                    elif isinstance(segment, Curve):
                        curve_points = segment.as_tuple_list(30)
                        ax.plot([p[0] for p in curve_points], [p[1] for p in curve_points], '-',
                                color=color, linewidth=2)
                        path_points.extend(curve_points)

            # Add to legend
            legend_handles.append(plt.Line2D([0], [0], color=color, linewidth=2, label=name))

            # Plot points with labels if requested
            if show_points:
                for point_name, point in piece.points.items():
                    # Only show numbered points and a few key points
                    if (point_name.isdigit() or point_name in ['origin',
                                                               'center_waist']) and 'control' not in point_name.lower():
                        ax.plot(point.x, point.y, 'o', markersize=4, color=color)
                        # If it's a short sleeve point, add "(short)" to the label
                        label_text = point_name
                        if "short" in name.lower() and point_name in ["17", "21"]:
                            label_text += "(short)"
                        ax.text(point.x + 0.5, point.y + 0.5, label_text, fontsize=8,
                                color=color, ha='left', va='bottom')

        # Add a legend
        ax.legend(handles=legend_handles, loc='upper right')

        # Add coordinate tables if requested
        if show_tables:
            # Create separate tables for each pattern piece type
            body_table = ""
            sleeve_table = ""

            # Check what type of pieces we have
            has_body = any("bodice" in name.lower() or "back" in name.lower() or "front" in name.lower()
                           for name in piece_names)
            has_sleeve = any("sleeve" in name.lower() for name in piece_names)

            if has_body:
                body_table = "Body Pattern Coordinates:\n"
                body_table += "-" * 30 + "\n"
                body_table += "Point   X       Y\n"
                body_table += "-" * 30 + "\n"

                # Add points from body pieces
                for name, points in all_point_data:
                    if "sleeve" not in name.lower():
                        for point_name, x, y in points:
                            if point_name.isdigit() or point_name in ['origin', 'center_waist']:
                                body_table += f"{point_name:<8}{x:<8}{y:<8}\n"

                # Add box around body table
                table_ax.add_patch(Rectangle((0.01, 0.55), 0.98, 0.44, fill=False,
                                             edgecolor='black', linewidth=1))
                table_ax.text(0.05, 0.95, body_table, va='top', ha='left',
                              fontfamily='monospace', fontsize=9)

            if has_sleeve:
                sleeve_table = "Sleeve Pattern Coordinates:\n"
                sleeve_table += "-" * 30 + "\n"
                sleeve_table += "Point   X       Y\n"
                sleeve_table += "-" * 30 + "\n"

                # Add points from sleeve pieces
                for name, points in all_point_data:
                    if "sleeve" in name.lower():
                        for point_name, x, y in points:
                            if point_name.isdigit():
                                label = point_name
                                if "short" in name.lower() and point_name in ["17", "21"]:
                                    label = f"{point_name}(s)"
                                sleeve_table += f"{label:<8}{x:<8}{y:<8}\n"

                # Add box around sleeve table
                table_ax.add_patch(Rectangle((0.01, 0.01), 0.98, 0.44, fill=False,
                                             edgecolor='black', linewidth=1))
                table_ax.text(0.05, 0.45, sleeve_table, va='top', ha='left',
                              fontfamily='monospace', fontsize=9)

            # Add a note about seam allowance
            note = "Note: 1cm seam allowance\non all pattern pieces\nexcept where stated"
            table_ax.add_patch(Rectangle((0.7, 0.01), 0.28, 0.15, fill=True,
                                         facecolor='white', edgecolor='black', linewidth=1))
            table_ax.text(0.84, 0.08, note, va='center', ha='center',
                          fontsize=8, multialignment='center')

        # Set axis properties
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(max_y, min_y)  # Reverse Y axis to match pattern convention
        ax.set_xlabel('X-coordinate (cm)')
        ax.set_ylabel('Y-coordinate (cm)')
        ax.set_aspect('equal')
        ax.set_title(title)

        plt.tight_layout()

        return fig

    def export_pdf(self, filename: str):
        """Export technical views to a PDF file."""
        figures = self.render_technical_view()

        with PdfPages(filename) as pdf:
            for fig, _ in figures:
                pdf.savefig(fig)
                plt.close(fig)

            # Add a measurements page
            if self.pattern.measurements:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.axis('off')

                measurement_text = f"Measurements for {self.pattern.name}\n\n"

                for name, value in self.pattern.measurements.items():
                    measurement_text += f"{name}: {value:.1f} cm\n"

                ax.text(0.5, 0.5, measurement_text, ha='center', va='center', fontsize=12)

                pdf.savefig(fig)
                plt.close(fig)

    def export_all_simplified_svgs(self, base_filename: str):
        """
        Export simplified SVGs for all pattern pieces with auto-generated filenames.
        Preserves the exact sizes of all elements in the SVG.

        Args:
            base_filename: Base path for output files (e.g. "my_pattern" creates
                         "my_pattern_front_bodice.svg", "my_pattern_back.svg", etc)
        """
        if not self.pattern.pieces:
            raise ValueError("No pattern pieces found to export")

        # Create output directory if needed
        output_dir = os.path.dirname(base_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Get base name without extension
        base, ext = os.path.splitext(base_filename)
        if not ext:
            ext = ".svg"

        for piece_name, piece in self.pattern.pieces.items():
            # Generate safe filename
            sanitized_name = piece_name.lower().replace(" ", "_")
            filename = f"{base}_{sanitized_name}{ext}"

            # Calculate viewBox parameters
            min_point, max_point = piece.get_bounding_box()
            padding = 5

            # Create SVG file directly with proper dimensions
            with open(filename, 'w', encoding='utf-8') as f:
                # Calculate dimensions
                width = max_point.x - min_point.x + 2 * padding
                height = max_point.y - min_point.y + 2 * padding

                # Write SVG header with proper viewBox and dimensions in mm
                f.write(f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
                f.write(f'<svg xmlns="http://www.w3.org/2000/svg" ')
                f.write(f'viewBox="{min_point.x - padding} {min_point.y - padding} {width} {height}" ')
                f.write(f'width="{width}mm" height="{height}mm" ')
                f.write(f'preserveAspectRatio="xMidYMid meet">\n')
                f.write(f'<title>{piece_name}</title>\n')

                # Draw paths
                color = self.colors.get(piece_name, 'black')

                for path in piece.paths:
                    for segment in path:
                        if isinstance(segment, Line):
                            # Draw each line segment individually
                            f.write(f'<line x1="{segment.start.x}" y1="{segment.start.y}" ')
                            f.write(f'x2="{segment.end.x}" y2="{segment.end.y}" ')
                            f.write(f'stroke="{color}" stroke-width="0.5mm" />\n')

                        elif isinstance(segment, Curve):
                            # Handle curve segments using your existing as_tuple_list method
                            points = segment.as_tuple_list(30)  # Use the same number of points as original

                            if len(points) >= 2:
                                # Create polyline for the curve
                                points_str = " ".join([f"{x},{y}" for x, y in points])
                                f.write(f'<polyline points="{points_str}" ')
                                f.write(f'fill="none" stroke="{color}" stroke-width="0.5mm" />\n')

                # Close the SVG tag
                f.write('</svg>\n')