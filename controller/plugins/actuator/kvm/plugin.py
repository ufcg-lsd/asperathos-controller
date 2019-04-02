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


class KVMActuator(Actuator):
    def __init__(self, instance_locator, remote_kvm, default_io_cap):
        self.instance_locator = instance_locator
        self.remote_kvm = remote_kvm
        self.default_io_cap = default_io_cap

    # TODO: validation
    # This method receives as argument a map {vm-id:CPU cap}
    def adjust_resources(self, vm_data):

        # Discover vm_id - compute nodes map
        for instance in vm_data.keys():
            try:
                # Access compute nodes to discover vms location
                instance_location = self.instance_locator.locate(instance)
                # Access a compute node and change cap
                self.remote_kvm.change_vcpu_quota(
                    instance_location, instance, int(vm_data[instance]))
                self.remote_kvm.change_io_quota(
                    instance_location, instance, self.default_io_cap)

            except InstanceNotFoundException:
                print "instance not found:%s" % (instance)

    # TODO: validation
    def get_allocated_resources(self, vm_id):

        # Access compute nodes to discover vm location
        host = self.instance_locator.locate(vm_id)
        # Access a compute node and get amount of allocated resources
        return self.remote_kvm.get_allocated_resources(host, vm_id)

    # TODO: validation
    def get_allocated_resources_to_cluster(self, vms_ids):
        for vm_id in vms_ids:
            try:
                return self.get_allocated_resources(vm_id)
            except InstanceNotFoundException:
                print "instance not found:%s" % (vm_id)

        raise Exception("Could not get allocated resources")
