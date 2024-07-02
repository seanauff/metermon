#!/bin/bash
docker buildx build --tag seanauff/metermon:latest --platform linux/arm/v7,linux/arm64/v8,linux/amd64 --builder container --push .
