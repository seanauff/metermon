#!/bin/sh

# basic run command, uses all default env vars
docker run -d seanauff/metermon

# command to set env vars to custom values
# docker run -d -e 