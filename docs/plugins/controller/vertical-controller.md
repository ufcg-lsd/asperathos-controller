# Vertical Plugin

## How does it works?

The following steps describes the basic flow of an execution using Vertical:

* Step 1: The client sends a POST request to the Asperathos Manager with a JSON body describing the execution.
* Step 2: The application execution is triggered on the cluster.
* Step 3: The Monitor is triggered by the Manager when application starts to run.
* Step 4: The Monitor periodically gets the CPU information of the nodes contained in the cluster.
* Step 5: As soon as this metrics are being published, the Manager starts the Controller, which consumes metrics from the API to take decisions about scaling based on specific threshold.


## Configuration

In order to correctly configure the Controller to execute the Vertical plugin, modifications in the *controller.cfg* file are necessary. Following you can check an example of a configuration file that can be used to execute the Vertical plugin.

> **NOTE**: Currently, the Vertical controller plugin requires to be used together with the external-api actuator plugin.

### Configuration file example:

```
[general]
host = 0.0.0.0
port = 5000
actuator_plugins = external_api
metric_source_plugins =

[external_api]
# The specific metric that the actuator will modify
actuator_metric = cpu
# The config file that gives permission to access the kubernetes cluster
k8s_manifest = /home/user/.kube/config
```

## Execute plugin

In order to execute the plugin, a JSON needs to be correctly configurate with all necessary variables that will be used by Asperathos components. Following you can check an example of this JSON file that will be used to sends a POST request to the Asperathos Manager.

### JSON file example:

```javascript
{  
   "plugin":"plugin",
   "plugin_info":{  
      "username":"usr",
      "password":"psswrd",
      "cmd":[  
         [...]
      ],
      "img":"img",
      "init_size":1,
      "redis_workload":"workload",
      "config_id":"id",
      "control_plugin":"vertical",
      "graphic_metrics": true,
      "control_parameters":{  
         "actuator":"external_api",
         "check_interval":5,
         "trigger_down":0,
         "trigger_up":0,
         "min_quota":30000,
         "max_quota":100000,
         "actuator_metric":"cpu"
      },
      "monitor_plugin":"vertical",
      "monitor_info":{  
         [...]
      },
      "enable_visualizer":true,
      "visualizer_plugin":"k8s-grafana",
      "visualizer_info":{  
         [...]
      },
      "env_vars":{  
         [...]
      }
   }
}
```