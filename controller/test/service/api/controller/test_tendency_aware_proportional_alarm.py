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
import unittest

from mock.mock import MagicMock
from controller.plugins.metric_source.builder import MetricSourceBuilder
from controller.utils.locator.instance import InstanceLocator
from controller.utils.ssh import SSHUtils
from controller.utils.remote.kvm import RemoteKVM
from controller.plugins.actuator.kvm.plugin import KVMActuator
from controller.plugins.controller.tendency.alarm \
    import TendencyAwareProportionalAlarm


class TestTendencyAwareProportionalAlarm(unittest.TestCase):

    def setUp(self):
        self.application_id_0 = "app-00"
        self.application_id_1 = "app-01"
        self.application_id_2 = "app-02"
        self.application_id_3 = "app-03"
        self.application_id_4 = "app-04"

        self.timestamp_1 = datetime.datetime.strptime(
            "2000-01-01T00:00:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_2 = datetime.datetime.strptime(
            "2000-01-01T00:05:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_3 = datetime.datetime.strptime(
            "2000-01-01T00:10:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_4 = datetime.datetime.strptime(
            "2000-01-01T00:15:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')

        self.instance_name_1 = "instance1"
        self.instance_name_2 = "instance2"
        self.instances = [self.instance_name_1, self.instance_name_2]

        self.trigger_down = 30.0
        self.trigger_up = 10.0
        self.min_cap = 10.0
        self.max_cap = 100.0
        self.allocated_resources = 50
        self.metric_round = 2
        self.actuation_size = 25
        self.default_io_cap = 67

        # self.bigsea_username = "username"
        # self.bigsea_password = "password"
        # self.authorization_url = "authorization_url"
        # self.authorization_data = dict(
        #                                authorization_url=self.authorization_url,
        #                                bigsea_username=self.bigsea_username,
        #                                bigsea_password=self.bigsea_password)

        compute_nodes = []
        compute_nodes_key = "key"
        self.instances = [self.instance_name_1, self.instance_name_2]
        self.metric_source = MetricSourceBuilder().get_metric_source("nop", {})
        self.instance_locator = InstanceLocator(
            SSHUtils({}), compute_nodes, compute_nodes_key)
        self.remote_kvm = RemoteKVM(SSHUtils({}), compute_nodes_key)
        self.actuator = KVMActuator(self.instance_locator,
                                    self.remote_kvm,
                                    # self.authorization_data,
                                    self.default_io_cap)

        self.alarm = TendencyAwareProportionalAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.actuation_size,
            self.metric_round)

        self.timestamps = [self.timestamp_1, self.timestamp_2,
                           self.timestamp_3, self.timestamp_4]
        self.diff_values = {self.application_id_0: [10.0, 10.0],
                            self.application_id_1: [10.0, -5.0],
                            self.application_id_2: [0.0, 15.0]}

    def metric_values(self, metric_name, options):
        application_id = options["application_id"]
        timestamp = self.timestamps.pop(0)
        return timestamp, self.diff_values[application_id].pop(0)

    def test_alarm_base_case(self):
        # Base case
        # diff is null
        # difference is null
        # Do nothing

        # First call
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value\
            .side_effect = self.metric_values
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=None)
        self.actuator.adjust_resources = MagicMock(return_value=None)

        self.alarm.check_application_state(
            self.application_id_0, self.instances)

        self.metric_source.get_most_recent_value\
            .assert_any_call(
                             self.alarm.ERROR_METRIC_NAME,
                             {"application_id": self.application_id_0})
        self.actuator.get_allocated_resources_to_cluster.assert_not_called()
        self.actuator.adjust_resources.assert_not_called()

        # Second call
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value\
            .side_effect = self.metric_values
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=None)
        self.actuator.adjust_resources = MagicMock(return_value=None)

        self.alarm.check_application_state(
            self.application_id_0, self.instances)

        self.metric_source.get_most_recent_value\
            .assert_any_call(
                             self.alarm.ERROR_METRIC_NAME,
                             {"application_id": self.application_id_0})
        self.actuator.get_allocated_resources_to_cluster.assert_not_called()
        self.actuator.adjust_resources.assert_not_called()

    def test_case1(self):
        # Case 1
        # progress is ok. application performance is worse.
        # add more resources. how much?
        # First call
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value\
            .side_effect = self.metric_values
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=None)
        self.actuator.adjust_resources = MagicMock(return_value=None)

        self.alarm.check_application_state(
            self.application_id_1, self.instances)

        self.metric_source.get_most_recent_value\
            .assert_any_call(
                             self.alarm.ERROR_METRIC_NAME, {
                                "application_id": self.application_id_1
                                })
        self.actuator.get_allocated_resources_to_cluster.assert_not_called()
        self.actuator.adjust_resources.assert_not_called()

        # Second call
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value\
            .side_effect = self.metric_values
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)
        self.actuator.adjust_resources = MagicMock(return_value=None)

        self.alarm.check_application_state(
            self.application_id_1, self.instances)

        self.metric_source.get_most_recent_value.assert_any_call(
            self.alarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_1
                })

        self.actuator.get_allocated_resources_to_cluster.assert_any_call(
            self.instances)

        new_cap = self.allocated_resources + self.actuation_size
        self.actuator.adjust_resources.assert_any_call(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    def test_case2(self):
        # Case 2
        # progress is ok. application performance is improving.
        # remove resources. how much?
        # First call
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value\
            .side_effect = self.metric_values
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=None)
        self.actuator.adjust_resources = MagicMock(return_value=None)

        self.alarm.check_application_state(
            self.application_id_2, self.instances)

        self.metric_source.get_most_recent_value.assert_any_call(
            self.alarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_2
                })
        self.actuator.get_allocated_resources_to_cluster.assert_not_called()
        self.actuator.adjust_resources.assert_not_called()

        # Second call
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value\
            .side_effect = self.metric_values
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)
        self.actuator.adjust_resources = MagicMock(return_value=None)

        self.alarm.check_application_state(
            self.application_id_2, self.instances)

        self.metric_source.get_most_recent_value.assert_any_call(
            self.alarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_2
                })

        self.actuator.get_allocated_resources_to_cluster.assert_any_call(
            self.instances)

        new_cap = self.allocated_resources - self.actuation_size
        self.actuator.adjust_resources.assert_any_call(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})


if __name__ == "__main__":
    unittest.main()
