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

from abc import abstractmethod
from abc import ABCMeta


'''
The Actuator is the component responsible for connecting to the underlying
infrastructure and triggering the commands or API calls that allocate or
deallocate resources, based on other component's (normally the Controller)
requests.
'''


class Actuator:
    __metaclass__ = ABCMeta

    '''
        Sets the amount of allocated resources to the given instances, using
        the given values of caps. This method expects a dictionary of format:

        {
            "instance_id_1":cap_value_1,
            "instance_id_2":cap_value_2
        }

        Normally used when executing an application.
    '''
    @abstractmethod
    def adjust_resources(self, vm_data):
        pass

    '''
        Returns a number which represents the amount of allocated resources
        to the given instance
    '''
    @abstractmethod
    def get_allocated_resources(self, vm_id):
        pass

    '''
        Returns a number which represents the amount of allocated resources
        to the given cluster
    '''
    @abstractmethod
    def get_allocated_resources_to_cluster(self, vms_ids):
        pass
