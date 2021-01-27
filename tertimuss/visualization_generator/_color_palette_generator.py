import abc
from typing import List, Tuple

from matplotlib import pyplot, colors, cm


class AbstractColorPaletteGenerator(metaclass=abc.ABCMeta):

    @staticmethod
    @abc.abstractmethod
    def obtain_color_palette(number_of_colors: int) -> List[Tuple[int, int, int, int]]:
        """
        Return a color palette
        :param number_of_colors: number of colors to return
        :return: the color palette generated.
                 List of colors. Each element is a tuple that represents a RGBA color.
        """
        pass


class DefaultColorPaletteGenerator(AbstractColorPaletteGenerator):
    @staticmethod
    def obtain_color_palette(number_of_colors: int) -> List[Tuple[int, int, int, int]]:
        """
        Return a color palette
        :param number_of_colors: number of colors to return
        :return: the color palette generated.
                 List of colors. Each element is a tuple that represents a RGBA color.
        """
        color_map = pyplot.get_cmap('RdYlGn')
        c_norm = colors.Normalize(vmin=0, vmax=number_of_colors - 1)
        scalar_map = cm.ScalarMappable(norm=c_norm, cmap=color_map)
        return [scalar_map.to_rgba(i) for i in range(number_of_colors)]
