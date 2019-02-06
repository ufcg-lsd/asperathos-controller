# Actuator plugin - "k8s-replicas"
This plugin uses a Kubernetes python API to scale the replicas in a cluster with the purpose of control the total execution time of a job.

## Configuration
The "k8s-replicas" plugin requires the following parameters in "controller.cfg"

* **k8s-manifest**: The config file that gives permission to access the kubernetes cluster

### Example 

```
[general]
...
actuator_plugin = k8s_replicas

[k8s_replicas]
k8s_manifest = /home/rafaelvf/.kube/config
```
