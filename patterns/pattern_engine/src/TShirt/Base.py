from patterns.pattern_engine.src.Point import Point


class BaseTShirtCalculations:

    def __init__(self, measurements, ease_fitting):
        """
        Initialize the base T-shirt block.
        
        Args:
            builder: The pattern builder
            measurements: Dictionary of measurements
            ease_fitting: If True, use the measurements for easier fitting
        """
        self.measurements = measurements
        self.ease_fitting = ease_fitting

        # Extract needed measurements
        self.chest = measurements["chest"]
        self.half_back = measurements["half_back"]
        self.back_neck_to_waist = measurements["back_neck_to_waist"]
        self.scye_depth = measurements["scye_depth"]
        self.neck_size = measurements["neck_size"]
        self.finished_length = measurements["finished_length"]

        # Calculate ease values
        self.scye_depth_ease = 2.5 if ease_fitting else 1
        self.half_back_ease = 2 if ease_fitting else 1
        self.chest_ease = 4 if ease_fitting else 2.5

    def get_shoulder_height(self):
        return (self.scye_depth + self.scye_depth_ease) / 2 / 4

    def get_shoulder_width(self):
        return (self.half_back + self.half_back_ease + 0.75)

    def get_underarm_width(self):
        return self.chest / 4 + self.chest_ease

    def get_underarm_height(self):
        return self.scye_depth + self.scye_depth_ease

    def shoulder_point(self):
        return Point(self.get_shoulder_width(), self.get_shoulder_height())

    def underarm_point(self):
        return Point(self.get_underarm_width(), self.get_underarm_height())
