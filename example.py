import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# Original data with harsh angles
x = np.array([0, 1, 2, 3, 4, 5])
y = np.array([0, 8, 2, 10, 4, 12])

# Create finer x points for smoother curve
x_fine = np.linspace(min(x), max(x), 100)

# Apply cubic spline interpolation
cs = CubicSpline(x, y)
y_smooth = cs(x_fine)

# Plot original points and smoothed line
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'o-', label='Original Line')
plt.plot(x_fine, y_smooth, '-', label='Smoothed Line')
plt.legend()
plt.title("Cubic Spline Interpolation")
plt.grid(True)
plt.show()