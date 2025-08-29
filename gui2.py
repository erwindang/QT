import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from main_window import Ui_MainWindow
from scipy.interpolate import CubicSpline
from ride import RideDrag, ReverseRideSimulation
from line import Line

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes1 = fig.add_subplot(311)
        self.axes2 = fig.add_subplot(312, sharex=self.axes1)
        self.axes3 = fig.add_subplot(313, sharex=self.axes1)
        fig.subplots_adjust(hspace=0.6)

        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self, line, drag):
        super(MainWindow, self).__init__()
        self.jump_plot = None
        self.run_in_plot = None
        self.run_in_speed_plot = None
        self.jump_speed_plot = None
        self.adjustSizejump_speed_plot = None
        self.ride = None
        self.marker1 = None
        self.v_line1 = None
        self.h_line1 = None
        self.marker2 = None
        self.v_line2 = None
        self.h_line2 = None
        self.main_takeoff_marker = None
        self.landing_marker = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Compute line
        self.drag = drag
        self.line_x=line.x
        self.line_y=line.y
        self.line = line
        self.takeoff_indices = line.find_takeoffs()

        # Create a Matplotlib canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Connect mouse events
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_click)        
    
        # Add the canvas to the placeholder widget
        layout = QVBoxLayout(self.ui.plotWidget)  # Use the object name from Qt Designer
        layout.addWidget(self.canvas)

    def plot_graph(self):

        # Clear the previous plot
        self.canvas.axes1.clear()
        self.canvas.axes2.clear()
        self.canvas.axes3.clear()

        # Plot line profile with smoothing
        cubic_spline = CubicSpline(self.line_x, self.line_y)
        smooth_x = np.linspace(min(self.line_x), max(self.line_x), 200)  # 500 points for a smooth curve
        smooth_y = cubic_spline(smooth_x)
        ground, = self.canvas.axes1.plot(smooth_x, smooth_y, color="tan", label='Line', linewidth=1.0, alpha=0)
        self.canvas.axes1.fill_between(smooth_x, self.canvas.axes1.get_ylim()[0], smooth_y, color="tan", alpha=0.5)
        self.canvas.axes1.set_ylabel("Line profile (m)")
        self.canvas.axes2.set_ylabel("Speed (m/s)")
        self.canvas.axes3.set_ylabel("Acceleration (m/s²)")

        # Initialize marker1 and marker lines
        self.marker1, = self.canvas.axes1.plot(self.line_x[-1], self.line_y[-1], color = "blue" ,marker='+',  markersize=20, label='Marker')
        self.v_line1 = self.canvas.axes1.axvline(x=self.line_x[-1], color='black', linestyle='-', linewidth=1, alpha=0.2)
        self.h_line1 = self.canvas.axes1.axhline(y=self.line_y[-1], color='black', linestyle='-', linewidth=1, alpha=0.2)

        # Displaying segment data and marker coordinates
        line_idx = self.line_x.index(self.line_x[-1])
        angle = self.line.angle[line_idx] if hasattr(self.line, 'angle') else 0
        segment_num = self.get_user_segment_number(line_idx)
        x_marker = self.line_x[-1]
        y_marker = self.line_y[-1]
        self.canvas.axes1.set_title(f'segment: {segment_num}  index: {line_idx}  angle: {angle:.2f}°  coord: {x_marker:.3f}, {y_marker:.3f}',
            fontsize=10, pad=15)
    
        self.set_speed_title(0, 'm/s', True)

        # Plot take-off points
        takeoff_x = [self.line_x[i] for i in self.takeoff_indices]
        takeoff_y = [self.line_y[i] for i in self.takeoff_indices]
        self.canvas.axes1.scatter(takeoff_x, takeoff_y, color='blueviolet', marker='^', zorder=8, s=60, alpha=1.0, label='Take-offs')

        self.canvas.draw()

    def get_user_segment_number(self, line_idx):
        """
        Returns the user segment number for a given line index.
        Assumes self.line.user_segments is a list of Segment objects.
        """
        for seg_num, seg in enumerate(self.line.user_segments):
            # Check if the line index falls within this segment's interpolated indices
            if hasattr(seg, 'line_indices') and line_idx in seg.line_indices:
                return seg_num
        # Fallback: estimate by position
        return None

    def set_speed_title(self, speed, unit="m/s", draw=True):
        if unit == "m/s" or unit == "m.s-1":
            unit = "m/s"
            self.canvas.axes2.set_title(f'speed: {speed:.2f} {unit:s} - {speed * 3.6:.2f} km/h', fontsize=10, pad=15)
        elif unit == "km/h" or unit == "km.h-1":
            unit = "km/h"
            self.canvas.axes2.set_title(f'speed: {speed:.2f} {unit:s} - {speed / 3.6:.2f} m/s', fontsize=10, pad=15)
        elif unit == "mph":
            unit = "mph"
            self.canvas.axes2.set_title(f'speed: {speed:.2f} {unit:s} - {speed * 1.60934:.2f} km/h - {speed * 0.44704:.2f} m/s', fontsize=10, pad=15)
        else:
            unit = unit
            self.canvas.axes2.set_title(f'speed: {speed:.2f} {unit:s}', fontsize=10, pad=15)
            
        if draw : self.canvas.draw_idle()
    
    def on_mouse_move(self, event):
       if event.inaxes:
            if event.xdata < max(self.line_x[:]) and event.xdata > min(self.line_x[:]):
                x_mouse = event.xdata

                # --- Update line marker ---
                y_plot = np.interp(x_mouse, self.line_x, self.line_y)
                self.marker1.set_data([x_mouse], [y_plot])
                self.v_line1.set_xdata([x_mouse])
                self.h_line1.set_ydata([y_plot])

                # --- Update speed marker ---
                if self.marker2 is not None:
                    if x_mouse >= min(self.jump_x) and x_mouse <= max(self.jump_x):
                        marker_y = np.interp(x_mouse, self.jump_x, self.jump_speed_values)
                        self.marker2.set_data([x_mouse], [marker_y])
                        self.v_line2.set_xdata([x_mouse])
                        self.h_line2.set_ydata([marker_y])
                    elif x_mouse >= min(self.run_in_x) and x_mouse <= max(self.run_in_x):
                        marker_y = np.interp(x_mouse, self.run_in_x, [s.value for s in self.ride.run_in_speeds])
                        self.marker2.set_data([x_mouse], [marker_y])
                        self.v_line2.set_xdata([x_mouse])
                        self.h_line2.set_ydata([marker_y])
                    
                    self.set_speed_title(marker_y, 'm/s', False)

                # Find nearest index
                idx = np.abs(np.array(self.line_x) - x_mouse).argmin()
                angle = self.line.angle[idx] if hasattr(self.line, 'angle') else 0
                segment_num = self.get_user_segment_number(idx)
                self.canvas.axes1.set_title(f'segment: {segment_num}  index: {idx}  angle: {angle:.2f}°  coord: {x_mouse:.3f}, {y_plot:.3f}',
                    fontsize=10, pad=15
                )
                self.canvas.draw_idle()

    def on_mouse_click(self, event):
        if event.inaxes:
            if event.xdata < max(self.line_x[:]) and event.xdata > min(self.line_x[:]):         
                x_mouse = event.xdata  # Mouse x-coordinate

                # --- Update line simulation ---
                if len(self.line.takeoff_indices) > 0 and x_mouse > self.line.x[self.line.takeoff_indices[0]] : 
                    self.ride = ReverseRideSimulation(self.line, x_mouse, self.drag)
                    self.ride.run()

                # Update coord marker
                y_plot = np.interp(x_mouse, self.line_x[:], self.line_y[:])
                self.marker1.set_data([x_mouse], [y_plot])

                # --- Clear previous jump plot and landing marker ---
                if self.jump_plot is not None:
                    self.jump_plot.remove()
                    self.jump_plot = None
                if self.landing_marker is not None:
                    self.landing_marker.remove()
                    self.landing_marker = None
                if hasattr(self, "main_takeoff_marker") and self.main_takeoff_marker is not None:
                    self.main_takeoff_marker.remove()
                    self.main_takeoff_marker = None

                # --- Plot jump trajectory if available ---
                if hasattr(self, 'ride') and hasattr(self.ride, 'main_jump') and self.ride.main_jump is not None:
                    self.jump_x = getattr(self.ride.main_jump, 'x', None)
                    self.jump_y = getattr(self.ride.main_jump, 'y', None)
                    jump_speed = getattr(self.ride.main_jump, 'speed', None)
                    if self.jump_x is not None and self.jump_y is not None:
                        self.jump_plot, = self.canvas.axes1.plot(
                            self.jump_x, self.jump_y, color='red', linestyle='--', linewidth=1, alpha=0.4, label='Jump Trajectory', zorder=12)
                    # --- Plot landing point ---
                    landing_x = getattr(self.ride.main_jump, 'landing_x', None)
                    landing_y = getattr(self.ride.main_jump, 'landing_y', None)
                    if landing_x is not None and landing_y is not None:
                        self.landing_marker = self.canvas.axes1.scatter(
                            [landing_x], [landing_y], color='red', marker='o', label='Landing Point', zorder=13, s=20
                        )
            
                    # --- Plot takeoff point ---
                    takeoff_x = getattr(self.ride.main_jump, 'takeoff_x', None)
                    takeoff_y = getattr(self.ride.main_jump, 'takeoff_y', None)
                    if takeoff_x is not None and takeoff_y is not None:
                        self.main_takeoff_marker = self.canvas.axes1.scatter(
                            [takeoff_x], [takeoff_y], color='red', marker='^', label='Takeoff Point', zorder=14, s=60
                        )

                    # --- Plot run-in ---
                    if self.run_in_plot is not None:
                        self.run_in_plot.remove()
                        self.run_in_plot = None
                    self.run_in_x = getattr(self.ride, 'run_in_x', None)
                    self.run_in_y = getattr(self.ride, 'run_in_y', None)
                    if self.run_in_x is not None and self.run_in_y is not None:
                        self.run_in_plot, = self.canvas.axes1.plot(self.run_in_x, self.run_in_y, color='blueviolet', linestyle='--', linewidth=1, alpha=0.8, label='Run-in Trajectory', zorder=12)

                    # --- Plot jump speed on axes2 ---
                    if self.jump_x is not None and jump_speed is not None:
                        # If speed is a list of objects, extract the value attribute
                        if hasattr(jump_speed[0], 'value'):
                            # speed_values_x = [s.x_value for s in jump_speed]
                            # speed_values_y = [s.y_value for s in jump_speed]
                            self.jump_speed_values = [s.value for s in jump_speed]
                        else:
                            self.jump_speed_values = [None] * len(self.jump_x)

                        if self.jump_speed_plot is not None:
                            self.jump_speed_plot.remove()
                            self.jump_speed_plot = None

                        self.jump_speed_plot, = self.canvas.axes2.plot(self.jump_x, self.jump_speed_values, color='red', linestyle='-', linewidth=1, alpha=0.7)
                        # self.canvas.axes2.plot(jump_x, speed_values_x, color='grey', linestyle='-', linewidth=0.7, alpha=0.3)
                        # self.canvas.axes2.plot(jump_x, speed_values_y, color='grey', linestyle='-', linewidth=0.7, alpha=0.3)
                        # self.canvas.axes2.fill_between(jump_x, jump_speed_values, self.canvas.axes2.get_ylim()[0], color='cornflowerblue', alpha=0.2)
                    
                    # --- PLot run-in speed
                    if self.run_in_speed_plot is not None:
                        self.run_in_speed_plot.remove()
                        self.run_in_speed_plot = None
                    self.run_in_x = getattr(self.ride, 'run_in_x', None)
                    if self.run_in_x is not None:
                        run_in_speeds_values = [s.value for s in self.ride.run_in_speeds]   
                        self.run_in_speed_plot, = self.canvas.axes2.plot(self.run_in_x, run_in_speeds_values, color='blueviolet', linestyle='-', linewidth=0.7, alpha=0.7, label='Run-in Speed', zorder=12)
                        # self.canvas.axes2.fill_between(self.run_in_x, run_in_speeds_values, self.canvas.axes2.get_ylim()[0], color='cornflowerblue', alpha=0.2)                        

                    # --- Update speed marker ---
                    if x_mouse >= min(self.jump_x) and x_mouse <= max(self.jump_x):
                        marker_x = x_mouse
                        marker_y = np.interp(x_mouse, self.jump_x, self.jump_speed_values)
                        if self.marker2 is None:
                            self.marker2, = self.canvas.axes2.plot(marker_x, marker_y, color='black', marker='+', markersize=20, label='Speed Marker', zorder=15)
                            self.v_line2 = self.canvas.axes2.axvline(marker_x, color='black', linestyle='-', linewidth=1, alpha=0.2)
                            self.h_line2 = self.canvas.axes2.axhline(marker_y, color='black', linestyle='-', linewidth=1, alpha=0.2)
                    else:
                        self.marker2.set_data([x_mouse], [marker_y])
                        self.v_line2.set_xdata([x_mouse])
                        self.h_line2.set_ydata([marker_y])
                    
                    self.set_speed_title(marker_y, 'm/s', False)

                self.canvas.draw()                
                # self.canvas.draw_idle()


if __name__ == "__main__":
    my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (0.5,-15.0), (0.5,-10.0), (0.5,-6.0), (2.0,-3.0), (1.0,0.0)]
    # my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (0.7,-70.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (3.0,-6.0), (2.0,-3.0), (1.0,0.0)]
    # my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0)]
    # my_segments = [(1.0,0.0), (0.5,4.0), (0.5,6.0), (0.5,8.0), (0.5,11.0), (0.5,22.0), (0.5,40.0), (0.5,54.0), (1.5,-3.0), (0.5,-7.0), (0.5,-11.0), (2.0,-17.0), (0.5,-8.0), (0.5,0.0)]
    # my_segments = [(1.0,0.0), (0.5,4.0), (0.5,6.0), (0.5,8.0), (0.5,11.0), (0.5,22.0), (0.5,40.0), (0.5,54.0), (1.5,-3.0), (0.5,-7.0), (0.5,-11.0), (2.0,-17.0), (0.5,-8.0), (0.5,0.0),(1.0,0.0), (0.5,4.0), (0.5,6.0), (0.5,8.0), (0.5,11.0), (0.5,22.0), (0.5,40.0), (0.5,54.0), (1.5,-3.0), (0.5,-7.0), (0.5,-11.0), (2.0,-17.0), (0.5,-8.0), (0.5,0.0)]

    my_resolution = 0.1 #meters
    drag = RideDrag()
    line = Line (my_segments, my_resolution) 
   
    app = QApplication(sys.argv)
    window = MainWindow(line, drag)
    window.plot_graph()
    window.show()
    sys.exit(app.exec_())