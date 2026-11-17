# Manaschmiede unter Windows (lokal, ohne Server)

1. **Python 3** installieren (python.org, beim Installieren „Add python.exe to PATH“ anhaken).
2. Diesen Ordner in einen Ordner deiner Wahl kopieren, z. B. `Downloads`.
3. Doppelklick auf **`Commander-DB starten.bat`** – der Browser öffnet die Manaschmiede unter `http://localhost:8000`.
   Beim ersten Start werden Kartendaten, Precons und Regeln geladen (1–3 Minuten). Das schwarze Fenster offen lassen.
4. Für Handy und Tablet im Heimnetz: **`Commander-DB im Netzwerk starten.bat`** – das Fenster zeigt die Adresse
   samt Zugangsschlüssel (`http://192.168.…:8000/?key=…`).

| Datei | Zweck |
|---|---|
| `commander_db_v41.py` | das Programm (identisch mit `server/commander_db.py`) |
| `Commander-DB starten.bat` | Start nur auf diesem PC |
| `Commander-DB im Netzwerk starten.bat` | Start mit Zugriff aus dem Heimnetz |
| `Alte Versionen archivieren.bat` | verschiebt ältere `commander_db_vNN.py` in den Unterordner „Alte Versionen“ |

Deine Daten (Decks, Sammlung, Kartendaten) liegen in `cards.db` neben dem Programm – diese Datei gehört **nicht**
ins Repository und wird über `.gitignore` ausgeschlossen.

Für Forge-Duelle zusätzlich Java 17+ und Forge installieren; die Hilfe in der Oberfläche (❓) erklärt die Schritte.
