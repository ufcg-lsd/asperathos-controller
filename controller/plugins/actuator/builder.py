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

import controller.service.api as api

from controller.plugins.actuator.k8s_replicas.plugin import K8sActuator
from controller.plugins.actuator.nop.plugin import NopActuator
from controller.service import plugin_service


class ActuatorBuilder:
    def get_actuator(self, plugin, parameters={}):
        name = plugin['name']
        if name == "k8s_replicas":
            actuator = K8sActuator(parameters['app_id'],
                                   api.k8s_manifest)
            return actuator

        elif name == "nop":
            return NopActuator()

        else:
            try:
                return plugin_service.get_plugin(plugin['module'])
            except ImportError:
                plugin_service.install_plugin(plugin['source'], plugin['plugin_source'])
                return plugin_service.get_plugin(plugin['module'])
