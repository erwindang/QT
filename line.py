import sys
from math import pi, cos, sin  
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

#segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (3.0,-6.0), (2.0,-3.0), (1.0,0.0)]
segments = [(1.0,-20.0), (1.0,-8.0)]
#segments = [(1.0,-4.0)]
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

class Segment:
    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.dx = end_x - start_x
        self.dy = end_y - start_y
        self.length = np.sqrt(self.dx**2 + self.dy**2)
        self.angle = np.degrees(np.arctan2(self.dy, self.dx))  # Angle in degrees

    def __str__(self):
        return f"Segment: start=({self.start_x:.2f}, {self.start_y:.2f}), end=({self.end_x:.2f}, {self.end_y:.2f}), length={self.length:.2f}, angle={self.angle:.2f}°"
    
# Class to generate a line from segments
# Each segment is defined by its length and angle in degrees
class GroundProfile():
    def __init__(self, res = 0.2):
        # User segments
        #self.user_segments = segments
        self.user_x = []
        self.user_y = []
        self.user_dx = []
        self.user_dy = []
        self.user_dist = []
        self.user_degrees = []
        self.user_radians = []
        self.user_nb_pts = 0 # number of user points, last point is not included
        self.user_total_dist = 0.0
        self.user_total_dx = 0.0
        self.user_total_dy = 0.0
        self.user_total_dplus = 0.0
        self.user_total_dminus = 0.0 
        
        # Interpolated line segments
        self.line_x = []
        self.line_y = []
        self.line_dx = []
        self.line_dy = []
        self.line_dist = []
        self.line_radians = []
        self.line_degrees = []
        self.types = []
        self.line_nb_pts = 0 #number of points in the line, last point is not included
        self.line_total_dist = 0.0
        self.line_total_dx = 0.0
        self.line_total_dy = 0.0
        self.line_total_dplus = 0.0
        self.line_total_dminus = 0.0

        current_x = 0.0
        current_y = 0.0
        self.res_x = res
 
        for length, degrees in segments :
            radians = degrees_to_radians(degrees)

            # Calculate the end coordinates of the segment
            # using the current coordinates, the segment length and angle
            end_x = current_x + length * cos(radians)
            end_y = current_y + length * sin(radians)
            point_types = ["user"] # first point is a user point
     
            # Interpolate the points between the start and end of the segment
            # using the specified resolution
            intp_x = np.arange(current_x, end_x, res)
            intp_y = np.interp(intp_x, [current_x, end_x], [current_y, end_y])
            line_degrees = [degrees for _ in range(len(intp_x))]
            line_radians = [radians for _ in range(len(intp_x))]
            intp_types = ["intp" for _ in range(len(intp_x)-1)]
            point_types.extend(intp_types)
            nb_pts = len(intp_x)
            dx = intp_x[1:] - intp_x[:-1]  # difference between consecutive x points
            dx = np.append(dx, end_x - intp_x[:-1])  # add the last segment
            dy = intp_y[1:] - intp_y[:-1]  # difference between consecutive y points
            dy = np.append(dy, end_y - intp_y[:-1])
            dist = np.sqrt(dx**2 + dy**2)  # distance between consecutive points
            dist = np.append(dist, np.sqrt((end_x - intp_x[-1])**2 + (end_y - intp_y[-1])**2))  # add the last segment

            # Append the interpolated points to the lists
            self.line_x = np.append(self.line_x, intp_x)
            self.line_y = np.append(self.line_y, intp_y)
            self.line_dx = np.append(self.line_dx, dx)
            self.line_dy = np.append(self.line_dy, dy)
            self.line_dist = np.append(self.line_dist, dist)
            self.line_radians = np.append(self.line_radians, line_radians)
            self.line_degrees = np.append(self.line_degrees, line_degrees) 
            self.types.extend(point_types)
            self.line_total_dist += length
            self.line_total_dx += end_x - current_x
            self.line_total_dy += end_y - current_y
            self.line_total_dplus += max(0.0, end_y - current_y)
            self.line_total_dminus += min(0.0, end_y - current_y)
            self.line_nb_pts += nb_pts
            
            self.user_x.append(current_x)
            self.user_y.append(current_y)
            self.user_dx = np.append(self.user_dx, end_x - current_x)
            self.user_dy = np.append(self.user_dy, end_y - current_y)
            self.user_dist = np.append(self.user_dist, length)
            self.user_degrees.append(degrees)
            self.user_radians.append(radians)
            self.user_total_dist += length
            self.user_total_dx += end_x - current_x
            self.user_total_dy += end_y - current_y
            self.user_total_dplus += max(0.0, end_y - current_y)
            self.user_total_dminus += min(0.0, end_y - current_y)   
            self.user_nb_pts += 1
           
            current_x = end_x
            current_y = end_y
            
        # Add the last point
        self.user_x.append(end_x)
        self.user_y.append(end_y)
        self.user_dx = np.append(self.user_dx, 0.0)  # last point has no dx
        self.user_dy = np.append(self.user_dy, 0.0)  # last point has no dy
        self.user_dist = np.append(self.user_dist, 0.0)
        self.user_degrees.append(radians)
        self.user_radians.append(degrees)
        self.line_x = np.append(self.line_x, end_x)
        self.line_y = np.append(self.line_y, end_y)
        self.line_dx = np.append(self.line_dx, 0.0)
        self.line_dy = np.append(self.line_dy, 0.0)
        self.line_dist = np.append(self.line_dist, 0.0)
        self.types.append("user")
        self.line_degrees = np.append(self.line_degrees, degrees)  # assume last point angle is same as previous
        self.line_radians = np.append(self.line_radians, radians)  # assume last point angle is same as previous

        # Create B-spline
        #spl = make_interp_spline(self.line_x, self.line_y, k=3)  # B-spline of degree 3 (cubic)
        # Generate new x values for the B-spline
        #self.y_smooth = spl(self.line_x)


    def plot(self):
        plt.figure(figsize=(10, 6))

        plt.plot(self.user_x, self.user_y, 'bo')
        plt.plot(self.line_x, self.line_y, 'r+')
        #plt.plot(self.line_x, self.y_smooth, 'g-', label='B-spline')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Points générés à partir des segments')
        plt.grid(True)
        plt.show()

    def print_line(self):
        for x, y , angle in zip(self.line_x, self.line_y, self.line_degrees):
            print(f"Line: x = {x:.2f}, y = {y:.2f}, angle = {angle:.2f}°")
        print(f"Nb points: {len(self.line_x)}")

    def print_all_points(self):
        print(f"len(self.line_x): {len(self.line_x)} self.nb_pts: {self.line_nb_pts} self.user_nb_pts: {self.user_nb_pts}")
        for i in range(len(self.line_x)):
            print(f"{i:04d} {self.types[i]} x= {self.line_x[i]:.2f} y= {self.line_y[i]:.2f} deg= {self.line_degrees[i]}° dx= {self.line_dx[i]:.2f} dy= {self.line_dy[i]:.2f} dist= {self.line_dist[i]:.2f}")

if __name__ == "__main__":
    all_points = GroundProfile ()
    all_points.print_all_points()
    all_points.plot()
    sys.exit(False)
