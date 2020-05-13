# Copyright (c) 2020 UFCG-LSD.
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


class PidSchedulerMultiErrorCombineErrors(SchedulerBase):

    def __init__(self, data):
        self.validate(data)
        self.logger = ScalingLog("pid_scheduler.log", "scheduler.log")
        heuristic_options = data.get('heuristic_options')
        self.max_rep = data.get('max_rep')
        self.min_rep = data.get('min_rep')
        self.proportional_gain = heuristic_options["proportional_gain"]
        self.derivative_gain = heuristic_options["derivative_gain"]
        self.integral_gain = heuristic_options["integral_gain"]
        self.alpha = heuristic_options["alpha"]
        self.correction_factor = heuristic_options["correction_factor"]
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

        replicas = info.get('last_replicas')
        error_list = info.get('error_info')

        error0 = error_list[0]
        error1 = self.correction_factor * error_list[1]

        final_error = self.alpha * error0 + (1 - self.alpha) * error1
        self.logger.log("Final error: %f" % final_error)

        proportional_component = -1 * final_error * self.proportional_gain

        if self.last_error is None:
            derivative_component = 0
        else:
            derivative_component = -1 * self.derivative_gain * \
                (final_error - self.last_error)

        self.integrated_error += final_error

        integrative_component = -1 * self.integrated_error * self.integral_gain

        calculated_action = int(proportional_component +
                                derivative_component + integrative_component)

        total_rep = replicas + calculated_action

        new_rep = max(min(total_rep, self.max_rep), self.min_rep)

        self.last_error = final_error

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

        # TODO Add validation of PID parameters
