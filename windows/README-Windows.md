# Manaschmiede unter Windows (lokal, ohne Server)

1. Python 3 installieren (python.org, beim Installieren „Add python.exe to PATH“ anhaken).
2. Diesen Ordner an einen Ort deiner Wahl kopieren, z. B. nach `Downloads`.
3. `Commander-DB starten.bat` doppelklicken. Der Browser öffnet die Manaschmiede unter `http://localhost:8000`.
   Beim ersten Start werden Kartendaten, Precons und Regeln geladen (1–3 Minuten). Das schwarze Fenster offen lassen.
4. Für Handy und Tablet im Heimnetz startest du `Commander-DB im Netzwerk starten.bat`. Das Fenster zeigt die
   Adresse samt Zugangsschlüssel (`http://192.168.…:8000/?key=…`).

| Datei | Zweck |
|---|---|
| `commander_db_v61.py` | das Programm (identisch mit `server/commander_db.py`) |
| `Commander-DB starten.bat` | Start nur auf diesem PC |
| `Commander-DB im Netzwerk starten.bat` | Start mit Zugriff aus dem Heimnetz |
| `Alte Versionen archivieren.bat` | verschiebt ältere `commander_db_vNN.py` in den Unterordner „Alte Versionen“ |

Deine Daten (Decks, Sammlung, Kartendaten) liegen in `cards.db` neben dem Programm. Diese Datei gehört nicht
ins Repository und ist über `.gitignore` ausgeschlossen.

Für Forge-Duelle brauchst du zusätzlich Java 17 oder neuer und Forge. Die Hilfe in der Oberfläche (❓) erklärt die Schritte.
