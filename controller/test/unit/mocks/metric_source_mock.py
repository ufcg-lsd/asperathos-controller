# Copyright (c) 2017 UFCG-LSD.
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

from datetime import datetime

"""
Class that represents a mock of the MetricSource object
"""
class MetricSourceMock():
    """ Constructor of the mock of a MetricSource object
    
    Returns:
        MockRedis: The simulation of a MetricSource object
    """
    def __init__(self, timestamp, error):
        self.timestamp = datetime.strptime(
                    timestamp,'%Y-%m-%dT%H:%M:%S.%fZ')

        self.error = error

    """
    Simulate the behavior of the function get_most_recent_value
    of MetricSource.
    Return:
        number_of_replicas(Integer)
    """
    def get_most_recent_value(self, application_id):
        return (self.timestamp, self.error)