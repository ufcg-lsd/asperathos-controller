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


from abc import ABCMeta
from abc import abstractmethod


'''
The Controller is the component responsible for, based on metrics of
infrastructure and application
health such as application progress and CPU usage,
taking actions to ensure compliance with
quality of service levels.
'''


class Controller:
    __metaclass__ = ABCMeta

    '''
        Creates a Controller instance.

        app_id is the id of the application associated with the instance.
        parameters is a dictionary of scaling parameters.
    '''
    @abstractmethod
    def __init__(self, app_id, parameters):
        pass

    '''
        Starts scaling for the application associated
        with the controller instance. The method is not expected
        to return until the scaling is stopped through the
        stop_application_scaling. Normally, this method is used
        as a run method by a thread.
    '''
    @abstractmethod
    def start_application_scaling(self):
        pass

    '''
        Stops scaling for the application associated
        with the controller instance. This method's expected
        side effect is to make start_application_scaling to return.
    '''
    @abstractmethod
    def stop_application_scaling(self):
        pass

    '''
        Returns information on the status of the scaling of applications,
        normally as a string.
    '''
    @abstractmethod
    def status(self):
        pass
