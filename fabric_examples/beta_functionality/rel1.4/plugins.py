import logging
import time

from fabric_cf.orchestrator.orchestrator_proxy import Status
from fabrictestbed.slice_editor import Labels, Flags

from fabrictestbed_extensions.fablib.network_service import NetworkService, ServiceType


class Plugins:
    @staticmethod
    def load():
        n = NetworkService
        n.change_public_ip = Plugins.change_public_ip
    
    def change_public_ip(self, ipv6: list[str] = None, ipv4: list[str] = None):
        labels = self.fim_network_service.labels
        if labels is None:
            labels = Labels()
        if self.fim_network_service.type == ServiceType.FABNetv4Ext:
            labels = Labels.update(labels, ipv4=ipv4)
            
        elif self.fim_network_service.type == ServiceType.FABNetv6Ext:
            labels = Labels.update(labels, ipv6=ipv6)
        
        self.fim_network_service.set_properties(labels=labels)
