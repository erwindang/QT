import matplotlib.pyplot as plt
import numpy as np
import sys

class Jump:
    def __init__(self, takeoff_x, takeoff_y, takeoff_angle, landing_x, landing_y):
        self.takeoff_x = takeoff_x
        self.takeoff_y = takeoff_y
        self.landing_x = landing_x
        self.landing_y = landing_y
        self.takeoff_angle = takeoff_angle
        self.takeoff_speed = compute_takeoff_speed(landing_x, landing_y, takeoff_x, takeoff_y, takeoff_angle)
   
    def plot_jump_trajectory(self, res=0.1):
        """
        Plot the jump trajectory based on the takeoff and landing points.
        """
        # Convert angle to radians
        angle_radians = np.radians(self.takeoff_angle)
        
        dx = self.landing_x - self.takeoff_x

        # Compute the trajectory points
        x = np.linspace(self.takeoff_x, self.landing_x, int(dx/res))
        y = np.zeros_like(x)  # Initialize y array with zeros
        for i in range(len(x)): 
            # Compute the vertical position using the jump equation
            y[i] = -0.5 * 9.81 * (x[i] - self.takeoff_x) ** 2 / (self.takeoff_speed * np.cos(angle_radians)) ** 2 + \
                    self.takeoff_y + (x[i] - self.takeoff_x) * np.tan(angle_radians)
        # Plot the trajectory  
        # plt.plot(x, y, label='Jump Trajectory')
        plt.plot(x, y, label='Jump Trajectory', color = 'black', marker = "+", markersize = "8", linestyle = "-", linewidth=1, alpha=0.3, antialiased = True) # Plot the trajectory       
        plt.scatter([self.takeoff_x], [self.takeoff_y], color='green', label='Takeoff Point')
        plt.scatter([self.landing_x], [self.landing_y], color='red', label='Landing Point')
        plt.title(f"takeoff speed: {self.takeoff_speed:.2f} m/s")    
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.axhline(0, color='black', linewidth=0.5, linestyle='--')
        plt.axvline(0, color='black', linewidth=0.5, linestyle='--')
        plt.grid(True)
        plt.gca().set_aspect('equal', adjustable='box') 
        plt.legend()
        plt.show()

def compute_takeoff_speed (landing_x, landing_y, takeoff_x, takeoff_y, takeoff_angle):
    """
    Compute the takeoff speed backward from the landing point.
    
    Parameters:
    - landing_x: x-coordinate of the landing point
    - landing_y: y-coordinate of the landing point
    - takeoff_x: x-coordinate of the takeoff point
    - takeoff_y: y-coordinate of the takeoff point
    - takeoff_angle: angle of takeoff in degrees
    
    Returns:
    - takeoff_speed: speed at takeoff
    """
    # Convert angle to radians
    angle_radians = np.radians(takeoff_angle)
    
    # Compute horizontal and vertical distances
    dx = landing_x - takeoff_x
    dy = landing_y - takeoff_y
    
    # Acceleration due to gravity
    g = 9.81  # m/s²
    
    # Compute horizontal velocity component (v_x)
    # v_x = dx / (np.sqrt(2 * dy /  (2 * dx * np.tan(anglge_radians)) / g))
    v_x = dx *np.sqrt(g / (2 * dx * np.tan(angle_radians) - 2 * dy))


    # Compute vertical velocity component (v_y)
    v_y = v_x * np.tan(angle_radians)
    
    # Compute total takeoff speed
    takeoff_speed = np.sqrt(v_x**2 + v_y**2)
    
    return takeoff_speed

if __name__ == "__main__":
    # Example parameters
    landing_x = 2.5  # x-coordinate of the landing point
    landing_y = 1   # y-coordinate of the landing point
    takeoff_x = 0   # x-coordinate of the takeoff point
    takeoff_y = 0   # y-coordinate of the takeoff point
    takeoff_angle = 60  # angle of takeoff in degrees

    jump = Jump(takeoff_x, takeoff_y, takeoff_angle, landing_x, landing_y)
    jump.plot_jump_trajectory()  # Plot the jump trajectory with a resolution of 0.2 m
     
    sys.exit(0)

    