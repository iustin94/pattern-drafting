import math

from patterns.pattern_engine.src.tshirt.BaseSleeveBlock import BaseSleeveBlock


class ShortSleeveBlock(BaseSleeveBlock):
    """Short sleeve block with continuous curved hem construction."""
    
    SHORT_SLEEVE_LENGTH = 25

    def __init__(self, builder, measurements, piece_name, ease_fitting=False):
        super().__init__(
            builder, measurements, piece_name, ease_fitting
        )

    def _sleeve_length(self) -> float:
        return self.SHORT_SLEEVE_LENGTH

    def _create_sleeve_body(self):
        """Construct continuous sleeve path with measured curved hem."""
        m = self.measurements_system
        
        # Calculate sleeve bottom width using armhole dimensions
        sleeve_bottom = math.sqrt(
            (m.armhole_length + 2.5)**2 - m.half_scye_depth**2
        ) - 4

        # Build path sequence
        (self.builder
            .add_point("21", sleeve_bottom, self._sleeve_length())
            .add_bezier_curve_with_reference(
                start_point_name="18",
                end_point_name="21",
                reference_point_name="18",
                target_distance=m.armhole_length * 0.15
            )
        )

    def _add_common_paths(self):
        """Override to create curved hem connection."""
        (self.builder
            .add_line_path(["21", "17"])
            .add_bezier_curve("17", "15", 1.5, 0.6)  # Curved hem to underarm
        )