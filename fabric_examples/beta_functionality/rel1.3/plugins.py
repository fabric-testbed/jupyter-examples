import logging
import time

from fabric_cf.orchestrator.orchestrator_proxy import Status
from fabrictestbed.slice_editor import Labels, Flags

from fabrictestbed_extensions.fablib.slice import Slice
from fabrictestbed_extensions.fablib.node import Node
from fabrictestbed_extensions.fablib.component import Component


class Plugins:
    @staticmethod
    def load():

        s = Slice
        s.modify = Plugins.modify
        s.modify_accept = Plugins.modify_accept
        setattr(s, 'isStable', Plugins.isStable)
        setattr(s, 'wait', Plugins.wait)

        n = Node
        n.get_storage = Plugins.get_storage
        n.add_storage = Plugins.add_storage

        c = Component
        c.get_device_name = Plugins.get_device_name
        c.new_storage = Plugins.new_storage

    def isStable(self) -> bool:
        """
        Tests is the slice is stable. Stable means all requests for
        to add/remove/modify slice resources have completed.  Both successful
        and failed slice requests are considered to be completed.

        :return: True if slice is stable, False otherwise
        :rtype: Bool
        """
        if self.get_state() in ["StableOK",
                                "StableError",
                                "ModifyOK",
                                "ModifyError",
                                "Closing",
                                "Dead"]:
            return True
        else:
            return False

    def modify(self, wait: int = True, wait_timeout: int = 600, wait_interval: int = 10, progress: bool = True,
               wait_jupyter: str = "text"):
        """
        Submits a modify slice request to FABRIC.

        Can be blocking or non-blocking.

        Blocking calls can, optionally,configure timeouts and intervals.

        Blocking calls can, optionally, print progress info.


        :param wait: indicator for whether to wait for the slice's resources to be active
        :param wait_timeout: how many seconds to wait on the slice resources
        :param wait_interval: how often to check on the slice resources
        :param progress: indicator for whether to show progress while waiting
        :param wait_jupyter: Special wait for jupyter notebooks.
        """

        if not wait:
            progress = False

        # Generate Slice Graph
        slice_graph = self.get_fim_topology().serialize()

        # Request slice from Orchestrator
        return_status, slice_reservations = self.fablib_manager.get_slice_manager().modify(slice_id=self.slice_id,
                                                                                           slice_graph=slice_graph)
        if return_status != Status.OK:
            raise Exception("Failed to submit modify slice: {}, {}".format(return_status, slice_reservations))

        logging.debug(f'slice_reservations: {slice_reservations}')
        logging.debug(f"slice_id: {slice_reservations[0].slice_id}")
        self.slice_id = slice_reservations[0].slice_id

        time.sleep(1)
        self.update()

        if progress and wait_jupyter == 'text' and self.fablib_manager.is_jupyter_notebook():
            self.wait_jupyter(timeout=wait_timeout, interval=wait_interval)
            return self.slice_id

        if wait:
            self.wait_ssh(timeout=wait_timeout, interval=wait_interval, progress=progress)

            if progress:
                print("Running post boot config ... ",end="")

            self.update()
            self.post_boot_config()

        if progress:
            print("Done!")

    def modify_accept(self):
        """
        Submits a accept to accept the last modify slice request to FABRIC.
        """
        # Request slice from Orchestrator
        return_status, topology = self.fablib_manager.get_slice_manager().modify_accept(slice_id=self.slice_id)
        if return_status != Status.OK:
            raise Exception("Failed to accept the last modify slice: {}, {}".format(return_status, topology))
        else:
            self.topology = topology

        logging.debug(f'modified topology: {topology}')

        self.update_slice()

    def get_storage(self, name: str) -> Component:
        """
        Gets a particular storage associated with this node.
        :param name: the name of the storage
        :type name: String
        :raise Exception: if storage not found by name
        :return: the storage on the FABRIC node
        :rtype: Component
        """
        try:
            return Component(self, self.get_fim_node().components[name])
        except Exception as e:
            logging.error(e, exc_info=True)
            raise Exception(f"Storage not found: {name}")

    def add_storage(self, name: str, auto_mount: bool = False) -> Component:
        """
        Creates a new FABRIC Storage component and attaches it to the Node
        :param name: Name of the Storage volume created for the project outside the scope of the Slice
        :param auto_mount: Mount the storage volume
        :rtype: Component
        """
        return Component.new_storage(node=self, name=name, auto_mount=auto_mount)

    def get_device_name(self) -> str:
        """
        Not for API use
        """
        labels = self.get_fim_component().get_property(pname="label_allocations")
        return labels.device_name

    @staticmethod
    def new_storage(node: Node, name: str, auto_mount: bool = False):
        """
        Not intended for API use

        Creates a new FIM component on the fablib node inputted.

        :param node: the fablib node to build the component on
        :param name: the name of the new component
        :param auto_mount: True - mount the storage; False - do not mount
        :return: the new fablib compoent
        :rtype: Component
        """
        # Hack to make it possile to find interfaces

        fim_component = node.fim_node.add_storage(name=name, labels=Labels(local_name=name),
                                                  flags=Flags(auto_mount=auto_mount))
        return Component(node=node, fim_component=fim_component)

    def wait(self, timeout: int = 360, interval: int = 10, progress: bool = False):
        """
        Waits for the slice on the slice manager to be in a stable, running state.

        :param timeout: how many seconds to wait on the slice
        :type timeout: int
        :param interval: how often in seconds to check on slice state
        :type interval: int
        :param progress: indicator for whether to print wait progress
        :type progress: bool
        :raises Exception: if the slice state is undesirable, or waiting times out
        :return: the stable slice on the slice manager
        :rtype: SMSlice
        """
        slice_id = self.sm_slice.slice_id

        timeout_start = time.time()
        slice = self.sm_slice

        if progress:
            print("Waiting for slice .", end='')
        while time.time() < timeout_start + timeout:
            return_status, slices = self.fablib_manager.get_slice_manager().slices(excludes=[], slice_id=self.slice_id,
                                                                                   name=self.slice_name)
            if return_status == Status.OK:
                slice = list(filter(lambda x: x.slice_id == slice_id, slices))[0]
                if slice.state == "StableOK" or slice.state == "ModifyOK":
                    if progress:
                        print(" Slice state: {}".format(slice.state))
                    return slice
                if slice.state == "Closing" or slice.state == "Dead" or slice.state == "StableError" or \
                        slice.state == "ModifyError":
                    if progress:
                        print(" Slice state: {}".format(slice.state))
                    try:
                        exception_string = self.build_error_exception_string()
                    except Exception as e:
                        exception_string = "Exception while getting error messages"

                    raise Exception(str(exception_string))
            else:
                print(f"Failure: {slices}")

            if progress:
                print(".", end='')
            time.sleep(interval)

        if time.time() >= timeout_start + timeout:
            raise Exception(" Timeout exceeded ({} sec). Slice: {} ({})".format(timeout, slice.name, slice.state))

        # Update the fim topology (wait to avoid get topology bug)
        # time.sleep(interval)
        self.update()