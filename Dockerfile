FROM golang:buster

LABEL org.opencontainers.image.source=https://github.com/seanauff/metermon
LABEL org.opencontainers.image.description="Metermon is a dockerized rtlamr wrapper that connects to an existing rtl_tcp instance and outputs formatted messages over MQTT for consumption by other software."
LABEL org.opencontainers.image.licenses=MIT

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-setuptools \
    python3-pip \
    wget \
    git 

RUN pip3 install paho-mqtt typing-extensions

RUN git clone https://github.com/bemasher/rtlamr.git /go/src/github.com/bemasher/rtlamr &&\
    git clone https://github.com/bemasher/rtltcp.git /go/src/github.com/bemasher/rtltcp &&\
    git clone https://github.com/pkg/errors.git /go/src/github.com/pkg/errors

WORKDIR /go/src/github.com/bemasher/rtlamr

RUN go install

ADD metermon.py .

CMD ["python3", "-u", "./metermon.py"]
