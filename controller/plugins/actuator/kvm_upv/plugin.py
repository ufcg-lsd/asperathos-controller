# Copyright (c) 2017 LSD - UFCG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from controller.plugins.actuator.base import Actuator
from controller.exceptions.kvm import InstanceNotFoundException

import ConfigParser
import paramiko


class KVMUPVActuator(Actuator):

    def __init__(self, iops_reference, bs_reference):
        self.conn = paramiko.SSHClient()
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.config = ConfigParser.RawConfigParser()
        self.config.read("controller.cfg")
        self.one_user = self.config.get("actuator", "one_username")
        self.one_password = self.config.get("actuator", "one_password")
        self.one_url = self.config.get("actuator", "one_url")
        self.compute_nodes_frontend = self.config.get("actuator",
                                                      "compute_nodes_frontend")
        self.iops_reference = iops_reference
        self.bs_reference = bs_reference

    def _connect(self):
        self.conn.connect(
            hostname=self.config.get("actuator", "access_ip"),
            username=self.config.get("actuator", "access_username"),
            password=self.config.get("actuator", "access_password"))

    # TODO: validation
    def prepare_environment(self, vm_data):
        self.adjust_resources(vm_data)

    # TODO: validation
    # This method receives as argument a map {vm-id:CPU cap}
    def adjust_resources(self, vm_data):
        self._connect()

        instances_locations = {}

        # Discover vm_id - compute nodes map
        for instance in vm_data.keys():
            # Access compute nodes to discover vms location
            instances_locations[instance] = self._find_host(instance)

        for instance in vm_data.keys():
            # Access a compute node and change cap
            self._change_vcpu_quota(instances_locations[instance],
                                    instance, int(vm_data[instance]))

            self._change_io_quota(instances_locations[instance],
                                  instance, int(vm_data[instance]))

        self.conn.close()

    # TODO: validation
    def get_allocated_resources(self, vm_id):
        self._connect()
        # Access compute nodes to discover vm location
        host = self._find_host(vm_id)

        # List all the vms to get the ONE id and map with the KVM id
        virsh_list = "virsh list"
        command = ("ssh root@%s \'ssh %s \"%s\"\'"
                   % (self.compute_nodes_frontend,
                      host,
                      virsh_list))

        stdin, stdout, stderr = self.conn.exec_command(command)

        vm_list = stdout.read().split("\n")
        virsh_id = self._extract_id(vm_list, vm_id)
        virsh_schedinfo = (("virsh schedinfo %s | grep vcpu_quota "
                            % (virsh_id)) + "| awk \'{print $3}\'")

        command = ("ssh root@%s \'ssh %s \'%s\'\'"
                   % (self.compute_nodes_frontend, host, virsh_schedinfo))

        stdin, stdout, stderr = self.conn.exec_command(command)

        cap = int(stdout.read())

        print "get_allocated_resources: id: %s - cap: %s" % (vm_id, cap)

        self.conn.close()

        if cap == -1:
            return 100
        else:
            return cap / 1000

    def get_allocated_resources_to_cluster(self, vms_ids):
        for vm_id in vms_ids:
            try:
                return self.get_allocated_resources(vm_id)
            except InstanceNotFoundException:
                print "instance not found:%s" % (vm_id)

        raise Exception("Could not get allocated resources")

    def _change_vcpu_quota(self, host, vm_id, cap):
        # ssh for the actual host
        virsh_list = "virsh list"
        command = ("ssh root@%s \'ssh %s \"%s\"\'"
                   % (self.compute_nodes_frontend, host, virsh_list))

        # List all the vms to get the ONE id and map with the KVM id
        stdin, stdout, stderr = self.conn.exec_command(command)
        vm_list = stdout.read().split("\n")
        virsh_id = self._extract_id(vm_list, vm_id)

        virsh_cap = "virsh schedinfo %s | awk 'FNR == 3 {print $3}'" % virsh_id
        command = ("ssh root@%s \'ssh %s \'%s\'\'"
                   % (self.compute_nodes_frontend, host, virsh_cap))

        stdin, stdout, stderr = self.conn.exec_command(command)

        virsh_schedinfo = (("virsh schedinfo %s" % virsh_id) +
                           (" --set vcpu_quota=$(( %s * 1000 ))" % (cap)) +
                           " > /dev/null")

        command = ("ssh root@%s \'ssh %s \'%s\'\'"
                   % (self.compute_nodes_frontend, host, virsh_schedinfo))

        print "_change_vcpu_quota: id: %s - cap: %s" % (vm_id, cap * 1000)

        # Set the CPU cap
        self.conn.exec_command(command)

    def _change_io_quota(self, host, vm_id, cap):
        virsh_list = "virsh list"
        command = ("ssh root@%s \'ssh %s \"%s\"\'"
                   % (self.compute_nodes_frontend, host, virsh_list))

        # List all the vms to get the ONE id and map with the KVM id
        stdin, stdout, stderr = self.conn.exec_command(command)
        vm_list = stdout.read().split("\n")
        virsh_id = self._extract_id(vm_list, vm_id)

        # Get device to set cap
        command_get_block_device = (
            "virsh domblklist %s | awk 'FNR == 3 {print $1}'" % (virsh_id)
        )

        command = ("ssh root@%s \'ssh %s \'%s\'\'"
                   % (self.compute_nodes_frontend,
                      host,
                      command_get_block_device))

        stdin, stdout, stderr = self.conn.exec_command(command)
        block_device = stdout.read().strip()

        command_iops_quota = (cap * self.iops_reference) / 100
        command_bs_quota = (cap * self.bs_reference) / 100

        command_set_io_quota = ("virsh blkdeviotune %s %s "
                                "--current --total_iops_sec %s "
                                "--total_bytes_sec %s"
                                % (virsh_id, block_device,
                                   command_iops_quota,
                                   command_bs_quota))

        command = ("ssh root@%s \'ssh %s \'%s\'\'"
                   % (self.compute_nodes_frontend, host, command_set_io_quota))

        print ("_change_io_quota: id: %s - iops: %s - bs: %s"
               % (virsh_id, str(command_iops_quota), str(command_bs_quota)))

        # Set I/O cap
        self.conn.exec_command(command)

    def _find_host(self, vm_id):
        list_vms = ("onevm show %s --user %s " +
                    "--password %s --endpoint %s") % (vm_id, self.one_user,
                                                      self.one_password,
                                                      self.one_url)

        stdin, stdout, stderr = self.conn.exec_command(list_vms)

        for line in stdout.read().split('\n'):
            if "HOST" in line and "niebla" in line:
                return line.split()[2]

        return None

    def _extract_id(self, vm_list, vm_id):
        one_id = "one-" + vm_id
        for vm in vm_list:
            if one_id in vm:
                return vm.split()[0]

        return None
