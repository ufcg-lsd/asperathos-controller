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
from controller.plugins.controller.generic.alarm import GenericAlarm
from controller.utils.ssh import SSHUtils
from controller.plugins.actuator.kvm.plugin import KVMActuator
from controller.utils.locator.instance import InstanceLocator
from controller.utils.remote.kvm import RemoteKVM


class TestGenericAlarm(unittest.TestCase):

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
        self.actuation_size = 10.0
        self.allocated_resources = 50
        self.metric_round = 2
        self.default_io_cap = 45

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

        self.timestamps = [self.timestamp_1, self.timestamp_2,
                           self.timestamp_3, self.timestamp_4]

    def metrics(self, metric_name, options):
        application_id = options["application_id"]

        progress_error = {
            self.application_id_0: -50.0,
            self.application_id_1: 0.00,
            self.application_id_2: 50.0,
            self.application_id_3: -9.996,
            self.application_id_4: 29.997}

        if metric_name == GenericAlarm.ERROR_METRIC_NAME:
            return self.timestamp_1, progress_error[application_id]

    def metrics_different_timestamps(self, metric_name, options):
        application_id = options["application_id"]

        progress_error = {
            self.application_id_0: -50.0,
            self.application_id_1: 0.00,
            self.application_id_2: 50.0,
            self.application_id_3: -9.996,
            self.application_id_4: 29.997}

        timestamp = self.timestamps.pop(0)

        if metric_name == GenericAlarm.ERROR_METRIC_NAME:
            return timestamp, progress_error[application_id]

    def test_alarm_gets_metrics_and_scales_down(self):
        self.alarm = GenericAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.actuation_size,
            self.metric_round,
            self.application_id_2,
            self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)

        self.alarm.check_application_state()

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(
            GenericAlarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_2
                })

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        # Remove resources
        new_cap = self.allocated_resources - self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    def test_alarm_gets_metrics_and_scales_up(self):
        self.alarm = GenericAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.actuation_size,
            self.metric_round,
            self.application_id_0,
            self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)

        self.alarm.check_application_state()

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(
            GenericAlarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_0
                })

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        # Add resources
        new_cap = self.allocated_resources + self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    def test_alarm_does_nothing(self):
        self.alarm = GenericAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.actuation_size,
            self.metric_round,
            self.application_id_1,
            self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)

        self.alarm.check_application_state()

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(
            GenericAlarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_1
                })

        # The method doesn't try to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_not_called()
        # The method doesn't try to adjust the amount of resources
        self.actuator.adjust_resources.assert_not_called()

    def test_alarm_metric_rounding(self):
        #
        # The metrics are rounded to 2 digits from the decimal point
        # There should be scale up and down in these cases
        #
        self.alarm = GenericAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.actuation_size,
            2,
            self.application_id_3,
            self.instances)

        # Scale up
        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)

        self.alarm.check_application_state()

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(
            GenericAlarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_3
                })

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        new_cap = self.allocated_resources + self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        # Scale down
        # Set up mocks
        self.alarm = GenericAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.actuation_size,
            2,
            self.application_id_4,
            self.instances)

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)

        self.alarm.check_application_state()

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(
            GenericAlarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_4
                })

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        new_cap = self.allocated_resources - self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # The metrics are rounded to 3 digits from the decimal point
        # There should not be scale up and down in these cases
        #
        self.alarm = GenericAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.actuation_size,
            3,
            self.application_id_3,
            self.instances)

        # Scale up
        # Start up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)

        self.alarm.check_application_state()

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(
            GenericAlarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_3
                })

        # The method doesn't try to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_not_called()
        # The method doesn't try to adjust the amount of resources
        self.actuator.adjust_resources.assert_not_called()

        # Scale down
        # Start up mocks
        self.alarm = GenericAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.actuation_size,
            3,
            self.application_id_4,
            self.instances)

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)

        self.alarm.check_application_state()

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(
            GenericAlarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_4
                })

        # The method doesn't try to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_not_called()
        # The method doesn't try to adjust the amount of resources
        self.actuator.adjust_resources.assert_not_called()

    def test_alarm_does_not_reuse_metrics_with_same_timestamp(self):
        self.alarm = GenericAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.actuation_size,
            2,
            self.application_id_0,
            self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)

        self.alarm.check_application_state()

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(
            GenericAlarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_0
                })

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        # Add resources
        new_cap = self.allocated_resources + self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # 2nd call. The method checks if the metric is new and does not act
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)

        self.alarm.check_application_state()

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(
            GenericAlarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_0
                })

        # The method doesn't try to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_not_called()
        # The method doesn't try to adjust the amount of resources
        self.actuator.adjust_resources.assert_not_called()

    def test_alarm_metrics_with_different_timestamps(self):
        self.alarm = GenericAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.actuation_size,
            3,
            self.application_id_2,
            self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value\
            .side_effect = self.metrics_different_timestamps

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)

        self.alarm.check_application_state()

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(
            GenericAlarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_2
                })

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        # Remove resources
        new_cap = self.allocated_resources - self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # 2nd call. The method checks if the metric is new and acts
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value\
            .side_effect = self.metrics_different_timestamps

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = MagicMock(
            return_value=self.allocated_resources)

        self.alarm.check_application_state()

        # The method tries to get the metrics correctly
        self.metric_source.get_most_recent_value.assert_any_call(
            GenericAlarm.ERROR_METRIC_NAME, {
                "application_id": self.application_id_2
                })

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        # Remove resources
        new_cap = self.allocated_resources - self.actuation_size
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})


if __name__ == "__main__":
    unittest.main()
