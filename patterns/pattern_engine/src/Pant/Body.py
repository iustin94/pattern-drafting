from patterns.pattern_engine.src.PatternBuilder import PatternBuilder
from patterns.pattern_engine.src.Point import Point
from patterns.pattern_engine.src.Util import Util


class BasePantCalculations:
    """Calculations for trouser block using specified measurements"""

    def __init__(self, measurements, ease_fitting=False):
        self.body_rise = measurements["body_rise"]
        self.inside_leg = measurements["inside_leg"]
        self.seat = measurements["seat_measurement"]
        self.waist = measurements["waist_measurement"]
        self.ease = 4 if ease_fitting else 2  # Ease adjustment
        
    def get_crotch_point(self):
        eighth_point = self.body_rise + (self.body_rise / 4) + (0.5 if self.ease else -0.5)
        return Point(eighth_point, self.get_crotch_height())
    
    def get_leg_middle(self):
        return (self.seat / 4 / 2) + 1

    def get_knee_height(self):
        return self.body_rise + (self.inside_leg / 2)
    
    def get_leg_length(self):
        return self.body_rise + self.inside_leg
    
    def get_crotch_height(self):
        return self.body_rise + self.ease


class BasePantBlock:
    
    def __init__(self, builder: PatternBuilder, measurements, ease_fitting=False):
        self.builder = builder
        self.calc = BasePantCalculations(measurements, ease_fitting)
        self.ease_fitting = ease_fitting
        self.seat_width = self.calc.seat/4
        
    def add_common_points(self):
        # FRONT SECTION CONSTRUCTION
        # 0 - Starting point
        self.builder.add_point("0", 0, 0)

        # 0-1: Body rise + ease
        self.builder.add_point("1", 0, self.calc.get_crotch_height())

        # 1-2: Inside leg measurement
        self.builder.add_point("2", 0, self.calc.get_leg_length())

        # 1-3: 1/2 inside leg
        self.builder.add_point("3", 0, self.calc.get_knee_height())

        # 1-4: 1/4 seat + ease
        self.builder.add_point("4", self.seat_width, self.calc.get_crotch_height())
        self.builder.add_point("5", self.seat_width, 0)
        self.builder.add_point("6", self.seat_width - 1, 0)

        crotch_point = self.calc.get_crotch_point()
        self.builder.add_point("8", crotch_point.x, crotch_point.y)
        self.builder.add_point("9", self.calc.get_leg_middle(), self.calc.get_crotch_height())
        
        self.builder.add_point("10", self.calc.get_leg_middle(),  self.calc.get_knee_height())
        
        self.builder.add_point("11", self.calc.get_leg_middle(), self.calc.get_leg_length())
        self.builder.add_point("12", self.calc.get_leg_middle() - (self.seat_width / 3) - 1, self.calc.get_leg_length())
        self.builder.add_point("13", self.calc.get_leg_middle() + (self.seat_width / 3) + 1, self.calc.get_leg_length())

    def add_common_lines(self):
        pass


class FrontPantBlock(BasePantBlock):
    """Front trouser block following exact instruction numbering"""

    def __init__(self, builder, measurements, ease_fitting=False):
        super().__init__(builder, measurements, ease_fitting)


    def draft(self):
        self.builder.start_piece("Front")
        self.add_common_points()
        self.add_common_lines()

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

        self.builder.end_piece()


class BackPantBlock(BasePantBlock):
    """Back trouser block following exact instruction numbering"""

    def __init__(self, builder, measurements, ease_fitting=False):
        super().__init__(builder, measurements, ease_fitting)

    def draft(self):
        self.builder.start_piece("Back")
        self.add_common_points()
        self.add_common_lines()

        # BACK SECTION CONSTRUCTION
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

        self.builder.add_line_path(["25", "24", "22", "18", "17", "19"])
        self.builder.add_bezier_curve("21", "25", 2, 0.5)

        point_22 = self.builder.current_piece.get_point("22")
        point_24 = self.builder.current_piece.get_point("24")


        self.builder.end_piece()