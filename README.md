# Manaschmiede (Commander-Deckbau-Datenbank) – Version 32

| Teil | Inhalt | Anleitung |
|---|---|---|
| **Windows (lokal)** | `commander_db_v32.py` + Startdateien im Download-Ordner – läuft wie bisher ohne Server | Doppelklick auf `Commander-DB starten.bat` |
| **Server (Internet)** | Ordner `server`: Docker-Image mit Python, Java, Forge, HTTPS über Caddy oder Cloudflare-Tunnel | `server/README-Server.md` |
| **Android** | installierbare Web-App direkt vom Server **oder** eigene APK (Ordner `android`, Bau automatisch bei GitHub) | `android/README-Android.md` |
| **Windows-App vom Server** | Serveradresse in Edge/Chrome öffnen → Installieren-Symbol in der Adressleiste → eigenes App-Fenster im Startmenü | – |

Alle Varianten zeigen dieselben Inhalte und Funktionen. Auf dem Server kommen Anmeldung, Benutzerkonten
und getrennte Decks je Benutzer dazu.

## Schnellstart mit Docker
Fertiges Image: **`ghcr.io/normanweis/manaschmiede:32`** (auch `:latest`) – Ubuntu 24.04, Python, Java 17, Forge 2.0.16,
für x86_64-/amd64-Server. Ist das Paket privat, vorher einmal anmelden (Token mit Recht `read:packages`):
```
docker login ghcr.io -u NormanWeis
```

**docker run** – ein Container, ohne HTTPS (zum Ausprobieren oder hinter einem eigenen Reverse-Proxy):
```
docker run -d --name manaschmiede --restart unless-stopped \
  -p 8000:8000 \
  -v manaschmiede_data:/data \
  -e CDB_ADMIN_USER=admin -e CDB_ADMIN_PASSWORD='ein-langes-eigenes-passwort' \
  ghcr.io/normanweis/manaschmiede:32
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
