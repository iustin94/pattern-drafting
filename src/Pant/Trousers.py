import math

from src.Pant.Body import FrontPantBlock, BackPantBlock
from src.Point import Point
from src.Util import Util


class ModifiedFrontPantBlock(FrontPantBlock):
    """
    Modified front pant block with pocket and additional modifications
    """

    def draft(self):
        """
        Draft the modified front pant block with pocket and modifications
        """
        # Ensure the piece is started
        if not self.builder.current_piece:
            self.builder.start_piece("Front")

        # Perform the base front block drafting
        # First, add common points
        self.add_common_points()
        self.add_common_lines()

        # Retrieve point 5 from the just-created piece
        point_5 = self.builder.current_piece.get_point("5")

        # Mark point A at the side seam
        self.builder.add_point("A", point_5.x, point_5.y)

        # Pocket bag calculations
        pocket_length = 22  # 22cm pocket length
        pocket_width = 12  # 12cm pocket width
        pocket_extension = 4  # 4cm pocket extension

        # Calculate pocket bag points
        # B is 17cm from A along the side seam
        b_x = point_5.x
        b_y = point_5.y + 17
        self.builder.add_point("B", b_x, b_y)

        # Pocket bag points
        # Assuming pocket is slightly angled and not perfectly rectangular
        pocket_angle = math.radians(15)  # slight angle for more natural pocket shape

        # Pocket bag top points
        self.builder.add_point("PocketTopLeft",
                               b_x - pocket_width * math.cos(pocket_angle),
                               b_y + pocket_width * math.sin(pocket_angle))
        self.builder.add_point("PocketTopRight",
                               b_x + pocket_width * math.cos(pocket_angle),
                               b_y + pocket_width * math.sin(pocket_angle))

        # Pocket bag bottom points
        self.builder.add_point("PocketBottomLeft",
                               b_x - pocket_width * math.cos(pocket_angle) - pocket_length * math.sin(pocket_angle),
                               b_y + pocket_width * math.sin(pocket_angle) - pocket_length * math.cos(pocket_angle))
        self.builder.add_point("PocketBottomRight",
                               b_x + pocket_width * math.cos(pocket_angle) - pocket_length * math.sin(pocket_angle),
                               b_y + pocket_width * math.sin(pocket_angle) - pocket_length * math.cos(pocket_angle))

        # Add pocket bag path
        self.builder.add_line_path(["PocketTopLeft", "PocketTopRight",
                                    "PocketBottomRight", "PocketBottomLeft", "PocketTopLeft"])

        # Add 5cm to top edge for elasticated casing
        # This typically means extending the waist point
        point_1 = self.builder.current_piece.get_point("1")
        self.builder.add_point("1_Casing", point_1.x, point_1.y + 5)

        # Add 4cm hem allowance
        # This means extending the bottom points
        point_11 = self.builder.current_piece.get_point("11")
        point_13 = self.builder.current_piece.get_point("13")
        self.builder.add_point("11_Hem", point_11.x, point_11.y + 4)
        self.builder.add_point("13_Hem", point_13.x, point_13.y + 4)

        # Existing construction code
        self.builder.add_line_path(["0", "1"])
        self.builder.add_point("7", self.seat_width, self.calc.body_rise - (self.calc.body_rise / 4))
        self.builder.add_line_path(["6", "7"])
        self.builder.add_line_path(["0", "6"])
        self.builder.add_bezier_curve_with_reference("7", "8", "4", 3.25)
        self.builder.add_line_path(["13", "11", "12"])
        self.builder.add_line_path(["1", "12"])

        point14 = Util.line_intersection(
            self.builder.current_piece.get_point("1"),
            self.builder.current_piece.get_point("12"),
            self.builder.current_piece.get_point("3"),
            self.builder.current_piece.get_point("10")
        )

        if not point14:
            raise Exception("Lines 1-12 and 3-10 don't intersect")

        self.builder.add_point("14", point14.x, point14.y)

        # Calculate point 15 using reflection
        point10 = self.builder.current_piece.get_point("10")
        point15 = Util.reflect_vertical(point14, point10.x)
        self.builder.add_point("15", point15.x, point15.y)

        self.builder.add_line_path(["13", "15"])
        self.builder.add_bezier_curve("15", "8", -1, 0.5)

        # Update final piece construction
        self.builder.add_line_path(["1_Casing", "0", "6", "A", "B", "11_Hem", "13_Hem"])

        # End the piece
        self.builder.end_piece()


class ModifiedBackPantBlock(BackPantBlock):
    """
    Modified back pant block with modifications for elasticated waist and hem
    """
    def draft(self):
        """
        Draft the modified back pant block with modifications
        """
        # Ensure the piece is started
        if not self.builder.current_piece:
            self.builder.start_piece("Back")

        # Perform the base back block drafting
        # First, add common points
        self.add_common_points()
        self.add_common_lines()

        # Starting from front point 6
        # 6-16: 5cm
        point_6 = self.builder.current_piece.get_point("6")
        self.builder.add_point("16", point_6.x - 5, point_6.y)

        # 16-17: 4cm
        point_16 = self.builder.current_piece.get_point("16")
        self.builder.add_point("17", point_16.x, point_16.y - 4)

        # 0-18: 4cm (5cm with ease)
        self.builder.add_point("18", -(5 if self.ease_fitting else 4), 0)

        point_4 = self.builder.current_piece.get_point("4")
        point_8 = self.builder.current_piece.get_point("8")
        crotch_ease = 1 if self.ease_fitting else 0.5
        point_19 = Point(point_4.x, point_4.y/2)
        point_20 = Point(point_8.x + (abs(point_8.x) - abs(point_4.x)) + crotch_ease, point_4.y)

        self.builder.add_point("19", point_19.x, point_19.y)
        self.builder.add_point("20", point_20.x, point_20.y)
        self.builder.add_point("21", point_20.x, point_20.y + 1)

        crotch_curve_distance = 6 if self.ease_fitting else 5.5
        self.builder.add_bezier_curve_with_reference("19", "21", "4", crotch_curve_distance)

        point_12 = self.builder.current_piece.get_point("12")
        point_13 = self.builder.current_piece.get_point("13")
        self.builder.add_point("22", point_12.x - 1, point_12.y)
        self.builder.add_point("24", point_13.x + 1, point_13.y)

        point_23 = Util.line_intersection(
            self.builder.current_piece.get_point("18"),
            self.builder.current_piece.get_point("22"),
            self.builder.current_piece.get_point("3"),
            self.builder.current_piece.get_point("10")
        )

        if not point_23:
            raise Exception("Lines 18-22 and 3-10 don't intersect")

        point_10 = self.builder.current_piece.get_point("10")
        self.builder.add_point("23", point_23.x, point_23.y)

        point_25 = Util.reflect_vertical(point_23, point_10.x)
        self.builder.add_point("25", point_25.x, point_25.y)

        # Add 5cm to top edge for elasticated casing
        point_1 = self.builder.current_piece.get_point("1")
        self.builder.add_point("1_Casing", point_1.x, point_1.y + 5)

        # Add 4cm hem allowance
        point_11 = self.builder.current_piece.get_point("11")
        point_13 = self.builder.current_piece.get_point("13")
        self.builder.add_point("11_Hem", point_11.x, point_11.y + 4)
        self.builder.add_point("24_Hem", point_13.x, point_13.y + 4)

        # Update final piece construction
        self.builder.add_line_path(["1_Casing", "18", "17", "19", "21", "25", "24_Hem", "11_Hem"])

        # Add the existing line paths and bezier curves
        self.builder.add_line_path(["25", "24", "22", "18", "17", "19"])
        self.builder.add_bezier_curve("21", "25", 2, 0.5)

        # End the piece
        self.builder.end_piece()

class AnkleRibTrouserBlock:
    """
    Base class for modifying trouser blocks with ankle ribs
    """

    def __init__(self, builder, measurements, rib_depth=3, ease_fitting=False):
        """
        Initialize trouser block with ankle rib modifications

        :param builder: Pattern builder
        :param measurements: Measurements dictionary
        :param rib_depth: Depth of the ankle rib (default 3cm)
        :param ease_fitting: Whether to use ease fitting
        """
        self.builder = builder
        self.measurements = measurements
        self.rib_depth = rib_depth
        self.ease_fitting = ease_fitting

    def modify_leg_length(self, original_block):
        """
        Modify the leg length by subtracting rib depth

        :param original_block: The original pant block to modify
        :return: Modified measurements
        """
        modified_measurements = self.measurements.copy()
        modified_measurements["inside_leg"] -= self.rib_depth
        return modified_measurements


class ModifiedAnkleFrontPantBlock(ModifiedFrontPantBlock, AnkleRibTrouserBlock):
    """
    Front pant block with ankle rib and other modifications
    """

    def __init__(self, builder, measurements, rib_depth=3, ease_fitting=False):
        ModifiedFrontPantBlock.__init__(self, builder,
                                        self.modify_leg_length(measurements),
                                        ease_fitting)
        AnkleRibTrouserBlock.__init__(self, builder, measurements, rib_depth, ease_fitting)


class ModifiedAnkleBackPantBlock(ModifiedBackPantBlock, AnkleRibTrouserBlock):
    """
    Back pant block with ankle rib and other modifications
    """

    def __init__(self, builder, measurements, rib_depth=3, ease_fitting=False):
        ModifiedBackPantBlock.__init__(self, builder,
                                       self.modify_leg_length(measurements),
                                       ease_fitting)
        AnkleRibTrouserBlock.__init__(self, builder, measurements, rib_depth, ease_fitting)


def draft_trouser_pattern(builder, measurements, rib_depth=3, ease_fitting=False):
    """
    Draft a complete trouser pattern with modifications

    :param builder: Pattern builder
    :param measurements: Measurements dictionary
    :param rib_depth: Depth of ankle rib
    :param ease_fitting: Whether to use ease fitting
    :return: Completed pattern
    """
    # Draft front block
    front_block = ModifiedAnkleFrontPantBlock(builder, measurements, rib_depth, ease_fitting)
    front_block.draft()

    # Draft back block
    back_block = ModifiedAnkleBackPantBlock(builder, measurements, rib_depth, ease_fitting)
    back_block.draft()

    # Pocket bag as a separate piece
    builder.start_piece("Pocket Bag")
    # Use the pocket bag points from the front block to create a separate piece
    front_piece = builder.pattern.pieces[0]  # Assuming front block is first piece
    pocket_points = [
        "PocketTopLeft", "PocketTopRight",
        "PocketBottomRight", "PocketBottomLeft"
    ]

    for point_name in pocket_points:
        point = front_piece.get_point(point_name)
        builder.add_point(point_name, point.x, point.y)

    builder.add_line_path(pocket_points + [pocket_points[0]])
    builder.end_piece()

    return builder.pattern