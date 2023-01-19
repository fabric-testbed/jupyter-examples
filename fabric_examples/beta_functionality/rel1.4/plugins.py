import logging
import time

from fabric_cf.orchestrator.orchestrator_proxy import Status
from fabrictestbed.slice_editor import Labels, Flags

from fabrictestbed_extensions.fablib.network_service import NetworkService, ServiceType


class Plugins:
    @staticmethod
    def load():
        n = NetworkService
    
    def update(self, ip_list: list):   
        labels = self.fim_network_service.labels
        if labels is None:
            labels = Labels()
        if self.fim_network_service.type == ServiceType.FABNetv4Ext:
            labels = Labels.update(labels, ipv4=ip_list)
            
        elif self.fim_network_service.type == ServiceType.FABNetv6Ext:
            labels = Labels.update(labels, ipv6=ip_list)
        
        self.fim_network_service.set_properties(labels=labels)
        