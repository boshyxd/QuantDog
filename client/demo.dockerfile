FROM python:3.11-bookworm AS base

ENV PYTHONUNBUFFERED=True
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

RUN apt update && apt install -y git iproute2


FROM base AS build

COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-install-workspace --package=client

COPY . /app/
RUN uv sync --frozen --package=client

FROM base AS prod


COPY --from=build /app/.venv /app/.venv
COPY --from=build /app /app

RUN mkdir -p /dev/net && mknod /dev/net/tun c 10 200 && chmod 600 /dev/net/tun

CMD [ "/app/.venv/bin/python", "/app/client/main.py" ]
