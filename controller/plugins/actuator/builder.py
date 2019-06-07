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


class ActuatorBuilder:
    def get_actuator(self, name, parameters={}):

        if name == "k8s_replicas":
            actuator = K8sActuator(parameters['app_id'],
                                   api.k8s_manifest)
            return actuator

        elif name == "nop":
            return NopActuator()

        else:
            # FIXME: review this exception type
            raise Exception("Unknown actuator type")
