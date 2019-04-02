# Copyright (c) 2019 LSD - UFCG.
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
from controller.plugins.controller.base import Controller
from controller.plugins.metric_source.builder import MetricSourceBuilder
from controller.plugins.controller.vertical.alarm import Vertical
from controller.utils.logger import ScalingLog


class VerticalController(Controller):

    def __init__(self, application_id, parameters):
        self.logger = ScalingLog(
            "diff.controller.log", "controller.log", application_id)
        scaling_parameters = parameters["control_parameters"]
        self.application_id = application_id
        parameters.update({"app_id": application_id})

        # Read scaling parameters
        self.check_interval = scaling_parameters["check_interval"]
        self.actuator_metric = scaling_parameters["actuator_metric"]
        self.trigger_down = scaling_parameters["trigger_down"]
        self.trigger_up = scaling_parameters["trigger_up"]
        self.min_quota = scaling_parameters["min_quota"]
        self.max_quota = scaling_parameters["max_quota"]

        # The actuator plugin name
        self.actuator_type = scaling_parameters["actuator"]

        # The metric source plugin name
        self.metric_source_type = scaling_parameters["metric_source"]

        # We use a lock here to prevent race conditions when stopping the
        # controller
        self.running = True
        self.running_lock = threading.RLock()

        # Gets a new metric source plugin using the given name
        metric_source = MetricSourceBuilder().get_metric_source(
            self.metric_source_type, parameters)

        # TODO: Add new actuator as option in the ActuatorBuilder
        # Gets a new actuator plugin using the given name
        actuator = ActuatorBuilder().get_actuator(self.actuator_type,
                                                  parameters=parameters)

        # The alarm here is responsible for deciding whether to scale up or
        # down, or even do nothing
        self.alarm = Vertical(
            actuator,
            metric_source,
            self.actuator_metric,
            self.trigger_down,
            self.trigger_up,
            self.min_quota,
            self.max_quota,
            self.application_id)

    def start_application_scaling(self):
        run = True
        print "Start to control resources"

        while run:
            self.logger.log("Monitoring application: %s" %
                            self.application_id)

            # Call the alarm to check the application
            self.alarm.check_application_state()

            # Wait some time
            time.sleep(float(self.check_interval))

            with self.running_lock:
                run = self.running

    def stop_application_scaling(self):
        with self.running_lock:
            self.running = False

    def status(self):
        return self.alarm.status()
