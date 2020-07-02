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

import datetime
import time

from controller.utils.logger import ScalingLog
from controller.plugins.scheduler.default.plugin import DefaultScheduler
from controller.plugins.scheduler.pid.plugin import PidScheduler
from controller.plugins.scheduler.pid_scripted.plugin import PidScripted
from controller.plugins.metric_source.builder import MetricSourceBuilder
from controller.plugins.actuator.builder import ActuatorBuilder


# This class contains the logic used to adjust the amount of resources
# allocated to applications


class KubeJobs:

    ERROR_METRIC_NAME = "application-progress.error"

    def __init__(self, data):
        # TODO: Check parameters
        scaling_parameters = data
        self.metric_source = MetricSourceBuilder().\
            get_metric_source(scaling_parameters.get('metric_source'), data)
        self.app_id = data.get('app_id')
        scaling_parameters.update({'app_id': self.app_id})
        self.scheduler = self.setup_scheduler(scaling_parameters)
        self.actuator = self.setup_actuator(scaling_parameters)
        self.logger = ScalingLog("%s.generic.alarm.log" % (self.app_id),
                                 "controller.log", self.app_id)
        self.cap_logger = ScalingLog("%s.cap.log" % (self.app_id),
                                     "cap.log", self.app_id)
        self.last_progress_error_timestamp = datetime.datetime.strptime(
            "0001-01-01T00:00:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')
        self.last_action = ""
        self.cap = -1

    def setup_scheduler(self, parameters):
        strategy = parameters.get('schedule_strategy')
        if strategy == "default":
            return DefaultScheduler(parameters)

        elif strategy == "pid":
            return PidScheduler(parameters)

        elif strategy == "scripted":
            return PidScripted(parameters)

    def setup_actuator(self, parameters):
        actuator = parameters.get('actuator')
        return ActuatorBuilder().get_actuator(actuator,
                                              parameters)

    def check_application_state(self):
        """
            Checks the application progress by getting progress metrics from a
            metric source, checks if the metrics are new
            and tries to modify the
            amount of allocated resources if necessary.
        """
        # TODO: Check parameters
        progress_error_timestamp, progress_error = \
            self._get_progress_error(self.app_id)

        self.last_action = "Progress error-[%s]-%f" % \
            (str(progress_error_timestamp), progress_error)
        if self._check_measurements_are_new(progress_error_timestamp):
            self._scale(progress_error)
            if self.cap != -1:
                self.cap_logger.log("%.0f|%s|%s" % (time.time(),
                                    str(self.app_id), str(self.cap)))
            self.last_progress_error_timestamp = progress_error_timestamp
        else:
            self.last_action += " Could not acquire more recent metrics"
            self.logger.log(self.last_action)

    def _get_progress_error(self, app_id):
        self.last_action = "Getting progress error"
        self.logger.log(self.last_action)
        progress_error_measurement = self.metric_source.get_most_recent_value(
            app_id)
        progress_error_timestamp = progress_error_measurement[0]
        progress_error = progress_error_measurement[1]

        return progress_error_timestamp, progress_error

    def _scale(self, progress_error):

        last_replicas = self.actuator.get_number_of_replicas()

        info = {'last_replicas': last_replicas,
                'progress_error': progress_error}

        new_resource_allocation = self.scheduler.scale(info)

        if new_resource_allocation is not None:
            self.logger.log("Scaling from %d to %d" %
                            (last_replicas, new_resource_allocation))
            self.actuator.adjust_resources(new_resource_allocation)

    def _check_measurements_are_new(self, progress_error_timestamp):
        return self.last_progress_error_timestamp < progress_error_timestamp

    def status(self):
        return self.last_action
