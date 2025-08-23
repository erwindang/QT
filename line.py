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
    
class Line:
    """
    Class to create a continuous line from a list of segments.
    Each segment is defined by its length and angle in degrees. 
    The segments are connected end-to-end to form a continuous line.
    The line is generated with a specified resolution (res).
    """
    def __init__(self, segments, res=0.2):
        self.user_segments = [] # user segments
        self.line_segments = [] # segments with interpolated points
        self.line_indices = []
        self.res = res  # resolution in meters
        # generated x-coordinates according to segments and resolution
        self.x = [] 
        self.y = []
        self.angle = [] 
        self.radian = []
        self._process_segments(segments) # generate line coordinates
        self.takeoff_indices = self.find_takeoffs() # find takeoff indices

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
            self.user_segments.append(segment)
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
        start_idx = len(self.x)    # index for user segment numbering    
        res = self.res*cos(np.radians(segment.angle)) # compute resolution depending on segment angle 
        intp_x = np.arange(segment.start_x, segment.end_x, res)
        if intp_x[-1] >= segment.end_x:
            intp_x = intp_x[:-1]  # Remove the last point if it exceeds end_x
        intp_y = np.interp(intp_x, [segment.start_x, segment.end_x], [segment.start_y, segment.end_y])
        self.x.extend(intp_x)
        self.y.extend(intp_y)
        self.angle.extend([segment.angle] * len(intp_x))    # Store angle for each point
        self.radian.extend([segment.radian] * len(intp_x)
                           )  # Store radian for each point
        end_idx = len(self.x) - 1
        # Assign indices to the segment
        segment.line_indices = list(range(start_idx, end_idx + 1))

        # Generate line segments
        for i in range(len(intp_x) - 1):
            self.line_segments.append(Segment(intp_x[i], intp_y[i], intp_x[i + 1], intp_y[i + 1]))
        
        # Add the last segment
        self.line_segments.append(Segment(intp_x[-1], intp_y[-1], segment.end_x, segment.end_y))

    def _line_distance(self):
        return np.sum(self.user_segments[i].length for i in range(len(self.user_segments)))
    
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
            for segment in self.user_segments:
                plt.plot([segment.start_x, segment.end_x], [segment.start_y, segment.end_y], 'b+')
        else:
            for segment in self.user_segments:
                plt.plot([segment.start_x, segment.end_x], [segment.start_y, segment.end_y], 'bo')
            plt.plot(self.x, self.y, 'r+')

        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Points générés à partir des segments (avec ou sans bruit)')
        plt.grid(True)
        plt.show()

    def find_takeoffs(self, angle_threshold_deg=15, radius_threshold=1.0, distance_threshold=2.0):
        """
        Detect jump take-offs using both angle change and radius of curvature,
        and filter so that no two take-offs are closer than distance_threshold.
        Only negative angle changes and concave (downward) curvature are considered.
        Returns a list of indices in self.x/self.y.
        """
        takeoff_indices = []

        # Angle threshold method: only negative angle difference
        for i in range(1, len(self.angle)):
            angle_diff = self.angle[i] - self.angle[i-1]
            if angle_diff < -angle_threshold_deg and angle_diff < 0:
                takeoff_indices.append(i)

        # Radius of curvature method: only concave (downward) curvature
        def radius_of_curvature_and_sign(x1, y1, x2, y2, x3, y3):
            a = np.hypot(x2 - x1, y2 - y1)
            b = np.hypot(x3 - x2, y3 - y2)
            c = np.hypot(x1 - x3, y1 - y3)
            s = (a + b + c) / 2
            area = np.sqrt(max(s * (s - a) * (s - b) * (s - c), 0))
            if area == 0:
                return np.inf, 0
            radius = (a * b * c) / (4 * area)
            # Compute sign of curvature using cross product (z-component)
            v1 = np.array([x2 - x1, y2 - y1])
            v2 = np.array([x3 - x2, y3 - y2])
            cross = v1[0]*v2[1] - v1[1]*v2[0]
            sign = np.sign(cross)
            return radius, sign

        for i in range(1, len(self.x) - 1):
            r, sign = radius_of_curvature_and_sign(
                self.x[i-1], self.y[i-1],
                self.x[i], self.y[i],
                self.x[i+1], self.y[i+1]
            )
            # sign < 0 means concave downward (jump possible)
            if r < radius_threshold and sign < 0:
                takeoff_indices.append(i)

        # Remove duplicates and sort
        takeoff_indices = sorted(set(takeoff_indices))

        # Apply distance threshold: keep only the first takeoff if two are too close
        filtered_indices = []
        last_x = None
        for idx in takeoff_indices:
            if last_x is None or abs(self.x[idx] - last_x) >= distance_threshold:
                filtered_indices.append(idx)
                last_x = self.x[idx]
            # else: skip this takeoff because it's too close to the previous one

        return filtered_indices

    def __str__(self):
        """
        String representation of the Line object.
        """
        return f"Line: {len(self.user_segments)} segments, Nb.pts: {len(self.x)} total length={self._line_distance():.2f} m"

if __name__ == "__main__":
    # my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (3.0,-6.0), (2.0,-3.0), (1.0,0.0)]
    my_segments = [(1.0,0.0), (0.5,4.0), (0.5,6.0), (0.5,8.0), (0.5,11.0), (0.5,22.0), (0.5,40.0), (0.5,54.0), (1.5,0.0), (2.0,-17.0), (1.0,-16.0), (0,5, -14.0), (0.5,-8.0), (0.5,-4.0), (0.5,0.0)]
    # my_segments = [(1.0,-20.0), (1.0,-8.0), (1.0,0.0)]
    # my_segments = [(1.0,-4.0)]
    # my_segments = [(1.0, 0.0)]
    my_resolution = 0.1 #meters
    
    my_line = Line (my_segments, my_resolution)
    print(my_line)

    for i, segment in enumerate(my_line.user_segments):
        print(f"User segment {i+1}: {segment}")

    for i, segment in enumerate(my_line.line_segments):
        print(f"Line segment {i+1}: {segment}")

    my_line.plot(add_noise=False, noise_sigma=0.005)

    
    sys.exit(False)