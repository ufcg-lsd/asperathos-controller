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

import six

from controller.exceptions import api as ex
from controller.plugins.controller.base import Controller
from controller.plugins.controller.kubejobs.alarm import KubeJobs
from controller.utils.logger import ScalingLog

# This class dictates the pace of the scaling process.
# It controls when Generic_Alarm
# is called to check application state and when is necessary to wait.


class KubejobsController(Controller):

    def __init__(self, application_id, parameters):
        self.validate(parameters)
        self.logger = ScalingLog(
            "diff.controller.log", "controller.log", application_id)
        self.application_id = application_id
        parameters.update({"app_id": application_id})
        # read scaling parameters
        self.check_interval = \
            parameters["check_interval"]
        # We use a lock here to prevent race conditions when stopping the
        # controller
        self.running = True
        self.running_lock = threading.RLock()

        # The alarm here is responsible for deciding whether to scale up or
        # down, or even do nothing
        self.alarm = KubeJobs(parameters)

    def start_application_scaling(self):
        run = True
        self.logger.log("Start to control resources")

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

    def validate(self, data):
        data_model = {
            "actuator": six.string_types,
            "check_interval": int,
            "metric_source": six.string_types,
            "schedule_strategy": six.string_types
        }

        for key in data_model:
            if (key not in data):
                raise ex.BadRequestException(
                    "Variable \"{}\" is missing".format(key))
            if (not isinstance(data[key], data_model[key])):
                raise ex.BadRequestException(
                    "\"{}\" has unexpected variable type: {}. Was expecting {}"
                    .format(key, type(data[key]), data_model[key]))
