#!/bin/bash
# Script based on this guide: https://medium.com/@life-is-short-so-enjoy-it/docker-how-to-build-and-push-multi-arch-docker-images-to-docker-hub-64dea4931df9
docker buildx build --tag seanauff/metermon:latest --platform linux/arm/v7,linux/arm64/v8,linux/amd64 --builder container --push .
