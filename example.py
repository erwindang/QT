import sys
import numpy as np
import matplotlib.pyplot as plt


class line():
    def __init__(self):
        self.x = [0.0, 9.0]
        self.y = [0.0, 3.0]
        self.res = 0.1
        # self.new_x = np.arange(self.x[0], self.x[-1]+self.res, self.res) 
        new_x = np.arange(self.x[0], self.x[-1], self.res)
        #self.new_x.append(self.x[-1])
        self.new_x = np.append(new_x, self.x[-1])
        self.new_y = np.interp(self.new_x,self.x, self.y)

    def plot(self):
        plt.plot(self.x, self.y, 'bo', markersize=5)
        plt.plot(self.new_x, self.new_y, 'r+', markersize=5)
        plt.show()

if __name__ == "__main__":
    my_line = line()
    my_line.plot()
    sys.exit(False)