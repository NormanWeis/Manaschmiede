# Manaschmiede (Commander-Deckbau-Datenbank) – Version 58

| Teil | Inhalt | Anleitung |
|---|---|---|
| **Windows (lokal)** | Ordner `windows`: `commander_db_v58.py` + Startdateien – läuft ohne Server | `windows/README-Windows.md` |
| **Server (Internet)** | Ordner `server`: Docker-Image mit Python, Java, Forge, HTTPS über Caddy oder Cloudflare-Tunnel | `server/README-Server.md` |
| **Android** | installierbare Web-App direkt vom Server **oder** eigene APK (Ordner `android`, Bau automatisch bei GitHub) | `android/README-Android.md` |
| **Windows-App vom Server** | Serveradresse in Edge/Chrome öffnen → Installieren-Symbol in der Adressleiste → eigenes App-Fenster im Startmenü | – |

Alle Varianten zeigen dieselben Inhalte und Funktionen. Auf dem Server kommen Anmeldung, Benutzerkonten
und getrennte Decks je Benutzer dazu.

## Schnellstart mit Docker
Fertiges Image: **`ghcr.io/normanweis/manaschmiede:58`** (auch `:latest`) – Ubuntu 24.04, Python, Java 17, Forge 2.0.16,
für x86_64-/amd64-Server. Das Image ist **öffentlich** – Herunterladen ohne Anmeldung:
```
docker pull ghcr.io/normanweis/manaschmiede:58
```

**docker run** – ein Container, ohne HTTPS (zum Ausprobieren oder hinter einem eigenen Reverse-Proxy):
```
docker run -d --name manaschmiede --restart unless-stopped \
  -p 8000:8000 \
  -v manaschmiede_data:/data \
  -e CDB_ADMIN_USER=admin -e CDB_ADMIN_PASSWORD='ein-langes-eigenes-passwort' \
  ghcr.io/normanweis/manaschmiede:58
```
Dann `http://SERVER-IP:8000` öffnen und als `admin` anmelden.

**docker compose** – für den Dauerbetrieb mit HTTPS (Caddy) oder Cloudflare-Tunnel:
```
cd server
cp .env.example .env && nano .env      # Domain, E-Mail, Admin-Zugang eintragen
docker compose pull
docker compose up -d
```
Ausführlich (Einstellungen, Benutzer, Sicherung, Updates): [`server/README-Server.md`](server/README-Server.md)

## Inhalt des Repositorys
| Ordner | Inhalt |
|---|---|
| `server/` | Programm, Dockerfile, docker-compose, Caddy, Anleitung für den Serverbetrieb |
| `android/` | Android-App (WebView, Kartenscanner, Dauerscan) |
| `windows/` | Programm und Startdateien für den lokalen Betrieb unter Windows |
| `docker/` | Anleitung und Zusammenfüge-Datei für das Image als Datei in zwei Teilen |
| `docs/` | Funktionsvergleich mit anderen Apps, Punktetabelle, Versionsverlauf, bekannte Grenzen |
| `archiv/` | frühere Programmversionen 6–32 |
| `.github/workflows/` | automatischer Bau von Docker-Image (ghcr.io) und Android-APK |

Downloads (Docker-Image als Datei, APK, Windows-Paket): unter **Releases** im Repository. Ein neues Release erstellt
**Actions → „Release erstellen“ → Run workflow** (Versionsnummer eintragen) – APK und Image werden dabei frisch gebaut.
