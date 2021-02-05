from tertimuss.simulation_lib.system_definition import PeriodicTask, PreemptiveExecution, Criticality

periodic_implicit_deadline_tasks = [(790, 10.0), (620, 10.0), (339, 3.0), (150, 10.0), (1200, 30.0), (828, 12.0),
                                    (72, 4.0), (410, 10.0), (490, 5.0), (3360, 30.0), (105, 15.0), (330, 10.0),
                                    (80, 2.0), (1220, 10.0), (194, 2.0), (840, 30.0), (420, 60.0), (60, 6.0),
                                    (354, 3.0), (130, 5.0), (330, 30.0), (12, 4.0), (2220, 20.0), (600, 30.0),
                                    (204, 12.0), (6240, 60.0), (2340, 60.0), (20, 20.0), (137, 1.0), (80, 5.0),
                                    (48, 4.0), (510, 5.0), (312, 12.0), (140, 20.0), (292, 4.0), (178, 2.0), (14, 2.0),
                                    (4320, 60.0), (50, 1.0), (528, 6.0), (570, 6.0), (208, 4.0), (780, 60.0),
                                    (504, 12.0), (7260, 60.0), (700, 4.0), (15, 5.0), (3, 1.0), (1000, 20.0), (20, 2.0),
                                    (66, 1.0), (68, 2.0), (20, 2.0), (20, 20.0), (45, 3.0), (660, 10.0), (10, 1.0),
                                    (134, 2.0), (28, 4.0), (92, 1.0), (77, 1.0), (370, 10.0), (175, 5.0), (1, 1.0),
                                    (140, 20.0), (1260, 60.0), (240, 60.0), (55, 5.0), (780, 20.0), (1500, 12.0),
                                    (780, 60.0), (2880, 60.0), (348, 6.0), (2260, 20.0), (56, 2.0), (630, 30.0),
                                    (192, 2.0), (48, 2.0), (83, 1.0), (6420, 60.0)]


def create_implicit_deadline_periodic_task_h_rt(task_id: int, worst_case_execution_time: int,
                                                period: float) -> PeriodicTask:
    # Create implicit deadline task with priority equal to identification id
    return PeriodicTask(identifier=task_id,
                        worst_case_execution_time=worst_case_execution_time,
                        relative_deadline=period,
                        best_case_execution_time=None,
                        execution_time_distribution=None,
                        memory_footprint=None,
                        priority=None,
                        preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                        deadline_criteria=Criticality.HARD,
                        energy_consumption=None,
                        phase=None,
                        period=period)
