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

from controller.plugins.controller.basic.plugin import BasicController
from controller.plugins.controller.generic.plugin import GenericController
from controller.plugins.controller.pid.plugin import PIDController
from controller.plugins.controller.single.plugin import (
    SingleApplicationController
)
from controller.plugins.controller.proportional.plugin import (
    ProportionalController
)
from controller.plugins.controller.tendency.plugin import (
    TendencyAwareProportionalController
)
from controller.plugins.controller.proportional_derivative.plugin import (
    ProportionalDerivativeController
)
from controller.plugins.controller.kubejobs.plugin import KubejobsController
from controller.plugins.metric_source.builder import MetricSourceBuilder
from controller.plugins.actuator.builder import ActuatorBuilder


class ControllerBuilder:

    def __init__(self):
        pass

    def get_controller(self, name, app_id, plugin_info):
        if name == "basic":
            metric_source_type = plugin_info["policy"]["metric_source"]
            actuator_type = plugin_info["policy"]["actuator"]

            metric_source = MetricSourceBuilder().get_metric_source(
                                metric_source_type, plugin_info)

            actuator = ActuatorBuilder().get_actuator(actuator_type)

            return BasicController(metric_source, actuator, plugin_info)

        elif name == "single":
            return SingleApplicationController(app_id, plugin_info)

        elif name == "progress_error":
            return GenericController(app_id, plugin_info)

        elif name == "proportional":
            return ProportionalController(app_id, plugin_info)

        elif name == "proportional_derivative":
            return ProportionalDerivativeController(app_id,
                                                    plugin_info)

        elif name == "pid":
            return PIDController(app_id, plugin_info)

        elif name == "progress_tendency":
            return TendencyAwareProportionalController(app_id,
                                                          plugin_info)

        elif name == "kubejobs":
            return KubejobsController(app_id, plugin_info)


        else:
            # FIXME: exception type
            raise Exception("Unknown controller type")
