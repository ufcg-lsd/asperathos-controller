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

from controller.utils.logger import configure_logging, Log
import datetime

# TODO: documentation


class BasicAlarm:

    # TODO: Think about these constants placements
    PROGRESS_METRIC_NAME = "spark.job_progress"
    ELAPSED_TIME_METRIC_NAME = 'spark.elapsed_time'

    def __init__(self, actuator, metric_source, trigger_down, trigger_up,
                 min_cap, max_cap, actuation_size, metric_rounding):

        # TODO: Check parameters
        self.metric_source = metric_source
        self.actuator = actuator
        self.trigger_down = trigger_down
        self.trigger_up = trigger_up
        self.min_cap = min_cap
        self.max_cap = max_cap
        self.actuation_size = actuation_size
        self.metric_rounding = metric_rounding

        self.logger = Log("basic.alarm.log", "controller.log")
        configure_logging()

        self.last_time_progress_timestamp = datetime.datetime.strptime(
            "0001-01-01T00:00:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')

        self.last_job_progress_timestamp = datetime.datetime.strptime(
            "0001-01-01T00:00:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')

    def get_job_progress(self, application_id):
        job_progress_measurement = self.metric_source.get_most_recent_value(
            BasicAlarm.PROGRESS_METRIC_NAME,
            {"application_id": application_id})

        job_progress_timestamp = job_progress_measurement[0]
        job_progress = job_progress_measurement[1]
        job_progress = round(job_progress, self.metric_rounding)

        return job_progress_timestamp, job_progress

    def get_time_progress(self, application_id):
        time_progress_measurement = self.metric_source.get_most_recent_value(
            BasicAlarm.ELAPSED_TIME_METRIC_NAME,
            {"application_id": application_id})

        time_progress_timestamp = time_progress_measurement[0]
        time_progress = time_progress_measurement[1]
        time_progress = round(time_progress, self.metric_rounding)

        return time_progress_timestamp, time_progress

    def check_measurements_are_new(self, job_progress_timestamp,
                                   time_progress_timestamp):

        return (self.last_job_progress_timestamp < job_progress_timestamp
                and
                self.last_time_progress_timestamp < time_progress_timestamp)

    def check_application_state(self, application_id, instances):
        # TODO: Check parameters
        try:
            self.logger.log("Getting progress")
            job_progress_timestamp, job_progress = self.get_job_progress(
                application_id)

            self.logger.log("Getting time progress")
            time_progress_timestamp, time_progress = self.get_time_progress(
                application_id)

            self.logger.log("Progress-[%s]-%f|Time progress-[%s]-%f" %
                            (str(job_progress_timestamp),
                             job_progress,
                             str(time_progress_timestamp),
                             time_progress))

            if self.check_measurements_are_new(job_progress_timestamp,
                                               time_progress_timestamp):

                diff = job_progress - time_progress

                self.scale_down(diff, instances)
                self.scale_up(diff, instances)

                self.last_job_progress_timestamp = job_progress_timestamp
                self.last_time_progress_timestamp = time_progress_timestamp

            else:
                self.logger.log("Could not acquire more recent metrics")

        except Exception:
            # TODO: Check exception type
            self.logger.log("Could not get metrics")
            return

    def scale_down(self, diff, instances):
        if diff > 0 and diff >= self.trigger_down:
            self.logger.log("Scaling down")
            cap = self.actuator.get_allocated_resources(instances[0])
            new_cap = max(cap - self.actuation_size, self.min_cap)
            cap_instances = {instance: new_cap for instance in instances}

            self.actuator.adjust_resources(cap_instances)

    def scale_up(self, diff, instances):
        if diff < 0 and abs(diff) >= self.trigger_up:
            self.logger.log("Scaling up")
            cap = self.actuator.get_allocated_resources(instances[0])
            new_cap = min(cap + self.actuation_size, self.max_cap)
            cap_instances = {instance: new_cap for instance in instances}

            self.actuator.adjust_resources(cap_instances)
