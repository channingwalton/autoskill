# Trial sandbox: Claude Code + the interpreters the fixtures need, nothing else.
# Build:  docker build -t autoskill-trial docker/
# Trials mount ONLY the throwaway work dir at /work; the host filesystem,
# credentials and config are invisible.
FROM node:22-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @anthropic-ai/claude-code

RUN useradd -m agent
USER agent
# Bind-mounted /work belongs to a host uid; git must still operate on it.
RUN git config --global --add safe.directory '*'
ENV CLAUDE_CONFIG_DIR=/tmp/claude-config
WORKDIR /work
