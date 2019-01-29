# Actuator plugin - "External API"
This plugin uses a API running inside the cluster in order to modify the amount of allocated resources in the node.

## Configuration
The "external-api" plugin requires the following parameters in "controller.cfg"

* **actuator_metric**: The specific metric that the actuator will modify
* **k8s-manifest**: The config file that gives permission to access the kubernetes cluster

### Example 

```
[external_api]
actuator_metric = cpu
k8s_manifest = /home/user/.kube/config
```