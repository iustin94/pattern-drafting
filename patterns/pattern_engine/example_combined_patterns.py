"""
Example script demonstrating multiple pattern types with various features.

This script shows how to create both T-shirts and pants with different
features using the refactored pattern system.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import from the pattern engine package
from patterns.pattern_engine import (
    TShirtDrafter, PantDrafter
)
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
    
    # Create output directories
    tshirt_dir = create_output_directory("outfit_tshirt")
    pant_dir = create_output_directory("outfit_pants")
    
    # Create T-shirt with hem
    tshirt_drafter = TShirtDrafter(
        measurements=tshirt_measurements,
        ease_fitting=True,
        short_sleeve=True
    )
    tshirt_drafter.add_feature("hem", hem_width=2.5)
    tshirt_pattern = tshirt_drafter.draft()
    
    # Create pants with hem
    pant_drafter = PantDrafter(
        measurements=pant_measurements,
        ease_fitting=True
    )
    pant_drafter.add_feature("hem", hem_width=4.0)
    pant_pattern = pant_drafter.draft()
    
    # Render T-shirt
    tshirt_renderer = TechnicalPatternRenderer(tshirt_pattern)
    tshirt_renderer.render_technical_view(
        os.path.join(tshirt_dir, "outfit_tshirt_technical")
    )
    tshirt_renderer.export_pdf(
        os.path.join(tshirt_dir, "outfit_tshirt_technical.pdf")
    )
    tshirt_renderer.export_all_simplified_svgs(
        os.path.join(tshirt_dir, "outfit_tshirt_lasercut")
    )
    
    # Render pants
    pant_renderer = TechnicalPatternRenderer(pant_pattern)
    pant_renderer.render_technical_view(
        os.path.join(pant_dir, "outfit_pants_technical")
    )
    pant_renderer.export_pdf(
        os.path.join(pant_dir, "outfit_pants_technical.pdf")
    )
    pant_renderer.export_all_simplified_svgs(
        os.path.join(pant_dir, "outfit_pants_lasercut")
    )
    
    print(f"Generated T-shirt pattern in {tshirt_dir}")
    print(f"Generated pants pattern in {pant_dir}")
    print("Complete outfit with hem features generated successfully!")


def generate_size_ranges():
    """Generate patterns in multiple sizes using measurement scaling."""
    # Base measurements for a medium size
    base_tshirt_measurements = {
        "chest": 100,
        "half_back": 20,
        "back_neck_to_waist": 44.2,
        "scye_depth": 24.4,
        "neck_size": 40,
        "sleeve_length": 65,
        "close_wrist": 17.8,
        "finished_length": 70
    }
    
    # Define size scaling factors
    size_scales = {
        "S": 0.9,
        "M": 1.0,  # Base size
        "L": 1.1,
        "XL": 1.2
    }
    
    # Generate T-shirts for each size
    for size, scale in size_scales.items():
        # Scale measurements
        scaled_measurements = {
            key: value * scale for key, value in base_tshirt_measurements.items()
        }
        
        # Create output directory
        output_dir = create_output_directory(f"tshirt_size_{size}")
        
        # Create T-shirt drafter
        drafter = TShirtDrafter(
            measurements=scaled_measurements,
            ease_fitting=True,
            short_sleeve=False
        )
        
        # Add hem feature
        drafter.add_feature("hem", hem_width=2.5)
        
        # Draft pattern
        pattern = drafter.draft()
        
        # Render pattern
        renderer = TechnicalPatternRenderer(pattern)
        renderer.render_technical_view(
            os.path.join(output_dir, f"tshirt_size_{size}_technical")
        )
        renderer.export_pdf(
            os.path.join(output_dir, f"tshirt_size_{size}_technical.pdf")
        )
        
        print(f"Generated T-shirt size {size} in {output_dir}")
    
    print("All size variations generated successfully!")


if __name__ == "__main__":
    print("Generating full outfit...")
    generate_full_outfit()
    
    print("\nGenerating size range T-shirts...")
    generate_size_ranges()
    
    print("\nAll examples completed successfully!")