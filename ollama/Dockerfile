FROM ollama/ollama:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl ca-certificates coreutils \
 && rm -rf /var/lib/apt/lists/*

COPY Modelfile /opt/Modelfile
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh \
 && sed -i '1s/^\xEF\xBB\xBF//' /usr/local/bin/docker-entrypoint.sh \
 && chmod +x /usr/local/bin/docker-entrypoint.sh
 
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]