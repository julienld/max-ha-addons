ARG BUILD_FROM
FROM $BUILD_FROM

# Install dependencies based on Alpine
# ttyd is often in community or edge/community repo
RUN apk add --no-cache \
    python3 \
    py3-pip \
    nodejs \
    npm \
    ttyd \
    git \
    bash \
    curl \
    nano

# Install Google Gemini CLI globally
RUN npm config set strict-ssl false && \
    npm config set fetch-retries 5 && \
    npm config set fetch-retry-factor 2 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm install -g @google/gemini-cli \
    --no-audit \
    --no-fund \
    --foreground-scripts \
    --loglevel verbose

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
