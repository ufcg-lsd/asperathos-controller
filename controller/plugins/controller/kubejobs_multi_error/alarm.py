# Copyright (c) 2020 LSD - UFCG.
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
from controller.plugins.scheduler.pid_multierror_combine_actions.plugin import PidSchedulerMultiErrorCombineActions
from controller.plugins.scheduler.pid_multierror_combine_errors.plugin import PidSchedulerMultiErrorCombineErrors
from controller.plugins.metric_source.builder import MetricSourceBuilder
from controller.plugins.actuator.builder import ActuatorBuilder


# This class contains the logic used to adjust the amount of resources
# allocated to applications


class MultiErrorKubeJobs:

    ERROR_METRIC_NAME = "application-progress.error"

    def __init__(self, data):
        # TODO: Check parameters
        scaling_parameters = data
        self.metric_sources = {}
        self.last_error_info = {}
        self.metric_source_names = data['metric_source_names']

        for name in data['metric_source_names']:
            metric_source_parameters = data.copy()
            metric_source_parameters['metric_queue'] = name
            metric_source = MetricSourceBuilder(). \
                get_metric_source(scaling_parameters.get('metric_source'), metric_source_parameters)
            self.metric_sources[name] = metric_source
            self.last_error_info[name] = (datetime.datetime.strptime(
                            "0001-01-01T00:00:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ'), None)

        self.app_id = data.get('app_id')
        scaling_parameters.update({'app_id': self.app_id})
        self.scheduler = self.setup_scheduler(scaling_parameters)
        self.actuator = self.setup_actuator(scaling_parameters)
        self.logger = ScalingLog("%s.generic.alarm.log" % (self.app_id),
                                 "controller.log", self.app_id)
        self.cap_logger = ScalingLog("%s.cap.log" % (self.app_id),
                                     "cap.log", self.app_id)
        self.last_action = ""
        self.cap = -1

    def setup_scheduler(self, parameters):
        strategy = parameters.get('schedule_strategy')
        if strategy == "default":
            return DefaultScheduler(parameters)

        elif strategy == "pid_combine_actions":
            return PidSchedulerMultiErrorCombineActions(parameters)

        elif strategy == "pid_combine_errors":
            return PidSchedulerMultiErrorCombineErrors(parameters)

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

        error_dict = self._get_progress_error(self.app_id)

        if self._check_measurements_are_new(error_dict):
            self._scale(error_dict)
            if self.cap != -1:
                self.cap_logger.log("%.0f|%s|%s" % (time.time(),
                                    str(self.app_id), str(self.cap)))
            self.last_error_info = error_dict
        else:
            self.last_action += " Could not acquire more recent metrics"
            self.logger.log(self.last_action)

    def _get_progress_error(self, app_id):
        self.last_action = "Getting progress error"
        self.logger.log(self.last_action)

        error_info = {}

        for name in self.metric_sources:
            self.logger.log("Getting error: %s" % name)
            error_info[name] = self.metric_sources[name].get_most_recent_value(app_id)
            self.logger.log(error_info)

        return error_info

    def _scale(self, error_dict):

        last_replicas = self.actuator.get_number_of_replicas()

        error_list = []

        for error_name in self.metric_source_names:
            error_list.append(error_dict[error_name][1])

        info = {'last_replicas': last_replicas,
                'error_info': error_list}

        new_resource_allocation = self.scheduler.scale(info)

        if new_resource_allocation is not None:
            self.logger.log("Scaling from %d to %d" %
                            (last_replicas, new_resource_allocation))
            self.actuator.adjust_resources(new_resource_allocation)

    def _check_measurements_are_new(self, error_dict):
        # TODO review this rule
        for error_name in error_dict:
            if error_dict[error_name][0] <= self.last_error_info[error_name][0]:
                return False
        return True

    def status(self):
        return self.last_action
