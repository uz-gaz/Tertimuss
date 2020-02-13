from typing import List

import scipy


class RUNServer(object):
    def __init__(self, c: int, d: int):
        # c: WCET in cycles
        # d: deadline in cycles
        self.c = c
        self.d = d
        self.laxity = d - c
        self.pending_c = self.c
        self.pending_laxity = self.laxity
        self.next_arrive = self.d
        self.server_id = id(self)

        # This value will be used to give more priority to the last executed task
        self.last_time_executed_dual = 0
        self.last_time_executed_edf = 0


class RUNTask(RUNServer):
    def __init__(self, task_id: int, c: int, d: int):
        self.task_id = task_id
        self.last_cpu_execution = -1
        super().__init__(c, d)


class RUNPack(RUNServer):
    """
    This class represent the union of a DUAL and an EDF server
    """

    def __init__(self, content: List[RUNServer]):
        self.content = content
        d = scipy.gcd.reduce([i.d for i in content])
        c = sum([(i.laxity if isinstance(i, RUNPack) else i.c) * (d / i.d) for i in content])
        super().__init__(c, d)


class PacksBin(object):
    def __init__(self, pack: RUNServer):
        self.c = pack.laxity if isinstance(pack, RUNPack) else pack.c
        self.d = pack.d
        self.packs = [pack]

    def can_add_server(self, pack: RUNServer) -> bool:
        deadline = scipy.gcd.reduce([pack.d, self.d])
        bin_c = int(self.c / (self.d / deadline))
        ant_pack_c = pack.laxity if isinstance(pack, RUNPack) else pack.c
        pack_c = int(ant_pack_c / (pack.d / deadline))
        return bin_c + pack_c <= deadline

    def add_server(self, pack: RUNServer):
        deadline = scipy.gcd.reduce([pack.d, self.d])
        bin_c = float(self.c / (self.d / deadline))
        ant_pack_c = pack.laxity if isinstance(pack, RUNPack) else pack.c
        pack_c = float(ant_pack_c / (pack.d / deadline))
        self.c = bin_c + pack_c
        self.d = deadline
        self.packs.append(pack)

    def transform_to_pack(self) -> RUNPack:
        return RUNPack(self.packs)


class ReductionToUNiprocessorScheduler(object):

    @classmethod
    def _create_packs_from_virtual_tasks(cls, packs: List[RUNServer]) -> List[RUNPack]:
        started_bins: List[PacksBin] = []

        packs.sort(key=lambda x: (x.laxity if isinstance(x, RUNPack) else x.c) / x.d,
                   reverse=True)  # Sort packs in descendant order of utilization

        for pack in packs:
            emptiest_bin_index = None

            if len(started_bins) > 0:
                emptiest_bin_index = scipy.argmin([x.c / x.d for x in started_bins])

            if emptiest_bin_index is not None and started_bins[emptiest_bin_index].can_add_server(pack):
                started_bins[emptiest_bin_index].add_server(pack)
            else:
                started_bins.append(PacksBin(pack))

        return [actual_bin.transform_to_pack() for actual_bin in started_bins]

    @classmethod
    def _create_recursive_tree(cls, packs: List[RUNServer]) -> List[RUNPack]:
        tree_parents: List[RUNPack] = []
        tree_children: List[RUNServer] = []

        for pack in packs:
            if pack.laxity == 0 and isinstance(pack, RUNPack):
                tree_parents.append(pack)
            else:
                tree_children.append(pack)

        if len(tree_children) > 0:
            tree_parents = tree_parents + cls._create_recursive_tree(
                cls._create_packs_from_virtual_tasks(tree_children))
            return tree_parents
        else:
            return tree_parents

    @classmethod
    def _create_tree(cls, tasks: List[RUNTask]) -> List[RUNPack]:
        parents = cls._create_recursive_tree(tasks)
        return parents


if __name__ == '__main__':
    tasks = [
        RUNTask(0, 77, 1000),
        RUNTask(1, 300, 1000),
        RUNTask(2, 288, 1000),
        RUNTask(3, 296, 1000),
        RUNTask(4, 175, 1000),
        RUNTask(5, 115, 1000),
        RUNTask(6, 145, 1000),
        RUNTask(7, 279, 1000),
        RUNTask(8, 197, 1000),
        RUNTask(9, 128, 1000)
    ]

    print(sum([i.c for i in tasks]))
