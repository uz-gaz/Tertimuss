import pickle
import unittest

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as manimation


class TestVideo(unittest.TestCase):
    def test_video(self):
        with open('heat_map.txt', 'rb') as fp:
            heat_map = pickle.load(fp)

        FFMpegWriter = manimation.writers['ffmpeg']
        metadata = dict(title='Movie Test', artist='Matplotlib',
                        comment='Movie support!')
        writer = FFMpegWriter(fps=15, metadata=metadata)

        fig = plt.figure()

        with writer.saving(fig, "generated_video.mp4", 100):
            for i in range(len(heat_map)):
                data = heat_map[i]
                heatmap = plt.pcolor(data)
                plt.suptitle(str(i * 0.01) + "Seconds")
                writer.grab_frame()
                print(i)

        print("acabado")


if __name__ == '__main__':
    unittest.main()
