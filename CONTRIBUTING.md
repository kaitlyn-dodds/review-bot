
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
