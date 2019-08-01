# metermon

Metermon is a dockerized rtlamr wrapper that connects to an existing rtl_tcp instance and outputs formatted messages over MQTT for consumption by other software (e.g. telegraf for storage into influxdb and display in grafana).  

All credit for rtlamr goes to bemasher: https://github.com/bemasher/rtlamr

### Enviromental Variables
| Variable          | Default Value | Notes |
|-------------------|---------------|-------|
| MQTT_BROKER_HOST  |  127.0.0.1    |IP or hostname of MQTT broker       |
| MQTT_BROKER_PORT  |  1883         |Port of MQTT broker       |
| MQTT_CLIENT_ID    |  "metermon"   |Change this if the default is already in use by another client       |
| MQTT_USERNAME     |               |Username for connecting to MQTT broker when using auth. TLS not currently supported       |
| MQTT_PASSWORD     |               |Password for connecting to MQTT broker when using auth. TLS not currently supported       |
| MQTT_TOPIC_PREFIX | "metermon"    |       |
| RTL_TCP_SERVER    |127.0.0.1:1234 |       |
| RTLAMR_MSGTYPE    | "all"         |see https://github.com/bemasher/rtlamr/wiki/Configuration       |
| RTLAMR_FILTERID   |               |see https://github.com/bemasher/rtlamr/wiki/Configuration       |
| METERMON_SEND_RAW | false         |set to ```true``` to enable sending the raw json from rtlamr on another topic      |
