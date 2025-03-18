import sys
from math import pi, cos, sin  
import matplotlib.pyplot as plt

segments = [(1.0,0.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (3.0,-6.0), (2.0,-3.0), (1.0,0.0)]
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

class line():
    def __init__(self, user_segments):
        self.user_points = [(0.0, 0.0)]
        self.line_points = [(0.0, 0.0)]
        self.x = 0.0
        self.y = 0,0 
        current_x = 0.0
        current_y = 0.0

        for len, angle in user_segments :
            radians = degrees_to_radians(angle)
            delta_x = len * cos(radians)
            delta_y = len * sin(radians)
            current_x += delta_x
            current_y += delta_y
            self.user_points.append((current_x, current_y))

    def plot(self):
        x_coords, y_coords = zip(*self.user_points)
        plt.plot(x_coords, y_coords, marker='o')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Points générés à partir des segments')
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    all_points = line (segments)
    # print(all_points.user_points)
    for point in all_points.user_points:
        print(point)
    all_points.plot()
    sys.exit(False)
