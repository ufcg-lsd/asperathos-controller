# Copyright (c) 2019 UFCG-LSD.
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

from controller.utils.logger import ScalingLog
from controller.plugins.scheduler.base import SchedulerBase
from controller.exceptions import api as ex


class PidScheduler(SchedulerBase):

    def __init__(self, data):
        self.validate(data)
        self.logger = ScalingLog("pid_scheduler.log", "scheduler.log")
        heuristic_options = data.get('heuristic_options')
        self.max_rep = data.get('max_rep')
        self.min_rep = data.get('min_rep')
        self.app_id = data.get('app_id')
        self.proportional_gain = heuristic_options["proportional_gain"]
        self.derivative_gain = heuristic_options["derivative_gain"]
        self.integral_gain = heuristic_options["integral_gain"]
        self.last_error = None
        self.integrated_error = 0

    def scale(self, info):
        """
            Calculates the new cap value using a PID algorithm.

            The new rep expression is:
            new rep = old rep
                      - proportional_gain * error
                      - derivative_gain * (error difference)
                      - integral_gain * (integrated_error)
        """

        error = info.get('progress_error')
        replicas = info.get('last_replicas')

        proportional_component = -1 * error * self.proportional_gain

        self.logger.log('pid_info|app_id:%s|proportional_component:%f' % (self.app_id, proportional_component))

        if self.last_error is None:
            derivative_component = 0
        else:
            derivative_component = -1 * self.derivative_gain * \
                (error - self.last_error)

        self.logger.log('pid_info|app_id:%s|derivative_component:%f' % (self.app_id, derivative_component))
        
        self.integrated_error += error

        integrative_component = -1 * self.integrated_error * self.integral_gain

        self.logger.log('pid_info|app_id:%s|integral_component:%f' % (self.app_id, integrative_component))
        
        calculated_action = int(proportional_component +
                                derivative_component + integrative_component)

        self.logger.log('pid_info|app_id:%s|calculated_action:%d' % (self.app_id, calculated_action))
        
        total_rep = replicas + calculated_action

        new_rep = max(min(total_rep, self.max_rep), self.min_rep)

        self.last_error = error

        return new_rep

    def update_gains(self, data):
        self.proportional_gain = data["proportional_gain"]
        self.derivative_gain = data["derivative_gain"]
        self.integral_gain = data["integral_gain"]       
        self.logger.log("Updated scheduler gains:p(%f)-d(%f)-i(%f)" % (self.proportional_gain, self.derivative_gain, self.integral_gain))

        if data["reset"]:
            self.integrated_error = 0
            self.last_error = None

    def validate(self, data):

        data_model = {
            "max_rep": int,
            "min_rep": int,
            "heuristic_options": dict
        }
        for key in data_model:
            if (key not in data):
                raise ex.BadRequestException(
                    "Variable \"{}\" is missing".format(key))
            if (not isinstance(data[key], data_model[key])):
                raise ex.BadRequestException(
                    "\"{}\" has unexpected variable type: {}. Was expecting {}"
                    .format(key, type(data[key]), data_model[key]))

        if (data["min_rep"] < 1):
            raise ex.BadRequestException(
                "Variable \"min_rep\" must be greater than 0")
        if (data["min_rep"] > data["max_rep"]):
            raise ex.BadRequestException(
                "Variable \"max_rep\" must be greater\
                     or equal than \"min_rep\"")

        key = "heuristic_options"
        heuristics = \
            ["proportional_gain", "derivative_gain", "integral_gain"]
        types = [float, int]

        data = data.get(key)
        for key in heuristics:
            if (key not in data):
                raise ex.BadRequestException(
                    "Variable \"{}\" is missing".format(key))

            if (type(data[key]) not in types):
                raise ex.BadRequestException(
                    "\"{}\" has unexpected variable type: {}. Was expecting {}"
                    .format(key, type(data[key]), types))
