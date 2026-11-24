# Manaschmiede (Commander-Deckbau-Datenbank), Version 60

| Teil | Inhalt | Anleitung |
|---|---|---|
| Windows (lokal) | Ordner `windows`: `commander_db_v60.py` und Startdateien, läuft ohne Server | `windows/README-Windows.md` |
| Server (Internet) | Ordner `server`: Docker-Image mit Python, Java und Forge, HTTPS über Caddy oder Cloudflare-Tunnel | `server/README-Server.md` |
| Android | Web-App direkt vom Server installieren oder eigene APK bauen (Ordner `android`, Bau automatisch bei GitHub) | `android/README-Android.md` |
| Windows-App vom Server | Serveradresse in Edge oder Chrome öffnen, Installieren-Symbol in der Adressleiste anklicken; die App erscheint mit eigenem Fenster im Startmenü | |

Alle Varianten zeigen dieselben Inhalte und Funktionen. Auf dem Server kommen Anmeldung, Benutzerkonten
und getrennte Decks je Benutzer dazu.

## Schnellstart mit Docker
Das fertige Image heißt `ghcr.io/normanweis/manaschmiede:60` (auch `:latest`). Es enthält Ubuntu 24.04, Python,
Java 17 und Forge 2.0.16 und läuft auf x86_64-/amd64-Servern. Das Image ist öffentlich, Herunterladen geht ohne Anmeldung:
```
docker pull ghcr.io/normanweis/manaschmiede:60
```

Mit `docker run` startet ein einzelner Container ohne HTTPS, zum Ausprobieren oder hinter einem eigenen Reverse-Proxy:
```
docker run -d --name manaschmiede --restart unless-stopped \
  -p 8000:8000 \
  -v manaschmiede_data:/data \
  -e CDB_ADMIN_USER=admin -e CDB_ADMIN_PASSWORD='ein-langes-eigenes-passwort' \
  ghcr.io/normanweis/manaschmiede:60
```
Danach `http://SERVER-IP:8000` öffnen und als `admin` anmelden.

Für den Dauerbetrieb mit HTTPS (Caddy) oder Cloudflare-Tunnel gibt es `docker compose`:
```
cd server
cp .env.example .env && nano .env      # Domain, E-Mail, Admin-Zugang eintragen
docker compose pull
docker compose up -d
```
Einstellungen, Benutzer, Sicherung und Updates beschreibt [`server/README-Server.md`](server/README-Server.md).

## Inhalt des Repositorys
| Ordner | Inhalt |
|---|---|
| `server/` | Programm, Dockerfile, docker-compose, Caddy, Anleitung für den Serverbetrieb |
| `android/` | Android-App (WebView, Kartenscanner, Dauerscan) |
| `windows/` | Programm und Startdateien für den lokalen Betrieb unter Windows |
| `docker/` | Anleitung und Zusammenfüge-Datei für das Image als Datei in zwei Teilen |
| `docs/` | Funktionsvergleich mit anderen Apps, Punktetabelle, Versionsverlauf, bekannte Grenzen |
| `archiv/` | frühere Programmversionen 6–59 |
| `.github/workflows/` | automatischer Bau von Docker-Image (ghcr.io) und Android-APK |

Downloads (Docker-Image als Datei, APK, Windows-Paket) stehen unter Releases im Repository. Ein neues Release
entsteht über Actions → „Release erstellen“ → Run workflow mit der Versionsnummer. APK und Image werden dabei frisch gebaut.
