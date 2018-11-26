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

from controller.plugins.controller.kubejobs.alarm import KubeJobs
from controller.test.mocks.actuator_mock import ActuatorMock
from controller.test.mocks.metric_source_mock import MetricSourceMock

class TestKubeJobs(unittest.TestCase):

    """
    """    
    def setUp(self):
        metric_source_1 = MetricSourceMock("2018-11-26T15:00:00.000Z", "error1")
        actuator = ActuatorMock()
        trigger_down = 0
        trigger_up = 0
        min_cap = 0
        max_cap = 0
        actuation_size = 0
        application_id_1 = "00001"

        application_id_2 = "00002"
        metric_source_2 = MetricSourceMock("2017-08-06T07:00:00.000Z", "error2")

        self.kubejobs1 = KubeJobs(actuator, metric_source_1,
                                trigger_down, trigger_up,
                                min_cap, max_cap,
                                actuation_size,
                                application_id_1)

        self.kubejobs2 = KubeJobs(actuator, metric_source_2,
                                trigger_down, trigger_up,
                                min_cap, max_cap,
                                actuation_size,
                                application_id_2)

    """
    """
    def tearDown(self):
        pass

    """
    """
    def test_check_application_state(self):
        pass

    """
    """
    def test_scale_down(self):
        pass

    """
    """
    def test_scale_up(self):
        pass

    """
    """
    def test_get_progress_error(self):
        self.assertEqual(self.kubejobs1._get_progress_error("00001"), ("2018-11-26T15:00:00.000Z", "error1"))
        self.assertEqual(self.kubejobs2._get_progress_error("00002"), ("2017-08-06T07:00:00.000Z", "error2"))

    """
    """
    def test_check_measurements_are_new(self):
        pass

    """
    """
    def test_status(self):
        pass
