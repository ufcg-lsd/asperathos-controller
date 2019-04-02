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

from controller.utils.logger import ScalingLog
import datetime
import time


class PIDAlarm:

    ERROR_METRIC_NAME = "application-progress.error"

    def __init__(self, actuator, metric_source, trigger_down, trigger_up,
                 min_cap, max_cap, metric_rounding, heuristic_options,
                 application_id, instances):

        self.metric_source = metric_source
        self.actuator = actuator
        self.trigger_down = trigger_down
        self.trigger_up = trigger_up
        self.min_cap = min_cap
        self.max_cap = max_cap
        self.metric_rounding = metric_rounding
        self.heuristic_options = heuristic_options
        self.application_id = application_id
        self.instances = instances
        self.integrated_error = 0

        self.logger = ScalingLog("%s.pid.alarm.log" % (application_id),
                                 "controller.log", application_id)

        self.cap_logger = ScalingLog("%s.cap.log" % (
            application_id), "cap.log", application_id)

        self.last_error = ""
        self.last_error_timestamp = datetime.datetime.strptime(
            "0001-01-01T00:00:00.0Z",
            '%Y-%m-%dT%H:%M:%S.%fZ')
        self.last_action = ""
        self.cap = -1

    def check_application_state(self):
        """
            Checks the application progress by getting progress metrics from a
            metric source, checks if the metrics are new and tries to modify
            the amount of allocated resources if necessary.
        """
        self.last_action = "getting progress error"

        # Get the progress error value and timestamp
        error_timestamp, error = self._get_error(
            self.application_id)

        self.last_action = "Progress error-[%s]-%f" % (
            str(error_timestamp), error)
        print self.last_action

        # Check if the metric is new by comparing the timestamps
        # of the current metric and most recent metric
        if self._check_measurements_are_new(error_timestamp):
            self._scale(error, self.instances)

            if self.cap != -1:
                print("%.0f|%s|%s" % (
                      time.time(), str(self.application_id), str(self.cap)))

            self.last_error = error
            self.last_error_timestamp = error_timestamp

        else:
            self.last_action += " Could not acquire more recent metrics"
            self.logger.log("Could not acquire more recent metrics")

    def _scale(self, error, instances):
        """
            Checks if it is necessary to scale, according to
            the error. If it is, calculates the new CPU cap
            value and tries to modify the cap of the vms.
        """

        self.logger.log("Scaling down")
        self.last_action = "Getting allocated resources"

        # Get current CPU cap
        cap = self.actuator.get_allocated_resources_to_cluster(instances)
        new_cap = self._decide_next_cap(
            cap, error, self.heuristic_options)

        self.logger.log("Scaling from %d to %d" % (cap, new_cap))
        self.last_action = "Scaling from %d to %d" % (cap, new_cap)

        # Currently, we use the same cap for all the vms
        cap_instances = {instance: new_cap for instance in instances}

        # Set the new cap
        self.actuator.adjust_resources(cap_instances)

        self.cap = new_cap

    def _get_error(self, application_id):
        error_measurement = self.metric_source.get_most_recent_value(
            PIDAlarm.ERROR_METRIC_NAME,
            {"application_id": application_id}
        )
        error_timestamp = error_measurement[0]
        error = error_measurement[1]
        error = round(error, self.metric_rounding)
        return error_timestamp, error

    def _check_measurements_are_new(self, error_timestamp):
        return self.last_error_timestamp < error_timestamp

    def _decide_next_cap(self, current_cap, error, heuristic_options):
        heuristic = heuristic_options["heuristic_name"]

        if heuristic == "error_pid":
            return self._error_pid(current_cap, error, heuristic_options)
        else:
            raise Exception("Unknown heuristic")

    def _error_pid(self, current_cap, error, heuristic_options):
        """
            Calculates the new cap value using a PID algorithm.

            The new cap expression is:
            new cap = old cap
                      - proportional_factor * error
                      - derivative_factor * (error difference)
                      - integrative_factor * (integrated_error)
        """

        proportional_factor = heuristic_options["proportional_factor"]
        derivative_factor = heuristic_options["derivative_factor"]
        integrative_factor = heuristic_options["integrative_factor"]

        proportional_component = -1 * error * proportional_factor

        """ If it is the first call, there is no last_error and the derivative
            component value is null """
        if self.last_error == "":
            derivative_component = 0
        else:
            derivative_component = -1 * derivative_factor * \
                (error - self.last_error)

        self.integrated_error += error
        integrative_component = -1 * self.integrated_error * integrative_factor

        new_cap = current_cap + proportional_component + \
            derivative_component + integrative_component
        new_cap = max(min(new_cap, self.max_cap), self.min_cap)

        return new_cap
