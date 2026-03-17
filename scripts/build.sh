#!/bin/bash

# Builds and pushes image w/ platform linux/amd64
docker buildx build \
  --platform linux/amd64 \
  -t ghcr.io/kaitlyn-dodds/review-bot:latest \
  --push .