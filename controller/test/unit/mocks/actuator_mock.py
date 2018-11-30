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

"""
Class that represents a mock of the Actuator object
"""
class ActuatorMock():
    """ Constructor of the mock of a Actuator object
    
    Returns:
        MockRedis: The simulation of a Actuator object
    """
    def __init__(self):
        
        self.replicas = 1

    """
    Simulate the behavior of the function get_number_of_replicas
    of Actuator.
    Return:
        number_of_replicas(Integer)
    """
    def get_number_of_replicas(self):
        return self.replicas

    """
    Simulate the behavior of the function get_number_of_replicas
    of Actuator.
    """
    def adjust_resources(self, new_replicas):
        self.replicas = new_replicas