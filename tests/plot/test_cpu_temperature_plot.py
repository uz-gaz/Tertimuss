import unittest

from matplotlib import animation

from tertimuss.plot_generator._cpu_temperature_plot import generate_board_temperature_evolution_2d_video, \
    generate_cpu_temperature_evolution_3d_video
from tests.plot._generate_simulation_result import get_simulation_result


class CpuTemperaturePlotTest(unittest.TestCase):
    @unittest.skip("Manual visualization test")
    def test_board_temperature_evolution_2d_plot(self):
        tasks, _, simulation_result = get_simulation_result()

        heat_map_2d_video = generate_board_temperature_evolution_2d_video(schedule_result=simulation_result,
                                                                          title="Temperature evolution video")
        writer = animation.FFMpegWriter()
        heat_map_2d_video.save("2d_generation.mp4", writer=writer)

    @unittest.skip("Manual visualization test")
    def test_cpu_temperature_evolution_3d_plot(self):
        tasks, _, simulation_result = get_simulation_result()

        heat_map_3d_video = generate_cpu_temperature_evolution_3d_video(schedule_result=simulation_result,
                                                                        title="Temperature evolution video")
        writer = animation.FFMpegWriter()
        heat_map_3d_video.save("3d_generation.mp4", writer=writer)
