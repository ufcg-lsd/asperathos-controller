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

import unittest
from controller.utils.remote.kvm import RemoteKVM
from controller.utils.ssh import SSHUtils
from mock.mock import MagicMock


class TestRemoteKVM(unittest.TestCase):

    def setUp(self):
        self.ssh_utils = SSHUtils({})
        self.compute_nodes_key = "key"
        self.iops_reference = 50
        self.bs_reference = 10000000
        self.remote_kvm = RemoteKVM(self.ssh_utils, self.compute_nodes_key,
                                    self.iops_reference, self.bs_reference)
        self.cap = 56
        self.host_ip = "vm-ip"
        self.vm_id = "vm-id"
        self.io_quota = 1000

    #
    # change_cpu_quota
    #

    def test_change_cpu_quota(self):
        self.ssh_utils.run_command = MagicMock(return_value=None)

        self.remote_kvm.change_vcpu_quota(self.host_ip, self.vm_id, self.cap)

        command = "virsh schedinfo %s" \
                  " --set vcpu_quota=$(( %s * `virsh schedinfo %s" \
                  " | awk \'FNR == 3 {print $3}\'`/100 ))" \
                  " > /dev/null" % (self.vm_id, self.cap, self.vm_id)

        self.ssh_utils.run_command.assert_called_once_with(
            command, "root", self.host_ip, self.compute_nodes_key)

    def test_change_cpu_quota_negative_cap_value(self):
        self.assertRaises(Exception, self.remote_kvm.change_vcpu_quota,
                          self.host_ip, self.vm_id,
                          -10, self.compute_nodes_key)

    def test_change_cpu_quota_too_high_cap_value(self):
        self.assertRaises(
            Exception,
            self.remote_kvm.change_vcpu_quota,
            self.host_ip,
            self.vm_id,
            100 + 20,
            self.compute_nodes_key)

    #
    # change_io_quota
    #

    def test_change_io_quota(self):
        command_iops_quota = (self.cap * self.iops_reference) / 100
        command_bs_quota = (self.cap * self.bs_reference) / 100
        command_set_io_quota = "virsh blkdeviotune %s" \
            " \"`virsh domblklist %s | awk 'FNR == 3 {print $1}'`\"" \
            " --current --total_iops_sec %s" \
            " --total_bytes_sec %s" % (self.vm_id, self.vm_id,
                                       command_iops_quota, command_bs_quota)

        self.ssh_utils.run_command = MagicMock(return_value=None)

        self.remote_kvm.change_io_quota(self.host_ip, self.vm_id, self.cap)

        self.ssh_utils.run_command.assert_called_once_with(
            command_set_io_quota, "root", self.host_ip, self.compute_nodes_key)

    def test_change_io_quota_negative_cap_value(self):
        self.assertRaises(Exception, self.remote_kvm.change_io_quota,
                          self.host_ip, self.vm_id, -10,
                          self.compute_nodes_key)

    def test_change_io_quota_too_high_cap_value(self):
        self.assertRaises(
            Exception,
            self.remote_kvm.change_io_quota,
            self.host_ip,
            self.vm_id,
            100 + 20,
            self.compute_nodes_key)

    def test_get_allocated_resources_success(self):
        self.ssh_utils.run_and_get_result = MagicMock(return_value="56")

        result_cap = self.remote_kvm.get_allocated_resources(
            self.host_ip, self.vm_id)

        self.assertEquals(result_cap, 56)

        command = "virsh schedinfo %s" \
            " | awk '{if(NR==3){period=$3}" \
            " if(NR==4){print 100*$3/period}}'" % \
            (self.vm_id)
        self.ssh_utils.run_and_get_result.assert_called_once_with(
            command, "root", self.host_ip, self.compute_nodes_key)

    #
    # get_cpu_quota
    #

    def test_get_allocated_resources_virsh_returns_negative_1(self):
        self.ssh_utils.run_and_get_result = MagicMock(return_value="-1")

        result_cap = self.remote_kvm.get_allocated_resources(
            self.host_ip, self.vm_id)

        self.assertEquals(result_cap, 100)

        command = "virsh schedinfo %s" \
            " | awk '{if(NR==3){period=$3}" \
            " if(NR==4){print 100*$3/period}}'" % (self.vm_id)
        self.ssh_utils.run_and_get_result.assert_called_once_with(
            command, "root", self.host_ip, self.compute_nodes_key)

    def test_get_allocated_resources_ssh_returns_empty_string(self):
        self.ssh_utils.run_and_get_result = MagicMock(return_value="")

        self.assertRaises(Exception, self.remote_kvm.get_allocated_resources,
                          self.host_ip, self.vm_id, self.compute_nodes_key)

    #
    # get_io_quota
    #

    def get_io_quota_ssh_values(self, command, user, host, key):
        if "blkdeviotune" in command:
            return str(self.io_quota)
        elif "domblklist" in command:
            return self.block_device

    def test_get_io_quota(self):
        command_get_io_quota = "virsh blkdeviotune %s" \
            " \"`virsh domblklist %s | awk 'FNR == 3 {print $1}'`\"" \
            " | grep total_iops_sec: | awk '{print $2}'" % (
                self.vm_id, self.vm_id)

        self.ssh_utils.run_and_get_result = MagicMock()
        self.ssh_utils.run_and_get_result.side_effect = \
            self.get_io_quota_ssh_values

        quota = self.remote_kvm.get_io_quota(self.host_ip, self.vm_id)

        self.assertEqual(quota, 100 * float(self.io_quota) /
                         self.iops_reference)
        self.ssh_utils.run_and_get_result.assert_any_call(
            command_get_io_quota, "root", self.host_ip, self.compute_nodes_key)

    def test_get_io_quota_ssh_returns_empty_string(self):
        self.ssh_utils.run_and_get_result = MagicMock(return_value="")

        self.assertRaises(
            Exception,
            self.remote_kvm.get_io_quota,
            self.host_ip,
            self.vm_id,
            self.compute_nodes_key)


if __name__ == "__main__":
    unittest.main()
