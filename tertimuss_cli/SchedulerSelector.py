from typing import List

from main.core.schedulers_definition.implementations.G_EDF_AFA import GlobalEDFAffinityFrequencyAwareScheduler
from main.core.schedulers_definition.implementations.G_LLF_AFA import GlobalLeastLaxityFirstAFAScheduler
from main.core.schedulers_definition.implementations.AIECS import AIECSScheduler
from main.core.schedulers_definition.implementations.OLDTFS import OLDTFSScheduler
from main.core.schedulers_definition.implementations.RUN import RUNScheduler
from main.core.schedulers_definition.templates import AbstractScheduler
from main.core.schedulers_definition.implementations.G_EDF_A import GlobalEDFAffinityScheduler
from main.core.schedulers_definition.implementations.G_EDF import GlobalEDFScheduler


class SchedulerSelector(object):
    @staticmethod
    def select_scheduler(name: str) -> AbstractScheduler:
        """
        Select scheduler by name
        :param name: Name of the scheduler
        :return:
        """
        # TODO: Substitute with AbstractScheduler.__subclasses__
        schedulers_definition = {
            "G-EDF": GlobalEDFScheduler(),
            "G-EDF-A": GlobalEDFAffinityScheduler(),
            "G-EDF-AFA": GlobalEDFAffinityFrequencyAwareScheduler(),
            "G-LLF-AFA": GlobalLeastLaxityFirstAFAScheduler(),
            "JDEDS": AIECSScheduler(),
            "OLDTFS": OLDTFSScheduler(),
            "RUN": RUNScheduler()
        }
        return schedulers_definition.get(name)

    @staticmethod
    def get_scheduler_names() -> List[str]:
        # TODO: Substitute with AbstractScheduler.__subclasses__
        return ["G-EDF", "G-EDF-A", "G-EDF-AFA", "G-LLF-AFA", "JDEDS", "OLDTFS", "RUN"]
