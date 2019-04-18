import matplotlib.pyplot as plt
import numpy as np

plt.ion()

fig, ax = plt.subplots()

a = np.random.random((16, 16))
im = ax.imshow(a, cmap='hot', vmax=100, vmin=0)

# Create colorbar
cbar = ax.figure.colorbar(im, ax=ax)
cbar.ax.set_ylabel("Temperature", rotation=-90, va="bottom")

for i in range(10):
    a = np.random.random((16, 16))
    im = ax.imshow(a, cmap='hot', vmax=100, vmin=0)
    # plt.imshow(a, cmap='hot')
    plt.pause(0.3)
