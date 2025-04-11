from patterns.pattern_engine.src.tshirt.BaseTShirtBlock import BaseTShirtBlock


class BackTShirtBlock(BaseTShirtBlock):
    """Back piece with optimized path flow."""

    def draft(self):
        """Construct back piece as continuous loop."""
        self.start_piece()
        self.add_core_points()

        # Build path sequence
        (self.builder
         .add_bezier_curve("0", "7", 0.75, 0.8)  # Back neck curve
         .add_line_path(["7", "11"])  # Shoulder line
         .add_bezier_curve("11", "9", 0.25, 0.3)  # Armhole curve
         .add_bezier_curve("9", "12", 2.5, 0.7)  # Underarm curve
         .add_line_path(["12", "13", "2", "0"])  # Side seam and hem
         )

        self.builder.set_seam_allowance(1.0)
        self.end_piece()
