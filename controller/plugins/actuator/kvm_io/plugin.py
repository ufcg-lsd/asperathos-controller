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


class KVMIOActuator(Actuator):
    def __init__(self, locator, remote):
        self.locator = locator
        self.remote = remote

    # This method receives as argument a map {vm-id:cap}
    def adjust_resources(self, vmcap_map):
        for vm in vmcap_map:
            try:
                host = self.locator.locate(vm)

                cap = int(vmcap_map[vm])
                self.remote.change_vcpu_quota(host, vm, cap)
                self.remote.change_io_quota(host, vm, cap)

            except InstanceNotFoundException:
                print "instance not found:%s" % (vmcap_map)

    def get_allocated_resources(self, vm_id):
        host = self.locator.locate(vm_id)
        allocated_resources = self.remote.get_allocated_resources(host, vm_id)

        return allocated_resources

    def get_allocated_resources_to_cluster(self, vms_ids):
        for vm_id in vms_ids:
            try:
                return self.get_allocated_resources(vm_id)

            except InstanceNotFoundException:
                print "instance not found:%s" % (vm_id)

        raise Exception("Could not get allocated resources")
