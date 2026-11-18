# Manaschmiede (Commander-Deckbau-Datenbank) – Server-Image (Weboberfläche, Android-/Windows-App-Zugang, Forge-Duelle)
# Basis Ubuntu 24.04 – identisch mit dem fertig gelieferten Image manaschmiede:NN
FROM ubuntu:24.04
ENV TZ=Europe/Berlin DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 LANG=C.UTF-8
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 openjdk-17-jre xvfb xauth bzip2 ca-certificates tzdata tini fonts-dejavu-core util-linux passwd \
 && rm -rf /var/lib/apt/lists/*
# Ubuntu-Images bringen teils einen Benutzer „ubuntu“ mit UID 1000 mit – vorher entfernen
RUN (userdel -r ubuntu 2>/dev/null || true) && useradd --create-home --uid 1000 cdb

# Forge: mitgelieferte Installation aus ./forge oder neueste Version von GitHub
ARG FORGE_VERSION=latest
COPY fetch_forge.py /opt/cdb/fetch_forge.py
COPY forge/ /tmp/forge-local/
RUN python3 /opt/cdb/fetch_forge.py /tmp/forge-local /opt/forge "$FORGE_VERSION" \
 && rm -rf /tmp/forge-local \
 && cd /opt/forge && rm -rf *editor*.jar forge-gui-mobile-*.jar Uninstaller *.exe res/adventure res/music \
 && chown -R cdb:cdb /opt/forge

COPY commander_db.py /opt/cdb/commander_db.py
COPY entrypoint.sh /usr/local/bin/cdb-entrypoint
RUN chmod +x /usr/local/bin/cdb-entrypoint && mkdir -p /data && chown cdb:cdb /data

ENV CDB_SERVER=1 \
    CDB_DATA_DIR=/data \
    CDB_PORT=8000 \
    CDB_FORGE_DIR=/opt/forge \
    CDB_FORGE_WRAPPER="xvfb-run -a" \
    HOME=/home/cdb

VOLUME /data
EXPOSE 8000
HEALTHCHECK --interval=60s --timeout=10s --start-period=15m --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/version', timeout=5)" || exit 1

ENTRYPOINT ["tini", "--", "cdb-entrypoint"]
CMD ["python3", "/opt/cdb/commander_db.py", "serve"]
