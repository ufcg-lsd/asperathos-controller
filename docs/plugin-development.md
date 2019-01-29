# Plugin development
This is an important step to enjoy all flexibility and features that this framework provides.

## The Controller, Actuator and Metric Source
The controller is implemented following a **plugin architecture**, providing flexibility to add or remove plugins when necessary. It works with usage of three types of plugins: **Actuator**, **Controller** and **Metric Source**.
* The **Controller**, based on metrics such as application progress and CPU usage, decides the amount of resources to allocate to the applications.
* The **Actuator** is responsible for connecting to the underlying infrastructure (such as a Mesos or an OpenStack Sahara platform) and triggering the commands or API calls that allocate or deallocate resources, based on the Controller’s requests.
* The **Metric Source** plugin is responsible for getting application metrics from a metric source, such as Monasca, and returning them to the Controller.

## Steps

1. In *controller.cfg* add the plugin to the list of desired plugins:

### Example:

```
[general]
host = 0.0.0.0
port = 6000
actuator_plugins = my_new_controller_plugin
metric_source_plugins = metric_source

[metric_source]
metric_source_endpoint =
username = 
password = 
project_name =
auth_url =
api_version =

[my_new_controller_plugin]
var1 =
var2 =
var3 = 
```
In this tutorial, we will use MyNewControllerPlugin to represent a new controller plugin.

2. In *controller/plugins* folder, exists three directories (*controller*, *actuator* and *metric_source*). Choose what kind of plugin you will develop and create a new folder under one of these directories with the desired plugin name and add *__init__.py*.

3. Create a new if statement condition in the file *controller/service/api/__init__.py* that will recognize if the new plugin added is informed in the configuration file (*controller.cfg*). If this condition is true, then the necessary variables to execute the plugin needs to be informed in the *controller.cfg* file and computed in the *controller/service/api/__init__.py*.

### Example:

```
import ConfigParser

try:

[...]

if 'my_new_controller_plugin' in plugins:
    var1 = config.get('my_new_controller_plugin', 'var1')
    var2 = config.get('my_new_controller_plugin', 'var2')
    var3 = config.get('my_new_controller_plugin', 'var3')

[...]
```
 
4. Write a new python class under *controller/plugins/mynewcontrollerplugin*
 
It must implement the methods *__init__*, *start_application_scaling* and *stop_application_scaling*.

- **init__(self, app_id, plugin_info)**
  - Creates a new controller which scales the given application using the given parameters.

- **start_application_scaling(self)**
  - Starts scaling for an application. This method is used as a run method by a thread.

- **stop_application_scaling(self)**
  - Stops scaling of an application.

### Example:
```
class MyNewControllerPlugin:

    def __init__(self, application_id, parameters):
        # set things up
        pass

    def start_application_scaling(self):
        # scaling logic
        pass
            
    def stop_application_scaling(self):
        # stop logic
        pass
```

5. Add the class to controller project into the plugins directory.

6. Edit ControllerBuilder (*controller/plugins/controller/builder.py*)
- Add a new condition to get_controller. Instantiate the plugin using the new condition.

### Example:
```
...
elif name == "my_new_controller_plugin":
            # prepare parameters
            return MyNewControllerPlugin(application_id, parameters)
...
```

The string used in the condition must be passed in the request to start scaling as the value to “plugin” parameter.

The example of controller plugin contained in the repository is composed of two classes: the GenericController and the GenericAlarm. The GenericAlarm contains the logic used to adjust the amount of resources allocated to applications. The GenericController dictates the pace of the scaling process. It controls when GenericAlarm is called to check the application state and when is necessary to wait.

## The Actuator plugin
Our actuation plugin (“basic”) can act on KVM virtual machines, getting and changing the amount of allocated resources through virsh. It uses SSH to access the compute nodes.

The “basic” plugin implements the following methods:

- **prepare_environment(self, vm_data)**
  - Sets up environment properties, like allocated resources, using vm_data as parameter. Usually is used before starting the application. In the “basic” plugin implementation, vm_data is a map “virtual machine to CPU cap“. The plugin uses this map to set the cap of each vm.

- **adjust_resources(self, vm_data)**
  - Modifies the environment properties using vm_data as parameter. Usually is used when the application is already running. In the “basic” plugin implementation, vm_data is a map “virtual machine to CPU cap“. The plugin uses this map to set the cap of each vm.

- **get_allocated_resources(self, vm_id)**
  - It returns the cap of the given virtual machine. In example of actuator plugin is available in the controller repository.
