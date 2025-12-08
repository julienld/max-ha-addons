ARG BUILD_FROM=ghcr.io/hassio-addons/base/amd64:14.3.1
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Install python3
RUN \
  apk add --no-cache \
    python3 \
    py3-pip

WORKDIR /app

# Copy data for add-on
COPY run.py /app/run.py

CMD [ "python3", "/app/run.py" ]
