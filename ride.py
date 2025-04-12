import sys
from speed import SpeedVector, zero_speed
from line import GroundProfile

#  My code
# rider.ride.x
# rider.ride.y
# rider.ride.speed.x
# rider.ride.speed.y
# rider.ride.speed.magn
# rider.ride.acc.x
# rider.ride.acc.y

class RideDrag:
    def __init__(self):
        # initialize riding drag values
        self.mass = 70.0 + 15.0         #(kg) rider + bike
        self.mu_roll_drag = 4E-3        # rolling resistance, typical value, no unit
        self.rider_A_surface = 0.5      # exposed front surface, in m2 
        self.rider_Cd_airDrag = 0.9     # aerodynamic drag coeficient, no unit
        self.rho_air_density = 1.22     # air density kg.m-3
        self.drag_const_k = self.rider_Cd_airDrag * self.rider_A_surface * self.rho_air_density / self.mass # drag constant, no unit

def trajectory (linePts, drag, start_x =0, start_speed = zero_speed):
    # initialize trajectory values
    speed = [start_speed]
    takeoffs = []
    state = "start"

    # compute trajectory
    for i in range(1, linePts.line_nb_pts):
        sgmt = LineSegment(linePts.line_x[i-1], linePts.line_y[i-1], linePts.line_x[i], linePts.line_y[i])
        dx = linePts.line_x[i] - linePts.line_x[i-1]
    
    
    # def speed (self):
    
    # def plot_position (self):
    
    # def plot_speed (self):


if __name__ == "__main__":
    drag = RideDrag()
    linePts = GroundProfile()
    
    sys.exit(False)


