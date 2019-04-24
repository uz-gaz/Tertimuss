from typing import Optional

from core.schedulers.abstract_scheduler import AbstractScheduler
from core.schedulers.global_edf_affinity_scheduler import GlobalEDFAffinityScheduler
from core.schedulers.global_edf_scheduler import GlobalEDFScheduler
from core.schedulers.rt_tcpn_scheduler import RtTCPNScheduler
from core.schedulers.rt_tcpn_thermal_aware_scheduler import RTTcpnThermalAwareScheduler


def select_scheduler(name: str) -> Optional[AbstractScheduler]:
    """
    Select scheduler by name
    :param name: Name of the scheduler
    :return:
    """
    schedulers_definition = {
        "global_edf_scheduler": GlobalEDFScheduler(),
        "global_edf_affinity_scheduler": GlobalEDFAffinityScheduler(),
        "rt_tcpn_scheduler": RtTCPNScheduler(),
        "rt_tcpn_thermal_aware_scheduler": RTTcpnThermalAwareScheduler()
    }
    return schedulers_definition.get(name)
