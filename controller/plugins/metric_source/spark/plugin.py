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

import requests
import datetime
import time
import tzlocal
import pytz


class SparkMetricSource:

    def __init__(self, parameters):
        self.parameters = parameters

    def _get_elapsed_time(self, gmt_timestamp):
        try:
            local_tz = tzlocal.get_localzone()
        except Exception:
            local_tz = "America/Recife"
            local_tz = pytz.timezone(local_tz)
        date_time = datetime.datetime.strptime(
            gmt_timestamp, '%Y-%m-%dT%H:%M:%S.%fGMT')
        date_time = date_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
        elapsed_time = datetime.datetime.now() - date_time.replace(tzinfo=None)
        return elapsed_time.seconds

    def _get_progress(self, response_json, total_tasks):
        completed_tasks = 0

        for i in xrange(len(response_json)):
            completed_tasks += response_json[i]['numCompletedTasks']

        return completed_tasks / float(total_tasks)

    def _get_time_progress(self, response_json, expected_time):
        return self._get_elapsed_time(
            response_json[-1]['submissionTime']) / float(expected_time)

    def get_most_recent_value(self, metric_name, options):
        spark_master_ip = self.parameters["spark_master_ip"]
        app_id = options["application_id"]
        total_tasks = self.parameters["total_tasks"]
        expected_time = self.parameters["expected_time"]

        response = requests.get(
            'http://%s:4040/api/v1/applications/%s/jobs' %
            (spark_master_ip, app_id))
        response_json = response.json()

        job_progress = self._get_progress(response_json, total_tasks)
        time_progress = self._get_time_progress(response_json, expected_time)
        error = job_progress - time_progress

        timestamp = datetime.datetime.fromtimestamp(time.time())

        return timestamp, 100 * error
