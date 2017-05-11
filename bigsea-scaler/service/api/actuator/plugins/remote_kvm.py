# TODO: documentation
class Remote_KVM(object):

    def __init__(self, ssh_utils, compute_nodes_key):
        self.ssh_utils = ssh_utils
        self.compute_nodes_key = compute_nodes_key

    # Warning: This code requires that the vcpu_quota parameter is between 0 and 100000
    def change_vcpu_quota(self, host_ip, vm_id, cap):
        # TODO: check ip value
        # TODO: check id value
        if cap < 0 or cap > 100:
            # FIXME review this exception type
            raise Exception("Invalid cap value")
        
        command = "virsh schedinfo %s --set vcpu_quota=%s > /dev/null" % (vm_id, cap*1000)
        # TODO: check errors
        self.ssh_utils.run_command(command, "root", host_ip, self.compute_nodes_key)
        
    # Warning: This code requires that the vcpu_quota parameter is between 0 and 100000 
    def get_allocated_resources(self, host_ip, vm_id):
        # TODO: check ip value
        # TODO: check id value
        command = "virsh schedinfo %s | grep vcpu_quota | awk '{print $3}'" % (vm_id)
        # TODO: check errors
        ssh_result = self.ssh_utils.run_and_get_result(command, "root", host_ip, self.compute_nodes_key)
        
        try:
            cap = int(ssh_result)
            
            if cap == -1:
                return 100
            return cap/1000
        except:
            # FIXME: review this exception type
            raise Exception("Could not get allocated resources")