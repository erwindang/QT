import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from main_window import Ui_MainWindow
from scipy.interpolate import CubicSpline
from ride import RideDrag
from line import GroundProfile
from jump import JumpSimulation, Jump

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes1 = fig.add_subplot(311)
        self.axes2 = fig.add_subplot(312, sharex=self.axes1)
        self.axes3 = fig.add_subplot(313, sharex=self.axes1)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self, line):
        super(MainWindow, self).__init__()
        self.jump_plot = None
        self.landing_marker = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Compute line
        self.line_x=line.x
        self.line_y=line.y
        self.line = line

        # Find take-off indices
        self.takeoff_indices = JumpSimulation.find_take_offs(line, angle_threshold_deg=20, radius_threshold=0.5)
        self.takeoff_x = [self.line_x[i] for i in self.takeoff_indices]
        self.takeoff_y = [self.line_y[i] for i in self.takeoff_indices]
        self.takeoff_angle = [line.angle[i-1] for i in self.takeoff_indices]
        self.takeoff_radian = [line.radian[i-1] for i in self.takeoff_indices]
    
        self.jumps = [Jump(self.takeoff_x[i], self.takeoff_y[i], self.takeoff_angle[i], self.takeoff_x[i], self.takeoff_y[i]) for i in range(len(self.takeoff_x))]
        print (f"jump angles={self.takeoff_angle}")

        # Create a Matplotlib canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Connect mouse events
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_click)        
    
        # Add the canvas to the placeholder widget
        layout = QVBoxLayout(self.ui.plotWidget)  # Use the object name from Qt Designer
        layout.addWidget(self.canvas)

    def on_mouse_move(self, event):
      
        if event.inaxes:
            if event.xdata < max(self.line_x[:]) and event.xdata > min(self.line_x[:]):         
                x_mouse = event.xdata  # Mouse x-coordinate

                # Update coord marker
                y_plot = np.interp(x_mouse, self.line_x[:], self.line_y[:])
                self.marker1.set_data([x_mouse], [y_plot])
                
                # self.jumps[-1].plot_jump_trajectory(axis = self.canvas.axes1)

                self.canvas.draw_idle()

    def on_mouse_click(self, event):
        if event.inaxes:
            if event.xdata < max(self.line_x[:]) and event.xdata > min(self.line_x[:]):         
                x_mouse = event.xdata  # Mouse x-coordinate

                # Identify take-off
                for i in reversed(range(len(self.takeoff_x))):
                    if (self.takeoff_x[i] < x_mouse) :
                        break

                # Update coord marker
                y_plot = np.interp(x_mouse, self.line_x[:], self.line_y[:])
                self.marker1.set_data([x_mouse], [y_plot])

                self.jumps[-1].set_jump_parameters(self.takeoff_x[i], self.takeoff_y[i], self.takeoff_angle[i], x_mouse, y_plot)

    # --- Clear previous jump plot and landing marker ---
                if self.jump_plot is not None:
                    self.jump_plot.remove()
                    self.jump_plot = None
                if self.landing_marker is not None:
                    self.landing_marker.remove()
                    self.landing_marker = None

                # --- Plot new jump trajectory and landing marker ---
                jump = self.jumps[-1]
                self.jump_plot, = self.canvas.axes1.plot(
                    jump.x, jump.y, label='Jump Trajectory', color='black', linestyle="-", linewidth=1, alpha=0.7, zorder=12
                )
                self.landing_marker = self.canvas.axes1.scatter(
                    [jump.landing_x], [jump.landing_y], color='red', label='Landing Point', zorder=13, s=40
                )


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
                
        # Plot take-off points
        self.canvas.axes1.scatter(self.takeoff_x, self.takeoff_y, color='blueviolet', marker='^', zorder=8, s=30, alpha=1.0)
        
        # InitializPe landing marker at the last take-off point
        if self.takeoff_x:
            self.marker1, = self.canvas.axes1.plot(self.takeoff_x[-1], self.takeoff_y[-1], color = 'darkturquoise' ,marker='v',  markersize=6, label='Marker', zorder=10, alpha=1.0)

        self.canvas.draw()

if __name__ == "__main__":
    # my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (3.0,-6.0), (2.0,-3.0), (1.0,0.0)]
    # my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (0.7,-70.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (3.0,-6.0), (2.0,-3.0), (1.0,0.0)]
    # my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0)]
    # my_segments = [(1.0,0.0), (0.5,4.0), (0.5,6.0), (0.5,8.0), (0.5,11.0), (0.5,22.0), (0.5,40.0), (0.5,54.0), (1.5,-3.0), (0.5,-7.0), (0.5,-11.0), (2.0,-17.0), (0.5,-8.0), (0.5,0.0)]
    my_segments = [(1.0,0.0), (0.5,4.0), (0.5,6.0), (0.5,8.0), (0.5,11.0), (0.5,22.0), (0.5,40.0), (0.5,54.0), (1.5,-3.0), (0.5,-7.0), (0.5,-11.0), (2.0,-17.0), (0.5,-8.0), (0.5,0.0),(1.0,0.0), (0.5,4.0), (0.5,6.0), (0.5,8.0), (0.5,11.0), (0.5,22.0), (0.5,40.0), (0.5,54.0), (1.5,-3.0), (0.5,-7.0), (0.5,-11.0), (2.0,-17.0), (0.5,-8.0), (0.5,0.0)]

    my_resolution = 0.1 #meters
    drag = RideDrag()
    line = GroundProfile (my_segments, my_resolution) 
   
    app = QApplication(sys.argv)
    window = MainWindow(line)
    window.plot_graph()
    window.show()
    sys.exit(app.exec_())