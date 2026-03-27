#!/bin/bash

echo "Starting run..."

# Load environment variables
source /etc/environment

docker run --rm \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v /opt/review-bot/state:/app/state \
  -v /opt/review-bot/repos:/app/repos \
  -v /opt/review-bot/logs:/app/logs \
  -v /home/kaitlyn/.ssh/id_ed25519:/home/botuser/.ssh/id_ed25519:ro \
  -v /home/kaitlyn/.ssh/known_hosts:/home/botuser/.ssh/known_hosts:ro \
  ghcr.io/kaitlyn-dodds/review-bot:latest --repo "$1" "${@:2}"
  