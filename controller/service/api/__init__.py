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

import configparser
from controller.utils.logger import Log

LOG = Log('api_log', 'api.log')

try:
    # Conf reading
    config = configparser.RawConfigParser()
    config.read('./controller.cfg')

    """ General configuration """
    host = config.get("general", "host")
    port = config.getint("general", "port")
    actuator_plugins = config.get('general', 'actuator_plugins').split(',')
    metric_source_plugins = config.get(
        'general', 'metric_source_plugins').split(',')

    """ Validate if really exists a section to listed plugins """
    for plugin in actuator_plugins:
        if plugin != '' and plugin not in config.sections():
            raise Exception("plugin '%s' section missing" % plugin)

    for plugin in metric_source_plugins:
        if plugin != '' and plugin not in config.sections():
            raise Exception("plugin '%s' section missing" % plugin)

    if 'monasca' in metric_source_plugins:
        monasca_endpoint = config.get('monasca', 'monasca_endpoint')
        monasca_username = config.get('monasca', 'username')
        monasca_password = config.get('monasca', 'password')
        monasca_auth_url = config.get('monasca', 'auth_url')
        monasca_project_name = config.get('monasca', 'project_name')
        monasca_api_version = config.get('monasca', 'api_version')

    if 'k8s_replicas' in actuator_plugins:

        # Setting default value
        k8s_manifest = "./data/conf"

        # If explicitly stated in the cfg file, overwrite the variable
        if(config.has_section('k8s_replicas')):
            if(config.has_option('k8s_replicas', 'k8s_manifest')):
                k8s_manifest = config.get("k8s_replicas", "k8s_manifest")

except Exception as e:
    LOG.log("Error: %s" % e)
    quit()
