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


class DefaultScheduler(SchedulerBase):

    def __init__(self, data):
        self.validate(data)
        self.logger = ScalingLog("default_scheduler.log", "scheduler.log")
        self.trigger_down = data.get("trigger_down")
        self.trigger_up = data.get("trigger_up")
        self.max_cap = data.get("max_rep")
        self.min_cap = data.get("min_rep")
        self.actuation_size = data.get("actuation_size")

    def scale(self, info):
        new_replicas = None
        progress_error = info.get('progress_error')
        replicas = info.get('last_replicas')

        if progress_error > 0 and progress_error >= self.trigger_down:
            new_replicas = max(replicas - self.actuation_size, self.min_cap)

        elif progress_error < 0 and abs(progress_error) >= self.trigger_up:
            new_replicas = min(replicas + self.actuation_size, self.max_cap)

        return new_replicas

    def update_gains(self, data):
        self.logger.log("Update gain is not supported by default scheduler")

    def validate(self, data):
        data_model = {
            "actuation_size": int,
            "max_rep": int,
            "min_rep": int
        }

        for key in data_model:
            if (key not in data):
                raise ex.BadRequestException(
                    "Variable \"{}\" is missing".format(key))
            if (not isinstance(data[key], data_model[key])):
                raise ex.BadRequestException(
                    "\"{}\" has unexpected variable type: {}. Was expecting {}"
                    .format(key, type(data[key]), data_model[key]))

        if 'trigger_up'not in data:
            raise ex.BadRequestException(
                    "Variable \"{}\" is missing".format(key))

        if not (isinstance(data['trigger_up'], int) or
                isinstance(data['trigger_up'], float)):
            raise ex.BadRequestException(
                "\"trigger_up\" has unexpected variable type: {}. Was"
                " expecting float or int".format(type(data['trigger_up'])))

        if 'trigger_down' not in data:
            raise ex.BadRequestException(
                "Variable \"{}\" is missing".format(key))

        if not (isinstance(data['trigger_down'], int) or
                isinstance(data['trigger_down'], float)):
            raise ex.BadRequestException(
                "\"trigger_down\" has unexpected variable type: {}. Was"
                " expecting float or int".format(type(data['trigger_down'])))

        if (data["min_rep"] < 1):
            raise ex.BadRequestException(
                "Variable \"min_rep\" must be greater than 0")
        if (data["min_rep"] > data["max_rep"]):
            raise ex.BadRequestException(
                "Variable \"max_rep\" must be greater\
                    or equal than \"min_rep\"")
