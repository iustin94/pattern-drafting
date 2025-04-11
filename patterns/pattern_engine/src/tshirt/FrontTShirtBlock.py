from patterns.pattern_engine.src.tshirt.BaseTShirtBlock import BaseTShirtBlock


class FrontTShirtBlock(BaseTShirtBlock):
    """Front piece with continuous path construction."""

    def draft(self):
        """Draft front piece as single continuous path."""
        self.start_piece()
        self.add_core_points()

        # Add front-specific points
        self.builder.add_point("14", 0, self.measurements.neck_size / 5 - 2)

        # Build path in sequence
        (self.builder
         .add_bezier_curve("7", "14", -2.5, 0.5)  # Neck curve
         .add_line_path(["14", "2", "13", "12"])  # Side seam
         .add_bezier_curve("12", "9", 2.5, 0.7)  # Armhole curve part 1
         .add_bezier_curve("9", "11", 0.25, 0.3)  # Armhole curve part 2
         .add_line_path(["11", "7"])  # Shoulder line
         )

        self.builder.set_seam_allowance(1.0)
        self.end_piece()


