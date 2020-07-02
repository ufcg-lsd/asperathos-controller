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


class PidSchedulerMultiErrorCombineActions(SchedulerBase):

    def __init__(self, data):
        self.validate(data)
        self.logger = ScalingLog("pid_scheduler.log", "scheduler.log")
        heuristic_options = data.get('heuristic_options')
        self.max_rep = data.get('max_rep')
        self.min_rep = data.get('min_rep')
        self.proportional_gain1 = heuristic_options["proportional_gain1"]
        self.derivative_gain1 = heuristic_options["derivative_gain1"]
        self.integral_gain1 = heuristic_options["integral_gain1"]
        self.proportional_gain2 = heuristic_options["proportional_gain2"]
        self.derivative_gain2 = heuristic_options["derivative_gain2"]
        self.integral_gain2 = heuristic_options["integral_gain2"]
        self.alpha = heuristic_options["alpha"]
        self.last_error1 = None
        self.integrated_error1 = 0
        self.last_error2 = None
        self.integrated_error2 = 0

    def _pid_1(self, error):
        proportional_component = -1 * error * self.proportional_gain1

        if self.last_error1 is None:
            derivative_component = 0
        else:
            derivative_component = -1 * self.derivative_gain1 * \
                                   (error - self.last_error1)

        self.integrated_error1 += error

        integrative_component = -1 * self.integrated_error1 * self.integral_gain1

        calculated_action = \
            proportional_component + derivative_component + integrative_component

        self.last_error1 = error

        return calculated_action

    def _pid_2(self, error):
        proportional_component = -1 * error * self.proportional_gain2

        if self.last_error2 is None:
            derivative_component = 0
        else:
            derivative_component = -1 * self.derivative_gain2 * \
                                   (error - self.last_error2)

        self.integrated_error2 += error

        integrative_component = -1 * self.integrated_error2 * self.integral_gain2

        calculated_action = \
            proportional_component + derivative_component + integrative_component

        self.last_error2 = error

        return calculated_action

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

        self.logger.log("Running PID 1")
        calculated_action1 = self._pid_1(error_list[0])
        self.logger.log("Calculated action 1: %f" % calculated_action1)
        self.logger.log("Running PID 2")
        calculated_action2 = self._pid_2(error_list[1])
        self.logger.log("Calculated action 2: %f" % calculated_action2)

        final_calculated_action = self.alpha * calculated_action1 + (1 - self.alpha) * calculated_action2
        final_calculated_action = int(final_calculated_action)
        self.logger.log("Final calculated action: %f" % final_calculated_action)

        total_rep = replicas + final_calculated_action

        new_rep = max(min(total_rep, self.max_rep), self.min_rep)

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