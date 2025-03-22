
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QIntValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.interpolate import interp1d

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.setWindowTitle("Basic X-Y Graph with PyQt")
        self.setGeometry(100, 100, 800, 600)
        
        # Create the main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Create the canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.canvas)
        
        #
        # Create input field sub-layout
        #
        input_layout = QHBoxLayout()

        self.x_label = QLabel("x:")
        input_layout.addWidget(self.x_label)

        self.marker_x_input = QLineEdit("3")  # Default value
        input_layout.addWidget(self.marker_x_input)
        
        # Connect the returnPressed signal to update_graph method
        self.marker_x_input.returnPressed.connect(self.update_graph)
        input_layout.addWidget(self.marker_x_input)

        # Set validator to restrict range
        self.marker_x_input.setValidator(QIntValidator(0, 99))

        # Add the input layout to the main layout
        layout.addLayout(input_layout)

        # Set the central widget
        self.setCentralWidget(main_widget)

        # Initialize graph
        self.marker_x = int(self.marker_x_input.text())
        self.plot_graph()

    def update_graph(self):
            try:
                # Get the marker x value from the input field
                marker_x_text = self.marker_x_input.text()
                self.marker_x = int(marker_x_text)
                
                # Update the graph
                self.plot_graph()
                
            except ValueError:
                # Show error message if input is not a valid float
                QMessageBox.warning(self, "Invalid Input", 
                                "Please enter a valid number for the amplitude.")

    def plot_graph(self):
   
        # Create some sample data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)

        # Limit marker position
        if (self.marker_x > len(x)-1) : 
            marker_x_graph = len(x)-1
        else:
            marker_x_graph = self.marker_x

        # Clear the previous plot
        self.canvas.axes.clear()
        
        # Text for displaying coordinates
        self.coord_text = self.canvas.axes.text(0.05, 0.95, '', transform=self.canvas.axes.transAxes, bbox=dict(facecolor='white', alpha=0.8))
        self.coord_text.set_text('x= y=')

        # Connect mouse events
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        #self.canvas.mpl_connect('button_press_event', self.on_mouse_click)

        # Plot the line
        self.canvas.axes.plot(x, y, 'r-')

        
        # Plot dot marker at the specified x position
        self.canvas.axes.plot(x[marker_x_graph], y[marker_x_graph] , 'bo', markersize=5, label=f'Point at x={x[marker_x_graph]:.2f}')
        
        # Add a vertical line to highlight the x position
        self.canvas.axes.axvline(x=x[marker_x_graph], color='b', linestyle='-', linewidth=1, alpha=0.5)
        self.canvas.axes.axhline(y=y[marker_x_graph], color='b', linestyle='-', linewidth=1, alpha=0.5)
        
        # Add labels
        self.canvas.axes.set_title('Basic X-Y Graph')
        self.canvas.axes.set_xlabel('X axis')
        self.canvas.axes.set_ylabel('Y axis')
        self.canvas.axes.grid(True)  

        # Redraw the canvas
        self.canvas.draw()

    def on_mouse_move(self, event):
        if event.inaxes:
            self.coord_text.set_text(f'x = {event.xdata:.4f}, y = {event.ydata:.4f}')
            self.canvas.draw_idle()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())