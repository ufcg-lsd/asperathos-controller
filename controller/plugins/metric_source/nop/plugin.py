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


class NopMetricSource:

    def get_most_recent_value(self, metric_name, options):
        return datetime.datetime.strptime("0001-01-01T00:00:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ'), 0