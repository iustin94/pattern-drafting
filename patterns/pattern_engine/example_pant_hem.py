"""
Example script demonstrating pants with hem feature.

This script shows how to use the refactored pattern drafting system to create
pant patterns with hem features.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import from the pattern engine package
# This ensures all features are properly registered
from patterns.pattern_engine import HemFeature, PantDrafter
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


def generate_pants_with_hem():
    """Generate a pant pattern with hem feature using the new system."""
    # Define measurements
    measurements = {
        "body_rise": 28,
        "inside_leg": 92,
        "seat_measurement": 119,
        "waist_measurement": 111
    }

    # Create output directory
    pattern_name = "pants_with_hem"
    output_dir = create_output_directory(pattern_name)

    # Create a pant drafter with a hem feature
    drafter = PantDrafter(
        measurements=measurements,
        ease_fitting=True
    )

    # Add a 4cm hem at the bottom
    drafter.add_feature("hem", hem_width=4.0)

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

    print(f"Generated pant pattern with hem feature in {output_dir}")


def generate_pant_variations():
    """Generate multiple pant variations using the new system."""
    # Define measurements
    measurements = {
        "body_rise": 28,
        "inside_leg": 92,
        "seat_measurement": 119,
        "waist_measurement": 111
    }

    # Define variations to generate
    variations = [
        {
            "name": "standard_pants",
            "ease_fitting": False,
            "features": []
        },
        {
            "name": "standard_pants_with_hem",
            "ease_fitting": False,
            "features": [("hem", {"hem_width": 4.0})]
        },
        {
            "name": "ease_pants",
            "ease_fitting": True,
            "features": []
        },
        {
            "name": "ease_pants_with_hem",
            "ease_fitting": True,
            "features": [("hem", {"hem_width": 4.0})]
        }
    ]

    # Generate each variation
    for variant in variations:
        output_dir = create_output_directory(variant["name"])

        # Create drafter
        drafter = PantDrafter(
            measurements=measurements,
            ease_fitting=variant["ease_fitting"]
        )

        # Add features
        for feature_name, feature_options in variant["features"]:
            drafter.add_feature(feature_name, **feature_options)

        # Draft pattern
        pattern = drafter.draft()

        # Create renderer
        renderer = TechnicalPatternRenderer(pattern)

        # Generate outputs
        renderer.render_technical_view(
            os.path.join(output_dir, f"{variant['name']}_technical")
        )

        renderer.export_pdf(
            os.path.join(output_dir, f"{variant['name']}_technical.pdf")
        )

        print(f"Generated {variant['name']} in {output_dir}")


if __name__ == "__main__":
    print("Generating pants with hem feature...")
    generate_pants_with_hem()

    print("\nGenerating pant variations...")
    generate_pant_variations()

    print("\nAll patterns generated successfully!")