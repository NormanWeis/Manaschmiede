#!/bin/sh
# Startet als root, richtet die Rechte für das Datenverzeichnis ein und läuft dann als unprivilegierter Benutzer „cdb“.
set -e
DATA="${CDB_DATA_DIR:-/data}"
mkdir -p "$DATA"
chown -R cdb:cdb "$DATA" 2>/dev/null || true
chmod -R u+rwX "$DATA" 2>/dev/null || true
chown cdb:cdb "${HOME:-/home/cdb}" 2>/dev/null || true
exec setpriv --reuid=cdb --regid=cdb --init-groups "$@"
