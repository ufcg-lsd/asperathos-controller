# KubeJobs Plugin

## How does it works?

The following steps describes the basic flow of an execution using KubeJobs:

* Step 1: The client sends a POST request to the Asperathos Manager with a JSON body describing the execution.
* Step 2: The Manager creates a Redis service in the cluster, enqueues the items described in the input file in Redis through the queue auxiliary service.
* Step 3: The application execution is triggered on the cluster.
* Step 4: The application running on Kubernetes cluster starts to consume items from the Redis storage.
* Step 5: The Monitor is triggered by the Manager when application starts to run.
* Step 6: The Monitor periodically gets the number of processed items from the queued service.
* Step 7: As soon as metrics are being published, the Manager starts the Controller, which consumes metrics from Redis to take decisions about scaling based on the predefined control logic.


## Configuration

In order to correctly configure the Manager to execute the KubeJobs plugin, modifications in the *controller.cfg* file are necessary. Following you can check an example of a configuration file that can be used to execute the KubeJobs plugin.

> **NOTE**: Currently, the KubeJobs controller plugin requires to be used together with the k8s-replicas actuator plugin.

### Configuration file example:

```
[general]
host = 0.0.0.0
port = 5000
actuator_plugins = k8s_replicas
metric_source_plugins = metric_source

[metric_source]
metric_source_endpoint = 
username = usr
password = psswrd
project_name = admin
auth_url = 
api_version = 1_0

[k8s_replicas]
k8s_manifest = /home/user/.kube/config
```

## Execute plugin

In order to execute the plugin, a JSON needs to be correctly configurate with all necessary variables that will be used by Asperathos components. Following you can check an example of this JSON file that will be used to sends a POST request to the Asperathos Manager.

### JSON file example:

```javascript
{  
   "plugin":"kubejobs",
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
      "control_plugin":"kubejobs",
      "control_parameters":{ 
         "schedule_strategy": "pid",
         "actuator":"k8s_replicas",
         "check_interval":5,
         "trigger_down":0,
         "trigger_up":0,
         "min_rep":1,
         "max_rep":10,
         "actuation_size":1,
         "metric_source":"redis"
         "heuristic_options": {
            	"proportional_gain": 0.1,
            	"derivative_gain": 0,
            	"integral_gain": 0
            }
      },
      "monitor_plugin":"kubejobs",
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