import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from main_window import Ui_MainWindow  # Import the generated UI class

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes1 = fig.add_subplot(311)
        self.axes2 = fig.add_subplot(312, sharex=self.axes1)
        self.axes3 = fig.add_subplot(313, sharex=self.axes1)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Create a Matplotlib canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Add the canvas to the placeholder widget
        layout = QVBoxLayout(self.ui.plotWidget)  # Use the object name from Qt Designer
        layout.addWidget(self.canvas)

        # Example plot
        self.canvas.axes1.plot([0, 1, 2, 3], [10, 1, 20, 3])
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())