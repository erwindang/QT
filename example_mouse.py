import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(fig)
        
        # Generate sample data
        self.x = np.linspace(0, 10, 100)
        self.y = np.sin(self.x)
        
        # Plot the data
        self.axes.plot(self.x, self.y)
        self.axes.set_title('Mouse Position Tracking')
        
        # Text for displaying coordinates
        self.coord_text = self.axes.text(0.05, 0.95, '', transform=self.axes.transAxes,
                                        bbox=dict(facecolor='white', alpha=0.8))
        
        # Connect mouse events
        self.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.mpl_connect('button_press_event', self.on_mouse_click)
    
    def on_mouse_move(self, event):
        if event.inaxes:
            self.coord_text.set_text(f'x = {event.xdata:.4f}, y = {event.ydata:.4f}')
            self.draw_idle()
        else:
            self.coord_text.set_text('')
            self.draw_idle()
    
    def on_mouse_click(self, event):
        if event.inaxes:
            print(f"Clicked at x = {event.xdata:.4f}, y = {event.ydata:.4f}")
            
            # Find the closest point in our data
            idx = np.abs(self.x - event.xdata).argmin()
            print(f"Closest data point: x = {self.x[idx]:.4f}, y = {self.y[idx]:.4f}")


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Set up the main window
        self.setWindowTitle("Qt Matplotlib Mouse Tracking")
        self.setGeometry(100, 100, 800, 600)
        
        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create the matplotlib canvas and add it to the layout
        self.canvas = MatplotlibCanvas(self, width=8, height=6, dpi=100)
        layout.addWidget(self.canvas)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())