import pickle
import unittest

import scipy
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class TestOutput(unittest.TestCase):

    def heatmap_animation1(self):
        NUMBER_X: int = 10
        NUMBER_Y: int = 10

        CANVAS_WIDTH: int = 10
        CANVAS_HEIGHT: int = 10

        fig = plt.figure()

        # ax_lst = ax_lst.ravel()

        def plot(data):
            data = np.random.rand(CANVAS_WIDTH, CANVAS_HEIGHT)
            heatmap = plt.pcolor(data)

        ani = animation.FuncAnimation(fig, plot, interval=1)
        plt.show()

    def heatmap_animation2(self):
        with open('heat_map.txt', 'rb') as fp:
            heat_map = pickle.load(fp)

        fig = plt.figure()

        def plot(i):
            data = heat_map[i]
            heatmap = plt.pcolor(data)
            plt.suptitle(str(i))

        ani = animation.FuncAnimation(fig, plot, len(heat_map), interval=1)
        plt.show()

    def test_output(self):
        with open('heat_map.txt', 'rb') as fp:
            heat_map = pickle.load(fp)

        fig = plt.figure()

        def plot(i):
            data = heat_map[i]
            plt.pcolor(data)
            plt.suptitle(str(i))

        animation.FuncAnimation(fig, plot, len(heat_map), interval=1)
        plt.show()


if __name__ == '__main__':
    unittest.main()
