"""
Pattern class implementation using Shapely and Matplotlib.

This module replaces the original Pattern class with one based on Shapely
geometries and Matplotlib for rendering and export.
"""
import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from patterns.pattern_engine.src.core.PatternPiece import PatternPiece


class Pattern:
    """
    Represents a complete pattern with multiple pieces.

    This implementation uses Shapely geometries and Matplotlib for
    rendering and export functionality.
    """

    def __init__(self, name: str):
        """
        Initialize a pattern.

        Args:
            name: Name for the pattern
        """
        self.name = name
        self.pieces: Dict[str, PatternPiece] = {}
        self.measurements: Dict[str, float] = {}

    def add_piece(self, piece: PatternPiece) -> None:
        """
        Add a pattern piece to the pattern.

        Args:
            piece: PatternPiece object to add
        """
        self.pieces[piece.name] = piece

    def get_piece(self, name: str) -> PatternPiece:
        """
        Get a pattern piece by name.

        Args:
            name: Name of the piece to retrieve

        Returns:
            The requested PatternPiece

        Raises:
            KeyError: If the pattern piece is not found
        """
        if name not in self.pieces:
            raise KeyError(f"Pattern piece '{name}' not found in pattern '{self.name}'")
        return self.pieces[name]

    def set_measurement(self, name: str, value: float) -> None:
        """
        Set a measurement value.

        Args:
            name: Measurement name
            value: Measurement value
        """
        self.measurements[name] = value

    def get_measurement(self, name: str) -> float:
        """
        Get a measurement value.

        Args:
            name: Measurement name

        Returns:
            The measurement value

        Raises:
            KeyError: If the measurement is not found
        """
        if name not in self.measurements:
            raise KeyError(f"Measurement '{name}' not found in pattern '{self.name}'")
        return self.measurements[name]

    def get_bounding_box(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Get the bounding box of the entire pattern.

        Returns:
            Tuple of ((min_x, min_y), (max_x, max_y))
        """
        if not self.pieces:
            return ((0, 0), (0, 0))

        # Calculate combined bounding box of all pieces
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')

        for piece in self.pieces.values():
            min_point, max_point = piece.get_bounding_box()
            min_x = min(min_x, min_point.x)
            min_y = min(min_y, min_point.y)
            max_x = max(max_x, max_point.x)
            max_y = max(max_y, max_point.y)

        return ((min_x, min_y), (max_x, max_y))

    def render(self, separate: bool = False, show_seam_allowance: bool = True,
               show_fold_lines: bool = True, add_title: bool = True):
        """
        Render all pattern pieces.

        Args:
            separate: If True, render each piece on a separate figure,
                     otherwise arrange them in a grid
            show_seam_allowance: Whether to show seam allowances
            show_fold_lines: Whether to show fold lines
            add_title: Whether to add a title to the figure

        Returns:
            List of figures if separate=True, otherwise a single figure
        """
        if not self.pieces:
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.text(0.5, 0.5, "No pattern pieces", ha='center', va='center', fontsize=12)
            ax.axis('off')
            return [fig] if separate else fig

        if separate:
            figures = []
            for name, piece in self.pieces.items():
                fig = piece.render(color=self._get_piece_color(name),
                                   show_seam_allowance=show_seam_allowance,
                                   show_fold_line=show_fold_lines)
                figures.append(fig)
            return figures
        else:
            # Arrange pieces in a grid
            n_pieces = len(self.pieces)
            cols = min(3, n_pieces)  # Maximum of 3 columns
            rows = (n_pieces + cols - 1) // cols  # Ceiling division

            fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 5 * rows), squeeze=False)
            axes = axes.flatten()

            for i, (name, piece) in enumerate(self.pieces.items()):
                if i < len(axes):
                    piece.render(ax=axes[i], color=self._get_piece_color(name),
                                 show_seam_allowance=show_seam_allowance,
                                 show_fold_line=show_fold_lines)

            # Hide unused subplots
            for i in range(n_pieces, len(axes)):
                axes[i].axis('off')

            if add_title:
                plt.suptitle(self.name, fontsize=16, y=0.98)

            plt.tight_layout(rect=[0, 0, 1, 0.96])  # Leave space for the title
            return fig

    def _get_piece_color(self, piece_name: str) -> str:
        """
        Get a consistent color for a pattern piece based on its name.

        Args:
            piece_name: Name of the pattern piece

        Returns:
            Color string for the piece
        """
        # Define colors for common piece types
        if "back" in piece_name.lower():
            return 'blue'
        elif "front" in piece_name.lower():
            return 'red'
        elif "sleeve" in piece_name.lower():
            return 'green'
        elif "collar" in piece_name.lower():
            return 'purple'
        elif "pocket" in piece_name.lower():
            return 'orange'
        else:
            return 'black'

    def save_pdf(self, filename: str, separate_pages: bool = True,
                 include_measurements: bool = True) -> str:
        """
        Save the pattern as a PDF file.

        Args:
            filename: Path to save the PDF file
            separate_pages: Whether to put each piece on a separate page
            include_measurements: Whether to include a page with measurements

        Returns:
            Path to the saved PDF file
        """
        # Create directory if needed
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

        with PdfPages(filename) as pdf:
            if separate_pages:
                # Each piece on a separate page
                for name, piece in self.pieces.items():
                    fig = piece.render(color=self._get_piece_color(name))
                    pdf.savefig(fig)
                    plt.close(fig)
            else:
                # All pieces on one page
                fig = self.render(separate=False)
                pdf.savefig(fig)
                plt.close(fig)

            # Add measurements page if requested
            if include_measurements and self.measurements:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.axis('off')

                # Create a table of measurements
                # Calculate how many rows we need
                n_measurements = len(self.measurements)
                cols = 2  # Two columns: name and value
                rows = n_measurements + 1  # +1 for header

                # Create table data
                cell_text = []
                header = ['Measurement', 'Value (cm)']

                # Sort measurements alphabetically
                for name, value in sorted(self.measurements.items()):
                    cell_text.append([name, f"{value:.1f}"])

                # Create the table
                table = ax.table(
                    cellText=cell_text,
                    colLabels=header,
                    loc='center',
                    cellLoc='left'
                )

                # Style the table
                table.auto_set_font_size(False)
                table.set_fontsize(10)
                table.scale(1, 1.5)  # Increase row height

                # Add a title
                plt.title(f"Measurements for {self.name}", fontsize=14, pad=20)

                pdf.savefig(fig)
                plt.close(fig)

        return filename

    def save_svg(self, filename: str, separate: bool = True) -> List[str]:
        """
        Save the pattern as SVG file(s).

        Args:
            filename: Base path to save the SVG file(s)
            separate: Whether to save each piece as a separate SVG

        Returns:
            List of paths to the saved SVG files
        """
        # Create directory if needed
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

        svg_files = []

        if separate:
            # Save each piece as a separate SVG
            base, ext = os.path.splitext(filename)
            if not ext:
                ext = '.svg'

            for name, piece in self.pieces.items():
                # Create safe filename
                safe_name = name.lower().replace(' ', '_')
                piece_filename = f"{base}_{safe_name}{ext}"

                # Export the piece
                piece.export_svg(piece_filename)
                svg_files.append(piece_filename)
        else:
            # Make sure filename ends with .svg
            if not filename.lower().endswith('.svg'):
                filename += '.svg'

            # Render all pieces on one figure
            fig = self.render(separate=False)
            fig.savefig(filename, format='svg', bbox_inches='tight')
            plt.close(fig)
            svg_files.append(filename)

        return svg_files

    def add_seam_allowance(self, allowance: float = None) -> 'Pattern':
        """
        Create a new pattern with seam allowance added to all pieces.

        Args:
            allowance: Seam allowance to add (uses piece.seam_allowance if None)

        Returns:
            New Pattern with seam allowance added to all pieces
        """
        new_pattern = Pattern(f"{self.name}_with_seam_allowance")

        # Copy measurements
        for name, value in self.measurements.items():
            new_pattern.set_measurement(name, value)

        # Add seam allowance to each piece
        for name, piece in self.pieces.items():
            # Use the piece's seam allowance if allowance is None
            piece_allowance = allowance if allowance is not None else piece.seam_allowance

            if piece_allowance > 0:
                new_piece = piece.add_seam_allowance(piece_allowance)
                new_pattern.add_piece(new_piece)
            else:
                # If no seam allowance, just copy the piece
                new_pattern.add_piece(piece)

        return new_pattern