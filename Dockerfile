FROM golang:1.9.2

RUN apt-get update && apt-get install -y --no-install-recomends \
    python-pip \
    wget \
    git

RUN pip install paho-mqtt

RUN git clone https://github.com/bemasher/rtlamr.git /go/src/github.com/bemasher/rtlamr

WORKDIR /go/src/github.com/bemasher/rtlamr
ADD metermon.py .

RUN go-wrapper install

ENTRYPOINT ["python", "./metermon.py"]