
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from line import GroundProfile

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        #fig.patch.set_facecolor('black')  # Set the canvas background to black
        self.axes = fig.add_subplot(211)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Compute line
        line = GroundProfile() 
        self.x=line.line_x
        self.y=line.line_y

        self.setWindowTitle("Basic X-Y Graph with PyQt")
        self.setGeometry(100, 100, 1200, 900)
        
        # Set main window background to black
        #self.setStyleSheet("background-color: black; color: white;")

        # Create the main widget and layout
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: black; color: white;")  # Set child widget background to black
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
        self.canvas.axes.clear()
       
        # Set black background and white grid/axes
        # self.canvas.axes.set_facecolor('black')  # Set the background color to black
        # self.canvas.axes.tick_params(colors='white')  # Set tick colors to white
        # self.canvas.axes.spines['bottom'].set_color('white')  # Set x-axis spine color to white
        # self.canvas.axes.spines['left'].set_color('white')  # Set y-axis spine color to white
        # self.canvas.axes.spines['top'].set_color('white')  # Set top spine color to white
        # self.canvas.axes.spines['right'].set_color('white')  # Set right spine color to white
        # self.canvas.axes.yaxis.label.set_color('white')  # Set y-axis label color to white
        # self.canvas.axes.xaxis.label.set_color('white')  # Set x-axis label color to white
        # self.canvas.axes.title.set_color('white')  # Set title color to white
        # self.canvas.axes.grid(color='white', linestyle='--', linewidth=0.5)  # Set grid color to white

        # Text for displaying coordinates
        self.coord_text = self.canvas.axes.text(0.5, 0.9, '', transform=self.canvas.axes.transAxes, bbox=dict(facecolor='white', alpha=0))
        self.coord_text.set_text('x= y=')

        # Plot the line
        ground, = self.canvas.axes.plot(self.x, self.y, color='tan', label='Line', linewidth=1.5, alpha=0.3)
        #ground.set_visible(False)
        # Fill the area below the line
        self.canvas.axes.fill_between(self.x, self.canvas.axes.get_ylim()[0], self.y, color='tan', alpha=0.5)
        
        # Initialize marker
        self.marker, = self.canvas.axes.plot([self.x[-1]], [self.y[-1]], 'b+', markersize=20, label='Marker')
        
        # Add a vertical line to highlight the x position
        self.v_line = self.canvas.axes.axvline(x=self.x[len(self.x)-1], color='b', linestyle='--', linewidth=1, alpha=0.2)
        self.h_line = self.canvas.axes.axhline(y=self.y[len(self.y)-1], color='b', linestyle='--', linewidth=1, alpha=0.2)
        
        # Add labels
        self.canvas.axes.set_title('Basic X-Y Graph')
        self.canvas.axes.set_xlabel('X axis')
        self.canvas.axes.set_ylabel('Y axis')
        self.canvas.axes.grid(True)  
        #self.canvas.axes.axis ('equal')
        #self.canvas.axes.set_ylim(min(self.y)*1.2,max(self.y)*2)   

        # Redraw the canvas
        self.canvas.draw()

    def on_mouse_move(self, event):
        
        if event.inaxes:
            if event.xdata < max(self.x) and event.xdata > min(self.x):         
                # Update marker
                x_mouse = event.xdata  # Mouse x-coordinate
                #y_plot = self.interp_func(x_mouse)  # Compute y-value from plot
                y_plot = np.interp(x_mouse, self.x, self.y)
                self.marker.set_data([x_mouse], [y_plot])
                
                # Update marker lines
                self.v_line.set_xdata([x_mouse])
                self.h_line.set_ydata([y_plot])

                # Update text box coordinates
                self.coord_text.set_text(f'x = {x_mouse:.4f}, y = {y_plot:.4f}')

                self.canvas.draw_idle()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())