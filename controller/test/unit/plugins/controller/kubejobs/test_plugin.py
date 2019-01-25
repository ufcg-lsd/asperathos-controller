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

import unittest
import threading

from controller.plugins.controller.kubejobs.plugin import KubejobsController
from controller.test.unit.mocks.actuator_mock import ActuatorMock
from controller.test.unit.mocks.metric_source_mock import MetricSourceMock
from controller.plugins.controller.kubejobs.alarm import KubeJobs

"""
Class that tests the KubeJobsController components.
"""
class TestKubeJobsController(unittest.TestCase):

    """
    Set up KubeJobsController object.
    """    
    def setUp(self):
        parameters = {"control_parameters": {
                            "check_interval": 2,
                            "trigger_down": 1,
                            "trigger_up": 1,
                            "min_rep": 2,
                            "max_rep": 10,
                            "actuation_size": 3,
                            "actuator": "nop",
                            "metric_source": "redis",
                            "redis_ip": "192.168.0.0",
                            "redis_port": "5000"
                    },
                    "redis_ip": "192.168.0.0",
                    "redis_port": "5000"
        }
        
        application_id = "000001"

        metric_source_1 = MetricSourceMock("2018-11-26T15:00:00.000Z", -2)
        actuator = ActuatorMock()
        trigger_down = 1
        trigger_up = 1
        min_cap = 2
        max_cap = 10
        actuation_size = 3

        alarm = self.kubejobs1 = KubeJobs(actuator, metric_source_1,
                                trigger_down, trigger_up,
                                min_cap, max_cap,
                                actuation_size,
                                application_id)


        self.controller = KubejobsController(application_id, parameters)
        self.controller.alarm = alarm

    """
    """
    def tearDown(self):
        pass

    """
    Test that stop application works.
    """
    def test_start_stop_application(self):
        
        thread1 = threading.Thread(target=self.controller.start_application_scaling)
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

        thread1 = threading.Thread(target=self.controller.start_application_scaling)
        thread1.start()

        self.assertTrue(self.controller.running)
        while thread1.is_alive():
            if self.controller.running:
                self.controller.stop_application_scaling()

        self.assertEqual("Scaling from 1 to 4", self.controller.status())