import unittest

from tertimuss.visualization import generate_frequency_evolution_plot
from ._generate_simulation_result import get_simulation_result


class FrequencyEvolutionPlotTest(unittest.TestCase):
    def test_frequency_evolution_plot(self):
        _, _, simulation_result = get_simulation_result()

        fig = generate_frequency_evolution_plot(schedule_result=simulation_result, title="Frequency evolution")
