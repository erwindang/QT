import sys
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from line import Segment, GroundProfile
from math import radians, sqrt, cos, sin, tan, atan2, degrees, pow

class RideDrag:
    def __init__(self):
        # initialize riding drag values
        self.rider_mass = 70.0 + 15.0         #(kg) rider + bike
        self.Mu_roll_drag = 4E-3        # rolling resistance, typical value, no unit
        self.A_surface = 0.5      # rider exposed front surface, in m2 
        self.Cd_air_drag = 0.9     # aerodynamic drag coeficient, no unit
        self.Rho_air_density = 1.22     # air density kg.m-3
        self.K_drag_const = self.Cd_air_drag * self.A_surface * self.Rho_air_density / self.rider_mass # air drag constant, no unit

class RideState(Enum):
    ROLLING = "rolling"
    JUMPING = "jumping"
    LANDING = "landing"
    STOPPED = "stopped"
    
    def __str__(self):
        return self.value.capitalize()  
    
class Vector:
    def __init__(self, magnitude, angle, unit):
        self.angle = angle
        self.radian = radians(angle)
        self.value = magnitude
        self.x_value = magnitude * cos(self.radian)
        self.y_value = magnitude * sin(self.radian)
        self.unit = unit

    def __str__(self):
        return f"Vector: {self.value:.2f} {self.unit}, Angle: {self.angle:.2f}°"

class SpeedVector(Vector):
    def __init__(self, speed, angle, unit="m/s"):
        super().__init__(speed, angle, unit)

class AccelerationVector(Vector):
    def __init__(self, acceleration, angle, unit="m/s²"):
        super().__init__(acceleration, angle, unit)

def set_acceleration_unit(speed_unit):
    dict = {
        "m/s": "m/s²",
        "km/h": "km/h²"
    }
    return dict.get(speed_unit)

class TakeOff:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.position = (x, y)
        self.speed = speed
    
    def __str__(self):
        return f"TakeOff: x={self.x:.2f}, y={self.y:.2f}, speed={self.speed:.2f}"   


class RidePhysics:
 
    @staticmethod
    def compute_rolling (current_speed, current_time, segment, drag):
        """
        Compute the speed while rolling on the ground.

        Args:
            slope (float): Slope of the ground segment.
            drag (RideDrag): Drag parameters.
            current_speed (float): Current speed of the rider.

        Returns:
            float: Updated speed (SpeedVector). 
            float: Position (x,y) tuple .
            float: Time taken to travel the segment.
        """
        g = 9.80665   # gravity m.s-2
        val =  (2*g*(sin(-segment.radian) - drag.Mu_roll_drag*cos(segment.radian)) 
                    - drag.K_drag_const*pow(current_speed.value,2))*segment.length + pow(current_speed.value,2)
        #speed =  (2*g*sin(-segment.radian))*segment.length + pow(current_speed.value,2)
        if val < 0:
            print (f"negative compute_rolling {val} for segment {segment}. Set speed to 0")
            speed = 0.0
            delay = float('inf')
        else:
            try:
                speed =  sqrt(val)
                delay = segment.length / speed
            except ValueError:
                print (f"compute_rolling speed error {val} for segment {segment}. Set speed to 0")
                speed = 0.0
                delay = float('inf')
        
        new_speed = SpeedVector(speed, segment.degree, current_speed.unit)
        new_position = (segment.end_x, segment.end_y)
        new_time = current_time + delay

        # Compute acceleration
        acceleration_x = (new_speed.x_value - current_speed.x_value) / delay
        acceleration_y = (new_speed.y_value - current_speed.y_value) / delay
        acceleration_unit = set_acceleration_unit(current_speed.unit)
        acceleration_value = sqrt(pow(acceleration_x,2) + pow(acceleration_y,2))
        acceleration_angle = degrees(atan2(acceleration_y, acceleration_x))
        acceleration = AccelerationVector(acceleration_value, acceleration_angle, acceleration_unit) 

        return new_speed, new_position, new_time, acceleration
    
    @staticmethod
    def compute_jump (current_speed, current_time, segment, drag, take_off):
        """
        Compute the trajectory during a jump as a function of x-position.
        Args:
            initial_speed (float): Initial speed at take-off.
            angle (float): Take-off angle in degrees.
            x_start (float): Starting x-position of the jump.
            x_target (float): Target x-position to compute the y-coordinate.

        Returns:
            float: y-coordinate of the rider at the given x_target.
        """
        g = 9.80665   # gravity m.s-2
        dx = segment.end_x - take_off.x # distance from take-off to target x-position
        # Compute new position
        try :
            delta_y = -0.5*g / (take_off.speed.x_value**2) * (dx**2) + tan(take_off.speed.radian) * dx
        except ZeroDivisionError:
            delta_y = 0
        new_position = (segment.end_x, take_off.y + delta_y)
        
        # Compute new speed
        #FIXME: no drag in jump speed
        new_speed_x = take_off.speed.x_value
        new_speed_y = - g * dx / take_off.speed.x_value + take_off.speed.y_value
        new_speed_value = pow(new_speed_x,2) + pow(new_speed_y,2)

        try:
            new_speed = sqrt(new_speed_value)
            delay = dx / take_off.speed.x_value
        except ValueError:
            print (f"compute_jump speed error {new_speed_value} for segment {segment}. Set speed to 0")
            new_speed = 0.0
            delay = float('inf')

        new_angle = atan2(new_speed_y, new_speed_x)
        new_speed_vector = SpeedVector(new_speed, degrees(new_angle), take_off.speed.unit)
        new_time = current_time + delay

        acceleration_x = (new_speed_x - current_speed.x_value) / delay
        acceleration_y = (new_speed_y - current_speed.y_value) / delay
        acceleration_unit = set_acceleration_unit(current_speed.unit)
        acceleration_value = sqrt(pow(acceleration_x,2) + pow(acceleration_y,2))
        acceleration_angle = atan2(acceleration_y, acceleration_x)
        acceleration = AccelerationVector(acceleration_value, acceleration_angle, acceleration_unit) 
             
        return new_speed_vector, new_position, new_time, acceleration

    @staticmethod
    def compute_landing (current_speed, current_time, segment, drag):
        """
        Compute the speed while landing on the ground.

        Args:
            slope (float): Slope of the ground segment.
            drag (RideDrag): Drag parameters.
            current_speed (float): Current speed of the rider.

        Returns:
            float: Updated speed (SpeedVector). 
            float: Position (x,y) tuple .
        """
        # speed_x = current_speed.x_value - drag.K_drag_const * current_speed.x_value**2
        # speed_y = speed_x * tan(segment.radian)
        # val = pow(speed_x,2) + pow(speed_y,2)
        # try:
        #     speed = sqrt(val)
        #     time = segment.length / speed
        # except ValueError:
        #     print (f"compute_landing speed error {val} for segment {segment}. Set speed to 0")
        #     speed = 0.0
        #     time = float('inf')

        # FIXME: no drag in landing speed
        speed = current_speed.value * cos(current_speed.radian - segment.radian)
        try:
            delay = segment.dx / current_speed.x_value  #FIXME Assuming horizontal speed is constant
        except ZeroDivisionError:
            print (f"compute_landing speed error {current_speed.x_value} for segment {segment}. Set speed to 0")
            speed = 0.0
            delay = float('inf')

        speed_vector= SpeedVector(speed, segment.degree, current_speed.unit)
        position = (segment.end_x, segment.end_y)
        new_time = current_time + delay

        acceleration_x = (speed_vector.x_value - current_speed.x_value) / delay
        acceleration_y = (speed_vector.y_value - current_speed.y_value) / delay
        acceleration_unit = set_acceleration_unit(current_speed.unit)
        acceleration_value = sqrt(pow(acceleration_x,2) + pow(acceleration_y,2))
        acceleration_angle = atan2(acceleration_y, acceleration_x)
        acceleration = AccelerationVector(acceleration_value, acceleration_angle, acceleration_unit) 

        return speed_vector, position, delay, acceleration
    
    @staticmethod
    def is_take_off(speed, segment):
        """
        Detect if the rider is jumping based on speed and angle.

        Args:
            speed (float): Current speed of the rider.
            segment (Segment): Current segment of the ground.

        Returns:
            bool: True if jumping, False otherwise.
        """
        return (speed.angle > (segment.angle + 10)) and (speed.value > 3.0)  # sp
    
class RideTrajectory:
    def __init__(self, line, initial_speed, drag):
        self.line = line
        self.drag = drag
        self.state = RideState.ROLLING
        self.states = [RideState.ROLLING]  # Store states
        self.speed = [initial_speed]  # Initial speed (SpeedVector)
        self.positions = [(line.x[0], line.y[0])]  # Initial position
        self.takeoffs = []  # Store take-off points
        self.landings = []  # Store landing points
        self.time=[0.0]  # Store time points
        self.acceleration = [AccelerationVector(0.0, 0.0, initial_speed.unit)]  # Store acceleration vectors


    def compute_trajectory(self):
        """
        Compute the trajectory of the rider along the ground line.
        """
        for i in range(1, len(self.line.x)):
            # Get the current segment
            current_segment = Segment(
                self.line.x[i-1], self.line.y[i-1],
                self.line.x[i], self.line.y[i]
            )
       
            current_speed = self.speed[-1]
            current_time = self.time[-1]
            
            if current_speed.value > 0:
                match self.state:
                    
                    case RideState.ROLLING:
                        if RidePhysics.is_take_off(current_speed, current_segment): 
                            # JUMPING - Log take-off position
                            self.state = RideState.JUMPING  
                            new_take_off = TakeOff(self.line.x[i-1], self.line.y[i-1], current_speed)
                            self.takeoffs.append(new_take_off)
                            # Compute jump trajectory
                            new_speed, new_position, delay, acceleration = RidePhysics.compute_jump(current_speed, current_time, current_segment, self.drag, self.takeoffs[-1])
                        else: #ROLLING
                            new_speed, new_position, delay, acceleration = RidePhysics.compute_rolling(current_speed, current_time, current_segment, self.drag)
                        
                    case RideState.JUMPING:                       
                        # new_speed, new_position = RidePhysics.compute_rolling(current_speed, current_segment, self.drag)
                        new_speed, new_position, delay, acceleration = RidePhysics.compute_jump(current_speed, current_time, current_segment, self.drag, self.takeoffs[-1])
                        if new_position[1] < self.line.y[i]:
                            # LANDING - Log landing position
                            self.state = RideState.ROLLING
                            self.landings.append((self.line.x[i], self.line.y[i]))
                            new_speed, new_position, delay, acceleration = RidePhysics.compute_landing(current_speed, current_time, current_segment, self.drag)
                    
                    case RideState.STOPPED:
                        new_speed = SpeedVector(0.0, 0.0, current_speed.unit)
                        new_position = (self.line.x[i], self.line.y[i])
                        acceleration = AccelerationVector(0.0, 0.0, current_speed.unit)
                        delay = float('inf')

                    case _:
                        new_speed = (current_speed)
                        new_position = (self.line.x[i-1], self.line.y[i-1])
                        acceleration = AccelerationVector(0.0, 0.0, current_speed.unit)
                        delay = 0.0
                        print(f"Error Unknown state: {self.state}. Using some default values.")
                        raise ValueError("Undefined riding state")
                        
                if new_speed.value == 0.0:
                    self.state = RideState.STOPPED
    
                self.speed.append(new_speed)
                self.positions.append(new_position)
                self.acceleration.append(acceleration)
                self.states.append(self.state)
                self.time.append(self.time[-1] + delay)
            
            else: 
                self.state = RideState.STOPPED
                self.speed.append(current_speed)
                self.positions.append((self.line.x[i], self.line.y[i]))
                self.acceleration.append(AccelerationVector(0.0, 0.0, current_speed.unit))
                self.states.append(self.state)
                self.time.append(float('inf'))  

class RideSimulation:
    def __init__(self, line, initial_speed, drag):
        self.trajectory = RideTrajectory(line, initial_speed, drag)

    def run(self):
        """
        Run the simulation.
        """
        self.trajectory.compute_trajectory()

    def plot(self):
        """
        Plot the trajectory, including take-offs and landings.
        """
        positions = np.array(self.trajectory.positions)
        speeds = np.array([abs(speed.value) for speed in self.trajectory.speed])
    
        # Create subplots
        fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

        # Plot ground profile
        axs[0].plot(self.trajectory.line.x, self.trajectory.line.y, label="Ground Profile", color="tan")
        # Plot position & take offs (trajectory)
        axs[0].plot(positions[:, 0], positions[:, 1], label="Trajectory", color="blue", marker='+', markersize=1, linestyle="None")
        if (len(self.trajectory.landings) > 0):
            axs[0].scatter(*zip(*self.trajectory.landings), color='red', label="Landings", marker='x')
        if (len(self.trajectory.takeoffs) > 0):
            takeoff_positions = [takeoff.position for takeoff in self.trajectory.takeoffs]
            axs[0].scatter(*zip(*takeoff_positions), color='green', label="Take-offs", marker='o')
        axs[0].set_ylabel("Y (m)")
        axs[0].set_title("Rider Trajectory")
        axs[0].legend()
        axs[0].grid(True)

        # Plot speed
        axs[1].plot(positions[:, 0], speeds, label="Speed", color="red", marker='+', markersize=1, linestyle="None")
        # axs[1].plot(positions[:, 0], speeds, label="Speed", color="red", marker='+', markersize=4, linestyle="-")
        #axs[1].set_xlabel("x (m)")
        axs[1].set_ylabel("Speed (m/s) ")
        axs[1].legend()
        axs[1].grid(True)

        # Plot acceleration
        axs[2].plot(positions[:, 0], [accel.y_value for accel in self.trajectory.acceleration], label="Acceleration", color="green", marker='+', markersize=1, linestyle="-")
        axs[2].set_xlabel("X (m)")
        axs[2].set_ylabel("Acceleration (m/s²)")
        axs[2].legend()
        axs[2].grid(True)

        plt.show()


if __name__ == "__main__":
    # my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (3.0,-6.0), (2.0,-3.0), (1.0,0.0)]
    my_segments = [(0.5,0.0), (0.3,4.0), (0.3,6.0), (0.3,8.0), (0.3,11.0), (0.3,22.0), (0.3,40.0), (0.3,54.0), (1.0,0.0), (2.0,-25.0)]
    # my_segments = [(1.0,0.0), (1.0,-89.0), (3.0,0.0)] # step down
    # my_segments = [(1.0,-20.0), (1.0,-8.0)]
    # my_segments = [(1.0,-4.0)]
    # my_segments = [(1.0,0.0)]  # 1 meters flat
    # my_segments = [(10.0,0.0)]  # flat
    # my_segments = [(1.0,0.0),(1.0,0.0)]  # 2 meters flat
    # my_segments = [(1.0,5.0)]  # ramp up
    # my_segments = [(20.0,0.0),(20.0,0.0),(20.0,0.0),(20.0,0.0),(20.0,0.0)]  # 100 meters flat

    drag = RideDrag()
    line = GroundProfile(my_segments, 0.1)  # Create a ground profile with segments and resolution
    start_speed = SpeedVector(5, 0.0, "m/s")  # Initial speed of the rider
    simulation = RideSimulation(line, start_speed, drag)
    simulation.run()
    simulation.plot()
    sys.exit(0)
