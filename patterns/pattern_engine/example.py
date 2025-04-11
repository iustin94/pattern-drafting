"""
Example script demonstrating the Shapely and Matplotlib-based pattern drafting system.

This script shows how to use the pattern drafting system to create
T-shirt and pants patterns with features like hems.
"""
import os
import sys

from src.core.TechnicalPatternRenderer import TechnicalPatternRenderer
from src.tshirt.TShirtDrafter import TShirtDrafter
# from src.pant.PantDrafter import PantDrafter

# Import from the pattern engine package

def create_output_directory(pattern_name):
    """Create an output directory for a pattern if it doesn't exist."""
    base_dir = "outputs/shapely"
    pattern_dir = os.path.join(base_dir, pattern_name)

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    if not os.path.exists(pattern_dir):
        os.makedirs(pattern_dir)

    return pattern_dir


def generate_tshirt_with_features():
    """Generate a T-shirt pattern with features using the Shapely-based system."""
    # Define measurements for size MEDIUM
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
    pattern_name = "tshirt_with_features"
    output_dir = create_output_directory(pattern_name)

    # Create a T-shirt drafter with features
    drafter = TShirtDrafter(
        measurements=measurements,
        ease_fitting=True,
        short_sleeve=False  # Long sleeve
    )

    # Add a hem feature
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
    svg_files = renderer.export_all_simplified_svgs(
        os.path.join(output_dir, f"{pattern_name}_lasercut")
    )

    print(f"Generated T-shirt pattern with hem feature in {output_dir}")
    for svg in svg_files:
        print(f"  - {os.path.basename(svg)}")


def generate_tshirt_variations():
    """Generate multiple T-shirt variations using the Shapely-based system."""
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

    # Define variations to generate
    variations = [
        {
            "name": "standard_long_sleeve",
            "ease_fitting": False,
            "short_sleeve": False,
            "features": []
        },
        {
            "name": "standard_short_sleeve",
            "ease_fitting": False,
            "short_sleeve": True,
            "features": []
        },
        {
            "name": "ease_long_sleeve_with_hem",
            "ease_fitting": True,
            "short_sleeve": False,
            "features": [("hem", {"hem_width": 3.0})]
        },
        {
            "name": "ease_short_sleeve_with_hem",
            "ease_fitting": True,
            "short_sleeve": True,
            "features": [("hem", {"hem_width": 2.0})]
        }
    ]

    # Generate each variation
    for variant in variations:
        output_dir = create_output_directory(variant["name"])

        # Create drafter
        drafter = TShirtDrafter(
            measurements=measurements,
            ease_fitting=variant["ease_fitting"],
            short_sleeve=variant["short_sleeve"]
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

        # Also directly export SVGs using the Pattern class
        pattern.save_svg(os.path.join(output_dir, f"{variant['name']}.svg"), separate=True)

        print(f"Generated {variant['name']} in {output_dir}")


# def generate_pants_with_hem():
#     """Generate a pant pattern with hem feature using the Shapely-based system."""
#     # Define measurements
#     measurements = {
#         "body_rise": 28,
#         "inside_leg": 92,
#         "seat_measurement": 119,
#         "waist_measurement": 111
#     }
#
#     # Create output directory
#     pattern_name = "pants_with_hem"
#     output_dir = create_output_directory(pattern_name)
#
#     # # Create a pant drafter with a hem feature
#     # drafter = PantDrafter(
#     #     measurements=measurements,
#     #     ease_fitting=True
#     # )
#
#     # Add a 4cm hem at the bottom
#     drafter.add_feature("hem", hem_width=4.0)
#
#     # Draft the pattern
#     pattern = drafter.draft()
#
#     # Create technical renderer
#     renderer = TechnicalPatternRenderer(pattern)
#
#     # Generate technical views
#     renderer.render_technical_view(
#         os.path.join(output_dir, f"{pattern_name}_technical")
#     )
#
#     # Generate PDF with all details
#     renderer.export_pdf(
#         os.path.join(output_dir, f"{pattern_name}_technical.pdf")
#     )
#
#     # Export SVGs for each piece
#     svg_files = renderer.export_all_simplified_svgs(
#         os.path.join(output_dir, f"{pattern_name}_lasercut")
#     )
#
#     print(f"Generated pant pattern with hem feature in {output_dir}")
#     for svg in svg_files:
#         print(f"  - {os.path.basename(svg)}")


def generate_full_outfit():
    """Generate a complete outfit with matching T-shirt and pants."""
    # Define measurements for T-shirt
    tshirt_measurements = {
        "chest": 100,
        "half_back": 20,
        "back_neck_to_waist": 44.2,
        "scye_depth": 24.4,
        "neck_size": 40,
        "sleeve_length": 65,
        "close_wrist": 17.8,
        "finished_length": 70
    }

    # Define measurements for pants
    pant_measurements = {
        "body_rise": 28,
        "inside_leg": 92,
        "seat_measurement": 119,
        "waist_measurement": 111
    }

    # Create output directory
    outfit_dir = create_output_directory("full_outfit")

    # Create T-shirt with hem
    tshirt_drafter = TShirtDrafter(
        measurements=tshirt_measurements,
        ease_fitting=True,
        short_sleeve=True
    )
    tshirt_drafter.add_feature("hem", hem_width=2.5)
    tshirt_pattern = tshirt_drafter.draft()

    # # Create pants with hem
    # pant_drafter = PantDrafter(
    #     measurements=pant_measurements,
    #     ease_fitting=True
    # )
    # pant_drafter.add_feature("hem", hem_width=4.0)
    # pant_pattern = pant_drafter.draft()

    # Create combined pattern renderer
    from patterns.pattern_engine.src.core.Pattern import Pattern

    # Create a combined pattern with all pieces
    combined_pattern = Pattern("Full Outfit")
    for name, piece in tshirt_pattern.pieces.items():
        combined_pattern.add_piece(piece)
    for name, piece in pant_pattern.pieces.items():
        combined_pattern.add_piece(piece)

    # Create a renderer for the combined pattern
    renderer = TechnicalPatternRenderer(combined_pattern)

    # Generate combined technical view
    renderer.render_technical_view(
        os.path.join(outfit_dir, "full_outfit_technical")
    )

    # Generate PDF with all details
    renderer.export_pdf(
        os.path.join(outfit_dir, "full_outfit_technical.pdf")
    )

    # Export SVGs for all pieces
    svg_files = renderer.export_all_simplified_svgs(
        os.path.join(outfit_dir, "full_outfit_lasercut")
    )

    print(f"Generated complete outfit in {outfit_dir}")
    print(f"Pattern includes {len(combined_pattern.pieces)} pattern pieces")


if __name__ == "__main__":
    print("Generating T-shirt with features...")
    generate_tshirt_with_features()

    print("\nGenerating T-shirt variations...")
    generate_tshirt_variations()

    # print("\nGenerating pants with hem...")
    # generate_pants_with_hem()

    # print("\nGenerating full outfit...")
    # generate_full_outfit()
    
    print("\nAll patterns generated successfully!")