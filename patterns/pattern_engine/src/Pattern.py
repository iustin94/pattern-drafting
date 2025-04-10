from matplotlib import pyplot as plt
from pyparsing import Dict

from patterns.pattern_engine.src.PatternPiece import PatternPiece


class Pattern:
    """Represents a complete pattern with multiple pieces."""

    def __init__(self, name: str):
        self.name = name
        self.pieces: Dict[str, PatternPiece] = {}
        self.measurements: Dict[str, float] = {}

    def add_piece(self, piece: PatternPiece) -> None:
        """Add a pattern piece to the pattern."""
        self.pieces[piece.name] = piece

    def get_piece(self, name: str) -> PatternPiece:
        """Get a pattern piece by name."""
        if name not in self.pieces:
            raise KeyError(f"Pattern piece '{name}' not found in pattern '{self.name}'")
        return self.pieces[name]

    def set_measurement(self, name: str, value: float) -> None:
        """Set a measurement value."""
        self.measurements[name] = value

    def get_measurement(self, name: str) -> float:
        """Get a measurement value."""
        if name not in self.measurements:
            raise KeyError(f"Measurement '{name}' not found in pattern '{self.name}'")
        return self.measurements[name]

    def render(self, separate: bool = False):
        """Render all pattern pieces.
        
        Args:
            separate: If True, render each piece on a separate subplot,
                     otherwise arrange them in a grid.
        """
        if separate:
            figs = []
            for name, piece in self.pieces.items():
                fig = piece.render()
                figs.append(fig)
            return figs
        else:
            n = len(self.pieces)
            cols = min(3, n)
            rows = (n + cols - 1) // cols

            fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 5 * rows))
            if n == 1:
                axes = [axes]
            else:
                axes = axes.flatten()

            for i, (name, piece) in enumerate(self.pieces.items()):
                if i < len(axes):
                    piece.render(ax=axes[i])

            # Hide unused subplots
            for i in range(n, len(axes)):
                axes[i].axis('off')

            plt.tight_layout()
            plt.suptitle(self.name, fontsize=16)
            return fig

    def save_pdf(self, filename: str):
        """Save the pattern as a PDF file."""
        fig = self.render()
        fig.savefig(filename, format='pdf')
        plt.close(fig)

    def save_svg(self, filename: str):
        """Save the pattern as an SVG file."""
        fig = self.render()
        fig.savefig(filename, format='svg')
        plt.close(fig)

