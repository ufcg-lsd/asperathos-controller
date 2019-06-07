# Controller plugin - "progress_error"

## Start scaling
### Expected parameters
* **check_interval**: Time between application state checks, in seconds. The controller checks the application state every check_interval seconds.
* **trigger_down**: The absolute value of the difference between job progress and time progress that triggers the scale down.
* **trigger_up**: The absolute value of the difference between job progress and time progress that triggers the scale up. 
* **min_cap**: The minimum possible value of resources that can be allocated to the application. Must be in range [0,100].
* **max_cap**: The maximum possible value of resources that can be allocated to the application. Must be in range [0,100].
* **actuation_size**: Amount of resources added or removed when scaling up or down. Must be in range [0,100].
* **metric_rounding**: The amount of decimal digits considered when taking scaling decisions. e.g.:If the scaler gets a metric value 0.567 from the metric source and metric_rounding = 2 then the value the scaler will use is 0.57.

### Request example

```javascript
{
    "username":"username",
    "password":"password",
    "plugin":"progress_error",
    "plugin_info":{
        "actuator":"k8s-replicas",
        "metric_source":"monasca",
        "instances":["6f9fe95f-9072-4545-a62a-fc5fd7cae9a4", "45034c39-c280-4047-8b92-a8efb61bc589"],
        "check_interval":10,
        "trigger_down":10,
        "trigger_up":10,
        "min_cap":10,
        "max_cap":100,
        "actuation_size":20,
        "metric_rounding":2
    }
}
```
