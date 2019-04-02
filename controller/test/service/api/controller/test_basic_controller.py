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

import ConfigParser
from mock.mock import MagicMock
import time
import unittest

from controller.plugins.controller.basic.plugin import BasicController
from controller.plugins.metric_source.builder import MetricSourceBuilder
from controller.plugins.actuator.builder import ActuatorBuilder


class TestBasicController(unittest.TestCase):

    CHECK_INTERVAL = 1

    def config_values(self, section, option):
        values = {
            "check_interval": self.CHECK_INTERVAL,
            "trigger_down": 10,
            "trigger_up": 10,
            "min_cap": 10,
            "max_cap": 100,
            "actuation_size": 20}

        if section == "scaling":
            if option in values.keys():
                return values[option]
        return None

    def setUp(self):
        config = ConfigParser.RawConfigParser()
        config.get = MagicMock()
        config.get.side_effect = self.config_values

        self.bigsea_username = "username"
        self.bigsea_password = "password"

        scaling_parameters = {
            "check_interval": self.CHECK_INTERVAL,
            "trigger_down": 10,
            "trigger_up": 10,
            "min_cap": 10,
            "max_cap": 100,
            "actuation_size": 20,
            "metric_rounding": 2}

        parameters = {"scaling_parameters": scaling_parameters,
                      "bigsea_username": self.bigsea_username,
                      "bigsea_password": self.bigsea_password}

        metric_source = MetricSourceBuilder().get_metric_source("nop", {})
        actuator = ActuatorBuilder().get_actuator("nop", parameters)

        self.controller = BasicController(
            metric_source, actuator, scaling_parameters)
        self.application_id_1 = "app-01"
        self.application_id_2 = "app-02"
        self.instance_1 = "instance-1"
        self.instance_2 = "instance-2"
        self.instances_1 = [self.instance_1, self.instance_2]
        self.instances_2 = [self.instance_2]
        self.parameters_1 = {"instances": self.instances_1}
        self.parameters_2 = {"instances": self.instances_2}

    def tearDown(self):
        self.controller.stop_controller()

    def test_start_application_scaling_1_application(self):
        self.controller.alarm.check_application_state = MagicMock(
            return_value=None)

        # Start application scaling
        self.controller.start_application_scaling(
            self.application_id_1, self.parameters_1)

        # Check applications list content
        self.assertEqual(len(self.controller.applications.items()), 1)
        self.assertTrue(self.application_id_1 in self.controller.applications)
        application_1_parameters = self.controller.applications.get(
            self.application_id_1)

        self.assertEqual(application_1_parameters.get(
            "instances"), self.instances_1)

        # Sleep to assure the calls to alarm and stop the controller
        time.sleep(float(2 * self.CHECK_INTERVAL))

        # Check if the alarm was called correctly
        self.controller.alarm.check_application_state.assert_called_with(
            self.application_id_1, self.instances_1)

    def test_start_application_scaling_2_applications(self):
        self.controller.alarm.check_application_state = MagicMock(
            return_value=None)

        # Start application scaling
        self.controller.start_application_scaling(
            self.application_id_1, self.parameters_1)
        self.controller.start_application_scaling(
            self.application_id_2, self.parameters_2)

        # Check applications list content
        self.assertEqual(len(self.controller.applications.items()), 2)

        # Check application 1
        self.assertTrue(self.application_id_1 in self.controller.applications)
        application_1_parameters = self.controller.applications.get(
            self.application_id_1)

        self.assertEqual(application_1_parameters.get(
            "instances"), self.instances_1)

        # Check application 2
        self.assertTrue(self.application_id_2 in self.controller.applications)
        application_2_parameters = self.controller.applications.get(
            self.application_id_2)

        self.assertEqual(application_2_parameters.get(
            "instances"), self.instances_2)

        # Sleep to assure the calls to alarm and stop the controller
        time.sleep(float(2 * self.CHECK_INTERVAL))

        # Check if the alarm was called correctly
        self.controller.alarm.check_application_state.assert_any_call(
            self.application_id_1, self.instances_1)
        self.controller.alarm.check_application_state.assert_any_call(
            self.application_id_2, self.instances_2)

    def test_stop_application_scaling(self):
        self.controller.alarm.check_application_state = MagicMock(
            return_value=None)
        self.controller.applications = {
            self.application_id_1: self.parameters_1,
            self.application_id_2: self.parameters_2}

        # Stop scaling for application 1
        self.controller.stop_application_scaling(self.application_id_1)

        # Check applications list content
        self.assertEqual(len(self.controller.applications.items()), 1)

        # Check application 2
        self.assertTrue(self.application_id_2 in self.controller.applications)
        application_2_parameters = self.controller.applications.get(
            self.application_id_2)

        self.assertEqual(application_2_parameters.get(
            "instances"), self.instances_2)

        # Stop scaling for application 2
        self.controller.stop_application_scaling(self.application_id_2)

        # Check applications list content
        self.assertEqual(len(self.controller.applications.items()), 0)


if __name__ == "__main__":
    unittest.main()
