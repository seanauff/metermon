# metermon

Metermon is a dockerized [rtlamr] wrapper that connects to an existing rtl_tcp instance and outputs formatted messages over MQTT for consumption by other software (e.g. telegraf for storage in influxdb and display in grafana).

The script can be run using docker (takes care of all dependencies) or standalone. It is design to run on Raspberry Pi or similar.

All credit for [rtlamr] goes to [bemasher](https://github.com/bemasher).

## Usage

1. Ensure you have a rtl_tcp instance that is listening for new connections. I have been using this [docker container](https://github.com/radiowitness/librtlsdr-docker).

2. Run the container or script using instructions below.

3. Subscribe to the mqtt output topic, `metermon/output`, with the data consumer of your choice.

4. Process with your data consumer of choice. An [example telegraf config](/telegraf_example.conf) is provided.

## Output format

By default, metermon outputs JSON messages to the `metermon/output` mqtt topic. The `metermon` prefix can be changed to anything by setting the `MQTT_TOPIC_PREFIX` environment variable. Metermon will then send its output messages on `[MQTT_TOPIC_PREFIX]/output`. Note that adding a trailing `/` to `MQTT_TOPIC_PREFIX` will create an empty level.

|Value of MQTT_TOPIC_PREFIX|mqtt output topic|
|--------------------------|-----------------|
|`metermon`                |`metermon/output`|
|`sensors/meters`          |`sensors/meters/output`|
|`sensors/meters/`         |`sensors/meters//output`|

### JSON keys

The JSON message has a single level with the following keys:

|Key         |Example     |Description|
|------------|------------|-----------|
|Protocol    | SCM        |The protocol of the received message. See [here](https://github.com/bemasher/rtlamr/wiki/Protocol) for the list.          |
|Type        |  5         |The meter type of the received message. See [here](https://github.com/bemasher/rtlamr/blob/master/meters.md).           |
|ID          |29163678    |The unique ID of the meter the received message originated from.           |
|Consumption |96948.54    |The current consumption value in the received message, processed into standard units (Ex.: electric meters report in 1/100 kWh, metermon divides this value by 100 to get kWh).            |
|Unit        | kWh        |The unit that metermon has converted the value to. Metermon decides this by knowing the type of meter and/or the protocol.           |

If the `METERMON_SEND_RAW` environment variable is set to `true`, metermon will send the entire unprocessed JSON message received from [rtlamr] to the `[MQTT_TOPIC_PREFIX]/raw` topic.

## Running via Docker

Pull the image. If using raspberry pi or similar use `arm` in place of `[tag]`. The `latest` tag will pull the `amd64` image:

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
| RTLAMR_MSGTYPE    |scm, scm+|List of message types to listen for. Currently only scm, scm+, idm, netidm supported. See [rtlamr config](https://github.com/bemasher/rtlamr/wiki/Configuration)|
| RTLAMR_FILTERID   |               |List of meter IDs to look for. See [rtlamr config](https://github.com/bemasher/rtlamr/wiki/Configuration)       |
| METERMON_SEND_RAW | false         |Set to `true` to enable sending the raw json from rtlamr on another topic      |

### Build the image yourself

Clone the repository and build the image:

```shell
git clone https://github.com/seanauff/metermon.git
docker build -t seanauff/metermon WOL-proxy
```

[rtlamr]: https://github.com/bemasher/rtlamr
