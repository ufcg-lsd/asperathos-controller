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
import requests
import json


class ServiceActuator(Actuator):

    def __init__(self, actuator_port, instance_locator):
        self.instance_locator = instance_locator
        self.actuator_port = actuator_port

    def prepare_environment(self, vm_data):
        self.adjust_resources(vm_data)

    def adjust_resources(self, vm_data):
        for vm_id in vm_data.keys():
            actuator_ip = self.instance_locator.locate(vm_id)
            url = ("http://" + actuator_ip + ":" + self.actuator_port +
                   "/actuator/set_vcpu_cap/")

            cap = vm_data[vm_id]
            options = {"actuator_plugin": "kvm",
                       "vm_id": vm_id,
                       "cap": cap}

            requests.post(url, headers={"Content-Type": "application/json"},
                          data=json.dumps(options))

    def get_allocated_resources(self, vm_id):
        try:
            actuator_ip = self.instance_locator.locate(vm_id)
            url = ("http://" + actuator_ip + ":" + self.actuator_port +
                   "/actuator/allocated_resources/")

            options = {"actuator_plugin": "kvm", "vm_id": vm_id}
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(options))

            return float(response.text)

        except BaseException:
            raise Exception("Could not get allocated resources")
