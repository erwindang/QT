import numpy as np

class gravity_const:
    def __init__(self):
        self.value = 9.80665
        self.unit = "m/s²"

g = gravity_const()

class Vector:
    def __init__(self, magnitude, angle):
        self.angle = angle
        self.radian = np.radians(angle)
        self.value = magnitude
        self.x_value = magnitude * np.cos(self.radian)
        self.y_value = magnitude * np.sin(self.radian)

    def __str__(self):
        return f"Vector: {self.value:.2f}, Angle: {self.angle:.2f}°"

class SpeedVector(Vector):
    def __init__(self, speed, angle, unit="m/s"):
        super().__init__(speed, angle)
        self.unit = unit

    def __str__(self):
            return f"SpeedVector: {self.value:.2f} {self.unit}, Angle: {self.angle:.2f}°"
    
    def projected_speed(self, angle):
        radians = np.radians(angle)
        projected_value = self.value * np.cos(self.radian - radians)
        return SpeedVector(projected_value, angle, self.unit)

def to_km_h(speed_m_s):
    return speed_m_s * 3.6

def to_m_s(speed_km_h):
    return speed_km_h / 3.6

class AccelerationVector(Vector):
    def __init__(self, acceleration, angle, unit="m/s²"):
        super().__init__(acceleration, angle, unit)

def set_acceleration_unit(speed_unit):
    dict = {
        "m/s": "m/s²",
        "km/h": "km/h²"
    }
    return dict.get(speed_unit)
