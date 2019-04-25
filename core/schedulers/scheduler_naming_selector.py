from typing import Optional

from core.schedulers.abstract_scheduler import AbstractScheduler
from core.schedulers.global_edf_affinity_scheduler import GlobalEDFAffinityScheduler
from core.schedulers.global_edf_scheduler import GlobalEDFScheduler
from core.schedulers.rt_tcpn_scheduler import RtTCPNScheduler
from core.schedulers.rt_tcpn_thermal_aware_scheduler import RTTcpnThermalAwareScheduler


def select_scheduler(name: str, with_thermal: bool) -> Optional[AbstractScheduler]:
    """
    Select scheduler by name
    :param name: Name of the scheduler
    :param with_thermal: True if is thermal definition included
    :return:
    """
    schedulers_definition_thermal = {
        "global_edf_scheduler": GlobalEDFScheduler(),
        "global_edf_affinity_scheduler": GlobalEDFAffinityScheduler(),
        "rt_tcpn_scheduler": RtTCPNScheduler(),
        "rt_tcpn_thermal_aware_scheduler": RTTcpnThermalAwareScheduler()
    }

    schedulers_definition_no_thermal = {
        "global_edf_scheduler": GlobalEDFScheduler(),
        "global_edf_affinity_scheduler": GlobalEDFAffinityScheduler(),
        "rt_tcpn_scheduler": RtTCPNScheduler()
    }

    return schedulers_definition_thermal.get(name) if with_thermal else schedulers_definition_no_thermal.get(name)
