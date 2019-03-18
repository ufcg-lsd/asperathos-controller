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

# TODO: documentation

from kubernetes import client, config


class K8sActuator:

    def __init__(self, app_id, k8s_manifest):
        # load config from default location (~/.kube/config)
        config.load_kube_config(k8s_manifest)
        # api instance
        self.k8s_api = client.BatchV1Api()
        self.app_id = app_id

    # TODO: validation
    def adjust_resources(self, replicas, namespace="default"):
        patch_object = {"spec": {"parallelism": replicas}}
        try:
            self.k8s_api.patch_namespaced_job(self.app_id,
                                              namespace,
                                              patch_object)
        except Exception as e:
            print e

    # TODO: validation
    def get_number_of_replicas(self, namespace="default"):
        all_jobs = self.k8s_api.list_namespaced_job(namespace)
        for job in all_jobs.items:
            if job.metadata.name == self.app_id:
                return job.spec.parallelism
