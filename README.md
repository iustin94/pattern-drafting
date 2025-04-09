# Pattern Drafting System

A Python library for creating, manipulating, and rendering clothing patterns in a declarative way.

## Features

- Define pattern pieces with a declarative API
- Support for various geometric operations in pattern creation
- Bezier curve support for smooth pattern lines
- Visualization tools with matplotlib
- Export patterns as SVG or PDF files
- Support for common pattern features: darts, seam allowances, notches, etc.

## Installation

```bash
pip install pattern-drafting
```

## Quick Start

Here's a simple example of creating a basic rectangle pattern:

```python
from pattern_drafting import PatternBuilder

# Create a pattern
builder = PatternBuilder("Simple Rectangle")

# Add measurements
builder.add_measurements(
    width=50,
    height=75
)

# Create a pattern piece
builder.start_piece("Rectangle")

# Define the points
builder.add_point("top_left", 0, 0)
builder.add_point("top_right", 50, 0)
builder.add_point("bottom_right", 50, 75)
builder.add_point("bottom_left", 0, 75)

# Define the outline path
builder.add_line_path(["top_left", "top_right", "bottom_right", "bottom_left", "top_left"])

# Add seam allowance
builder.set_seam_allowance(1.0)

# Finish the piece
builder.end_piece()

# Build the pattern
pattern = builder.build()

# Render and save
pattern.save_svg("rectangle.svg")
pattern.save_pdf("rectangle.pdf")
```

## Advanced Example

For more complex patterns, see the example implementations:

- Basic skirt pattern: `example_skirt.py`
- Fitted bodice pattern: `example_bodice.py`

These examples demonstrate more advanced techniques like darts, curves, and princess seams.

## Usage for Pattern Drafting

The library is designed to be used for:

1. **Pattern Creation**: Define patterns using geometric operations
2. **Pattern Visualization**: Render patterns with customizable styles
3. **Pattern Export**: Save patterns in various formats for printing or further editing

## License

MIT License