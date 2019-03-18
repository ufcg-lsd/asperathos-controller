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

from controller.exceptions.kvm import InstanceNotFoundException


class InstanceLocator(object):
    def __init__(self, ssh, compute_nodes, keypair):
        self.compute_nodes = compute_nodes
        self.keypair = keypair
        self.ssh = ssh

    def locate(self, vm_id):
        for compute_node in self.compute_nodes:
            command = (
                "virsh schedinfo %s > /dev/null 2> /dev/null ; echo $?"
                % (vm_id))

            in_node = self.ssh.run_and_get_result(command,
                                                  "root",
                                                  compute_node,
                                                  self.keypair)

            if in_node == "0\n":
                return compute_node

        message = ("""It was not possible to find the instance:
                      command %s, ssh return value %s""" % (command, in_node))

        raise InstanceNotFoundException(vm_id, message)
