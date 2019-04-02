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

# TODO: Documentation


class RemoteKVMTunnel:
    def __init__(self, ssh, keypair, iops_reference=1000,
                 bs_reference=1000000):
        self.ssh = ssh
        self.keypair = keypair
        self.iops_reference = iops_reference
        self.bs_reference = bs_reference

    def change_vcpu_quota(self, host_ip, vm_id, cap):
        if cap < 0 or cap > 100:
            raise Exception("Invalid cap value")

        command = self._format_change_vcpu_quota_command(vm_id, cap)
        self.ssh.run_command_tunnel(command, "root", host_ip, self.keypair)

    def change_io_quota(self, host_ip, vm_id, cap):
        if cap < 0 or cap > 100:
            raise Exception("Invalid cap value")

        command = self._format_change_io_quota_command(vm_id, cap,
                                                       self.iops_reference,
                                                       self.bs_reference)

        self.ssh.run_command_tunnel(command, "root", host_ip, self.keypair)

    def get_allocated_resources(self, host_ip, vm_id):
        command = self._format_get_allocated_resources_command(vm_id)

        ssh_result = self.ssh.run_and_get_result_tunnel(command,
                                                        "root",
                                                        host_ip,
                                                        self.keypair)

        try:
            cap = int(ssh_result)
            if cap == 0:
                raise Exception("Could not get allocated resources")

            if cap < 0:
                cap = 100
            return cap

        except BaseException:
            # FIXME: review this exception type
            raise Exception("Could not get allocated resources")

    def get_io_quota(self, host_ip, vm_id):
        command = self._format_get_io_quota_command(vm_id)
        ssh_result = self.ssh.run_and_get_result_tunnel(
            command, "root", host_ip, self.keypair)

        try:
            quota = int(ssh_result)
            return 100 * quota / float(self.iops_reference)
        except BaseException:
            # FIXME: review this exception type
            raise Exception("Could not get allocated resources")

    def _format_get_io_quota_command(self, vm_id):
        command = "virsh blkdeviotune %s" \
                  " \"`virsh domblklist %s | awk 'FNR == 3 {print $1}'`\"" \
                  " | grep total_iops_sec: | awk '{print $2}'" % (vm_id, vm_id)

        return command

    def _format_change_vcpu_quota_command(self, vm_id, cap):
        command = ("virsh schedinfo %s --set vcpu_quota=$(( %s *"
                   " `virsh schedinfo %s | awk 'FNR == 3 {print $3}'`/100 ))"
                   " > /dev/null" % (vm_id, cap, vm_id))

        return command

    def _format_change_io_quota_command(self, vm_id, cap, iops_reference,
                                        bs_reference):
        command_iops_quota = (cap * iops_reference) / 100
        command_bs_quota = (cap * bs_reference) / 100

        command = ("virsh blkdeviotune %s \"`virsh domblklist %s | awk 'FNR"
                   " == 3 {print $1}'`\" --current --total_iops_sec %s "
                   "--total_bytes_sec %s" % (vm_id, vm_id,
                                             command_iops_quota,
                                             command_bs_quota))

        return command

    def _format_get_allocated_resources_command(self, vm_id):
        command = ("virsh schedinfo %s | awk '{if(NR==3){period=$3} "
                   "if(NR==4){print 100*$3/period}}'" % (vm_id))

        return command
