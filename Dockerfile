FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} botuser && useradd -m -u ${UID} -g ${GID} botuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY runner.py .
COPY configs/ configs/
COPY agents/ agents/
COPY prompts/ prompts/
COPY lib/ lib/

ENV GIT_AUTHOR_NAME="Review Bot"                                                                                                                                
ENV GIT_AUTHOR_EMAIL="review-bot@noreply"
ENV GIT_COMMITTER_NAME="Review Bot"                                                                                                                             
ENV GIT_COMMITTER_EMAIL="review-bot@noreply"
ENV REPO_DIR="/app/repos"
ENV LOG_DIR="/app/logs"

RUN mkdir -p /app/state /app/repos /app/logs && chown -R botuser:botuser /app

USER botuser

ENTRYPOINT ["python", "runner.py"]