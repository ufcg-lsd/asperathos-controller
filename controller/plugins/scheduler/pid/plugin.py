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
import time

class PidScheduler(SchedulerBase):

    def __init__(self, data):
        self.validate(data)
        self.logger = ScalingLog("pid_scheduler.log", "scheduler.log")
        heuristic_options = data.get('heuristic_options')
        self.max_rep = data.get('max_rep')
        self.min_rep = data.get('min_rep')
        self.proportional_gain = heuristic_options["proportional_gain"]
        self.derivative_gain = heuristic_options["derivative_gain"]
        self.integral_gain = heuristic_options["integral_gain"]
        self.last_error = 0.0
        self.integrated_error = 0.0
        self.last_timestamp = 0

    def scale(self, info):
        """
            Calculates the new cap value using a PID algorithm.

            The new rep expression is:
            new rep = proportional_gain * error
                      + derivative_gain * (error difference) / dt
                      + integral_gain * (integrated_error) * dt
        """

        time_now = time.time()
        
        # Default value = 2
        # TODO: get check_period from JSON
        dt = 2

        if self.last_timestamp != 0:
            dt = time_now - self.last_timestamp

        self.last_timestamp = time_now

        error = info.get('progress_error')

        proportional_action = self.proportional_gain * error

        derivative_action = 0.0
        if self.last_error != 0:
            derivative_action = self.derivative_gain * \
                (error - self.last_error) / dt

        self.integrated_error += error * dt
        integral_action = self.integral_gain * self.integrated_error

        control_action = int(proportional_action +
                                derivative_action + integral_action)

        # Asperathos fashion of computing the error
        # requires the multiplication by (-1) to adjust
        # the topology for better suit Control Theory implementation
        # of feedback control
        
        control_action *= -1
        total_rep = control_action

        new_rep = max(min(total_rep, self.max_rep), self.min_rep)

        log_str = f"\n"
        log_str += f"\nCONTROL ACTION: {control_action}"
        log_str += f"\nNEW_REP: {new_rep}"
        log_str += f"\nP: {proportional_action}"
        log_str += f"\nI: {integral_action}"
        log_str += f"\nD: {derivative_action}"
        
        self.logger.log(log_str)

        self.last_error = error

        return new_rep

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
