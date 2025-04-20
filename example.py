import matplotlib.pyplot as plt
import numpy as np

# Define the grid
x = np.arange(0, 5, 1)
y = np.arange(0, 5, 1)
X, Y = np.meshgrid(x, y)

# Define the vector components
U = np.ones_like(X)  # x-component of the vector
V = np.ones_like(Y)  # y-component of the vector

# Create the quiver plot
plt.quiver(X, Y, U, V, color='blue', scale=1)

# Add labels and title
plt.title("Quiver Plot Example")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")

# Show the plot
plt.show()