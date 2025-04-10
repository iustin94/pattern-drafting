"""
Example script demonstrating the refactored pattern drafting system.

This script shows how to use the new pattern drafting system to create
T-shirt patterns with features like hems.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Import from the pattern engine package
# This ensures all features are properly registered
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


def generate_tshirt_with_features():
    """Generate a T-shirt pattern with features using the new system."""
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
    renderer.export_all_simplified_svgs(
        os.path.join(output_dir, f"{pattern_name}_lasercut")
    )

    print(f"Generated T-shirt pattern with hem feature in {output_dir}")


def generate_tshirt_variations():
    """Generate multiple T-shirt variations using the new system."""
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
        
        print(f"Generated {variant['name']} in {output_dir}")


if __name__ == "__main__":
    print("Generating T-shirt with features...")
    generate_tshirt_with_features()
    
    print("\nGenerating T-shirt variations...")
    generate_tshirt_variations()
    
    print("\nAll patterns generated successfully!")