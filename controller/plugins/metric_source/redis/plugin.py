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

import ast
import datetime
import redis

from controller.plugins.metric_source.base import MetricSource


class RedisMetricSource(MetricSource):
    def __init__(self, parameters):
        print parameters['redis_ip'], parameters['redis_port']
        self.rds = redis.StrictRedis(host=parameters['redis_ip'],
                                     port=parameters['redis_port'])
        self.last_metric = 0.0
        self.last_timestamp = datetime.datetime.now()

    def get_most_recent_value(self, app_id):
        measurement = self.rds.rpop("%s:metrics" % app_id)
        print "\n%s\n%s\n\n" % (measurement, app_id)
        if measurement is not None:
            measurement = ast.literal_eval(measurement)
            timestamp = datetime.datetime.fromtimestamp(
                measurement['timestamp']/1000)
            value = float(measurement['value'])
            if timestamp > self.last_timestamp:
                self.last_timestamp = timestamp
                self.last_metric = value
                return timestamp, 100 * value
            else:
                return self.last_timestamp, 100 * self.last_metric
        else:
            return self.last_timestamp, 100 * self.last_metric