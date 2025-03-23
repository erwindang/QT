import sys
import numpy as np
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from scipy.interpolate import interp1d

class MouseTrackingCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        
        # Sample plot data
        self.x_data = np.linspace(0, 10, 100)
        self.y_data = np.sin(self.x_data)
        self.ax.plot(self.x_data, self.y_data, 'b-')
        
        # Initialize marker
        self.marker, = self.ax.plot([], [], 'ro', markersize=8, label='Marker')
        
        # Interpolation function for y-values
        self.interp_func = interp1d(self.x_data, self.y_data, kind='linear')
        
        # Connect mouse motion event
        self.mpl_connect('motion_notify_event', self._update_marker)

    def _update_marker(self, event):
        if event.inaxes == self.ax:
            x_mouse = event.xdata  # Mouse x-coordinate
            y_plot = self.interp_func(x_mouse)  # Compute y-value from plot
            
            # Update marker position
            self.marker.set_data([x_mouse], [y_plot])
            self.fig.canvas.draw_idle()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mouse Tracking with Plot Y-Value")
        
        # Create plot canvas
        self.canvas = MouseTrackingCanvas(self)
        
        # Add navigation toolbar
        toolbar = NavigationToolbar2QT(self.canvas, self)
        
        # Setup layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
