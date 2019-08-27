FROM golang:buster

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-setuptools \
    wget \
    git

RUN apt-get install -y --no-install-recommends python3-pip    

RUN pip3 install paho-mqtt

RUN git clone https://github.com/bemasher/rtlamr.git /go/src/github.com/bemasher/rtlamr &&\
    git clone https://github.com/bemasher/rtltcp.git /go/src/github.com/bemasher/rtltcp &&\
    git clone https://github.com/pkg/errors.git /go/src/github.com/pkg/errors

WORKDIR /go/src/github.com/bemasher/rtlamr
ADD metermon.py .

RUN go install

CMD ["python", "./metermon.py"]