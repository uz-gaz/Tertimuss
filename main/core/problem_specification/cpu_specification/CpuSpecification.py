import itertools
import math
from typing import List

from main.core.problem_specification.cpu_specification.BoardSpecification import BoardSpecification
from main.core.problem_specification.cpu_specification.CoreGroupSpecification import CoreGroupSpecification
from main.core.problem_specification.cpu_specification.Origin import Origin


class CpuSpecification(object):

    def __init__(self, board_specification: BoardSpecification, cores_specification: CoreGroupSpecification):
        """
        Specification of a processor

        :param board_specification: Specification of the board where cores are located
        :param cores_specification: Specification of the cores
        """
        self.board_specification: BoardSpecification = board_specification
        self.cores_specification: CoreGroupSpecification = cores_specification

        if self.cores_specification.cores_origins is None and board_specification is not None:
            # Generate automatic origins if none origins provided
            self.cores_specification.cores_origins = \
                self.__generate_automatic_origins(0, self.board_specification.physical_properties.x,
                                                  0, self.board_specification.physical_properties.y,
                                                  self.cores_specification.physical_properties.x,
                                                  self.cores_specification.physical_properties.y,
                                                  len(self.cores_specification.operating_frequencies))

    @classmethod
    def __generate_automatic_origins(cls, x0: float, x1: float, y0: float, y1: float, mx: float, my: float,
                                     m: int) -> List[Origin]:
        """
        Generate automatic origins distributed over the board in a symmetrical way
        :param x0: board left edge position
        :param x1: board right edge position
        :param y0: board bottom edge position
        :param y1: board top edge position
        :param mx: core width
        :param my: core height
        :param m: number of cores
        :return:
        """
        if m == 1:
            return [Origin(x0 + (x1 - x0 - mx) / 2, y0 + (y1 - y0 - my) / 2)]
        else:
            if (x1 - x0) >= (y1 - y0):
                return cls.__generate_automatic_origins(x0, x0 + (x1 - x0) / 2, y0, y1, mx, my, math.ceil(m / 2)) + \
                       cls.__generate_automatic_origins(x0 + (x1 - x0) / 2, x1, y0, y1, mx, my, math.floor(m / 2))
            else:
                return cls.__generate_automatic_origins(x0, x1, y0, y0 + (y1 - y0) / 2, mx, my, math.ceil(m / 2)) + \
                       cls.__generate_automatic_origins(x0, x1, y0 + (y1 - y0) / 2, y1, mx, my, math.floor(m / 2))

    @staticmethod
    def check_origins(cpu_origins: List[Origin], x_size_cpu: float, y_size_cpu: float, x_size_board: float,
                      y_size_board: float) -> bool:
        """
        Checks if any core overlaps with other core

        :param x_size_board: width of the board
        :param y_size_cpu: height of the core
        :param x_size_cpu: width of the core
        :param y_size_board: height of the board
        :param cpu_origins: list of cpu cores origins
        :return: true if no core overlaps with other core and all have valid positions, false otherwise
        """

        def overlaps(cpu_1_origin: Origin, cpu_2_origin: Origin, x_size: float, y_size: float):
            """
            Check if two cores overlap

            :param cpu_1_origin: first core
            :param cpu_2_origin: second core
            :param x_size: width of the cores
            :param y_size: height of the cores
            :return: true if they overlap, false otherwise
            """
            return not ((cpu_1_origin.x > cpu_2_origin.x + x_size or cpu_2_origin.x > cpu_1_origin.x + x_size) or (
                    cpu_1_origin.y < cpu_2_origin.y + y_size or cpu_2_origin.y < cpu_1_origin.y))

        return all([a.x + x_size_cpu <= x_size_board and a.y + y_size_cpu <= y_size_board for a in cpu_origins]) and \
               not any([overlaps(a[0], a[1], x_size_cpu, y_size_cpu) for a in itertools.combinations(cpu_origins, 2)])
