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

from controller.plugins.metric_source.monasca.plugin import MonascaMetricSource
from controller.plugins.metric_source.nop.plugin import NopMetricSource
from controller.plugins.metric_source.spark.plugin import SparkMetricSource
from controller.plugins.metric_source.redis.plugin import RedisMetricSource
from controller.plugins.metric_source.openstack_generic.plugin import (
    OpenstackGenericMetricSource
)


class MetricSourceBuilder:
    def get_metric_source(self, name, parameters):
        if name == "monasca":
            return MonascaMetricSource(parameters)

        elif name == "nop":
            return NopMetricSource()
        elif name == "spark":
            return SparkMetricSource(parameters)
        elif name == "openstack_generic":
            return OpenstackGenericMetricSource(parameters)
        elif name == "redis":
            return RedisMetricSource(parameters)

        else:
            # FIXME: exception type
            raise Exception("Unknown metric source type")
