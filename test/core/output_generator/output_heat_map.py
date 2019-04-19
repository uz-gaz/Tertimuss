import pickle
import unittest

import scipy
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class TestOutput(unittest.TestCase):

    def test_output(self):
        with open('heat_map.txt', 'rb') as fp:
            heat_map = pickle.load(fp)

        # Plot heat map
        sleep_between_frames = 0.01

        min_temp = min(map(lambda x: scipy.amin(x), heat_map)) - 0.5
        max_temp = max(map(lambda x: scipy.amax(x), heat_map)) + 0.5

        fig = plt.figure()

        ims = []

        for i in heat_map:
            im = plt.imshow(i, animated=True)
            ims.append([im])

        ani = animation.ArtistAnimation(fig, ims, interval=2, blit=True,
                                        repeat_delay=1000)

        # ani.save('dynamic_images.mp4')

        plt.show()


if __name__ == '__main__':
    unittest.main()
