import matplotlib.pyplot as plt
import numpy as np

# Example vector properties
magnitude = 5  # Length of the vector
angle = 45  # Angle in degrees
origin = (0, 0)  # Starting point of the vector

# Compute the vector's end point
angle_radians = np.radians(angle)
x_end = origin[0] + magnitude * np.cos(angle_radians)
y_end = origin[1] + magnitude * np.sin(angle_radians)

# Plot the vector as an arrow
plt.figure(figsize=(6, 6))
plt.quiver(
    origin[0], origin[1],  # Arrow start (x, y)
    x_end - origin[0], y_end - origin[1],  # Arrow direction (dx, dy)
    angles='xy', scale_units='xy', scale=1, color='blue', label='Vector'
)

# Add labels and grid
plt.xlim(-1, 10)
plt.ylim(-1, 10)
plt.axhline(0, color='black', linewidth=0.5, linestyle='--')
plt.axvline(0, color='black', linewidth=0.5, linestyle='--')
plt.grid(True)
plt.gca().set_aspect('equal', adjustable='box')
plt.title("Vector Representation")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.legend()
plt.show()