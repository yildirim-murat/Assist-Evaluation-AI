FROM ollama/ollama:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates coreutils \
 && rm -rf /var/lib/apt/lists/*

COPY Modelfile /opt/Modelfile
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]