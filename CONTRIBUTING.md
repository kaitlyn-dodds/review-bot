
## Docker Commands

Builds the image and tags it as 'review-bot'.
```
docker build -t review-bot .
```

Runs the container and removes it automatically on exit
```
docker run --rm review-bot
```

Log in to GHCR locally
```
echo $env:GHCR_TOKEN | docker login ghcr.io -u kaitlyn-dodds --password-stdin
```

Log out of GHCR
```
docker logout ghcr.io
```

Build and tag image for GCHR
```
docker build -t ghcr.io/kaitlyn-dodds/review-bot:latest .
```

Push image to GHCR
```
docker push ghcr.io/kaitlyn-dodds/review-bot:latest
```

Pull image from GHCR
```
docker pull ghcr.io/kaitlyn-dodds/review-bot:latest
```

Run the image pulled from GHCR
```
docker run --rm ghcr.io/kaitlyn-dodds/review-bot:latest
```

Docker run command:
```
docker run --rm \
    -e GITHUB_TOKEN=$GITHUB_TOKEN \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -v /opt/review-bot/state:/app/state \
    -v /opt/review-bot/repos:/app/repos \
    <!-- -v ~/.ssh:/root/.ssh:ro \ -->
    -v /home/kaitlyn/.ssh/id_ed25519:/root/.ssh/id_ed25519:ro \
    -v /home/kaitlyn/.ssh/known_hosts:/root/.ssh/known_hosts:ro \
    ghcr.io/your-username/review-bot:latest
``` 
