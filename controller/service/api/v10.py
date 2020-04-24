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

from controller.plugins.actuator.builder import ActuatorBuilder
from controller.plugins.controller.builder import ControllerBuilder
from controller.service import plugin_service
from controller.utils.logger import Log
from controller.exceptions import api as ex
from threading import Thread


API_LOG = Log("APIv10", "APIv10.log")

scaled_apps = {}

controller_builder = ControllerBuilder()
actuator_builder = ActuatorBuilder()


def install_plugin(source, plugin):
    status = plugin_service.install_plugin(source, plugin)
    if status:
        return {"message": "Plugin installed successfully"}, 200
    return {"message": "Error installing plugin"}, 400


def setup_environment(data):
    if ('actuator_plugin' not in data or 'instances_cap' not in data):
        API_LOG.log("Missing parameters in request")
        raise ex.BadRequestException()

    plugin = data['actuator_plugin']
    instances_cap = data['instances_cap']

    actuator = actuator_builder.get_actuator(plugin)
    try:
        actuator.adjust_resources(instances_cap)
    except Exception as e:
        API_LOG.log(str(e))


def start_scaling(app_id, data):
    if 'control_info' not in data:
        API_LOG.log("Missing parameters in request")
        raise ex.BadRequestException()

    for plugin_key in data['control_info']:
        API_LOG.log("Creating plugin: %s" % plugin_key)
        API_LOG.log(data)
        plugin = data['control_info'][plugin_key]['plugin']
        plugin_info = data['control_info'][plugin_key]
        plugin_info['redis_ip'] = data['redis_ip']
        plugin_info['redis_port'] = data['redis_port']
        controller = controller_builder.get_controller(plugin, app_id,
                                                       plugin_info)
        executor = Thread(target=controller.start_application_scaling)

        executor.start()

        if app_id not in scaled_apps:
            scaled_apps[app_id] = {}
        scaled_apps[app_id][plugin_key] = controller


def stop_scaling(app_id):
    if app_id in scaled_apps:
        API_LOG.log("Removing application id: %s" % (app_id))

        for plugin_key in scaled_apps[app_id]:
            executor = scaled_apps[app_id][plugin_key]
            executor.stop_application_scaling()

        scaled_apps.pop(app_id)

    else:
        raise ex.BadRequestException()


def controller_status():
    status = "Status: OK\n"
    status += "Monitoring applications:\n"
    for app_id in scaled_apps:
        status += app_id + "\n"
        for plugin in scaled_apps[app_id]:
            status += plugin + "\n"
            status += "Last action:" + scaled_apps[app_id][plugin].status()
            status += "\n"

    return status
