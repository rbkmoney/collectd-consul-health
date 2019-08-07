# collectd Consul Health Plugin

A consul collectd plugin which users can use to send states of health checks for every service on a node. State is obtained from the cluster-wide view, not the local view. Provides metrics of the following form:

```
gauge service.{service}.{status}
gauge node.{status}
```

...where `status` is either `passing`, `warning` or `critical`.

Almost entirely "inspired" by [collectd-consul](https://github.com/signalfx/collectd-consul).

## Installation

1. Checkout this repository somewhere on your system accessible by collectd. The suggested location is `/usr/share/collectd/`
1. Configure the plugin (see below)
1. Restart collectd

## Requirements

* collectd 4.9 or later (for the Python plugin)
* Python 3.6 or later
* Consul 0.7.0 or later

## Configuration

Next configure the collectd-consul plugin by using the below given example configuration file as a guide, provide values for the configuration options listed in the table that make sense for your environment.

**Configuration Option** | **Description** | **Default Value**
:------------------------|:----------------|:------------------
ApiHost	| IP address or DNS to which the Consul HTTP/HTTPS server binds to on the instance to be monitored | `localhost`
ApiPort |	Port to which the Consul HTTP/HTTPS server binds to on the instance to be monitored |	`8500`
ApiProtocol | Possible values - *http* or *https*	| `http`
AclToken | Consul ACL token. | None
CaCertificate | If Consul server has https enabled for the API, provide the path to the CA Certificate. | None
ClientCertificate | If client-side authentication is enabled, provide the path to the certificate file. | None
ClientKey | If client-side authentication is enabled, provide the path to the key file. | None
Debug | Possible values - *true* or *false*<br> | `false`

Note that multiple Consul instances can be configured in the same file.

```
LoadPlugin python

<Plugin python>
  ModulePath "/var/share/collectd/consul-health"

  Import consul_health_plugin
  <Module consul_health_plugin>
    ApiHost "localhost"
    ApiPort 8500
    ApiProtocol "http"
    Debug true
  </Module>
  ...

</Plugin>
```
