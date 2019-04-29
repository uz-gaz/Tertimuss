from core.problem_specification_models.TasksSpecification import TasksSpecification, Task

te: TasksSpecification = TasksSpecification([Task(1, 5, 1), Task(1, 10, 1), Task(1, 20, 1)])

print(te.h)
