"""
T-Shirt Pattern Implementation with Technical Rendering.

This script implements a tee shirt pattern for jersey fabrics based on the provided instructions.
It uses the technical renderer to create pattern outputs similar to the provided SVG example.
"""
import math
import os

from src.Pattern import Pattern
from src.PatternDrafter import PatternDrafter
from src.TShirt.Drafter import TShirtDrafter
from src.TechnicalPatternRenderer import TechnicalPatternRenderer

def main():
    # Create output directory structure
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create measurements for size MEDIUM
    measurements = {
        "chest": 112,
        "half_back": 23,
        "back_neck_to_waist": 52,
        "scye_depth": 28,
        "neck_size": 44,
        "sleeve_length": 70,
        "close_wrist": 20,
        "finished_length": 70
    }

    # Create pattern drafters
    regular_drafter = TShirtDrafter(measurements, ease_fitting=False, short_sleeve=False)
    ease_drafter = TShirtDrafter(measurements, ease_fitting=True, short_sleeve=True)

    # Draft patterns
    regular_pattern = regular_drafter.draft()
    ease_pattern = ease_drafter.draft()

    # Define pattern directories
    regular_dir = os.path.join(output_dir, "regular_tshirt")
    ease_dir = os.path.join(output_dir, "ease_tshirt")

    # Create directories if they don't exist
    for directory in [regular_dir, ease_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Create technical renderers
    regular_renderer = TechnicalPatternRenderer(regular_pattern)
    ease_renderer = TechnicalPatternRenderer(ease_pattern)

    # Render and save the technical views
    regular_renderer.render_technical_view(os.path.join(regular_dir, "regular_tshirt_technical"))
    ease_renderer.render_technical_view(os.path.join(ease_dir, "ease_tshirt_technical"))

    # Export PDFs with all details
    regular_renderer.export_pdf(os.path.join(regular_dir, "regular_tshirt_technical.pdf"))
    ease_renderer.export_pdf(os.path.join(ease_dir, "ease_tshirt_technical.pdf"))

    print(f"T-shirt patterns generated successfully:")
    print(f"  - Regular fit long sleeve: {len(regular_pattern.pieces)} pieces - saved in {regular_dir}")
    print(f"  - Ease fit short sleeve: {len(ease_pattern.pieces)} pieces - saved in {ease_dir}")


if __name__ == "__main__":
    main()