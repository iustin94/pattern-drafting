class Measurement:
    """Represents a measurement that can be used in pattern calculations."""

    def __init__(self, name: str, default_value: float = 0.0):
        self.name = name
        self.default_value = default_value

    def __repr__(self):
        return f"Measurement('{self.name}', default={self.default_value})"


