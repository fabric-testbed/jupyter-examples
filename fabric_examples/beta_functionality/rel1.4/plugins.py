import logging
import time

import ipaddress
from ipaddress import IPv4Network


from fabric_cf.orchestrator.orchestrator_proxy import Status
from fabrictestbed.slice_editor import Labels, Flags, Capacities

from fabrictestbed_extensions.fablib.slice import Slice
from fabrictestbed_extensions.fablib.facility_port import FacilityPort
from fabrictestbed_extensions.fablib.network_service import NetworkService, ServiceType
from typing import List

from fabrictestbed_extensions.fablib.interface import Interface

class Plugins:
    @staticmethod
    def load():
        n = NetworkService
        n.change_public_ip = Plugins.change_public_ip
        n.new_l3network = Plugins.new_l3network
        n.new_network_service = Plugins.new_network_service
        s = Slice
        s.add_facility_port = Plugins.add_facility_port
        s.add_l3network = Plugins.add_l3network
        f = FacilityPort
        f.new_facility_port = Plugins.new_facility_port

        
    
    def change_public_ip(self, ipv6: list[str] = None, ipv4: list[str] = None):
        labels = self.fim_network_service.labels
        if labels is None:
            labels = Labels()
        if self.fim_network_service.type == ServiceType.FABNetv4Ext:
            labels = Labels.update(labels, ipv4=ipv4)
            
        elif self.fim_network_service.type == ServiceType.FABNetv6Ext:
            labels = Labels.update(labels, ipv6=ipv6)
        
        self.fim_network_service.set_properties(labels=labels)
    
    def add_facility_port(self, name: str = None, site: str = None, labels: Labels = None, peer_labels: Labels = None, capacities: Capacities = None) -> NetworkService:
        """
        Adds a new L2 facility port to this slice
        :return: a new L2 facility port
        :rtype: NetworkService
        """
        return FacilityPort.new_facility_port(slice=self, name=name, site=site, labels=labels, peer_labels=peer_labels, capacities=capacities)

    @staticmethod
    def new_facility_port(
        slice: Slice = None, name: str = None, site: str = None,
        labels: Labels = None, peer_labels: Labels = None, capacities: Capacities = None):
        
        if capacities is None:
            capacities = Capacities(bw=10)
        
        fim_facility_port = slice.get_fim_topology().add_facility(name=name, site=site, capacities=capacities, labels=labels, peer_labels=peer_labels)
        
        return FacilityPort(slice, fim_facility_port)
    
    def add_l3network(
        self, name: str = None, interfaces: List[Interface] = [], type: str = "IPv4",
        technology: str = None) -> NetworkService:
        return NetworkService.new_l3network(
            slice=self, name=name, interfaces=interfaces, type=type, technology=technology
        )
    
    @staticmethod
    def new_l3network(
        slice: Slice = None,
        name: str = None,
        interfaces: List[Interface] = [],
        type: str = None, technology: str = None
    ):
        """
        Not inteded for API use. See slice.add_l3network
        """
        if type == "IPv6":
            nstype = ServiceType.FABNetv6
        elif type == "IPv4":
            nstype = ServiceType.FABNetv4
        elif type == "IPv4Ext":
            nstype = ServiceType.FABNetv4Ext
        elif type == "IPv6Ext":
            nstype = ServiceType.FABNetv6Ext
        elif type == "L3VPN":
            nstype = ServiceType.L3VPN
        else:
            raise Exception(
                "Invalid L3 Network Type: Allowed values [IPv4, IPv4Ext, IPv6, IPv6Ext, L3VPN]"
            )

        # TODO: need a fabnet version of this
        # validate nstype and interface List
        # NetworkService.validate_nstype(nstype, interfaces)

        return NetworkService.new_network_service(
            slice=slice, name=name, nstype=nstype, interfaces=interfaces, technology=technology
        )
    
    @staticmethod
    def new_network_service(
        slice: Slice = None,
        name: str = None,
        nstype: ServiceType = None,
        interfaces: List[Interface] = [],technology: str = None
    ):
        """
        Not inteded for API use. See slice.add_l2network


        Creates a new FABRIC network service and returns the fablib instance.

        :param slice: the fabric slice to build the network service with
        :type slice: Slice
        :param name: the name of the new network service
        :type name: str
        :param nstype: the type of network service to create
        :type nstype: ServiceType
        :param interfaces: a list of interfaces to
        :return: the new fablib network service
        :rtype: NetworkService
        """
        fim_interfaces = []
        for interface in interfaces:
            fim_interfaces.append(interface.get_fim_interface())

        logging.info(
            f"Create Network Service: Slice: {slice.get_name()}, Network Name: {name}, Type: {nstype}"
        )
        fim_network_service = slice.topology.add_network_service(
            name=name, nstype=nstype, interfaces=fim_interfaces, technology=technology
        )

        return NetworkService(slice=slice, fim_network_service=fim_network_service)    