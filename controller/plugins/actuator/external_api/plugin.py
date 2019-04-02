# Copyright (c) 2019 LSD - UFCG.
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

import kubernetes as kube

"""
Class that implements that plugin of the external-api actuator
"""


class ExternalApi:

    def __init__(self, app_id, actuator_metric, k8s_manifest):
        self.app_id = app_id
        self.k8s_manifest = k8s_manifest
        self.actuator_metric = actuator_metric
        self.api_address = self.get_api_address()

    def get_api_address(self):
        """Get the address of the external API
        (i.e One of the nodes of the k8s cluster)

        Arguments:
            None

        Returns:
            string -- The API address.
        """

        kube.config.load_kube_config(self.k8s_manifest)
        CoreV1Api = kube.client.CoreV1Api()
        api_address = CoreV1Api.list_node(
        ).items[0].status.addresses[0].address

        return api_address
