from math import radians, cos, sin

class Vector:
    def __init__(self, magnitude, angle):
        self.angle = angle
        self.radian = radians(angle)
        self.value = magnitude
        self.x_value = magnitude * cos(self.radian)
        self.y_value = magnitude * sin(self.radian)

    def __str__(self):
        return f"Vector: {self.value:.2f}, Angle: {self.angle:.2f}°"

class SpeedVector(Vector):
    def __init__(self, speed, angle, unit="m/s"):
        super().__init__(speed, angle)

    def __str__(self):
            return f"SpeedVector: {self.value:.2f} {self.unit}, Angle: {self.angle:.2f}°"

class AccelerationVector(Vector):
    def __init__(self, acceleration, angle, unit="m/s²"):
        super().__init__(acceleration, angle, unit)

def set_acceleration_unit(speed_unit):
    dict = {
        "m/s": "m/s²",
        "km/h": "km/h²"
    }
    return dict.get(speed_unit)
