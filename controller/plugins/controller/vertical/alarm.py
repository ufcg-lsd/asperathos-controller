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


import datetime
import requests
import time

from controller.utils.logger import ScalingLog

"""
Class that implements the alarm for the Vertical plugin
"""


class Vertical:

    ERROR_METRIC_NAME = "application-progress.error"

    def __init__(self, actuator, metric_source, actuator_metric, trigger_down,
                 trigger_up, min_quota, max_quota, application_id):
        # TODO: Check parameters
        self.metric_source = metric_source
        self.actuator = actuator
        self.actuator_metric = actuator_metric
        self.trigger_down = trigger_down
        self.trigger_up = trigger_up
        self.min_quota = min_quota
        self.max_quota = max_quota
        self.application_id = application_id

        self.logger = ScalingLog(
            "%s.vertical.alarm.log" %
            (application_id),
            "controller.log",
            application_id)
        self.cap_logger = ScalingLog("%s.cap.log" % (
            application_id), "cap.log", application_id)

        self.last_progress_error_timestamp = datetime.datetime.strptime(
            "0001-01-01T00:00:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')

        self.last_action = ""
        self.cap = -1

    def check_application_state(self):
        """
            Checks the application progress by getting progress metrics from a
            metric source, checks if
            the metrics are new and tries to modify the
            amount of allocated resources if necessary.
        """

        # TODO: Check parameters
        try:
            self.logger.log("Getting progress error")
            self.last_action = "getting progress error"
            # Get the progress error value and timestamp
            progress_error_timestamp, progress_error = \
                self._get_progress_error(self.application_id)

            self.logger.log(
                "Progress error-[%s]-%f" %
                (str(progress_error_timestamp), progress_error))
            self.last_action = "Progress error-[%s]-%f" % (
                str(progress_error_timestamp), progress_error)

            # Check if the metric is new by comparing the timestamps of the
            # current metric and most recent metric
            if self._check_measurements_are_new(progress_error_timestamp):
                self._scale_down(progress_error)
                self._scale_up(progress_error)

                if self.cap != -1:
                    self.cap_logger.log(
                        "%.0f|%s|%s" %
                        (time.time(), str(
                            self.application_id), str(
                            self.cap)))

                self.last_progress_error_timestamp = progress_error_timestamp
            else:
                self.last_action += " Could not acquire more recent metrics"
                self.logger.log("Could not acquire more recent metrics")
        except Exception as e:
            # TODO: Check exception type
            self.logger.log(str(e))

            raise e

    def _scale_down(self, progress_error):
        """Scales down the specific resource using an external API.

        Arguments:
            progress_error {float} -- progress error of the job
        """

        # If the error is positive and its absolute value is too high, scale
        # down
        if progress_error > 0 and progress_error >= self.trigger_down:
            if self.actuator_metric == 'cpu':
                self.logger.log("Scaling down")
                self.last_action = "Getting allocated resources"

                self.logger.log(
                    "Scaling %s quota from %d / %d" %
                    (self.actuator_metric, self.max_quota, self.max_quota))
                print("Scaling %s from %d / %d" %
                      (self.actuator_metric, self.max_quota, self.max_quota))
                self.set_cpu_quota(self.max_quota)

    def _scale_up(self, progress_error):
        """Scales up the specific resource using an external API.

        Arguments:
            progress_error {float} -- progress error of the job
        """

        # If the error is negative and its absolute value is too high, scale up
        if progress_error < 0 and abs(progress_error) >= self.trigger_up:
            if self.actuator_metric == 'cpu':
                self.logger.log("Scaling up")
                self.last_action = "Getting allocated resources"

                self.logger.log(
                    "Scaling from %d / %d" %
                    (self.min_quota, self.max_quota))
                print(
                    "Scaling from %d / %d" %
                    (self.min_quota, self.max_quota))
                self.set_cpu_quota(self.min_quota)

    def _get_progress_error(self, application_id):
        """Gets the progress error of the job

        Arguments:
            application_id {string} -- The application identifier

        Returns:
            [tuple] -- Returns a tuple containing the progress error
                       timestamp and
                       the current value of the progress error
        """

        progress_error_measurement = self.metric_source.get_most_recent_value(
            application_id)
        progress_error_timestamp = progress_error_measurement[0]
        progress_error = progress_error_measurement[1]
        return progress_error_timestamp, progress_error

    def _check_measurements_are_new(self, progress_error_timestamp):
        """Check if the currently measurements where already computed.

        Arguments:
            progress_error_timestamp {string} -- Timestamp of the
                                                 current progress error

        Returns:
            [boolean] -- 'true' if the measurements are new, 'false' otherwise
        """

        return self.last_progress_error_timestamp < progress_error_timestamp

    def status(self):
        return self.last_action

    def set_cpu_quota(self, new_cpu_quota):
        """Sets the CPU quota of the physical machine using a external API

        Arguments:
            new_cpu_quota {int} -- The new value for the CPU quota
                                   of the machine
        """
        try:
            requests.post(
                'http://%s:5000' %
                (self.actuator.api_address),
                data='{\"cpu_quota\":\"' +
                str(new_cpu_quota) +
                '\"}')
        except Exception as ex:
            print("Error while modifying cpu quota")
            print ex.message
            raise
