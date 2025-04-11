from patterns.pattern_engine.src.tshirt.BaseSleeveBlock import BaseSleeveBlock

class LongSleeveBlock(BaseSleeveBlock):
    """Long sleeve block with measurement inheritance"""

    def __init__(self, builder, measurements, ease_fitting=False):
        super().__init__(
            builder=builder,
            measurements=measurements,
            piece_name="Long Sleeve",
            ease_fitting=ease_fitting
        )

    def _sleeve_length(self) -> float:
        return self.measurements_system.sleeve_length

    def _create_sleeve_body(self):
        """Construct sleeve with measurement-driven dimensions"""
        m = self.measurements_system
        wrist_width = m.wrist_circumference / 2 + m.WRIST_EASE

        (self.builder
         .add_point("21", wrist_width, self._sleeve_length())
         .add_bezier_curve("18", "21", 2, 0.5)
         )