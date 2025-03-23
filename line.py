import sys
from math import pi, cos, sin  
import matplotlib.pyplot as plt
import numpy as np

segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (3.0,-6.0), (2.0,-3.0), (1.0,0.0)]
resolution_x = 0.02 #meters

#  My code
#
# line.user_pts.x
# line.user_pts.y
# line.profile.x
# line.profile.y

# Fonction pour convertir les degrés en radians
def degrees_to_radians(degrees):
    return degrees *pi / 180.0

class Line():
    def __init__(self):
        self.user_x = [0.0]
        self.user_y = [0.0]
        self.x = [0.0]
        self.y = [0.0]
        current_x = 0.0
        current_y = 0.0
        res = 0.05
 
        for len, angle in segments :
            radians = degrees_to_radians(angle)
            end_x = current_x + len * cos(radians)
            end_y = current_y + len * sin(radians)

            x = [current_x, end_x]
            y = [current_y, end_y]

            line_x = np.arange(current_x, end_x, res)
            line_y = np.interp(line_x, x, y)
            
            self.x = np.append(self.x, line_x)
            self.y = np.append(self.y, line_y)

            current_x = end_x
            current_y = end_y
            
            self.user_x.append(current_x)
            self.user_y.append(current_y)

    def plot(self):
        plt.plot(self.user_x, self.user_y, 'bo')
        plt.plot(self.x, self.y, 'r-')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Points générés à partir des segments')
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    all_points = Line ()
    all_points.plot()
    sys.exit(False)
