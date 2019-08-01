FROM golang:1.9.2

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils \
    python-pip \
    python-setuptools \
    wget \
    git

RUN pip install paho-mqtt

RUN git clone https://github.com/bemasher/rtlamr.git /go/src/github.com/bemasher/rtlamr &&\
    git clone https://github.com/bemasher/rtltcp.git /go/src/github.com/bemasher/rtltcp &&\
    git clone https://github.com/pkg/errors.git /go/src/github.com/pkg/errors

WORKDIR /go/src/github.com/bemasher/rtlamr
ADD metermon.py .

RUN go-wrapper install

ENV MQTT_BROKER_HOST  = 127.0.0.1 \
    MQTT_BROKER_PORT  = 1883 \
    MQTT_CLIENT_ID    = "metermon" \
    MQTT_USE_AUTH     = false \
    MQTT_USERNAME     = "" \
    MQTT_PASSWORD     = "" \
    MQTT_TOPIC_PREFIX = "metermon" \
    RTL_TCP_SERVER    = 127.0.0.1 \
    RTLAMR_MSGTYPE    = "scm, scm+" \
    RTLAMR_FILTERID   = ""

ENTRYPOINT ["python", "./metermon.py"]