# MIT License
#
# Copyright (c) 2022 FABRIC Testbed
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import json
from mflib import mflib
import os
import sys
import time
import requests
from fabrictestbed_extensions.fablib.fablib import fablib
from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class mf_data_export():
    
    def __init__(self, slice_name, meas_node_name):
        """
        Constructor. Builds Manager for mf_data_export object.
        """
        super().__init__()
        self.slice_name=slice_name
        try:
            self.slice = fablib.get_slice(name=self.slice_name)
        except Exception as e:
            print(f"Fail: {e}")
        try:
            self.measnode = self.slice.get_node(name=meas_node_name)
        except Exception as e:
            print(f"Fail: {e}")
            
            
    ##### functions that generate snapshots on meas node #####
    
    # prometheus
    def create_prometheus_snapshot(self, ht_user, ht_password):
        # uses rest api to generate prometheus snapshot
        # snapshot dir will be available at /opt/data/fabric_prometheus/prometheus/snapshots
        
        """
        generates backup data file (prometheus:snapshot)on the node
        Args:
            ht_user(str): ht user name
            ht_password(str): ht password
        """
        prometheus_snapshot_url = "https://localhost:9090/api/v1/admin/tsdb/snapshot?skip_head=false"
        cmd = f"sudo curl -k -u {ht_user}:{ht_password} -XPOST {prometheus_snapshot_url}"
        stdout, stderr= self.measnode.execute(cmd)
    
    
    # elk 
    
    # Step1: Change the directory permission on host that mounts elk container
    def change_elk_dir_permission(self, node, directory=None):
        """
        changes directory(binds dir in es container)permission so that elk can write snapshot to it
        Args:
            node(str): fabric node name
            directory(optional, str): directory on host that binds the dir in the docker compose file 
        """
        default_dir = "/var/lib/docker/volumes/elk_snapshotbackup/_data"
        if directory:
            cmd = f"sudo chown -R 1000:1000 {directory}"
        else:
            cmd = f"sudo chown -R 1000:1000 {default_dir}"
        try:
            node = self.slice.get_node(name=node)
        except Exception as e:
            print(f"Fail: {e}")
        stdout, stderr= node.execute(cmd)
    
    
    # Step2: create a snapshot repo    
    def create_snapshot_repo(self, repo_name):
        """
        registers a snapshot repo using elk rest api
        Args:
            repo_name(str): name of the repo to be created 
        """
        default_dir = "/usr/share/elasticsearch/backup"
        cmd = f'curl -X PUT "http://localhost:9200/_snapshot/{repo_name}?pretty" -H "Content-Type: application/json" -d \'{{ "type": "fs", "settings": {{ "location": "{default_dir}" }} }}\''
        stdout, stderr= self.measnode.execute(cmd)
        
        
    # Step3: verify the repo has been created
    def verify_repo(self, repo_name):
        """
        verify snapshot repo is created using elk rest api
        Args:
            repo_name(str): name of the repo to be created 
        """
        cmd = f'curl -X GET "http://localhost:9200/_snapshot/{repo_name}?pretty"'
        stdout, stderr= self.measnode.execute(cmd)
        
        
    # optional: list available indices
    def list_indices(self):
        """
        show existing elk indice using elk rest api
        
        """
        cmd = f'curl "http://localhost:9200/_cat/indices?v"'
        stdout, stderr= self.measnode.execute(cmd)
        
        
    #Step4: create a snapshot in the repo
    def create_elk_snapshot(self, repo_name, snapshot_name, indice=None):
        # indice default to None which includes all indices
        # snapshot will be available at /var/lib/docker/volumes/elk_snapshotbackup/_data
        
        """
        creates a snapshot repo using elk rest api
        Args:
            repo_name(str): name of the repo to be created 
            snapshot_name(str): name of the snapshot to be created
            indice(optional, list): list of indices to use
        """
        
        json_str = '"ignore_unavailable": true, "include_global_state": false'
        if indice:
            indice_str=",".join(indice)
            indice_str_final = f'"indices": "{indice_str}",'
            json_str_new = f'{indice_str_final} {json_str}'
            json_str_final = f"{{{json_str_new}}}"
        else:
            json_str_final = f"{{{json_str}}}"
        cmd = f'curl -X PUT "http://localhost:9200/_snapshot/{repo_name}/{snapshot_name}?wait_for_completion=true&pretty" -H "Content-Type: application/json" -d \'{json_str_final}\''
        stdout, stderr= self.measnode.execute(cmd)
        
        
    # Step5: verify the snapshot has been created in the repo
    def verify_snapshot(self, repo_name):
        """
        verify snapshot is created using elk rest api
        prints all snapshots in that repository
        Args:
            repo_name(str): name of the repo to be created 
        """
        cmd = f'curl -X GET "http://localhost:9200/_cat/snapshots/{repo_name}?v"'
        stdout, stderr= self.measnode.execute(cmd)
        
    # optional: 
    def delete_snapshot(self, repo_name, snapshot_name):
        """
        deletes a snapshot repo using elk rest api
        Args:
            repo_name(str): name of the repo to be created 
            snapshot_name(str): name of the snapshot to be created
        """
        cmd= f'curl -X DELETE "http://localhost:9200/_snapshot/{repo_name}/{snapshot_name}?pretty"'
        stdout, stderr= self.measnode.execute(cmd)
        
    # optional: 
    def delete_repo(self, repo_name):
        """
        deletes a repo using elk rest api
        Args:
            repo_name(str): name of the repo to be created 
        """
        cmd= f'curl -X DELETE "http://localhost:9200/_snapshot/{repo_name}?pretty"'
        stdout, stderr= self.measnode.execute(cmd)
        
    # optional: 
    def get_snapshot(self, repo_name, snapshot_name):
        """
        gets snapshot info in a repo using elk rest api
        Args:
            repo_name(str): name of the repo to be created 
            snapshot_name(str): name of the snapshot to be created
        """
        cmd= f'curl -X GET "http://localhost:9200/_snapshot/{repo_name}/{snapshot_name}?pretty"'
        stdout, stderr= self.measnode.execute(cmd)
        
    
        
    ##### tar the snapshots #####
    def create_dir_for_prometheus_tar(self, dir_name):
        """
        creates snapshot dir 
        Args: 
            dir_name(str): name of the dir for the tar file to be created
        """
        cmd = f'sudo mkdir -p {dir_name}'
        stdout, stderr= self.measnode.execute(cmd)

    
    def create_dir_for_elk_tar(self, dir_name):
        """
        creates snapshot dir 
        Args: 
            dir_name(str): name of the dir for the tar file to be created
        """
        cmd = f'sudo mkdir -p {dir_name}'
        stdout, stderr= self.measnode.execute(cmd)
        
    
    def tar_prometheus_snapshot(self, dir_name, snapshot_name):
        """
        tars the snapshot dir 
        Args: 
            dir_name(str): name of the dir for the tar file to be created
            snapshot_name(str): name of the tar file to be created
        """
        path = '/opt/data/fabric_prometheus/prometheus/snapshots'
        cmd = f'sudo tar -C {path} -cvf {dir_name}/{snapshot_name}.tar {snapshot_name}'
        stdout, stderr= self.measnode.execute(cmd)
        
    def tar_elk_snapshot(self, dir_name, file_name):
        """
        tars the snapshot dir 
        
        """
        # all the data is inside /var/lib/docker/volumes/elk_snapshotbackup/_data 
        # no way to select snapshot based on name since all the snapshot data will be in this dir
        path = '/var/lib/docker/volumes/elk_snapshotbackup/'
        cmd = f'sudo tar -C {path} -cvf {dir_name}/{file_name}.tar _data'
        stdout, stderr= self.measnode.execute(cmd)
        
    ##### download the snapshot tar file from meas node #####
    def download_tar_file(self, file_src, file_dst):
        """
        downloads the snapshot tar file to JH 
        
        """
        self.measnode.download_file(local_file_path=file_src, remote_file_path=file_dst)


class mf_data_import():
    
    def __init__(self, slice_name):
        """
        Constructor. Builds Manager for mf_data_import object.
        """
        super().__init__()
        self.slice_name=slice_name
        try:
            self.slice = fablib.get_slice(name=self.slice_name)
        except Exception as e:
            print(f"Fail: {e}")
            
    ################################################################
    ## For Import ## 
    ## This assumes that user want to restore the snapshot in a node in another fabric slice ##
    
    ##### untar the snapshots #####
    def untar_snapshots(self, node, tar_file_name):
        '''
        untars the snapshot file
        Args:
            node(fablib.node): fabric node
            tar_file_name(str): name of file to untar
        '''
        try:
            node = self.slice.get_node(name=node)
        except Exception as e:
            print(f"Fail: {e}")
        cmd = f'sudo tar -xvf {tar_file_name}'
        stdout, stderr= node.execute(cmd)
        
    def upload_docker_compose_file(self, node, file_src, file_dst):
        try:
            node = self.slice.get_node(name=node)
        except Exception as e:
            print(f"Fail: {e}")
        node.upload_file(local_file_path=file_src, remote_file_path=file_dst)
        
        
    def start_prometheus(self, node, docker_compose_file_path, args):
        return


class mf_data_transfer_docker():
    
    ## functions that run in container ###
    ######################################
    def __init__(self, slice_name, container_name, meas_node_name):
        """
        Constructor. Builds Manager for mf_data_export object.
        """
        super().__init__()
        self.slice_name=slice_name
        self.container_name=container_name
        try:
            self.slice = fablib.get_slice(name=self.slice_name)
        except Exception as e:
            print(f"Fail: {e}")
        try:
            self.measnode = self.slice.get_node(name=meas_node_name)
        except Exception as e:
            print(f"Fail: {e}")
    
    def create_remote_dir_using_rclone(self, node, storage, remote_dir, verbose= False):
        """
        creates remote dir on the storage
        Args:
            node(fablib.node): fabric node on which the timestamp docker container is running 
            storage(str): storage name configured in rclone
            remote_dir(str): directory name to be create in the storage
        """
        try:
            node = self.slice.get_node(name=node)
        except Exception as e:
            print(f"Fail: {e}")
        base_cmd = f"sudo docker exec -i {self.container_name} python3 /root/services/data_transfer/service_files/data_transfer_tool.py process_remote_dir create"
        storage_cmd = f"-s {storage}"
        remote_dir_cmd = f"-d {remote_dir}"
        cmd= f"{base_cmd} {storage_cmd} {remote_dir_cmd} "
        if verbose is True:
            verbose_cmd = f"-v" 
            cmd = f"{cmd} {verbose_cmd}"
        print (f"The docker command is: {cmd}")
        stdout, stderr= node.execute(cmd)
        
    def delete_remote_dir_using_rclone(self, node, storage, remote_dir, verbose= False):
        """
        deletes remote dir on the storage
        Args:
            node(fablib.node): fabric node on which the timestamp docker container is running 
            storage(str): storage name configured in rclone
            remote_dir(str): directory name to be create in the storage
        """
        try:
            node = self.slice.get_node(name=node)
        except Exception as e:
            print(f"Fail: {e}")
        base_cmd = f"sudo docker exec -i {self.container_name} python3 /root/services/data_transfer/service_files/data_transfer_tool.py process_remote_dir delete"
        storage_cmd = f"-s {storage}"
        remote_dir_cmd = f"-d {remote_dir}"
        cmd= f"{base_cmd} {storage_cmd} {remote_dir_cmd} "
        if verbose is True:
            verbose_cmd = f"-v" 
            cmd = f"{cmd} {verbose_cmd}"
        print (f"The docker command is: {cmd}")
        stdout, stderr= node.execute(cmd)

            
    def generate_backup(self, node, data_type, user_name, password, verbose=False):
        """
        generates backup data file (prometheus:snapshot, elk: snapshot)on the node
        Args:
            node(fablib.node): fabric node on which the timestamp docker container is running
            data_type(str): name of data type(prometheus or elk)
            user_name(str): ht user name
            password(str): ht password
        """
        try:
            node = self.slice.get_node(name=node)
        except Exception as e:
            print(f"Fail: {e}")
        base_cmd = f"sudo docker exec -i {self.container_name} python3 /root/services/data_transfer/service_files/data_transfer_tool.py generate_backup"
        data_type_cmd = f"{data_type}"
        user_cmd = f"-u {user_name}"
        password_cmd = f"-p {password}"
        cmd= f"{base_cmd} {data_type_cmd} {user_cmd} {password_cmd} "
        if verbose is True:
            verbose_cmd = f"-v" 
            cmd = f"{cmd} {verbose_cmd}"
        print (f"The docker command is: {cmd}")
        stdout, stderr= node.execute(cmd)
        
        
    def upload_backup(self, node, data_type, file_name, storage, remote_dir, verbose=False):
        """
        uploads backup data file (prometheus:snapshot, elk: snapshot) to the cloud stroage remote dir
        Args:
            node(fablib.node): fabric node on which the timestamp docker container is running
            data_type(str): name of data type(prometheus or elk)
            file_name(str): name of the file to be uploaded
            storage(str): storage name configured in rclone
            remote_dir(str): directory name to be create in the storage
        """
        try:
            node = self.slice.get_node(name=node)
        except Exception as e:
            print(f"Fail: {e}")
        base_cmd = f"sudo docker exec -i {self.container_name} python3 /root/services/data_transfer/service_files/data_transfer_tool.py upload_backup"
        data_type_cmd = f"{data_type}"
        file_name_cmd = f"-file {file_name}"
        storage_cmd = f"-s {storage}"
        remote_dir_cmd = f"-d {remote_dir}"
        
        cmd= f"{base_cmd} {data_type_cmd} {file_name_cmd} {storage_cmd} {remote_dir_cmd}"
        if verbose is True:
            verbose_cmd = f"-v" 
            cmd = f"{cmd} {verbose_cmd}"
        print (f"The docker command is: {cmd}")
        stdout, stderr= node.execute(cmd)
    
    # This function should appear in the import class below. Leave it here for convenience
    def download_backup(self, node, data_type, file_name, storage, remote_dir, verbose=False):
        """
        downloads backup data file (prometheus:snapshot, elk: json) from the cloud stroage remote dir
        Args:
            node(fablib.node): fabric node on which the timestamp docker container is running
            data_type(str): name of data type(prometheus or elk)
            file_name(str): name of the file to be uploaded
            storage(str): storage name configured in rclone
            remote_dir(str): directory name to be create in the storage
        """
        try:
            node = self.slice.get_node(name=node)
        except Exception as e:
            print(f"Fail: {e}")
        base_cmd = f"sudo docker exec -i {self.container_name} python3 /root/services/data_transfer/service_files/data_transfer_tool.py download_backup"
        data_type_cmd = f"{data_type}"
        file_name_cmd = f"-file {file_name}"
        storage_cmd = f"-s {storage}"
        remote_dir_cmd = f"-d {remote_dir}"
        
        cmd= f"{base_cmd} {data_type_cmd} {file_name_cmd} {storage_cmd} {remote_dir_cmd}"
        if verbose is True:
            verbose_cmd = f"-v" 
            cmd = f"{cmd} {verbose_cmd}"
        print (f"The docker command is: {cmd}")
        stdout, stderr= node.execute(cmd)

        

        

   
