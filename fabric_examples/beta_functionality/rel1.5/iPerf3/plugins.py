import logging
import time

from fabric_cf.orchestrator.orchestrator_proxy import Status
from fabrictestbed_extensions.fablib.node import Node

from typing import List, Dict, Union


class Plugins:
    @staticmethod
    def load():
        n = Node
        n.perform_operational_action = Plugins.perform_operational_action

    def perform_operational_action(self, operation: str, vcpu_cpu_map: List[Dict[str, str]] = None,
                                   node_set: List[str] = None) -> Union[Dict, str]:

        status, poa_info = self.get_fablib_manager().get_slice_manager().poa(sliver_id=self.get_reservation_id(), 
                                                                             operation=operation, vcpu_cpu_map=vcpu_cpu_map,
                                                                             node_set=node_set)
        
        if status != Status.OK:
            raise Exception(f"Failed to issue POA - {operation} Error {poa_info}")
            
        print(f"POA {poa_info[0].poa_id}/{operation} submitted for {self.get_reservation_id()}/{self.get_name()}")

        poa_state = "Nascent"
        poa_info_status = None
        attempt = 0
        while poa_state != "Success" and poa_state != "Failed":
            status, poa_info_status = self.get_fablib_manager().get_slice_manager().get_poas(poa_id=poa_info[0].poa_id)
            attempt += 1
            if status != Status.OK:
                raise Exception(f"Failed to get POA Status - {poa_info[0].poa_id}/{operation} Error {poa_info_status}")
            poa_state = poa_info_status[0].state
            print(f"Waiting for POA {poa_info[0].poa_id}/{operation} to complete: attempt: {attempt} current state: {poa_state}")
            time.sleep(10)

        if poa_info_status[0].state == "Failed":
            raise Exception(f"POA - {poa_info[0].poa_id}/{operation} failed with error: - {poa_info_status[0].error}")

        if poa_info_status[0].info.get(operation) is not None:
            return poa_info_status[0].info.get(operation)
        else:
            return poa_info_status[0].state
