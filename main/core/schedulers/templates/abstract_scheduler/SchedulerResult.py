import scipy


class SchedulerResult(object):
    def __init__(self, temperature_map: scipy.ndarray, max_temperature_cores: scipy.ndarray,
                 time_steps: scipy.ndarray,
                 execution_time_scheduler: scipy.ndarray,
                 scheduler_assignation: scipy.ndarray,
                 frequencies: scipy.ndarray,
                 energy_consumption: scipy.ndarray,
                 quantum: float):
        self.time_steps = time_steps
        self.temperature_map = temperature_map
        self.max_temperature_cores = max_temperature_cores
        self.execution_time_scheduler = execution_time_scheduler
        self.frequencies = frequencies
        self.energy_consumption = energy_consumption

        self.scheduler_assignation = scheduler_assignation
        self.quantum = quantum

        # This was used only for debug purposes
        # self.execution_time_tcpn = execution_time_tcpn