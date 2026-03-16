# Server Setup Documentation

## Overview

The review bot runs on Proxmox Container 104 (review-bot) running Ubuntu Server. The bot itself is packaged as a Docker image hosted on GitHub Container Registry (GHCR) (here)[https://github.com/users/kaitlyn-dodds/packages/container/package/review-bot]. The host machine is intentionally kept thin — it pulls the image and provides runtime configuration, persistent state, and the target repo. All application logic and dependencies live inside the Docker image.

Repositories and repo state is stored on the host machine (container). The image carries no persistent data. 

---

## Proxmox LXC Configuration

The container requires the following features enabled to allow Docker to run inside an LXC:

- **Nesting**: enabled
- **keyctl**: enabled

---

## Host Directory Structure

```
/opt/review-bot/
  state/              # runtime state, persists between container runs
    {repo-name}.json   # auto-created on first run
  repos/
    {repo-name}/       # git clone of the project repo
  run.sh              # script that docker runs on cron schedule
```

---

## Docker

Docker is installed on the container. The bot image is pulled from GHCR (manual step).

### Logging in to GHCR

```bash
echo $GHCR_TOKEN | docker login ghcr.io -u kaitlyn-dodds --password-stdin
```

Credentials are saved to `~/.docker/config.json` after first login — subsequent pulls do not require re-authentication.

### Pulling the latest image

```bash
docker pull ghcr.io/kaitlyn-dodds/review-bot:latest
```

### Running the container manually

```bash
/opt/review-bot/run.sh
```

Or directly:

```bash
docker run --rm \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v /opt/review-bot/state:/app/state \
  -v /opt/review-bot/repos:/app/repos \
  -v /home/kaitlyn/.ssh/id_ed25519:/root/.ssh/id_ed25519:ro \
  -v /home/kaitlyn/.ssh/known_hosts:/root/.ssh/known_hosts:ro \
  ghcr.io/kaitlyn-dodds/review-bot:latest
```

---

## run.sh

Located at `/opt/review-bot/run.sh`. This is the script the cron job calls. It sources environment variables and runs the Docker container.

```bash
#!/bin/bash

source /etc/environment

docker run --rm \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v /opt/review-bot/state:/app/state \
  -v /opt/review-bot/repos:/app/repos \
  -v /home/kaitlyn/.ssh/id_ed25519:/root/.ssh/id_ed25519:ro \
  -v /home/kaitlyn/.ssh/known_hosts:/root/.ssh/known_hosts:ro \
  ghcr.io/kaitlyn-dodds/review-bot:latest
```

Must be executable:

```bash
chmod +x /opt/review-bot/run.sh
```

---

## Cron

The bot runs nightly at 2am via cron. Edit with `crontab -e`:

```
0 2 * * * /opt/review-bot/run.sh >> /var/log/review-bot.log 2>&1
```

Logs are written to `/var/log/review-bot.log`. To view recent output:

```bash
tail -f /var/log/review-bot.log
```

---

## Environment Variables

Set in `/etc/environment` so they are available system-wide including to cron jobs. Note: no `export` keyword, no bash syntax.

```
GHCR_TOKEN=ghcr_token
GITHUB_TOKEN=github_pat
ANTHROPIC_API_KEY=anthropic_key
```

Reload after editing:

```bash
source /etc/environment
```

### What each token is for

| Variable | Purpose |
|---|---|
| `GHCR_TOKEN` | Authenticates `docker pull` from GitHub Container Registry |
| `GITHUB_TOKEN` | Authenticates GitHub REST API calls (open PRs, check PR status) |
| `ANTHROPIC_API_KEY` | Authenticates calls to the Claude API for code analysis |

---

## SSH Deploy Key

An SSH key pair was generated on the host to allow the bot to clone and push to the private Godot project repo on GitHub.

- Private key: `/home/kaitlyn/.ssh/id_ed25519`
- Public key: `/home/kaitlyn/.ssh/id_ed25519.pub` — added to the Godot repo on GitHub under **Settings → Deploy Keys**

The key is mounted read-only into the container at runtime. It is never baked into the Docker image.

To verify the key works:

```bash
ssh -T git@github.com
```

---

## Godot Project Repo

Cloned into `/opt/review-bot/repos/` using the SSH deploy key. The bot pulls the latest code from this directory at the start of each run.

To re-clone if needed:

```bash
cd /opt/review-bot/repos
git clone git@github.com:kaitlyn-dodds/your-godot-repo.git
```

---

## Re-deploying the Bot

When a new version of the bot is pushed to GHCR:

```bash
docker pull ghcr.io/kaitlyn-dodds/review-bot:latest
```

The next cron run will automatically use the new image. No other changes needed on the server.

---

## Troubleshooting

**Container fails to start**
- Check that nesting and keyctl are enabled on the LXC in Proxmox

**git pull fails inside container**
- Verify the SSH key is still valid on GitHub: Settings → Deploy Keys
- Test the key from the host: `ssh -T git@github.com`
- Check that `known_hosts` contains a GitHub entry: `ssh-keyscan github.com >> ~/.ssh/known_hosts`

**API calls failing**
- Verify environment variables are set: `cat /etc/environment`
- Check token permissions on GitHub

**No PR being opened**
- Check `/var/log/review-bot.log` for errors
- Run the container manually to see output in real time: `/opt/review-bot/run.sh`
- Check if a PR from a previous run is still open — the bot will skip opening a new one until it is resolved