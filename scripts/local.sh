#!/bin/bash

echo "Starting local build and run"

# build new image
docker build -t review-bot .

echo "Build complete, triggering run script"

# run image w/ full args
docker run --rm \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v ./temp/state:/app/state \
  -v ./temp/repos:/app/repos \
  -v ./temp/logs:/app/logs \
  -v ~/.ssh/id_ed25519:/home/botuser/.ssh/id_ed25519:ro \
  -v ~/.ssh/known_hosts:/home/botuser/.ssh/known_hosts:ro \
  review-bot --repo "$1" "${@:2}"
