from abc import abstractmethod
from typing import Dict, Set, Tuple, List

from .integer_math_utils import list_lcm
from .task import ImplicitDeadlineTask


class AbstractBPPBasedPartitionAlgorithm(object):
    # Cost of this solution O(number_of_cpus * max(O(do_bpp_strategy), O(len(task_set) * log(len(task_set)))))
    def do_partition(self, task_set: Dict[int, ImplicitDeadlineTask], number_of_cpus: int, is_debug: bool = False) \
            -> List[Tuple[int, Set[int]]]:
        """
        Do a partition over the task set
        :param is_debug: True if is debug execution
        :param task_set: Task set to partition
        :param number_of_cpus: Number of cpus
        :return: ID of the tasks in each partition and the number of CPUS for the partition
        """
        m = number_of_cpus
        clusters: List[Tuple[int, Set[int]]] = []

        major_cycle = list_lcm([i.d for i in task_set.values()])

        task_sets_cc_in_major_cycle: Dict[int, int] = {i: j.c * (major_cycle // j.d) for i, j in task_set.items()}

        # Actual number of CPUS
        actual_number_of_cpus = 1

        while actual_number_of_cpus <= m:
            packs: List[Set[int]] = self._do_bpp_strategy(task_sets_cc_in_major_cycle,
                                                          major_cycle * actual_number_of_cpus)

            if is_debug:
                # only for debug purposes
                tasks_in_packs = sum([len(i) for i in packs])
                if tasks_in_packs != len(task_sets_cc_in_major_cycle.keys()) \
                        or set.union(*packs) != task_sets_cc_in_major_cycle.keys():
                    raise Exception("BPP have return an incorrect solution")

            # O(len(tasks) * cost(remove(tasks_to_pack)))
            for pack in packs:
                pack_utilization = sum([task_sets_cc_in_major_cycle[i] for i in pack])
                if pack_utilization == major_cycle * actual_number_of_cpus:
                    clusters.append((actual_number_of_cpus, pack))
                    for task in pack:
                        task_sets_cc_in_major_cycle.pop(task)
                    m = m - actual_number_of_cpus

            actual_number_of_cpus = actual_number_of_cpus + 1

        if m != 0:
            remaining_tasks: Set[int] = {i for i in task_sets_cc_in_major_cycle.keys()}
            clusters.append((m, remaining_tasks))

        return clusters

    @abstractmethod
    def _do_bpp_strategy(self, objects_size: Dict[int, int], bin_size: int) -> List[Set[int]]:
        """
        Run the bpp strategy
        :param objects_size: List of tuples [Objects ID, Size of objects]
        :param bin_size: Size of bins
        :return: List of bins. Each bin is a set with the Objects ID
        """
        pass


class WorstFitBPPBasedPartitionAlgorithm(AbstractBPPBasedPartitionAlgorithm):
    def _do_bpp_strategy(self, objects_size: Dict[int, int], bin_size: int) -> List[Set[int]]:
        """
        Run the bpp strategy
        :param objects_size: List of tuples [Objects ID, Size of objects]
        :param bin_size: Size of bins
        :return: List of bins. Each bin is a set with the Objects ID
        """
        sorted_objects_size: List[Tuple[int, int]] = sorted(objects_size.items(), key=lambda i: i[1])

        bins_sizes: List[Tuple[int, Set[int]]] = [(bin_size, set())]

        for object_id, object_size in sorted_objects_size:
            bin_where_pack: Tuple[int, Tuple[int, Set[int]]] = max(
                (i for i in enumerate(bins_sizes) if i[1][0] >= object_size), key=lambda x: x[1][0],
                default=None)
            if bin_where_pack is None:
                local_bin_where_pack = (bin_size - object_size, {object_id})
                bins_sizes.append(local_bin_where_pack)
            else:
                bin_where_pack[1][1].add(object_id)
                bins_sizes[bin_where_pack[0]] = (bin_where_pack[1][0] - object_size, bin_where_pack[1][1])

        return [i[1] for i in bins_sizes]


class WorstFitDescendantBPPBasedPartitionAlgorithm(AbstractBPPBasedPartitionAlgorithm):
    def _do_bpp_strategy(self, objects_size: Dict[int, int], bin_size: int) -> List[Set[int]]:
        """
        Run the bpp strategy
        :param objects_size: List of tuples [Objects ID, Size of objects]
        :param bin_size: Size of bins
        :return: List of bins. Each bin is a set with the Objects ID
        """
        sorted_objects_size: List[Tuple[int, int]] = sorted(objects_size.items(), key=lambda i: i[1], reverse=True)

        bins_sizes: List[Tuple[int, Set[int]]] = [(bin_size, set())]

        for object_id, object_size in sorted_objects_size:
            bin_where_pack: Tuple[int, Tuple[int, Set[int]]] = max(
                (i for i in enumerate(bins_sizes) if i[1][0] >= object_size), key=lambda x: x[1][0],
                default=None)
            if bin_where_pack is None:
                local_bin_where_pack = (bin_size - object_size, {object_id})
                bins_sizes.append(local_bin_where_pack)
            else:
                bin_where_pack[1][1].add(object_id)
                bins_sizes[bin_where_pack[0]] = (bin_where_pack[1][0] - object_size, bin_where_pack[1][1])

        return [i[1] for i in bins_sizes]


class BestFitBPPBasedPartitionAlgorithm(AbstractBPPBasedPartitionAlgorithm):
    def _do_bpp_strategy(self, objects_size: Dict[int, int], bin_size: int) -> List[Set[int]]:
        """
        Run the bpp strategy
        :param objects_size: List of tuples [Objects ID, Size of objects]
        :param bin_size: Size of bins
        :return: List of bins. Each bin is a set with the Objects ID
        """
        sorted_objects_size: List[Tuple[int, int]] = sorted(objects_size.items(), key=lambda i: i[1])

        bins_sizes: List[Tuple[int, Set[int]]] = [(bin_size, set())]

        for object_id, object_size in sorted_objects_size:
            bin_where_pack: Tuple[int, Tuple[int, Set[int]]] = min(
                (i for i in enumerate(bins_sizes) if i[1][0] >= object_size), key=lambda x: x[1][0],
                default=None)
            if bin_where_pack is None:
                local_bin_where_pack = (bin_size - object_size, {object_id})
                bins_sizes.append(local_bin_where_pack)
            else:
                bin_where_pack[1][1].add(object_id)
                bins_sizes[bin_where_pack[0]] = (bin_where_pack[1][0] - object_size, bin_where_pack[1][1])

        return [i[1] for i in bins_sizes]


class BestFitDescendantBPPBasedPartitionAlgorithm(AbstractBPPBasedPartitionAlgorithm):
    def _do_bpp_strategy(self, objects_size: Dict[int, int], bin_size: int) -> List[Set[int]]:
        """
        Run the bpp strategy
        :param objects_size: List of tuples [Objects ID, Size of objects]
        :param bin_size: Size of bins
        :return: List of bins. Each bin is a set with the Objects ID
        """
        sorted_objects_size: List[Tuple[int, int]] = sorted(objects_size.items(), key=lambda i: i[1], reverse=True)

        bins_sizes: List[Tuple[int, Set[int]]] = [(bin_size, set())]

        for object_id, object_size in sorted_objects_size:
            bin_where_pack: Tuple[int, Tuple[int, Set[int]]] = min(
                (i for i in enumerate(bins_sizes) if i[1][0] >= object_size), key=lambda x: x[1][0],
                default=None)
            if bin_where_pack is None:
                local_bin_where_pack = (bin_size - object_size, {object_id})
                bins_sizes.append(local_bin_where_pack)
            else:
                bin_where_pack[1][1].add(object_id)
                bins_sizes[bin_where_pack[0]] = (bin_where_pack[1][0] - object_size, bin_where_pack[1][1])

        return [i[1] for i in bins_sizes]
