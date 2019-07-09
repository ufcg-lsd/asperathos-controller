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


from controller.plugins.controller.kubejobs.plugin import KubejobsController
from controller.service import plugin_service


class ControllerBuilder:

    def __init__(self):
        pass

    def get_controller(self, name, app_id, plugin_info):

        if name == "kubejobs":
            return KubejobsController(app_id, plugin_info)

        else:
            try:
                return plugin_service.get_plugin(name)
            except Exception:
                raise Exception("Unknown actuator type")
