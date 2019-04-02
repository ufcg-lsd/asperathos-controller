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

import requests
import json


class ServiceInstanceLocator:
    def __init__(self, compute_nodes, actuator_service_port):
        self.compute_nodes = compute_nodes
        self.actuator_service_port = actuator_service_port

    def locate(self, vm_id):
        # TODO: check vm_id

        for compute_node in self.compute_nodes:
            url = ("http://" + compute_node + ":"
                   + str(self.actuator_service_port) +
                   "/actuator/list_vms/")

            options = {"actuator_plugin": "kvm", "vm_id": vm_id}
            response = requests.post(
                url,
                headers={
                    "Content-Type": "application/json"},
                data=json.dumps(options))

            vms_ids_str = response.text
            vms_ids = vms_ids_str.split(",")

            if vm_id in vms_ids:
                return compute_node

        raise Exception(
            "It was not possible to find the instance %s"
            % (vm_id))
