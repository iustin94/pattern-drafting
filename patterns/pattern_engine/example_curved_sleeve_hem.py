"""
Example script demonstrating curved hem creation.

This script specifically shows how the improved sleeve implementation
properly supports curved hems.
"""
import os
import sys
import math

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import from the pattern engine package
from patterns.pattern_engine import HemFeature, TShirtDrafter
from patterns.pattern_engine.src.TechnicalPatternRenderer import TechnicalPatternRenderer


def create_output_directory(pattern_name):
    """Create an output directory for a pattern if it doesn't exist."""
    base_dir = "outputs"
    pattern_dir = os.path.join(base_dir, pattern_name)

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    if not os.path.exists(pattern_dir):
        os.makedirs(pattern_dir)

    return pattern_dir


def generate_sleeve_with_curved_hem():
    """Generate a short sleeve with a curved hem that properly mirrors the edge."""
    # Define measurements
    measurements = {
        "chest": 100,
        "half_back": 20,
        "back_neck_to_waist": 44.2,
        "scye_depth": 24.4,
        "neck_size": 40,
        "sleeve_length": 65,
        "close_wrist": 17.8,
        "finished_length": 70
    }

    # Create various hem widths for comparison
    hem_widths = [2.0, 3.0, 4.0]

    for hem_width in hem_widths:
        # Create output directory
        pattern_name = f"curved_hem_sleeve_{int(hem_width)}"
        output_dir = create_output_directory(pattern_name)

        # Create a T-shirt drafter with short sleeve
        drafter = TShirtDrafter(
            measurements=measurements,
            ease_fitting=True,
            short_sleeve=True
        )

        # Add a hem feature that targets only the sleeve
        drafter.add_feature("hem", hem_width=hem_width, piece_names=["Short Sleeve"])

        # Draft the pattern
        pattern = drafter.draft()

        # Create technical renderer
        renderer = TechnicalPatternRenderer(pattern)

        # Generate technical views
        renderer.render_technical_view(
            os.path.join(output_dir, f"{pattern_name}_technical")
        )

        # Generate PDF with all details
        renderer.export_pdf(
            os.path.join(output_dir, f"{pattern_name}_technical.pdf")
        )

        # Export SVGs for each piece
        renderer.export_all_simplified_svgs(
            os.path.join(output_dir, f"{pattern_name}_lasercut")
        )

        print(f"Generated sleeve with {hem_width}cm curved hem in {output_dir}")


def generate_tshirt_with_curved_hem():
    """Generate a complete T-shirt with curved hems on all pieces."""
    # Define measurements
    measurements = {
        "chest": 100,
        "half_back": 20,
        "back_neck_to_waist": 44.2,
        "scye_depth": 24.4,
        "neck_size": 40,
        "sleeve_length": 65,
        "close_wrist": 17.8,
        "finished_length": 70
    }

    # Create output directory
    pattern_name = "tshirt_curved_hem"
    output_dir = create_output_directory(pattern_name)

    # Create a T-shirt drafter with short sleeve
    drafter = TShirtDrafter(
        measurements=measurements,
        ease_fitting=True,
        short_sleeve=True
    )

    # Add a hem feature for all pieces
    drafter.add_feature("hem", hem_width=3.0)

    # Draft the pattern
    pattern = drafter.draft()

    # Create technical renderer
    renderer = TechnicalPatternRenderer(pattern)

    # Generate technical views
    renderer.render_technical_view(
        os.path.join(output_dir, f"{pattern_name}_technical")
    )

    # Generate PDF with all details
    renderer.export_pdf(
        os.path.join(output_dir, f"{pattern_name}_technical.pdf")
    )

    # Export SVGs for each piece
    renderer.export_all_simplified_svgs(
        os.path.join(output_dir, f"{pattern_name}_lasercut")
    )

    print(f"Generated complete T-shirt with curved hems in {output_dir}")


if __name__ == "__main__":
    print("Generating sleeve with curved hem examples...")
    generate_sleeve_with_curved_hem()

    print("\nGenerating complete T-shirt with curved hems...")
    generate_tshirt_with_curved_hem()

    print("\nAll examples completed successfully!")