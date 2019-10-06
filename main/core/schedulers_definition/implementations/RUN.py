from typing import List

import scipy


class VirtualTask(object):
    def __init__(self, c: int, d: int):
        self.c = c
        self.d = d
        self.laxity = d - c
        self.pending_c = self.c
        self.pending_laxity = self.laxity
        self.next_arrive = self.d


class Pack(VirtualTask):
    def __init__(self, content: List[VirtualTask]):
        self.content = content
        d = int(scipy.gcd.reduce([i.d for i in content]))
        c = int(sum([i.laxity * (d / i.d) for i in content]))
        super().__init__(c, d)


class RUNTask(VirtualTask):
    def __init__(self, task_id: int, c: int, d: int):
        self.task_id = task_id
        super().__init__(c, d)


class PacksBin(object):
    def __init__(self, c: int, d: int, packs: List[VirtualTask]):
        self.c = c
        self.d = d
        self.packs = packs


def create_packs_from_virtual_tasks(packs: List[VirtualTask]) -> List[Pack]:
    started_bins: List[PacksBin] = []

    packs.sort(key=lambda x: x.laxity / x.d, reverse=True)  # Sort packs in descendant order of utilization

    for pack in packs:
        started_bins.sort(key=lambda x: x.c / x.d, reverse=False)  # Sort started bins in ascendant order of utilization

        assigned = False
        index_started_bins = 0
        while not assigned and index_started_bins < len(started_bins):
            actual_bin = started_bins[index_started_bins]
            c_actual_bin = actual_bin.c
            d_actual_bin = actual_bin.d
            possible_deadline = scipy.gcd(pack.d, d_actual_bin)
            c_actual = int(pack.laxity * (possible_deadline / pack.d))
            c_actual_bin_new_deadline = int(c_actual_bin * (d_actual_bin / pack.d))

            if c_actual <= (possible_deadline - c_actual_bin_new_deadline):
                assigned = True
                started_bins[index_started_bins].c = started_bins[index_started_bins].c + c_actual
                started_bins[index_started_bins].d = possible_deadline
                started_bins[index_started_bins].packs.append(pack)
            index_started_bins = index_started_bins + 1

        if not assigned:
            started_bins.append(PacksBin(pack.laxity, pack.d, [pack]))
    return [Pack(actual_bin.packs) for actual_bin in started_bins]


def create_recursive_tree(packs: List[Pack]) -> List[Pack]:
    tree_parents: List[Pack] = []
    tree_children: List[Pack] = []

    for pack in packs:
        if pack.laxity == 0:
            tree_parents.append(pack)
        else:
            tree_children.append(pack)

    if len(tree_children) > 0:
        tree_parents = tree_parents + create_recursive_tree(create_packs_from_virtual_tasks(tree_children))

    return tree_parents


def update_virtual_task_info(children: List[VirtualTask], actual_time: int):
    for i in children:
        if i.next_arrive <= actual_time:
            # We need update the task info
            i.pending_c = i.c
            i.next_arrive = i.next_arrive + i.d
            i.pending_laxity = i.laxity

        if isinstance(i, Pack):
            update_virtual_task_info(i.content, actual_time)


def create_tree(tasks: List[RUNTask]) -> List[Pack]:
    packs = create_packs_from_virtual_tasks(tasks)
    parents = create_recursive_tree(packs)
    return parents


def select_children_to_execute(parent: Pack, dt: int) -> List[RUNTask]:
    children_with_time_to_execute = [i for i in parent.content if i.pending_laxity > 0]
    if len(children_with_time_to_execute) == 0:
        return []

    children_with_time_to_execute.sort(key=lambda x: x.next_arrive,
                                       reverse=False)  # Sort packs in ascendant order of arrive

    children_with_time_to_execute[0].pending_laxity -= dt

    tasks_to_execute = []

    for i in children_with_time_to_execute[1:]:
        if isinstance(i, RUNTask):
            tasks_to_execute.append(i)
        elif isinstance(i, Pack):
            tasks_to_execute = tasks_to_execute + select_children_to_execute(i, dt)

    return tasks_to_execute


def select_tasks_to_execute(parents: List[Pack], actual_time: int, dt: int) -> List[RUNTask]:
    update_virtual_task_info(parents, actual_time)
    children_to_execute = []
    for parent in parents:
        children_to_execute = children_to_execute + select_children_to_execute(parent, dt)

    # TODO: Do assignation algorithm
    return children_to_execute


def run_algorithm(task_set: List[RUNTask]) -> List[List[int]]:
    # Run algorithm
    h = int(scipy.lcm.reduce([i.d for i in task_set]))
    parents_of_tree = create_tree(task_set)

    result_algorithm = []

    for i in range(h):
        iteration_result = select_tasks_to_execute(parents_of_tree, i, 1)
        result_algorithm.append([j.task_id for j in iteration_result])

    return result_algorithm


if __name__ == '__main__':
    set_of_tasks_1 = [
        RUNTask(1, 5, 7),
        RUNTask(2, 5, 7),
        RUNTask(3, 5, 7),
        RUNTask(4, 10, 14),
        RUNTask(5, 5, 14),
        RUNTask(6, 5, 14),
        RUNTask(7, 5, 7)
    ]
    idle_task_1 = RUNTask(-1, 10, 14)

    total_tasks_1 = set_of_tasks_1 + [idle_task_1]

    result = run_algorithm(total_tasks_1)

    pass
