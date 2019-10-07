from typing import List

import scipy


class RUNServer(object):
    def __init__(self, c: int, d: int):
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


class RUNPack(RUNServer):
    """
    This class represent the union of a DUAL and an EDF server
    """

    def __init__(self, content: List[RUNServer]):
        self.content = content
        d = int(scipy.gcd.reduce([i.d for i in content]))
        c = int(sum([i.laxity * (d / i.d) for i in content]))
        super().__init__(c, d)


class RUNTask(RUNServer):
    def __init__(self, task_id: int, c: int, d: int):
        self.task_id = task_id
        super().__init__(c, d)


class PacksBin(object):
    def __init__(self, c: int, d: int, packs: List[RUNServer]):
        self.c = c
        self.d = d
        self.packs = packs


def create_packs_from_virtual_tasks(packs: List[RUNServer]) -> List[RUNPack]:
    started_bins: List[PacksBin] = []

    packs.sort(key=lambda x: x.laxity / x.d, reverse=True)  # Sort packs in descendant order of utilization

    for pack in packs:
        started_bins.sort(key=lambda x: x.c / x.d, reverse=False)  # Sort started bins in ascendant order of utilization

        assigned = False
        index_started_bins = 0
        while not assigned and index_started_bins < len(started_bins):
            actual_bin = started_bins[index_started_bins]
            deadline = scipy.gcd(pack.d, actual_bin.d)
            actual_bin_c = int(actual_bin.c / (actual_bin.d / deadline))
            actual_pack_dual = int(pack.laxity / (pack.d / deadline))

            if actual_pack_dual <= (deadline - actual_bin_c):
                assigned = True
                started_bins[index_started_bins].c = actual_bin_c + actual_pack_dual
                started_bins[index_started_bins].d = deadline
                started_bins[index_started_bins].packs.append(pack)
            index_started_bins = index_started_bins + 1

        if not assigned:
            started_bins.append(PacksBin(pack.laxity, pack.d, [pack]))
    return [RUNPack(actual_bin.packs) for actual_bin in started_bins]


def create_recursive_tree(packs: List[RUNPack]) -> List[RUNPack]:
    tree_parents: List[RUNPack] = []
    tree_children: List[RUNPack] = []

    for pack in packs:
        if pack.laxity == 0:
            tree_parents.append(pack)
        else:
            tree_children.append(pack)

    if len(tree_children) > 0:
        tree_parents = tree_parents + create_recursive_tree(create_packs_from_virtual_tasks(tree_children))

    return tree_parents


def update_virtual_task_info(children: List[RUNServer], actual_time: int):
    for i in children:
        if i.next_arrive <= actual_time:
            # We need update the task info
            i.pending_c = i.c
            i.next_arrive = i.next_arrive + i.d
            i.pending_laxity = i.laxity

        if isinstance(i, RUNPack):
            update_virtual_task_info(i.content, actual_time)


def create_tree(tasks: List[RUNTask]) -> List[RUNPack]:
    packs = create_packs_from_virtual_tasks(tasks)
    parents = create_recursive_tree(packs)
    return parents


def count_tree_levels(parent: RUNPack) -> int:
    """
    Return the number of levels including the root
    :param parent:
    :return:
    """
    count = 0
    actual_parent = parent
    while not isinstance(actual_parent, RUNTask):
        actual_parent = actual_parent.content[0]
        count += 1
    return count


def edf_server_selection(previous_dual_selection: List[RUNPack]) -> List[RUNServer]:
    selection = []

    for server in previous_dual_selection:
        children_with_time_to_execute = [i for i in server.content if i.pending_laxity > 0]
        if len(children_with_time_to_execute) != 0:
            # Order the tasks by the EDF criteria
            children_with_time_to_execute.sort(key=lambda x: x.next_arrive,
                                               reverse=False)  # Sort packs in ascendant order of arrive
            selected_next_arrive = children_with_time_to_execute[0].next_arrive

            # If there are several tasks with the same priority, the last executed is selected to decrease
            # context changes
            children_with_highest_priority = [i for i in children_with_time_to_execute if
                                              i.next_arrive == selected_next_arrive]
            children_with_highest_priority.sort(key=lambda x: x.last_time_executed_edf,
                                                reverse=True)  # Sort packs in descendant order of last execution

            # Append to selection the highest priority task
            selection.append(children_with_highest_priority[0])

    return selection


def _select_servers_from_level(level: int, parent: RUNPack) -> List[RUNServer]:
    if level == 0:
        return [parent]
    else:
        to_return = []
        for i in parent.content:
            if isinstance(i, RUNPack):
                to_return = to_return + _select_servers_from_level(level - 1, i)
            else:
                to_return = to_return.append(i)

        return to_return


def dual_server_selection(level: int, parent: RUNPack, previous_edf_selection: List[RUNServer]) -> List[RUNServer]:
    servers_from_level = _select_servers_from_level(level, parent)

    previous_edf_selection_ids = [i.server_id for i in previous_edf_selection]

    servers_not_selected_in_edf = [i for i in servers_from_level if i.server_id not in previous_edf_selection_ids]

    servers_with_pending_c = [i for i in servers_not_selected_in_edf if i.pending_c >= 0]

    return servers_with_pending_c


def select_tasks_to_execute_one_parent(parent: RUNPack, actual_time: int, dt: int) -> List[RUNTask]:
    tree_levels = count_tree_levels(parent)
    dual_selection = [parent]
    for level in range(1, tree_levels):
        # Select servers by EDF
        edf_selection = edf_server_selection(dual_selection)

        # Decrease pending dual_c (laxity) of those servers selected by edf
        for server in edf_selection:
            server.pending_laxity -= dt
            server.last_time_executed_edf = actual_time

        # Select servers from the set of dual servers previously selected
        dual_selection = dual_server_selection(level, parent, edf_selection)

        # Decrease pending c of those servers selected
        for server in dual_selection:
            server.pending_c -= dt
            server.last_time_executed_dual = actual_time

    # In the leafs of the tree, we must have Tasks
    return [i for i in dual_selection if isinstance(i, RUNTask)]


def select_tasks_to_execute(parents: List[RUNPack], actual_time: int, dt: int) -> List[RUNTask]:
    update_virtual_task_info(parents, actual_time)
    tasks_to_execute = []
    for parent in parents:
        actual_tasks = select_tasks_to_execute_one_parent(parent, actual_time, dt)
        tasks_to_execute += actual_tasks
    return tasks_to_execute


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
    # Tasks set 1: Can't produce feasible scheduling
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

    # Tasks set 2:
    set_of_tasks_2 = [
        RUNTask(1, 5, 7),
        RUNTask(2, 5, 7),
        RUNTask(3, 5, 7),
        RUNTask(4, 10, 14),
        RUNTask(5, 10, 14),
        RUNTask(6, 10, 14),
        RUNTask(7, 5, 7)
    ]

    total_tasks_2 = set_of_tasks_2

    result = run_algorithm(total_tasks_2)

    pass
