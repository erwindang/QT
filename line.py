import sys
from math import pi, cos, sin, radians, degrees, atan2, sqrt  
import matplotlib.pyplot as plt
import numpy as np

class Segment:
    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.dx = end_x - start_x
        self.dy = end_y - start_y
        self.length = float(np.sqrt(self.dx**2 + self.dy**2))
        self.radian = float(np.arctan2(self.dy, self.dx))  # Angle in radians
        self.degree = float(np.degrees(self.radian))  # Angle in degrees
        self.angle = self.degree
        self.slope = self.dy / self.dx if self.dx != 0 else float('inf')  # Slope of the segment (rise/run)
        self.intercept = start_y - self.slope * start_x  # y-intercept of the line (y = mx + b)
        self.start_point = (start_x, start_y)   
        self.end_point = (end_x, end_y)
        self.mid_point = ((start_x + end_x) / 2, (start_y + end_y) / 2)  # Midpoint of the segment
        self.is_vertical = self.dx == 0  # Check if the segment is vertical (dx = 0)
        self.is_horizontal = self.dy == 0  # Check if the segment is horizontal (dy = 0)
        self.is_positive = self.dy > 0
        self.is_negative = self.dy < 0  

    def __str__(self):
        return f"Segment: start=({self.start_x:.2f}, {self.start_y:.2f}), end=({self.end_x:.2f}, {self.end_y:.2f}), length={self.length:.2f}, angle={self.angle:.2f}°"
    
class GroundProfile:
    """
    Class to create a continuous line from a list of segments.
    Each segment is defined by its length and angle in degrees. 
    The segments are connected end-to-end to form a continuous line.
    The line is generated with a specified resolution (res).
    """
    def __init__(self, segments, res=0.2):
        self.segments = []
        self.x = []
        self.y = []
        self.res = res
        self._process_segments(segments)

    def _process_segments(self, segments):
        """
        Process the segments to create a continuous line and interpolate at the specified resolution.
        """
        current_x, current_y = 0.0, 0.0
        for length, degrees in segments:
            radian = np.radians(degrees)
            end_x = current_x + length * np.cos(radian)
            end_y = current_y + length * np.sin(radian)
            segment = Segment(current_x, current_y, end_x, end_y)
            self.segments.append(segment)
            self._interpolate_segment(segment)
            current_x, current_y = end_x, end_y
        
        # Add the last point to the line
        # self.x.append(current_x)
        # self.y.append(current_y)    
    
        
    def _interpolate_segment(self, segment):
        """
        Interpolate the segment to create points at the specified resolution.       
        The points are added to the line_x and line_y lists.
        """
        res = self.res*cos(np.radians(segment.angle))

        intp_x = np.arange(segment.start_x, segment.end_x, res)
        if intp_x[-1] >= segment.end_x:
            intp_x = intp_x[:-1]  # Remove the last point if it exceeds end_x
        intp_y = np.interp(intp_x, [segment.start_x, segment.end_x], [segment.start_y, segment.end_y])
        self.x.extend(intp_x)
        self.y.extend(intp_y)
    
    def _line_distance(self):
        return np.sum(self.segments[i].length for i in range(len(self.segments)))
    
    def _add_noise(self, sigma=0.01):
        """
        Add random noise to the interpolated line.

        Args:
            sigma (float): Standard deviation of the noise.
        """
        noise_x = np.random.normal(0, sigma, len(self.x))  # Noise for x-coordinates
        noise_y = np.random.normal(0, sigma, len(self.y))  # Noise for y-coordinates

        self.x = np.array(self.x) + noise_x
        self.y = np.array(self.y) + noise_y

    def plot(self, add_noise=False, noise_sigma=0.01):
        """
        Plot the generated ground profile (in red) with individual segments (in blue).
        Optionally add noise to the line.

        Args:
            add_noise (bool): Whether to add noise to the line.
            noise_sigma (float): Standard deviation of the noise.
        """
        if add_noise:
            self._add_noise(sigma=noise_sigma)

        plt.figure(figsize=(10, 6))
        if len(self.x) > 50:
            plt.plot(self.x, self.y, 'r-', linewidth=1, alpha=0.5) 
            for segment in self.segments:
                plt.plot([segment.start_x, segment.end_x], [segment.start_y, segment.end_y], 'b+')
        else:
            for segment in self.segments:
                plt.plot([segment.start_x, segment.end_x], [segment.start_y, segment.end_y], 'bo')
            plt.plot(self.x, self.y, 'r+')

        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Points générés à partir des segments (avec ou sans bruit)')
        plt.grid(True)
        plt.show()

    def __str__(self):
        """
        String representation of the GroundProfile object.
        """
        return f"GroundProfile: {len(self.segments)} segments, Nb.pts: {len(self.x)} total length={self._line_distance():.2f} m"

if __name__ == "__main__":
    # my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (3.0,-6.0), (2.0,-3.0), (1.0,0.0)]
    my_segments = [(1.0,0.0), (0.5,4.0), (0.5,6.0), (0.5,8.0), (0.5,11.0), (0.5,22.0), (0.5,40.0), (0.5,54.0), (1.5,0.0), (2.0,-17.0), (1.0,0.0)]
    # my_segments = [(1.0,-20.0), (1.0,-8.0), (1.0,0.0)]
    # my_segments = [(1.0,-4.0)]
    # my_segments = [(1.0, 0.0)]
    my_resolution = 0.1 #meters
    
    my_line = GroundProfile (my_segments, my_resolution)
    print(my_line)

    for i, segment in enumerate(my_line.segments):
        print(f"Segment {i+1}: {segment}")

    my_line.plot(add_noise=False, noise_sigma=0.005)

    
    sys.exit(False)