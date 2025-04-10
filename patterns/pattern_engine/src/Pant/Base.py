
class BasePantCalculations:
    """Base calculations for pant block measurements"""

    def __init__(self, measurements, ease_fitting=False):
        self.measurements = measurements
        self.ease_fitting = ease_fitting

    def get_waist_ease(self):
        return 2 if self.ease_fitting else 1

    def get_hip_ease(self):
        return 4 if self.ease_fitting else 2

    def get_crotch_depth(self):
        return self.measurements["crotch_depth"] + (2 if self.ease_fitting else 1)

    def get_front_rise(self):
        return self.measurements["crotch_depth"] * 0.45

    def get_back_rise(self):
        return self.measurements["crotch_depth"] * 0.55
