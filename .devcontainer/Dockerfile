FROM mcr.microsoft.com/devcontainers/python:3.11
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    ca-certificates \
    nodejs \
    npm \
 && rm -rf /var/lib/apt/lists/*
USER vscode
