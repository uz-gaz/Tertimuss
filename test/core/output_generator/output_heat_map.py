import pickle
import unittest

import scipy
import matplotlib.pyplot as plt


class TestOutput(unittest.TestCase):

    def test_output(self):
        with open('heat_map.txt', 'rb') as fp:
            heat_map = pickle.load(fp)

        # Plot heat map
        sleep_between_frames = 0.01

        min_temp = min(map(lambda x: scipy.amin(x), heat_map)) - 0.5
        max_temp = max(map(lambda x: scipy.amax(x), heat_map)) + 0.5

        plt.ion()

        fig, ax = plt.subplots(num="Heat map")

        im = ax.imshow(heat_map[0], cmap='viridis', vmax=max_temp, vmin=min_temp)

        # Create colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Temperature ºC", rotation=-90, va="bottom")

        plt.pause(sleep_between_frames)

        for i in range(1, len(heat_map)):
            ax.imshow(heat_map[i], cmap='viridis', vmax=max_temp, vmin=min_temp)
            plt.pause(sleep_between_frames)
            print(i)


if __name__ == '__main__':
    unittest.main()
