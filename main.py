"""
Pattern Drafting System Demonstration

This script shows how to use the pattern drafting system to create, visualize,
and export various pattern types with the new technical rendering.
"""
import os

from patterns.pattern_engine.src.pant.Drafter import PantDrafter, PantMeasurements
from patterns.pattern_engine.src.core.TechnicalPatternRenderer import TechnicalPatternRenderer


def create_output_directory(pattern_name):
    """Create an output directory for a pattern if it doesn't exist."""
    base_dir = "outputs"
    pattern_dir = os.path.join(base_dir, pattern_name)

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    if not os.path.exists(pattern_dir):
        os.makedirs(pattern_dir)

    return pattern_dir


def generate_tshirt_patterns():
    """Generate T-shirt patterns with different options."""
    # Size chart for different sizes
    size_charts = {
            "JUSTIN": {
            "chest": 112,
            "half_back": 23,
            "back_neck_to_waist": 52,
            "scye_depth": 28,
            "neck_size": 44,
            "sleeve_length": 70,
            "close_wrist": 20,
            "finished_length": 70
        }
    }

    # Generate patterns for selected sizes
    sizes_to_generate = ["JUSTIN"]
    fitting_options = [
        {"ease_fitting": True, "short_sleeve": True, "name": "ease_fit_short_sleeve"},
    ]

    for size in sizes_to_generate:
        measurements = size_charts[size]

        for option in fitting_options:
            pattern_name = f"{size.lower()}_{option['name']}"
            output_dir = create_output_directory(pattern_name)

            # Create and draft pattern
            drafter = TShirtDrafter(
                measurements,
                ease_fitting=option['ease_fitting'],
                short_sleeve=option['short_sleeve']
            )
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
            
            renderer.export_all_simplified_svgs(
                os.path.join(output_dir, f"{pattern_name}_lasercut")
            )

            print(f"Generated {pattern_name} pattern in {output_dir}")


def generate_combined_pattern():
    """Generate a T-shirt pattern with both sleeve options."""
    # Use MEDIUM size for the combined pattern
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
    pattern_name = "tshirt_combined"
    output_dir = create_output_directory(pattern_name)

    # Create long sleeve pattern (base pattern)
    long_drafter = TShirtDrafter(measurements, ease_fitting=True, short_sleeve=False)
    long_pattern = long_drafter.draft()

    # Create short sleeve pattern
    short_drafter = TShirtDrafter(measurements, ease_fitting=True, short_sleeve=True)
    short_pattern = short_drafter.draft()

    # Add short sleeve to combined pattern
    short_sleeve = short_pattern.pieces["Short Sleeve"]
    long_pattern.add_piece(short_sleeve)

    # Create technical renderer for combined pattern
    renderer = TechnicalPatternRenderer(long_pattern)

    # Generate technical views
    renderer.render_technical_view(
        os.path.join(output_dir, f"{pattern_name}_technical")
    )

    # Generate PDF with all details
    renderer.export_pdf(
        os.path.join(output_dir, f"{pattern_name}_technical.pdf")
    )

    print(f"Generated combined T-shirt pattern with both sleeve options in {output_dir}")


def generate_pant_patterns():
    """Generate pant patterns with different options."""
    # Size chart for different sizes


    measurements: PantMeasurements = {
        "body_rise": 28,
        "inside_leg": 92,
        "seat_measurement": 119,
        "waist_measurement": 111
    }
    
    # Generate patterns for selected sizes
    sizes_to_generate = ["JUSTIN"]
    fitting_options = [
        {"ease_fitting": True, "name": "ease_fit"},
        {"ease_fitting": False, "name": "standard_fit"}
    ]

    for option in fitting_options:
        pattern_name = f"pants_{option['name']}"
        output_dir = create_output_directory(pattern_name)

        # Create and draft pattern
        drafter = PantDrafter(
            measurements,
            ease_fitting=option['ease_fitting']
        )
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

        renderer.export_all_simplified_svgs(
            os.path.join(output_dir, f"{pattern_name}_lasercut")
        )

        print(f"Generated {pattern_name} pattern in {output_dir}")


def generate_all_patterns():
    """Generate all pattern types."""
    print("Generating T-shirt patterns...")
    generate_tshirt_patterns()

    print("\nGenerating pant patterns...")
    generate_pant_patterns()

    print("\nGenerating combined T-shirt pattern...")
    generate_combined_pattern()

    print("\nAll patterns generated successfully!")


if __name__ == "__main__":
    generate_all_patterns()