import itertools
import math
from typing import List

from main.core.problem_specification.cpu_specification.BoardSpecification import BoardSpecification
from main.core.problem_specification.cpu_specification.CoreGroupSpecification import CoreGroupSpecification
from main.core.problem_specification.cpu_specification.Origin import Origin


class CpuSpecification(object):

    def __init__(self, board_specification: BoardSpecification, cores_specification: CoreGroupSpecification):
        """
        CPU specification

        :param board_specification: Specification of the board
        :param cores_specification: Specification of the cores
        """
        self.board_specification: BoardSpecification = board_specification
        self.cores_specification: CoreGroupSpecification = cores_specification

        if self.cores_specification.cores_origins is None and board_specification is not None:
            # Generate automatic origins
            self.cores_specification.cores_origins = \
                self.__generate_automatic_origins(0, self.board_specification.physical_properties.x,
                                                  0, self.board_specification.physical_properties.y,
                                                  self.cores_specification.physical_properties.x,
                                                  self.cores_specification.physical_properties.y,
                                                  len(self.cores_specification.operating_frequencies))

    @classmethod
    def __generate_automatic_origins(cls, x0: float, x1: float, y0: float, y1: float, mx: float, my: float,
                                     n: int) -> List[Origin]:
        # Distribute CPUs in a symmetrical way
        if n == 1:
            return [Origin(x0 + (x1 - x0 - mx) / 2, y0 + (y1 - y0 - my) / 2)]
        else:
            if (x1 - x0) >= (y1 - y0):
                return cls.__generate_automatic_origins(x0, x0 + (x1 - x0) / 2, y0, y1, mx, my, math.ceil(n / 2)) + \
                       cls.__generate_automatic_origins(x0 + (x1 - x0) / 2, x1, y0, y1, mx, my, math.floor(n / 2))
            else:
                return cls.__generate_automatic_origins(x0, x1, y0, y0 + (y1 - y0) / 2, mx, my, math.ceil(n / 2)) + \
                       cls.__generate_automatic_origins(x0, x1, y0 + (y1 - y0) / 2, y1, mx, my, math.floor(n / 2))

    @staticmethod
    def check_origins(cpu_origins: List[Origin], x_size_cpu: float, y_size_cpu: float, x_size_board: float,
                      y_size_board: float) -> bool:
        """
        Return true if no core overlap

        :param x_size_board: x size of board
        :param y_size_cpu: y size of core
        :param x_size_cpu: x size of core
        :param y_size_board: y size of board
        :param cpu_origins: cpu core origins list
        :return: true if no core overlap with others and all are valid
        """

        def overlaps(cpu_1_origin: Origin, cpu_2_origin: Origin, x_size: float, y_size: float):
            """
            Return true if cpu 1 and cpu 2 overlaps
            Ref: https://www.geeksforgeeks.org/find-two-rectangles-overlap/

            :param cpu_1_origin: cpu 1 origins
            :param cpu_2_origin: cpu 2 origins
            :param x_size: cpus x size
            :param y_size: cpus y size
            :return: true if overlaps false otherwise
            """
            return not ((cpu_1_origin.x > cpu_2_origin.x + x_size or cpu_2_origin.x > cpu_1_origin.x + x_size) or (
                    cpu_1_origin.y < cpu_2_origin.y + y_size or cpu_2_origin.y < cpu_1_origin.y))

        return all(
            map(lambda a: a.x + x_size_cpu <= x_size_board and a.y + y_size_cpu <= y_size_board,
                cpu_origins)) and not any(
            map(lambda a: overlaps(a[0], a[1], x_size_cpu, y_size_cpu), itertools.combinations(cpu_origins, 2)))
