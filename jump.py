import matplotlib.pyplot as plt
import numpy as np
import sys
from phy import SpeedVector

class Jump:
    def __init__(self, takeoff_x, takeoff_y, takeoff_angle, landing_x, landing_y):
        self.takeoff_x = takeoff_x
        self.takeoff_y = takeoff_y
        self.landing_x = landing_x
        self.landing_y = landing_y
        self.takeoff_angle = takeoff_angle
        self.takeoff_speed = self.compute_takeoff_speed()
        self.landing_speed = self.compute_landing_speed()
        self.compute_jump_trajectory()
        
   
    def set_jump_parameters(self, takeoff_x, takeoff_y, takeoff_angle, landing_x, landing_y):
        """
        Set the jump parameters for the jump trajectory.
        
        Parameters:
        - takeoff_x: x-coordinate of the takeoff point
        - takeoff_y: y-coordinate of the takeoff point
        - takeoff_angle: angle of takeoff in degrees
        - landing_x: x-coordinate of the landing point
        - landing_y: y-coordinate of the landing point
        """
        self.takeoff_x = takeoff_x
        self.takeoff_y = takeoff_y
        self.landing_x = landing_x
        self.landing_y = landing_y
        self.takeoff_angle = takeoff_angle
        self.takeoff_speed = self.compute_takeoff_speed()
        self.compute_jump_trajectory()
        self.landing_speed = self.compute_landing_speed()

        return self.takeoff_speed
      
    def compute_landing_speed(self):
        return SpeedVector(5,-15,"m/s")

    def compute_jump_trajectory(self, res=0.1):
    #      """
    #     compute the jump trajectory based on the, takeoff and landing points.
    #     """
    #     # Initialize the trajectory points
    #     # Convert angle to radians
        angle_radians = np.radians(self.takeoff_angle)
        dx = self.landing_x - self.takeoff_x

        if dx > 0:
            # Compute the trajectory points
            self.x = np.linspace(self.takeoff_x, self.landing_x, int(dx/res))
            self.y = np.zeros_like(self.x)  # Initialize y array with zeros
            for i in range(len(self.x)): 
                # Compute the vertical position using the jump equation
                self.y[i] = -0.5 * 9.81 * (self.x[i] - self.takeoff_x) ** 2 / (self.takeoff_speed.value * np.cos(angle_radians)) ** 2 + \
                        self.takeoff_y + (self.x[i] - self.takeoff_x) * np.tan(angle_radians)
        
        return self.x, self.y
    
    def plot_jump_trajectory(self, res=0.1, axis=None):
        """
        Plot the jump trajectory based on the, takeoff and landing points.
        """
        if len(self.x) > 0 :
            ax = axis if axis is not None else plt

            if ax:

                # Plot the trajectory  
                ax.scatter([self.takeoff_x], [self.takeoff_y], color='green', label='Takeoff Point')
                # ax.plot(self.x, self.y, label='Jump Trajectory', color = 'black', marker = None, markersize = "8", linestyle = "-", linewidth=1, alpha=0.3, antialiased = True) # Plot the trajectory       
                ax.plot(self.x, self.y, label='Jump Trajectory', color = 'black', marker = "+", markersize = "8", linestyle = "-", linewidth=1, alpha=0.3, antialiased = True) # Plot the trajectory       
                ax.scatter([self.landing_x], [self.landing_y], color='red', label='Landing Point')
                ax.set_title(f"takeoff speed: {self.takeoff_speed:.2f} m/s")    
                ax.set_xlabel("X-axis")
                ax.set_ylabel("Y-axis")
                ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
                ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
                ax.grid(True)
                ax.set_aspect('equal', adjustable='box') 
                ax.legend()

            if axis is None:
                plt.show()
        
    def get_takeoff_speed(self):
        return self.takeoff_speed

    def compute_takeoff_speed (self):
        """
        Compute the takeoff speed backward from the landing point.
        
        Parameters:
        - landing_x: x-coordinate of the landing point - in meters
        - landing_y: y-coordinate of the landing point - in meters
        - takeoff_x: x-coordinate of the takeoff point - in meters
        - takeoff_y: y-coordinate of the takeoff point - in meters  
        - takeoff_angle: angle of takeoff in degrees
        
        Returns:
        - takeoff_speed: speed at takeoff in m/s
        """
        # Convert angle to radians
        angle_radians = np.radians(self.takeoff_angle)
        
        # Compute horizontal and vertical distances
        dx = self.landing_x - self.takeoff_x
        dy = self.landing_y - self.takeoff_y
        
        # Acceleration due to gravity
        g = 9.81  # m/s²
        
        divider = 2 * dx * np.tan(angle_radians) - 2 * dy

        if divider == 0:
            takeoff_speed = 0
        else:
            # Compute horizontal velocity component (v_x)
            v_x = dx *np.sqrt(g / divider)

            # Compute vertical velocity component (v_y)
            v_y = v_x * np.tan(angle_radians)
            
            # Compute total takeoff speed
            takeoff_speed = np.sqrt(v_x**2 + v_y**2)   

        return SpeedVector(takeoff_speed,self.takeoff_angle)

class JumpSimulation :
    def __init__(self, line):
        self.line = line
        self.jumps = []
        self.take_offs = []

if __name__ == "__main__":
    # Example parameters
    landing_x = 2.5  # x-coordinate of the landing point
    landing_y = 0   # y-coordinate of the landing point
    takeoff_x = 0   # x-coordinate of the takeoff point
    takeoff_y = 1   # y-coordinate of the takeoff point
    takeoff_angle =  -5  # angle of takeoff in degrees

    fig, ax = plt.subplots()

    jump = Jump(takeoff_x, takeoff_y, takeoff_angle, landing_x, landing_y)
    jump.plot_jump_trajectory(axis = ax)  # Plot the jump trajectory with a resolution of 0.2 m

    plt.show()
     
    sys.exit(0)

    