import scipy.io

from core.schedulers.templates.abstract_scheduler import SchedulerResult


def load_scheduler_result(path: str) -> SchedulerResult:
    matlab_file = scipy.io.loadmat(path + ".mat")
    time_steps = matlab_file["time_steps"][0]
    temperature_map = matlab_file["temperature_map"]
    max_temperature_cores = matlab_file["max_temperature_cores"]
    execution_time_scheduler = matlab_file["execution_time_scheduler"]
    frequencies = matlab_file["frequencies"]
    energy_consumption = matlab_file["energy_consumption"]
    scheduler_assignation = matlab_file["scheduler_assignation"]
    quantum = matlab_file["time_steps"][0][0]
    return SchedulerResult(temperature_map, max_temperature_cores, time_steps, execution_time_scheduler,
                           scheduler_assignation, frequencies, energy_consumption,
                           quantum)


def save_scheduler_result(scheduler_simulation: SchedulerResult, path: str):
    scipy.io.savemat(path + ".mat", {
        'time_steps': scheduler_simulation.time_steps,
        'temperature_map': scheduler_simulation.temperature_map,
        'max_temperature_cores': scheduler_simulation.max_temperature_cores,
        'execution_time_scheduler': scheduler_simulation.execution_time_scheduler,
        'frequencies': scheduler_simulation.frequencies,
        'energy_consumption': scheduler_simulation.energy_consumption,
        'scheduler_assignation': scheduler_simulation.scheduler_assignation,
        'quantum': scheduler_simulation.quantum
    })
