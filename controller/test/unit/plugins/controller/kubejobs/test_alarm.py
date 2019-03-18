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
from datetime import datetime

from controller.plugins.controller.kubejobs.alarm import KubeJobs
from controller.test.unit.mocks.actuator_mock import ActuatorMock
from controller.test.unit.mocks.metric_source_mock import MetricSourceMock

"""
Class that tests the KubeJobs Alarm components.
"""


class TestKubeJobs(unittest.TestCase):

    """
    Set up KubeJobs alarm objects
    """

    def setUp(self):
        metric_source_1 = MetricSourceMock("2018-11-26T15:00:00.000Z", -2)
        actuator = ActuatorMock()
        trigger_down = 1
        trigger_up = 1
        min_cap = 2
        max_cap = 10
        actuation_size = 3
        application_id_1 = "00001"

        application_id_2 = "00002"
        metric_source_2 = MetricSourceMock("2017-08-06T07:00:00.000Z", 0.0002)

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
    Test that if necessary, the number of replicas is increased, or not.
    """

    def test_check_application_state(self):

        initial_replicas1 = self.kubejobs1.actuator.get_number_of_replicas()
        self.kubejobs1.check_application_state()
        final_replicas1 = self.kubejobs1.actuator.get_number_of_replicas()

        self.assertTrue(final_replicas1 > initial_replicas1)

        initial_replicas2 = self.kubejobs2.actuator.get_number_of_replicas()
        self.kubejobs2.check_application_state()
        final_replicas2 = self.kubejobs2.actuator.get_number_of_replicas()

        self.assertTrue(final_replicas2 == initial_replicas2)

    """
    Test that the scale down works, decreasing the number of replicas.
    """

    def test_scale_down(self):
        self.kubejobs1.actuator.replicas = 10

        self.kubejobs1._scale_down(2)
        self.assertEqual(self.kubejobs1.actuator.get_number_of_replicas(), 7)

        self.kubejobs1._scale_down(2)
        self.assertEqual(self.kubejobs1.actuator.get_number_of_replicas(), 4)

        self.kubejobs1._scale_down(2)
        self.assertEqual(self.kubejobs1.actuator.get_number_of_replicas(), 2)

    """
    Test that the scale down works, increasing the number of replicas.
    """

    def test_scale_up(self):
        self.kubejobs1._scale_up(-2)
        self.assertEqual(self.kubejobs1.actuator.get_number_of_replicas(), 4)

        self.kubejobs1._scale_up(-2)
        self.assertEqual(self.kubejobs1.actuator.get_number_of_replicas(), 7)

        self.kubejobs1._scale_up(-2)
        self.assertEqual(self.kubejobs1.actuator.get_number_of_replicas(), 10)

    """
    Test that the function _get_progress_error returns the progress
    error correct.
    """

    def test_get_progress_error(self):
        self.assertEqual(self.kubejobs1._get_progress_error("00001"),
                         (datetime.strptime("2018-11-26T15:00:00.000Z",
                                            '%Y-%m-%dT%H:%M:%S.%fZ'), -2))

        self.assertEqual(self.kubejobs2._get_progress_error("00002"),
                         (datetime.strptime("2017-08-06T07:00:00.000Z",
                                            '%Y-%m-%dT%H:%M:%S.%fZ'), 0.0002))

    """
    Test that the function _check_measurements_are_new works correctly.
    """

    def test_check_measurements_are_new(self):

        self.assertFalse(self.kubejobs1._check_measurements_are_new(
            datetime.strptime("0001-01-01T00:00:00.0Z",
                              '%Y-%m-%dT%H:%M:%S.%fZ')))

        self.assertTrue(self.kubejobs1._check_measurements_are_new(
            datetime.strptime("2017-08-06T07:00:00.000Z",
                              '%Y-%m-%dT%H:%M:%S.%fZ')))

    """
    Test that the status returned is correct.
    """

    def test_status(self):
        self.kubejobs1.metric_source = MetricSourceMock(
            "2018-11-26T15:00:00.000Z", 0.0001)
        initial_state1 = ""
        final_state1 = "Progress error-[%s]-%f" % \
            self.kubejobs1._get_progress_error("00001")

        self.assertEqual(self.kubejobs1.status(), initial_state1)
        self.kubejobs1.check_application_state()
        self.assertEqual(self.kubejobs1.status(), final_state1)

        self.kubejobs2.metric_source = MetricSourceMock(
            "0001-01-01T00:00:00.0Z", 0.0002)
        initial_state2 = ""
        final_state2 = "Progress error-[%s]-%f" % \
            self.kubejobs2._get_progress_error("00002") \
            + " Could not acquire more recent metrics"

        self.assertEqual(self.kubejobs2.status(), initial_state2)
        self.kubejobs2.check_application_state()
        self.assertEqual(self.kubejobs2.status(), final_state2)
