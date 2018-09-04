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

# This class contains the logic used to adjust the amount of resources allocated to applications


class KubeJobs:

    ERROR_METRIC_NAME = "application-progress.error"

    def __init__(self, actuator, metric_source, trigger_down, trigger_up, min_cap, max_cap,
                 actuation_size, application_id):
        # TODO: Check parameters
        self.metric_source = metric_source
        self.actuator = actuator
        self.trigger_down = trigger_down
        self.trigger_up = trigger_up
        self.min_cap = min_cap
        self.max_cap = max_cap
        self.actuation_size = actuation_size
        self.application_id = application_id

        self.logger = ScalingLog("%s.generic.alarm.log" % (application_id), "controller.log",
                                 application_id)
        self.cap_logger = ScalingLog("%s.cap.log" % (
            application_id), "cap.log", application_id)

        self.last_progress_error_timestamp = datetime.datetime.strptime("0001-01-01T00:00:00.0Z",
                                                                        '%Y-%m-%dT%H:%M:%S.%fZ')
        self.last_action = ""
        self.cap = -1

    def check_application_state(self):
        """
            Checks the application progress by getting progress metrics from a
            metric source, checks if the metrics are new and tries to modify the
            amount of allocated resources if necessary.
        """

        # TODO: Check parameters
        try:
            self.logger.log("Getting progress error")
            self.last_action = "getting progress error"
            # Get the progress error value and timestamp
            progress_error_timestamp, progress_error = self._get_progress_error(
                self.application_id)

            self.logger.log(
                "Progress error-[%s]-%f" % (str(progress_error_timestamp), progress_error))
            self.last_action = "Progress error-[%s]-%f" % (
                str(progress_error_timestamp), progress_error)

            # Check if the metric is new by comparing the timestamps of the current metric and most recent metric
            if self._check_measurements_are_new(progress_error_timestamp):
                self._scale_down(progress_error)
                self._scale_up(progress_error)

                if self.cap != -1:
                    self.cap_logger.log("%.0f|%s|%s" % (time.time(),
                                                        str(self.application_id), str(self.cap)))

                self.last_progress_error_timestamp = progress_error_timestamp
            else:
                self.last_action += " Could not acquire more recent metrics"
                self.logger.log("Could not acquire more recent metrics")
        except Exception as e:
            # TODO: Check exception type
            self.logger.log(str(e))

            raise e
            
    def _scale_down(self, progress_error):
        """
            Checks if it is necessary to scale down, according to
            the progress_error. If it is, calculates the new CPU cap
            value and tries to modify the cap of the vms.
        """

        # If the error is positive and its absolute value is too high, scale down
        if progress_error > 0 and progress_error >= self.trigger_down:
            self.logger.log("Scaling down")
            self.last_action = "Getting allocated resources"

            # Get current CPU cap
            replicas = self.actuator.get_number_of_replicas()
            new_replicas = max(replicas - self.actuation_size, self.min_cap)
            # new_cap = max(cap - self.actuation_size, self.min_cap)

            self.logger.log("Scaling from %d to %d" % (replicas, new_replicas))
            self.last_action = "Scaling from %d to %d" % (replicas, new_replicas)

            # Currently, we use the same cap for all the vms
            # cap_instances = {instance: new_cap for instance in instances}

            # Set the new cap
            self.actuator.adjust_resources(new_replicas)

    def _scale_up(self, progress_error):
        """
            Checks if it is necessary to scale up, according to
            the progress_error. If it is, calculates the new CPU cap
            value and tries to modify the cap of the vms.
        """

        # If the error is negative and its absolute value is too high, scale up
        if progress_error < 0 and abs(progress_error) >= self.trigger_up:
            self.logger.log("Scaling up")
            self.last_action = "Getting allocated resources"

            # Get current number of replicas
            replicas = self.actuator.get_number_of_replicas()
            new_replicas = min(replicas + self.actuation_size, self.max_cap)

            self.logger.log("Scaling from %d to %d" % (replicas, new_replicas))
            self.last_action = "Scaling from %d to %d" % (replicas, new_replicas)

            # Currently, we use the same cap for all the vms
            # cap_instances = {instance: new_cap for instance in instances}

            # Set the new cap
            self.actuator.adjust_resources(new_replicas)

    def _get_progress_error(self, application_id):
        progress_error_measurement = self.metric_source.get_most_recent_value(application_id)
        progress_error_timestamp = progress_error_measurement[0]
        progress_error = progress_error_measurement[1]
        return progress_error_timestamp, progress_error

    def _check_measurements_are_new(self, progress_error_timestamp):
        return self.last_progress_error_timestamp < progress_error_timestamp

    def status(self):
        return self.last_action
