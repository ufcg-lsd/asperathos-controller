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

import copy
import threading
import unittest

from controller.exceptions import api as ex
from controller.plugins.controller.kubejobs.alarm import KubeJobs
from controller.plugins.controller.kubejobs.plugin import KubejobsController
from controller.test.unit.mocks.actuator_mock import ActuatorMock
from controller.test.unit.mocks.metric_source_mock import MetricSourceMock

"""
Class that tests the KubeJobsController components.
"""


class TestKubeJobsController(unittest.TestCase):

    """
    Set up KubeJobsController object.
    """

    def setUp(self):
        application_id = "000001"

        self.parameters = {
            "control_parameters": {
                "metric_source": "redis",
                "schedule_strategy": "default",
                "actuator": 'nop',
                "trigger_down": 1,
                "trigger_up": 1,
                "min_rep": 2,
                "max_rep": 10,
                "check_interval": 1,
                "actuation_size": 3},
            "redis_ip": "192.168.0.0",
            "redis_port": "5000",
            "application_id": application_id
        }

        self.kubejobs1 = KubeJobs(self.parameters)
        self.kubejobs1.metric_source = \
            MetricSourceMock("2018-11-26T15:00:00.000Z", -2)
        self.kubejobs1.actuator = ActuatorMock()

        self.controller = KubejobsController(application_id, self.parameters)
        self.controller.alarm = self.kubejobs1

    """
    """

    def tearDown(self):
        pass

    """
    Test that stop application works.
    """

    def test_start_stop_application(self):

        thread1 = threading.Thread(
            target=self.controller.start_application_scaling)
        thread1.start()

        self.assertTrue(self.controller.running)
        while thread1.is_alive():
            if self.controller.running:
                self.controller.stop_application_scaling()

        self.assertFalse(self.controller.running)

    """
    Test that the status returned is correct.
    """

    def test_status(self):

        self.assertEqual("", self.controller.status())

        thread1 = threading.Thread(
            target=self.controller.start_application_scaling)
        thread1.start()

        self.assertTrue(self.controller.running)
        while thread1.is_alive():
            if self.controller.running:
                self.controller.stop_application_scaling()

        self.assertEqual("Progress error-[2018-11-26 15:00:00]--2.000000",
                         self.controller.status())

    def test_wrong_request_body(self):

        """
        Asserts that a BadRequestException will occur if
        one of the parameters is missing
        Args: None
        Returns: None
        """
        application_id = "000002"
        request_error_counter = len(self.parameters["control_parameters"])
        for key in self.parameters["control_parameters"]:
            parameters_test = copy.deepcopy(self.parameters)
            del parameters_test["control_parameters"][key]
            try:
                KubejobsController(application_id, parameters_test)
            except ex.BadRequestException:
                request_error_counter -= 1

        self.assertEqual(request_error_counter, 1)
