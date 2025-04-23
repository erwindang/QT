
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from line import GroundProfile
from ride import RideDrag, SpeedVector, RideSimulation
from scipy.interpolate import CubicSpline

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        #fig.patch.set_facecolor('black')  # Set the canvas background to black
        self.axes1 = fig.add_subplot(311)
        self.axes2 = fig.add_subplot(312)
        self.axes3 = fig.add_subplot(313)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self, line, ride_simulation):
        super(MainWindow, self).__init__()

        # Compute line
        # self.simulation = ride_simulation
        self.x=line.x
        self.y=line.y

        self.setWindowTitle("Basic X-Y Graph with PyQt")
        self.setGeometry(100, 100, 1200, 900)
        
        # Set main window background to black
        #self.setStyleSheet("background-color: black; color: white;")

        # Create the main widget and layout
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: white; color: white;")  # Set child widget background to black
        layout = QVBoxLayout(main_widget)
        
        # Create the canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.canvas)
        
        # Connect mouse events
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        #self.canvas.mpl_connect('button_press_event', self.on_mouse_click)
       
        # Set the central widget
        self.setCentralWidget(main_widget)

        # Initialize graph
        self.plot_graph()

    def plot_graph(self):

        # Clear the previous plot
        self.canvas.axes1.clear()
        self.canvas.axes2.clear()
       
        # Set black background and white grid/axes
        # self.canvas.axes1.set_facecolor('dimgrey')  # Set the background color to black
        # self.canvas.axes2.set_facecolor('dimgrey')  # Set the background color to black
        # self.canvas.axes1.tick_params(colors='white')  # Set tick colors to white
        # self.canvas.axes1.spines['bottom'].set_color('white')  # Set x-axis spine color to white
        # self.canvas.axes1.spines['left'].set_color('white')  # Set y-axis spine color to white
        # self.canvas.axes1.spines['top'].set_color('white')  # Set top spine color to white
        # self.canvas.axes1.spines['right'].set_color('white')  # Set right spine color to white
        # self.canvas.axes1.yaxis.label.set_color('white')  # Set y-axis label color to white
        # self.canvas.axes1.xaxis.label.set_color('white')  # Set x-axis label color to white
        # self.canvas.axes1.title.set_color('white')  # Set title color to white
        # self.canvas.axes1.grid(color='white', linestyle='--', linewidth=0.5)  # Set grid color to white

        # Plot line profile
        # ground, = self.canvas.axes1.plot(self.x, self.y, color='tan', label='Line', linewidth=1.5, alpha=0.3)
        # self.canvas.axes1.fill_between(self.x, self.canvas.axes1.get_ylim()[0], self.y, color='tan', alpha=0.5)
        
        # Plot line profile with smoothing
        cubic_spline = CubicSpline(self.x, self.y)
        smooth_x = np.linspace(min(self.x), max(self.x), 200)  # 500 points for a smooth curve
        smooth_y = cubic_spline(smooth_x)
        ground, = self.canvas.axes1.plot(smooth_x, smooth_y, color='tan', label='Line', linewidth=1.0, alpha=0.2)
        self.canvas.axes1.fill_between(smooth_x, self.canvas.axes1.get_ylim()[0], smooth_y, color='tan', alpha=0.6)

        # Plot trajectory
        self.positions = np.array(simulation.trajectory.positions)
        self.canvas.axes1.plot(self.positions[:, 0], self.positions[:, 1], label="Trajectory", color="blue", marker='+', markersize=1, linestyle="None", alpha=0.5)
        self.canvas.axes1.set_title('Line')
        # self.canvas.axes1.set_xlabel('m')
        self.canvas.axes1.set_ylabel('(m)')
        self.canvas.axes1.grid(True)  
        self.canvas.axes1.axis ('equal')
        self.canvas.axes1.set_xlim(min(self.x),max(self.x))
        # self.canvas.axes1.set_ylim(min(self.y)*1.2,max(self.y)*2)   
       
        # Plot speed
        self.speeds = np.array([abs(speed.value) for speed in simulation.trajectory.speed])
        self.canvas.axes2.plot(self.positions[:, 0], self.speeds, label="Speed", color="red", marker='+', markersize=1, linestyle="None", alpha=0.5)
        self.canvas.axes2.set_title('Speed')    
        self.canvas.axes2.set_xlabel('distance (m)')
        self.canvas.axes2.set_ylabel('(m/s)')
        self.canvas.axes2.grid(True)
        # self.canvas.axes2.axis ('equal')
        # self.canvas.axes2.set_xlim(min(self.speeds),max(self.speeds[:]))
        # self.canvas.axes2.set_ylim(min(self.speeds),max(self.speeds[:]))       

        # Initialize marker and marker lines
        self.marker1, = self.canvas.axes1.plot(self.positions[-1, 0], self.positions[-1, 1], 'b+', markersize=20, label='Marker')
        self.v_line1 = self.canvas.axes1.axvline(x=self.positions[-1, 0], color='b', linestyle='--', linewidth=1, alpha=0.2)
        self.h_line1 = self.canvas.axes1.axhline(y=self.positions[-1, 1], color='b', linestyle='--', linewidth=1, alpha=0.2)

        self.marker2, = self.canvas.axes2.plot(self.positions[-1, 0], self.positions[-1, 1], 'r+', markersize=20, label='Marker')
        self.v_line2 = self.canvas.axes2.axvline(x=self.positions[-1, 0], color='r', linestyle='--', linewidth=1, alpha=0.2)
        self.h_line2 = self.canvas.axes2.axhline(y=self.speeds[-1], color='r', linestyle='--', linewidth=1, alpha=0.2)

        # Text for displaying coordinates
        self.coord_text = self.canvas.axes1.text(0.5, 0.9, '', transform=self.canvas.axes1.transAxes, bbox=dict(facecolor='white', alpha=0))
        self.coord_text.set_text(f'x: {self.positions[-1, 0]:.3f}  y: {self.positions[-1, 1]:.3f}')

        # Text for displaying speed
        self.speed_text = self.canvas.axes2.text(0.5, 0.9, '', transform=self.canvas.axes2.transAxes, bbox=dict(facecolor='white', alpha=0))
        self.speed_text.set_text(f'{self.speeds[-1]:.3f} (m/s)')

        # Redraw the canvas
        self.canvas.draw()

    def on_mouse_move(self, event):
        
        if event.inaxes:
            if event.xdata < max(self.positions[:, 0]) and event.xdata > min(self.positions[:, 0]):         
                x_mouse = event.xdata  # Mouse x-coordinate

                # Update coord marker
                y_plot = np.interp(x_mouse, self.positions[:, 0], self.positions[:, 1])
                self.marker1.set_data([x_mouse], [y_plot])
                self.v_line1.set_xdata([x_mouse])
                self.h_line1.set_ydata([y_plot])
                self.coord_text.set_text(f'x = {x_mouse:.3f}, y = {y_plot:.3f}')

                # Update speed marker
                y_plot = np.interp(x_mouse, self.positions[:, 0], self.speeds)
                self.marker2.set_data([x_mouse], [y_plot])
                self.v_line2.set_xdata([x_mouse])
                self.h_line2.set_ydata([y_plot])
                self.speed_text.set_text(f'{y_plot:.3f} (m/s)')

                self.canvas.draw_idle()


if __name__ == "__main__":
    # my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (3.0,-6.0), (2.0,-3.0), (1.0,0.0)]
    # my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0), (1.0,-14.0), (0.7,-70.0), (1.0,-11.0), (1.0,-20.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-25.0), (1.0,-16.0), (1.0,-6.0), (1.0,-3.0), (1.0,0.0), (1.0,4.0), (1.0,4.0), (1.0,4.0), (1.0,11.0), (1.0,22.0), (1.0,40.0), (0.5,54.0), (1.5,0.0), (1.0,-17.0), (1.0,-21.0), (1.0,-20.0), (3.0,-6.0), (2.0,-3.0), (1.0,0.0)]
    # my_segments = [(1.0,-4.0), (1.0,-4.0), (1.0,-8.0), (1.0,-11.0)]
    my_segments = [(1.0,0.0), (0.5,4.0), (0.5,6.0), (0.5,8.0), (0.5,11.0), (0.5,22.0), (0.5,40.0), (0.5,54.0), (1.5,-3.0), (0.5,-7.0), (0.5,-11.0), (2.0,-17.0), (0.5,-8.0), (0.5,0.0)]
    #my_segments = [(1.0,-20.0), (1.0, -70.0), (1.0,0.0)]
    # my_segments = [(1.0,-4.0)]
    # my_segments = [(1.0, 0.0)]
    my_resolution = 0.1 #meters
    start_speed = SpeedVector(1, 0.0, "m/s")  # Initial speed of the rider
    drag = RideDrag()
    line = GroundProfile (my_segments, my_resolution) 
    simulation = RideSimulation(line, start_speed, drag)
    simulation.run()

    app = QApplication(sys.argv)
    window = MainWindow(line, simulation)
    window.show()
    
    sys.exit(app.exec_())