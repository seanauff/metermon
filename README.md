# metermon

Metermon is a dockerized [rtlamr] wrapper that connects to an existing rtl_tcp instance and outputs formatted messages over MQTT for consumption by other software (e.g. telegraf for storage in influxdb and display in grafana).

The script can be run using docker (takes care of all dependencies) or standalone. It is design to run on Raspberry Pi or equivalent.

All credit for [rtlamr] goes to [bemasher](https://github.com/bemasher).

## Usage

1. Ensure you have a rtl_tcp instance that is listening for new connections.

2. Run the container or script using instructions below.

3. Subscribe to the output topic, `metermon/output`, with the data consumer of your choice.

## Running via Docker

Pull the image using either `amd64` or `arm` in place of `[tag]`:

```shell
docker pull seanauff/metermon:[tag]
```

Start the container with all default environment variables:

```shell
docker run -d seanauff/metermon:[tag]
```

Start the container with modified environment variables:

```shell
docker run -d -e MQTT_BROKER_HOST=[host] -e RTL_TCP_SERVER=[server] seanauff/metermon:[tag]
```

### Environment Variables

| Variable          | Default Value | Notes |
|-------------------|---------------|-------|
| MQTT_BROKER_HOST  |  127.0.0.1    |IP or hostname of MQTT broker       |
| MQTT_BROKER_PORT  |  1883         |Port of MQTT broker       |
| MQTT_CLIENT_ID    |  metermon   |Change this if the default is already in use by another client       |
| MQTT_USERNAME     |               |Username for connecting to MQTT broker when using auth. TLS not currently supported       |
| MQTT_PASSWORD     |               |Password for connecting to MQTT broker when using auth. TLS not currently supported       |
| MQTT_TOPIC_PREFIX | metermon    |Set the prefix to use for the MQTT topic that messages are sent to       |
| RTL_TCP_SERVER    |127.0.0.1:1234 |`server:port` that your rtl_tcp instance is listening on |
| RTLAMR_MSGTYPE    |scm, scm+|List of message types to listen for. Currently only scm, scm+ supported. See [rtlamr config](https://github.com/bemasher/rtlamr/wiki/Configuration)|
| RTLAMR_FILTERID   |               |List of meter IDs to look for. See [rtlamr config](https://github.com/bemasher/rtlamr/wiki/Configuration)       |
| METERMON_SEND_RAW | false         |Set to `true` to enable sending the raw json from rtlamr on another topic      |

### Build the image yourself

Clone the repository and build the image:

```shell
git clone https://github.com/seanauff/metermon.git
docker build -t seanauff/metermon WOL-proxy
```

[rtlamr]: https://github.com/bemasher/rtlamr
