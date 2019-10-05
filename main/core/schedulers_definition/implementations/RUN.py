from typing import List

import scipy


class VirtualTask(object):
    def __init__(self, c: int, d: int):
        self.c = c
        self.d = d
        self.dual = d - c


class Pack(VirtualTask):
    def __init__(self, content: List[VirtualTask]):
        self.content = content
        d = int(scipy.lcm.reduce([i.d for i in content]))
        c = int(sum([i.c * (d / i.d) for i in content]))
        super().__init__(c, d)


class RUNTask(VirtualTask):
    def __init__(self, task_id: int, c: int, d: int):
        self.task_id = task_id
        super().__init__(c, d)


def create_packs_from_virtual_tasks(packs: List[VirtualTask]) -> List[Pack]:
    packs_mcd = 14  # TODO
    pass


def create_recursive_tree(packs: List[Pack]) -> List[Pack]:
    tree_parents: List[Pack] = []
    tree_children: List[Pack] = []

    for pack in packs:
        if pack.dual == 0:
            tree_parents.append(pack)
        else:
            tree_children.append(pack)

    if len(tree_children):
        tree_parents = tree_parents + create_recursive_tree(tree_parents)

    return tree_parents


def create_tree(tasks: List[RUNTask]) -> List[Pack]:
    packs = create_packs_from_tasks(tasks)
    parents = create_recursive_tree(packs)
    return parents


if __name__ == '__main__':
    set_of_tasks = [
        RUNTask(1, 5, 7),
        RUNTask(2, 5, 7),
        RUNTask(3, 5, 7),
        RUNTask(4, 10, 14),
        RUNTask(5, 5, 14),
        RUNTask(6, 5, 14),
        RUNTask(7, 5, 7)
    ]
    idle_task = RUNTask(-1, 10, 14)
    parents_of_tree = create_tree(set_of_tasks + [idle_task])
