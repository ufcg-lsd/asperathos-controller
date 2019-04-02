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

import threading
import time

from controller.plugins.actuator.builder import ActuatorBuilder
from controller.plugins.metric_source.builder import MetricSourceBuilder
from controller.plugins.controller.base import Controller
from controller.exceptions.monasca import MetricNotFoundException
from controller.plugins.controller.proportional_derivative.alarm import (
    ProportionalDerivativeAlarm
)

from controller.utils.logger import ScalingLog


class ProportionalDerivativeController(Controller):

    def __init__(self, application_id, plugin_info):
        self.logger = ScalingLog("proportional_derivative.controller.log",
                                 "controller.log", application_id)

        plugin_info = plugin_info["plugin_info"]

        self.application_id = application_id
        self.instances = plugin_info["instances"]
        self.check_interval = plugin_info["check_interval"]
        self.trigger_down = plugin_info["trigger_down"]
        self.trigger_up = plugin_info["trigger_up"]
        self.min_cap = plugin_info["min_cap"]
        self.max_cap = plugin_info["max_cap"]
        self.metric_rounding = plugin_info["metric_rounding"]
        self.actuator_type = plugin_info["actuator"]
        self.metric_source_type = plugin_info["metric_source"]
        self.heuristic_options = plugin_info["heuristic_options"]

        self.running = True
        self.running_lock = threading.RLock()

        # Gets a new metric source plugin using the given name
        metric_source = MetricSourceBuilder().get_metric_source(
            self.metric_source_type, plugin_info)

        # Gets a new actuator plugin using the given name
        actuator = ActuatorBuilder().get_actuator(self.actuator_type,
                                                  plugin_info)

        """ The alarm here is responsible for deciding whether to
            scale up or down, or even do nothing """
        self.alarm = ProportionalDerivativeAlarm(actuator, metric_source,
                                                 self.trigger_down,
                                                 self.trigger_up,
                                                 self.min_cap,
                                                 self.max_cap,
                                                 self.metric_rounding,
                                                 self.heuristic_options,
                                                 application_id,
                                                 self.instances)

    def start_application_scaling(self):
        run = True

        while run:
            self.logger.log("Monitoring application: %s" %
                            (self.application_id))

            # Call the alarm to check the application
            try:
                self.alarm.check_application_state()
            except MetricNotFoundException:
                self.logger.log("No metrics available")
            except Exception as e:
                self.logger.log(str(e))

            # Wait some time
            time.sleep(float(self.check_interval))

            with self.running_lock:
                run = self.running

    def stop_application_scaling(self):
        with self.running_lock:
            self.running = False

    def status(self):
        return self.alarm.status()
