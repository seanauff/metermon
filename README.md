# metermon

Metermon is a dockerized [rtlamr] wrapper that connects to an existing rtl_tcp instance and outputs formatted messages over MQTT for consumption by other software (e.g. telegraf for storage in influxdb and display in grafana, or import into Home Assistant).

The script can be run using docker (takes care of all dependencies) or standalone. It is designed to run on Raspberry Pi or similar.

All credit for [rtlamr] goes to [bemasher](https://github.com/bemasher).

## Usage

1. Have a MQTT broker you can connect to. I use [Mosquitto](https://hub.docker.com/_/eclipse-mosquitto).

2. Ensure you have a rtl_tcp instance that is listening for new connections. I use this [docker container](https://github.com/radiowitness/librtlsdr-docker).

3. Run the container or script using instructions below.

4. Subscribe to the mqtt output topic, `metermon/output`, with the data consumer of your choice.

5. Process with your data consumer of choice. An example config for [Telegraf](/telegraf_example.conf) and [Home Assistant](/hass_example.yaml) is provided.

### Output format

By default, metermon outputs JSON messages to the `metermon/output` mqtt topic. The `metermon` prefix can be changed by setting the `MQTT_TOPIC_PREFIX` environment variable. Metermon will then send its output messages on `[MQTT_TOPIC_PREFIX]/output`. Note that adding a trailing `/` to `MQTT_TOPIC_PREFIX` will create an empty level.

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
|Type        | Electric   |The meter type of the received message, converted to generic utility type, e.g. "Electric", "Gas", or "Water". See [here](https://github.com/bemasher/rtlamr/blob/master/meters.md) for mapping of numeric ERT type.           |
|ID          |29163678    |The unique ID of the meter the received message originated from.           |
|Consumption |96948.54    |The current consumption value in the received message, processed into standard units (Ex.: electric meters report in 1/100 kWh, metermon divides this value by 100 to get kWh).            |
|Unit        | kWh        |The unit that metermon has converted the value to. Metermon decides this by knowing the type of meter and/or the protocol.           |

If the `METERMON_SEND_RAW` environment variable is set to `true`, metermon will send the entire unprocessed JSON message received from [rtlamr] to the `[MQTT_TOPIC_PREFIX]/raw` topic.

If the `METERMON_SEND_BY_ID` environment variable is set to `true`, metermon will also send the processed JSON message received from [rtlamr] to the `[MQTT_TOPIC_PREFIX]/[UNIQUE_ID_OF_METER]` topic. This, combined with the use of the `RTLAMR_FILTERID` environment variable, can make it easier for parsing just a few meters into Home Assistant.

### Status Messages

Metermon will report its status on the `[MQTT_TOPIC_PREFIX]/status` topic via retained messages. Metermon reports `Online` once it connects to the broker. Upon disconnect, the broker will report `Offline`.

### Performance Tuning

By adjusting the `RTLAMR_SYMBOLLENGTH` environment variable, sample rates can be modified to reduce CPU load. See documentation of this feature [here](https://github.com/bemasher/rtlamr/wiki/Symbol-Length) and a discussion of the potential performance impacts [here](https://github.com/bemasher/rtlamr/issues/57#issuecomment-246166300).

## Running via Docker

Pull the image. The `latest` tag has multiarch support, so it should pull the correct image for your system.

```shell
docker pull seanauff/metermon
```

Start the container with all default environment variables:

```shell
docker run -d seanauff/metermon
```

Start the container with modified environment variables:

```shell
docker run -d -e MQTT_BROKER_HOST=<host> -e RTL_TCP_SERVER=<server> seanauff/metermon
```

Alternativly, use docker-compose. See [docker_compose.yaml](/docker_compose.yaml)

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
| RTLAMR_MSGTYPE    |all|List of message types to listen for. See [rtlamr config](https://github.com/bemasher/rtlamr/wiki/Configuration)|
| RTLAMR_FILTERID   |               |List of meter IDs to look for. See [rtlamr config](https://github.com/bemasher/rtlamr/wiki/Configuration)       |
| RTLAMR_SYMBOLLENGTH | 72            |Adjust sample rate by setting the length of each symbol. See [rtlamr wiki](https://github.com/bemasher/rtlamr/wiki/Symbol-Length)       |
| RTLAMR_UNIQUE     | true          |Suppress duplicate messages from each meter. See [rtlamr config](https://github.com/bemasher/rtlamr/wiki/Configuration) |
| METERMON_SEND_RAW | false         |Set to `true` to enable sending the raw json from rtlamr to the `[MQTT_TOPIC_PREFIX]/raw` topic      |
| METERMON_SEND_BY_ID | false       |Set to `true` to enable sending the processed json to the `[MQTT_TOPIC_PREFIX]/[UNIQUE_ID_OF_METER]` topic. |
| METERMON_RETAIN   | false         |Controls the `retain` flag when publishing messages.|
| METERMON_ELECTRIC_DIVISOR | 100.0 |Change this to correct the electricity units that your meter reports in to kWh |
| METERMON_WATER_DIVISOR | 10.0     |Change this to correct the water units that your meter reports in to gal |

### Troubleshooting

If you receive meter messages with rtlamr but they are not showing up in metermon, it is likely that metermon doesn't recognize the "Endpoint Type" of your meter. This can be easily fixed so please open an issue with the rtlamr output and meter type (gas, electric, water) and I can add it.

### Build the image yourself

Clone the repository and build the image:

```shell
git clone https://github.com/seanauff/metermon.git
docker build -t seanauff/metermon metermon
```

[rtlamr]: https://github.com/bemasher/rtlamr
