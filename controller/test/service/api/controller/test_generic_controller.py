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

from mock.mock import MagicMock
import threading
import time
import unittest

from controller.plugins.controller.generic.plugin import GenericController


class TestGenericController(unittest.TestCase):

    def setUp(self):
        self.app_id_0 = "app-00"
        self.scaling_parameters = {}
        self.parameters = {}

        self.instance_1 = "instance-1"
        self.instance_2 = "instance-2"
        self.instances = [self.instance_1, self.instance_2]

        self.bigsea_username = "username"
        self.bigsea_password = "password"

        self.check_interval = 2
        self.trigger_down = 10
        self.trigger_up = 100
        self.min_cap = 10
        self.max_cap = 100
        self.actuation_size = 20
        self.metric_rounding = 2
        self.actuator = "nop"
        self.metric_source = "nop"

        self.scaling_parameters["instances"] = self.instances
        self.scaling_parameters["check_interval"] = self.check_interval
        self.scaling_parameters["trigger_down"] = self.trigger_down
        self.scaling_parameters["trigger_up"] = self.trigger_up
        self.scaling_parameters["min_cap"] = self.min_cap
        self.scaling_parameters["max_cap"] = self.max_cap
        self.scaling_parameters["actuation_size"] = self.actuation_size
        self.scaling_parameters["metric_rounding"] = self.metric_rounding
        self.scaling_parameters["actuator"] = self.actuator
        self.scaling_parameters["metric_source"] = self.metric_source

        self.parameters = {"scaling_parameters": self.scaling_parameters,
                           "bigsea_username": self.bigsea_username,
                           "bigsea_password": self.bigsea_password}

        self.controller = GenericController(
            self.app_id_0, self.scaling_parameters)

    def test_start_and_stop_scaling(self):
        self.controller.alarm.check_application_state = MagicMock(
            return_value=None)

        controller_thread = threading.Thread(
            target=self.controller.start_application_scaling)
        controller_thread.start()

        time.sleep(float(2 * self.check_interval))

        self.controller.alarm.check_application_state.assert_any_call()

        self.controller.stop_application_scaling()


if __name__ == "__main__":
    unittest.main()
