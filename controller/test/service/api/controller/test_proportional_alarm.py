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

import unittest
import datetime

from controller.plugins.metric_source.builder import MetricSourceBuilder
from controller.utils.locator.instance import InstanceLocator
from controller.utils.ssh import SSHUtils
from controller.utils.remote.kvm import RemoteKVM
from controller.plugins.actuator.kvm.plugin import KVMActuator
from controller.plugins.controller.proportional.alarm import ProportionalAlarm
from mock.mock import MagicMock


class TestProportionalAlarm(unittest.TestCase):

    def setUp(self):
        self.application_id_0 = "app-00"
        self.application_id_1 = "app-01"
        self.application_id_2 = "app-02"

        self.timestamp_1 = datetime.datetime.strptime("2000-01-01T00:00:00.0Z",
                                                      '%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_2 = datetime.datetime.strptime("2000-01-01T00:05:00.0Z",
                                                      '%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_3 = datetime.datetime.strptime("2000-01-01T00:10:00.0Z",
                                                      '%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_4 = datetime.datetime.strptime("2000-01-01T00:15:00.0Z",
                                                      '%Y-%m-%dT%H:%M:%S.%fZ')

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
        self.default_io_cap = 78

        self.bigsea_username = "username"
        self.bigsea_password = "password"
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
        self.actuator = KVMActuator(self.instance_locator, self.remote_kvm,
                                    # self.authorization_data,
                                    self.default_io_cap)

        self.proportional_factor = 1
        self.factor_up = 1
        self.factor_down = 0.5
        self.heuristic_options_error_proportional = {
            "heuristic_name": "error_proportional",
            "proportional_factor": self.proportional_factor}
        self.heuristic_options_error_proportional_up_down = \
            {"heuristic_name": "error_proportional_up_down",
             "factor_up": self.factor_up,
             "factor_down": self.factor_down}

        self.progress_error = {
            self.application_id_0: -20.0,
            self.application_id_1: 0.00,
            self.application_id_2: 30.0}

        self.timestamps = [self.timestamp_1, self.timestamp_2,
                           self.timestamp_3, self.timestamp_4]

    # normal cases
    # application 0 -> job progress < time progress -> scale up
    # application 1 -> job progress = time progress -> do nothing
    # application 2 -> job progress > time progress -> scale down

    def metrics(self, metric_name, options):
        application_id = options["application_id"]

        if metric_name == ProportionalAlarm.ERROR_METRIC_NAME:
            return self.timestamp_1, self.progress_error[application_id]

    def metrics_different_timestamps(self, metric_name, options):
        application_id = options["application_id"]

        timestamp = self.timestamps.pop(0)

        if metric_name == ProportionalAlarm.ERROR_METRIC_NAME:
            return timestamp, self.progress_error[application_id]

    def test_alarm_gets_metrics_and_scales_down_error_proportional(self):
        #
        # Case 1: normal scale down
        #
        proportional_factor = 1
        heuristic_options = {"heuristic_name": "error_proportional",
                             "proportional_factor": proportional_factor}

        self.alarm = ProportionalAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            heuristic_options,
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        # Remove resources
        error = self.metrics(ProportionalAlarm.ERROR_METRIC_NAME,
                             {"application_id": self.application_id_2})[1]
        new_cap = self.allocated_resources - self.proportional_factor * error
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Case 2: calculated cap is too low. Use min cap instead
        #
        proportional_factor = 3
        heuristic_options = {"heuristic_name": "error_proportional",
                             "proportional_factor": proportional_factor}

        self.alarm = ProportionalAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            heuristic_options,
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        # Remove resources
        new_cap = self.min_cap
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    def test_alarm_gets_metrics_and_scales_up_error_proportional(self):
        #
        # Case 1: normal scale up
        #
        proportional_factor = 1
        heuristic_options = {"heuristic_name": "error_proportional",
                             "proportional_factor": proportional_factor}

        self.alarm = ProportionalAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            heuristic_options,
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        # Add resources
        error = self.metrics(ProportionalAlarm.ERROR_METRIC_NAME,
                             {"application_id": self.application_id_0})[1]
        new_cap = self.allocated_resources + proportional_factor * abs(error)
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Case 2: calculated cap is too high. Use max cap instead
        #
        proportional_factor = 3
        heuristic_options = {"heuristic_name": "error_proportional",
                             "proportional_factor": proportional_factor}

        self.alarm = ProportionalAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            heuristic_options,
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        # Add resources
        new_cap = self.max_cap
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    def test_alarm_does_nothing(self):
        proportional_factor = 1
        heuristic_options = {"heuristic_name": "error_proportional",
                             "proportional_factor": proportional_factor}

        self.alarm = ProportionalAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            heuristic_options,
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_1})

        # The method doesn't try to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_not_called()
        # The method doesn't try to adjust the amount of resources
        self.actuator.adjust_resources.assert_not_called()

    def test_alarm_does_not_reuse_metrics_with_same_timestamp(self):
        proportional_factor = 1
        heuristic_options = {"heuristic_name": "error_proportional",
                             "proportional_factor": proportional_factor}

        self.alarm = ProportionalAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            heuristic_options,
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        # Add resources
        error = self.metrics(ProportionalAlarm.ERROR_METRIC_NAME,
                             {"application_id": self.application_id_0})[1]
        new_cap = self.allocated_resources + proportional_factor * abs(error)
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_0})

        # The method doesn't try to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster.assert_not_called()
        # The method doesn't try to adjust the amount of resources
        self.actuator.adjust_resources.assert_not_called()

    def test_alarm_metrics_with_different_timestamps(self):
        proportional_factor = 1
        heuristic_options = {"heuristic_name": "error_proportional",
                             "proportional_factor": proportional_factor}

        self.alarm = ProportionalAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            heuristic_options,
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        # Remove resources
        error = self.metrics(ProportionalAlarm.ERROR_METRIC_NAME,
                             {"application_id": self.application_id_2})[1]
        new_cap = self.allocated_resources - self.proportional_factor * error
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        # Remove resources

        error = self.metrics(ProportionalAlarm.ERROR_METRIC_NAME,
                             {"application_id": self.application_id_2})[1]
        new_cap = self.allocated_resources - self.proportional_factor * error
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    def test_alarm_gets_metrics_and_scales_down_error_proportional_up_down(
            self):
        #
        # Case 1: normal scale down
        #
        heuristic_options = {"heuristic_name": "error_proportional_up_down",
                             "factor_up": self.factor_up,
                             "factor_down": self.factor_down}

        self.alarm = ProportionalAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            heuristic_options,
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        # Remove resources
        error = self.metrics(ProportionalAlarm.ERROR_METRIC_NAME,
                             {"application_id": self.application_id_2})[1]
        new_cap = self.allocated_resources - self.factor_down * error
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Case 2: calculated cap is too low. Use min cap instead
        #
        factor_down = 5
        heuristic_options = {"heuristic_name": "error_proportional_up_down",
                             "factor_up": self.factor_up,
                             "factor_down": factor_down}

        self.alarm = ProportionalAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            heuristic_options,
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        # Remove resources
        new_cap = self.min_cap
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources\
            .assert_called_once_with(
                {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    def test_alarm_gets_metrics_and_scales_up_error_proportional_up_down(self):
        #
        # Case 1: normal scale up
        #
        heuristic_options = {"heuristic_name": "error_proportional_up_down",
                             "factor_up": self.factor_up,
                             "factor_down": self.factor_down}

        self.alarm = ProportionalAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            heuristic_options,
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        # Add resources
        error = self.metrics(ProportionalAlarm.ERROR_METRIC_NAME,
                             {"application_id": self.application_id_0})[1]
        new_cap = self.allocated_resources + self.factor_up * abs(error)
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Case 2: calculated cap is too high. Use max cap instead
        #
        factor_up = 5
        heuristic_options = {"heuristic_name": "error_proportional_up_down",
                             "factor_up": factor_up,
                             "factor_down": self.factor_down}

        self.alarm = ProportionalAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            heuristic_options,
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
        self.metric_source.get_most_recent_value.\
            assert_any_call(ProportionalAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)
        # Add resources
        new_cap = self.max_cap
        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})


if __name__ == "__main__":
    unittest.main()
