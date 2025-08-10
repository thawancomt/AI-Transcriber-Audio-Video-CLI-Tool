#Don't worth
FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y curl ca-certificates

ENV PATH="/root/.local/bin:${PATH}"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv python pin 3.12
RUN uv sync --no-cache

COPY . .

# Criar diretórios de trabalho
RUN mkdir -p /app/workspace

# O script vai trabalhar no /app/workspace
WORKDIR /app/workspace
CMD ["uv", "run", "/app/app.py"]