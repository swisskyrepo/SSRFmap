FROM python:3.12.4-alpine

COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /bin/

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN apk update

# Install curl with outdated libcurl
RUN apk add --update build-base cmake c-ares-dev
RUN cp examples/curl-7.71.0.tar.gz /tmp
RUN tar -xvf /tmp/curl-7.71.0.tar.gz -C /tmp/
RUN cd /tmp/curl-7.71.0 && ./configure --enable-ares && make && make install

# Install locked runtime dependencies
RUN uv sync --frozen --no-default-groups

# Downloaded files are written here after privileges are dropped.
RUN mkdir -p /usr/src/app/loot && chown 1000:1000 /usr/src/app/loot

# Keep uv runtime state in a location writable by the unprivileged user.
ENV UV_CACHE_DIR=/tmp/uv-cache

ENTRYPOINT ["uv", "run", "--no-sync", "python3"]
