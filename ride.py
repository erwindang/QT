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
        self.K_drag_const = self.Cd_air_drag * self.A_surface * self.Rho_air_density / self.rider_mass # drag constant, no unit

class RideState(Enum):
    ROLLING = "rolling"
    JUMPING = "jumping"
    LANDING = "landing"

class SpeedVector:
    """
    Class representing a speed vector with angle in degrees and speed components.
    """
    def __init__(self, speed, angle, unit = "m/s"):
        self.angle = angle      # angle from horizontal in degrees
        self.degree = angle
        self.radian = radians(angle)      # angle from horizontal in radians
        self.speed = speed            # module scalar value
        self.theta = radians(angle)      # angle from horizontal in radians
        self.value = speed            # module scalar value
        self.x_value = speed*cos(radians(angle)) # projected vector on x-axis
        self.y_value= speed*sin(radians(angle)) # projected vextor on z-axis
        self.unit = unit                # speed unit ("m/s", "m.s-1", "km/h", ...)
    
    def set_acceleration_unit(speed_unit):
        dict = {
            "m/s": "m/s2",
            "km/h": "km/h2"
        }
        return dict.get(speed_unit)

class RidePhysics:
 
    @staticmethod
    def compute_rolling (current_speed, segment, drag):
        """
        Compute the speed while rolling on the ground.

        Args:
            slope (float): Slope of the ground segment.
            drag (RideDrag): Drag parameters.
            current_speed (float): Current speed of the rider.

        Returns:
            float: Updated speed (SpeedVector). 
            float: Position (x,y) tuple .
        """
        g = 9.80665   # gravity m.s-2
        # speed =  sqrt((2*g*(sin(-segment.radian) - drag.Mu_roll_drag*cos(segment.radian))
        #             - drag.K_drag_const*pow(current_speed.value,2))*segment.length 
        #             + pow(current_speed.value,2)) 
        speed =  sqrt((2*g*sin(-segment.radian))*segment.length + pow(current_speed.value,2))
        return SpeedVector(speed, segment.degree, current_speed.unit), (segment.end_x, segment.end_y)
    
    @staticmethod
    def compute_jump (current_speed, segment, drag, take_off):
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
        dx = segment.end_x - take_off[0] # distance from take-off to target x-position
        # Compute new position
        try :
            delta_y = -0.5*g/(current_speed.x_value**2)*(dx**2) + tan(current_speed.radian)*dx
        except ZeroDivisionError:
            delta_y = 0
        new_position = (segment.end_x, segment.start_y + delta_y)
        
        # Compute new speed
        # new_speed_x = current_speed.x_value - drag.K_drag_const * current_speed.x_value**2
        new_speed_x = current_speed.x_value
        # new_speed_y = - g * dx / current_speed.x_value + current_speed.y_value - drag.K_drag_const * current_speed.y_value**2
        new_speed_y = - g * dx / current_speed.x_value + current_speed.y_value 
        new_speed = sqrt(pow(new_speed_x,2) + pow(new_speed_y,2))
        new_angle = atan2(new_speed_y, new_speed_x)
        new_speed_vector = SpeedVector(new_speed, degrees(new_angle), current_speed.unit)
        
        return new_speed_vector, new_position
    
    # vx = v0.speed*cos(v0.theta)
    # vy = -g*dx/vx + v0.speed*sin(v0.theta) 
    # speed = sqrt(pow(vx,2)+pow(vy,2)) #- airFrictionLoss(k, v0.speed) #Approximate constant air friction along dx segment
    # unit = v0.unit
    # theta = atan (vy/vx)


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
        return (speed.angle > (segment.angle + 10)) and (speed.value > 5.0)  # sp
    
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
            

            if current_speed.value > 0:
                match self.state:
                    
                    case RideState.ROLLING:
                        if RidePhysics.is_take_off(current_speed, current_segment): 
                            # JUMPING - Log take-off position
                            self.state = RideState.JUMPING  
                            self.takeoffs.append((self.line.x[i-1], self.line.y[i-1]))
                            # Compute jump trajectory
                            new_speed, new_position = RidePhysics.compute_jump(current_speed, current_segment, self.drag, self.takeoffs[-1])
                        else: #ROLLING
                            new_speed, new_position = RidePhysics.compute_rolling(current_speed, current_segment, self.drag)

                    case RideState.JUMPING:                       
                        # new_speed, new_position = RidePhysics.compute_rolling(current_speed, current_segment, self.drag)
                        new_speed, new_position = RidePhysics.compute_jump(current_speed, current_segment, self.drag, self.takeoffs[-1])
                        if new_position[1] < self.line.y[i]:
                            # LANDING - Log landing position
                            self.state = RideState.ROLLING
                            self.landings.append((self.line.x[i], self.line.y[i]))
                            new_position = (self.line.x[i], self.line.y[i]) #FIXME => compute intersection with ground
                            new_speed_value = sqrt(pow(current_speed.x_value,2) + pow(tan(current_segment.angle) * current_speed.x_value,2)) #FIXME => compute intersection with groun
                            new_speed = SpeedVector(new_speed_value, current_segment.angle, current_speed.unit)
                        
                    case _:
                        new_speed = (current_speed)
                        new_position = (self.line.x[i-1], self.line.y[i-1])
                        raise ValueError("Undefined riding state")
                        
                self.speed.append(new_speed)
                self.positions.append(new_position)
                self.states.append(self.state)
            else: 
                self.speed.append(current_speed)
                self.positions.append((self.line.x[i], self.line.y[i]))
                self.states.append(self.state)


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
        fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

        # Plot position & take offs (trajectory)
        axs[0].plot(positions[:, 0], positions[:, 1], label="Trajectory", color="blue", marker='+', markersize=1, linestyle="None")
        # axs[0].plot(positions[:, 0], positions[:, 1], label="Trajectory", color="blue", marker='+', markersize=4, linestyle="-")
        if (len(self.trajectory.landings) > 0):
            axs[0].scatter(*zip(*self.trajectory.landings), color='red', label="Landings", marker='x')
        if (len(self.trajectory.takeoffs) > 0):
            axs[0].scatter(*zip(*self.trajectory.takeoffs), color='green', label="Take-offs", marker='o')
        axs[0].set_ylabel("Y (m)")
        axs[0].set_title("Rider Trajectory")
        axs[0].legend()
        axs[0].grid(True)

        # Plot speed
        axs[1].plot(positions[:, 0], speeds, label="Speed", color="red", marker='+', markersize=1, linestyle="None")
        # axs[1].plot(positions[:, 0], speeds, label="Speed", color="red", marker='+', markersize=4, linestyle="-")
        axs[1].set_xlabel("x (m)")
        axs[1].set_ylabel("Speed (m/s) ")
        axs[1].legend()
        axs[1].grid(True)

        # plt.scatter(*zip(*self.trajectory.landings), color='blue', label="Landings")
        # plt.xlabel("X")
        # plt.ylabel("Y")
        # plt.title("Rider Trajectory")
        # plt.legend()
        plt.show()

if __name__ == "__main__":
    # my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (3.0,-6.0), (2.0,-3.0), (1.0,0.0)]
    my_segments = [(1.0,0.0), (0.5,4.0), (0.5,6.0), (0.5,8.0), (0.5,11.0), (0.5,22.0), (0.5,40.0), (0.5,54.0), (1.5,0.0), (2.0,-17.0), (1.0,0.0)]
    # my_segments = [(1.0,-20.0), (1.0,-8.0)]
    # my_segments = [(1.0,-4.0)]
    # my_segments = [(1.0,0.0)]  # 1 meters flat
    # my_segments = [(10.0,0.0)]  # flat
    # my_segments = [(20.0,0.0),(20.0,0.0),(20.0,0.0),(20.0,0.0),(20.0,0.0)]  # 100 meters flat


    drag = RideDrag()
    line = GroundProfile(my_segments, 0.1)  # Create a ground profile with segments and resolution
    start_speed = SpeedVector(10, 0.0, "m/s")  # Initial speed of the rider
    simulation = RideSimulation(line, start_speed, drag)
    simulation.run()
    simulation.plot()
    sys.exit(0)


