# metermon

Metermon is a dockerized rtlamr wrapper that connects to an existing rtl_tcp instance and outputs formatted messages over MQTT for consumption by other software (e.g. telegraf for storage into influxdb and display in grafana).  

All credit for rtlamr goes to bemasher: https://github.com/bemasher/rtlamr

### Enviromental Variables
| Variable          | Default Value | Notes |
|-------------------|---------------|-------|
| MQTT_BROKER_HOST  |  127.0.0.1    |       |
| MQTT_BROKER_PORT  |  1883         |       |
| MQTT_CLIENT_ID    |  "metermon"   |       |
| MQTT_USE_AUTH     |  false        |       |
| MQTT_USERNAME     |               |       |
| MQTT_PASSWORD     |               |       |
| MQTT_TOPIC_PREFIX | "metermon"    |       |
| RTL_TCP_SERVER    |127.0.0.1:1234 |       |
| RTLAMR_MSGTYPE    | "all"         |       |
| RTLAMR_FILTERID   |               |       |
