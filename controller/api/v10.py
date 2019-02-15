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

from flask import request

from controller.utils import api as u
from controller.utils.logger import Log
from controller.service.api import v10 as api


rest = u.Rest('v10', __name__)


""" Setup environment.

    Normal response codes: 204
    Error response codes: 400, 401
"""
@rest.post('/setup', 204)
def setup_environment(data):
    return u.render(api.setup_environment(data))


""" Start scaling.

    Normal response codes: 204
    Error response codes: 400, 401
"""
@rest.post('/scaling/<app_id>', 204)
def start_scaling(app_id, data):
    return u.render(api.start_scaling(app_id, data))


""" Stop scaling.

    Normal response codes: 204
    Error response codes: 400, 401
"""
@rest.put('/scaling/<app_id>/stop')
def stop_scaling(app_id, data):
    return u.render(api.stop_scaling(app_id))


""" Controller status.

    Normal response codes: 200
    Error response codes: 400
"""
@rest.get('/scaling')
def controller_status():
    return u.render(api.controller_status())

""" Add a new cluster reference in the Asperathos section.

    Normal response codes: 202
    Error response codes: 400, 401
"""
@rest.post('/cluster')
def add_cluster(data):
    return u.render(api.add_cluster(data)) 

""" Delete a cluster reference in the Asperathos section.

    Normal response codes: 202
    Error response codes: 400, 401
"""
@rest.post('/cluster/<cluster_name>/delete')
def delete_cluster(cluster_name, data):
    return u.render(api.delete_cluster(cluster_name, data)) 

""" Start to use the informed cluster as active cluster
    in the Asperathos section.
                                                                              
    Normal response codes: 200
    Error response codes: 400
"""
@rest.post('/cluster/<cluster_name>')
def active_cluster(cluster_name, data):
    return u.render(api.active_cluster(cluster_name, data))

""" Add a certificate to a cluster reference in the Asperathos section.

    Normal response codes: 202
    Error response codes: 400, 401
"""
@rest.post('/cluster/<cluster_name>/certificate')
def add_certificate(cluster_name, data):
    return u.render(api.add_certificate(cluster_name, data)) 

""" Delete a certificate to a cluster reference in the Asperathos section.

    Normal response codes: 202
    Error response codes: 400, 401
"""
@rest.post('/cluster/<cluster_name>/certificate/<certificate_name>/delete')
def delete_certificate(cluster_name, certificate_name, data):
    return u.render(api.delete_certificate(cluster_name, certificate_name, data)) 
