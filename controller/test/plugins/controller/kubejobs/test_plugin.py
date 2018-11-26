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

from controller.plugins.controller.kubejobs.plugin import KubejobsController

class TestKubeJobsController(unittest.TestCase):

    """
    """    
    def setUp(self):
        parameters = {"control_parameters": {
            "check_interval": "",
            "trigger_down": "",
            "trigger_up": "",
            "min_rep": "",
            "max_rep": "",
            "actuation_size": "",
            "actuator": "",
            "metric_source": ""
        }}
        application_id = "000001"

    """
    """
    def tearDown(self):
        pass

    """
    """
    def test_start_stop_application(self):
        pass

    """
    """
    def test_status(self):
        pass
