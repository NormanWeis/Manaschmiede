# Manaschmiede im Internet betreiben (Docker)

Damit läuft die Commander-Datenbank auf einem Server und ist von überall erreichbar – im Browser,
als installierte App auf Android und Windows und über die Android-App. Mit Anmeldung, eigenen Decks
je Benutzer und Forge-Duellen auf dem Server.

## Was du brauchst
- Einen Linux-Server mit **mind. 2 CPU-Kernen und 4 GB RAM** (z. B. ein kleiner Cloud-Server bei einem
  deutschen Anbieter) – Forge-Duelle brauchen Rechenleistung und Speicher.
- **Docker** mit Compose (Installation: `curl -fsSL https://get.docker.com | sh`).
- Für Variante **HTTPS**: eine (Sub-)Domain, z. B. `commander.deine-domain.de`, deren DNS-Eintrag (A-Record)
  auf die IP-Adresse des Servers zeigt; Ports 80 und 443 müssen offen sein.
- Für Variante **Tunnel** (z. B. zu Hause, ohne offene Ports): ein kostenloses Cloudflare-Konto mit Domain.

## Das Image
Das fertige Image liegt in der GitHub Container Registry:

| Tag | Inhalt |
|---|---|
| `ghcr.io/normanweis/manaschmiede:47` | Version 47 (fest) |
| `ghcr.io/normanweis/manaschmiede:latest` | immer die neueste gebaute Version |

Enthalten: Ubuntu 24.04, Python 3.12, Java 17, Xvfb und Forge 2.0.16 – für x86_64-/amd64-Server.
Das Image ist **öffentlich**: `docker pull`, `docker run` und `docker compose pull` funktionieren ohne Anmeldung.

*Optional – nur nötig, wenn das Paket wieder auf privat steht oder du ein eigenes privates Image verwendest:*
auf GitHub unter *Settings → Developer settings → Personal access tokens → Tokens (classic)* einen Token mit dem
Recht `read:packages` erstellen und auf dem Server einmal anmelden:
```
docker login ghcr.io -u NormanWeis        # als Passwort den Token eingeben
```

## Variante 1: docker run (ein Container, ohne HTTPS)
Zum Ausprobieren oder wenn schon ein eigener Reverse-Proxy (nginx, Traefik, Caddy) davor läuft:
```
docker run -d --name manaschmiede --restart unless-stopped \
  -p 8000:8000 \
  -v manaschmiede_data:/data \
  -e CDB_ADMIN_USER=admin \
  -e CDB_ADMIN_PASSWORD='ein-langes-eigenes-passwort' \
  -e CDB_MAX_DUELS=1 -e CDB_MAX_GAMES=20 \
  --memory 4g \
  ghcr.io/normanweis/manaschmiede:47
```
- Aufruf: `http://SERVER-IP:8000`, Anmeldung mit dem Admin-Zugang.
- Alle Daten (Kartendaten, Decks, Benutzer) liegen im Volume `manaschmiede_data` und bleiben bei Updates erhalten.
- Beim ersten Start lädt der Server Kartendaten, Precons und Regeln (1–3 Minuten); erst danach ist die Seite
  erreichbar. Fortschritt: `docker logs -f manaschmiede`
- Ohne HTTPS funktionieren die Live-Kamera im Browser und die Installation als Web-App nicht; für den Dauerbetrieb
  im Internet daher Variante 2 oder ein eigener Reverse-Proxy mit HTTPS. Ein Proxy muss den Header
  `X-Forwarded-Proto: https` setzen, dann werden die Anmelde-Cookies als „Secure“ markiert.

| Aufgabe | Befehl |
|---|---|
| Logs | `docker logs -f manaschmiede` |
| Neue Version | `docker pull ghcr.io/normanweis/manaschmiede:47`, Container löschen (`docker rm -f manaschmiede`) und mit neuem Tag erneut starten |
| Sicherung | `docker cp manaschmiede:/data/cards.db ./sicherung-$(date +%F).db` |
| Benutzer anlegen | `docker exec -it manaschmiede python3 /opt/cdb/commander_db.py adduser NAME` |

## Variante 2: docker compose (Dauerbetrieb mit HTTPS oder Tunnel)
1. Ordner `server` auf den Server kopieren (z. B. mit WinSCP, oder `git clone` des Repositorys) und dort eine Konsole öffnen.
2. Einstellungen anlegen: `cp .env.example .env` und `.env` bearbeiten (`nano .env`):
   Domain, E-Mail, **Admin-Benutzer und ein langes Passwort**. `CDB_IMAGE` gibt an, welches Image verwendet wird.
3. Starten:
   ```
   docker compose pull
   docker compose up -d
   ```
   Fortschritt: `docker compose logs -f app` – beim ersten Start werden Kartendaten, Precons und Regeln geladen.
4. `https://deine-domain.de` öffnen und mit dem Admin-Zugang anmelden. Das HTTPS-Zertifikat holt Caddy
   automatisch und erneuert es selbst.

Selbst bauen statt das fertige Image zu nehmen: `docker compose up -d --build`. Optional vorher deinen
Forge-Installer (`forge-installer-2.0.16.jar`) oder deine Forge-Installation in den Ordner `forge` legen –
sonst lädt der Bau Forge von GitHub (Version über `--build-arg FORGE_VERSION=…`, Standard: neueste).

## Image aus einer Datei laden (ohne Internetzugriff auf ghcr.io)
Mit den Dateien `manaschmiede-NN-docker-image.tar.gz.teil0/1`:
```
cat manaschmiede-*-docker-image.tar.gz.teil* > manaschmiede-image.tar.gz
docker load -i manaschmiede-image.tar.gz      # ergibt das Image manaschmiede:NN
```
Danach bei `docker run` den Namen `manaschmiede:NN` verwenden bzw. in `.env` `CDB_IMAGE=manaschmiede:NN` setzen.

## Benutzer
- Neue Benutzer legt der Admin in der Oberfläche an: oben **„Benutzer verwalten“**.
- Alternativ in der Konsole: `docker compose exec app python3 /opt/cdb/commander_db.py adduser NAME`
  (mit `--admin` für Administratoren).
- Jeder Benutzer hat eigene gespeicherte Decks; Passwörter werden nur als sicherer Hash gespeichert.

## Bisherige Daten übernehmen (optional)
Deine lokale `cards.db` (mit gespeicherten Decks) auf den Server kopieren und dann:
```
docker compose cp cards.db app:/data/cards.db
docker compose restart app
```
Lokal gespeicherte Decks gehören danach dem ersten Administrator.

## Variante Tunnel (ohne offene Ports, z. B. Server zu Hause)
1. In Cloudflare unter *Zero Trust → Networks → Tunnels* einen Tunnel anlegen, als Dienst
   `http://app:8000` und deine Subdomain eintragen, den **Tunnel-Token** kopieren.
2. In `.env`: `COMPOSE_PROFILES=tunnel` und `TUNNEL_TOKEN=…` setzen.
3. `docker compose pull && docker compose up -d` – HTTPS übernimmt Cloudflare.

## Betrieb
| Aufgabe | Befehl |
|---|---|
| Status / Logs | `docker compose ps` · `docker compose logs -f app` |
| Neu starten | `docker compose restart app` |
| Sicherung der Daten | `docker compose cp app:/data/cards.db ./sicherung-$(date +%F).db` |
| Neue Version | in `.env` `CDB_IMAGE` auf das neue Tag setzen, dann `docker compose pull && docker compose up -d` |
| Selbst gebaute Version | neue `commander_db.py` in den Ordner kopieren, dann `docker compose up -d --build` |
| Neue Forge-Version | `docker compose build --no-cache app && docker compose up -d` |
| Stoppen | `docker compose down` (Daten bleiben im Volume erhalten) |

Regeln, Precons und Kartendaten aktualisieren sich bei jedem Start und zusätzlich **jede Nacht um 4:07 Uhr**
(einstellbar mit `CDB_UPDATE_HOUR`). Die Kartendaten mit den Preisen werden dabei täglich neu geladen, sobald
Scryfall neuere hat – das hält Preisalarm, Wunschliste und Wertverlauf aktuell (rund 150 MB Download pro Tag).
Die **Euro-Preise** kommen aus der öffentlichen Cardmarket-Preisliste (`price_guide_1.json` und
`products_singles_1.json`, rund 40 MB), die ebenfalls jede Nacht neu geladen wird. Ist sie nicht erreichbar,
nimmt der Server die beiden Dateien aus dem Datenordner (Volume), sonst bleibt die letzte Preisliste gültig.
In der Oberfläche steht überall „Preise: Cardmarket“ mit Datum der Preisliste – so verlangt es Cardmarket.
Admins sehen oben den Stand und die nächste automatische Prüfung und können „Jetzt aktualisieren“ klicken.

Neue **Programmversionen** holt der Server nicht von selbst: nach einer neuen Version
`docker compose pull && docker compose up -d` ausführen (bei `CDB_IMAGE=…:latest` genügt das immer).

## Einstellungen (.env)
| Variable | Bedeutung | Standard |
|---|---|---|
| `CDB_IMAGE` | verwendetes Docker-Image | `ghcr.io/normanweis/manaschmiede:47` |
| `CDB_DOMAIN`, `ACME_EMAIL` | Domain und E-Mail für HTTPS | – |
| `CDB_ADMIN_USER`, `CDB_ADMIN_PASSWORD` | Admin wird bei jedem Start angelegt/gesetzt | – |
| `CDB_MAX_DUELS` | gleichzeitige Forge-Duelle (weitere warten in einer Schlange) | 1 |
| `CDB_MAX_GAMES` | höchstens so viele Partien je Duell | 20 |
| `CDB_FORGE_XMX` | Java-Speicher je Duell | 2048m |
| `CDB_MEM_LIMIT` | Speichergrenze des Containers | 4g |
| `CDB_SESSION_DAYS` | Anmeldung bleibt so viele Tage gültig | 30 |
| `CDB_UPDATE_HOUR` | Stunde der täglichen Prüfung auf neue Daten (0–23, `off` = aus) | 4 |
| `CDB_CARDS_MAX_AGE_DAYS` | Kartendaten neu laden ab diesem Alter in Tagen, wenn Scryfall neuere hat | 1 (Server), 7 (Windows) |
| `CDB_CM_PRICE_URL`, `CDB_CM_PRODUCTS_URL` | Adressen der Cardmarket-Preisliste und Produktliste | Cardmarket-Downloads |
| `TZ` | Zeitzone für Uhrzeit und Zeitstempel | Europe/Berlin |

Fehlt ein Admin in `.env`, erzeugt der Server beim ersten Start einen Benutzer „admin“ mit zufälligem
Passwort und schreibt es ins Log (`docker compose logs app`).

## Sicherheit
- Alle Seiten und Funktionen erfordern eine Anmeldung; Fehlversuche führen zu einer zunehmenden Sperre.
- Verbindungen laufen ausschließlich verschlüsselt (HTTPS), Sitzungs-Cookies sind gegen Auslesen geschützt.
- Der Server ruft beim Import nur bekannte Deckseiten ab (Archidekt, Moxfield, MTGGoldfish, TappedOut,
  Deckstats) – keine beliebigen Adressen. Funktionen, die Dateien auf dem Server schreiben würden, sind gesperrt.
- Das Programm läuft im Container als eingeschränkter Benutzer, nicht als root.
- Ein starkes Admin-Passwort verwenden und regelmäßig Sicherungen ziehen.

## Rechtliches (bitte vor einer öffentlichen Freigabe beachten)
Für dich, Freunde oder deine Spielgruppe hinter einer Anmeldung ist der Betrieb unkritisch. Soll der Dienst
**öffentlich** für alle angeboten werden, prüfe bitte vorher insbesondere:
- **Wizards of the Coast:** Magic ist eine Marke von Wizards; für Fan-Projekte gilt deren *Fan Content Policy*.
  Der Text der Comprehensive Rules gehört Wizards – öffentlich besser verlinken statt selbst bereitstellen.
- **Scryfall:** Kartendaten und -bilder nach den Scryfall-Nutzungsbedingungen (Quellenangabe, keine Bezahlschranke).
- **Forge** steht unter der GPL-3.0: bei Weitergabe des Images den Quellcode-Hinweis beilegen.
- **Datenschutz (DSGVO):** bei fremden Nutzern Impressum/Datenschutzerklärung, Umgang mit Konten und Logs.
