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

from mock import MagicMock
import unittest

from controller.utils.ssh import SSHUtils
from controller.plugins.actuator.kvm.plugin import KVMActuator
from controller.utils.locator.instance import InstanceLocator
from controller.utils.remote.kvm import RemoteKVM
from controller.exceptions.kvm import InstanceNotFoundException
from controller.exceptions.infra import AuthorizationFailedException


class TestBasicActuator(unittest.TestCase):

    def setUp(self):
        self.vm_id1 = "vm_id1"
        self.vm_id2 = "vm_id2"

        self.host_ip1 = "host_ip1"
        self.host_ip2 = "host_ip2"

        self.cap1 = 50
        self.cap2 = 78
        self.io_cap = 75

        self.bigsea_username = "username"
        self.bigsea_password = "password"
        self.authorization_url = "authorization_url"
        # self.authorization_data = dict(
        # authorization_url=self.authorization_url,
        # bigsea_username=self.bigsea_username,
        # bigsea_password=self.bigsea_password)

        compute_nodes = []
        compute_nodes_key = "key"
        self.instance_locator = InstanceLocator(
            SSHUtils({}), compute_nodes, compute_nodes_key)
        self.remote_kvm = RemoteKVM(SSHUtils({}), compute_nodes_key)
        self.actuator = KVMActuator(self.instance_locator,
                                    self.remote_kvm, self.io_cap)

    def locator(self, vm_id):
        return {self.vm_id1: self.host_ip1, self.vm_id2: self.host_ip2}[vm_id]

    def locator_instance_does_not_exist(self, vm_id):
        if vm_id == self.vm_id1:
            return self.host_ip1
        else:
            raise InstanceNotFoundException(vm_id)

    @unittest.skip("Authorization isn't working")
    def test_authorization(self):
        self.actuator.authorizer.get_authorization = MagicMock(
            return_value={'success': True})

        # Actuator tries to authenticate
        self.actuator.authorizer.get_authorization.assert_called_once_with(
            self.authorization_url, self.bigsea_username, self.bigsea_password)

    def test_adjust_resources_locates_and_acts_correctly_1_instance(self):
        vm_data = {self.vm_id1: self.cap1}

        self.instance_locator.locate = MagicMock(return_value=self.host_ip1)
        self.remote_kvm.change_vcpu_quota = MagicMock(return_value=None)
        self.remote_kvm.change_io_quota = MagicMock(return_value=None)

        self.actuator.adjust_resources(vm_data)

        # Actuator tries to locate the instances
        self.instance_locator.locate.assert_called_once_with(self.vm_id1)

        # Actuator tries to change the cap
        self.remote_kvm.change_vcpu_quota.assert_called_once_with(
            self.host_ip1, self.vm_id1, self.cap1)
        self.remote_kvm.change_io_quota.assert_called_once_with(
            self.host_ip1, self.vm_id1, self.io_cap)

    def test_adjust_resources_locates_and_acts_correctly_n_instances(self):
        vm_data = {self.vm_id1: self.cap1, self.vm_id2: self.cap2}

        self.instance_locator.locate = MagicMock()
        self.instance_locator.locate.side_effect = self.locator
        self.remote_kvm.change_vcpu_quota = MagicMock(return_value=None)
        self.remote_kvm.change_io_quota = MagicMock(return_value=None)

        self.actuator.adjust_resources(vm_data)

        # Actuator tries to locate the instances
        self.instance_locator.locate.assert_any_call(self.vm_id1)
        self.instance_locator.locate.assert_any_call(self.vm_id2)

        # Actuator tries to locate only the given instances
        self.assertEqual(self.instance_locator.locate.call_count, 2)

        # Actuator tries to change the cap
        self.remote_kvm.change_vcpu_quota.assert_any_call(
            self.host_ip1, self.vm_id1, self.cap1)
        self.remote_kvm.change_io_quota.assert_any_call(
            self.host_ip1, self.vm_id1, self.io_cap)

        self.remote_kvm.change_vcpu_quota.assert_any_call(
            self.host_ip2, self.vm_id2, self.cap2)
        self.remote_kvm.change_io_quota.assert_any_call(
            self.host_ip2, self.vm_id2, self.io_cap)

        # Actuator tries to change the cap of only the given instances
        self.assertEqual(self.remote_kvm.change_vcpu_quota.call_count, 2)

    def test_adjust_resources_one_instance_does_not_exist(self):
        vm_data = {self.vm_id1: self.cap1, self.vm_id2: self.cap2}

        self.instance_locator.locate = MagicMock()
        self.instance_locator.locate.side_effect = \
            self.locator_instance_does_not_exist

        self.remote_kvm.change_vcpu_quota = MagicMock(return_value=None)
        self.remote_kvm.change_io_quota = MagicMock(return_value=None)

        self.actuator.adjust_resources(vm_data)

        # Actuator tries to locate the instances
        self.instance_locator.locate.assert_any_call(self.vm_id1)
        self.instance_locator.locate.assert_any_call(self.vm_id2)

        # Actuator tries to change the cap
        self.remote_kvm.change_vcpu_quota.assert_called_once_with(
            self.host_ip1, self.vm_id1, self.cap1)
        self.remote_kvm.change_io_quota.assert_called_once_with(
            self.host_ip1, self.vm_id1, self.io_cap)

    def test_get_allocated_resources(self):
        self.instance_locator.locate = MagicMock()
        self.instance_locator.locate.side_effect = self.locator
        self.remote_kvm.get_allocated_resources = MagicMock(return_value=50)

        cap = self.actuator.get_allocated_resources(self.vm_id1)

        # Actuator returns the correct cap value
        self.assertEquals(cap, 50)

        # Actuator tries to locate the instance
        self.instance_locator.locate.assert_called_once_with(self.vm_id1)

        # Actuator tries to get the resources allocated to the given instance
        self.remote_kvm.get_allocated_resources.assert_called_once_with(
            self.host_ip1, self.vm_id1)

    def test_get_allocated_resources_to_cluster(self):
        vms_ids = [self.vm_id1, self.vm_id2]

        self.instance_locator.locate = MagicMock()
        self.instance_locator.locate.side_effect = self.locator
        self.remote_kvm.get_allocated_resources = MagicMock(return_value=50)

        self.actuator.get_allocated_resources_to_cluster(vms_ids)

        # Actuator tries to locate the first instance
        self.instance_locator.locate.assert_called_once_with(self.vm_id1)

        # Actuator tries to get the resources allocated to the given instance
        self.remote_kvm.get_allocated_resources.assert_called_once_with(
            self.host_ip1, self.vm_id1)

    def test_get_allocated_resources_to_cluster_instance_does_not_exist(self):
        vms_ids = [self.vm_id2, self.vm_id1]

        self.instance_locator.locate = MagicMock()
        self.instance_locator.locate.side_effect = \
            self.locator_instance_does_not_exist
        self.remote_kvm.get_allocated_resources = MagicMock(return_value=50)

        self.actuator.get_allocated_resources_to_cluster(vms_ids)

        # Actuator tries to locate the first instance
        self.instance_locator.locate.assert_any_call(self.vm_id1)
        self.instance_locator.locate.assert_any_call(self.vm_id2)

        # Actuator tries to get the resources allocated to the given instance
        self.remote_kvm.get_allocated_resources.assert_called_once_with(
            self.host_ip1, self.vm_id1)

    @unittest.skip("Authorization isn't working")
    def test_adjust_resources_raises_exception_if_not_authorized(self):
        vm_data = {self.vm_id1: self.cap1, self.vm_id2: self.cap2}

        self.instance_locator.locate = MagicMock()
        self.instance_locator.locate.side_effect = \
            self.locator_instance_does_not_exist

        self.remote_kvm.change_vcpu_quota = MagicMock(return_value=None)
        self.actuator.authorizer.get_authorization = MagicMock(
            return_value={'success': False})

        self.assertRaises(AuthorizationFailedException,
                          self.actuator.adjust_resources, vm_data)

    @unittest.skip("Authorization isn't working")
    def test_get_allocated_resources_raises_exception_if_not_authorized(self):
        vms_ids = [self.vm_id2, self.vm_id1]

        self.instance_locator.locate = MagicMock()
        self.instance_locator.locate.side_effect = \
            self.locator_instance_does_not_exist
        self.remote_kvm.get_allocated_resources = MagicMock(return_value=50)
        self.actuator.authorizer.get_authorization = MagicMock(
            return_value={'success': False})

        self.assertRaises(
            AuthorizationFailedException,
            self.actuator.get_allocated_resources_to_cluster,
            vms_ids)


if __name__ == "__main__":
    unittest.main()
