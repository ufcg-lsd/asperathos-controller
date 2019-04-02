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
from controller.plugins.controller.pid.alarm import PIDAlarm
from mock import MagicMock


class TestPIDAlarm(unittest.TestCase):

    def setUp(self):
        self.application_id_0 = "app-00"
        self.application_id_1 = "app-01"
        self.application_id_2 = "app-02"
        self.application_id_3 = "app-03"
        self.application_id_4 = "app-04"
        self.application_id_5 = "app-05"
        self.application_id_6 = "app-06"
        self.application_id_7 = "app-07"
        self.application_id_8 = "app-08"
        self.application_id_9 = "app-09"

        self.timestamp_1 = datetime.datetime.strptime("2000-01-01T00:00:00.0Z",
                                                      "%Y-%m-%dT%H:%M:%S.%fZ")
        self.timestamp_2 = datetime.datetime.strptime("2000-01-01T00:05:00.0Z",
                                                      "%Y-%m-%dT%H:%M:%S.%fZ")
        self.timestamp_3 = datetime.datetime.strptime("2000-01-01T00:10:00.0Z",
                                                      "%Y-%m-%dT%H:%M:%S.%fZ")
        self.timestamp_4 = datetime.datetime.strptime("2000-01-01T00:15:00.0Z",
                                                      "%Y-%m-%dT%H:%M:%S.%fZ")

        self.timestamps = [self.timestamp_1, self.timestamp_2,
                           self.timestamp_3, self.timestamp_4]

        self.instance_name_1 = "instance1"
        self.instance_name_2 = "instance2"
        self.instances = [self.instance_name_1, self.instance_name_2]

        self.trigger_down = 0.0
        self.trigger_up = 0.0
        self.min_cap = 10.0
        self.max_cap = 100.0
        self.actuation_size = 10.0
        self.allocated_resources_scale_down = 100
        self.allocated_resources_scale_up = 10
        self.metric_round = 2
        self.default_io_cap = 34

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
        self.actuator = KVMActuator(self.instance_locator,
                                    self.remote_kvm,
                                    # self.authorization_data,
                                    self.default_io_cap)

        self.proportional_factor = 1.5
        self.derivative_factor = 0.5
        self.integrative_factor = 1.5

        self.heuristic_options = {
            "heuristic_name": "error_pid",
            "proportional_factor": self.proportional_factor,
            "derivative_factor": self.derivative_factor,
            "integrative_factor": self.integrative_factor}

        self.progress_error = {
            # CASE 1
            self.application_id_0: {self.timestamp_1: -30.0,
                                    self.timestamp_2: -20.0,
                                    self.timestamp_3: -15.0},

            # CASE 2
            self.application_id_1: {self.timestamp_1: -30.0,
                                    self.timestamp_2: -40.0,
                                    self.timestamp_3: -60.0},

            # CASE 3
            self.application_id_2: {self.timestamp_1: 30.0,
                                    self.timestamp_2: 20.0,
                                    self.timestamp_3: 15.0},

            # CASE 4
            self.application_id_3: {self.timestamp_1: 30.0,
                                    self.timestamp_2: 40.0,
                                    self.timestamp_3: 55.0},

            # CASE 5
            self.application_id_4: {self.timestamp_1: 100.0,
                                    self.timestamp_2: 100.0,
                                    self.timestamp_3: 100.0},

            # CASE 6
            self.application_id_5: {self.timestamp_1: -100.0,
                                    self.timestamp_2: -100.0,
                                    self.timestamp_3: -100.0},

            # CASE 7
            self.application_id_6: {
                                    self.timestamp_1: -30.0,
                                    self.timestamp_2: 10.0,
                                    self.timestamp_3: 30.0},

            # CASE 8
            self.application_id_7: {
                                    self.timestamp_1: -5.0,
                                    self.timestamp_2: -1.0,
                                    self.timestamp_3: 2.0},

            # CASE 9
            self.application_id_8: {
                                    self.timestamp_1: -10.0,
                                    self.timestamp_2: -5.0,
                                    self.timestamp_3: 20.0,
                                    self.timestamp_4: -5.0},

            # CASE 10
            self.application_id_9: {
                                    self.timestamp_1: -10.0,
                                    self.timestamp_2: 0.0,
                                    self.timestamp_3: 10.0,
                                    self.timestamp_4: 5.0}
        }

    def metrics(self, metric_name, options):
        application_id = options["application_id"]

        timestamp_to_use = self.timestamps.pop(0)

        if metric_name == PIDAlarm.ERROR_METRIC_NAME:
            return timestamp_to_use,\
                self.progress_error[application_id][timestamp_to_use]

    '''

        CASE 1
        The error is always negative and its absolute value
        decreases throughout the execution
        The derivative component decreases the proportional effect
        Uses application_id_0 progress

    '''

    def test_alarm_gets_metrics_and_scales_up_decreasing_error(self):
        self.heuristic_options = {
            "heuristic_name": "error_pid",
            "proportional_factor": self.proportional_factor,
            "derivative_factor": self.derivative_factor,
            "integrative_factor": 0}

        self.alarm = PIDAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            self.heuristic_options,
            self.application_id_0,
            self.instances)

        #
        # First call - there is no derivative effect - timestamp_1
        # Proportional effect = 45
        # Derivative effect = 0
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_up + 45

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        # Proportional effect = 30
        # Derivative effect = -5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_up + 25

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Third call - timestamp_3
        # Proportional effect = 22.5
        # Derivative effect = -2.5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_0})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_up + 20

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    '''

       CASE 2

       The error is always negative and its absolute value
       increases throughout the execution
       The derivative component increases the proportional effect
       Uses application_id_1 progress

    '''

    def test_alarm_gets_metrics_and_scales_up_increasing_error(self):
        #
        # First call - there is no derivative effect - timestamp_1
        # Proportional effect = 45
        # Derivative effect = 0
        #
        self.heuristic_options = {
            "heuristic_name": "error_pid",
            "proportional_factor": self.proportional_factor,
            "derivative_factor": self.derivative_factor,
            "integrative_factor": 0}

        self.alarm = PIDAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            self.heuristic_options,
            self.application_id_1,
            self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_1})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_up + 45

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        # Proportional effect = 60
        # Derivative effect = 5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_1})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_up + 65

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Third call - timestamp_3
        # Proportional effect = 90
        # Derivative effect = 10
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_1})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_up + 90

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    '''

       CASE 3

       The error is always positive and its absolute value
       decreases throughout the execution
       The derivative component decreases the proportional effect
       Uses application_id_2 progress

    '''

    def test_alarm_gets_metrics_and_scales_down_decreasing_error(self):
        #
        # First call - there is no derivative effect - timestamp_1
        # Proportional effect = -45
        # Derivative effect = 0
        #
        self.heuristic_options = {
            "heuristic_name": "error_pid",
            "proportional_factor": self.proportional_factor,
            "derivative_factor": self.derivative_factor,
            "integrative_factor": 0}

        self.alarm = PIDAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            self.heuristic_options,
            self.application_id_2,
            self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_down - 45

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        # Proportional effect = -30
        # Derivative effect = 5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_down - 25

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Third call - timestamp_3
        # Proportional effect = -22.5
        # Derivative effect = 2.5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_2})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_down - 20

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    '''

       CASE 4

       The error is always positive and its absolute value
       increases throughout the execution
       The derivative component increases the proportional effect
       Uses application_id_3 progress

    '''

    def test_alarm_gets_metrics_and_scales_down_increasing_error(self):
        #
        # First call - there is no derivative effect - timestamp_1
        # Proportional effect = -45
        # Derivative effect = 0
        #
        self.heuristic_options = {
            "heuristic_name": "error_pid",
            "proportional_factor": self.proportional_factor,
            "derivative_factor": self.derivative_factor,
            "integrative_factor": 0}

        self.alarm = PIDAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            self.heuristic_options,
            self.application_id_3,
            self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_3})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_down - 45

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        # Proportional effect = -60
        # Derivative effect = -5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_3})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_down - 65

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Third call - timestamp_3
        # Proportional effect = -82.5
        # Derivative effect = -7.5
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_3})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_down - 90

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    '''

       CASE 5

       The error value is set to force the use of the
       minimum possible cap value
       Uses application_id_4 progress

    '''

    def test_alarm_scale_down_limits(self):
        #
        # First call - there is no derivative effect - timestamp_1
        #
        self.heuristic_options = {
            "heuristic_name": "error_pid",
            "proportional_factor": self.proportional_factor,
            "derivative_factor": self.derivative_factor,
            "integrative_factor": 0}

        self.alarm = PIDAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            self.heuristic_options,
            self.application_id_4,
            self.instances)

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_4})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.min_cap

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_4})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.min_cap

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    '''

       CASE 6

       The error value is set to force the use of the
       maximum possible cap value
       Uses application_id_5 progress

    '''

    def test_alarm_scale_up_limits(self):
        #
        # First call - there is no derivative effect - timestamp_1
        #
        self.heuristic_options = {
            "heuristic_name": "error_pid",
            "proportional_factor": self.proportional_factor,
            "derivative_factor": self.derivative_factor,
            "integrative_factor": 0}

        self.alarm = PIDAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            self.heuristic_options,
            self.application_id_5,
            self.instances)

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_5})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.max_cap

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_5})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.max_cap

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    '''

       CASE 7

       The error is negative in the first call and
       positive in the following calls.
       Uses application_id_6 progress

    '''

    def test_alarm_negative_to_positive_error(self):
        #
        # First call - there is no derivative effect - timestamp_1
        # Proportional effect = 45
        # Derivative effect = 0
        self.heuristic_options = {
            "heuristic_name": "error_pid",
            "proportional_factor": self.proportional_factor,
            "derivative_factor": self.derivative_factor,
            "integrative_factor": 0}

        self.alarm = PIDAlarm(
            self.actuator,
            self.metric_source,
            0,
            0,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            self.heuristic_options,
            self.application_id_6,
            self.instances)

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_6})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_up + 45

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        # Proportional effect = -15
        # Derivative effect = -20
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_6})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_down - 35

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Third call - timestamp_3
        # Proportional effect = -45
        # Derivative effect = -10
        #

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_6})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_down - 55

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    '''

       CASE 8

       The error is negative in the two first calls and
       positive in the following calls.
       Uses application_id_7 progress

    '''

    def test_alarm_smoothly_negative_to_positive_error(self):
        #
        # First call - there is no derivative effect - timestamp_1
        # Proportional effect = 7.5
        # Derivative effect = 0
        #
        self.heuristic_options = {
            "heuristic_name": "error_pid",
            "proportional_factor": self.proportional_factor,
            "derivative_factor": self.derivative_factor,
            "integrative_factor": 0}

        self.alarm = PIDAlarm(
            self.actuator,
            self.metric_source,
            0,
            0,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            self.heuristic_options,
            self.application_id_7,
            self.instances)

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_7})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_up + 7.5

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Second call - timestamp_2
        # Proportional effect = 1.5
        # Derivative effect = -2.0
        #

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_7})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_down - 0.5

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        #
        # Third call - timestamp_3
        # Proportional effect = -3.0
        # Derivative effect = -1.5
        #

        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_down)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_7})

        # The method tries to get the amount of allocated resources
        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        new_cap = self.allocated_resources_scale_down - 4.5

        # The method tries to adjust the amount of resources
        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    '''

       CASE 9

       The proportional and derivative components are equal to zero.
       The error is negative in the two first calls, positive in the third and
       negative in the last one.

       Uses application_id_8 progress

    '''

    def test_integrative_only(self):

        # First call

        self.proportional_factor = 0.0
        self.derivative_factor = 0.0
        self.allocated_resources_scale_up = 30

        self.heuristic_options = {
            "heuristic_name": "error_pid",
            "proportional_factor": self.proportional_factor,
            "derivative_factor": self.derivative_factor,
            "integrative_factor": self.integrative_factor}

        self.alarm = PIDAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            self.heuristic_options,
            self.application_id_8,
            self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_8})

        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        # Accumulated error is negative, therefore scale up
        new_cap = self.allocated_resources_scale_up + 15

        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        # Second call

        # Set up mocks
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_8})

        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        # Accumulated error is negative, therefore scale up
        new_cap = self.allocated_resources_scale_up + 22.5

        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        # Third call

        # Set up mocks
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_8})

        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        # Accumulated error is positive, therefore scale down
        new_cap = self.allocated_resources_scale_up - 7.5

        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        # Fourth call

        # Set up mocks
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_8})

        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        # Accumulated error is zero, therefore do not scale
        new_cap = self.allocated_resources_scale_up

        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

    '''

       CASE 10 - Tests interaction between the proportional, derivative
       and integrative algorithms

       Uses application_id_9 progress

    '''

    def test_proportional_derivative_integrative(self):
        self.heuristic_options = {
            "heuristic_name": "error_pid",
            "proportional_factor": self.proportional_factor,
            "derivative_factor": self.derivative_factor,
            "integrative_factor": self.integrative_factor}

        self.alarm = PIDAlarm(
            self.actuator,
            self.metric_source,
            self.trigger_down,
            self.trigger_up,
            self.min_cap,
            self.max_cap,
            self.metric_round,
            self.heuristic_options,
            self.application_id_9,
            self.instances)

        # Set up mocks
        self.metric_source.get_most_recent_value = MagicMock()
        self.metric_source.get_most_recent_value.side_effect = self.metrics

        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_9})

        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        proportional_component = 15
        derivative_component = 0
        integrative_component = 15
        component_sum = proportional_component + \
            derivative_component + integrative_component

        new_cap = min(max(self.allocated_resources_scale_up +
                          component_sum, self.min_cap), self.max_cap)

        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        # Second call

        # Set up mocks
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_9})

        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        proportional_component = 0
        derivative_component = -5
        integrative_component = 15
        component_sum = proportional_component + \
            derivative_component + integrative_component

        new_cap = min(max(self.allocated_resources_scale_up +
                          component_sum, self.min_cap), self.max_cap)

        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        # Third call

        # Set up mocks
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_9})

        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        proportional_component = -15
        derivative_component = -5
        integrative_component = 0
        component_sum = proportional_component + \
            derivative_component + integrative_component

        new_cap = min(max(self.allocated_resources_scale_up +
                          component_sum, self.min_cap), self.max_cap)

        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})

        # Fourth call

        # Set up mocks
        self.actuator.adjust_resources = MagicMock(return_value=None)
        self.actuator.get_allocated_resources_to_cluster = \
            MagicMock(return_value=self.allocated_resources_scale_up)

        self.alarm.check_application_state()

        self.metric_source.get_most_recent_value.\
            assert_any_call(PIDAlarm.ERROR_METRIC_NAME,
                            {"application_id": self.application_id_9})

        self.actuator.get_allocated_resources_to_cluster\
            .assert_called_once_with(
                self.instances)

        proportional_component = -7.5
        derivative_component = 2.5
        integrative_component = -7.5
        component_sum = proportional_component + \
            derivative_component + integrative_component

        new_cap = min(max(self.allocated_resources_scale_up +
                          component_sum, self.min_cap), self.max_cap)

        self.actuator.adjust_resources.assert_called_once_with(
            {self.instance_name_1: new_cap, self.instance_name_2: new_cap})


if __name__ == "__main__":
    unittest.main()
