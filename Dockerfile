FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY runner.py .
COPY configs/ configs/
COPY agents/ agents/
COPY prompts/ prompts/
COPY lib/ lib/

RUN mkdir -p /app/state /app/repos

ENTRYPOINT ["python", "runner.py"]