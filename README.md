# Asperathos - Controller
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview
The **Controller** is responsible for adjusting the amount of resources allocated to the virtual infrastructure where the applications run, in order to guarantee application’s QoS.

**Asperathos** was developed by the [**LSD-UFCG**](https://www.lsd.ufcg.edu.br/#/) *(Distributed Systems Laboratory at Federal University of Campina Grande)* as one of the existing tools in **EUBra-BIGSEA** ecosystem.

**EUBra-BIGSEA** is committed to making a significant contribution to the **cooperation between Europe and Brazil** in the *area of advanced cloud services for Big Data applications*. See more about in [EUBra-BIGSEA website](http://www.eubra-bigsea.eu/).

To more info about **Controller** and how does it works in **BIGSEA Asperathos environment**, see [details.md](docs/details.md) and [asperathos-workflow.md](docs/asperathos-workflow.md).

## How does it works?
The controller is implemented following a **plugin architecture**, providing flexibility to add or remove plugins when necessary. It works with usage of three types of plugins: **Actuator**, **Controller** and **Metric Source**.
* The **Controller**, based on metrics such as application progress and CPU usage, decides the amount of resources to allocate to the applications.
* The **Actuator** is responsible for connecting to the underlying infrastructure (such as a Mesos or an OpenStack Sahara platform) and triggering the commands or API calls that allocate or deallocate resources, based on the Controller’s requests.
* The **Metric Source** plugin is responsible for getting application metrics from a metric source, such as Monasca, and returning them to the Controller.

## How to develop a plugin?
See [plugin-development.md](docs/plugin-development.md).

## Requirements
* Python 2.7 or Python 3.5
* Linux packages: python-dev and python-pip
* Python packages: setuptools, tox and flake8

To **apt** distros, you can use [pre-install.sh](pre-install.sh) to install the requirements.

## Install
Clone the [Controller repository](https://github.com/ufcg-lsd/asperathos-controller) in your machine.

### Configuration
A configuration file is required to run the Controller. **Edit and fill your controller.cfg in the root of Controller directory.** Make sure you have fill up all fields before run.
You can find a template in [config-example.md](docs/config-example.md). 

### Run
In the Controller root directory, start the service using run script:
```
$ ./run.sh
```

Or using tox command:
```
$ tox -e venv -- controller
```

## Controller REST API
Endpoints are avaliable on [restapi-endpoints.md](docs/restapi-endpoints.md) documentation.

## Avaliable plugins
### Controller
* [Kube Jobs](docs/plugins/controller/kubejobs.md)

### Actuator
* [K8s Replicas](docs/plugins/actuator/k8s-replicas.md)

### Metric source
* [Monasca](docs/plugins/metric_source/monasca-metric-source.md)
* [Redis]
