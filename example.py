import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QLineEdit, QHBoxLayout, QLabel, QMessageBox)
from PyQt5.QtGui import QDoubleValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.setWindowTitle("Sine Wave with X-Position Marker")
        self.setGeometry(100, 100, 800, 600)
        
        # Create the main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Create input layout
        input_layout = QHBoxLayout()
        
        # Add x-position input field
        self.x_pos_label = QLabel("X Position (0-10) [Press Enter to update]:")
        input_layout.addWidget(self.x_pos_label)
        
        self.x_pos_input = QLineEdit("5.0")  # Default value
        self.x_pos_input.setPlaceholderText("Enter X position")
        
        # Set validator to restrict range from 0 to 10
        self.x_pos_input.setValidator(QDoubleValidator(0, 10, 2))
        
        # Connect the returnPressed signal to update_graph method
        self.x_pos_input.returnPressed.connect(self.update_graph)
        input_layout.addWidget(self.x_pos_input)
        
        # Add the input layout to the main layout
        main_layout.addLayout(input_layout)
        
        # Create the canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        main_layout.addWidget(self.canvas)
        
        # Set the central widget
        self.setCentralWidget(main_widget)
        
        # Initial values
        self.x_position = 5.0
        self.amplitude = 1.0  # Fixed amplitude for the sine wave
        self.plot_graph()
    
    def plot_graph(self):
        # Clear the previous plot
        self.canvas.axes.clear()
        
        # Create data for the sine wave
        x = np.linspace(0, 10, 100)
        y = self.amplitude * np.sin(x)
        
        # Plot the sine wave
        self.canvas.axes.plot(x, y, 'b-', label='sin(x)')
        
        # Calculate the y value at the specified x position
        y_at_x = self.amplitude * np.sin(self.x_position)
        
        # Add a dot marker at the specified x position
        self.canvas.axes.plot(self.x_position, y_at_x, 'ro', markersize=10, 
                              label=f'Point at x={self.x_position:.2f}')
        
        # Add a vertical line to highlight the x position
        self.canvas.axes.axvline(x=self.x_position, color='r', linestyle='--', alpha=0.5)
        
        # Set titles and labels
        self.canvas.axes.set_title(f'Sine Wave with Marker at x = {self.x_position:.2f}')
        self.canvas.axes.set_xlabel('X axis')
        self.canvas.axes.set_ylabel('Y axis')
        
        # Set x and y axis limits
        self.canvas.axes.set_xlim(0, 10)
        self.canvas.axes.set_ylim(-1.5, 1.5)
        
        # Add grid and legend
        self.canvas.axes.grid(True)
        self.canvas.axes.legend()
        
        # Show the coordinates of the marked point
        self.canvas.axes.annotate(f'({self.x_position:.2f}, {y_at_x:.2f})', 
                                 (self.x_position, y_at_x),
                                 xytext=(5, 10), textcoords='offset points',
                                 ha='center')
        
        # Redraw the canvas
        self.canvas.draw()
    
    def update_graph(self):
        try:
            # Get the x position from the input field
            x_pos_text = self.x_pos_input.text()
            
            # If empty, set to default
            if not x_pos_text:
                self.x_position = 5.0
            else:
                # Convert to float and ensure it's within the valid range
                new_x_position = float(x_pos_text)
                if 0 <= new_x_position <= 10:
                    self.x_position = new_x_position
                else:
                    QMessageBox.warning(self, "Invalid Input", 
                                      "X position must be between 0 and 10.")
                    return
            
            # Update the graph
            self.plot_graph()
            
        except ValueError:
            # Show error message if input is not a valid float
            QMessageBox.warning(self, "Invalid Input", 
                               "Please enter a valid number for the X position.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())