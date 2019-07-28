from typing import List

from main.core.schedulers.implementations.G_EDF_AFA import GlobalEDFAffinityFrequencyAwareScheduler
from main.core.schedulers.implementations.G_LLF_AFA import GlobalLeastLaxityFirstAFAScheduler
from main.core.schedulers.implementations.JDEDS import GlobalJDEDSScheduler
from main.core.schedulers.implementations.OLDTFS import GlobalThermalAwareScheduler
from main.core.schedulers.templates.abstract_scheduler.AbstractScheduler import AbstractScheduler
from main.core.schedulers.implementations.G_EDF_A import GlobalEDFAffinityScheduler
from main.core.schedulers.implementations.G_EDF import GlobalEDFScheduler


class SchedulerSelector(object):
    @staticmethod
    def select_scheduler(name: str) -> AbstractScheduler:
        """
        Select scheduler by name
        :param name: Name of the scheduler
        :return:
        """
        schedulers_definition = {
            "G-EDF": GlobalEDFScheduler(),
            "G-EDF-A": GlobalEDFAffinityScheduler(),
            "G-EDF-AFA": GlobalEDFAffinityFrequencyAwareScheduler(),
            "G-LLF-AFA": GlobalLeastLaxityFirstAFAScheduler(),
            "JDEDS": GlobalJDEDSScheduler(),
            "OLDTFS": GlobalThermalAwareScheduler()
        }
        return schedulers_definition.get(name)

    @staticmethod
    def get_scheduler_names() -> List[str]:
        return ["G-EDF", "G-EDF-A", "G-EDF-AFA", "G-LLF-AFA", "JDEDS", "OLDTFS"]
