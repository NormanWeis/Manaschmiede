#!/usr/bin/env python3
"""Manaschmiede – Commander-Deckbau-Datenbank auf Basis der Scryfall-Bulk-Daten (SQLite + lokale Suche).

  python commander_db_v15.py import            # lädt "Oracle Cards" von Scryfall + Precons, baut cards.db
  python commander_db_v15.py import --file x.json   # statt Download eine lokale JSON-Datei nutzen
  python commander_db_v15.py precons           # nur die Precon-Decklisten (neu) laden
  python commander_db_v15.py serve             # Oberfläche unter http://localhost:8000 (prüft beim Start auf Updates)
  python commander_db_v15.py serve --no-update # ohne Update-Prüfung starten
  python commander_db_v15.py update            # Regeln, Precons und Kartendaten jetzt aktualisieren
  python commander_db_v15.py adduser NAME [--admin]   # Benutzer für den Server-Modus anlegen / Passwort setzen
Server-Modus (z. B. im Docker-Container): Umgebungsvariable CDB_SERVER=1, weitere siehe README-Server.md.
Nur Python-Standardbibliothek, keine Installation nötig.

Version 2: Namensvorschläge beim Tippen und Tippfehler-Toleranz, Farbidentität wird aus dem
Commander übernommen, alle Eingaben optional, Preise als Zahl, Importdatum, Grist-Fix.
Version 3: Deckansicht mit Kartenbildern, Vergleich mit offiziellen Commander-Precons
(Decklisten: github.com/taw/magic-preconstructed-decks-data, auch Grundlage von mtg.wtf/MTGJSON).
Version 4: Karten gezielt tauschen oder entfernen (mit Alternativen gleicher Aufgabe), Option ohne
Game Changer, Liste nicht verfügbarer Karten, bessere Ramp-Erkennung.
Version 38: Testspielfeld – Deck ohne Gegner durchspielen (Bibliothek, Hand, Spielfeld, Friedhof, Exil, Kommandozone,
  Mulligan, Tappen, Marken, Tokens, Scry/Suchen, Rückgängig).
Version 37: Gemeinsamer Spieltisch – mehrere Handys an einem Tisch (Code/QR beitreten, jeder steuert sein Feld, Abgleich
  in Echtzeit); Decks an andere Benutzer senden (Postfach) bzw. per Link an andere Manaschmieden.
Version 36: Commander-Vorschläge mit Abwechslung – jede Anfrage mischt beliebte Commander, Geheimtipps und günstige
  Optionen, achtet auf verschiedene Farbkombinationen; „Andere Vorschläge“ zeigt noch nicht gezeigte Commander.
Version 35: Handyansicht – das Endgerät wird erkannt; auf Mobiltelefonen kompakter Kopf, Navigationsleiste unten,
  einspaltige Formulare und Kacheln, kein seitliches Verrutschen; umschaltbar (automatisch / Handy / PC).
Version 34: Commander-Vorschläge nur nach Farbe und/oder Thema; neuer Bereich „Neu hier?“ mit Einstieg für
  Magic- und Commander-Neulinge.
Version 60: Sprachliche Überarbeitung aller Texte (Hilfe, Hinweise, Meldungen, Rechtstexte, Anleitungen): Gedankenstriche
            durch passende Satzzeichen ersetzt, aufgesetzte Gegenüberstellungen und Füllwörter entfernt, Beschriftungen
            vereinheitlicht; Hilfe um Spielabend, Messlabor, KI-Einstellungen, Kaufassistent und Impressum ergänzt,
            veraltete Angaben korrigiert.
Version 59: Proxy-Druck: Hinweis, die Kopie mit einer echten, wertlosen Karte in eine Hülle zu stecken (einheitliche Rückseite,
            auch in durchsichtigen Hüllen) – im Dialog, in der Druckansicht, in der Sammlung und in der Hilfe.
Version 58: Commander-Vorschläge nach Thema erkennen Verzauberungs- und Artefakttypen (Sagen, Auren, Klassen, Räume, Fälle,
            Schreine, Flüche, Hintergründe, Rollen, Ausrüstungen, Fahrzeuge – deutsch und englisch); Erinnerungstext in Klammern
            zählt nicht mehr als Treffer; Deckbau-Synergie für Sagen.
Version 57: Proxy-Druck erweitert: beliebige Kartenlisten (Sammlung, Deck, Kaufplan), bestimmter Druck per „(SET) Nr“,
            Rückseiten doppelseitiger Karten, Textfassung ohne Kartenbild, Schnittlinien, Abstand, Graustufen, A4/Letter;
            fester Vermerk „PROXY – keine echte Karte“ und Hinweis, dass es nur Kopien zum privaten Testen sind.
Version 56: Kaufassistent (Sammlung, auch „Kauf planen“ im Deck): fehlende Karten für ein Deck, alle Decks oder die Wunschliste;
            Budget mit Vorrang für mehrfach genutzte Karten, Druck und Foil je Karte, Aufteilung Cardmarket/Trader-online,
            Cardmarket-Wants für beliebige Drucke, Precon-Check, CSV, „gekauft“ übernimmt Karten mit Druck in die Sammlung.
Version 55: Messlabor mit Umfang-Stufen (Schnell, Standard, Gründlich, Sehr gründlich, eigene Einstellung), jeweils mit ungefährer
            Dauer passend zu Varianten und Gegnern; Stufen über der Partien-Grenze sind gesperrt.
Version 54: Messlabor (Gegner & Duell): Kartentausch-Varianten oder KI-Profile per Forge gegen ein Gegnerfeld messen, gleicher
            Zufallsstart, Siegquote mit 90-%-Bereich, Urteil, Restzeit; Ergebnisse archiviert, Übernehmen ins Deck. Duelle mit
            KI-Profil und Vorausschau.
Version 53: Spielabend-Modus (Spieltisch-Tab): Spieler eintragen, gemischte Vierer-Tische auslosen (wiederholte Paarungen werden
            vermieden), Sieger per Antippen, Rangliste nach Siegen, Saison optional; Mitspieler tragen Ergebnisse über Link/QR-Code ohne Konto
            ein (/n/CODE); Tisch direkt im Lebenszähler starten. Impressum und Datenschutzerklärung (/impressum, /datenschutz), vom Admin pflegbar.
Version 52: Händler-Links: je Karte Cardmarket und Trader-online, bei Precons zusätzlich cardcosmos; Einkaufs- und
            Wunschliste mit „Bei Cardmarket kaufen“ (Liste kopieren, Wants öffnen); Händler einzeln abschaltbar.
Version 51: Neuer Spieltisch (allein und zu zweit) nach dem Vorbild digitaler Kartenspiele: Gegner oben, Spielfeld in der Mitte,
            Hand als Fächer, Leben und Stapel als Symbole, ein großer Zug-Knopf, Phasenleiste, Karten ziehen per Drag & Drop,
            Aktionen beim Antippen, alles Weitere hinter ⚙; Protokoll und Statistik im Seitenmenü.
Version 50: Textansicht der Spieltische („Aa“): Karten als lesbare Kacheln mit Name, Manakosten, Typ, Regeltext,
            Stärke/Widerstand bzw. Loyalität; große Ansicht mit vollem Text; Stärke/Widerstand werden beim Kartenimport gespeichert.
Version 49: Spieltische am Handy: „📱 Quer“ (Vollbild + Querformat), Hinweis im Hochformat, eigenes Querformat-Layout,
            Kartengröße A−/A+ und „🔍 Groß ansehen“ (lange drücken bzw. Kartenmenü).
Version 48: Sammlung je Druck (Set, Sammlernummer, Foil/Etched, Zustand, Sprache) mit Cardmarket-Preis je Druckversion,
            Druckauswahl, Import der Druckangaben aus ManaBox, Moxfield, Deckbox, Archidekt, Dragon Shield und Textlisten,
            Export je Druck; manuelles Testduell im Browser (beide Seiten selbst spielen) und lokal „In Forge selbst spielen“;
            genaue Statistik der Forge-Duelle (Mulligans, Commander-Runde, Länder, Zauber, Schaden, Schlüsselkarten, Verlauf je Partie).
Version 47: Cardmarket-Preise direkt aus der öffentlichen Cardmarket-Preisliste (täglich): Preis je Karte = günstigste
            Druckversion (Trendpreis), dazu Tiefstpreis, Durchschnitt 1/7/30 Tage, Foil und Zahl der Drucke; Links zur
            günstigsten Druckversion auf Cardmarket; Preisalarm nutzt die Cardmarket-Durchschnitte. Kennzeichnung als Cardmarket-Preise.
Version 46: Neuer Bereich „📦 Precons“: alle offiziellen Commander-Precons nach Set mit Suche, Farbfilter, Wert,
            Bracket-Schätzung und Sammlungsanteil; Deckliste ansehen, im Editor öffnen, in Meine Decks speichern, als Gegner
            setzen, kopieren oder als gekauftes Precon in die Sammlung übernehmen.
Version 45: Fehler behoben: „Combos mitprüfen“ brach ab, sobald Commander Spellbook Combos lieferte. Die Bracket-Einstufung
            prüft Combos jetzt automatisch mit (Internet), sobald ein Deck geladen ist; ohne Verbindung bleibt die Einstufung ohne Combos.
Version 44: Bracket-Einstufung je Deck nach den offiziellen Regeln (Game Changer, Massen-Landzerstörung, Extra-Züge,
            Zwei-Karten-Combos) mit Begründung, eigenem Ziel-Bracket, Anzeige in Meine Decks, Galerie (mit Filter) und
            Teilen-Seite sowie ausführlicher Erklärung der fünf Brackets in der Hilfe.
Version 43: Tägliche Aktualisierung im Server-Betrieb: Regeln, Precons und Kartendaten (mit Preisen) werden jede Nacht
            geprüft (Standard 4 Uhr, CDB_UPDATE_HOUR), Kartendaten täglich statt nach 7 Tagen neu geladen (CDB_CARDS_MAX_AGE_DAYS).
Version 42: Deck-Editor: eigene Gruppen per Ziehen und Ablegen (am Handy „verschieben nach …“), Rückgängig/Wiederherstellen,
            Mehrfachauswahl (verschieben, taggen, ins Maybeboard, entfernen), Stapelansicht nach Manawert; Gruppen werden gespeichert,
            auf der Teilen-Seite und im Archidekt-Export als Kategorien gezeigt.
Version 41: Sammlung: Einkaufsliste über alle Decks, Wunschliste mit Zielpreis, Ordner (z. B. Tauschordner), Wertverlauf.
            Preise: Preisalarm auf der Startseite, zweite Preisquelle (US-Dollar/TCGplayer über Scryfall), Budget-Tausch je Deck.
Version 40: Empfehlungen auch aus der Galerie (veröffentlichte Decks anderer Benutzer), Lückenanalyse für Ramp, Kartenziehen,
            Removal und Board-Wipes mit passenden Karten, Filter „nur aus meiner Sammlung“ und Höchstpreis je Karte.
Version 39: Öffentliche Deck-Galerie im Server-Betrieb: Decks veröffentlichen, Galerie mit Filtern (Commander, Farben,
            Preis, Game Changer, Thema), Decks kopieren, Herzchen und Kommentare, Administrator kann Decks ausblenden.
Version 38: Testspielfeld zum Goldfischen (Kommandozone, Bibliothek, Friedhof, Exil, Spielmarken, Zähler, Rückgängig).
Version 33: Spieltisch mit Tischansicht im Stil von Lebenszähler-Apps (große Felder je Spieler, Tippen links/rechts,
  Halten für ±10, Kartenbild des Commanders als Hintergrund, Vollbild); die Tabellenansicht bleibt umschaltbar.
Version 32: Neuer Name „Manaschmiede“ (Titel, Willkommensseite, Web-App, Android-App).
Version 31: Forge-Duell auch als Runde zu dritt (dein Deck gegen zwei Gegner).
Version 30: Dauerscan – Karten nacheinander vor die Kamera halten, jede erkannte Karte landet automatisch in der Scanliste
            (Browser-Live-Kamera und Android-App mit eigener Kameraansicht).
Version 29: Kartenscanner: Foto oder Live-Kamera, Texterkennung im Browser (Tesseract.js, einmalig geladen) oder in der
            Android-App (ML Kit auf dem Gerät), Erkennung über Namen (auch deutsch) oder Set + Sammlernummer.
Version 28: Gespeicherte Decks direkt im Tab „Deck bauen“ öffnen und als „Zuletzt gespeichert“ auf der Willkommen-Seite.
Version 27: Neuer Aufbau: Willkommen-Seite im Magic-Stil, alle Funktionen in Tabs (Deck bauen, Gegner & Duell, Meine Decks,
            Sammlung, Spieltisch, Kartensuche, Regeln), Hinweis auf Wizards of the Coast im Kopf, Fan-Content-Hinweis in der Fußzeile.
Version 26: Precon-Auswahlliste mit allen Precons (Name, Commander, Set, Jahr, Farben), auch für die Vierer-Runde.
Version 25: Deutsche (und andere fremdsprachige) Kartennamen in Import, Sammlung und Suche – Übersetzung über Scryfall, lokal gemerkt.
Version 24: Forge-Duell als Commander-Runde zu viert (dein Deck gegen drei Gegner), Siege je Spieler, Zeitlimit als Unentschieden.
Version 23: Empfehlungen aus eigener Statistik (Precons, eigene Decks, Spielprotokoll, Commander-Text), Streichvorschläge,
            Frust-Index (eigene Einschätzung von Stax, Landzerstörung, Extra-Zügen usw.).
Version 22: Decks per Link teilen (Nur-Lese-Seite mit Karten, Bildern, Tags, Notizen; jederzeit widerrufbar).
Version 21: Spieltisch mit Lebenszähler (2–6 Spieler, Commander-Schaden, Gift, Züge), Spielprotokoll und Siegquoten
            je Deck und Spieler, Forge-Ergebnisse übernehmbar.
Version 20: Preisverlauf (bei jeder Kartenaktualisierung gesichert), Wertentwicklung je Deck, größte Preisänderungen.
Version 19: Token-Liste je Deck (aus Scryfall-Verknüpfungen, sonst aus dem Kartentext), Proxy-Druck (63 × 88 mm, A4).
Version 18: Maybeboard, eigene Tags je Karte (Gruppierung nach Tags), Notizen/Primer je Deck – mit dem Deck gespeichert.
Version 17: Kartensammlung (Import aus ManaBox, Moxfield, Deckbox, Archidekt, Text), Besitzanteil je Deck,
            „schon in anderem Deck“, Assistent baut aus der Sammlung oder bevorzugt sie.
Version 16: Manabasis mit Such-/Fetchländern und Ramp, strenge Partner-Prüfung, Versionen frei vergleichen mit Notiz,
            Mengen ändern, bessere Mehrfarben-Länder, Hinweis auf Karten ohne Preis.
Version 15: Karten frei hinzufügen/entfernen, Synergie mit dem Commander-Text, Partner im Assistenten, Budget-Grenzen,
Fast-Combos und Bracket-Schätzung von Commander Spellbook, Manabasis-Analyse, Probehand mit Starthand-Statistik, Deck-Versionen.
Version 14: Kodierungen abgesichert (Forge-Ausgabe unter Windows als UTF-8, Import von UTF-8/BOM/UTF-16/Windows-1252),
Duell-Auswertung an echtes Forge-Ausgabeformat angepasst (Siegzug), Import von MTGO-.dek und Cockatrice-.cod.
Version 13: Server-Modus fürs Internet (CDB_SERVER=1: Anmeldung, Benutzerkonten, Decks je Benutzer, Duell-Warteschlange,
Sicherheitssperren), installierbar als App auf Android/Windows (PWA), Docker-Betrieb, Brücke für die Android-App.
Version 12: Cardmarket-Links entfernt (werden von Cardmarket blockiert); Preise bleiben.
Version 11: Kartensymbol vor jedem Kartennamen – Maus darüber (am Handy antippen) zeigt das Kartenbild.
Version 10: Kein veralteter Seitenstand mehr: Browser-Cache abgeschaltet, Versionsprüfung der Seite, eine ältere noch
laufende Version wird beim Start erkannt (neuere werden beendet, sonst wird ein freier Port gewählt).
Version 9: Zugriff aus dem Heimnetz (Handy/Tablet, --lan mit Zugangscode), Browser öffnet sich selbst. Offizielle Comprehensive Rules (Wizards of the Coast) mit Suche; beim Start automatische Prüfung auf neue
Regeln, Precons und Kartendaten (Kartendaten, wenn älter als 7 Tage); ausführliche Nutzerhilfe für Einsteiger.
Version 8: Optik im Magic-Stil (umschaltbar auf neutral), farbige Mana-Symbole, Speichern robuster (Datenbank im WAL-Modus, längere Wartezeit, sichtbare Rückmeldung); Decks exportieren
(Moxfield/Arena, Archidekt, Text, Forge-.dck, CSV) und per Klick in Moxfield oder Archidekt übertragen; Speichern im Forge-Deckordner.
Version 7: Eigene Decks speichern und importieren (Textliste, Forge-.dck, CSV, JSON, Links zu Archidekt,
Moxfield, MTGGoldfish, TappedOut, Deckstats) und statt eines Precons als Gegner nutzen – auch im Forge-Duell.
Version 6: findet das neueste installierte Java automatisch (auch wenn Java 8 im PATH vorne steht).
Version 5: Combos beider Decks (Commander Spellbook) mit Wahrscheinlichkeit je Zug und Bracket-Regel,
direktes Duell beider Decks über die Regel-Engine Forge (KI gegen KI, Commander 1-gegen-1).
Eine mit Version 1 gebaute cards.db wird beim ersten 'serve' automatisch umgestellt.
"""
import urllib.error
import urllib.parse
import math
import base64, getpass, hmac, secrets, struct, time, zlib
import xml.etree.ElementTree as ET
import argparse, csv, datetime, difflib, io, gzip, hashlib, json, os, random, re, shutil, sqlite3, subprocess, sys, tempfile, threading, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

APP_VERSION = "60"
ENV = os.environ.get
SERVER = ENV("CDB_SERVER", "") == "1"                 # Betrieb im Internet: Anmeldung Pflicht, Sicherheitssperren aktiv
DATA_DIR = ENV("CDB_DATA_DIR") or os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(DATA_DIR, "cards.db")              # lokal: liegt neben dem Skript
MAX_DUELS = max(1, int(ENV("CDB_MAX_DUELS", "1")))   # gleichzeitige Forge-Duelle (je ca. 2–4 GB RAM)
MAX_GAMES = max(1, int(ENV("CDB_MAX_GAMES", "20" if SERVER else "100")))
SESSION_DAYS = int(ENV("CDB_SESSION_DAYS", "30"))
HEADERS = {"User-Agent": "CommanderDeckDB/0.1", "Accept": "application/json"}  # von Scryfall verlangt
SKIP_LAYOUTS = {"token", "double_faced_token", "emblem", "art_series", "vanguard", "scheme", "planar"}
ORDER = "WUBRG"
OUTSIDE_CREATURE = re.compile(r"isn't on the battlefield, it's a [^.]*creature", re.I)
SCHEMA = """CREATE TABLE cards(oracle_id TEXT PRIMARY KEY, name TEXT, mana_cost TEXT, cmc REAL, type_line TEXT,
  oracle_text TEXT, color_identity TEXT, keywords TEXT, rarity TEXT, edhrec_rank INTEGER,
  commander_legal INTEGER, game_changer INTEGER, can_be_commander INTEGER, eur REAL,
  scryfall_uri TEXT, cardmarket_uri TEXT, image TEXT);
CREATE INDEX idx_name ON cards(name COLLATE NOCASE);
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);"""


def db():
    """Verbindung mit Wartezeit: parallele Anfragen (Combos, Duell, Speichern) sperren sich nicht gegenseitig aus."""
    return sqlite3.connect(DB, timeout=30)


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=120) as r:
        return r.read()


def to_row(c):
    faces = c.get("card_faces") or []
    f0 = faces[0] if faces else {}
    text = c.get("oracle_text") or "\n//\n".join(f.get("oracle_text", "") for f in faces)
    front_type = (c.get("type_line") or f0.get("type_line") or "").split(" // ")[0]
    ci = "".join(x for x in ORDER if x in (c.get("color_identity") or []))
    img = (c.get("image_uris") or f0.get("image_uris") or {}).get("normal")
    can_cmd = int(("Legendary" in front_type and "Creature" in front_type) or "can be your commander" in text
                  or ("Legendary" in front_type and bool(OUTSIDE_CREATURE.search(text))))  # z. B. Grist
    eur = (c.get("prices") or {}).get("eur")
    return (
        c["oracle_id"] if c.get("oracle_id") else c["id"], c["name"],
        c.get("mana_cost") or f0.get("mana_cost") or "", c.get("cmc") or 0,
        c.get("type_line") or "", text, ci, " ".join(c.get("keywords") or []),
        c.get("rarity"), c.get("edhrec_rank"),
        int((c.get("legalities") or {}).get("commander") in ("legal", "restricted")),
        int(bool(c.get("game_changer"))), can_cmd,
        float(eur) if eur else None, c.get("scryfall_uri"),
        (c.get("purchase_uris") or {}).get("cardmarket"), img,
    )


def parse(raw, name):
    """Entpackt gzip falls nötig und liest JSON bzw. JSON Lines (.jsonl)."""
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    text = raw.decode("utf-8")
    if ".jsonl" in name:
        return [json.loads(l) for l in text.splitlines() if l.strip()]
    return json.loads(text)


def ensure_price_baseline():
    try:
        con = db()
        price_table(con)
        if not con.execute("SELECT 1 FROM price_hist LIMIT 1").fetchone() and con.execute("SELECT 1 FROM cards LIMIT 1").fetchone():
            sd = (con.execute("SELECT value FROM meta WHERE key = 'source_date'").fetchone() or [None])[0]
            record_prices(con, sd)
    except sqlite3.Error:
        pass


def do_import(path):
    source_date = None
    if path:
        data = parse(open(path, "rb").read(), path)
        source_date = datetime.datetime.fromtimestamp(os.path.getmtime(path)).isoformat(timespec="minutes")
    else:
        print("Hole Bulk-Liste von Scryfall ...")
        bulk = json.loads(fetch("https://api.scryfall.com/bulk-data"))
        entry = next((b for b in bulk.get("data", []) if b.get("type") == "oracle_cards"), None) or {}
        uri = entry.get("jsonl_download_uri") or entry.get("download_uri")
        if not uri:
            print("Konnte keine Download-Adresse finden. Eintrag von Scryfall:")
            print(json.dumps(entry, indent=1)[:1500])
            sys.exit(1)
        print("Lade Kartendaten (ca. 25 MB, kann etwas dauern) ...")
        data = parse(fetch(uri), uri)
        source_date = (entry.get("updated_at") or "")[:16].replace("T", " ") or None
    global NAMES
    rows = [to_row(c) for c in data if c.get("layout") not in SKIP_LAYOUTS]
    parts = [(c["name"], pt.get("name"), pt.get("type_line") or "", pt.get("id"))
             for c in data if c.get("layout") not in SKIP_LAYOUTS
             for pt in (c.get("all_parts") or []) if pt.get("component") == "token" and pt.get("name")]
    con = db()
    con.executescript(SCHEMA.replace("CREATE TABLE cards(", "CREATE TABLE IF NOT EXISTS cards(").replace(
        "CREATE INDEX idx_name", "CREATE INDEX IF NOT EXISTS idx_name"))
    con.executescript("DROP TABLE IF EXISTS cards_new;" + SCHEMA.split(";")[0].replace("CREATE TABLE cards(", "CREATE TABLE cards_new("))
    con.executemany("INSERT OR REPLACE INTO cards_new VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    con.commit()
    # In einem Schritt austauschen – eine laufende Oberfläche sieht entweder alt oder neu, nie halb
    con.executescript("BEGIN; DROP TABLE cards; ALTER TABLE cards_new RENAME TO cards; "
                      "CREATE INDEX IF NOT EXISTS idx_name ON cards(name COLLATE NOCASE); COMMIT;")
    NAMES = None
    record_prices(con, source_date)
    usd = [(c["name"], float((c.get("prices") or {}).get("usd") or (c.get("prices") or {}).get("usd_foil")))
           for c in data if c.get("layout") not in SKIP_LAYOUTS and ((c.get("prices") or {}).get("usd") or (c.get("prices") or {}).get("usd_foil"))]
    con.execute("CREATE TABLE IF NOT EXISTS card_usd(name TEXT PRIMARY KEY, usd REAL)")
    con.execute("DELETE FROM card_usd")
    con.executemany("INSERT OR REPLACE INTO card_usd VALUES(?,?)", usd)
    stats = []
    for c in data:
        if c.get("layout") in SKIP_LAYOUTS:
            continue
        fs = c.get("card_faces") or [c]
        pt = " // ".join(f"{f['power']}/{f['toughness']}" for f in fs if f.get("power") is not None and f.get("toughness") is not None)
        loy = " // ".join(str(f["loyalty"]) for f in fs if f.get("loyalty"))
        if pt or loy or c.get("defense"):
            stats.append((c["name"], pt, loy or (f"Verteidigung {c['defense']}" if c.get("defense") else "")))
    con.execute("CREATE TABLE IF NOT EXISTS card_stats(name TEXT PRIMARY KEY, pt TEXT, loyalty TEXT)")
    con.execute("DELETE FROM card_stats")
    con.executemany("INSERT OR REPLACE INTO card_stats VALUES(?,?,?)", stats)
    con.execute("CREATE TABLE IF NOT EXISTS card_tokens(card TEXT, token TEXT, type_line TEXT, sid TEXT)")
    con.execute("DELETE FROM card_tokens")
    con.executemany("INSERT INTO card_tokens VALUES(?,?,?,?)", parts)
    con.execute("CREATE INDEX IF NOT EXISTS idx_ct ON card_tokens(card)")
    now = datetime.datetime.now().isoformat(sep=" ", timespec="minutes")
    con.executemany("INSERT OR REPLACE INTO meta VALUES(?,?)",
                    [("imported_at", now), ("source_date", source_date or "unbekannt"), ("count", str(len(rows)))])
    con.commit()
    print(f"{len(rows)} Karten in {DB} gespeichert.")


def price_table(con):
    con.execute("CREATE TABLE IF NOT EXISTS price_hist(name TEXT, day TEXT, eur REAL, PRIMARY KEY(name, day))")


def record_prices(con, source_date=None):
    """Sichert den Preis jeder Karte, wenn er sich gegenüber dem letzten gesicherten Wert geändert hat (platzsparend)."""
    price_table(con)
    day = (source_date or "")[:10] if re.match(r"\d{4}-\d\d-\d\d", source_date or "") else datetime.date.today().isoformat()
    last = {n: e for n, e in con.execute("SELECT h.name, h.eur FROM price_hist h JOIN (SELECT name, max(day) d FROM price_hist "
                                         "GROUP BY name) m ON m.name = h.name AND m.d = h.day")}
    rows = [(n, day, e) for n, e in con.execute("SELECT name, min(eur) FROM cards WHERE eur IS NOT NULL GROUP BY name")
            if n not in last or abs((last[n] or 0) - e) >= 0.005]
    con.executemany("INSERT OR REPLACE INTO price_hist VALUES(?,?,?)", rows)
    con.commit()
    return len(rows)


def price_history(p):
    """Wertentwicklung einer Deckliste über alle gesicherten Stichtage und die größten Änderungen."""
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    price_table(con)
    ent, _ = entries_from_list(con, g("list"), g("commander"))
    names = {r["name"]: q for r, q in ent if not r["type_line"].startswith("Basic")}
    if not names:
        return {"error": "Leere Deckliste."}
    marks = ",".join("?" * len(names))
    hist = {}
    for r in con.execute(f"SELECT name, day, eur FROM price_hist WHERE name IN ({marks}) ORDER BY day", list(names)):
        hist.setdefault(r["name"], []).append((r["day"], r["eur"]))
    days = sorted({d for h in hist.values() for d, _ in h})
    if not days:
        return {"days": [], "hint": "Noch kein Preisverlauf. Er entsteht ab jetzt mit jeder Kartenaktualisierung (einmal täglich beim Start)."}
    def at(n, day):
        v = None
        for d, e in hist.get(n, []):
            if d <= day:
                v = e
        return v
    series = [{"day": d, "value": round(sum((at(n, d) or 0) * q for n, q in names.items()), 2)} for d in days]
    first, lastd = days[0], days[-1]
    ref = next((d for d in days if d >= (datetime.date.fromisoformat(lastd) - datetime.timedelta(days=30)).isoformat()), first)
    moves = []
    for n, q in names.items():
        a, b = at(n, ref), at(n, lastd)
        if a is not None and b is not None and abs(b - a) >= 0.01:
            moves.append({"name": n, "from": a, "to": b, "diff": round((b - a) * q, 2), "pct": round(100 * (b - a) / a) if a else None})
    moves.sort(key=lambda x: -abs(x["diff"]))
    um = usd_map(con, names)
    usd = round(sum((um.get(n) or 0) * q for n, q in names.items()), 2) if um else None
    return {"days": days, "series": series, "since": ref, "moves": moves[:10], "usd": usd, "usd_missing": sum(1 for n in names if n not in um) if um else None,
            "hint": (f"{len(days)} Stichtag(e) seit {first}. Euro-Preise: Cardmarket-Preisliste vom {setting('cm_at')} "
                     "(günstigste Druckversion, Trendpreis); Dollar: TCGplayer über Scryfall." if setting("cm_at") else
                     f"{len(days)} Stichtag(e) seit {first}. Preise: Scryfall (Euro = Cardmarket, Dollar = TCGplayer), "
                     "Druckversion wie in der Kartendatenbank.")}


def upgrade_db():
    """Bringt eine mit der alten Skriptversion gebaute cards.db auf den neuen Stand (einmalig, ohne Download)."""
    con = db()
    cols = {r[1]: r[2] for r in con.execute("PRAGMA table_info(cards)")}
    if not cols:
        sys.exit(f"{DB} enthält keine Karten. Bitte zuerst 'python commander_db.py import' ausführen.")
    if cols.get("eur", "").upper() == "REAL":
        return
    print("Aktualisiere cards.db auf das neue Format (einmalig) ...")
    old = datetime.datetime.fromtimestamp(os.path.getmtime(DB)).isoformat(sep=" ", timespec="minutes")
    con.executescript("ALTER TABLE cards RENAME TO cards_old; DROP INDEX IF EXISTS idx_name;" + SCHEMA + """
      INSERT INTO cards SELECT oracle_id,name,mana_cost,cmc,type_line,oracle_text,color_identity,keywords,rarity,
        edhrec_rank,commander_legal,game_changer,can_be_commander,CAST(eur AS REAL),scryfall_uri,cardmarket_uri,image
        FROM cards_old;
      DROP TABLE cards_old;""")
    rows = con.execute("SELECT oracle_id, type_line, oracle_text FROM cards WHERE can_be_commander = 0").fetchall()
    fix = [(i,) for i, t, x in rows if "Legendary" in t.split(" // ")[0] and OUTSIDE_CREATURE.search(x or "")]
    con.executemany("UPDATE cards SET can_be_commander = 1 WHERE oracle_id = ?", fix)
    n = con.execute("SELECT count(*) FROM cards").fetchone()[0]
    con.executemany("INSERT OR REPLACE INTO meta VALUES(?,?)",
                    [("imported_at", old + " (ungefähr)"), ("source_date", "unbekannt"), ("count", str(n))])
    con.commit()
    con.execute("VACUUM")


NAMES = None  # Suchschlüssel -> Kartennamen, für Vorschläge und Tippfehler


def name_index(con):
    global NAMES
    if NAMES is None:
        NAMES = {}
        for (n,) in con.execute("SELECT name FROM cards"):
            for k in {n.lower(), *[f.lower() for f in n.split(" // ")], n.split(",")[0].lower()}:
                NAMES.setdefault(k, set()).add(n)
    return NAMES


def find_names(con, text, commander=False, limit=10):
    """Kartennamen zu einer Eingabe: erst Anfang, dann enthalten, dann ähnliche Schreibweise (Tippfehler)."""
    t = text.strip()
    if not t:
        return []
    cond = "commander_legal = 1" + (" AND can_be_commander = 1" if commander else "")
    rank = "ORDER BY name LIKE ? DESC, edhrec_rank IS NULL, edhrec_rank, name"
    out = [r[0] for r in con.execute(f"SELECT DISTINCT name FROM cards WHERE {cond} AND name LIKE ? {rank} LIMIT ?",
                                     (f"%{t}%", f"{t}%", limit))]
    if len(out) < limit:
        idx = name_index(con)
        keys = difflib.get_close_matches(t.lower(), list(idx), 8, 0.6)
        cand = list({n for k in keys for n in idx[k]})
        if cand:
            q = ",".join("?" * len(cand))
            rk = {n: (r if r is not None else 10**9) for n, r in
                  con.execute(f"SELECT name, min(edhrec_rank) FROM cards WHERE {cond} AND name IN ({q}) GROUP BY name", cand)}
            # Reihenfolge: Ähnlichkeit des Schlüssels, dann exakter Name vor Teilname, dann Beliebtheit
            for i, k in enumerate(keys):
                for n in sorted((n for n in idx[k] if n in rk), key=lambda n: (n.lower() != k, rk[n])):
                    if n not in out:
                        out.append(n)
    return out[:limit]


def alias_table(con):
    con.execute("CREATE TABLE IF NOT EXISTS name_alias(alias TEXT PRIMARY KEY COLLATE NOCASE, name TEXT, lang TEXT)")


def translate_names(con, names, limit=80):
    """Fremdsprachige Kartennamen über Scryfall ins Englische übersetzen (aufgedruckter Name -> Oracle-Name), Ergebnis merken.
    Nur Namen, die weder exakt noch als gemerkte Übersetzung bekannt sind; höchstens `limit` Abfragen je Aufruf."""
    alias_table(con)
    todo = []
    for n in dict.fromkeys(x.strip() for x in names if x and x.strip()):
        if con.execute("SELECT 1 FROM cards WHERE name = ? COLLATE NOCASE", (n,)).fetchone():
            continue
        if con.execute("SELECT 1 FROM name_alias WHERE alias = ?", (n,)).fetchone():
            continue
        if " // " in n and con.execute("SELECT 1 FROM cards WHERE name LIKE ?", (n.split(" // ")[0] + " // %",)).fetchone():
            continue
        todo.append(n)
    found = 0
    for n in todo[:limit]:
        q = urllib.parse.quote(f'!"{n}" lang:any')
        try:
            res = json.loads(fetch(f"https://api.scryfall.com/cards/search?q={q}&include_multilingual=true&unique=prints"))
        except Exception:
            res = {}
        hit = next((c for c in res.get("data") or [] if (c.get("printed_name") or "").lower() == n.lower()
                    or any((f.get("printed_name") or "").lower() == n.lower() for f in c.get("card_faces") or [])), None)
        if hit:
            con.execute("INSERT OR REPLACE INTO name_alias VALUES(?,?,?)", (n, hit["name"], hit.get("lang") or ""))
            found += 1
        else:
            con.execute("INSERT OR REPLACE INTO name_alias VALUES(?,?,?)", (n, "", ""))  # nicht erneut fragen
        time.sleep(0.1)  # Scryfall bittet um höchstens 10 Anfragen je Sekunde
    con.commit()
    return found


def lookup(con, name, commander=False):
    """Liefert (Karte, Hinweis). Bei mehreren gleichnamigen Karten wird die Commander-legale bevorzugt."""
    pref = "ORDER BY commander_legal DESC, can_be_commander DESC, edhrec_rank IS NULL, edhrec_rank LIMIT 1"
    r = con.execute(f"SELECT * FROM cards WHERE name = ? COLLATE NOCASE {pref}", (name,)).fetchone()
    if r:
        return r, None
    try:
        al = con.execute("SELECT name FROM name_alias WHERE alias = ? AND name <> ''", (name.strip(),)).fetchone()
    except sqlite3.Error:
        al = None
    if al:
        r = con.execute(f"SELECT * FROM cards WHERE name = ? {pref}", (al[0],)).fetchone()
        if r:
            return r, f"„{name}“ → {r['name']}"
    hits = find_names(con, name, commander, 1) or (find_names(con, name, False, 1) if commander else [])
    if not hits:
        return None, None
    r = con.execute(f"SELECT * FROM cards WHERE name = ? {pref}", (hits[0],)).fetchone()
    return r, f"„{name}“ nicht exakt gefunden, verwendet: {r['name']}."


# Commander-Vorschläge ohne festen Commander: nach Farbidentität und/oder Thema (Text, Schlüsselwort, Kreaturtyp)
TRIBES_DE = {"drache": "Dragon", "drachen": "Dragon", "elf": "Elf", "elfen": "Elf", "goblin": "Goblin", "goblins": "Goblin",
             "vampir": "Vampire", "vampire": "Vampire", "zombie": "Zombie", "zombies": "Zombie", "engel": "Angel",
             "dinosaurier": "Dinosaur", "dinos": "Dinosaur", "katze": "Cat", "katzen": "Cat", "ritter": "Knight",
             "pirat": "Pirate", "piraten": "Pirate", "meervolk": "Merfolk", "schlange": "Snake", "schlangen": "Snake",
             "spinne": "Spider", "spinnen": "Spider", "wolf": "Wolf", "wölfe": "Wolf", "werwolf": "Werewolf",
             "werwölfe": "Werewolf", "elementar": "Elemental", "elementare": "Elemental", "krieger": "Warrior",
             "zauberer": "Wizard", "dämon": "Demon", "dämonen": "Demon", "hydra": "Hydra", "hydren": "Hydra",
             "eichhörnchen": "Squirrel", "ratte": "Rat", "ratten": "Rat", "soldat": "Soldier", "soldaten": "Soldier",
             "menschen": "Human", "mensch": "Human", "schurke": "Rogue", "schurken": "Rogue", "kleriker": "Cleric",
             "vögel": "Bird", "vogel": "Bird", "dämmerung": "Horror", "slivers": "Sliver", "sliver": "Sliver",
             "eldrazi": "Eldrazi", "faerie": "Faerie", "feen": "Faerie", "riesen": "Giant", "riese": "Giant",
             "zwerge": "Dwarf", "zwerg": "Dwarf", "hunde": "Dog", "hund": "Dog", "frösche": "Frog", "frosch": "Frog"}
# Verzauberungs- und Artefakttypen als Thema: Typ -> (deutsche Bezeichnung, starke Hinweise im Commander-Text)
CARD_SUBTYPES = {
    "Saga": ("Sagen", ["lore counter", "chapter", "saga"]),
    "Aura": ("Auren", ["aura", "enchanted creature", "enchanted permanent", "bestow", "enchant creature"]),
    "Class": ("Klassen", ["class", "class level"]),
    "Room": ("Räume", ["room", "unlock"]),
    "Case": ("Fälle", ["case", "solved"]),
    "Shrine": ("Schreine", ["shrine"]),
    "Curse": ("Flüche", ["curse", "enchanted player"]),
    "Background": ("Hintergründe", ["background"]),
    "Role": ("Rollen", ["role token", "role"]),
    "Equipment": ("Ausrüstungen", ["equipment", "equipped creature", "equip"]),
    "Vehicle": ("Fahrzeuge", ["vehicle", "crew"]),
}
SUBTYPE_DE = {"saga": "Saga", "sagas": "Saga", "sage": "Saga", "sagen": "Saga", "aura": "Aura", "auras": "Aura", "auren": "Aura",
              "class": "Class", "classes": "Class", "klasse": "Class", "klassen": "Class", "room": "Room", "rooms": "Room",
              "raum": "Room", "räume": "Room", "case": "Case", "cases": "Case", "fälle": "Case", "shrine": "Shrine",
              "shrines": "Shrine", "schrein": "Shrine", "schreine": "Shrine", "curse": "Curse", "curses": "Curse", "fluch": "Curse",
              "flüche": "Curse", "background": "Background", "backgrounds": "Background", "hintergrund": "Background",
              "hintergründe": "Background", "role": "Role", "roles": "Role", "rolle": "Role", "rollen": "Role",
              "equipment": "Equipment", "ausrüstung": "Equipment", "ausrüstungen": "Equipment", "vehicle": "Vehicle",
              "vehicles": "Vehicle", "fahrzeug": "Vehicle", "fahrzeuge": "Vehicle"}
REMINDER_RE = re.compile(r"\([^)]*\)")


def theme_terms(theme):
    """Liefert [(Beschreibung, SQL-Bedingung, Parameter)] für ein frei eingegebenes Thema (deutsch oder englisch)."""
    out, t = [], theme.lower().strip()
    if not t:
        return out
    key = ALIAS.get(t, t)
    if key in THEMES:
        words, typ = THEMES[key]
        out.append(({"enchantress": "Verzauberungen"}.get(key, key.capitalize()), "(" + " OR ".join("lower(oracle_text) LIKE ?" for _ in words) + ")",
                    [f"%{w.lower()}%" for w in words]))
    for _rx, words, label in SYNERGY:
        if key in THEMES or t in SUBTYPE_DE:  # eigenes Thema oder Verzauberungs-/Artefakttyp: nicht doppelt zählen
            break
        if label.lower() == t or label.lower().startswith(t) and len(t) >= 4:
            out.append((label, "(" + " OR ".join("lower(oracle_text) LIKE ?" for _ in words) + ")", [f"%{w.lower()}%" for w in words]))
    for w in re.split(r"[,\s]+", t):
        if not w:
            continue
        st = SUBTYPE_DE.get(w)
        if st:  # Verzauberungs-/Artefakttyp: Commander mit diesem Typ oder Text dazu (ohne Erinnerungstext, siehe suggest_commanders)
            words = CARD_SUBTYPES[st][1]
            out.append((f"{CARD_SUBTYPES[st][0]} ({st})", "(" + " OR ".join(["type_line LIKE ?"] + ["lower(oracle_text) LIKE ?" for _ in words]) + ")",
                        [f"%{st}%"] + [f"%{x}%" for x in words]))
            continue
        sub = SUBTYPES or set()
        eng = {st.lower(): st for st in sub}
        eng.update({plural(st).lower(): st for st in sub})
        tr = TRIBES_DE.get(w) or (eng.get(w) if len(w) >= 3 else None)
        if tr:
            out.append((f"Kreaturtyp {tr}", "(type_line LIKE ? OR oracle_text LIKE ?)", [f"%{tr}%", f"%{tr}%"]))
    if not out:  # frei: Wort kommt im Regeltext oder in der Typzeile vor
        ws = [w for w in re.split(r"[,\s]+", t) if len(w) >= 3]
        if ws:
            out.append((theme.strip(), "(" + " AND ".join("(lower(oracle_text) LIKE ? OR lower(type_line) LIKE ?)" for _ in ws) + ")",
                        [x for w in ws for x in (f"%{w}%", f"%{w}%")]))
    return out

def pick_varied(rows, n, seed="", vary_colors=False, hits=None, bonus=None):
    """Abwechslungsreiche Auswahl aus einer nach Passung sortierten Liste:
    ein Teil beliebte Commander, ein Teil Geheimtipps (weniger gespielt), ein Teil günstige,
    Rest gewichtet zufällig; bei offenen Farben höchstens drei gleiche Farbkombinationen."""
    if len(rows) <= n:
        return [(r, "beliebt" if i < 3 else "") for i, r in enumerate(rows)]
    rnd = random.Random(seed or None)
    hits = hits or {}
    best = len(hits.get(rows[0]["name"], [])) if rows else 0
    # Kandidaten: nur gut passende (gleiche Trefferzahl wie die besten), höchstens 80
    pool = [r for r in rows if len(hits.get(r["name"], [])) >= best][:80] or rows[:80]
    first = []
    if bonus:  # Stammes- oder Typ-Thema: Commander, deren Text den Typ unterstützt, zuerst
        strong = [r for r in pool if bonus.get(r["name"], 0) >= 2]
        if len(strong) >= n * 2:
            pool = strong
        elif strong:  # wenige echte Unterstützer: die stehen vorne, der Rest füllt auf
            first = sorted(strong, key=lambda r: (-bonus[r["name"]], r["edhrec_rank"] or 10 ** 7))[:max(1, (2 * n) // 3)]
    if len(pool) < n * 2:
        pool = rows[:max(n * 3, 36)]
    by_rank = sorted(pool, key=lambda r: r["edhrec_rank"] or 10 ** 7)
    chosen, names, ci_count = [], set(), {}
    def ok(r):
        if r["name"] in names:
            return False
        if vary_colors and ci_count.get(r["color_identity"] or "", 0) >= 3:
            return False
        return True
    def take(r, tag):
        chosen.append((r, tag)); names.add(r["name"])
        ci_count[r["color_identity"] or ""] = ci_count.get(r["color_identity"] or "", 0) + 1
    def take_some(cands, k, tag):
        cands = [r for r in cands if ok(r)]
        rnd.shuffle(cands)
        for r in cands:
            if k <= 0 or len(chosen) >= n:
                break
            if ok(r):
                take(r, tag); k -= 1
    for r in first:
        if ok(r) and len(chosen) < n:
            take(r, "passt genau")
    q = max(1, n // 3)
    take_some(by_rank[:max(q * 2, 8)], q, "beliebt")                       # bekannte, oft gespielte
    third = len(by_rank) // 3
    take_some(by_rank[third:], q, "Geheimtipp")                            # seltener gespielt
    take_some([r for r in pool if r["eur"] not in (None, "") and float(r["eur"]) <= 2], max(1, n // 6), "günstig")
    rest = [r for r in pool if ok(r)]                                     # Rest: Beliebtere leicht bevorzugt
    weights = [1.0 / (1 + i / 15) for i in range(len(rest))]
    while len(chosen) < n and rest:
        r = rnd.choices(rest, weights=weights)[0]
        i = rest.index(r); rest.pop(i); weights.pop(i)
        if ok(r):
            take(r, "")
    if len(chosen) < n:                                                    # Farbgrenze notfalls lockern
        for r in pool + rows:
            if len(chosen) >= n:
                break
            if r["name"] not in names:
                take(r, "")
    order = {"passt genau": -1, "beliebt": 0, "": 1, "günstig": 2, "Geheimtipp": 3}
    chosen.sort(key=lambda x: (order.get(x[1], 1), x[0]["edhrec_rank"] or 10 ** 7))
    return chosen

def suggest_commanders(p):
    g = lambda k: (p.get(k) or [""])[0].strip()
    ci = "".join(x for x in ORDER if x in g("ci").upper())
    colorless = g("ci").upper() in ("C", "FARBLOS")
    fewer, nogc, theme = g("fewer") == "1", g("nogc") == "1", g("theme")
    maxeur = float(g("maxeur").replace(",", ".")) if re.fullmatch(r"\d+([.,]\d+)?", g("maxeur")) else 0
    if not ci and not colorless and not theme:
        return {"error": "Bitte eine Farbidentität oder ein Thema angeben."}
    con = db()
    con.row_factory = sqlite3.Row
    try:
        creature_subtypes(con)
        where, args = ["can_be_commander = 1", "commander_legal = 1"], []
        if nogc:
            where.append("game_changer = 0")
        if maxeur:
            where.append("(eur IS NULL OR eur <= ?)"); args.append(maxeur)
        terms = theme_terms(theme)
        if theme and not terms:
            return {"error": "Zum Thema wurde nichts gefunden. Andere Begriffe probieren (z. B. Tokens, Drachen, Friedhof).", "cards": []}
        rows = con.execute("SELECT * FROM cards WHERE " + " AND ".join(where), args).fetchall()
        def ci_ok(r):
            c = r["color_identity"] or ""
            if colorless:
                return c == ""
            if not ci:
                return True
            return c == ci if not fewer else (c != "" and all(x in ci for x in c))
        rows = [r for r in rows if ci_ok(r)]
        hits, bonus = {}, {}
        for label, cond, a in terms:
            if label.startswith("Kreaturtyp "):  # Commander, deren Text den Typ nennt, sind die eigentlichen Stammes-Commander
                for (nm,) in con.execute("SELECT name FROM cards WHERE can_be_commander = 1 AND oracle_text LIKE ?", (a[0],)):
                    bonus[nm] = bonus.get(nm, 0) + 2
            names = {x[0] for x in con.execute(f"SELECT name FROM cards WHERE can_be_commander = 1 AND {cond}", a)}
            words = [x.strip("%").lower() for x in a]
            need_all = " AND " in cond
            for r in rows:
                if r["name"] not in names:
                    continue
                txt = REMINDER_RE.sub("", (r["oracle_text"] or "")).lower()  # Erinnerungstext zählt nicht
                tl = (r["type_line"] or "").lower()
                found = [w for w in words if w and (w in txt or w in tl)]
                if not found or (need_all and len(set(found)) < len(set(words)) // (2 if label == theme.strip() else 1)):
                    continue
                hits.setdefault(r["name"], []).append(label)
                if "(" in label and label.endswith(")"):  # Verzauberungs-/Artefakttyp: je weiterem starkem Hinweis höher
                    sup = {w for w in found[0:] if w in txt and w != words[0]} | ({words[0]} if words[0] in txt else set())
                    bonus[r["name"]] = bonus.get(r["name"], 0) + 2 * len(sup) + (1 if words[0] in tl else 0)
        if theme:
            rows = [r for r in rows if r["name"] in hits]
        big = 10 ** 7
        rows.sort(key=lambda r: (-len(hits.get(r["name"], [])), -bonus.get(r["name"], 0), r["edhrec_rank"] or big, r["name"]))
        total = len(rows)
        shown = {x for x in g("shown").split("|") if x}
        rows = [r for r in rows if r["name"] not in shown]
        picked = pick_varied(rows, int(g("limit") or 12), g("seed"), vary_colors=not ci or fewer, hits=hits, bonus=bonus)
        out = []
        for r, tag in picked:
            txt = (r["oracle_text"] or "").replace("\n", " ")
            out.append({"name": r["name"], "ci": r["color_identity"] or "", "type": r["type_line"], "image": r["image"] or "",
                        "eur": r["eur"], "rank": r["edhrec_rank"], "gc": bool(r["game_changer"]), "tag": tag,
                        "why": hits.get(r["name"], []), "text": txt[:220] + ("…" if len(txt) > 220 else "")})
        return {"cards": out, "total": total, "left": len(rows) - len(out), "ci": ci or ("C" if colorless else ""), "theme": theme}
    finally:
        con.close()

def search(p):
    g = lambda k: (p.get(k) or [""])[0].strip()
    where, args = [], []
    for w in g("q").split():
        where.append("(name LIKE ? OR oracle_text LIKE ? OR type_line LIKE ?)")
        args += [f"%{w}%"] * 3
    if g("type"):
        where.append("type_line LIKE ?"); args.append(f"%{g('type')}%")
    if g("kw"):
        where.append("keywords LIKE ?"); args.append(f"%{g('kw')}%")
    if g("cmin"):
        where.append("cmc >= ?"); args.append(float(g("cmin")))
    if g("cmax"):
        where.append("cmc <= ?"); args.append(float(g("cmax")))
    if g("ci"):  # erlaubte Farbidentität, z. B. "WUB"; "C" = farblos
        for x in ORDER:
            if x not in g("ci").upper():
                where.append("color_identity NOT LIKE ?"); args.append(f"%{x}%")
    if g("legal") == "1":
        where.append("commander_legal = 1")
    if g("commander") == "1":
        where.append("can_be_commander = 1")
    sql = "SELECT name,mana_cost,cmc,type_line,color_identity,edhrec_rank,eur,scryfall_uri,cardmarket_uri,game_changer,image FROM cards"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY edhrec_rank IS NULL, edhrec_rank, name LIMIT 100"
    con = db()
    keys = "name mana cmc type ci rank eur scryfall cardmarket gc image".split()
    rows = [dict(zip(keys, r)) for r in con.execute(sql, args)]
    if not rows and len(g("q")) >= 3:  # vielleicht ein deutscher (oder anderer fremdsprachiger) Kartenname
        try:
            translate_names(con, [g("q")], limit=1)
            al = con.execute("SELECT name FROM name_alias WHERE alias = ? AND name <> ''", (g("q"),)).fetchone()
        except Exception:
            al = None
        if al:
            rows = [dict(zip(keys, r)) for r in con.execute(sql.split(" WHERE ")[0].split(" ORDER BY ")[0] + " WHERE name = ? LIMIT 5", (al[0],))]
    for r in rows:
        r["eur"] = float(r["eur"]) if r["eur"] not in (None, "") else None
        r["cardmarket"] = cm_link(r["name"]) or r["cardmarket"]
    return rows


def card_dict(r, qty=1):
    eur = r["eur"]
    return {"name": r["name"], "mana": r["mana_cost"], "cmc": r["cmc"], "qty": qty,
            "eur": float(eur) if eur not in (None, "") else None, "image": r["image"],
            "scryfall": r["scryfall_uri"], "cardmarket": cm_link(r["name"]) or r["cardmarket_uri"], "gc": bool(r["game_changer"]),
            "land": "Land" in r["type_line"].split(" // ")[0]}


def basic_dict(con, name, qty):
    r = con.execute("SELECT * FROM cards WHERE name = ? AND type_line LIKE 'Basic%'", (name,)).fetchone()
    d = card_dict(r, qty) if r else {"name": name, "mana": "", "cmc": 0, "qty": qty, "eur": None, "image": None,
                                     "scryfall": None, "cardmarket": None, "gc": False, "land": True}
    d["basic"] = True
    d["eur"] = None  # Basic Lands werden nicht eingepreist
    return d


THEMES = {
    "mill": (["mill", "top cards of target player", "library into their graveyard"], None),
    "lifegain": (["gain life", "lifelink"], None),
    "stompy": (["trample", "haste", "hexproof", "+1/+1 counter"], "Creature"),
    "tokens": (["token"], None),
    "counters": (["+1/+1 counter", "proliferate"], None),
    "aristocrats": (["sacrifice", "dies"], None),
    "spellslinger": (["instant or sorcery"], None),
    "voltron": (["equipped", "aura", "equipment"], None),
    "enchantress": (["enchantment spell", "enchantments you control", "enchantment you control", "constellation",
                     "enchantment enters", "enchantment card", "enchanted creature"], None),
}
ALIAS = {"lebensgewinn": "lifegain", "opfer": "aristocrats", "marken": "counters", "zauber": "spellslinger",
         "verzauberung": "enchantress", "verzauberungen": "enchantress", "enchantment": "enchantress", "enchantments": "enchantress"}
FIXED = [  # Name, Ziel-Anzahl, SQL-Bedingung (Nicht-Länder)
    ("Ramp", 10, "(oracle_text LIKE '%Add {%' OR oracle_text LIKE '%Add one mana%' OR oracle_text LIKE '%Add two mana%' OR oracle_text LIKE '%basic land card%') AND cmc <= 3"),
    ("Kartenvorteil", 9, "(oracle_text LIKE '%draw a card%' OR oracle_text LIKE '%draw two%' OR oracle_text LIKE '%draw three%')"),
    ("Entfernung", 8, "(oracle_text LIKE '%destroy target%' OR oracle_text LIKE '%exile target%')"),
    ("Massenentfernung", 3, "(oracle_text LIKE '%destroy all%' OR oracle_text LIKE '%exile all%')"),
]
# Synergie: Begriffe im Text des Commanders -> Suchbegriffe für passende Karten
SYNERGY = [
    (r"\+1/\+1 counter", ["+1/+1 counter", "proliferate"], "+1/+1-Marken"),
    (r"proliferate|loyalty counter|poison counter|\bcounters? on\b", ["counter on", "counters on", "proliferate"], "Marken"),
    (r"\btokens?\b", ["token"], "Spielsteine"),
    (r"sacrific", ["sacrifice"], "Opfern"),
    (r"\bdies\b|\bdie\b", ["dies"], "Sterben"),
    (r"graveyard", ["graveyard"], "Friedhof"),
    (r"\bartifacts?\b", ["artifact"], "Artefakte"),
    (r"\benchantments?\b", ["enchantment"], "Verzauberungen"),
    (r"\bequip", ["equip"], "Ausrüstungen"),
    (r"\bauras?\b", ["aura"], "Auren"),
    (r"\bsagas?\b|lore counter", ["saga", "lore counter"], "Sagen"),
    (r"instant or sorcery|noncreature spell", ["instant or sorcery", "noncreature spell"], "Spontanzauber/Hexereien"),
    (r"landfall|land enters|lands? you control|additional land", ["landfall", "land enters", "additional land"], "Länder"),
    (r"gains? (\d+ |x |that much )?life|lifelink", ["gain life", "gains life", "you gain", "lifelink"], "Lebensgewinn"),
    (r"loses? (\d+ |x |that much )?life", ["loses life", "lose life", "each opponent loses"], "Lebensverlust"),
    (r"\bmill", ["mill"], "Mahlen"),
    (r"\battack", ["attacks", "attacking"], "Angriff"),
    (r"\bflying\b", ["flying"], "Flugfähigkeit"),
    (r"treasure", ["treasure"], "Schätze"),
    (r"discard", ["discard"], "Abwerfen"),
    (r"\bcop(y|ies)\b", ["copy"], "Kopieren"),
    (r"poison|infect|toxic", ["poison", "infect", "toxic"], "Gift"),
    (r"\benergy\b", ["energy"], "Energie"),
    (r"\bdraws? (a|two|three|x|that many|\d+) cards?", ["draw a card", "draws a card", "draw two cards", "draw cards"], "Kartenziehen"),
    (r"\blegendary\b", ["legendary"], "Legendäres"),
    (r"\bexile\b.*\breturn", ["exile", "return it"], "Exil und Rückkehr"),
]
SUBTYPES = None


def creature_subtypes(con):
    global SUBTYPES
    if SUBTYPES is None:
        SUBTYPES = set()
        for (t,) in con.execute("SELECT type_line FROM cards WHERE type_line LIKE '%Creature —%'"):
            for part in t.split(" // "):
                if "Creature" in part and "—" in part:
                    SUBTYPES.update(w for w in part.split("—", 1)[1].split() if re.fullmatch(r"[A-Z][a-z'-]{2,}", w))
        SUBTYPES -= set(CARD_SUBTYPES)  # z. B. „Enchantment Creature — Saga …“: Saga ist ein Verzauberungstyp, kein Kreaturtyp
    return SUBTYPES


def plural(w):
    special = {"Elf": "Elves", "Dwarf": "Dwarves", "Wolf": "Wolves", "Werewolf": "Werewolves", "Ox": "Oxen"}
    return special.get(w) or (w + "es" if w.endswith(("s", "x", "ch", "sh")) else w + "s")


def synergy_terms(con, cmds):
    """Was der Commander-Text verlangt: Mechaniken und genannte Kreaturentypen -> (Suchbegriffe, Bezeichnungen)."""
    lines = []
    for r in cmds:  # reine Fähigkeitszeilen („Flying, vigilance, lifelink“) beschreiben den Commander selbst, kein Thema
        kw = set((r["keywords"] or "").lower().split())
        for line in (r["oracle_text"] or "").split("\n"):
            parts = [x.strip().lower() for x in line.split(",") if x.strip()]
            if parts and all(all(w in kw for w in x.split()) for x in parts) and "proliferate" not in line.lower():
                continue
            lines.append(line)
    text = " ".join(lines)
    low = text.lower()
    terms, labels, tribal = [], [], []
    for pat, t, label in SYNERGY:
        if re.search(pat, low):
            terms += t; labels.append(label)
    names = {w for r in cmds for w in re.split(r"[ ,]+", r["name"])}
    for st in sorted(creature_subtypes(con)):
        if st in names:
            continue
        if re.search(rf"\b({re.escape(st)}|{re.escape(plural(st))})\b", text):
            tribal.append(st); labels.append(st)
    return list(dict.fromkeys(tribal + terms))[:14], labels[:8], set(tribal)


BASICS = {"W": "Plains", "U": "Island", "B": "Swamp", "R": "Mountain", "G": "Forest"}
NL = "type_line NOT LIKE '%Land%'"


def theme_sql(theme):
    """SQL-Bedingung und Parameter für ein Thema (feste Themen oder freie Stichwörter)."""
    th = ALIAS.get(theme.lower(), theme.lower())
    terms, typ = THEMES.get(th) or ([t for t in re.split(r"[,;\s]+", th) if t], None)
    if not terms:
        return None, []
    sql = "(" + " OR ".join(["(oracle_text LIKE ? OR type_line LIKE ? OR keywords LIKE ? OR name LIKE ?)"] * len(terms)) + ")"
    if typ:
        sql += f" AND type_line LIKE '%{typ}%'"
    return sql, [f"%{t}%" for t in terms for _ in range(4)]


def build(p, uid=0):
    g = lambda k: (p.get(k) or [""])[0].strip()
    con = db()
    con.row_factory = sqlite3.Row

    def one(name, commander=False):
        r, hint = lookup(con, name, commander)
        if hint:
            notes.append(hint)
        return r

    island = lambda r: "Land" in r["type_line"].split(" // ")[0]
    notes = []
    cmds = []
    for cn in cmd_names(g("commander"))[:2]:  # bis zu zwei Commander (Partner, Hintergrund, Freunde fürs Leben …)
        r = one(cn, True)
        if not r:
            notes.append(f"Commander „{cn}“ nicht gefunden.")
            continue
        if not r["can_be_commander"]:
            notes.append(f"{r['name']} gilt nach meiner Näherung nicht als Commander, bitte prüfen.")
        if not r["commander_legal"]:
            notes.append(f"{r['name']} ist im Commander-Format nicht legal (gebannt).")
        if r["name"] not in [c["name"] for c in cmds]:
            cmds.append(r)
    if g("commander") and not cmds:
        notes.append("Kein Commander gefunden. Das Deck wird ohne Commander vorgeschlagen.")
    if len(cmds) == 2:
        err = partner_problem(cmds)
        if err:
            notes.append("Achtung: " + err)
    cmd = cmds[0] if cmds else None
    own, chosen = [], set(c["name"] for c in cmds)
    maxprice = float(g("maxprice").replace(",", ".") or 0) if re.fullmatch(r"[\d.,]*", g("maxprice")) else 0
    budget = float(g("budget").replace(",", ".") or 0) if re.fullmatch(r"[\d.,]*", g("budget")) else 0
    price = lambda r: float(r["eur"]) if r["eur"] not in (None, "") else 0.0
    spent = [sum(price(c) for c in cmds)]
    nogc = g("nogc") == "1"
    coll = g("coll")  # "" | "prefer" | "only"
    collection_table(con)
    has_coll = coll and con.execute("SELECT 1 FROM collection WHERE owner = ? LIMIT 1", (int(uid),)).fetchone()
    excluded = {x.strip() for x in g("exclude").splitlines() if x.strip()}
    for line in g("cards").splitlines():
        n = re.sub(r"^\d+\s*x?\s+", "", line.strip())
        if not n:
            continue
        r = one(n)
        if not r:
            notes.append(f"„{n}“ nicht gefunden.")
        elif not r["commander_legal"]:
            notes.append(f"{r['name']} ist im Commander-Format nicht legal und wurde weggelassen.")
        elif not r["type_line"].startswith("Basic") and r["name"] not in chosen:
            own.append(r); chosen.add(r["name"])
    if cmds:
        ci = "".join(x for x in ORDER if any(x in c["color_identity"] for c in cmds))
    elif g("ci"):
        ci = "".join(x for x in ORDER if x in g("ci").upper())
    elif own:
        ci = "".join(x for x in ORDER if any(x in r["color_identity"] for r in own))
    elif g("theme"):
        ci = ORDER
        notes.append("Ohne Commander und Farbidentität wurden alle fünf Farben zugelassen.")
    else:
        return {"error": "Bitte mindestens eine Angabe machen: Commander, Thema, Farbidentität oder Karten.",
                "notes": notes}
    if nogc and any(r["game_changer"] for r in own):
        notes.append("Deine eigenen Karten enthalten Game Changer. Sie wurden trotz Filter übernommen.")
    if excluded:
        notes.append(f"{len(excluded)} als nicht verfügbar markierte Karten wurden ausgeschlossen.")
    for r in own:
        if any(x not in ci for x in r["color_identity"]):
            notes.append(f"{r['name']} passt nicht zur Farbidentität ({ci or 'farblos'}).")

    spent[0] += sum(price(r) for r in own)

    def pick(sql, args, n, order="edhrec_rank IS NULL, edhrec_rank", order_args=(), filt=None, factor=1):
        if n <= 0:
            return []
        where, a = ["commander_legal = 1", "type_line NOT LIKE 'Basic%'"], []
        if maxprice:
            where.append("(eur IS NULL OR eur = '' OR CAST(eur AS REAL) <= ?)"); a.append(maxprice)
        for x in ORDER:
            if x not in ci:
                where.append("color_identity NOT LIKE ?"); a.append(f"%{x}%")
        if nogc:
            where.append("game_changer = 0")
        if has_coll and coll == "only":
            where.append(f"name IN (SELECT name FROM collection WHERE owner = {int(uid)} AND qty > 0)")
        block = chosen | excluded
        if block:
            where.append("name NOT IN (%s)" % ",".join("?" * len(block))); a += list(block)
        ordr = (f"(name IN (SELECT name FROM collection WHERE owner = {int(uid)} AND qty > 0)) DESC, " + order) \
            if has_coll and coll == "prefer" else order
        rows = con.execute(f"SELECT * FROM cards WHERE {' AND '.join(where)} AND {sql} "
                           f"ORDER BY {ordr} LIMIT {int(n) * max(factor, 6 if budget else 1)}", a + args + list(order_args)).fetchall()
        out = []
        for r in rows:
            if len(out) >= n:
                break
            if filt and not filt(r):
                continue
            if budget:  # Gesamtbudget: teure Karten überspringen, Reserve von 0,25 € je noch offenem Platz
                left = max(0, 99 - len(chosen) - 1)
                if spent[0] + price(r) > budget - 0.25 * left:
                    continue
            out.append(r)
            chosen.add(r["name"])
            spent[0] += price(r)
        return out

    size = 100 - max(1, len(cmds))  # Karten neben dem/den Commander(n)
    groups = [("Deine Karten", own)] if own else []
    nonland = lambda: sum(1 for _, rs in groups for r in rs if not island(r))
    for name, n, sql in FIXED:
        groups.append((name, pick(f"{NL} AND {sql}", [], n)))
    syn_terms, syn_labels, tribal = synergy_terms(con, cmds) if cmds else ([], [], set())
    if syn_terms:  # Karten, die zum Text des Commanders passen; je mehr Treffer, desto weiter vorn (Kreaturentypen zählen dreifach)
        cond = " OR ".join(["(oracle_text LIKE ? OR type_line LIKE ?)"] * len(syn_terms))
        score = " + ".join(f"(CASE WHEN oracle_text LIKE ? OR type_line LIKE ? THEN {3 if t in tribal else 1} ELSE 0 END)"
                           for t in syn_terms)
        likes = [f"%{t}%" for t in syn_terms for _ in range(2)]
        groups.append((f"Synergie mit dem Commander ({', '.join(syn_labels)})",
                       pick(f"{NL} AND ({cond})", likes, 15 if g("theme") else 25,
                            order=f"({score}) DESC, edhrec_rank IS NULL, edhrec_rank", order_args=likes)))
    elif cmds:
        notes.append("Im Text des Commanders wurden keine typischen Mechaniken erkannt, deshalb Auswahl nach allgemeiner Beliebtheit.")
    tsql, targs = theme_sql(g("theme"))
    if tsql:
        groups.append((f"Thema: {g('theme')}", pick(f"{NL} AND {tsql}", targs, size - 42 - nonland())))
    elif not syn_terms:
        notes.append("Kein Thema angegeben, deshalb wurden allgemein beliebte Karten gewählt.")
    groups.append(("Weitere beliebte Karten", pick(NL, [], size - 36 - nonland())))

    own_l = sum(1 for r in own if island(r))
    lands_total = size - nonland()
    free = max(0, lands_total - own_l)
    if len(ci) >= 2:  # Mehrfarbig: zuerst Länder, die mindestens zwei Deckfarben liefern, dann wenige Spezialländer
        n_fix = min(free, {2: 12, 3: 18, 4: 24, 5: 31}[len(ci)])
        util = pick("type_line LIKE '%Land%'", [], n_fix, filt=lambda r: len(produced_colors(r, ci)) >= 2, factor=8)
        util += pick("type_line LIKE '%Land%'", [], max(0, min(3, free - len(util))))
    else:
        util = pick("type_line LIKE '%Land%'", [], max(0, min(8, free)))
    allr = [r for _, rs in groups for r in rs] + util
    nb = lands_total - own_l - len(util)
    spells = [r for r in allr if not island(r)] + cmds
    letters = [x for x in ORDER if x in ci]
    basics = []
    if nb > 0 and not letters:
        basics = [("Wastes", nb)]
    elif nb > 0:
        w = [1 + sum(r["mana_cost"].count("{" + x) + r["mana_cost"].count("/" + x) for r in spells) for x in letters]
        tot = sum(w)
        q = [nb * v // tot for v in w]
        for i in sorted(range(len(w)), key=lambda i: -(nb * w[i] % tot))[: nb - sum(q)]:
            q[i] += 1
        basics = [(BASICS[x], k) for x, k in zip(letters, q) if k]

    out = ([{"name": "Commander", "cards": [card_dict(c) for c in cmds]}] if cmds else [])
    out += [{"name": n, "cards": [card_dict(r) for r in rs]} for n, rs in groups if rs]
    out.append({"name": "Länder", "cards": [card_dict(r) for r in util] + [basic_dict(con, n, k) for n, k in basics]})
    curve = [0] * 8
    for r in allr:
        if not island(r):
            curve[min(int(r["cmc"]), 7)] += 1
    priced = [float(r["eur"]) for r in allr + cmds if r["eur"] not in (None, "")]
    total = len(allr) + sum(k for _, k in basics)
    if total < 100 - max(1, len(cmds)):
        notes.append(f"Es konnten nur {total} von {100 - max(1, len(cmds))} Karten gefunden werden.")
    if coll and not has_coll:
        notes.append("Du hast noch keine Sammlung importiert. Das Deck wurde ohne Sammlung gebaut.")
    elif has_coll:
        notes.append("Nur Karten aus deiner Sammlung (außer Standardländern)." if coll == "only" else
                     "Karten aus deiner Sammlung wurden bevorzugt.")
    if budget:
        unpriced = sum(1 for r in allr + cmds if r["eur"] in (None, "") and not r["type_line"].startswith("Basic"))
        notes.append(f"Budget: ca. {sum(priced):.2f} € von {budget:.2f} € genutzt (ohne Standardländer)."
                     + (f" {unpriced} Karte(n) ohne bekannten Preis sind nicht eingerechnet." if unpriced else ""))
    if maxprice:
        notes.append(f"Höchstpreis je Karte: {maxprice:.2f} €.")
    if syn_terms:
        notes.append("Synergie-Karten wurden nach dem Text des Commanders gewählt, die übrigen nach allgemeiner EDHREC-Beliebtheit. Bitte prüfen.")
    else:
        notes.append("Die Auswahl folgt der allgemeinen EDHREC-Beliebtheit, nicht commanderspezifischen Daten. Bitte prüfen.")
    lines = [f"{c['qty']} {c['name']}" for gr in out for c in gr["cards"]]
    return {"commander": " + ".join(c["name"] for c in cmds) or None, "ci": ci, "notes": notes, "groups": out, "curve": curve,
            "cost": {"total": sum(priced), "priced": len(priced), "missing": len(allr) + len(cmds) - len(priced)},
            "export": "\n".join(lines)}


# ---------------------------------------------------------------- Kartenscanner (Texterkennung)
# Browser: Tesseract.js (Apache-2.0) wird beim ersten Scan einmalig aus der npm-Paketquelle geladen und lokal
# im Datenordner abgelegt; danach läuft die Erkennung ohne Internet direkt im Browser (PC, Handy, Android-App).
OCR_DIR = os.path.join(DATA_DIR, "ocr7")
OCR_PKGS = [  # (Paket, Version, {Datei im Paket: Ablage})
    ("tesseract.js", "7.0.0", {"package/dist/tesseract.min.js": "tesseract.min.js", "package/dist/worker.min.js": "worker.min.js"}),
    ("tesseract.js-core", "7.0.0", {f"package/{n}": f"core/{n}" for n in (  # passend zu tesseract.js 7
        "tesseract-core-lstm.wasm.js", "tesseract-core-simd-lstm.wasm.js", "tesseract-core-relaxedsimd-lstm.wasm.js")}),
    ("@tesseract.js-data/eng", "1.0.0", {"package/4.0.0_best_int/eng.traineddata.gz": "lang/eng.traineddata.gz"}),
    ("@tesseract.js-data/deu", "1.0.0", {"package/4.0.0_best_int/deu.traineddata.gz": "lang/deu.traineddata.gz"}),
]
OCR_LOCK = threading.Lock()


def ocr_files():
    return [dst for _, _, m in OCR_PKGS for dst in m.values()]


def ocr_status():
    have = [f for f in ocr_files() if os.path.isfile(os.path.join(OCR_DIR, f))]
    return {"ready": len(have) == len(ocr_files()), "files": len(have), "total": len(ocr_files()),
            "size_mb": round(sum(os.path.getsize(os.path.join(OCR_DIR, f)) for f in have) / 1e6, 1)}


def ocr_prepare():
    """Lädt die Texterkennung einmalig (rund 30 MB) von registry.npmjs.org und entpackt nur die benötigten Dateien."""
    import tarfile, io
    with OCR_LOCK:
        if ocr_status()["ready"]:
            return ocr_status()
        for pkg, ver, files in OCR_PKGS:
            if all(os.path.isfile(os.path.join(OCR_DIR, d)) for d in files.values()):
                continue
            base = pkg.split("/")[-1]
            url = f"https://registry.npmjs.org/{pkg}/-/{base}-{ver}.tgz"
            try:
                data = fetch(url)
            except Exception as e:
                return {"error": f"Texterkennung konnte nicht geladen werden ({e}). Internetverbindung prüfen.", **ocr_status()}
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
                for src, dst in files.items():
                    m = tf.getmember(src)
                    out = os.path.join(OCR_DIR, dst)
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    with tf.extractfile(m) as f, open(out + ".part", "wb") as o:
                        o.write(f.read())
                    os.replace(out + ".part", out)
        return ocr_status()


SET_RE = re.compile(r"\b(\d{1,4})\s*/\s*\d{1,4}\b")
SETCODE_RE = re.compile(r"\b([A-Z0-9]{3,5})\s*[•·*.\-]?\s*(?:EN|DE|FR|IT|ES|PT|JA|KO|RU|ZHS|ZHT)\b")


def scan_match(p):
    """Erkannte Textzeilen eines Kartenfotos -> wahrscheinlichste Karten (Name zuerst, sonst Set + Sammlernummer)."""
    g = lambda k: (p.get(k) or [""])[0]
    try:
        lines = [str(x) for x in json.loads(g("lines") or "[]")][:40]
    except Exception:
        return {"error": "Ungültige Daten."}
    con = db()
    con.row_factory = sqlite3.Row
    idx = name_index(con)
    keys = list(idx)
    alias_table(con)
    aliases = {a.lower(): n for a, n in con.execute("SELECT alias, name FROM name_alias WHERE name <> ''")}
    found = {}

    def add(name, score, via):
        if name and (name not in found or found[name]["score"] < score):
            found[name] = {"name": name, "score": round(score, 3), "via": via}

    tried = 0
    for i, raw in enumerate(lines):
        t = re.sub(r"[^A-Za-zÀ-ÿ',\- ]+", " ", raw).strip(" -,'")
        t = re.sub(r"\s{2,}", " ", t)
        letters = sum(ch.isalpha() for ch in t)
        if len(t) < 3 or letters < 3 or letters < 0.6 * len(raw.strip() or "x") * 0.7:
            continue
        if re.match(r"^(Legendary|Creature|Artifact|Enchantment|Instant|Sorcery|Land|Basic|Planeswalker|Battle|Kreatur|"
                    r"Legendäre|Artefakt|Verzauberung|Spontanzauber|Hexerei|Standardland)\b", t):
            continue
        pos = max(0.0, 0.03 * i)  # Namen stehen oben auf der Karte
        k = t.lower()
        if k in idx:
            for n in idx[k]:  # exakter Kartenname vor Treffer auf nur eine Kartenseite („A // B“)
                add(n, (1.0 if n.lower() == k else 0.93) - pos, "Name" if n.lower() == k else "Kartenseite")
        elif k in aliases:
            add(aliases[k], 0.98 - pos, "deutscher Name")
        else:
            if tried >= 12:
                continue
            tried += 1
            for cand in difflib.get_close_matches(k, keys, 3, 0.7):
                r = difflib.SequenceMatcher(None, k, cand).ratio()
                for n in idx[cand]:
                    add(n, r - pos - (0.02 if n.lower() == cand else 0.09), "ähnlicher Name")
            for cand in difflib.get_close_matches(k, list(aliases), 2, 0.75):
                add(aliases[cand], difflib.SequenceMatcher(None, k, cand).ratio() - pos - 0.03, "ähnlicher deutscher Name")
    best = max((x["score"] for x in found.values()), default=0)
    if best < 0.8 and g("lang") == "deu":  # deutscher Name, noch nicht übersetzt: einmal bei Scryfall nachschlagen
        heads = [re.sub(r"[^A-Za-zÀ-ÿ',\- ]+", " ", l).strip() for l in lines[:3]]
        heads = [h for h in heads if len(h) >= 4]
        try:
            translate_names(con, heads, limit=2)
            for h in heads:
                al = con.execute("SELECT name FROM name_alias WHERE alias = ? AND name <> ''", (h,)).fetchone()
                if al:
                    add(al[0], 0.97, "deutscher Name (Scryfall)")
        except Exception:
            pass
    best = max((x["score"] for x in found.values()), default=0)
    if best < 0.8:  # Set-Kürzel und Sammlernummer unten links (z. B. „263/281“ und „C21 • EN“)
        text = "\n".join(lines)
        num, code = SET_RE.search(text), SETCODE_RE.search(text.upper())
        if num and code:
            try:
                c = json.loads(fetch(f"https://api.scryfall.com/cards/{code.group(1).lower()}/{int(num.group(1))}"))
                if c.get("name"):
                    add(c["name"], 0.95, f"Set {code.group(1)} Nr. {int(num.group(1))}")
            except Exception:
                pass
    out = sorted(found.values(), key=lambda x: -x["score"])[:6]
    for x in out:
        r = con.execute("SELECT image, scryfall_uri, eur, type_line FROM cards WHERE name = ? LIMIT 1", (x["name"],)).fetchone()
        if r:
            x.update(image=r["image"], scryfall=r["scryfall_uri"], eur=float(r["eur"]) if r["eur"] not in (None, "") else None,
                     type=r["type_line"])
    return {"best": out[0] if out and out[0]["score"] >= 0.6 else None, "alts": out[1:] if out else [],
            "sure": bool(out and out[0]["score"] >= 0.85)}


# ---------------------------------------------------------------- Kartensammlung
def collection_table(con):
    con.execute("CREATE TABLE IF NOT EXISTS collection(owner INTEGER, name TEXT, qty INTEGER, updated_at TEXT, PRIMARY KEY(owner, name))")
    inv_tables(con)


NAME_COLS = ("name", "card name", "card", "cardname", "card_name", "kartenname")
QTY_COLS = ("quantity", "count", "qty", "amount", "anzahl", "menge", "have", "owned")
SETC_COLS = ("set code", "set_code", "setcode", "edition code", "edition_code", "set")
SETN_COLS = ("set name", "set_name", "edition name", "expansion", "edition")
NUM_COLS = ("collector number", "collector_number", "collector #", "card number", "card_number", "number", "cn", "nummer")
FOIL_COLS = ("foil", "finish", "printing", "is foil", "foil/non-foil")
COND_COLS = ("condition", "cond", "zustand")
LANG_COLS = ("language", "lang", "sprache")
SID_COLS = ("scryfall id", "scryfall_id", "scryfallid")


def parse_collection(text):
    """Text oder CSV (ManaBox, Moxfield, Deckbox, Archidekt, Dragon Shield …) -> [{name, qty, set, number, foil, cond, lang, sid, set_name}]."""
    import csv, io
    text = (text or "").lstrip("\ufeff")
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return []
    head = lines[0]
    if head.lower().startswith("sep="):
        lines = lines[1:]
        head = lines[0] if lines else ""
    delim = max([",", ";", "\t"], key=head.count)
    cols = [c.strip().strip('"').lower() for c in next(csv.reader([head], delimiter=delim))]
    col = lambda names: next((i for n in names for i, c in enumerate(cols) if c == n), None)
    ni = col(NAME_COLS)
    if ni is not None and head.count(delim):
        qi, sci, sni, nui, fi, ci, li, si = (col(x) for x in (QTY_COLS, SETC_COLS, SETN_COLS, NUM_COLS, FOIL_COLS, COND_COLS, LANG_COLS, SID_COLS))
        if sni == sci:
            sni = None
        out = []
        for row in csv.reader(io.StringIO("\n".join(lines[1:])), delimiter=delim):
            if len(row) <= ni or not row[ni].strip():
                continue
            v = lambda i: row[i].strip() if i is not None and len(row) > i else ""
            q = v(qi) or "1"
            sc, sn = v(sci), v(sni)
            if sc and not re.fullmatch(r"[A-Za-z0-9]{2,6}", sc):  # „Edition“ enthält bei manchen Programmen den Set-Namen
                sn, sc = sn or sc, ""
            elif not sc and re.fullmatch(r"[A-Za-z0-9]{2,6}", sn):  # Moxfield: „Edition“ = Set-Code
                sc = sn
            out.append({"name": row[ni].strip(), "qty": int(q) if q.isdigit() else 1, "set": sc.upper(), "set_name": sn,
                        "number": v(nui).lstrip("#"), "foil": norm_foil(v(fi)), "cond": norm_cond(v(ci)), "lang": norm_lang(v(li)), "sid": v(si)})
        return out
    out = []
    for l in lines:
        l = l.strip()
        if not l or l.startswith(("//", "#")):
            continue
        foil = 2 if re.search(r"\*E\*", l) else 1 if re.search(r"\*F\*|\(foil\)|\bfoil\s*$", l, re.I) else 0
        l = re.sub(r"\s*\*[FE]\*|\s*\(foil\)", "", l, flags=re.I)
        m = re.match(r"^(\d+)\s*x?\s+(.+)$", l)
        q, rest = (int(m.group(1)), m.group(2)) if m else (1, l)
        sm = re.search(r"\s*[\(\[]([A-Za-z0-9]{2,6})[\)\]]\s*([0-9A-Za-z★†\-]+)?.*$", rest)
        sc = num = ""
        if sm:
            sc, num = sm.group(1).upper(), sm.group(2) or ""
            rest = rest[:sm.start()]
        if rest.strip():
            out.append({"name": rest.strip(), "qty": q, "set": sc, "set_name": "", "number": num, "foil": foil, "cond": "", "lang": "", "sid": ""})
    return out


def collection_import(p, uid=0):
    g = lambda k: (p.get(k) or [""])[0]
    rows = parse_collection(g("text"))
    if not rows:
        return {"error": "Keine Karten erkannt. Erwartet wird eine Liste („4 Sol Ring“) oder eine CSV-Datei mit Spalten für Name und Anzahl."}
    if len(rows) > 60000:
        return {"error": "Zu viele Zeilen (höchstens 60.000)."}
    con = db()
    con.row_factory = sqlite3.Row
    collection_table(con)
    names = {}
    for (n,) in con.execute("SELECT name FROM cards"):
        names[n.lower()] = n
        if " // " in n:
            names.setdefault(n.split(" // ")[0].lower(), n)
    fixed, unknown, fuzzy = [], [], 0
    try:
        translate_names(con, [r["name"] for r in rows if r["name"].lower() not in names], limit=150)
    except Exception:
        pass
    good = []
    for r in rows:
        real = names.get(r["name"].lower())
        if not real and fuzzy < 300:
            fuzzy += 1
            hit, hint = lookup(con, r["name"])
            if hit:
                real = hit["name"]
                fixed.append(f"{r['name']} → {real}")
        if not real:
            unknown.append(r["name"])
            continue
        r["name"] = real
        good.append(r)
    # Druckangaben: Scryfall-ID oder Set-Name in Set-Code und Nummer übersetzen, fehlende Druckdaten nachladen
    err = None
    if any(r["set_name"] for r in good) and sets_load(con):
        sets = {n.lower(): c for c, n in con.execute("SELECT code, name FROM mtg_sets")}
        codes = set(sets.values())
        for r in good:
            if r["set_name"] and (not r["set"] or (codes and r["set"] not in codes)):
                r["set"] = sets.get(r["set_name"].lower(), "" if r["set"] not in codes else r["set"])
    sids = [r["sid"] for r in good if r["sid"] and not r["set"]]
    if sids:
        have = {sid for (sid,) in con.execute(f"SELECT sid FROM prints WHERE sid IN ({','.join('?' * len(sids[:900]))})", sids[:900])}
        _, err = prints_fetch(con, [{"id": x} for x in dict.fromkeys(sids) if x not in have][:3000])
        for r in good:
            if r["sid"] and not r["set"]:
                pr = con.execute("SELECT set_code, number FROM prints WHERE sid = ?", (r["sid"],)).fetchone()
                if pr:
                    r["set"], r["number"] = pr[0], pr[1]
    now = datetime.datetime.now().isoformat(sep=" ", timespec="minutes")
    if g("mode") == "replace":
        con.execute("DELETE FROM coll_items WHERE owner = ?", (uid,))
    total = {}
    for r in good:
        q = max(0, r["qty"])
        con.execute("INSERT INTO coll_items VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(owner, name, set_code, number, foil, cond, lang) "
                    "DO UPDATE SET qty = qty + excluded.qty, updated_at = excluded.updated_at",
                    (uid, r["name"], r["set"], r["number"], r["foil"], r["cond"], r["lang"], q, now))
        total[r["name"]] = total.get(r["name"], 0) + q
    coll_rebuild(con, uid)
    res = inv_resolve(con, uid) if any(r["set"] for r in good) and not err else {"resolved": 0, "left": 0}
    out = collection_summary(con, uid)
    with_print = sum(r["qty"] for r in good if r["set"])
    out.update(imported=sum(total.values()), imp_unique=len(total), fixed=fixed[:30], unknown=unknown[:50], unknown_count=len(unknown),
               with_print=with_print, without_print=sum(total.values()) - with_print, prints_left=res.get("left", 0),
               prints_error=err or res.get("error"))
    return out


def collection_summary(con, uid=0):
    collection_table(con)
    r = con.execute("SELECT count(*), coalesce(sum(c.qty),0), max(c.updated_at) FROM collection c WHERE c.owner = ?", (uid,)).fetchone()
    t = inv_totals(con, uid)
    return {"unique": r[0], "total": r[1], "value": t["value_print"], "value_cheap": t["value_cheap"], "known": t["known"],
            "unknown_print": t["unknown"], "foil": t["foil"], "pending": t["pending"], "updated": r[2]}


def owned_map(con, uid=0):
    collection_table(con)
    return {n: q for n, q in con.execute("SELECT name, qty FROM collection WHERE owner = ?", (uid,))}


def ownership(p, uid=0):
    """Besitzanteil eines Decks: welche Karten fehlen, welche stecken schon in anderen gespeicherten Decks."""
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    own = owned_map(con, uid)
    ent, _ = entries_from_list(con, g("list"), g("commander"))
    decks_table(con)
    elsewhere = {}
    for name, lst in con.execute("SELECT name, list FROM decks WHERE owner = ? AND name <> ?", (uid, g("deck_name"))):
        for n, q in list_counts(lst).items():
            elsewhere.setdefault(n, []).append(name)
    cards, need, have, missing_eur = {}, 0, 0, 0.0
    for r, q in ent:
        basic = r["type_line"].startswith("Basic")
        o = q if basic else min(q, own.get(r["name"], 0))
        other = [] if basic else elsewhere.get(r["name"], [])
        free = o if basic else max(0, own.get(r["name"], 0) - len(other))
        cards[r["name"]] = {"owned": own.get(r["name"], 0), "basic": basic, "other": other[:5], "free": free >= q or basic}
        need += q
        have += o
        if o < q and r["eur"] not in (None, ""):
            missing_eur += float(r["eur"]) * (q - o)
    missing = [n for n, c in cards.items() if not c["basic"] and c["owned"] == 0]
    shared = [n for n, c in cards.items() if not c["basic"] and c["owned"] and not c["free"]]
    return {"has_collection": bool(own), "cards": cards, "percent": round(100 * have / max(1, need)), "missing": missing,
            "missing_eur": round(missing_eur, 2), "shared": shared}


def collection_export(con, uid=0, fmt="prints"):
    """CSV der Sammlung: je Druck (Count, Name, Edition, Collector Number, Foil, Condition, Language), lesbar für Moxfield,
    ManaBox, Archidekt und die Manaschmiede) oder nur Name und Anzahl."""
    collection_table(con)
    qn = lambda n: '"' + n.replace(chr(34), chr(39)) + '"'
    if fmt == "names":
        rows = con.execute("SELECT name, qty FROM collection WHERE owner = ? ORDER BY name", (uid,)).fetchall()
        return "Count,Name\n" + "\n".join(f"{q},{qn(n)}" for n, q in rows) + "\n"
    rows = con.execute("SELECT name, set_code, number, foil, cond, lang, qty FROM coll_items WHERE owner = ? AND qty > 0 "
                       "ORDER BY name, set_code, number", (uid,)).fetchall()
    out = ["Count,Name,Edition,Collector Number,Foil,Condition,Language"]
    for n, sc, num, foil, cond, lang, q in rows:
        out.append(f"{q},{qn(n)},{sc.lower()},{num},{['', 'foil', 'etched'][foil if foil in (0, 1, 2) else 1]},{COND_NAMES.get(cond, '')},{lang.lower()}")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- Sammlung je Druck (Set, Nummer, Foil, Zustand, Sprache)
SCRYFALL_API = (ENV("CDB_SCRYFALL_API") or "https://api.scryfall.com").rstrip("/")
CONDS = ["MT", "NM", "EX", "GD", "LP", "PL", "PO"]
COND_NAMES = {"MT": "Mint", "NM": "Near Mint", "EX": "Excellent", "GD": "Good", "LP": "Light Played", "PL": "Played", "PO": "Poor"}
COND_DE = {"MT": "Mint", "NM": "Near Mint", "EX": "Excellent", "GD": "Good", "LP": "Light Played", "PL": "Played", "PO": "Poor"}
LANGS = {"EN": "Englisch", "DE": "Deutsch", "FR": "Französisch", "IT": "Italienisch", "ES": "Spanisch", "PT": "Portugiesisch",
         "JA": "Japanisch", "KO": "Koreanisch", "RU": "Russisch", "ZHS": "Chinesisch (vereinfacht)", "ZHT": "Chinesisch (traditionell)"}
_COND_ALIAS = {"mint": "MT", "mt": "MT", "m": "MT", "near mint": "NM", "nm": "NM", "nm mt": "NM", "nearmint": "NM",
               "excellent": "EX", "ex": "EX", "slightly played": "EX", "sp": "EX", "good": "GD", "gd": "GD", "moderately played": "GD",
               "mp": "GD", "light played": "LP", "lightly played": "LP", "lp": "LP", "played": "PL", "pl": "PL", "heavily played": "PL",
               "hp": "PL", "poor": "PO", "po": "PO", "damaged": "PO", "dmg": "PO"}
_LANG_ALIAS = {"en": "EN", "english": "EN", "englisch": "EN", "de": "DE", "german": "DE", "deutsch": "DE", "ger": "DE",
               "fr": "FR", "french": "FR", "französisch": "FR", "it": "IT", "italian": "IT", "italienisch": "IT",
               "es": "ES", "spanish": "ES", "spanisch": "ES", "sp": "ES", "pt": "PT", "portuguese": "PT", "portugiesisch": "PT",
               "ja": "JA", "jp": "JA", "japanese": "JA", "japanisch": "JA", "ko": "KO", "kr": "KO", "korean": "KO", "koreanisch": "KO",
               "ru": "RU", "russian": "RU", "russisch": "RU", "zhs": "ZHS", "cs": "ZHS", "zh cn": "ZHS", "chinese simplified": "ZHS",
               "simplified chinese": "ZHS", "zht": "ZHT", "ct": "ZHT", "zh tw": "ZHT", "chinese traditional": "ZHT", "traditional chinese": "ZHT"}
_INV_READY = set()


def norm_cond(v):
    v = re.sub(r"[_\-/]+", " ", (v or "").strip().lower())
    return _COND_ALIAS.get(v, "")


def norm_lang(v):
    v = re.sub(r"[_\-]+", " ", (v or "").strip().lower())
    return _LANG_ALIAS.get(v, "")


def norm_foil(v):
    v = (v or "").strip().lower()
    if v in ("etched", "foil etched", "etched foil"):
        return 2
    return 1 if v in ("foil", "true", "yes", "ja", "1", "y", "x", "f", "*f*", "premium foil", "galaxy foil", "surge foil") or "foil" in v and "non" not in v else 0


def inv_tables(con):
    con.execute("CREATE TABLE IF NOT EXISTS coll_items(owner INTEGER, name TEXT, set_code TEXT DEFAULT '', number TEXT DEFAULT '', "
                "foil INTEGER DEFAULT 0, cond TEXT DEFAULT '', lang TEXT DEFAULT '', qty INTEGER, updated_at TEXT, "
                "PRIMARY KEY(owner, name, set_code, number, foil, cond, lang))")
    con.execute("CREATE TABLE IF NOT EXISTS prints(set_code TEXT, number TEXT, name TEXT, set_name TEXT, released TEXT, cm_id INTEGER, "
                "eur REAL, eur_foil REAL, image TEXT, finishes TEXT, sid TEXT, rarity TEXT, at TEXT, PRIMARY KEY(set_code, number))")
    con.execute("CREATE INDEX IF NOT EXISTS prints_name ON prints(name)")
    con.execute("CREATE INDEX IF NOT EXISTS prints_sid ON prints(sid)")
    con.execute("CREATE TABLE IF NOT EXISTS mtg_sets(code TEXT PRIMARY KEY, name TEXT, released TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS prints_done(name TEXT PRIMARY KEY, at TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS cm_prices(id INTEGER PRIMARY KEY, trend REAL, low REAL, avg7 REAL, avg30 REAL, "
                "ftrend REAL, flow REAL)")
    key = DB
    if key not in _INV_READY:
        # Umzug: bisherige Sammlung (nur Name + Anzahl) wird zu Einträgen ohne bekannten Druck
        con.execute("INSERT OR IGNORE INTO coll_items SELECT c.owner, c.name, '', '', 0, '', '', c.qty, c.updated_at FROM collection c "
                    "WHERE c.qty > 0 AND NOT EXISTS (SELECT 1 FROM coll_items i WHERE i.owner = c.owner AND i.name = c.name)")
        con.commit()
        _INV_READY.add(key)


def coll_rebuild(con, uid):
    """Die Sammlung je Kartenname (für Deckbau, Einkaufsliste, Ordner …) aus den Einträgen je Druck zusammenzählen."""
    con.execute("DELETE FROM collection WHERE owner = ?", (uid,))
    con.execute("INSERT INTO collection SELECT owner, name, sum(qty), max(updated_at) FROM coll_items WHERE owner = ? AND qty > 0 "
                "GROUP BY owner, name", (uid,))
    con.commit()


def scry_get(path):
    time.sleep(0.08)  # Scryfall bittet um 50–100 ms Abstand
    return json.loads(fetch(SCRYFALL_API + path))


def scry_post(path, body):
    time.sleep(0.08)
    req = urllib.request.Request(SCRYFALL_API + path, data=json.dumps(body).encode(), method="POST",
                                 headers=dict(HEADERS, **{"Content-Type": "application/json"}))
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def print_row(c):
    f0 = (c.get("card_faces") or [{}])[0]
    img = (c.get("image_uris") or f0.get("image_uris") or {}).get("normal")
    pr = c.get("prices") or {}
    num = lambda v: float(v) if v not in (None, "") else None
    return (c.get("set", "").upper(), str(c.get("collector_number", "")), c.get("name"), c.get("set_name"), c.get("released_at"),
            c.get("cardmarket_id"), num(pr.get("eur")), num(pr.get("eur_foil")) or num(pr.get("eur_etched")), img,
            ",".join(c.get("finishes") or []), c.get("id"), c.get("rarity"),
            datetime.datetime.now().isoformat(sep=" ", timespec="minutes"))


def prints_store(con, cards):
    rows = [print_row(c) for c in cards if c.get("set") and c.get("collector_number") and c.get("layout") not in SKIP_LAYOUTS]
    con.executemany("INSERT OR REPLACE INTO prints VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    con.commit()
    return rows


def sets_load(con):
    inv_tables(con)
    if con.execute("SELECT count(*) FROM mtg_sets").fetchone()[0] and (setting("sets_at") or "") >= str(datetime.date.today() - datetime.timedelta(days=14)):
        return True
    try:
        data = scry_get("/sets").get("data") or []
    except Exception:
        return False
    con.executemany("INSERT OR REPLACE INTO mtg_sets VALUES(?,?,?)", [(s["code"].upper(), s.get("name"), s.get("released_at")) for s in data if s.get("code")])
    con.commit()
    setting("sets_at", str(datetime.date.today()))
    return True


def prints_fetch(con, idents):
    """Druckdaten über Scryfall /cards/collection (75 je Abfrage). Gibt (gefundene Karten, Fehlertext) zurück."""
    found, err = [], None
    for i in range(0, len(idents), 75):
        try:
            r = scry_post("/cards/collection", {"identifiers": idents[i:i + 75]})
        except Exception as e:
            err = f"Scryfall nicht erreichbar ({e.__class__.__name__}). Druckdaten werden später nachgeladen."
            break
        found += prints_store(con, r.get("data") or []) and (r.get("data") or [])
    return found, err


def prints_of(con, name, force=False):
    """Alle Drucke einer Karte (zwischengespeichert, höchstens wöchentlich neu von Scryfall)."""
    inv_tables(con)
    done = con.execute("SELECT at FROM prints_done WHERE name = ?", (name,)).fetchone()
    err = None
    if force or not done or done[0] < str(datetime.date.today() - datetime.timedelta(days=7)):
        url = "/cards/search?" + urllib.parse.urlencode({"q": f'!"{name}" game:paper', "unique": "prints", "order": "released", "dir": "desc"})
        try:
            for _ in range(4):
                r = scry_get(url)
                prints_store(con, r.get("data") or [])
                if not r.get("has_more") or not r.get("next_page"):
                    break
                url = r["next_page"].replace(SCRYFALL_API, "").replace("https://api.scryfall.com", "")
            con.execute("INSERT OR REPLACE INTO prints_done VALUES(?,?)", (name, str(datetime.date.today())))
            con.commit()
        except Exception as e:
            err = f"Scryfall nicht erreichbar ({e.__class__.__name__})."
    rows = con.execute("SELECT * FROM prints WHERE name = ? ORDER BY released DESC, set_code, number", (name,)).fetchall()
    out = []
    for r in rows:
        pn, srcn = print_price(con, r, 0)
        pf, srcf = print_price(con, r, 1)
        fin = (r["finishes"] or "nonfoil").split(",")
        out.append({"set_code": r["set_code"], "set_name": r["set_name"], "number": r["number"], "released": r["released"],
                    "image": r["image"], "finishes": fin, "rarity": r["rarity"], "eur": pn if "nonfoil" in fin else None,
                    "eur_foil": pf if ("foil" in fin or "etched" in fin) else None, "src": srcn or srcf,
                    "cm": CM_LINK.format(r["cm_id"]) if r["cm_id"] else None})
    return {"name": name, "prints": out, "error": err if not out else None, "warn": err if out else None}


def print_price(con, pr, foil):
    """Preis eines Drucks: Cardmarket-Preisliste über die Produktnummer, sonst Scryfall-Preis des Drucks."""
    if pr is None:
        return None, None
    if pr["cm_id"]:
        cp = con.execute("SELECT trend, ftrend FROM cm_prices WHERE id = ?", (pr["cm_id"],)).fetchone()
        if cp and (cp[1] if foil else cp[0]):
            return round(cp[1] if foil else cp[0], 2), "cm"
    v = pr["eur_foil"] if foil else pr["eur"]
    return (round(v, 2), "scryfall") if v else (None, None)


def inv_item(con, it, cheap):
    pr = con.execute("SELECT * FROM prints WHERE set_code = ? AND number = ?", (it["set_code"], it["number"])).fetchone() if it["set_code"] else None
    price, src = print_price(con, pr, it["foil"])
    if price is None:
        price, src = cheap.get(it["name"]), "cheapest" if cheap.get(it["name"]) is not None else None
    img = pr["image"] if pr is not None and pr["image"] else None
    return dict(it, set_name=pr["set_name"] if pr is not None else None, known=pr is not None, price=price, src=src,
                value=round(price * it["qty"], 2) if price is not None else None, image=img,
                finishes=(pr["finishes"] or "nonfoil").split(",") if pr is not None else None,
                cm=CM_LINK.format(pr["cm_id"]) if pr is not None and pr["cm_id"] else cm_link(it["name"]))


def inv_list(con, uid, q="", sort="name", page=0, only="", per=100):
    inv_tables(con)
    where, args = ["owner = ?", "qty > 0"], [uid]
    for w in (q or "").split():
        where.append("(name LIKE ? OR set_code LIKE ?)")
        args += [f"%{w}%", w.upper()]
    rows = [dict(zip(("name", "set_code", "number", "foil", "cond", "lang", "qty", "updated_at"), r)) for r in
            con.execute(f"SELECT name, set_code, number, foil, cond, lang, qty, updated_at FROM coll_items WHERE {' AND '.join(where)}", args)]
    cheap = eur_map(con, {r["name"] for r in rows})
    items = [inv_item(con, r, cheap) for r in rows]
    if only == "unknown":
        items = [x for x in items if not x["known"]]
    elif only == "foil":
        items = [x for x in items if x["foil"]]
    keyf = {"value": lambda x: (-(x["value"] or 0), x["name"]), "price": lambda x: (-(x["price"] or 0), x["name"]),
            "set": lambda x: (x["set_code"] or "~", x["number"].zfill(5), x["name"]), "new": lambda x: (x["updated_at"] or "", x["name"])}
    items.sort(key=keyf.get(sort, lambda x: (x["name"], x["set_code"], x["number"], x["foil"])))
    if sort == "new":
        items.reverse()
    tot = inv_totals(con, uid)
    return dict(tot, items=items[page * per:(page + 1) * per], count=len(items), page=page, per=per,
                conds=[[c, COND_NAMES[c]] for c in CONDS], langs=list(LANGS.items()), cm_at=setting("cm_at"))


def inv_totals(con, uid):
    inv_tables(con)
    rows = [dict(zip(("name", "set_code", "number", "foil", "cond", "lang", "qty", "updated_at"), r)) for r in
            con.execute("SELECT name, set_code, number, foil, cond, lang, qty, updated_at FROM coll_items WHERE owner = ? AND qty > 0", (uid,))]
    cheap = eur_map(con, {r["name"] for r in rows})
    vp = vc = 0.0
    known = unknown = foil = 0
    for r in rows:
        x = inv_item(con, r, cheap)
        vp += x["value"] or 0
        vc += (cheap.get(r["name"]) or 0) * r["qty"]
        if x["known"]:
            known += r["qty"]
        else:
            unknown += r["qty"]
        foil += r["qty"] if r["foil"] else 0
    pending = con.execute("SELECT count(*) FROM coll_items i WHERE owner = ? AND qty > 0 AND set_code <> '' AND NOT EXISTS "
                          "(SELECT 1 FROM prints p WHERE p.set_code = i.set_code AND p.number = i.number)", (uid,)).fetchone()[0]
    return {"value_print": round(vp, 2), "value_cheap": round(vc, 2), "known": known, "unknown": unknown, "foil": foil, "pending": pending,
            "entries": len(rows)}


def inv_resolve(con, uid, limit=1500):
    """Einträge mit Set (und Nummer), deren Druckdaten noch fehlen, bei Scryfall nachschlagen."""
    inv_tables(con)
    todo = con.execute("SELECT DISTINCT name, set_code, number FROM coll_items i WHERE owner = ? AND qty > 0 AND set_code <> '' AND NOT EXISTS "
                       "(SELECT 1 FROM prints p WHERE p.set_code = i.set_code AND p.number = i.number) LIMIT ?", (uid, limit)).fetchall()
    if not todo:
        return {"resolved": 0, "left": 0}
    idents = [{"set": s.lower(), "collector_number": n} if n else {"name": nm.split(" // ")[0], "set": s.lower()} for nm, s, n in todo]
    found, err = prints_fetch(con, idents)
    # nur Set bekannt: Nummer aus dem gefundenen Druck übernehmen
    now = datetime.datetime.now().isoformat(sep=" ", timespec="minutes")
    for nm, s, n in todo:
        if n:
            continue
        pr = con.execute("SELECT number FROM prints WHERE name = ? AND set_code = ? ORDER BY number LIMIT 1", (nm, s)).fetchone()
        if pr:
            inv_move(con, uid, {"name": nm, "set_code": s, "number": ""}, {"number": pr[0]}, now, all_variants=True)
    coll_rebuild(con, uid)
    left = inv_totals(con, uid)["pending"]
    return {"resolved": len(found), "left": left, "error": err}


def inv_move(con, uid, old, new, now=None, qty=None, all_variants=False):
    """Eintrag ändern (Druck, Foil, Zustand, Sprache, Anzahl); gleiche Einträge werden zusammengelegt."""
    now = now or datetime.datetime.now().isoformat(sep=" ", timespec="minutes")
    keys = ("name", "set_code", "number", "foil", "cond", "lang")
    if all_variants:
        rows = con.execute("SELECT name, set_code, number, foil, cond, lang, qty FROM coll_items WHERE owner = ? AND name = ? AND set_code = ? AND number = ?",
                           (uid, old["name"], old["set_code"], old["number"])).fetchall()
    else:
        rows = con.execute("SELECT name, set_code, number, foil, cond, lang, qty FROM coll_items WHERE owner = ? AND name = ? AND set_code = ? AND number = ? "
                           "AND foil = ? AND cond = ? AND lang = ?", (uid, *[old.get(k) for k in keys])).fetchall()
    for r in rows:
        cur = dict(zip(keys + ("qty",), r))
        tgt = {k: new.get(k, cur[k]) for k in keys}
        q = cur["qty"] if qty is None else max(0, int(qty))
        con.execute("DELETE FROM coll_items WHERE owner = ? AND name = ? AND set_code = ? AND number = ? AND foil = ? AND cond = ? AND lang = ?",
                    (uid, *[cur[k] for k in keys]))
        if q > 0:
            con.execute("INSERT INTO coll_items VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(owner, name, set_code, number, foil, cond, lang) "
                        "DO UPDATE SET qty = qty + excluded.qty, updated_at = excluded.updated_at", (uid, *[tgt[k] for k in keys], q, now))
    return len(rows)


def inv_add(con, uid, it):
    inv_tables(con)
    now = datetime.datetime.now().isoformat(sep=" ", timespec="minutes")
    q = max(0, int(it.get("qty") or 1))
    con.execute("INSERT INTO coll_items VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(owner, name, set_code, number, foil, cond, lang) "
                "DO UPDATE SET qty = qty + excluded.qty, updated_at = excluded.updated_at",
                (uid, it["name"], (it.get("set_code") or "").upper(), it.get("number") or "", int(it.get("foil") or 0),
                 it.get("cond") or "", it.get("lang") or "", q, now))
    coll_rebuild(con, uid)


# ---------------------------------------------------------------- Einkaufsliste, Wunschliste, Ordner, Preisalarm, Budget-Tausch
def usd_map(con, names=None):
    con.execute("CREATE TABLE IF NOT EXISTS card_usd(name TEXT PRIMARY KEY, usd REAL)")
    if names is None:
        return {n: u for n, u in con.execute("SELECT name, usd FROM card_usd")}
    names = list(names)
    out = {}
    for i in range(0, len(names), 900):
        part = names[i:i + 900]
        out.update({n: u for n, u in con.execute(f"SELECT name, usd FROM card_usd WHERE name IN ({','.join('?' * len(part))})", part)})
    return out


def eur_map(con, names):
    names, out = list(names), {}
    for i in range(0, len(names), 900):
        part = names[i:i + 900]
        out.update({n: e for n, e in con.execute(f"SELECT name, min(CAST(eur AS REAL)) FROM cards WHERE name IN ({','.join('?' * len(part))}) "
                                                 "AND eur IS NOT NULL AND eur <> '' GROUP BY name", part)})
    return out


def wish_table(con):
    con.execute("CREATE TABLE IF NOT EXISTS wishlist(owner INTEGER, name TEXT, qty INTEGER, target REAL, added TEXT, PRIMARY KEY(owner, name))")


def folder_table(con):
    con.execute("CREATE TABLE IF NOT EXISTS coll_folders(owner INTEGER, folder TEXT, name TEXT, qty INTEGER, PRIMARY KEY(owner, folder, name))")


def is_basic(con, name):
    r = con.execute("SELECT type_line FROM cards WHERE name = ? LIMIT 1", (name,)).fetchone()
    return bool(r and (r[0] or "").startswith("Basic"))


def shopping_list(con, uid=0, share=True):
    """Fehlende Karten über alle gespeicherten Decks. share: eine Karte kann zwischen Decks wandern (Bedarf = größte Menge
    in einem Deck), sonst braucht jedes Deck eigene Exemplare (Bedarf = Summe)."""
    decks_table(con)
    need, where = {}, {}
    for name, cmd, lst in con.execute("SELECT name, commander, list FROM decks WHERE owner = ?", (uid,)):
        cnt = dict(list_counts(lst))
        for c in [x.strip() for x in (cmd or "").split(" + ") if x.strip()]:
            cnt.setdefault(c, 1)
        for n, q in cnt.items():
            need[n] = max(need.get(n, 0), q) if share else need.get(n, 0) + q
            where.setdefault(n, []).append(name)
    basics = {n for n in need if is_basic(con, n)}
    own, wish = owned_map(con, uid), set()
    wish_table(con)
    wish = {n for n, in con.execute("SELECT name FROM wishlist WHERE owner = ?", (uid,))}
    prices, usd = eur_map(con, need), usd_map(con, need)
    items = []
    for n, q in need.items():
        if n in basics:
            continue
        miss = q - own.get(n, 0)
        if miss > 0:
            e = prices.get(n)
            items.append({"name": n, "need": q, "have": own.get(n, 0), "missing": miss, "eur": e, "usd": usd.get(n), "cm": cm_link(n),
                          "total": round(e * miss, 2) if e is not None else None, "decks": sorted(where[n]), "wish": n in wish})
    items.sort(key=lambda x: (-(x["total"] or 0), x["name"]))
    total = round(sum(x["total"] or 0 for x in items), 2)
    return {"items": items, "total": total, "cards": sum(x["missing"] for x in items), "decks": len({d for x in where.values() for d in x}),
            "has_collection": bool(own), "noprice": sum(1 for x in items if x["eur"] is None), "share": share,
            "text": "\n".join(f"{x['missing']} {x['name']}" for x in items)}


def wish_list(con, uid=0):
    wish_table(con)
    rows = con.execute("SELECT name, qty, target, added FROM wishlist WHERE owner = ? ORDER BY name COLLATE NOCASE", (uid,)).fetchall()
    prices, usd, own = eur_map(con, [r[0] for r in rows]), usd_map(con, [r[0] for r in rows]), owned_map(con, uid)
    items = [{"name": n, "qty": q, "target": t, "added": a, "eur": prices.get(n), "usd": usd.get(n), "have": own.get(n, 0), "cm": cm_link(n),
              "hit": t is not None and prices.get(n) is not None and prices[n] <= t} for n, q, t, a in rows]
    return {"items": items, "total": round(sum((x["eur"] or 0) * x["qty"] for x in items), 2), "hits": sum(1 for x in items if x["hit"])}


def wish_add(con, uid, text, target=None):
    """„2 Sol Ring“ je Zeile; bekannte Karten werden auf die Wunschliste gesetzt (Menge wird erhöht, Zielpreis bleibt)."""
    wish_table(con)
    con.row_factory = sqlite3.Row
    added, unknown = [], []
    for ln in (text or "").splitlines()[:500]:
        m = re.match(r"^\s*(?:(\d+)\s*x?\s+)?(.+?)\s*$", ln)
        if not m or not m.group(2).strip():
            continue
        r = lookup(con, m.group(2))[0]
        if not r:
            unknown.append(m.group(2))
            continue
        q = max(1, min(99, int(m.group(1) or 1)))
        con.execute("INSERT INTO wishlist VALUES(?,?,?,?,?) ON CONFLICT(owner, name) DO UPDATE SET qty = max(qty, excluded.qty), "
                    "target = coalesce(excluded.target, target)",
                    (uid, r["name"], q, target, datetime.date.today().isoformat()))
        added.append(r["name"])
    con.row_factory = None
    con.commit()
    out = wish_list(con, uid)
    out.update(added=len(added), unknown=unknown[:20])
    return out


def wish_set(con, uid, name, qty=None, target=None, remove=False):
    wish_table(con)
    if remove:
        con.execute("DELETE FROM wishlist WHERE owner = ? AND name = ?", (uid, name))
    else:
        if qty is not None:
            con.execute("UPDATE wishlist SET qty = ? WHERE owner = ? AND name = ?", (max(1, min(99, qty)), uid, name))
        if target is not None:
            con.execute("UPDATE wishlist SET target = ? WHERE owner = ? AND name = ?", (target if target > 0 else None, uid, name))
    con.commit()
    return wish_list(con, uid)


def folder_overview(con, uid=0):
    folder_table(con)
    rows = con.execute("SELECT f.folder, count(*), sum(f.qty), sum(f.qty * coalesce((SELECT min(CAST(eur AS REAL)) FROM cards k "
                       "WHERE k.name = f.name AND eur IS NOT NULL AND eur <> ''), 0)) FROM coll_folders f WHERE owner = ? "
                       "GROUP BY folder ORDER BY folder COLLATE NOCASE", (uid,)).fetchall()
    return {"folders": [{"name": f, "unique": u, "cards": c, "value": round(v or 0, 2)} for f, u, c, v in rows]}


def folder_get(con, uid, folder):
    folder_table(con)
    rows = con.execute("SELECT name, qty FROM coll_folders WHERE owner = ? AND folder = ? ORDER BY name COLLATE NOCASE", (uid, folder)).fetchall()
    prices, own = eur_map(con, [r[0] for r in rows]), owned_map(con, uid)
    items = [{"name": n, "qty": q, "eur": prices.get(n), "have": own.get(n, 0)} for n, q in rows]
    return {"folder": folder, "items": items, "value": round(sum((x["eur"] or 0) * x["qty"] for x in items), 2),
            "text": "\n".join(f"{x['qty']} {x['name']}" for x in items)}


def folder_put(con, uid, folder, text, mode="add"):
    """Karten aus der Sammlung in einen Ordner legen (mode add) oder herausnehmen (mode remove). Mehr Exemplare,
    als die Sammlung enthält, werden auf den Bestand begrenzt."""
    folder = re.sub(r"\s+", " ", folder or "").strip()[:40]
    if not folder:
        return {"error": "Bitte einen Ordnernamen angeben."}
    folder_table(con)
    if mode == "add" and not con.execute("SELECT 1 FROM coll_folders WHERE owner = ? AND folder = ?", (uid, folder)).fetchone() \
            and con.execute("SELECT count(DISTINCT folder) FROM coll_folders WHERE owner = ?", (uid,)).fetchone()[0] >= 50:
        return {"error": "Höchstens 50 Ordner."}
    own = owned_map(con, uid)
    con.row_factory = sqlite3.Row
    done, capped, unknown, notown = 0, [], [], []
    for ln in (text or "").splitlines()[:2000]:
        m = re.match(r"^\s*(?:(\d+)\s*x?\s+)?(.+?)\s*$", ln)
        if not m or not m.group(2).strip():
            continue
        r = lookup(con, m.group(2))[0]
        if not r:
            unknown.append(m.group(2))
            continue
        n, q = r["name"], max(1, int(m.group(1) or 1))
        cur = (con.execute("SELECT qty FROM coll_folders WHERE owner = ? AND folder = ? AND name = ?", (uid, folder, n)).fetchone() or [0])[0]
        if mode == "remove":
            new = max(0, cur - q)
        else:
            if not own.get(n):
                notown.append(n)
                continue
            new = cur + q
            if new > own[n]:
                capped.append(n)
                new = own[n]
        if new:
            con.execute("INSERT INTO coll_folders VALUES(?,?,?,?) ON CONFLICT(owner, folder, name) DO UPDATE SET qty = excluded.qty",
                        (uid, folder, n, new))
        else:
            con.execute("DELETE FROM coll_folders WHERE owner = ? AND folder = ? AND name = ?", (uid, folder, n))
        done += 1
    con.row_factory = None
    con.commit()
    out = folder_get(con, uid, folder)
    out.update(changed=done, capped=capped[:20], unknown=unknown[:20], notown=notown[:20])
    return out


def collection_history(con, uid=0):
    """Wert der Sammlung je gesichertem Stichtag (letzter bekannter Preis jeder Karte bis zu diesem Tag)."""
    collection_table(con); price_table(con)
    own = owned_map(con, uid)
    if not own:
        return {"days": [], "series": [], "hint": "Noch keine Sammlung importiert."}
    hist = {}
    names = list(own)
    for i in range(0, len(names), 900):
        part = names[i:i + 900]
        for n, d, e in con.execute(f"SELECT name, day, eur FROM price_hist WHERE name IN ({','.join('?' * len(part))}) ORDER BY day", part):
            hist.setdefault(n, []).append((d, e))
    days = sorted({d for h in hist.values() for d, _ in h})
    series = []
    for d in days[-120:]:
        v = 0.0
        for n, h in hist.items():
            last = None
            for dd, e in h:
                if dd > d:
                    break
                last = e
            v += (last or 0) * own[n]
        series.append({"day": d, "value": round(v, 2)})
    usd = usd_map(con, names)
    return {"days": [x["day"] for x in series], "series": series, "usd": round(sum((usd.get(n) or 0) * q for n, q in own.items()), 2) if usd else None,
            "hint": "Wert je gesichertem Stichtag (bei jeder Kartenaktualisierung)." if len(series) > 1 else
                    "Der Verlauf entsteht mit den nächsten Kartenaktualisierungen (je Aktualisierung ein Stichtag)."}


def price_alerts(con, uid=0, days=7, pct=20, min_eur=1.0):
    """Wunschliste unter Zielpreis und starke Preisbewegungen in der Sammlung (Vergleich mit dem Stand vor etwa 7 Tagen)."""
    wl = wish_list(con, uid)
    hits = [x for x in wl["items"] if x["hit"]]
    own = owned_map(con, uid)
    price_table(con)
    cut = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    moves = []
    names = list(own)
    cur = eur_map(con, names)
    for i in range(0, len(names), 900):
        part = names[i:i + 900]
        for n, e in con.execute(f"SELECT h.name, h.eur FROM price_hist h JOIN (SELECT name, max(day) d FROM price_hist WHERE day <= ? "
                                f"AND name IN ({','.join('?' * len(part))}) GROUP BY name) m ON m.name = h.name AND m.d = h.day",
                                [cut] + part):
            now = cur.get(n)
            if now is None or not e:
                continue
            diff = now - e
            if abs(diff) >= min_eur and abs(diff) / e * 100 >= pct:
                moves.append({"name": n, "from": e, "to": now, "diff": round(diff, 2), "pct": round(diff / e * 100), "qty": own[n]})
    seen = {m["name"] for m in moves}
    try:
        cm_table(con)
        cmv = {n: (a30, t) for n, a30, t in con.execute("SELECT name, avg30, trend FROM cm_cards")}
    except sqlite3.Error:
        cmv = {}
    for n in names:  # Cardmarket: Trend gegenüber dem 30-Tage-Durchschnitt
        if n in seen or n not in cmv:
            continue
        a30, t = cmv[n]
        if not a30 or not t:
            continue
        diff = t - a30
        if abs(diff) >= min_eur and abs(diff) / a30 * 100 >= pct:
            moves.append({"name": n, "from": round(a30, 2), "to": round(t, 2), "diff": round(diff, 2), "pct": round(diff / a30 * 100),
                          "qty": own[n], "src": "cm"})
    moves.sort(key=lambda x: -abs(x["diff"] * x["qty"]))
    return {"wish_hits": hits, "moves": moves[:15], "since": cut, "cm_at": setting("cm_at") or ""}


def budget_swaps(p, uid=0):
    """Günstigere Karten mit gleicher Aufgabe für teure Karten eines Decks."""
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    ent, _ = entries_from_list(con, g("list"), g("commander"))
    if not ent:
        return {"error": "Leere Deckliste."}
    cn = {r["name"] for r in resolve_cmds(con, g("commander"))}
    try:
        lim = float((g("min") or "5").replace(",", "."))
    except ValueError:
        lim = 5.0
    own = owned_map(con, uid)
    exp = sorted([(r, q) for r, q in ent if r["name"] not in cn and r["eur"] not in (None, "") and float(r["eur"]) >= lim
                  and not front_type(r).startswith("Basic") and r["name"] not in own], key=lambda x: -float(x[0]["eur"]))[:20]
    deck_names = "\n".join(r["name"] for r, _ in ent)
    out, save = [], 0.0
    for r, q in exp:
        e = float(r["eur"])
        alt = alternatives({"name": [r["name"]], "ci": [g("ci")], "deck": [deck_names], "maxeur": [str(round(e * 0.3, 2))], "limit": ["3"]})
        cards = alt.get("cards") or []
        if cards:
            best = min(c["eur"] or 0 for c in cards)
            save += (e - best) * q
        out.append({"name": r["name"], "eur": e, "qty": q, "reason": alt.get("reason", ""), "alts": cards})
    return {"items": out, "saving": round(save, 2), "min": lim,
            "hint": f"Karten ab {lim:.2f} € (ohne Commander und ohne Karten aus deiner Sammlung); Ersatz kostet höchstens 30 % des Preises.".replace(".", ",", 1)}


# ---------------------------------------------------------------- Empfehlungen und Frust-Index
FRUST = [  # (Bezeichnung, Regex auf den Kartentext, Gewicht)
    ("Massen-Landzerstörung", r"destroy all lands|each player sacrifices (?:all|\w+) lands|destroy all nonbasic lands", 3),
    ("Extra-Züge", r"take an extra turn|takes an extra turn", 2),
    ("Stax / Sperren", r"don't untap|can't cast more than|players can't|each player can't|can't untap|spells cost \{\d\} more|"
                       r"opponents can't|skip (?:their|your) (?:untap|draw)", 2),
    ("Gegenzauber", r"counter target (?:spell|noncreature spell|creature spell)", 0.5),
    ("Diebstahl / Kontrolle", r"gain control of target|you control target player", 1),
    ("Tutoren", r"search your library for (?:a|an|up to \w+) card(?!s? with)", 0.5),
]


def frust_index(ent):
    hits, score = {}, 0.0
    for r, q in ent:
        txt = (r["oracle_text"] or "")
        for label, rx, wt in FRUST:
            if re.search(rx, txt, re.I):
                hits.setdefault(label, []).append(r["name"])
                score += wt
        if r["game_changer"]:
            hits.setdefault("Game Changer", []).append(r["name"])
            score += 1
    level = 0 if score < 2 else 1 if score < 6 else 2 if score < 12 else 3
    return {"score": round(score, 1), "level": ["entspannt", "normal", "spürbar", "hoch"][level],
            "hits": [{"label": k, "cards": v} for k, v in sorted(hits.items(), key=lambda x: -len(x[1]))],
            "hint": "Eigene Schätzung aus dem Kartentext (keine EDHREC-Salt-Werte): wie sehr das Deck Mitspieler frustrieren kann."}


ROLE_TARGETS = {  # Funktion: (Bezeichnung, Richtwert, Suchmuster im Kartentext)
    "ramp": ("Ramp (Mana beschleunigen)", 10, ("add {", "add one mana", "add two mana", "basic land card")),
    "draw": ("Kartenziehen", 10, ("draw a card", "draw two", "draw three")),
    "removal": ("Gezieltes Removal", 8, ("destroy target", "exile target")),
    "wipe": ("Board-Wipes", 3, ("destroy all", "exile all")),
}


WIPE_RE = re.compile(r"(destroy|exile) all (other )?(creatures|nonland permanents|nonland|permanents|artifacts|enchantments|"
                     r"artifacts and enchantments|creatures and planeswalkers)|deals? \w+ damage to each (other )?creature|"
                     r"all creatures get -\w+/-\w+|each player sacrifices (all|\w+) (creatures|nonland)")


def role_ok(r, role):
    """Strengere Prüfung für Vorschläge: Rituale sind kein Ramp, „exile all spells“ ist kein Board-Wipe."""
    t, ty = (r["oracle_text"] or "").lower(), front_type(r)
    if role == "ramp":
        if "Instant" in ty:
            return False
        if "Sorcery" in ty:
            return "land card" in t
        return "Land" not in ty
    if role == "wipe":
        return bool(WIPE_RE.search(t))
    if role == "removal":
        return bool(re.search(r"(destroy|exile) target (creature|nonland permanent|permanent|artifact|enchantment|planeswalker|"
                              r"artifact or enchantment|creature or planeswalker)", t)) or "damage to any target" in t
    return True


def recommend(p, uid=0):
    """Ergänzungen und Streichkandidaten aus Precons, eigenen Decks, Spielprotokoll und dem Text des Commanders."""
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    ent, _ = entries_from_list(con, g("list"), g("commander"))
    if not ent:
        return {"error": "Leere Deckliste."}
    cmds = resolve_cmds(con, g("commander"))
    cn = {r["name"] for r in cmds}
    ci = "".join(x for x in ORDER if any(x in r["color_identity"] for r in cmds)) if cmds else \
        "".join(x for x in ORDER if any(x in r["color_identity"] for r, _ in ent))
    have = {r["name"] for r, _ in ent}
    core = {r["name"] for r, _ in ent if not r["type_line"].startswith("Basic") and r["name"] not in cn}
    # Vergleichsdecks: Precons und eigene gespeicherte Decks
    pools = []
    for pid, in con.execute("SELECT id FROM precons"):
        pools.append(("precon", {n for n, in con.execute("SELECT name FROM precon_cards WHERE precon_id = ?", (pid,))}))
    decks_table(con)
    for name, lst in con.execute("SELECT name, list FROM decks WHERE owner = ?", (uid,)):
        pools.append(("deck:" + name, set(list_counts(lst))))
    gallery_tables(con)
    ngal = 0
    for name, lst in con.execute("SELECT name, list FROM decks WHERE public = 1 AND hidden = 0 AND owner <> ?", (uid,)):
        pools.append(("galerie", set(list_counts(lst))))
        ngal += 1
    owned = owned_map(con, uid)
    only_owned = g("owned") == "1"
    try:
        maxeur = float(g("maxeur").replace(",", ".")) if g("maxeur").strip() else 0
    except ValueError:
        maxeur = 0
    def price_ok(r):
        return not maxeur or (r["eur"] not in (None, "") and float(r["eur"]) <= maxeur) or r["name"] in owned
    # Siegquoten eigener Decks aus dem Spielprotokoll
    games_table(con)
    rate = {}
    for e in games_overview(con, uid)["decks"]:
        if e["games"] >= 3:
            rate[e["name"]] = e["wins"] / e["games"]
    # Seltene Gemeinsamkeiten zählen mehr als Allerweltskarten (Sol Ring, Command Tower …): IDF-Gewichtung
    df = {}
    for _, cards in pools:
        for n in cards:
            df[n] = df.get(n, 0) + 1
    N = max(1, len(pools))
    idf = lambda n: math.log((N + 1) / (df.get(n, 0) + 1))
    core_w = sum(idf(n) for n in core) or 1
    co, support, origin, sims = {}, {n: 0.0 for n in core}, {}, []
    for kind, cards in pools:
        shared = cards & core
        if cards >= core:
            continue
        sim = sum(idf(n) for n in shared) / core_w
        if sim < 0.04:
            continue
        if kind.startswith("deck:") and kind[5:] in rate:
            sim *= 0.5 + rate[kind[5:]]
        sims.append(sim)
        for n in cards - have:
            co[n] = co.get(n, 0) + sim * idf(n)
            origin.setdefault(n, set()).add({"precon": "Precons", "galerie": "Galerie-Decks"}.get(kind, "eigenen Decks"))
        for n in shared:
            support[n] += sim
    terms, labels, tribal = synergy_terms(con, cmds) if cmds else ([], [], set())
    def syn(r):
        t = (r["oracle_text"] or "").lower() + " " + r["type_line"].lower()
        return sum(1 for x in terms if x.lower() in t) + 2 * sum(1 for x in tribal if x.lower() in r["type_line"].lower())
    cand = []
    for n, w in sorted(co.items(), key=lambda x: -x[1])[:400]:
        r = con.execute("SELECT * FROM cards WHERE name = ? AND commander_legal = 1", (n,)).fetchone()
        if not r or "Land" in r["type_line"].split(" // ")[0] or any(x not in ci for x in r["color_identity"]):
            continue
        if (only_owned and n not in owned) or not price_ok(r):
            continue
        s_ = syn(r)
        score = w * 3 + s_ * 1.5 + (1.5 if r["edhrec_rank"] and r["edhrec_rank"] < 3000 else 0) + (1 if n in owned else 0)
        why = []
        if w:
            why.append("oft zusammen mit deinen Karten in " + " und ".join(sorted(origin.get(n, []))))
        if s_:
            why.append("passt zum Commander-Text")
        cand.append({"name": n, "score": round(score, 2), "why": "; ".join(why), "eur": r["eur"], "image": r["image"],
                     "scryfall": r["scryfall_uri"], "mana": r["mana_cost"], "owned": n in owned})
    cand.sort(key=lambda x: -x["score"])
    # Lücken je Funktion (Richtwerte für 100-Karten-Commander) mit passenden Karten
    cnt = {k: 0 for k in ROLE_TARGETS}
    for r, q in ent:
        for c in categories(r):
            if c in cnt:
                cnt[c] += q
    gaps, taken = [], {x["name"] for x in cand[:15]}
    comax = max(co.values()) if co else 1
    for role, (label, target, likes) in ROLE_TARGETS.items():
        if cnt[role] >= target:
            continue
        sql = ("SELECT * FROM cards WHERE commander_legal = 1 AND (" + " OR ".join("lower(oracle_text) LIKE ?" for _ in likes)
               + ") ORDER BY CASE WHEN edhrec_rank IS NULL THEN 1 ELSE 0 END, edhrec_rank LIMIT 1500")
        picks, seen = [], set()
        for r in con.execute(sql, ["%" + x + "%" for x in likes]):
            n = r["name"]
            if n in have or n in seen or n in taken or role not in categories(r) or not role_ok(r, role) \
                    or any(x not in ci for x in r["color_identity"]):
                continue
            if (only_owned and n not in owned) or not price_ok(r) or r["type_line"].startswith("Basic"):
                continue
            seen.add(n)
            rk = r["edhrec_rank"] or 30000
            sc = co.get(n, 0) / comax * 4 + min(syn(r), 3) + 6 * (1 - min(rk, 20000) / 20000) + (2 if n in owned else 0)
            picks.append({"name": n, "score": round(sc, 2), "eur": r["eur"], "image": r["image"], "scryfall": r["scryfall_uri"],
                          "mana": r["mana_cost"], "owned": n in owned})
            if len(seen) >= 120:
                break
        picks.sort(key=lambda x: -x["score"])
        taken |= {x["name"] for x in picks[:6]}
        gaps.append({"role": role, "label": label, "have": cnt[role], "target": target, "cards": picks[:6]})
    # Streichkandidaten: wenig Rückhalt in ähnlichen Decks, wenig Synergie, wenig beliebt; nie Commander oder markierte Wincons
    tags = {}
    try:
        tags = (json.loads(g("extra") or "{}").get("tags") or {})
    except Exception:
        pass
    cuts = []
    for r, q in ent:
        n = r["name"]
        if n not in core or "Land" in r["type_line"].split(" // ")[0] or set(tags.get(n, [])) & {"Wincon", "Combo"}:
            continue
        rk = r["edhrec_rank"] or 99999
        keep = support.get(n, 0) * 4 + syn(r) * 1.5 + (6 if rk < 300 else 4 if rk < 1500 else 2 if rk < 5000 else 0) \
            + (2 if r["game_changer"] else 0)
        why = []
        if not support.get(n):
            why.append("in keinem ähnlichen Deck")
        if not syn(r):
            why.append("kein Bezug zum Commander-Text")
        if not r["edhrec_rank"] or r["edhrec_rank"] > 8000:
            why.append("selten gespielt")
        cuts.append({"name": n, "keep": round(keep, 2), "why": ", ".join(why) or "schwächster Rückhalt im Vergleich", "mana": r["mana_cost"],
                     "scryfall": r["scryfall_uri"], "image": r["image"]})
    cuts.sort(key=lambda x: x["keep"])
    used = len(sims)
    return {"add": cand[:15], "cut": cuts[:8], "compared": used, "frust": frust_index(ent), "labels": labels, "gaps": gaps,
            "counts": cnt, "gallery": ngal, "owned_filter": only_owned, "maxeur": maxeur,
            "hint": f"Grundlage: {used} ähnliche Decks (Precons, eigene gespeicherte Decks"
                    + (f" und {ngal} veröffentlichte Decks aus der Galerie" if ngal else "")
                    + "; gemeinsame seltene Karten zählen mehr als Allerweltskarten)"
                    + (", Siegquoten aus dem Spielprotokoll" if rate else "") + " und der Text des Commanders. Ohne EDHREC-Daten."}


# ---------------------------------------------------------------- Teilen per Link
def deck_share(con, did, on, uid=0):
    decks_table(con)
    r = con.execute("SELECT share FROM decks WHERE id = ? AND owner = ?", (did, uid)).fetchone()
    if not r:
        return {"error": "Deck nicht gefunden."}
    tok = (r[0] or secrets.token_urlsafe(12)) if on else ""
    con.execute("UPDATE decks SET share = ? WHERE id = ? AND owner = ?", (tok, did, uid))
    con.commit()
    return {"ok": True, "token": tok, "path": f"/d/{tok}" if tok else ""}


def shared_page(tok):
    import html as H
    con = db()
    con.row_factory = sqlite3.Row
    decks_table(con)
    d = con.execute("SELECT name, commander, list, extra, saved_at FROM decks WHERE share = ? AND share <> ''", (tok,)).fetchone() \
        if re.fullmatch(r"[A-Za-z0-9_-]{8,40}", tok or "") else None
    if not d:
        return None
    ent, _ = entries_from_list(con, d["list"], d["commander"])
    try:
        ex = json.loads(d["extra"] or "{}")
    except Exception:
        ex = {}
    tags = ex.get("tags") or {}
    cgroups = ex.get("groups") or {}
    cmds = {r["name"] for r in resolve_cmds(con, d["commander"])}
    def kind(r):
        t = r["type_line"].split(" // ")[0]
        if r["name"] in cmds:
            return "Commander"
        if cgroups.get(r["name"]):
            return cgroups[r["name"]]
        for k in ("Creature", "Planeswalker", "Battle", "Instant", "Sorcery", "Artifact", "Enchantment", "Land"):
            if k in t:
                return {"Creature": "Kreaturen", "Planeswalker": "Planeswalker", "Battle": "Schlachten", "Instant": "Spontanzauber",
                        "Sorcery": "Hexereien", "Artifact": "Artefakte", "Enchantment": "Verzauberungen", "Land": "Länder"}[k]
        return "Sonstige"
    groups = {}
    for r, q in ent:
        groups.setdefault(kind(r), []).append((r, q))
    order = ["Commander"] + sorted({v for v in cgroups.values() if v} - {"Commander", "Länder"}) + \
        ["Kreaturen", "Planeswalker", "Spontanzauber", "Hexereien", "Artefakte", "Verzauberungen", "Schlachten", "Sonstige", "Länder"]
    order = list(dict.fromkeys(order))
    total = sum(q for _, q in ent)
    value = sum(float(r["eur"]) * q for r, q in ent if r["eur"] not in (None, "") and not r["type_line"].startswith("Basic"))
    bc = bracket_check(con, ent, cmds)
    btxt = (f"Bracket {H.escape(ex['bracket'])} ({BRACKETS[int(ex['bracket'])][0]}) laut Besitzer · Schätzung {bc['bracket']}" if ex.get("bracket")
            else f"Bracket-Schätzung {bc['bracket']} ({bc['name']}, ohne Combo-Prüfung)")
    e = H.escape
    out = [f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>{e(d['name'])} · Commander-Deck</title>",
           "<style>body{font:15px system-ui,sans-serif;max-width:900px;margin:auto;padding:12px;background:#f7f4ee;color:#222}"
           "h1{margin:.2em 0}.g{columns:2 260px}.g div{break-inside:avoid;margin:2px 0}a{color:#0b5394;text-decoration:none}"
           ".t{font-size:.8em;padding:0 5px;border-radius:8px;background:#e7f1fb;border:1px solid #9bc;margin-left:4px}"
           "#pv{position:fixed;right:10px;top:10px;width:240px;display:none;border-radius:10px;box-shadow:0 2px 12px #0006}"
           "pre{white-space:pre-wrap;background:#fff;padding:8px;border:1px solid #ddd}textarea{width:100%}</style>",
           f"<h1>{e(d['name'])}</h1><p>Commander: <b>{e(d['commander'] or '–')}</b> · {total} Karten · ca. {f'{value:.2f}'.replace('.', ',')} € · Stand {e(d['saved_at'] or '')}</p><p>{btxt}</p>"]
    if ex.get("notes"):
        out.append(f"<h3>Notizen</h3><pre>{e(ex['notes'])}</pre>")
    for k in order:
        if k not in groups:
            continue
        out.append(f"<h3>{k} ({sum(q for _, q in groups[k])})</h3><div class=g>")
        for r, q in sorted(groups[k], key=lambda x: (x[0]["cmc"], x[0]["name"])):
            tg = "".join(f"<span class=t>{e(t)}</span>" for t in tags.get(r["name"], []))
            img = e(r["image"] or "")
            out.append(f"<div>{q} <a href='{e(r['scryfall_uri'] or '#')}' data-img='{img}' rel=noopener target=_blank>{e(r['name'])}</a> "
                       f"<small>{e(r['mana_cost'] or '')}</small>{tg}</div>")
        out.append("</div>")
    if ex.get("maybe"):
        out.append("<h3>Maybeboard</h3><div class=g>" + "".join(f"<div>{e(n)}</div>" for n in ex["maybe"]) + "</div>")
    out.append("<h3>Liste zum Kopieren</h3><textarea rows=8 readonly>" + e(d["list"]) + "</textarea>"
               "<p><small>Geteilt mit der Manaschmiede. Kartendaten und Bilder: Scryfall. Inoffizieller Fan-Inhalt, "
               "nicht von Wizards of the Coast unterstützt.</small></p><img id=pv alt=''>"
               "<script>const pv=document.getElementById('pv');document.querySelectorAll('[data-img]').forEach(a=>{"
               "a.onmouseenter=()=>{if(a.dataset.img){pv.src=a.dataset.img;pv.style.display='block'}};a.onmouseleave=()=>pv.style.display='none'})</script>")
    return "".join(out)


# ---------------------------------------------------------------- Spielprotokoll
def games_table(con):
    con.execute("CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY, owner INTEGER, played_at TEXT, players TEXT, winner INTEGER, "
                "turns INTEGER, note TEXT, source TEXT)")


def game_save(p, uid=0):
    """Eine oder mehrere Partien speichern. games = JSON-Liste aus {players:[{name, deck}], winner (Index oder -1), turns, note, source}."""
    g = lambda k: (p.get(k) or [""])[0]
    try:
        games = json.loads(g("games") or "[]")
        assert isinstance(games, list) and 0 < len(games) <= 200
    except Exception:
        return {"error": "Ungültige Spieldaten."}
    con = db()
    games_table(con)
    now = datetime.datetime.now().isoformat(sep=" ", timespec="minutes")
    n = 0
    for x in games:
        pl = [{"name": str(q.get("name") or f"Spieler {i + 1}")[:40], "deck": str(q.get("deck") or "")[:80]}
              for i, q in enumerate((x.get("players") or [])[:8])]
        if len(pl) < 2:
            continue
        w = int(x.get("winner", -1)) if str(x.get("winner", -1)).lstrip("-").isdigit() else -1
        con.execute("INSERT INTO games(owner, played_at, players, winner, turns, note, source) VALUES(?,?,?,?,?,?,?)",
                    (uid, now, json.dumps(pl, ensure_ascii=False), w if -1 <= w < len(pl) else -1,
                     int(x.get("turns") or 0) if str(x.get("turns") or "0").isdigit() else 0,
                     str(x.get("note") or "")[:300], "forge" if x.get("source") == "forge" else "tisch"))
        n += 1
    con.commit()
    out = games_overview(con, uid)
    out["saved"] = n
    return out


def games_overview(con, uid=0):
    games_table(con)
    rows = con.execute("SELECT id, played_at, players, winner, turns, note, source FROM games WHERE owner = ? ORDER BY id DESC",
                       (uid,)).fetchall()
    decks, players = {}, {}
    for _, _, pl, w, *_ in rows:
        pl = json.loads(pl)
        for i, q in enumerate(pl):
            for key, tab in ((q["deck"], decks), (q["name"], players)):
                if not key:
                    continue
                e = tab.setdefault(key, {"name": key, "games": 0, "wins": 0})
                e["games"] += 1
                e["wins"] += int(i == w)
    for tab in (decks, players):
        for e in tab.values():
            e["rate"] = round(100 * e["wins"] / e["games"])
    srt = lambda t: sorted(t.values(), key=lambda e: (-e["rate"], -e["games"], e["name"]))
    recent = [{"id": i, "at": at, "players": json.loads(pl), "winner": w, "turns": t, "note": nt, "source": src}
              for i, at, pl, w, t, nt, src in rows[:40]]
    return {"count": len(rows), "decks": srt(decks), "players": srt(players), "recent": recent}


# ---------------------------------------------------------------- Token-Liste
TOKEN_RE = re.compile(r"\b[Cc]reates? (?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|X|that many|\d+|a number of|"
                      r"twice that many|a copy of)?\s*(?:tapped |untapped |legendary |attacking )*(.{1,70}?) tokens?\b")


def text_tokens(text):
    out = []
    for m in TOKEN_RE.finditer(text or ""):
        t = re.sub(r"\s+with .*$|\s+that's .*$|\s+named .*$", "", m.group(1)).strip(" ,")
        t = re.sub(r"^(?:(?:and|tapped|attacking|untapped)\s+)+", "", t, flags=re.I)
        if t and 2 < len(t) < 60 and t.lower() not in ("a", "an") and not re.search(r"\b(that|those|the|it|copy|copies|of)\b", t):
            out.append(t[0].upper() + t[1:])
    return out


def deck_tokens(p):
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    ent, _ = entries_from_list(con, g("list"), g("commander"))
    con.execute("CREATE TABLE IF NOT EXISTS card_tokens(card TEXT, token TEXT, type_line TEXT, sid TEXT)")
    linked = con.execute("SELECT count(*) FROM card_tokens").fetchone()[0] > 0
    tok = {}
    for r, _ in ent:
        rows = con.execute("SELECT token, type_line, sid FROM card_tokens WHERE card = ?", (r["name"],)).fetchall() if linked else []
        if rows:
            for t in rows:
                k = (t["token"], t["type_line"])
                e = tok.setdefault(k, {"name": t["token"], "type": t["type_line"], "sid": t["sid"], "from": []})
                e["from"].append(r["name"])
        elif not linked or "token" in (r["oracle_text"] or "").lower():
            for t in text_tokens(r["oracle_text"]):
                e = tok.setdefault((t, ""), {"name": t, "type": "", "sid": None, "from": []})
                e["from"].append(r["name"])
    out = sorted(tok.values(), key=lambda x: (-len(x["from"]), x["name"]))
    for e in out:
        e["image"] = f"https://api.scryfall.com/cards/{e['sid']}?format=image&version=normal" if e["sid"] else None
        e["from"] = sorted(set(e["from"]))
    return {"tokens": out, "source": "scryfall" if linked else "text",
            "hint": None if linked else "Tokens aus dem Kartentext erkannt; nach der nächsten Kartenaktualisierung kommen genaue Daten und Bilder von Scryfall."}


# ---------------------------------------------------------------- Manabasis-Analyse
LAND_TYPES = {"Plains": "W", "Island": "U", "Swamp": "B", "Mountain": "R", "Forest": "G"}
COLOR_DE = {"W": "Weiß", "U": "Blau", "B": "Schwarz", "R": "Rot", "G": "Grün"}


def fetched_colors(text, ci):
    """Farben, die eine Karte per „Search your library for … land“ besorgen kann (Fetch-/Suchländer, Ramp-Zauber)."""
    out = set()
    for m in re.finditer(r"[Ss]earch(?:es)? (?:your|their) library for ([^.]*?)\b(?:cards?|and)\b", text):
        part = m.group(1)
        if not re.search(r"\bland\b|Plains|Island|Swamp|Mountain|Forest", part):
            continue
        out |= {c for t, c in LAND_TYPES.items() if t in part}
        if re.search(r"basic land|\bland card|lands? cards?|\bland\b", part) and not re.search(r"Plains|Island|Swamp|Mountain|Forest", part):
            out |= set(ci)
    return out & set(ci)


def source_weights(r, ci):
    """Gewicht als Farbquelle je Farbe: Länder, Fetch-/Suchländer und frühe Manasteine/-kreaturen zählen voll,
    Ramp-Zauber bis Manawert 3, die ein Land suchen, zur Hälfte (nach Frank Karstens Vorgehen)."""
    front = r["type_line"].split(" // ")[0]
    text = (r["oracle_text"] or "").split("\n//\n")[0] if r["oracle_text"] else ""
    w = {c: 1.0 for c in produced_colors(r, ci)}
    if "Land" in front:
        for c in fetched_colors(text, ci):
            w[c] = 1.0
    elif r["cmc"] <= 3 and re.search(r"(Sorcery|Instant)", front) or (r["cmc"] <= 3 and "Creature" in front):
        for c in fetched_colors(text, ci):
            w.setdefault(c, 0.5)
    return w


def partner_problem(cmds):
    """None, wenn die beiden Commander zusammen erlaubt sind (Regel 702.124 und verwandte), sonst ein Hinweistext."""
    a, b = cmds
    t = lambda r: (r["oracle_text"] or "").split("\n//\n")[0]
    def plain(r):
        return re.search(r"(?m)^Partner(?: \(|$)", t(r))
    def variant(r):
        m = re.search(r"(?m)^Partner—([^(\n]+?)\s*(?:\(|$)", t(r))
        return m.group(1).strip() if m else None
    def partner_with(r):
        m = re.search(r"(?m)^Partner with ([^(\n]+?)\s*(?:\(|$)", t(r))
        return m.group(1).strip() if m else None
    if plain(a) and plain(b):
        return None
    if variant(a) and variant(a) == variant(b):
        return None
    if partner_with(a) == b["name"] or partner_with(b) == a["name"]:
        return None
    if re.search(r"(?m)^Friends forever", t(a)) and re.search(r"(?m)^Friends forever", t(b)):
        return None
    for x, y in ((a, b), (b, a)):
        if re.search(r"Choose a Background", t(x)) and "Background" in y["type_line"]:
            return None
        if re.search(r"Doctor's companion", t(x)) and "Time Lord Doctor" in y["type_line"]:
            return None
    pw = partner_with(a) or partner_with(b)
    if pw:
        return f"„Partner with“ erlaubt nur den genannten Partner ({pw})."
    return (f"{a['name']} und {b['name']} dürfen nicht gemeinsam Commander sein. Beide brauchen „Partner“ "
            "(bzw. dieselbe Partner-Variante, „Friends forever“) oder es muss „Choose a Background“ mit einem Hintergrund "
            "bzw. „Doctor's companion“ mit einem Doktor sein.")


def produced_colors(r, ci):
    """Welche Farben eine Karte als Mana erzeugt (Länder vollständig inkl. Fetch-/Suchländer, Mana-Artefakte/-Kreaturen bis Manawert 2)."""
    front = r["type_line"].split(" // ")[0]
    text = (r["oracle_text"] or "").split("\n//\n")[0] if r["oracle_text"] else ""
    out = set()
    if "Land" in front:
        out |= {c for t, c in LAND_TYPES.items() if t in front}
        out |= fetched_colors(text, ci)
    elif not (r["cmc"] <= 2 and re.search(r"\bAdd\b", text)):
        return set()
    for m in re.finditer(r"\bAdd ([^.]*)", text):
        part = m.group(1)
        out |= set(re.findall(r"\{([WUBRG])\}", part))
        if re.search(r"any color|any one color|mana of any|any combination of colors|in any combination", part):
            out |= set(ci)
    if re.search(r"commander's color identity|mana of any color|one mana of any type", text):
        out |= set(ci)
    return out & set(ci)


def hyper_atleast(N, K, n, k):
    """Wahrscheinlichkeit, bei n aus N Karten (K Treffer im Stapel) mindestens k Treffer zu sehen."""
    if k <= 0:
        return 1.0
    if K < k or n < k:
        return 0.0
    tot = math.comb(N, n)
    return sum(math.comb(K, i) * math.comb(N - K, n - i) for i in range(k, min(n, K) + 1)) / tot


def mana_analysis(p):
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    ent, _ = entries_from_list(con, g("list"), g("commander"))
    if not ent:
        return {"error": "Leere Deckliste."}
    cmds = resolve_cmds(con, g("commander"))
    cn = {r["name"] for r in cmds}
    ci = "".join(x for x in ORDER if any(x in r["color_identity"] for r in cmds)) if cmds else \
        "".join(x for x in ORDER if any(x in r["color_identity"] for r, _ in ent))
    library = [(r, q) for r, q in ent if r["name"] not in cn]
    N = sum(q for _, q in library)
    lands = sum(q for r, q in library if "Land" in r["type_line"].split(" // ")[0])
    sources = {c: 0.0 for c in ci}
    for r, q in library:
        for c, wt in source_weights(r, ci).items():
            sources[c] += wt * q
    colors = []
    for c in ci:
        need = []
        for r, q in ent:
            if "Land" in r["type_line"].split(" // ")[0]:
                continue
            cost = (r["mana_cost"] or "").split(" // ")[0]
            pips = len(re.findall(r"\{" + c + r"(?:/[WUBRGP2])?\}", cost)) + len(re.findall(r"\{[WUBRG2]/" + c + r"\}", cost))
            if not pips:
                continue
            turn = max(int(r["cmc"] or 0), pips, 1)
            seen = 7 + turn - 1  # bis zu diesem Zug gesehene Karten (Startspieler)
            prob = hyper_atleast(N, int(round(sources[c])), min(seen, N), pips)
            need.append({"name": r["name"], "pips": pips, "turn": turn, "prob": round(prob * 100), "commander": r["name"] in cn})
        if not need:
            continue
        need.sort(key=lambda x: x["prob"])
        avg = round(sum(x["prob"] for x in need) / len(need))
        colors.append({"color": c, "label": COLOR_DE[c], "sources": round(sources[c], 1), "cards": len(need),
                       "pips": sum(x["pips"] for x in need), "avg": avg, "weak": [x for x in need if x["prob"] < 85][:6],
                       "status": "gut" if avg >= 90 else ("knapp" if avg >= 80 else "zu wenig Quellen")})
    nonland = [(r, q) for r, q in library if "Land" not in r["type_line"].split(" // ")[0]]
    avg_mv = sum(r["cmc"] * q for r, q in nonland) / max(1, sum(q for _, q in nonland))
    return {"colors": colors, "lands": lands, "cards": N, "avg_mv": round(avg_mv, 2),
            "hint": "Chance, die nötigen farbigen Quellen bis zum Zug mit dem Manawert der Karte gesehen zu haben "
                    "(als Startspieler, ohne Mulligan). Als Quelle zählen Länder einschließlich Fetch- und Suchländern sowie Mana-Artefakte/"
                    "-Kreaturen bis Manawert 2; Ramp-Zauber bis Manawert 3, die ein Land suchen, zählen halb. "
                    "Ziel: etwa 90 %."}


# ---------------------------------------------------------------- Karten tauschen
CAT_GROUP = {"ramp": "Ramp", "draw": "Kartenvorteil", "removal": "Entfernung", "wipe": "Massenentfernung"}
MAIN_TYPES = ["Creature", "Planeswalker", "Instant", "Sorcery", "Artifact", "Enchantment", "Battle"]


def alternatives(p):
    """Ersatzkarten mit gleicher Aufgabe im Deck: gleiche Gruppe bzw. Funktion, passende Farben, ähnlicher Manawert."""
    g = lambda k: (p.get(k) or [""])[0].strip()
    con = db()
    con.row_factory = sqlite3.Row
    r, _ = lookup(con, g("name"))
    if not r:
        return {"error": "Karte nicht gefunden."}
    ci = "".join(x for x in ORDER if x in g("ci").upper())
    where, args = ["commander_legal = 1", "type_line NOT LIKE 'Basic%'"], []
    for x in ORDER:
        if x not in ci:
            where.append("color_identity NOT LIKE ?"); args.append(f"%{x}%")
    if g("nogc") == "1":
        where.append("game_changer = 0")
    if g("maxeur"):
        where.append("eur IS NOT NULL AND eur <= ?"); args.append(float(g("maxeur").replace(",", ".")))
    block = {x.strip() for x in (g("deck") + "\n" + g("exclude")).splitlines() if x.strip()} | {r["name"]}
    where.append("name NOT IN (%s)" % ",".join("?" * len(block))); args += list(block)
    group, fixed = g("group"), {n: sql for n, _, sql in FIXED}
    cats = [c for c in categories(r) if c in CAT_GROUP]
    if "Land" in front_type(r):
        cond, targs, reason = "type_line LIKE '%Land%'", [], "andere Länder"
    elif group in fixed:
        cond, targs, reason = f"{NL} AND {fixed[group]}", [], f"gleiche Aufgabe: {group}"
    elif group.startswith("Thema:") and theme_sql(group[6:].strip())[0]:
        tsql, targs = theme_sql(group[6:].strip())
        cond, reason = f"{NL} AND {tsql}", f"passend zum {group}"
    elif cats:
        cond, targs, reason = f"{NL} AND {fixed[CAT_GROUP[cats[0]]]}", [], f"gleiche Aufgabe: {CAT_GROUP[cats[0]]}"
    else:
        t = next((t for t in MAIN_TYPES if t in front_type(r)), None)
        cond, targs = (f"{NL} AND type_line LIKE '%{t}%'" if t else NL), []
        reason = f"gleicher Kartentyp ({t})" if t else "beliebte Karten"
    rows = con.execute(f"SELECT * FROM cards WHERE {' AND '.join(where)} AND {cond} "
                       f"ORDER BY edhrec_rank IS NULL, edhrec_rank LIMIT 80", args + targs).fetchall()
    rows = sorted(rows, key=lambda x: (abs(x["cmc"] - r["cmc"]) > 1, x["edhrec_rank"] or 10**9))[:int(g("limit") or 12)]
    return {"for": r["name"], "reason": reason + ("" if "Land" in front_type(r) else ", ähnlicher Manawert bevorzugt"), "cards": [card_dict(x) for x in rows]}


# ---------------------------------------------------------------- Precons
PRECON_URL = "https://raw.githubusercontent.com/taw/magic-preconstructed-decks-data/master/decks_v2.json"


def has_precons(con):
    return bool(con.execute("SELECT 1 FROM sqlite_master WHERE name = 'precons'").fetchone())


def do_precons(path=None, raw=None):
    """Lädt alle offiziellen Commander-Precons (Datenquelle: mtg.wtf / MTGJSON, ca. 30 MB)."""
    if raw is not None:
        pass
    elif path:
        raw = open(path, "rb").read()
    else:
        print("Lade Precon-Decklisten (ca. 30 MB) ...")
        raw = fetch(PRECON_URL)
    data = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    con = db()
    names = {n for (n,) in con.execute("SELECT name FROM cards")}
    face = {}
    for n in names:
        for f in n.split(" // "):
            face.setdefault(f.lower(), n)
    norm = lambda n: n if n in names else face.get(n.lower()) or face.get(n.split(" // ")[0].lower()) or n
    ci_of = dict(con.execute("SELECT name, color_identity FROM cards"))
    decks = [x for x in data if x.get("type") == "Commander Deck" and x.get("commander")]
    decks.sort(key=lambda x: ("Collector" in x["name"], x.get("release_date") or ""))  # Normale Version vor Sammlerversion
    seen, pre, pcards = set(), [], []
    for x in decks:
        cmds = [norm(c["name"]) for c in x["commander"]]
        main = {}
        for c in x["cards"]:
            n = norm(c["name"])
            if n not in cmds:
                main[n] = main.get(n, 0) + c.get("count", 1)
        sig = (tuple(sorted(cmds)), tuple(sorted(main.items())))
        if sig in seen:
            continue
        seen.add(sig)
        pid = len(pre) + 1
        ci = "".join(c for c in ORDER if any(c in (ci_of.get(n) or "") for n in cmds))
        pre.append((pid, x["name"], x.get("set_name") or "", x.get("release_date") or "", " + ".join(cmds), ci))
        pcards += [(pid, n, 1, 1) for n in cmds] + [(pid, n, q, 0) for n, q in main.items()]
    con.executescript("""BEGIN; DROP TABLE IF EXISTS precons; DROP TABLE IF EXISTS precon_cards;
      CREATE TABLE precons(id INTEGER PRIMARY KEY, name TEXT, set_name TEXT, release_date TEXT, commander TEXT, color_identity TEXT);
      CREATE TABLE precon_cards(precon_id INTEGER, name TEXT, qty INTEGER, is_commander INTEGER);
      CREATE INDEX idx_pc ON precon_cards(precon_id);""")  # bleibt bis zum commit eine Transaktion
    con.executemany("INSERT INTO precons VALUES(?,?,?,?,?,?)", pre)
    con.executemany("INSERT INTO precon_cards VALUES(?,?,?,?)", pcards)
    con.execute("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)")
    con.execute("INSERT OR REPLACE INTO meta VALUES('precons_at', ?)",
                (datetime.datetime.now().isoformat(sep=" ", timespec="minutes"),))
    con.commit()
    print(f"{len(pre)} Commander-Precons gespeichert.")
    return len(pre)


def precon_list(con, q="", ci=""):
    """Precons passend zum Suchtext oder – ohne Text – zur Farbidentität (gleiche Farben zuerst)."""
    rows = con.execute("SELECT * FROM precons ORDER BY release_date DESC").fetchall()
    if q:
        ql = q.lower()
        hit = [r for r in rows if ql in (r["name"] + " " + r["commander"] + " " + r["set_name"]).lower()]
        if not hit:  # Tippfehler: ähnliche Deck- oder Commander-Namen
            words = {w: r for r in rows for w in [r["name"].lower(), *r["commander"].lower().split(" + ")]}
            hit = list(dict.fromkeys(words[k] for k in difflib.get_close_matches(ql, list(words), 10, 0.5)))
        rows = hit
    elif ci:
        own = set(ci)
        score = lambda r: (set(r["color_identity"]) == own, len(own & set(r["color_identity"])) - len(set(r["color_identity"]) - own))
        rows = sorted((r for r in rows if own & set(r["color_identity"]) or r["color_identity"] == ci),
                      key=score, reverse=True)
    return [{"id": r["id"], "name": r["name"], "set": r["set_name"], "date": r["release_date"],
             "commander": r["commander"], "ci": r["color_identity"]} for r in rows[:15]]


PRECON_CAT = {"key": None, "data": None}


def precon_catalog(con, uid=0):
    """Alle Precons mit Wert, Kartenzahl und Bracket-Schätzung. Zwischengespeichert (Speicher und Datenbank) bis zur
    nächsten Precon- oder Kartenaktualisierung."""
    if not has_precons(con):
        return {"precons": [], "loaded": False}
    key = f"{setting('precons_at')}|{setting('imported_at')}|1"
    if PRECON_CAT["key"] != key:
        con.execute("CREATE TABLE IF NOT EXISTS precon_catalog(key TEXT PRIMARY KEY, data TEXT)")
        hit = con.execute("SELECT data FROM precon_catalog WHERE key = ?", (key,)).fetchone()
        if hit:
            PRECON_CAT.update(key=key, data=json.loads(hit[0]))
        else:
            con.row_factory = sqlite3.Row
            best = {}
            for r in con.execute("SELECT * FROM cards WHERE name IN (SELECT DISTINCT name FROM precon_cards) ORDER BY commander_legal"):
                best[r["name"]] = r  # zuletzt = Commander-legale Fassung, wie in precon_entries
            pcards = {}
            for pid, n, q, ic in con.execute("SELECT precon_id, name, qty, is_commander FROM precon_cards"):
                pcards.setdefault(pid, []).append((n, q, ic))
            out = []
            for pr in con.execute("SELECT * FROM precons ORDER BY release_date DESC, set_name, name").fetchall():
                rows = pcards.get(pr["id"], [])
                plain = [(best[n], q) for n, q, ic in rows if n in best]
                cmds = {n for n, q, ic in rows if ic}
                eur = sum(float(r["eur"]) * q for r, q in plain if r["eur"] not in (None, "") and not front_type(r).startswith("Basic"))
                br = bracket_check(con, plain, cmds)
                out.append({"id": pr["id"], "name": pr["name"], "set": pr["set_name"], "date": pr["release_date"] or "",
                            "commander": pr["commander"], "ci": pr["color_identity"] or "C", "cards": sum(q for _, q in plain),
                            "eur": round(eur, 2), "bracket_est": br["bracket"], "gc": br["rules"][0]["count"],
                            "missing": sum(1 for n, q, ic in rows if n not in best)})
            con.row_factory = None
            con.execute("DELETE FROM precon_catalog")
            con.execute("INSERT INTO precon_catalog VALUES(?,?)", (key, json.dumps(out)))
            con.commit()
            PRECON_CAT.update(key=key, data=out)
    own = owned_map(con, uid)
    data = [dict(x) for x in PRECON_CAT["data"]]
    if own:  # Anteil der Karten (ohne Standardländer), die der Benutzer besitzt
        need, have = {}, {}
        for pid, n, q in con.execute("SELECT precon_id, name, qty FROM precon_cards WHERE name NOT IN "
                                     "('Plains','Island','Swamp','Mountain','Forest','Wastes')"):
            need[pid] = need.get(pid, 0) + q
            have[pid] = have.get(pid, 0) + min(q, own.get(n, 0))
        for x in data:
            x["owned"] = round(100 * have.get(x["id"], 0) / need[x["id"]]) if need.get(x["id"]) else 0
    return {"precons": data, "loaded": True, "at": setting("precons_at"), "has_collection": bool(own)}


def precon_to_collection(con, pid, uid=0):
    """Ein gekauftes Precon komplett in die Sammlung übernehmen (Karten werden addiert)."""
    rows = con.execute("SELECT name, qty FROM precon_cards WHERE precon_id = ?", (pid,)).fetchall()
    pr = con.execute("SELECT name FROM precons WHERE id = ?", (pid,)).fetchone()
    if not rows or not pr:
        return {"error": "Precon nicht gefunden."}
    out = collection_import({"text": ["\n".join(f"{q} {n}" for n, q in rows)], "mode": ["add"]}, uid)
    out["precon"] = pr[0]
    return out


def front_type(r):
    return r["type_line"].split(" // ")[0]


TUTOR = re.compile(r"search your library for ([^.]*)")
MLD = re.compile(r"(destroy|exile) all (nonbasic )?lands|each player sacrifices (all|[a-z]+) lands|lands don't untap", re.I)


def categories(r):
    """Funktionen einer Karte – dieselben Regeln wie beim Deckbau (Nicht-Länder)."""
    t, cats = (r["oracle_text"] or "").lower(), set()
    if "Land" in front_type(r):
        return cats
    if any(x in t for x in ("add {", "add one mana", "add two mana", "basic land card")) and r["cmc"] <= 3:
        cats.add("ramp")
    if any(s in t for s in ("draw a card", "draw two", "draw three")):
        cats.add("draw")
    if "destroy target" in t or "exile target" in t:
        cats.add("removal")
    if "destroy all" in t or "exile all" in t:
        cats.add("wipe")
    if any("land" not in m and not re.search(r"\b(forest|plains|island|swamp|mountain)\b", m) for m in TUTOR.findall(t)):
        cats.add("tutor")
    if "extra turn" in t:
        cats.add("extra")
    if MLD.search(t):
        cats.add("mld")
    return cats


def analyze(entries):
    """entries: Liste von (Kartenzeile, Anzahl), inklusive Commander."""
    m = {k: 0 for k in ("ramp", "draw", "removal", "wipe", "tutor", "extra", "mld")}
    lands = gc = total = 0
    cmcs, ranks, price, curve = [], [], 0.0, [0] * 8
    for r, q in entries:
        total += q
        if "Land" in front_type(r):
            lands += q
        else:
            cmcs += [r["cmc"]] * q
            curve[min(int(r["cmc"]), 7)] += q
        for c in categories(r):
            m[c] += q
        gc += q if r["game_changer"] else 0
        if r["edhrec_rank"] and not front_type(r).startswith("Basic"):
            ranks.append(r["edhrec_rank"])
        if r["eur"] not in (None, "") and not front_type(r).startswith("Basic"):
            price += float(r["eur"]) * q
    ranks.sort()
    if m["mld"] or gc > 3 or m["extra"] > EXTRA_TURN_LIMIT:
        bracket = "4"
    elif gc:
        bracket = "3"
    else:
        bracket = "1–2"
    return dict(m, total=total, lands=lands, gc=gc, price=round(price, 2), curve=curve,
                avg_cmc=round(sum(cmcs) / len(cmcs), 2) if cmcs else 0,
                median_rank=ranks[len(ranks) // 2] if ranks else None, bracket=bracket)


# (Kennzahl, Anzeige, Regel): min = mehr ist besser bis zum Richtwert; low = weniger ist besser;
# high = mehr ist besser (Spielstärke); range = möglichst im Bereich
DUEL = [("ramp", "Ramp", ("min", 10)), ("draw", "Kartenvorteil", ("min", 10)), ("removal", "Gezielte Entfernung", ("min", 8)),
        ("wipe", "Massenentfernung", ("min", 3)), ("lands", "Länder", ("range", 35, 38)),
        ("avg_cmc", "Ø Manawert (ohne Länder)", ("low", 0.1)), ("gc", "Game Changer", ("high",)),
        ("tutor", "Tutoren", ("high",)), ("median_rank", "Kartenqualität (EDHREC-Median, kleiner = beliebter)", ("low", 200))]


def duel(a, b):
    rows, sa, sb = [], 0, 0
    for key, label, rule in DUEL:
        x, y = a[key], b[key]
        if x is None or y is None:
            w = 0
        elif rule[0] == "min":
            w = (min(x, rule[1]) > min(y, rule[1])) - (min(x, rule[1]) < min(y, rule[1]))
        elif rule[0] == "high":
            w = (x > y) - (x < y)
        elif rule[0] == "low":
            w = 0 if abs(x - y) < rule[1] else (1 if x < y else -1)
        else:
            dist = lambda v: max(rule[1] - v, v - rule[2], 0)
            w = (dist(x) < dist(y)) - (dist(x) > dist(y))
        sa += w > 0
        sb += w < 0
        target = (f"Richtwert {rule[1]}+" if rule[0] == "min" else
                  f"Richtwert {rule[1]}–{rule[2]}" if rule[0] == "range" else "")
        rows.append({"label": label, "a": x, "b": y, "win": w, "hint": target})
    return rows, sa, sb


def cmd_names(text):
    """„A + B“ oder eine Zeile je Commander -> Liste der Namen (Partner, Hintergrund usw.)."""
    return [x.strip() for x in re.split(r"\s+\+\s+|\n", text or "") if x.strip()]


def resolve_cmds(con, text):
    return [r for r in (lookup(con, n, True)[0] for n in cmd_names(text)) if r]


def entries_from_list(con, text, commander=""):
    """Textliste („1 Sol Ring“ je Zeile) -> [(Kartenzeile, Anzahl)]; jeder Commander zählt genau einmal."""
    rows, qty, missing = {}, {}, []
    cmds = resolve_cmds(con, commander)
    for c in cmds:
        rows[c["name"]], qty[c["name"]] = c, 1
    cn = {c["name"] for c in cmds}
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        mt = re.match(r"^\s*(?:(\d+)\s*x?\s+)?(.+?)\s*$", line)
        if not mt:
            continue
        r = lookup(con, mt.group(2))[0]
        if not r:
            missing.append(mt.group(2))
        elif r["name"] in cn:
            continue
        else:
            rows[r["name"]] = r
            qty[r["name"]] = qty.get(r["name"], 0) + int(mt.group(1) or 1)
    return [(rows[n], qty[n]) for n in rows], missing


def precon_entries(con, pid):
    out, missing = [], []
    for n, q, ic in con.execute("SELECT name, qty, is_commander FROM precon_cards WHERE precon_id = ? ORDER BY is_commander DESC", (pid,)):
        r = con.execute("SELECT * FROM cards WHERE name = ? ORDER BY commander_legal DESC LIMIT 1", (n,)).fetchone()
        (out.append((r, q, ic)) if r else missing.append(n))
    return out, missing



# ---------------------------------------------------------------- Offizielle Regeln (Comprehensive Rules)
# Quelle: Wizards of the Coast, magic.wizards.com/en/rules. Der Text gehört Wizards of the Coast; das Skript lädt ihn
# zur persönlichen Nutzung direkt von dort und gibt ihn nicht weiter.
RULES_PAGE = "https://magic.wizards.com/en/rules"
RULE_LINE = re.compile(r"^(\d{3}(?:\.\d+[a-z]?)?)\.?\s+(.+)$")
CHAPTER_LINE = re.compile(r"^(\d)\.\s+(.+)$")


def rules_url_exists(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 CommanderDeckDB"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except Exception:
        return False


def find_rules_url():
    """Aktuellen TXT-Link von der offiziellen Regelseite lesen; notfalls die üblichen Veröffentlichungstage (freitags) prüfen."""
    found, err = [], None
    try:
        html = http_get(RULES_PAGE, "text/html")
        found = re.findall(r"https?://media\.wizards\.com/\d{4}/downloads/MagicCompRules[^\"'<>]*?\.txt", html)
    except Exception as e:
        err = e
    if not found:
        day = datetime.date.today()
        for _ in range(250):
            if day.weekday() == 4:
                u = f"https://media.wizards.com/{day.year}/downloads/MagicCompRules%20{day:%Y%m%d}.txt"
                if rules_url_exists(u):
                    return u
            day -= datetime.timedelta(days=1)
            if setting("rules_url") and (datetime.date.today() - day).days > 120:
                break
        raise RuntimeError(f"Regelseite von Wizards nicht erreichbar ({err})" if err else
                           "Auf der Regelseite von Wizards wurde kein TXT-Link gefunden.")
    found = [u.replace(" ", "%20") for u in found]
    return max(found, key=lambda u: re.sub(r"\D", "", u.rsplit("/", 1)[-1]))


def decode_rules(raw):
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


def parse_rules(text):
    """Comprehensive Rules -> (gültig ab, [(Nummer, Text)], [(Begriff, Erklärung)])."""
    lines = [l.rstrip() for l in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    eff = re.search(r"effective as of ([A-Z][a-z]+ \d{1,2}, \d{4})", text)
    starts = [i for i, l in enumerate(lines) if l.strip() == "1. Game Concepts"]
    gl = [i for i, l in enumerate(lines) if l.strip() == "Glossary"]
    cr = [i for i, l in enumerate(lines) if l.strip() == "Credits"]
    if len(starts) < 2 or len(gl) < 2:
        raise ValueError("Unbekannter Aufbau der Regeldatei.")
    body, gloss = lines[starts[1]:gl[1]], lines[gl[1] + 1:(cr[1] if len(cr) > 1 else len(lines))]
    rules = []
    for l in body:
        t = l.strip()
        if not t:
            continue
        m = RULE_LINE.match(t) or CHAPTER_LINE.match(t)
        if m and not t.lower().startswith("example"):
            rules.append([m.group(1), m.group(2)])
        elif rules:
            rules[-1][1] += "\n" + t
    terms, cur = [], []
    for l in gloss + [""]:
        if l.strip():
            cur.append(l.strip())
        elif cur:
            terms.append((cur[0], "\n".join(cur[1:])))
            cur = []
    return (eff.group(1) if eff else "unbekannt"), [tuple(r) for r in rules], terms


def store_rules(raw, url):
    eff, rules, terms = parse_rules(decode_rules(raw))
    if len(rules) < 1000:
        raise ValueError(f"Nur {len(rules)} Regeln erkannt. Ist die Datei unvollständig?")
    con = db()
    con.execute("CREATE TABLE IF NOT EXISTS rules(idx INTEGER PRIMARY KEY, num TEXT, text TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS glossary(term TEXT, text TEXT)")
    con.execute("DELETE FROM rules")
    con.execute("DELETE FROM glossary")
    con.executemany("INSERT INTO rules(num, text) VALUES(?,?)", rules)
    con.executemany("INSERT INTO glossary VALUES(?,?)", terms)
    con.execute("CREATE INDEX IF NOT EXISTS idx_rnum ON rules(num)")
    for k, v in (("rules_version", eff), ("rules_url", url), ("rules_count", str(len(rules))),
                 ("rules_at", datetime.datetime.now().isoformat(sep=" ", timespec="minutes"))):
        con.execute("INSERT OR REPLACE INTO meta VALUES(?,?)", (k, v))
    con.commit()
    return eff, len(rules), len(terms)


def has_rules(con):
    return bool(con.execute("SELECT 1 FROM sqlite_master WHERE name = 'rules'").fetchone()) and bool(
        con.execute("SELECT 1 FROM rules LIMIT 1").fetchone())


def rules_query(p):
    q = ((p.get("q") or [""])[0]).strip()
    con = db()
    meta = {"version": setting("rules_version"), "url": setting("rules_url"), "source": RULES_PAGE}
    if not has_rules(con):
        return dict(meta, error="Die Regeln sind noch nicht geladen. Oben auf „Jetzt aktualisieren“ klicken.", rules=[], glossary=[])
    if not q:
        rows = con.execute("SELECT num, text FROM rules WHERE length(num) <= 3 ORDER BY idx").fetchall()
        return dict(meta, toc=True, rules=[{"num": n, "text": t} for n, t in rows], glossary=[])
    num = re.sub(r"\.$", "", q.lower().replace("regel", "").replace("rule", "").strip())
    if re.fullmatch(r"\d{1,3}(\.\d+[a-z]?)?", num):
        if len(num) == 1:
            rows = con.execute("SELECT num, text FROM rules WHERE num = ? OR (length(num) = 3 AND num LIKE ?) ORDER BY idx",
                               (num, num + "%")).fetchall()
        else:
            rows = con.execute("SELECT num, text FROM rules WHERE num = ? OR num GLOB ? OR num LIKE ? ORDER BY idx",
                               (num, num + "[a-z]", num + ".%")).fetchall()
        return dict(meta, rules=[{"num": n, "text": t} for n, t in rows[:400]], glossary=[], total=len(rows))
    words = [w for w in re.split(r"\s+", q) if w]
    cond = " AND ".join(["text LIKE ?"] * len(words))
    args = [f"%{w}%" for w in words]
    gl = con.execute("SELECT term, text FROM glossary WHERE term LIKE ? OR (" + cond + ") "
                     "ORDER BY term LIKE ? DESC, term LIKE ? DESC, length(term) LIMIT 15",
                     [f"%{q}%"] + args + [q, f"{q}%"]).fetchall()
    rows = con.execute(f"SELECT num, text FROM rules WHERE {cond} ORDER BY idx", args).fetchall()
    return dict(meta, rules=[{"num": n, "text": t} for n, t in rows[:80]], total=len(rows),
                glossary=[{"term": a, "text": b} for a, b in gl])


# ---------------------------------------------------------------- Automatische Aktualisierung beim Start
UPDATE = {"running": False, "done": False, "items": {}, "at": "", "next": "", "max_age": 0}
def _int_env(name, default):
    try:
        return max(0, int(ENV(name, "") or default))
    except ValueError:
        return default


# Kartendaten werden neu geladen, wenn Scryfall neuere hat und die eigenen mindestens so alt sind (Tage).
# Server: täglich (Preise für Preisalarm und Verlauf), lokal: wöchentlich (der PC lädt nur beim Start).
CARDS_MAX_AGE_DAYS = _int_env("CDB_CARDS_MAX_AGE_DAYS", 1 if SERVER else 7)
# Stunde der nächtlichen Prüfung im Server-Betrieb; "off" schaltet sie ab. Lokal nur mit CDB_DAILY_UPDATE=1.
UPDATE_HOUR = None if (ENV("CDB_UPDATE_HOUR", "") or "").lower() in ("off", "aus", "-1") else min(23, _int_env("CDB_UPDATE_HOUR", 4))


def fetch_conditional(url, etag=""):
    """GET mit If-None-Match: liefert (None, etag), wenn sich nichts geändert hat."""
    h = dict(HEADERS, Accept="*/*")
    if etag:
        h["If-None-Match"] = etag
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=180) as r:
            return r.read(), r.headers.get("ETag") or ""
    except urllib.error.HTTPError as e:
        if e.code == 304:
            return None, etag
        raise


# ---------------------------------------------------------------- Cardmarket-Preisliste (öffentliche Dateien)
# Cardmarket stellt Price Guide und Produktliste frei zur Verfügung. Bedingungen laut Cardmarket-Support (19.11.2026):
# Nutzer müssen erkennen, dass es Cardmarket-Preise sind; Markenzeichen nur aus help.cardmarket.com/en/Downloads.
CM_PRICE_URL = ENV("CDB_CM_PRICE_URL", "") or "https://downloads.s3.cardmarket.com/productCatalog/priceGuide/price_guide_1.json"
CM_PRODUCTS_URL = ENV("CDB_CM_PRODUCTS_URL", "") or "https://downloads.s3.cardmarket.com/productCatalog/productList/products_singles_1.json"
CM_LINK = "https://www.cardmarket.com/de/Magic/Products?idProduct={}"
CM_CACHE = {"key": None, "map": {}}


def cm_table(con):
    con.execute("CREATE TABLE IF NOT EXISTS cm_cards(name TEXT PRIMARY KEY, id_cheap INTEGER, trend REAL, low REAL, avg1 REAL, "
                "avg7 REAL, avg30 REAL, foil REAL, prints INTEGER, eur_scryfall REAL)")


def cm_local_files():
    """Selbst heruntergeladene Dateien (Datenordner oder Downloads), falls der Abruf nicht klappt."""
    dirs = [DATA_DIR if "DATA_DIR" in globals() else ".", os.path.expanduser("~/Downloads"), "."]
    for d in dirs:
        a, b = os.path.join(d, "price_guide_1.json"), os.path.join(d, "products_singles_1.json")
        if os.path.isfile(a) and os.path.isfile(b):
            return open(a, "rb").read(), open(b, "rb").read(), d
    return None, None, None


def cm_value(trend, avg7, avg30, avg=None):
    """Robuster Preis einer Druckversion: Trendpreis, außer er liegt unter der Hälfte des 7- bzw. 30-Tage-Durchschnitts
    (einzelne Ausreißer-Verkäufe) – dann gilt der Durchschnitt."""
    ref = avg7 or avg30 or 0
    t = trend or 0
    if ref and t < ref * 0.5:
        return ref
    return t or ref or (avg or 0)


def cm_import(raw_prices, raw_products, con=None):
    """Ordnet Cardmarket-Produkte den Karten zu (Name, ältere Schreibweise „A / B“, sonst über die Produktnummer aus
    Scryfall und deren Metakarte) und übernimmt je Karte die günstigste Druckversion als Preis."""
    con = con or db()
    pg = json.loads(gzip.decompress(raw_prices) if raw_prices[:2] == b"\x1f\x8b" else raw_prices)
    pl = json.loads(gzip.decompress(raw_products) if raw_products[:2] == b"\x1f\x8b" else raw_products)
    guides = {x["idProduct"]: x for x in pg.get("priceGuides") or []}
    prods = pl.get("products") or []
    if len(guides) < 1000 or len(prods) < 1000:
        raise ValueError("Cardmarket-Dateien unvollständig")
    by_meta, by_name = {}, {}
    for x in prods:
        by_meta.setdefault(x.get("idMetacard"), []).append(x["idProduct"])
        by_name.setdefault(x["name"].lower(), set()).add(x.get("idMetacard"))
    id_meta = {x["idProduct"]: x.get("idMetacard") for x in prods}
    cm_table(con)
    # Sind die Kartendaten seit dem letzten Import schon mit Cardmarket-Preisen überschrieben, bleibt der alte Scryfall-Wert
    already = bool(setting("cm_applied")) and setting("cm_applied") == (setting("imported_at") or "")
    old_scry = {n: e for n, e in con.execute("SELECT name, eur_scryfall FROM cm_cards")} if already else {}
    rows = []
    for name, eur, uri in con.execute("SELECT name, CAST(eur AS REAL), cardmarket_uri FROM cards"):
        if already:
            eur = old_scry.get(name, eur)
        metas = set()
        for k in (name, name.replace(" // ", " / "), name.split(" // ")[0]):
            metas |= by_name.get(k.lower(), set())
            if metas:
                break
        m = re.search(r"idProduct=(\d+)", uri or "")
        if m and id_meta.get(int(m.group(1))) is not None:
            metas.add(id_meta[int(m.group(1))])
        metas.discard(0)
        ids = [i for mt in metas for i in by_meta.get(mt, [])]
        best, low, foil = None, None, None
        for i in ids:
            gd = guides.get(i)
            if not gd:
                continue
            t = cm_value(gd.get("trend"), gd.get("avg7"), gd.get("avg30"), gd.get("avg"))
            if t > 0 and (best is None or t < best[1]):
                best = (i, t, gd)
            if gd.get("low") and (low is None or gd["low"] < low):
                low = gd["low"]
            ft = cm_value(gd.get("trend-foil"), gd.get("avg7-foil"), gd.get("avg30-foil"), gd.get("avg-foil"))
            if ft > 0 and (foil is None or ft < foil):
                foil = ft
        if best:
            gd = best[2]
            rows.append((name, best[0], round(best[1], 2), low, gd.get("avg1"), gd.get("avg7"), gd.get("avg30"), foil, len(ids), eur))
    con.execute("DELETE FROM cm_cards")
    con.executemany("INSERT OR REPLACE INTO cm_cards VALUES(?,?,?,?,?,?,?,?,?,?)", rows)
    inv_tables(con)  # Preise je Druckversion für die Sammlung
    con.execute("DELETE FROM cm_prices")
    con.executemany("INSERT INTO cm_prices VALUES(?,?,?,?,?,?,?)",
                    [(i, round(cm_value(x.get("trend"), x.get("avg7"), x.get("avg30"), x.get("avg")), 2) or None, x.get("low"), x.get("avg7"), x.get("avg30"),
                      round(cm_value(x.get("trend-foil"), x.get("avg7-foil"), x.get("avg30-foil"), x.get("avg-foil")), 2) or None, x.get("low-foil"))
                     for i, x in guides.items()])
    con.commit()
    created = (pg.get("createdAt") or "")[:16].replace("T", " ")
    setting("cm_at", created)
    total = con.execute("SELECT count(*) FROM cards").fetchone()[0]
    setting("cm_matched", f"{len(rows)}/{total}")
    return cm_apply(con), len(rows), total, created


def cm_apply(con):
    """Cardmarket-Preis in die Kartendaten übernehmen (nach jedem Scryfall-Import erneut) und als Stichtag sichern."""
    cm_table(con)
    n = con.execute("UPDATE cards SET eur = (SELECT trend FROM cm_cards m WHERE m.name = cards.name) "
                    "WHERE name IN (SELECT name FROM cm_cards)").rowcount
    con.commit()
    setting("cm_applied", setting("imported_at") or "")
    record_prices(con, (setting("cm_at") or "")[:10])
    CM_CACHE.update(key=None, checked=0)
    return n


def update_cardmarket(force=False):
    con = db()
    cm_table(con)
    have = con.execute("SELECT count(*) FROM cm_cards").fetchone()[0]
    src = ""
    try:
        raw, etag = fetch_conditional(CM_PRICE_URL, "" if force or not have else setting("cm_etag"))
        prods = fetch(CM_PRODUCTS_URL) if raw is not None else None
    except Exception as e:
        raw, prods, d = cm_local_files()
        if raw is None:
            if have:
                if setting("cm_applied") != (setting("imported_at") or ""):
                    cm_apply(con)
                return f"Cardmarket nicht erreichbar ({e}); letzte Preisliste vom {setting('cm_at')} wird weiter genutzt"
            raise
        etag, src = "", f" aus {d}"
    if raw is None:
        if setting("cm_applied") != (setting("imported_at") or ""):
            cm_apply(con)  # neue Scryfall-Daten: Cardmarket-Preise wieder übernehmen
        return f"aktuell (Preisliste vom {setting('cm_at')}, {setting('cm_matched')} Karten zugeordnet)"
    n, matched, total, created = cm_import(raw, prods, con)
    setting("cm_etag", etag)
    return f"neu geladen{src}: Preisliste vom {created}, {matched} von {total} Karten zugeordnet"


def cm_info(con, name):
    """Cardmarket-Werte einer Karte (für Anzeige und Links)."""
    cm_table(con)
    r = con.execute("SELECT * FROM cm_cards WHERE name = ?", (name,)).fetchone()
    if not r:
        return {"name": name, "found": False}
    keys = ["name", "id_cheap", "trend", "low", "avg1", "avg7", "avg30", "foil", "prints", "eur_scryfall"]
    d = dict(zip(keys, tuple(r)))
    d.update(found=True, url=CM_LINK.format(d["id_cheap"]), at=setting("cm_at"))
    return d


def cm_link(name):
    """Link zur günstigsten Druckversion; Zwischenspeicher wird höchstens einmal pro Minute geprüft."""
    now = time.time()
    if now - CM_CACHE.get("checked", 0) > 60:
        CM_CACHE["checked"] = now
        try:
            cm_links(db())
        except Exception:
            pass
    return CM_CACHE["map"].get(name)


def cm_links(con):
    """Name → Link zur günstigsten Druckversion (zwischengespeichert)."""
    key = setting("cm_at")
    if CM_CACHE["key"] != key:
        try:
            cm_table(con)
            CM_CACHE.update(key=key, map={n: CM_LINK.format(i) for n, i in con.execute("SELECT name, id_cheap FROM cm_cards")})
        except sqlite3.Error:
            CM_CACHE.update(key=key, map={})
    return CM_CACHE["map"]


def update_rules(force=False):
    url = find_rules_url()
    con = db()
    if not force and url == setting("rules_url") and has_rules(con):
        return f"aktuell (gültig ab {setting('rules_version')})"
    eff, n, g = store_rules(fetch(url), url)
    return f"neu geladen: gültig ab {eff} ({n} Regeln, {g} Glossar-Begriffe)"


def update_precons(force=False):
    con = db()
    raw, etag = fetch_conditional(PRECON_URL, "" if force or not has_precons(con) else setting("precons_etag"))
    if raw is None:
        return f"aktuell (Stand {setting('precons_at')})"
    sha = hashlib.sha1(raw).hexdigest()
    if not force and sha == setting("precons_sha") and has_precons(con):
        setting("precons_etag", etag)
        return f"aktuell (Stand {setting('precons_at')})"
    n = do_precons(raw=raw)
    setting("precons_etag", etag)
    setting("precons_sha", sha)
    return f"neu geladen: {n} Precons"


def update_cards(force=False):
    entry = json.loads(fetch("https://api.scryfall.com/bulk-data/oracle-cards"))
    remote = (entry.get("updated_at") or "")[:16].replace("T", " ")
    local = setting("source_date")
    imported = setting("imported_at")[:16]
    try:
        age = (datetime.datetime.now() - datetime.datetime.fromisoformat(imported)).days
    except ValueError:
        age = 999
    if not force and local not in ("", "unbekannt") and (remote <= local or age < CARDS_MAX_AGE_DAYS):
        tage = "1 Tag" if CARDS_MAX_AGE_DAYS == 1 else f"{CARDS_MAX_AGE_DAYS} Tagen"
        return f"aktuell genug (Stand {local}{'; neuere Daten von ' + remote + ' werden ab ' + tage + ' Alter geladen' if remote > local else ''})"
    do_import(None)
    return f"neu geladen: Stand {setting('source_date')}, {setting('count')} Karten"


def auto_update(force=False, parts=("rules", "precons", "cards", "cardmarket")):
    if UPDATE["running"]:
        return
    UPDATE.update(running=True, done=False, items={})
    labels = {"rules": "Regeln", "precons": "Precons", "cards": "Kartendaten", "cardmarket": "Cardmarket-Preise"}
    for k in parts:
        UPDATE["items"][k] = {"label": labels[k], "status": "wird geprüft ...", "ok": None}
    for k, fn in (("rules", update_rules), ("precons", update_precons), ("cards", update_cards), ("cardmarket", update_cardmarket)):
        if k not in parts:
            continue
        try:
            UPDATE["items"][k].update(status=fn(force), ok=True)
        except Exception as e:
            UPDATE["items"][k].update(status=f"Prüfung fehlgeschlagen ({e}). Die vorhandenen Daten werden weiter genutzt.", ok=False)
        print(f"  {labels[k]}: {UPDATE['items'][k]['status']}")
    UPDATE.update(running=False, done=True, at=datetime.datetime.now().isoformat(sep=" ", timespec="minutes"))
    setting("updated_at", UPDATE["at"])


# ---------------------------------------------------------------- Benutzer und Anmeldung (Server-Modus)
def next_update_time(now=None):
    now = now or datetime.datetime.now()
    t = now.replace(hour=UPDATE_HOUR, minute=7, second=0, microsecond=0)
    return t if t > now else t + datetime.timedelta(days=1)


def update_scheduler():
    """Läuft im Hintergrund: einmal täglich (UPDATE_HOUR, 7 Minuten nach der vollen Stunde) auf neue Daten prüfen."""
    while True:
        nxt = next_update_time()
        UPDATE["next"] = nxt.isoformat(sep=" ", timespec="minutes")
        while datetime.datetime.now() < nxt:
            time.sleep(min(300, max(1, (nxt - datetime.datetime.now()).total_seconds())))
        print(f"Nächtliche Prüfung auf Aktualisierungen ({datetime.datetime.now():%d.%m.%Y %H:%M}) ...")
        try:
            auto_update(force=False)
        except Exception as e:  # der Server läuft auf jeden Fall weiter
            print("  Nächtliche Prüfung fehlgeschlagen:", e)
        time.sleep(90)


def users_tables(con):
    con.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT UNIQUE COLLATE NOCASE, pw TEXT, admin INTEGER, created TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, uid INTEGER, expires REAL)")


def pw_hash(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    return salt + "$" + hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200_000).hex()


def pw_check(pw, stored):
    try:
        return hmac.compare_digest(pw_hash(pw, stored.split("$")[0]), stored)
    except Exception:
        return False


def user_set(name, pw, admin=None):
    name = name.strip()
    if not re.fullmatch(r"[\w.@-]{2,40}", name):
        raise ValueError("Benutzername: 2–40 Zeichen, nur Buchstaben, Ziffern, Punkt, @, - und _.")
    if len(pw) < 8:
        raise ValueError("Das Passwort muss mindestens 8 Zeichen haben.")
    con = db()
    users_tables(con)
    r = con.execute("SELECT id, admin FROM users WHERE name = ?", (name,)).fetchone()
    if r:
        con.execute("UPDATE users SET pw = ?, admin = ? WHERE id = ?", (pw_hash(pw), r[1] if admin is None else int(admin), r[0]))
        con.execute("DELETE FROM sessions WHERE uid = ?", (r[0],))  # nach Passwortwechsel überall abmelden
    else:
        con.execute("INSERT INTO users(name, pw, admin, created) VALUES(?,?,?,?)",
                    (name, pw_hash(pw), int(bool(admin)), datetime.datetime.now().isoformat(sep=" ", timespec="minutes")))
    con.commit()


def session_new(uid):
    token = secrets.token_urlsafe(32)
    con = db()
    users_tables(con)
    con.execute("DELETE FROM sessions WHERE expires < ?", (time.time(),))
    con.execute("INSERT INTO sessions VALUES(?,?,?)", (token, uid, time.time() + SESSION_DAYS * 86400))
    con.commit()
    return token


def session_user(token):
    if not token:
        return None
    con = db()
    users_tables(con)
    r = con.execute("SELECT u.id, u.name, u.admin FROM sessions s JOIN users u ON u.id = s.uid WHERE s.token = ? AND s.expires > ?",
                    (token, time.time())).fetchone()
    return {"id": r[0], "name": r[1], "admin": bool(r[2])} if r else None


LOGIN_FAILS = {}  # IP -> (Anzahl, gesperrt bis)


def login(p, ip):
    g = lambda k: (p.get(k) or [""])[0]
    n, until = LOGIN_FAILS.get(ip, (0, 0))
    if until > time.time():
        return None, f"Zu viele Fehlversuche. Bitte {int(until - time.time()) + 1} Sekunden warten."
    con = db()
    users_tables(con)
    r = con.execute("SELECT id, pw FROM users WHERE name = ?", (g("name").strip(),)).fetchone()
    if r and pw_check(g("pw"), r[1]):
        LOGIN_FAILS.pop(ip, None)
        return session_new(r[0]), None
    n += 1
    LOGIN_FAILS[ip] = (n, time.time() + min(300, 2 ** max(0, n - 4)) if n >= 5 else 0)
    time.sleep(0.5)
    return None, "Benutzername oder Passwort falsch."


def users_list():
    con = db()
    users_tables(con)
    return [{"id": i, "name": n, "admin": bool(a), "created": c}
            for i, n, a, c in con.execute("SELECT id, name, admin, created FROM users ORDER BY name COLLATE NOCASE")]


def ensure_admin():
    """Legt beim Serverstart den Admin aus CDB_ADMIN_USER/CDB_ADMIN_PASSWORD an – oder erzeugt einen, falls es keinen gibt."""
    con = db()
    users_tables(con)
    name, pw = ENV("CDB_ADMIN_USER"), ENV("CDB_ADMIN_PASSWORD")
    if name and pw:
        user_set(name, pw, admin=True)
        print(f"Admin-Zugang „{name}“ ist eingerichtet.")
    elif not con.execute("SELECT 1 FROM users WHERE admin = 1").fetchone():
        pw = secrets.token_urlsafe(12)
        user_set("admin", pw, admin=True)
        print("=" * 70 + f"\nKein Admin konfiguriert, neu angelegt: Benutzer „admin“, Passwort: {pw}\n"
              "Bitte nach der ersten Anmeldung ändern (oder CDB_ADMIN_USER/CDB_ADMIN_PASSWORD setzen).\n" + "=" * 70)
    # Decks aus dem lokalen Betrieb (owner 0) gehören auf dem Server dem ersten Administrator
    aid = con.execute("SELECT id FROM users WHERE admin = 1 ORDER BY id LIMIT 1").fetchone()
    decks_table(con)
    if aid and con.execute("SELECT 1 FROM decks WHERE owner = 0 LIMIT 1").fetchone():
        n = con.execute("UPDATE OR IGNORE decks SET owner = ? WHERE owner = 0", (aid[0],)).rowcount
        con.commit()
        print(f"{n} Decks aus dem lokalen Betrieb dem Administrator zugeordnet.")


# ---------------------------------------------------------------- Spielabende: gemischte Gruppen, Siege, Rangliste, Saisons
GN_CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def gn_tables(con):
    con.execute("CREATE TABLE IF NOT EXISTS gn_nights(id INTEGER PRIMARY KEY, owner INTEGER, name TEXT, season TEXT DEFAULT '', "
                "code TEXT UNIQUE, created TEXT, closed INTEGER DEFAULT 0, log INTEGER DEFAULT 1)")
    con.execute("CREATE TABLE IF NOT EXISTS gn_players(night INTEGER, idx INTEGER, name TEXT, deck TEXT DEFAULT '', active INTEGER DEFAULT 1, "
                "PRIMARY KEY(night, idx))")
    con.execute("CREATE TABLE IF NOT EXISTS gn_pods(id INTEGER PRIMARY KEY, night INTEGER, round INTEGER, tab INTEGER, seats TEXT, "
                "winner INTEGER, reported TEXT, game_id INTEGER)")


def gn_pod_sizes(n):
    """Tischgrößen: möglichst Vierer, sonst Dreier; ein Fünfer nur, wenn es nicht anders geht (5 Spieler)."""
    if n < 3:
        return []
    k = -(-n // 4)
    while k > 1 and n // k < 3:
        k -= 1
    base, extra = divmod(n, k)
    return [base + 1] * extra + [base] * (k - extra)


def gn_pair(active, met, tries=400, rnd=None):
    """Gemischte Gruppen: viele zufällige Aufteilungen, gewählt wird die mit den wenigsten Wiederholungen bereits erlebter Paarungen."""
    import random
    rnd = rnd or random.Random()
    sizes = gn_pod_sizes(len(active))
    best, best_cost = None, None
    for _ in range(tries):
        order = active[:]
        rnd.shuffle(order)
        pods, i = [], 0
        for s in sizes:
            pods.append(sorted(order[i:i + s]))
            i += s
        cost = sum(met.get((a, b), 0) ** 2 for pod in pods for x, a in enumerate(pod) for b in pod[x + 1:])
        if best_cost is None or cost < best_cost:
            best, best_cost = pods, cost
            if cost == 0:
                break
    return best or [], best_cost or 0


def gn_get_night(con, nid=None, uid=0, code=None):
    gn_tables(con)
    if code:
        r = con.execute("SELECT id, owner, name, season, code, created, closed, log FROM gn_nights WHERE code = ?", (code.upper(),)).fetchone()
    else:
        r = con.execute("SELECT id, owner, name, season, code, created, closed, log FROM gn_nights WHERE id = ? AND owner = ?", (nid, uid)).fetchone()
    return dict(zip(("id", "owner", "name", "season", "code", "created", "closed", "log"), r)) if r else None


def gn_standings(con, night_ids):
    """Rangliste nach Siegen (danach Siegquote, dann weniger Partien)."""
    if not night_ids:
        return []
    q = ",".join("?" * len(night_ids))
    names = {(n, i): nm for n, i, nm in con.execute(f"SELECT night, idx, name FROM gn_players WHERE night IN ({q})", night_ids)}
    tab = {}
    for night, seats, w in con.execute(f"SELECT night, seats, winner FROM gn_pods WHERE night IN ({q}) AND winner IS NOT NULL", night_ids):
        for s in json.loads(seats):
            nm = names.get((night, s), f"Spieler {s + 1}")
            e = tab.setdefault(nm.casefold(), {"name": nm, "wins": 0, "games": 0, "draws": 0})
            e["games"] += 1
            e["wins"] += int(w == s)
            e["draws"] += int(w == -1)
    out = sorted(tab.values(), key=lambda e: (-e["wins"], -(e["wins"] / e["games"]), e["games"], e["name"].casefold()))
    rank, prev = 0, None
    for i, e in enumerate(out):
        e["rate"] = round(100 * e["wins"] / e["games"])
        key = (e["wins"], e["rate"])
        if key != prev:
            rank, prev = i + 1, key
        e["rank"] = rank
    return out


def gn_view(con, night, full=True):
    players = [dict(zip(("idx", "name", "deck", "active"), r)) for r in
               con.execute("SELECT idx, name, deck, active FROM gn_players WHERE night = ? ORDER BY idx", (night["id"],))]
    pods = [dict(zip(("id", "round", "tab", "seats", "winner", "reported"), r)) for r in
            con.execute("SELECT id, round, tab, seats, winner, reported FROM gn_pods WHERE night = ? ORDER BY round, tab", (night["id"],))]
    for p in pods:
        p["seats"] = json.loads(p["seats"])
    rounds = {}
    for p in pods:
        rounds.setdefault(p["round"], []).append(p)
    out = {"night": {k: night[k] for k in ("id", "name", "season", "code", "created", "closed", "log")}, "players": players,
           "rounds": [{"round": r, "pods": ps} for r, ps in sorted(rounds.items())], "standings": gn_standings(con, [night["id"]])}
    if night["season"]:
        ids = [i for (i,) in con.execute("SELECT id FROM gn_nights WHERE owner = ? AND season = ?", (night["owner"], night["season"]))]
        out["season"] = {"name": night["season"], "nights": len(ids), "standings": gn_standings(con, ids)}
    if not full:
        out["night"].pop("log", None)
    return out


def gn_sync_game(con, night, pod_id):
    """Ergebnis eines Tisches ins Spielprotokoll übernehmen (oder dort zurücknehmen)."""
    games_table(con)
    pod = con.execute("SELECT round, tab, seats, winner, game_id FROM gn_pods WHERE id = ?", (pod_id,)).fetchone()
    if not pod:
        return
    rnd, tab, seats, w, gid = pod
    if gid:
        con.execute("DELETE FROM games WHERE id = ? AND owner = ?", (gid, night["owner"]))
        con.execute("UPDATE gn_pods SET game_id = NULL WHERE id = ?", (pod_id,))
    if w is None or not night["log"]:
        return
    seats = json.loads(seats)
    pl = {i: (n, d) for i, n, d in con.execute("SELECT idx, name, deck FROM gn_players WHERE night = ?", (night["id"],))}
    players = [{"name": pl.get(s, (f"Spieler {s + 1}", ""))[0], "deck": pl.get(s, ("", ""))[1]} for s in seats]
    winner = seats.index(w) if w in seats else -1
    now = datetime.datetime.now().isoformat(sep=" ", timespec="minutes")
    cur = con.execute("INSERT INTO games(owner, played_at, players, winner, turns, note, source) VALUES(?,?,?,?,?,?,?)",
                      (night["owner"], now, json.dumps(players, ensure_ascii=False), winner, 0,
                       f"Spielabend {night['name']}, Runde {rnd}, Tisch {tab}", "spielabend"))
    con.execute("UPDATE gn_pods SET game_id = ? WHERE id = ?", (cur.lastrowid, pod_id))


def gn_api(path, p, uid=0):
    """Alle Spielabend-Aufrufe. Über den Code (gn_view/gn_report) auch ohne Anmeldung – für Mitspieler am Tisch."""
    import secrets as _sec
    g = lambda k: (p.get(k) or [""])[0].strip()
    con = db()
    gn_tables(con)
    now = datetime.datetime.now().isoformat(sep=" ", timespec="minutes")
    if path == "/api/gn_view":
        night = gn_get_night(con, code=g("code"))
        if not night:
            return {"error": "Unbekannter Spielabend. Bitte den Link prüfen."}
        out = gn_view(con, night, full=False)
        out["night"].pop("id", None)
        return out
    if path == "/api/gn_report":
        night = gn_get_night(con, code=g("code")) if g("code") else gn_get_night(con, int(g("id") or 0), uid)
        if not night:
            return {"error": "Unbekannter Spielabend."}
        if night["closed"]:
            return {"error": "Dieser Spielabend ist abgeschlossen."}
        pod = con.execute("SELECT id, seats FROM gn_pods WHERE id = ? AND night = ?", (int(g("pod") or 0), night["id"])).fetchone()
        if not pod:
            return {"error": "Unbekannter Tisch."}
        w = g("winner")
        win = None if w in ("", "none") else int(w)
        if win is not None and win != -1 and win not in json.loads(pod[1]):
            return {"error": "Dieser Spieler sitzt nicht an dem Tisch."}
        con.execute("UPDATE gn_pods SET winner = ?, reported = ? WHERE id = ?", (win, now if win is not None else None, pod[0]))
        if g("fromtable") == "1":  # vom Lebenszähler gemeldet: die Partie steht dort schon im Spielprotokoll
            con.execute("UPDATE gn_pods SET game_id = NULL WHERE id = ?", (pod[0],))
        else:
            gn_sync_game(con, night, pod[0])
        con.commit()
        out = gn_view(con, night, full=not g("code"))
        if g("code"):
            out["night"].pop("id", None)
        return out
    if path == "/api/gn_list":
        nights = [dict(zip(("id", "name", "season", "code", "created", "closed"), r)) for r in
                  con.execute("SELECT id, name, season, code, created, closed FROM gn_nights WHERE owner = ? ORDER BY id DESC", (uid,))]
        for n in nights:
            n["players"] = con.execute("SELECT count(*) FROM gn_players WHERE night = ? AND active = 1", (n["id"],)).fetchone()[0]
            n["rounds"] = con.execute("SELECT count(DISTINCT round) FROM gn_pods WHERE night = ?", (n["id"],)).fetchone()[0]
        seasons = sorted({n["season"] for n in nights if n["season"]})
        known = [r[0] for r in con.execute("SELECT DISTINCT p.name FROM gn_players p JOIN gn_nights n ON n.id = p.night WHERE n.owner = ? "
                                            "ORDER BY p.name COLLATE NOCASE", (uid,))]
        out = {"nights": nights, "seasons": seasons, "known": known}
        if g("season"):
            ids = [n["id"] for n in nights if n["season"] == g("season")]
            out["season"] = {"name": g("season"), "nights": len(ids), "standings": gn_standings(con, ids)}
        out["all"] = gn_standings(con, [n["id"] for n in nights])
        return out
    if path == "/api/gn_create":
        try:
            names = [str(x).strip()[:40] for x in json.loads(g("players") or "[]") if str(x).strip()]
        except ValueError:
            return {"error": "Ungültige Spielerliste."}
        seen, uniq = set(), []
        for n in names:
            if n.casefold() not in seen:
                seen.add(n.casefold())
                uniq.append(n)
        if len(uniq) < 3:
            return {"error": "Für einen Spielabend braucht es mindestens 3 Spieler."}
        code = "".join(_sec.choice(GN_CODE_CHARS) for _ in range(6))
        cur = con.execute("INSERT INTO gn_nights(owner, name, season, code, created, log) VALUES(?,?,?,?,?,?)",
                          (uid, (g("name") or f"Spielabend {now[:10]}")[:60], g("season")[:40], code, now, 0 if g("log") == "0" else 1))
        con.executemany("INSERT INTO gn_players(night, idx, name) VALUES(?,?,?)", [(cur.lastrowid, i, n) for i, n in enumerate(uniq[:64])])
        con.commit()
        return gn_view(con, gn_get_night(con, cur.lastrowid, uid))
    night = gn_get_night(con, int(g("id") or 0), uid)
    if not night:
        return {"error": "Unbekannter Spielabend."}
    if path == "/api/gn_get":
        return gn_view(con, night)
    if path == "/api/gn_player":
        idx = g("idx")
        if idx == "":
            name = g("name")[:40]
            if not name:
                return {"error": "Name fehlt."}
            if con.execute("SELECT 1 FROM gn_players WHERE night = ? AND name = ? COLLATE NOCASE", (night["id"], name)).fetchone():
                con.execute("UPDATE gn_players SET active = 1 WHERE night = ? AND name = ? COLLATE NOCASE", (night["id"], name))
            else:
                nxt = con.execute("SELECT coalesce(max(idx), -1) + 1 FROM gn_players WHERE night = ?", (night["id"],)).fetchone()[0]
                con.execute("INSERT INTO gn_players(night, idx, name) VALUES(?,?,?)", (night["id"], nxt, name))
        else:
            sets, args = [], []
            if "active" in p:
                sets.append("active = ?"); args.append(1 if g("active") == "1" else 0)
            if "deck" in p:
                sets.append("deck = ?"); args.append(g("deck")[:80])
            if "name" in p and g("name"):
                sets.append("name = ?"); args.append(g("name")[:40])
            if sets:
                con.execute(f"UPDATE gn_players SET {', '.join(sets)} WHERE night = ? AND idx = ?", (*args, night["id"], int(idx)))
        con.commit()
        return gn_view(con, night)
    if path == "/api/gn_round":
        last = con.execute("SELECT max(round) FROM gn_pods WHERE night = ?", (night["id"],)).fetchone()[0] or 0
        if last and con.execute("SELECT 1 FROM gn_pods WHERE night = ? AND round = ? AND winner IS NULL", (night["id"], last)).fetchone() \
                and g("force") != "1":
            return dict(gn_view(con, night), warn="In Runde %d sind noch Tische offen. Trotzdem neu auslosen?" % last)
        active = [i for (i,) in con.execute("SELECT idx FROM gn_players WHERE night = ? AND active = 1 ORDER BY idx", (night["id"],))]
        if len(active) < 3:
            return {"error": "Es braucht mindestens 3 anwesende Spieler."}
        met = {}
        for (seats,) in con.execute("SELECT seats FROM gn_pods WHERE night = ?", (night["id"],)):
            s = sorted(json.loads(seats))
            for x, a in enumerate(s):
                for b in s[x + 1:]:
                    met[(a, b)] = met.get((a, b), 0) + 1
        pods, cost = gn_pair(active, met)
        for t, pod in enumerate(pods, 1):
            con.execute("INSERT INTO gn_pods(night, round, tab, seats) VALUES(?,?,?,?)", (night["id"], last + 1, t, json.dumps(pod)))
        con.commit()
        out = gn_view(con, night)
        out["repeats"] = cost
        return out
    if path == "/api/gn_round_delete":
        last = con.execute("SELECT max(round) FROM gn_pods WHERE night = ?", (night["id"],)).fetchone()[0]
        if last:
            for (pid,) in con.execute("SELECT id FROM gn_pods WHERE night = ? AND round = ?", (night["id"], last)).fetchall():
                con.execute("UPDATE gn_pods SET winner = NULL WHERE id = ?", (pid,))
                gn_sync_game(con, night, pid)
            con.execute("DELETE FROM gn_pods WHERE night = ? AND round = ?", (night["id"], last))
            con.commit()
        return gn_view(con, night)
    if path == "/api/gn_set":
        if "name" in p and g("name"):
            con.execute("UPDATE gn_nights SET name = ? WHERE id = ?", (g("name")[:60], night["id"]))
        if "season" in p:
            con.execute("UPDATE gn_nights SET season = ? WHERE id = ?", (g("season")[:40], night["id"]))
        if "closed" in p:
            con.execute("UPDATE gn_nights SET closed = ? WHERE id = ?", (1 if g("closed") == "1" else 0, night["id"]))
        con.commit()
        return gn_view(con, gn_get_night(con, night["id"], uid))
    if path == "/api/gn_delete":
        for (pid,) in con.execute("SELECT id FROM gn_pods WHERE night = ?", (night["id"],)).fetchall():
            con.execute("UPDATE gn_pods SET winner = NULL WHERE id = ?", (pid,))
            gn_sync_game(con, night, pid)
        for t in ("gn_pods", "gn_players"):
            con.execute(f"DELETE FROM {t} WHERE night = ?", (night["id"],))
        con.execute("DELETE FROM gn_nights WHERE id = ?", (night["id"],))
        con.commit()
        return {"ok": True}
    return {"error": "Unbekannte Aktion."}


GN_PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1">
<title>Spielabend · Manaschmiede</title><meta name=robots content=noindex><link rel=icon href=/icon-192.png>
<style>body{margin:0;background:#140f0b radial-gradient(ellipse at top,#3a2a1c,#0e0a07) fixed;color:#eadfc8;font-family:Georgia,serif;padding:12px}
h1{color:#e2bd5b;font-size:22px;margin:4px 0}h2{font-size:17px;color:#e2bd5b;margin:18px 0 6px}.pod{background:#221811;border:1px solid #7a5c2e;border-radius:10px;padding:10px;margin:8px 0}
.pod b{color:#e2bd5b}button{font:inherit;font-size:16px;padding:10px 12px;margin:4px 4px 0 0;border-radius:8px;border:1px solid #a8843a;background:#2a2018;color:#eadfc8;min-width:44px}
button.win{background:linear-gradient(#f1d27a,#b8891f);color:#1b140e;font-weight:bold}table{border-collapse:collapse;width:100%;max-width:520px}td,th{padding:6px 8px;border-bottom:1px solid #fff2;text-align:left}
td.r,th.r{text-align:right}.hint{opacity:.75;font-size:14px}.err{color:#ff8a72}footer{margin-top:30px;font-size:13px;opacity:.7}a{color:#e2bd5b}#gnwrap{margin-top:14px;border:1px solid #a8843a77;border-radius:10px;padding:8px 12px}#gnwrap>summary{cursor:pointer;font-size:1.1em}
#gnbox .gnst{border-collapse:collapse;margin:6px 0}#gnbox .gnst td,#gnbox .gnst th{padding:4px 10px;border-bottom:1px solid #fff2;text-align:left}
#gnbox .gnpod{margin:6px 0;padding:8px;border:1px solid #7a5c2e55;border-radius:8px}#gnbox .gnpod button{margin:3px}#gnbox button.gnwin{background:linear-gradient(#f1d27a,#b8891f);color:#1b140e;font-weight:bold}
#gnbox .gnqr{width:180px;background:#fff;border-radius:6px;margin:6px 0}#gnbox .gnp{margin:3px 0}#gnbox .gnhead{font-size:1.15em;margin:6px 0}
#labwrap{margin-top:14px}#labwrap .labvar{margin:3px 0}#labwrap progress{width:260px;vertical-align:middle}#labwrap .labrun{margin:4px 0}#labres td.w{background:#e3f1e3;font-weight:bold}#labres td.l{color:#b5432f}
#buybox .buysum div{margin:2px 0}#buytab tr.buyover td{background:#f9eeda55}#buytab tr.buyskip td{opacity:.45;text-decoration:line-through}#buytab td div{font-size:12px;opacity:.75}#buybox .buypc{margin:6px 0}
</style>
<h1 id=t>Spielabend</h1><div class=hint id=s></div><div id=m class=err></div><div id=r></div><h2>Rangliste</h2><table id=st></table><div id=se></div>
<footer>Manaschmiede · <a href=/impressum>Impressum</a> · <a href=/datenschutz>Datenschutz</a></footer>
<script>const code=location.pathname.split('/').pop();let D=null;
const E=(t,x)=>{const e=document.createElement(t);if(x!=null)e.textContent=x;return e};
async function J(u,b){const r=await fetch(u,b?{method:'POST',body:new URLSearchParams(b)}:{});return r.json()}
function stand(tab,rows){tab.innerHTML='';const h=tab.insertRow();['Platz','Spieler','Siege','Partien'].forEach((x,i)=>{const th=E('th',x);if(i>1)th.className='r';h.append(th)});
 rows.forEach(e=>{const tr=tab.insertRow();[e.rank+'.',e.name,e.wins,e.games].forEach((v,i)=>{const c=tr.insertCell();c.textContent=v;if(i>1)c.className='r'})})}
function draw(d){if(d.error){document.getElementById('m').textContent=d.error;return}D=d;document.getElementById('m').textContent='';
 document.getElementById('t').textContent='🏆 '+d.night.name;document.getElementById('s').textContent=(d.night.season?'Saison '+d.night.season+' · ':'')+d.players.filter(p=>p.active).length+' Spieler'+(d.night.closed?' · abgeschlossen':'');
 const nm={};d.players.forEach(p=>nm[p.idx]=p.name);const r=document.getElementById('r');r.innerHTML='';
 const last=d.rounds[d.rounds.length-1];if(!last){r.append(E('p','Noch keine Runde ausgelost.'));}
 else{r.append(E('h2','Runde '+last.round));last.pods.forEach(p=>{const box=E('div');box.className='pod';box.append(E('b','Tisch '+p.tab+' '),E('span',p.winner==null?'– Sieger antippen':(p.winner==-1?'– Unentschieden':'– Sieg: '+nm[p.winner])));box.append(E('br'));
  p.seats.forEach(s=>{const b=E('button',(p.winner==s?'👑 ':'')+nm[s]);if(p.winner==s)b.className='win';b.disabled=!!d.night.closed;b.onclick=()=>rep(p.id,p.winner==s?'none':s);box.append(b)});
  const dr=E('button','Unentschieden');if(p.winner==-1)dr.className='win';dr.disabled=!!d.night.closed;dr.onclick=()=>rep(p.id,p.winner==-1?'none':-1);box.append(dr);r.append(box)})}
 stand(document.getElementById('st'),d.standings);const se=document.getElementById('se');se.innerHTML='';
 if(d.season){se.append(E('h2','Saison '+d.season.name+' ('+d.season.nights+' Abende)'));const t=E('table');se.append(t);stand(t,d.season.standings)}}
async function rep(pod,w){draw(await J('/api/gn_report',{code,pod,winner:w}))}
async function load(){draw(await J('/api/gn_view?code='+encodeURIComponent(code)))}load();setInterval(load,10000);</script>"""


# ---------------------------------------------------------------- Impressum und Datenschutzerklärung (Server-Betrieb)
LEGAL_KEYS = ("legal_name", "legal_addr", "legal_mail", "legal_phone", "legal_extra", "legal_host")


def legal_get():
    return {k: setting(k) or "" for k in LEGAL_KEYS}


def legal_save(p):
    for k in LEGAL_KEYS:
        if k in p:
            setting(k, (p.get(k) or [""])[0].strip()[:2000])
    return legal_get()


def legal_page(kind):
    import html as _h
    L = legal_get()
    e = lambda s: _h.escape(s or "").replace("\n", "<br>")
    missing = not (L["legal_name"] and L["legal_addr"] and L["legal_mail"])
    who = (f"<p>{e(L['legal_name'])}<br>{e(L['legal_addr'])}</p><p>E-Mail: <a href='mailto:{e(L['legal_mail'])}'>{e(L['legal_mail'])}</a>"
           + (f"<br>Telefon: {e(L['legal_phone'])}" if L["legal_phone"] else "") + "</p>")
    warn = ("<p style='color:#ff8a72'><b>Hinweis an den Betreiber:</b> Name, Anschrift und E-Mail fehlen noch. "
            "Bitte als Administrator unter „Impressum &amp; Datenschutz“ eintragen.</p>") if missing else ""
    if kind == "impressum":
        body = (f"<h1>Impressum</h1>{warn}<h2>Angaben gemäß § 5 DDG</h2>{who}"
                + (f"<p>{e(L['legal_extra'])}</p>" if L["legal_extra"] else "")
                + "<h2>Verantwortlich für den Inhalt</h2><p>Siehe oben.</p>"
                "<h2>Hinweis</h2><p>Die Manaschmiede ist ein privates, nicht kommerzielles Fan-Projekt und steht in keiner Verbindung zu Wizards of the Coast. "
                "Magic: The Gathering, Kartennamen, Kartenbilder und Symbole sind Eigentum von Wizards of the Coast LLC.</p>")
    else:
        host = e(L["legal_host"]) or "dem Server des Betreibers"
        body = (f"<h1>Datenschutzerklärung</h1>{warn}"
                f"<h2>1. Verantwortlicher</h2>{who}"
                "<h2>2. Welche Daten verarbeitet werden</h2><ul>"
                "<li><b>Benutzerkonto:</b> Benutzername und Passwort (nur als Prüfwert mit Salt gespeichert, nie im Klartext), Rolle, Datum der Anlage.</li>"
                "<li><b>Inhalte, die du anlegst:</b> Decks, Sammlung, Wunschliste, Ordner, Spielprotokoll, Spielabende mit den Namen der Mitspieler, "
                "Kommentare und Bewertungen in der Deck-Galerie, Einstellungen.</li>"
                "<li><b>Anmeldung:</b> ein Sitzungs-Cookie (cdbsess), technisch notwendig, um angemeldet zu bleiben (§ 25 Abs. 2 Nr. 2 TDDDG). "
                "Zum Schutz vor dem Erraten von Passwörtern wird die IP-Adresse bei fehlgeschlagenen Anmeldungen kurzzeitig im Arbeitsspeicher gehalten.</li>"
                "<li><b>Lokale Speicherung im Browser:</b> Ansichtseinstellungen und laufende Testpartien (localStorage); diese verlassen dein Gerät nicht.</li>"
                "<li><b>Spielabend-Links:</b> Wer den Link oder QR-Code eines Spielabends hat, sieht die Namen der Mitspieler, die Tische und die Rangliste "
                "und kann Ergebnisse eintragen.</li></ul>"
                "<h2>3. Zweck und Rechtsgrundlage</h2><p>Bereitstellung der Funktionen, die du nutzt (Art. 6 Abs. 1 lit. b DSGVO), "
                "Sicherheit des Dienstes (Art. 6 Abs. 1 lit. f DSGVO). Namen von Mitspielern werden nur für den Spielabend und das Spielprotokoll verwendet "
                "(Art. 6 Abs. 1 lit. f DSGVO; berechtigtes Interesse an der Organisation gemeinsamer Spielabende).</p>"
                f"<h2>4. Hosting</h2><p>Die Daten liegen auf {host}. Es werden keine Analyse- oder Werbedienste eingesetzt.</p>"
                "<h2>5. Dienste Dritter</h2><ul>"
                "<li><b>Scryfall (Scryfall, LLC, USA):</b> Kartenbilder werden direkt von den Servern von Scryfall geladen; dabei erhält Scryfall deine IP-Adresse "
                "und Browserdaten. Kartendaten ruft der Server ohne personenbezogene Daten ab.</li>"
                "<li><b>Commander Spellbook, Cardmarket, MTGJSON:</b> Abrufe erfolgen durch den Server ohne personenbezogene Daten.</li>"
                "<li><b>Links zu Händlern</b> (Cardmarket, Trader-online, cardcosmos): erst beim Anklicken werden Daten an den Händler übertragen; "
                "es gelten dessen Datenschutzbestimmungen.</li></ul>"
                "<h2>6. Speicherdauer</h2><p>Solange dein Konto besteht. Beim Löschen des Kontos werden Decks, Sammlung, Spielprotokoll und "
                "Spielabende mitgelöscht. Sitzungen laufen nach Ablauf der Gültigkeit oder beim Abmelden ab.</p>"
                "<h2>7. Deine Rechte</h2><p>Auskunft (Art. 15), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung (Art. 18), "
                "Datenübertragbarkeit (Art. 20) und Widerspruch (Art. 21 DSGVO). Wende dich dafür an die oben genannte Adresse. "
                "Du hast außerdem das Recht auf Beschwerde bei einer Datenschutz-Aufsichtsbehörde.</p>"
                + (f"<h2>8. Weitere Angaben</h2><p>{e(L['legal_extra'])}</p>" if L["legal_extra"] else ""))
    return ("<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width, initial-scale=1'>"
            f"<title>{'Impressum' if kind == 'impressum' else 'Datenschutz'} · Manaschmiede</title>"
            "<style>body{margin:0 auto;max-width:760px;padding:16px;background:#140f0b;color:#eadfc8;font-family:Georgia,serif;line-height:1.5}"
            "h1,h2{color:#e2bd5b}a{color:#e2bd5b}li{margin:4px 0}</style>" + body +
            "<p style='margin-top:30px;opacity:.7'><a href='/'>Zur Manaschmiede</a> · <a href='/impressum'>Impressum</a> · <a href='/datenschutz'>Datenschutz</a></p>")


LOGIN_PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1">
<title>Anmelden · Manaschmiede</title><link rel=manifest href=/manifest.webmanifest><meta name=theme-color content="#1a130e">
<link rel=icon href=/icon-192.png><style>body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
background:#140f0b radial-gradient(ellipse at top,#3a2a1c,#0e0a07);color:#eadfc8;font-family:Georgia,serif}
form{background:#221811;border:1px solid #a8843a;border-radius:10px;padding:26px 30px;width:300px;box-shadow:0 0 24px #0009}
h1{font-size:22px;color:#e2bd5b;text-align:center;margin:0 0 18px}input{width:100%;box-sizing:border-box;padding:9px;margin:6px 0 12px;
background:#140f0b;color:#f3e8cf;border:1px solid #7a5c2e;border-radius:5px;font-size:16px}
button{width:100%;padding:10px;background:linear-gradient(#f1d27a,#b8891f);border:0;border-radius:5px;font-weight:bold;font-size:16px;cursor:pointer}
#m{color:#ff8a72;min-height:20px;font-size:14px}</style>
<form id=f><h1>✦ Manaschmiede ✦</h1><p style="text-align:center;margin-top:-8px;opacity:.8">Commander-Deckbau</p><label>Benutzername<input name=name autocomplete=username required autofocus></label>
<label>Passwort<input name=pw type=password autocomplete=current-password required></label><div id=m></div><button>Anmelden</button>
<p style="text-align:center;font-size:13px;opacity:.75;margin:14px 0 0"><a href=/impressum style="color:#e2bd5b">Impressum</a> · <a href=/datenschutz style="color:#e2bd5b">Datenschutz</a></p></form>
<script>f.onsubmit=async e=>{e.preventDefault();m.textContent='';const r=await fetch('/api/login',{method:'POST',body:new URLSearchParams(new FormData(f))});
const j=await r.json();if(j.ok)location.href='/';else m.textContent=j.error||'Anmeldung fehlgeschlagen.'};
if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js').catch(()=>{});</script>"""

OFFLINE_PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1"><title>Offline</title>
<body style="background:#140f0b;color:#eadfc8;font-family:Georgia,serif;text-align:center;padding:60px 20px">
<h2 style="color:#e2bd5b">Keine Verbindung zum Server</h2><p>Bitte Internetverbindung prüfen und erneut versuchen.</p>
<button onclick="location.reload()" style="padding:10px 20px;font-size:16px">Erneut versuchen</button></body>"""

SW_JS = """const V='cdb-%s';
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(['/offline','/icon-192.png'])));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!=V).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{if(e.request.mode==='navigate')e.respondWith(fetch(e.request).catch(()=>caches.match('/offline')))});
"""


def manifest():
    return {"name": "Manaschmiede: Commander-Deckbau", "short_name": "Manaschmiede", "start_url": "/", "scope": "/",
            "display": "standalone", "background_color": "#140f0b", "theme_color": "#1a130e", "lang": "de",
            "description": "Commander-Decks bauen, vergleichen, Combos finden und per Forge gegeneinander spielen lassen.",
            "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                      {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
                      {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}


ICONS = {}


def app_icon(size, maskable=False):
    """App-Symbol ohne Bilddateien: goldene Raute mit Kartenumriss auf dunklem Grund (eigenes Motiv)."""
    key = (size, maskable)
    if key in ICONS:
        return ICONS[key]
    rows = []
    c = size / 2
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            dx, dy = (x + .5 - c) / c, (y + .5 - c) / c
            r = (dx * dx + dy * dy) ** .5
            if not maskable and r > .96:
                row += bytes((0, 0, 0, 0)); continue
            t = min(1, r)
            bg = (int(58 - 38 * t), int(42 - 28 * t), int(28 - 18 * t))
            px = bg
            s_ = .62 if not maskable else .5
            card = abs(dx) < .40 * s_ / .62 and abs(dy) < .56 * s_ / .62
            border = card and (abs(dx) > .34 * s_ / .62 or abs(dy) > .50 * s_ / .62)
            diamond = abs(dx) / (.22 * s_ / .62) + abs(dy) / (.32 * s_ / .62) < 1
            if border:
                px = (226, 189, 91)
            elif diamond:
                g = 1 - (abs(dx) + abs(dy)) * .9
                px = (int(200 + 41 * g), int(150 + 60 * g), int(50 + 60 * g))
            elif card:
                px = (40, 28, 18)
            row += bytes((*px, 255))
        rows.append(bytes(row))
    raw = zlib.compress(b"".join(rows), 9)
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)) +
           chunk(b"IDAT", raw) + chunk(b"IEND", b""))
    ICONS[key] = png
    return png

# ---------------------------------------------------------------- Eigene Decks: Import und Speicher
SKIP_SECTIONS = re.compile(r"^(side ?board|maybe ?board|considering|tokens?|acquire ?board|wishlist|companion|about|name .*)$", re.I)
CMD_SECTION = re.compile(r"^(commanders?|commander zone|general|kommandeur)$", re.I)
MAIN_SECTION = re.compile(r"^(deck|main ?(board|deck)?|library|mainboard|spells|creatures?|lands?|"
                          r"artifacts?|enchantments?|instants?|sorcer(y|ies)|planeswalkers?|battles?|other)( \(\d+\))?$", re.I)
SET_TAIL = re.compile(r"\s+\(([A-Za-z0-9]{2,6})\)(\s+[\w★\-]+)?\s*$")


def clean_line(line):
    """Eine Kartenzeile aus Moxfield, Archidekt, Arena, MTGO, TappedOut, Deckstats oder Forge -> (Anzahl, Name, Markierungen)."""
    tags = set()
    t = line.strip()
    if re.match(r"^SB:\s*", t, re.I):
        tags.add("side")
        t = re.sub(r"^SB:\s*", "", t, flags=re.I)
    for cat in re.findall(r"\[([^\]]*)\]", t):  # Archidekt-Kategorien „[Commander{top}]“, „[Maybeboard{noDeck}]“
        cl = cat.lower()
        if "commander" in cl:
            tags.add("cmd")
        if "nodeck" in cl or "maybe" in cl or "sideboard" in cl:
            tags.add("side")
    t = re.sub(r"\[[^\]]*\]", "", t)
    if re.search(r"\*cmdr\*|!commander|#\s*commander", t, re.I):
        tags.add("cmd")
    t = re.sub(r"\s+#.*$", "", t)                     # Deckstats-Kommentare
    t = re.sub(r"\*[A-Za-z]+\*", "", t)               # *F*, *E*, *CMDR*
    t = t.split("|")[0]                                # Forge: „1 Sol Ring|CMR|1“
    mt = re.match(r"^(\d+)\s*x?\s+(.+)$", t.strip(), re.I)
    qty, name = (int(mt.group(1)), mt.group(2)) if mt else (1, t.strip())
    name = SET_TAIL.sub("", name).strip()
    name = re.sub(r"\s+/{1,2}\s+", " // ", name)       # „Vorderseite / Rückseite“
    return qty, name, tags


def section_of(head):
    h = head.strip().rstrip(":").strip()
    if CMD_SECTION.match(h):
        return "cmd"
    if re.match(r"^side ?board", h, re.I):
        return "side"
    if h.lower() == "about":
        return "about"
    if h.lower() == "metadata" or SKIP_SECTIONS.match(h):
        return "skip"
    if MAIN_SECTION.match(h):
        return "main"
    return None


def parse_text(text):
    """Liefert (Deckname, [(Anzahl, Name, ist_Commander)], Blöcke, Sideboard-Namen) aus Text- oder Forge-Formaten."""
    name, out, blocks, side, section, cur = "", [], [], [], "main", []
    for raw in text.splitlines():
        line = raw.strip().lstrip("\ufeff")
        if not line:
            if cur:
                blocks.append(cur)
                cur = []
            continue
        if re.match(r"^name\s*=", line, re.I):
            name = line.split("=", 1)[1].strip()
            continue
        if section == "about" and line.lower().startswith("name "):
            name = line[5:].strip()
            continue
        bm = re.match(r"^\[(.+)\]$", line)
        cm = re.match(r"^(//+|#+)\s*(.*)$", line)
        if bm or cm:
            sec = section_of(bm.group(1) if bm else cm.group(2))
            if sec:
                section = sec
            elif bm:
                section = "main"
            continue
        if not re.match(r"^(SB:\s*)?\d", line, re.I):
            sec = section_of(line)
            if sec:
                section = sec
                continue
        if section in ("skip", "about"):
            continue
        q, n, tags = clean_line(line)
        if not n:
            continue
        if section == "side" or ("side" in tags and "cmd" not in tags):
            side.append(n)
            continue
        out.append((q, n, section == "cmd" or "cmd" in tags))
        cur.append(len(out) - 1)
    if cur:
        blocks.append(cur)
    return name, out, blocks, side


def parse_csv(text):
    rd = list(csv.reader(io.StringIO(text)))
    if len(rd) < 2:
        return None
    hd = [h.strip().lower() for h in rd[0]]
    ni = next((i for i, h in enumerate(hd) if h in ("name", "card name", "card", "card_name")), None)
    if ni is None:
        return None
    qi = next((i for i, h in enumerate(hd) if h in ("count", "quantity", "qty", "amount", "anzahl")), None)
    ci = next((i for i, h in enumerate(hd) if h in ("categories", "category", "board", "section", "tags")), None)
    out = []
    for row in rd[1:]:
        if len(row) <= ni or not row[ni].strip():
            continue
        cat = row[ci].lower() if ci is not None and len(row) > ci else ""
        if any(w in cat for w in ("maybe", "sideboard", "nodeck", "considering", "token")):
            continue
        q = int(re.sub(r"\D", "", row[qi]) or 1) if qi is not None and len(row) > qi else 1
        out.append((q, row[ni].strip(), "commander" in cat))
    return out


def parse_json(data):
    """Moxfield- (v2/v3) und Archidekt-JSON -> (Name, [(Anzahl, Name, ist_Commander)])."""
    out = []
    if "boards" in data or "mainboard" in data:  # Moxfield
        boards = data.get("boards") or {k: {"cards": data.get(k) or {}} for k in ("commanders", "mainboard", "companions")}
        for b in ("commanders", "mainboard"):
            for c in ((boards.get(b) or {}).get("cards") or {}).values():
                out.append((c.get("quantity", 1), c["card"]["name"], b == "commanders"))
        return data.get("name", ""), out
    if "cards" in data and isinstance(data["cards"], list):  # Archidekt
        off = {c["name"] for c in data.get("categories") or [] if not c.get("includedInDeck", True)}
        for c in data["cards"]:
            cats = set(c.get("categories") or [])
            if cats & off or any(x.lower().startswith(("maybe", "sideboard")) for x in cats):
                continue
            card = c.get("card") or {}
            n = (card.get("oracleCard") or {}).get("name") or card.get("name")
            if n:
                out.append((c.get("quantity", 1), n, "Commander" in cats))
        return data.get("name", ""), out
    raise ValueError("Unbekanntes JSON-Format (unterstützt: Moxfield, Archidekt).")


def http_get(url, accept="*/*"):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 CommanderDeckDB/0.7", "Accept": accept})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def fetch_deck_url(url):
    """Holt eine Deckliste von bekannten Seiten. Liefert ("json", dict) oder ("text", str)."""
    u = url.strip()
    m = re.search(r"/d/([A-Za-z0-9_-]{8,40})(?:\.txt)?/?(?:[?#].*)?$", u)
    if m:  # Link auf ein geteiltes Deck einer Manaschmiede: zuerst hier suchen, sonst (nicht auf dem Server) dort abholen
        t = shared_text(m.group(1))
        if t:
            return "text", t
        if SERVER:
            raise RuntimeError("Dieses geteilte Deck liegt auf einer anderen Manaschmiede. Dort „Text kopieren“ und hier einfügen.")
        return "text", http_get(u.split("?")[0].split("#")[0].rstrip("/").removesuffix(".txt") + ".txt")
    m = re.search(r"archidekt\.com/(?:api/)?decks/(\d+)", u)
    if m:
        return "json", json.loads(http_get(f"https://archidekt.com/api/decks/{m.group(1)}/", "application/json"))
    m = re.search(r"moxfield\.com/decks/([\w-]+)", u)
    if m:
        last = None
        for api in (f"https://api2.moxfield.com/v3/decks/all/{m.group(1)}", f"https://api2.moxfield.com/v2/decks/all/{m.group(1)}"):
            try:
                return "json", json.loads(http_get(api, "application/json"))
            except Exception as e:
                last = e
        raise RuntimeError(f"Moxfield blockiert direkte Abfragen oft ({last}). Bitte in Moxfield „Export“ → „Copy for MTGO/Arena“ "
                           "wählen und die Liste hier einfügen.")
    m = re.search(r"mtggoldfish\.com/deck/(?:download/)?(\d+)", u)
    if m:
        return "text", http_get(f"https://www.mtggoldfish.com/deck/download/{m.group(1)}")
    m = re.search(r"tappedout\.net/mtg-decks/([\w-]+)", u)
    if m:
        return "text", http_get(f"https://tappedout.net/mtg-decks/{m.group(1)}/?fmt=txt")
    if re.match(r"https?://(www\.)?deckstats\.net/decks/\d+/", u) is None and "deckstats.net/decks/" in u:
        raise RuntimeError("Ungültiger Deckstats-Link.")
    if "deckstats.net/decks/" in u:
        return "text", http_get(u.split("?")[0] + "?include_comments=1&export_txt=1")
    if SERVER:
        raise RuntimeError("Auf dem Server sind nur Links von Archidekt, Moxfield, MTGGoldfish, TappedOut und Deckstats erlaubt.")
    body = http_get(u)
    if body.lstrip().startswith("{"):
        return "json", json.loads(body)
    if "<html" in body[:500].lower():
        raise RuntimeError("Diese Seite liefert keine Deckliste als Text. Bitte auf der Seite die Exportfunktion nutzen "
                           "und die Liste hier einfügen oder als Datei hochladen.")
    return "text", body


def parse_xml_deck(text):
    """MTGO (.dek) und Cockatrice (.cod) -> (Name, [(Anzahl, Name, ist_Commander)], Sideboard-Namen)."""
    if re.search(r"<!DOCTYPE|<!ENTITY", text, re.I):
        raise ValueError("XML mit DOCTYPE/ENTITY wird aus Sicherheitsgründen nicht gelesen.")
    root = ET.fromstring(text.encode("utf-8"))
    out, side, name = [], [], ""
    if root.tag.lower() == "cockatrice_deck":
        name = (root.findtext("deckname") or "").strip()
        for zone in root.iter("zone"):
            zn = (zone.get("name") or "").lower()
            for c in zone.iter("card"):
                n, q = c.get("name") or "", int(c.get("number") or 1)
                if zn in ("main", "maindeck"):
                    out.append((q, n, False))
                elif zn in ("commander", "command"):
                    out.append((q, n, True))
                else:
                    side.append(n)
        return name, out, side
    for c in root.iter("Cards"):  # MTGO .dek
        n, q = c.get("Name") or "", int(c.get("Quantity") or 1)
        if not n:
            continue
        if (c.get("Sideboard") or "").lower() == "true":
            side.append(n)
        else:
            out.append((q, n, (c.get("Annotation") or "") == "1"))
    if not out and not side:
        raise ValueError("Unbekanntes XML-Format (unterstützt: MTGO .dek, Cockatrice .cod).")
    return name, out, side


def import_deck(p):
    """Erkennt Format und Commander, gleicht alle Namen mit der Datenbank ab."""
    g = lambda k: (p.get(k) or [""])[0]
    text, url, fname = g("text").lstrip("\ufeff"), g("url").strip(), g("filename")
    name, notes = "", []
    try:
        if url:
            kind, data = fetch_deck_url(url)
            if kind == "json":
                name, raw = parse_json(data)
                blocks, side = [], []
            else:
                name, raw, blocks, side = parse_text(data)
        elif text.lstrip().startswith("{"):
            name, raw = parse_json(json.loads(text))
            blocks, side = [], []
        elif text.lstrip().startswith("<"):
            name, raw, side = parse_xml_deck(text.strip())
            blocks = []
        else:
            raw = parse_csv(text) if fname.lower().endswith(".csv") or (
                "," in text.split("\n")[0] and "name" in text.split("\n")[0].lower()) else None
            blocks, side = [], []
            if raw is None:
                name, raw, blocks, side = parse_text(text)
    except Exception as e:
        return {"error": f"Import fehlgeschlagen: {e}"}
    if not raw:
        return {"error": "Keine Karten erkannt. Erwartet wird z. B. „1 Sol Ring“ je Zeile."}
    con = db()
    con.row_factory = sqlite3.Row
    if g("translate") != "0":
        try:
            translate_names(con, [n for _, n, _ in raw])
        except Exception:
            pass
    rows, qty, cmds, missing, fixed = {}, {}, [], [], []
    for i, (q, n, is_cmd) in enumerate(raw):
        r, hint = lookup(con, n)
        if not r:
            missing.append(n)
            continue
        if hint:
            fixed.append(hint)
        if r["name"] not in rows:
            rows[r["name"]], qty[r["name"]] = r, 0
        qty[r["name"]] += q
        if is_cmd and r["name"] not in cmds:
            cmds.append(r["name"])
    can = lambda n: bool(rows[n]["can_be_commander"]) if n in rows else False
    if not cmds:  # MTGO/Moxfield: Commander steht als einzelner Block am Ende oder als Sideboard
        side = [r for r in (lookup(con, x)[0] for x in side) if r]
        side = side if all(r["can_be_commander"] for r in side) else []
        if 1 <= len(side) <= 2:
            for r in side:
                rows.setdefault(r["name"], r)
                qty[r["name"]] = 1
                cmds.append(r["name"])
            notes.append("Commander aus dem Sideboard-Bereich übernommen.")
        else:
            lists = blocks
            for blk in ([lists[-1], lists[0]] if len(lists) > 1 else []):
                ns = list(dict.fromkeys(lookup(con, raw[i][1])[0]["name"] for i in blk if lookup(con, raw[i][1])[0]))
                if 1 <= len(ns) <= 2 and all(can(n) for n in ns):
                    cmds = ns
                    notes.append("Commander aus dem abgesetzten Block der Liste erkannt, bitte prüfen.")
                    break
    candidates = [n for n in rows if can(n)]
    if not cmds and candidates:
        first = lookup(con, raw[0][1])[0]
        if first and first["name"] in candidates:
            cmds = [first["name"]]
            notes.append("Kein Commander markiert. Die erste Karte wurde angenommen, bitte prüfen.")
        else:
            notes.append("Kein Commander markiert. Bitte unten auswählen.")
    total = sum(qty.values())
    if total != 100:
        notes.append(f"Die Liste hat {total} statt 100 Karten.")
    ci = "".join(c for c in ORDER if any(c in rows[n]["color_identity"] for n in cmds)) if cmds else ""
    illegal = [n for n, r in rows.items() if not r["commander_legal"]]
    if illegal:
        notes.append("Nicht Commander-legal: " + ", ".join(illegal))
    if ci or cmds:
        off = [n for n, r in rows.items() if n not in cmds and any(c not in ci for c in r["color_identity"])]
        if off:
            notes.append("Außerhalb der Farbidentität des Commanders: " + ", ".join(off))
    lines = [f"{qty[n]} {n}" for n in cmds] + [f"{qty[n]} {n}" for n in rows if n not in cmds]
    if not name and fname:
        name = re.sub(r"\.\w+$", "", fname)
    name = name or (" + ".join(cmds) if cmds else "Importiertes Deck")
    return {"name": name.strip(), "commander": " + ".join(cmds), "candidates": candidates, "list": "\n".join(lines),
            "count": total, "missing": missing, "fixed": fixed[:20], "notes": notes, "ci": ci}


def decks_table(con):
    """Decks gehören einem Benutzer (owner); lokal ist owner = 0. Alte Tabelle ohne owner wird übernommen."""
    cols = [r[1] for r in con.execute("PRAGMA table_info(decks)")]
    if cols and "owner" not in cols:
        con.executescript("""BEGIN; CREATE TABLE decks_new(id INTEGER PRIMARY KEY, owner INTEGER DEFAULT 0, name TEXT,
            commander TEXT, list TEXT, saved_at TEXT, UNIQUE(owner, name));
          INSERT INTO decks_new(id, owner, name, commander, list, saved_at) SELECT id, 0, name, commander, list, saved_at FROM decks;
          DROP TABLE decks; ALTER TABLE decks_new RENAME TO decks; COMMIT;""")
    con.execute("CREATE TABLE IF NOT EXISTS decks(id INTEGER PRIMARY KEY, owner INTEGER DEFAULT 0, name TEXT, commander TEXT, "
                "list TEXT, saved_at TEXT, UNIQUE(owner, name))")
    cols = [r[1] for r in con.execute("PRAGMA table_info(decks)")]
    if "note" not in cols:
        con.execute("ALTER TABLE decks ADD COLUMN note TEXT DEFAULT ''")
    if "extra" not in cols:  # Maybeboard, Tags, Notizen als JSON
        con.execute("ALTER TABLE decks ADD COLUMN extra TEXT DEFAULT ''")
    if "share" not in cols:  # Token für öffentlichen Nur-Lese-Link
        con.execute("ALTER TABLE decks ADD COLUMN share TEXT DEFAULT ''")
    if "bracket_est" not in cols:  # Bracket-Schätzung beim Speichern (ohne Combo-Prüfung)
        con.execute("ALTER TABLE decks ADD COLUMN bracket_est TEXT DEFAULT ''")
    if "public" not in cols:  # Galerie: 1 = veröffentlicht; hidden = vom Administrator ausgeblendet; pub_meta = Kennzahlen als JSON
        con.execute("ALTER TABLE decks ADD COLUMN public INTEGER DEFAULT 0")
        con.execute("ALTER TABLE decks ADD COLUMN hidden INTEGER DEFAULT 0")
        con.execute("ALTER TABLE decks ADD COLUMN pub_at TEXT DEFAULT ''")
        con.execute("ALTER TABLE decks ADD COLUMN pub_meta TEXT DEFAULT ''")


def deck_save(p, uid=0):
    g = lambda k: (p.get(k) or [""])[0].strip()
    if not g("list"):
        return {"error": "Leere Deckliste."}
    if len(g("list")) > 20000:
        return {"error": "Die Deckliste ist zu lang."}
    name = (g("name") or g("commander") or "Mein Deck")[:80]
    con = db()
    decks_table(con)
    if SERVER and con.execute("SELECT count(*) FROM decks WHERE owner = ?", (uid,)).fetchone()[0] >= 500:
        return {"error": "Maximal 500 gespeicherte Decks je Benutzer."}
    old = con.execute("SELECT id, commander, list, saved_at, note FROM decks WHERE owner = ? AND name = ?", (uid, name)).fetchone()
    if old and (old[2] or "").strip() != g("list") .strip():  # alte Fassung als Version sichern
        versions_table(con)
        con.execute("INSERT INTO deck_versions(deck_id, owner, saved_at, commander, list, note) VALUES(?,?,?,?,?,?)",
                    (old[0], uid, old[3], old[1], old[2], old[4] or ""))
        con.execute("DELETE FROM deck_versions WHERE deck_id = ? AND id NOT IN (SELECT id FROM deck_versions WHERE deck_id = ? "
                    "ORDER BY id DESC LIMIT 30)", (old[0], old[0]))
    extra = g("extra")
    if extra:
        try:
            ex = json.loads(extra)
            ex = {"maybe": [str(x)[:150] for x in (ex.get("maybe") or [])][:200],
                  "tags": {str(k)[:150]: [str(t)[:40] for t in v][:8] for k, v in list((ex.get("tags") or {}).items())[:300]},
                  "notes": str(ex.get("notes") or "")[:20000],
                  "groups": {str(k)[:150]: re.sub(r"\s+", " ", str(v)).strip()[:40] for k, v in list((ex.get("groups") or {}).items())[:300]
                             if str(v).strip()},
                  "bracket": str(ex.get("bracket") or "") if str(ex.get("bracket") or "") in ("1", "2", "3", "4", "5") else ""}
            extra = json.dumps(ex, ensure_ascii=False)
        except Exception:
            extra = ""
    con.execute("INSERT INTO decks(owner, name, commander, list, saved_at, note, extra) VALUES(?,?,?,?,?,?,?) ON CONFLICT(owner, name) DO UPDATE SET "
                "commander = excluded.commander, list = excluded.list, saved_at = excluded.saved_at, note = excluded.note, "
                "extra = CASE WHEN excluded.extra = '' AND ? = '1' THEN decks.extra ELSE excluded.extra END",
                (uid, name, g("commander"), g("list"), datetime.datetime.now().isoformat(sep=" ", timespec="minutes"), g("note")[:300], extra,
                 "1" if g("keep_extra") else ""))
    con.commit()
    return {"ok": True, "name": name, "decks": deck_list(con, uid)}


def versions_table(con):
    con.execute("CREATE TABLE IF NOT EXISTS deck_versions(id INTEGER PRIMARY KEY, deck_id INTEGER, owner INTEGER, saved_at TEXT, "
                "commander TEXT, list TEXT, note TEXT DEFAULT '')")
    if "note" not in [r[1] for r in con.execute("PRAGMA table_info(deck_versions)")]:
        con.execute("ALTER TABLE deck_versions ADD COLUMN note TEXT DEFAULT ''")


def list_counts(text):
    out = {}
    for line in (text or "").splitlines():
        m = re.match(r"^\s*(\d+)?\s*x?\s*(.+?)\s*$", line)
        if m and m.group(2):
            out[m.group(2)] = out.get(m.group(2), 0) + int(m.group(1) or 1)
    return out


def list_diff(old, new):
    a, b = list_counts(old), list_counts(new)
    added = [f"{b[n] - a.get(n, 0)} {n}" for n in sorted(b) if b[n] > a.get(n, 0)]
    removed = [f"{a[n] - b.get(n, 0)} {n}" for n in sorted(a) if a[n] > b.get(n, 0)]
    return added, removed


def deck_versions(con, did, uid=0):
    cur = deck_get(con, did, uid)
    if not cur:
        return {"error": "Deck nicht gefunden."}
    versions_table(con)
    out = []
    for vid, at, cm, lst, note in con.execute("SELECT id, saved_at, commander, list, note FROM deck_versions WHERE deck_id = ? AND owner = ? "
                                              "ORDER BY id DESC", (did, uid)):
        added, removed = list_diff(lst, cur["list"])  # was seit dieser Version dazukam bzw. wegfiel
        out.append({"vid": vid, "saved_at": at, "commander": cm, "count": deck_count(lst), "added": added, "removed": removed,
                    "note": note or ""})
    return {"deck": cur, "versions": out}


def deck_version_diff(con, did, a, b, uid=0):
    """Zwei beliebige Fassungen vergleichen (0 = aktuelle Fassung)."""
    cur = deck_get(con, did, uid)
    if not cur:
        return {"error": "Deck nicht gefunden."}
    versions_table(con)
    def get(v):
        if not v:
            return cur["list"], "aktuelle Fassung (" + (cur["saved_at"] or "") + ")"
        r = con.execute("SELECT list, saved_at FROM deck_versions WHERE id = ? AND deck_id = ? AND owner = ?", (v, did, uid)).fetchone()
        return (r[0], "Fassung vom " + r[1]) if r else (None, None)
    la, na = get(a)
    lb, nb = get(b)
    if la is None or lb is None:
        return {"error": "Version nicht gefunden."}
    added, removed = list_diff(la, lb)
    return {"from": na, "to": nb, "added": added, "removed": removed}


def deck_restore(con, did, vid, uid=0):
    cur = deck_get(con, did, uid)
    versions_table(con)
    v = con.execute("SELECT commander, list FROM deck_versions WHERE id = ? AND deck_id = ? AND owner = ?", (vid, did, uid)).fetchone()
    if not cur or not v:
        return {"error": "Version nicht gefunden."}
    return deck_save({"name": [cur["name"]], "commander": [v[0] or ""], "list": [v[1]], "note": ["wiederhergestellt"], "keep_extra": ["1"]}, uid)


def deck_count(text):
    return sum(int(re.match(r"\s*(\d*)", l).group(1) or 1) for l in (text or "").splitlines() if l.strip())


def deck_list(con, uid=0):
    decks_table(con)
    def tgt(ex):
        try:
            return (json.loads(ex or "{}").get("bracket") or "")
        except Exception:
            return ""
    return [{"id": i, "name": n, "commander": c, "saved_at": t, "count": deck_count(l), "shared": bool(sh), "public": bool(pb),
             "bracket": tgt(ex), "bracket_est": be or ""}
            for i, n, c, l, t, sh, pb, ex, be in con.execute("SELECT id, name, commander, list, saved_at, share, public, extra, bracket_est FROM decks WHERE owner = ? "
                                             "ORDER BY name COLLATE NOCASE", (uid,))]


def deck_get(con, did, uid=0):
    decks_table(con)
    r = con.execute("SELECT id, name, commander, list, saved_at, note, extra FROM decks WHERE id = ? AND owner = ?", (did, uid)).fetchone()
    return {"id": r[0], "name": r[1], "commander": r[2], "list": r[3], "saved_at": r[4], "note": r[5] or "", "extra": r[6] or ""} if r else None


def deck_view(p):
    """Beliebige Liste + Commander -> dieselbe Darstellung wie ein Deckvorschlag (Gruppen, Kurve, Kosten)."""
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    ent, missing = entries_from_list(con, g("list"), g("commander"))
    if not ent:
        return {"error": "Keine Karten erkannt."}
    cmds = resolve_cmds(con, g("commander"))
    cn = {r["name"] for r in cmds}
    groups = ([{"name": "Commander", "cards": [card_dict(r) for r in cmds]}] if cmds else []) + by_type(
        [(r, q) for r, q in ent if r["name"] not in cn])
    for gr in groups:
        for c in gr["cards"]:
            if c["land"] and con.execute("SELECT 1 FROM cards WHERE name = ? AND type_line LIKE 'Basic%'", (c["name"],)).fetchone():
                c["basic"], c["eur"] = True, None
    curve, tot, pr, mi = [0] * 8, 0.0, 0, 0
    for gr in groups:
        for c in gr["cards"]:
            if not c["land"]:
                curve[min(int(c["cmc"] or 0), 7)] += c["qty"]
            if c.get("basic"):
                continue
            if c["eur"] is not None:
                tot, pr = tot + c["eur"] * c["qty"], pr + 1
            else:
                mi += 1
    ci = "".join(c for c in ORDER if any(c in r["color_identity"] for r in cmds))
    notes = [f"Nicht gefunden: {', '.join(missing)}"] if missing else []
    return {"commander": " + ".join(r["name"] for r in cmds) or None, "ci": ci, "notes": notes, "groups": groups,
            "curve": curve, "cost": {"total": tot, "priced": pr, "missing": mi}, "name": g("name"),
            "export": "\n".join(f"{c['qty']} {c['name']}" for gr in groups for c in gr["cards"])}


def forge_deck_dir():
    base = os.environ.get("APPDATA") if os.name == "nt" else (
        os.path.expanduser("~/Library/Application Support") if sys.platform == "darwin" else os.path.expanduser("~/.forge"))
    if sys.platform.startswith("linux"):
        return os.path.join(base, "decks", "commander")
    return os.path.join(base or os.path.expanduser("~"), "Forge", "decks", "commander")


def deck_export(p):
    """Deckliste in verschiedenen Formaten: arena (Moxfield, Arena, die meisten Seiten), archidekt, text, dck, csv, forge (Datei im Forge-Ordner)."""
    g = lambda k: (p.get(k) or [""])[0]
    fmt = g("fmt") or "arena"
    con = db()
    con.row_factory = sqlite3.Row
    ent, missing = entries_from_list(con, g("list"), g("commander"))
    if not ent:
        return {"error": "Leere Deckliste."}
    cmds = resolve_cmds(con, g("commander"))
    cn = {r["name"] for r in cmds}
    main = [(r, q) for r, q in ent if r["name"] not in cn]
    name = g("name").strip() or " + ".join(cn) or "Commander-Deck"
    safe = re.sub(r'[\\/:*?"<>|]', "", name).strip()[:80] or "Deck"
    if fmt == "archidekt":
        try:
            cg = json.loads(g("groups") or "{}")
        except Exception:
            cg = {}
        cat = lambda n: f" [{re.sub(r'[\[\]{},]', '', str(cg[n]))[:40]}]" if cg.get(n) else ""
        text = "\n".join([f"1x {r['name']} [Commander{{top}}]" for r in cmds] + [f"{q}x {r['name']}{cat(r['name'])}" for r, q in main])
        ext = "txt"
    elif fmt == "text":
        text = "\n".join([f"1 {r['name']}" for r in cmds] + [f"{q} {r['name']}" for r, q in main])
        ext = "txt"
    elif fmt == "csv":
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(["Count", "Name", "Board"])
        w.writerows([[1, r["name"], "commander"] for r in cmds] + [[q, r["name"], "mainboard"] for r, q in main])
        text, ext = buf.getvalue(), "csv"
    elif fmt == "forge" and SERVER:
        return {"error": "Auf dem Server nicht verfügbar. Bitte als .dck herunterladen."}
    elif fmt in ("dck", "forge"):
        tmp = os.path.join(tempfile.gettempdir(), "export.dck")
        write_dck(tmp, name, cmds, ent)
        text, ext = open(tmp, encoding="utf-8").read(), "dck"
        if fmt == "forge":
            d = forge_deck_dir()
            os.makedirs(d, exist_ok=True)
            path = os.path.join(d, safe + ".dck")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            return {"ok": True, "path": path, "missing": missing}
    else:  # Arena-/Moxfield-Format mit Commander-Abschnitt
        text = "\n".join((["Commander"] + [f"1 {r['name']}" for r in cmds] + [""] if cmds else []) + ["Deck"] +
                         [f"{q} {r['name']}" for r, q in main])
        ext = "txt"
    return {"text": text + ("" if text.endswith("\n") else "\n"), "filename": f"{safe}.{ext}", "missing": missing}


def opponent(con, p):
    """Gegnerdeck: Precon (precon=id) oder eigenes Deck (opp_list + opp_commander). None, wenn keins gewählt."""
    g = lambda k: (p.get(k) or [""])[0]
    if g("opp_list").strip():
        ent, missing = entries_from_list(con, g("opp_list"), g("opp_commander"))
        cmds = resolve_cmds(con, g("opp_commander"))
        name = g("opp_name").strip() or " + ".join(r["name"] for r in cmds) or "Gegnerdeck"
        return {"kind": "deck", "name": name, "commander": " + ".join(r["name"] for r in cmds), "set": "eigenes Deck",
                "cmds": cmds, "entries": ent, "missing": missing}
    if g("precon") and has_precons(con):
        pr = con.execute("SELECT * FROM precons WHERE id = ?", (int(g("precon") or 0),)).fetchone()
        if pr:
            theirs, missing = precon_entries(con, pr["id"])
            return {"kind": "precon", "id": pr["id"], "name": pr["name"], "commander": pr["commander"], "set": pr["set_name"],
                    "cmds": [r for r, q, ic in theirs if ic], "entries": [(r, q) for r, q, _ in theirs], "missing": missing}
    return None


TYPE_GROUPS = [("Kreaturen", "Creature"), ("Planeswalker", "Planeswalker"), ("Spontanzauber", "Instant"),
               ("Hexereien", "Sorcery"), ("Artefakte", "Artifact"), ("Verzauberungen", "Enchantment"),
               ("Kampf", "Battle"), ("Länder", "Land")]


def by_type(rows):
    groups = {}
    for r, q in rows:
        ft = front_type(r)
        g = next((name for name, t in [TYPE_GROUPS[-1]] + TYPE_GROUPS[:-1] if t in ft), "Sonstige")
        groups.setdefault(g, []).append(card_dict(r, q))
    order = [g for g, _ in TYPE_GROUPS] + ["Sonstige"]
    return [{"name": g, "cards": sorted(groups[g], key=lambda c: (c["cmc"], c["name"]))} for g in order if g in groups]


def precon_view(p):
    con = db()
    con.row_factory = sqlite3.Row
    pid = int((p.get("id") or ["0"])[0])
    pr = con.execute("SELECT * FROM precons WHERE id = ?", (pid,)).fetchone()
    if not pr:
        return {"error": "Precon nicht gefunden."}
    ent, missing = precon_entries(con, pid)
    groups = [{"name": "Commander", "cards": [card_dict(r, q) for r, q, ic in ent if ic]}] + by_type([(r, q) for r, q, ic in ent if not ic])
    return {"name": pr["name"], "set": pr["set_name"], "date": pr["release_date"], "groups": groups, "commander": pr["commander"],
            "ci": pr["color_identity"],
            "missing": missing, "export": "\n".join(f"{c['qty']} {c['name']}" for g in groups for c in g["cards"])}


def compare(p):
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    opp = opponent(con, p)
    if not opp:
        return {"error": "Bitte ein Precon oder ein eigenes Deck als Gegner wählen."}
    mine, miss_a = entries_from_list(con, g("list"), g("commander").strip())
    if not mine:
        return {"error": "Kein eigenes Deck zum Vergleichen. Bitte zuerst ein Deck vorschlagen oder laden."}
    theirs = opp["entries"]
    a, b = analyze(mine), analyze(theirs)
    rows, sa, sb = duel(a, b)
    na, nb = {r["name"] for r, _ in mine}, {r["name"]: r for r, _ in theirs}
    basic = lambda r: front_type(r).startswith("Basic")
    shared = sorted(n for n in na & set(nb) if not basic(nb[n]))
    ideas = sorted((r for n, r in nb.items() if n not in na and "Land" not in front_type(r) and r["edhrec_rank"]
                    and all(c in (g("ci") or ORDER) for c in r["color_identity"])),
                   key=lambda r: r["edhrec_rank"])[:12]
    nm = opp["name"]
    if sa > sb:
        verdict = f"Dein Deck liegt in {sa} von {len(DUEL)} Kategorien vorn und ist auf dem Papier stärker als „{nm}“."
    elif sb > sa:
        verdict = f"„{nm}“ liegt in {sb} von {len(DUEL)} Kategorien vorn, dort hat dein Deck Nachholbedarf."
    else:
        verdict = f"Ausgeglichen: beide Decks gewinnen gleich viele Kategorien ({sa}:{sb})."
    if a["bracket"] != b["bracket"]:
        verdict += f" Achtung: unterschiedliche Bracket-Schätzung ({a['bracket']} gegen {b['bracket']})."
    return {"opp": {"kind": opp["kind"], "id": opp.get("id"), "name": nm, "set": opp["set"], "commander": opp["commander"]},
            "rows": rows, "score": [sa, sb], "verdict": verdict, "a": a, "b": b,
            "shared": shared, "ideas": [card_dict(r) for r in ideas], "missing": miss_a + opp["missing"]}


# ---------------------------------------------------------------- Combos (Commander Spellbook)
SPELLBOOK_BASE = (ENV("CDB_SPELLBOOK_URL", "") or "https://backend.commanderspellbook.com").rstrip("/")  # umleitbar für Tests
SPELLBOOK = SPELLBOOK_BASE + "/find-my-combos"
BRACKET_TAG = {"R": "Ruthless", "S": "Spicy", "P": "Powerful", "O": "Oddball", "C": "Core", "E": "Exhibition", "B": "gebannt"}


def parse_variant(v):
    uses = [{"name": u["card"]["name"], "zones": u.get("zoneLocations") or [],
             "commander": bool(u.get("mustBeCommander"))} for u in v.get("uses") or []]
    return {
        "id": v.get("id"), "cards": uses,
        "requires": [t["template"]["name"] for t in v.get("requires") or []],
        "produces": [f["feature"]["name"] for f in v.get("produces") or []],
        "mana": v.get("manaNeeded") or "", "mana_value": v.get("manaValueNeeded") or 0,
        "tag": v.get("bracketTag") or "", "steps": v.get("description") or "",
        "popularity": v.get("popularity") or 0,
        "prereq": " ".join(x for x in (v.get("easyPrerequisites"), v.get("notablePrerequisites")) if x),
        "url": f"https://commanderspellbook.com/combo/{v.get('id')}/"}


def spellbook_post(url, body):
    req = urllib.request.Request(url, data=body, method="POST", headers=dict(HEADERS, **{"Content-Type": "application/json"}))
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def fetch_combos(con, commanders, main):
    """Combos laut Commander Spellbook (mit Zwischenspeicher): {"included": [...], "almost": [...]}.
    almost = Combos, denen genau die Karten in „missing“ fehlen (innerhalb der Farbidentität)."""
    key = "v2:" + hashlib.sha1(json.dumps([sorted(commanders), sorted(main)]).encode()).hexdigest()
    con.execute("CREATE TABLE IF NOT EXISTS combo_cache(key TEXT PRIMARY KEY, data TEXT, fetched_at TEXT)")
    hit = con.execute("SELECT data FROM combo_cache WHERE key = ?", (key,)).fetchone()
    if hit:
        return json.loads(hit[0])
    body = json.dumps({"main": [{"card": n, "quantity": q} for n, q in main],
                       "commanders": [{"card": n, "quantity": 1} for n in commanders]}).encode()
    included, almost, url, pages = [], [], SPELLBOOK + "?limit=100", 0
    while url and pages < 20:
        page = spellbook_post(url, body)
        res = page.get("results") or {}
        included += res.get("included") or []
        if len(almost) < 300:
            almost += res.get("almostIncluded") or []
        url, pages = page.get("next"), pages + 1
    have = {n for n, _ in main} | set(commanders)
    near = []
    for v in almost:
        c = parse_variant(v)
        c["missing"] = [u["name"] for u in c["cards"] if u["name"] not in have]
        if c["missing"]:
            near.append(c)
    data = {"included": [parse_variant(v) for v in included], "almost": near}
    con.execute("INSERT OR REPLACE INTO combo_cache VALUES(?,?,?)",
                (key, json.dumps(data), datetime.datetime.now().isoformat(sep=" ", timespec="minutes")))
    con.commit()
    return data


# ---------------------------------------------------------------- Bracket-Einstufung (offizielles System, Beta)
# Quelle: Wizards of the Coast / Commander Format Panel, „Introducing Commander Brackets Beta“ (11.02.2025) mit den
# Aktualisierungen vom 22.04.2025, 21.10.2025 (Tutor-Regel entfällt) und 09.02.2026 (Game Changer: 53 Karten).
# Die Einstufung ist eine Untergrenze aus den prüfbaren Regeln; Absicht und Spielweise entscheiden am Tisch.
EXTRA_TURN_LIMIT = 3  # mehr Extra-Zug-Karten gelten als „Ketten“ – ab dann Bracket 4
BRACKETS = {
    1: ("Exhibition", "Thema vor Stärke, sehr locker; Partien dauern mindestens etwa 9 Züge."),
    2: ("Core", "Unoptimiert und geradlinig, sozial; Partien dauern mindestens etwa 8 Züge."),
    3: ("Upgraded", "Verstärkt mit guter Synergie und Kartenqualität; Partien dauern mindestens etwa 6 Züge."),
    4: ("Optimized", "Tödlich, beständig und schnell, aber nicht auf das Turnier-Metagame ausgerichtet; mindestens etwa 4 Züge."),
    5: ("cEDH", "Für das kompetitive Metagame gebaut; Partien können in jedem Zug enden."),
}


def bracket_check(con, entries, commander_names, combos=None):
    """Prüft die Deckbau-Regeln der Brackets. combos: Ergebnis von combo_report (optional, braucht Internet)."""
    gc, mld, extra, illegal = [], [], [], []
    for r, q in entries:
        if r["game_changer"]:
            gc.append(r["name"])
        cats = categories(r)
        if "mld" in cats:
            mld.append(r["name"])
        if "extra" in cats:
            extra += [r["name"]] * q
        if not r["commander_legal"] and not front_type(r).startswith("Basic"):
            illegal.append(r["name"])
    two, early = [], []
    if combos and combos.get("combos") is not None:
        for c in combos["combos"]:
            names = [x["name"] if isinstance(x, dict) else str(x) for x in c.get("cards") or []]
            if c.get("win") and len(names) <= 2:
                two.append({"cards": names, "median": c.get("median"), "result": ", ".join(c.get("produces") or [])})
                if (c.get("median") or 99) < 6:
                    early.append(two[-1])
    rules = [
        {"key": "gc", "label": "Game Changer", "count": len(gc), "cards": gc,
         "rule": "Bracket 1–2: keine · Bracket 3: höchstens 3 · ab Bracket 4: beliebig",
         "min": 1 if not gc else (3 if len(gc) <= 3 else 4)},
        {"key": "mld", "label": "Massen-Landzerstörung / Mana-Entzug", "count": len(mld), "cards": mld,
         "rule": "in Bracket 1–3 nicht vorgesehen", "min": 4 if mld else 1},
        {"key": "extra", "label": "Extra-Züge", "count": len(extra), "cards": sorted(set(extra)),
         "rule": "Bracket 1: keine · Bracket 2–3: wenige, nicht hintereinander (ab mehr als 3 Karten gilt das als Kette) · ab 4: frei",
         "min": 1 if not extra else (2 if len(extra) <= EXTRA_TURN_LIMIT else 4)},
        {"key": "combo", "label": "Zwei-Karten-Combos, die das Spiel entscheiden", "count": len(two),
         "cards": [" + ".join(c["cards"]) + (f" (frühestens etwa Zug {c['median']})" if c.get("median") else "") for c in two],
         "rule": "Bracket 1–2: keine absichtlichen · Bracket 3: keine vor etwa Zug 6 · ab 4: frei",
         "min": 1 if not two else (4 if early else 3), "checked": combos is not None and not (combos or {}).get("error")},
    ]
    low = max(r["min"] for r in rules)
    if low == 1:
        label, val = "1–2", 2
        note = ("Keine eingeschränkten Karten gefunden. Ob Bracket 1 (Exhibition) oder 2 (Core), entscheidet die Absicht: "
                "Steht ein Thema klar vor der Spielstärke, ist es Bracket 1.")
    elif low == 2:
        label, val, note = "2", 2, "Extra-Züge in geringer Zahl schließen Bracket 1 aus; sonst passt das Deck zu Bracket 2 (Core)."
    elif low == 3:
        label, val, note = "3", 3, "Eingeschränkte Karten in einem Umfang, der zu Bracket 3 (Upgraded) passt."
    else:
        label, val = "4–5", 4
        note = ("Mindestens eine Regel geht über Bracket 3 hinaus. Ob 4 (Optimized) oder 5 (cEDH), hängt davon ab, ob das Deck für "
                "das kompetitive Turnier-Metagame gebaut ist. Das lässt sich aus der Liste allein nicht ablesen.")
    for r in rules:
        r["ok_up_to"] = {1: "1–5", 2: "2–5", 3: "3–5", 4: "4–5"}[r["min"]]
    out = {"bracket": label, "value": val, "name": BRACKETS[val][0] if low != 1 else "Exhibition oder Core",
           "note": note, "rules": rules, "combos_checked": rules[3]["checked"], "illegal": illegal,
           "spellbook": (combos or {}).get("spellbook") if combos else None}
    if not rules[3]["checked"]:
        out["note"] += (" Zwei-Karten-Combos konnten nicht geprüft werden (Commander Spellbook nicht erreichbar)." if combos is not None
                        else " Zwei-Karten-Combos werden gerade bei Commander Spellbook geprüft …")
    return out


def bracket_for(p, uid=0):
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    ent, _ = entries_from_list(con, g("list"), g("commander").strip())
    if not ent:
        return {"error": "Leere Deckliste."}
    cn = {r["name"] for r in resolve_cmds(con, g("commander"))}
    rep = combo_report(con, ent, cn) if g("combos") == "1" else None
    out = bracket_check(con, ent, cn, rep)
    if rep and rep.get("error"):
        out["combo_error"] = rep["error"]
    out["brackets"] = {str(k): {"name": v[0], "text": v[1]} for k, v in BRACKETS.items()}
    return out


def bracket_quick(con, commander, lst):
    """Schnelle Einstufung ohne Internet für Listen (Meine Decks, Galerie). Gibt z. B. "3" oder "1–2" zurück."""
    con.row_factory = sqlite3.Row
    try:
        ent, _ = entries_from_list(con, lst, commander)
        r = bracket_check(con, ent, {x["name"] for x in resolve_cmds(con, commander)}) if ent else None
    finally:
        con.row_factory = None
    return r["bracket"] if r else ""



ESTIMATE_URL = SPELLBOOK_BASE + "/estimate-bracket"


def estimate_bracket(con, commanders, main):
    """Offizielle Bracket-Einstufung von Commander Spellbook (mit Zwischenspeicher)."""
    key = "eb1:" + hashlib.sha1(json.dumps([sorted(commanders), sorted(main)]).encode()).hexdigest()
    con.execute("CREATE TABLE IF NOT EXISTS combo_cache(key TEXT PRIMARY KEY, data TEXT, fetched_at TEXT)")
    hit = con.execute("SELECT data FROM combo_cache WHERE key = ?", (key,)).fetchone()
    if hit:
        return json.loads(hit[0])
    res = spellbook_post(ESTIMATE_URL, json.dumps({"main": [{"card": n, "quantity": q} for n, q in main],
                                                   "commanders": [{"card": n, "quantity": 1} for n in commanders]}).encode())
    cards = res.get("cards") or []
    combos = res.get("combos") or []
    name = lambda x: ((x.get("card") or {}).get("name") or "")
    out = {"tag": res.get("bracketTag") or "", "name": BRACKET_TAG.get(res.get("bracketTag") or "", res.get("bracketTag") or "?"),
           "game_changers": [name(c) for c in cards if c.get("gameChanger")],
           "mass_land_denial": [name(c) for c in cards if c.get("massLandDenial")],
           "extra_turns": [name(c) for c in cards if c.get("extraTurn")],
           "banned": [name(c) for c in cards if c.get("banned")],
           "two_card_combos": sum(1 for c in combos if c.get("definitelyTwoCard")),
           "relevant_combos": sum(1 for c in combos if c.get("relevant")),
           "locks": sum(1 for c in combos if c.get("lock") or c.get("controlAllOpponents"))}
    con.execute("INSERT OR REPLACE INTO combo_cache VALUES(?,?,?)",
                (key, json.dumps(out), datetime.datetime.now().isoformat(sep=" ", timespec="minutes")))
    con.commit()
    return out


def is_win_combo(c):
    p = " ".join(c["produces"]).lower()
    return any(w in p for w in ("win the game", "infinite", "lose the game", "each opponent loses"))


def combo_speed(entries, commander_names, combos, games=1500, max_turn=12, seed=1):
    """Monte-Carlo-Schätzung, ab welchem Zug alle Teile einer Combo verfügbar und bezahlbar sind.
    Modelliert: 99 Karten gemischt, 7 Startkarten, London-Mulligan (2–5 Länder), ein Land pro Zug,
    Ziehen ab Zug 2 für den Startspieler, Ramp-Karten als +1 Mana, Tutoren holen je ein fehlendes Teil.
    Nicht modelliert: Interaktion des Gegners, genaue Farbanforderungen."""
    rnd = random.Random(seed)
    library = []
    for r, q in entries:
        if r["name"] in commander_names:
            continue
        library += [r] * q
    if not combos or not library:
        return {}
    info = {r["name"]: (r["cmc"], "Land" in front_type(r), categories(r)) for r, _ in entries}
    cmc_of = {n: v[0] for n, v in info.items()}
    first = {i: [] for i in range(len(combos))}
    pieces_of = [[u["name"] for u in c["cards"] if u["name"] not in commander_names] for c in combos]
    cost_of = [(max(sum(cmc_of.get(n, 3) for n in p), c["mana_value"] or 0), max([cmc_of.get(n, 3) for n in p] or [0]))
               for p, c in zip(pieces_of, combos)]
    is_land = lambda r: info[r["name"]][1]
    for _ in range(games):
        deck = library[:]
        for mull in range(3):  # London-Mulligan: behalten bei 2–5 Ländern, sonst neu (höchstens zweimal)
            rnd.shuffle(deck)
            if 2 <= sum(is_land(r) for r in deck[:7]) <= 5 or mull == 2:
                break
        hand = deck[:7]
        if mull:  # mull Karten unter die Bibliothek: überzählige Länder (>4), sonst teuerste Karten
            lands = [r for r in hand if is_land(r)]
            spells = sorted((r for r in hand if not is_land(r)), key=lambda r: r["cmc"])
            keep = lands[:4] + spells + lands[4:]
            hand = keep[:7 - mull]
        pool, drawn = list(hand), 7
        on_play = rnd.random() < 0.5
        played = ramp = cum = 0
        ready = {}
        for turn in range(1, max_turn + 1):
            if (turn > 1 or not on_play) and drawn < len(deck):  # Startspieler zieht in Zug 1 nicht
                pool.append(deck[drawn]); drawn += 1
            if sum(is_land(r) for r in pool) > played:  # ein Land pro Zug
                played += 1
            mana = played + ramp
            # höchstens eine neue Ramp-Karte pro Zug, wirkt ab dem nächsten Zug
            if sum(1 for r in pool if "ramp" in info[r["name"]][2] and r["cmc"] <= mana) > ramp:
                ramp += 1
            tutors = sum(1 for r in pool if "tutor" in info[r["name"]][2] and r["cmc"] <= mana)
            cum += mana
            names = {r["name"] for r in pool}
            for i, p in enumerate(pieces_of):
                if i in ready:
                    continue
                missing = sum(1 for n in p if n not in names)
                cost, biggest = cost_of[i]
                if missing <= tutors and mana >= biggest and cum >= cost:
                    ready[i] = turn
        for i in range(len(combos)):
            first[i].append(ready.get(i, 99))
    out = {}
    for i, ts in first.items():
        ts.sort()
        out[i] = {"by6": round(sum(t <= 6 for t in ts) / games * 100), "by8": round(sum(t <= 8 for t in ts) / games * 100),
                  "by10": round(sum(t <= 10 for t in ts) / games * 100), "median": ts[len(ts) // 2] if ts[len(ts) // 2] < 99 else None}
    return out


def combo_report(con, entries, commander_names):
    """Combos eines Decks inkl. Geschwindigkeit und daraus folgender Bracket-Untergrenze."""
    main = [(r["name"], q) for r, q in entries if r["name"] not in commander_names]
    try:
        data = fetch_combos(con, list(commander_names), main)
    except Exception as e:
        return {"error": f"Combo-Datenbank nicht erreichbar ({e}). Internetverbindung prüfen.", "combos": [], "almost": []}
    combos = data["included"]
    try:
        sb = estimate_bracket(con, list(commander_names), main)
    except Exception as e:
        sb = {"error": f"Bracket-Schätzung von Commander Spellbook nicht erreichbar ({e})."}
    speed = combo_speed(entries, commander_names, combos)
    for i, c in enumerate(combos):
        c.update(speed.get(i, {}))
        c["win"] = is_win_combo(c)
        c["tag_name"] = BRACKET_TAG.get(c["tag"], c["tag"])
    combos.sort(key=lambda c: (not c["win"], c.get("median") or 99, len(c["cards"])))
    two = [c for c in combos if c["win"] and len(c["cards"]) <= 2]
    floor = None
    if two:  # Brackets 1–2: keine absichtlichen Zwei-Karten-Combos; Bracket 3: keine vor Zug 6
        early = any((c.get("median") or 99) < 6 for c in two)
        floor = "4" if early else "3"
    near = [c for c in data.get("almost") or [] if len(c["missing"]) == 1]
    for c in near:
        c["win"] = is_win_combo(c)
        c["tag_name"] = BRACKET_TAG.get(c["tag"], c["tag"])
    near.sort(key=lambda c: (not c["win"], -(c.get("popularity") or 0), len(c["cards"])))
    return {"combos": combos, "bracket_floor": floor, "count": len(combos), "win_count": sum(c["win"] for c in combos),
            "almost": near[:15], "almost_count": len(near), "spellbook": sb}


def combos_for(p):
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    mine, _ = entries_from_list(con, g("list"), g("commander").strip())
    out = {"mine": combo_report(con, mine, {r["name"] for r in resolve_cmds(con, g("commander"))})}
    opp = opponent(con, p)
    theirs = opp["entries"] if opp else []
    if opp:
        out["theirs"] = combo_report(con, theirs, {r["name"] for r in opp["cmds"]})
        out["opp_name"] = opp["name"]
    for k, rep in list(out.items()):  # Bracket-Schätzung mit Combo-Regel nachschärfen
        if isinstance(rep, dict) and rep.get("combos") is not None:
            base = analyze(mine if k == "mine" else theirs)["bracket"]
            fl = rep.get("bracket_floor")
            rep["bracket"] = max([base, fl], key=lambda b: {"1–2": 1, "3": 3, "4": 4}.get(b or "", 0)) if fl else base
    return out


# ---------------------------------------------------------------- Direktes Duell über Forge
# Forge (github.com/Card-Forge/forge, GPL-3.0) ist eine freie Regel-Engine, die jede Karte mit ihren
# tatsächlichen Fähigkeiten ausführt. Wir rufen ihren Simulationsmodus „KI gegen KI“ als eigenes Programm auf.
FORGE_JVM = (f"-Xmx{ENV('CDB_FORGE_XMX', '2048m' if SERVER else '4096m')} -Dio.netty.tryReflectionSetAccessible=true -Dfile.encoding=UTF-8 "
             "-Dstdout.encoding=UTF-8 -Dstderr.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -Dsun.stderr.encoding=UTF-8 "
             + " ".join(f"--add-opens {m}=ALL-UNNAMED" for m in (
                 "java.desktop/java.beans", "java.desktop/javax.swing.border", "java.desktop/javax.swing.event",
                 "java.desktop/sun.swing", "java.desktop/java.awt.image", "java.desktop/java.awt.color",
                 "java.desktop/sun.awt.image", "java.desktop/javax.swing", "java.desktop/java.awt",
                 "java.base/java.util", "java.base/java.lang", "java.base/java.lang.reflect", "java.base/java.text",
                 "java.desktop/java.awt.font", "java.base/jdk.internal.misc", "java.base/sun.nio.ch",
                 "java.base/java.nio", "java.base/java.math", "java.base/java.util.concurrent", "java.base/java.net"))).split()
JOBS = {}
DUEL_SLOTS = threading.Semaphore(MAX_DUELS)
FORGE_WRAPPER = (ENV("CDB_FORGE_WRAPPER") or "").split()   # z. B. "xvfb-run -a" auf Servern ohne Bildschirm


def setting(key, value=None):
    con = db()
    con.execute("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)")
    if value is not None:
        con.execute("INSERT OR REPLACE INTO meta VALUES(?,?)", (key, value))
        con.commit()
    r = con.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return r[0] if r else ""


def java_version(java):
    try:
        out = subprocess.run([java, "-version"], capture_output=True, text=True, timeout=30).stderr
        mt = re.search(r'version "(\d+)(?:\.(\d+))?', out)
        major = int(mt.group(1)) if mt else 0
        return int(mt.group(2)) if major == 1 and mt.group(2) else major
    except Exception:
        return 0


def java_candidates():
    """Alle auffindbaren java-Programme: JAVA_HOME, PATH und die üblichen Installationsordner unter Windows."""
    exe = "java.exe" if os.name == "nt" else "java"
    found = []
    home = os.environ.get("JAVA_HOME")
    if home:
        found.append(os.path.join(home, "bin", exe))
    w = shutil.which("java")
    if w:
        found.append(w)
    if os.name == "nt":
        for base in {os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", "")} - {""}:
            for vendor in ("Eclipse Adoptium", "Java", "Microsoft", "Zulu", "Amazon Corretto", "BellSoft", "Semeru"):
                vd = os.path.join(base, vendor)
                if os.path.isdir(vd):
                    found += [os.path.join(vd, d, "bin", exe) for d in os.listdir(vd)]
    if sys.platform == "darwin":  # Mac: installierte JDKs und Homebrew
        jv = "/Library/Java/JavaVirtualMachines"
        if os.path.isdir(jv):
            found += [os.path.join(jv, d, "Contents", "Home", "bin", "java") for d in os.listdir(jv)]
        found += ["/opt/homebrew/opt/openjdk/bin/java", "/usr/local/opt/openjdk/bin/java"]
    seen, out = set(), []
    for j in found:
        k = os.path.normcase(os.path.abspath(j))
        if os.path.exists(j) and k not in seen:
            seen.add(k)
            out.append(j)
    return out


def java_info():
    """Nimmt das neueste installierte Java (Forge braucht 17+), auch wenn ein altes Java 8 vorne im PATH steht."""
    manual = ENV("CDB_JAVA") or setting("java_path")
    if manual and os.path.exists(manual):
        return manual, java_version(manual)
    best = (None, 0)
    for j in java_candidates():
        v = java_version(j)
        if v > best[1]:
            best = (j, v)
    return best


def forge_status():
    d = ENV("CDB_FORGE_DIR") or setting("forge_dir")
    java, ver = java_info()
    jar = None
    if d and os.path.isdir(d):
        jars = sorted(f for f in os.listdir(d) if f.startswith("forge-gui-desktop") and f.endswith("jar-with-dependencies.jar"))
        jar = jars[-1] if jars else None
    msg = []
    if not java:
        msg.append("Java nicht gefunden. Bitte Java 17 oder neuer installieren.")
    elif ver < 17:
        msg.append(f"Java {ver} ist zu alt, Forge braucht Java 17 oder neuer.")
    if not d:
        msg.append("Forge-Ordner noch nicht angegeben.")
    elif not jar:
        msg.append("Im angegebenen Ordner wurde keine Datei forge-gui-desktop-…-jar-with-dependencies.jar gefunden.")
    return {"dir": d, "jar": jar, "java": java, "java_version": ver, "ready": bool(jar and java and ver >= 17),
            "message": " ".join(msg) or "Forge ist bereit."}


def forge_name(r):
    """Kartenname in Forge-Schreibweise: doppelseitige Karten und Abenteuer nur mit Vorderseite, Split-Karten komplett."""
    n = r["name"]
    if " // " not in n:
        return n
    if " // " in (r["mana_cost"] or "") and "Adventure" not in r["type_line"] and "Omen" not in r["type_line"]:
        return n
    return n.split(" // ")[0]


def write_dck(path, name, commanders, entries):
    lines = ["[metadata]", f"Name={name}", "[Commander]"]
    lines += [f"1 {forge_name(r)}" for r in commanders]
    lines.append("[Main]")
    cn = {r["name"] for r in commanders}
    lines += [f"{q} {forge_name(r)}" for r, q in entries if r["name"] not in cn]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


REASONS = [("has won due to effect of", "Sieg durch Karteneffekt (z. B. Combo)"),
           ("has lost because an opponent has won by spell", "Sieg durch Karteneffekt (z. B. Combo)"),
           ("damage from generals", "Commander-Schaden (21)"),
           ("damage from commander", "Commander-Schaden (21)"),
           ("life total reached 0", "Lebenspunkte auf 0"),
           ("10 poison counters", "Giftmarken (10)"),
           ("empty library", "Bibliothek leer (Mill)"),
           ("due to effect of spell", "Niederlage durch Karteneffekt"),
           ("conceded", "Aufgegeben")]


def parse_game(buf, winner_line, a_tag):
    """Wertet die Ausgabe eines Spiels aus. Forge 2.x schreibt am Ende „Game Outcome: Turn N“ und
    „Game Outcome: <Spieler> has lost because …“, ältere Versionen ein umgekehrtes Protokoll mit „Turn N“."""
    g = {"winner": None, "turn": None, "reason": None, "effect": None}
    mt = re.search(r"ended in \d+ ms\. (.+) has won!", winner_line)
    outcome = [l for l in buf if "Game Outcome:" in l]
    if mt:
        num = re.match(r"Ai\((\d+)\)-", mt.group(1))
        g["winner"] = "abcdef"[int(num.group(1)) - 1] if num and int(num.group(1)) <= 6 else ("a" if mt.group(1).startswith(a_tag) else "b")
    else:
        g["winner"] = "draw"
    if sum(1 for l in outcome if "has won because all opponents have lost" in l) > 1:  # Forge-Zeitlimit in Mehrspielerpartien
        g["winner"] = "draw"
        g["reason"] = "Zeitlimit erreicht (als Unentschieden gewertet)"
        g["turn"] = next((int(t.group(1)) for t in (re.search(r"Game Outcome: Turn (\d+)", l) for l in outcome) if t), None)
        return g
    for line in outcome:
        t = re.search(r"Game Outcome: Turn (\d+)", line)
        if t:
            g["turn"] = int(t.group(1))
    if g["turn"] is None:
        turns = [int(t.group(1)) for t in (re.match(r"^\s*Turn (\d+)\s*$", l) for l in buf) if t]
        g["turn"] = max(turns) if turns else None
    for line in outcome + buf:
        for key, label in REASONS:
            if key in line and g["reason"] is None:
                g["reason"] = label
                e = re.search(r"(?:effect of|by spell) (?:spell )?'+(.+?)'+\s*$", line)  # Kartenname kann ' enthalten
                g["effect"] = e.group(1) if e else None
        if g["reason"]:
            break
    if "Stopping slow match as draw" in "\n".join(buf):
        g["reason"] = "Zeitlimit erreicht (als Unentschieden gewertet)"
    return g


def parse_detail(buf, tags, cmds):
    """Genauer Verlauf einer Forge-Partie aus dem Spielprotokoll.
    tags: {"a": "Ai(1)-Mein Deck", …}; cmds: {"a": {Commander-Namen}, …}."""
    keys = list(tags)
    n = max(1, len(keys))
    order = sorted(tags.items(), key=lambda kv: -len(kv[1]))
    P = {k: {"mull": 7, "lands": 0, "casts": 0, "cmd_round": None, "cmd_casts": 0, "dmg_dealt": 0, "dmg_taken": 0,
             "combat": 0, "life": 40, "attacks": 0, "cast_names": {}, "dmg_src": {}} for k in keys}
    life = {k: [[0, 40]] for k in keys}
    log, owner, cur, turn, first = [], {}, None, 0, None
    rnd = lambda: (turn + n - 1) // n if turn else 0

    def sub(line):
        for k, t in order:
            line = line.replace(t, "@" + k)
        return line

    def ev(text, who=None):
        if cur is not None and len(cur["ev"]) < 40:
            cur["ev"].append([who, text])

    pend_attack = None
    for raw in buf:
        line = sub(raw)
        m = re.match(r"Turn: Turn (\d+) \(@(\w)\)", line)
        if m:
            turn = int(m.group(1))
            first = first or m.group(2)
            cur = {"turn": turn, "round": rnd(), "p": m.group(2), "ev": []}
            log.append(cur)
            continue
        m = re.match(r"Mulligan: @(\w) has kept a hand of (\d+)", line)
        if m and m.group(1) in P:
            P[m.group(1)]["mull"] = int(m.group(2))
            continue
        m = re.match(r"Land: @(\w) played (.+?)(?: \((\d+)\))?\s*$", line)
        if m and m.group(1) in P:
            k = m.group(1)
            P[k]["lands"] += 1
            if m.group(3):
                owner[m.group(3)] = k
            ev("Land: " + m.group(2), k)
            continue
        m = re.match(r"Add To Stack: @(\w) cast (.+?)\s*$", line)
        if m and m.group(1) in P:
            k, c = m.group(1), re.sub(r" \(\d+\)$", "", m.group(2))
            P[k]["casts"] += 1
            P[k]["cast_names"][c] = P[k]["cast_names"].get(c, 0) + 1
            if c in cmds.get(k, ()) or c.split(" // ")[0] in cmds.get(k, ()):
                P[k]["cmd_casts"] += 1
                if P[k]["cmd_round"] is None:
                    P[k]["cmd_round"] = rnd()
                ev("Commander: " + c, k)
            else:
                ev("Zauber: " + c, k)
            continue
        m = re.match(r"Combat: @(\w) assigned (.+) to attack @(\w)", line)
        if m and m.group(1) in P:
            k = m.group(1)
            ids = re.findall(r"\((\d+)\)", m.group(2))
            for i in ids:
                owner[i] = k
            P[k]["attacks"] += 1
            pend_attack = [k, m.group(3), len(ids) or 1, 0]
            ev(f"Angriff mit {len(ids) or 1} Kreatur{'en' if len(ids) != 1 else ''} auf @{m.group(3)}", k)
            continue
        m = re.match(r"Damage: (.+?) \((\d+)\) deals (\d+) (combat )?damage to @(\w)\.?\s*$", line)
        if m and m.group(5) in P:
            src, sid, d, tgt = m.group(1), m.group(2), int(m.group(3)), m.group(5)
            k = owner.get(sid)
            P[tgt]["dmg_taken"] += d
            if k and k != tgt:
                P[k]["dmg_dealt"] += d
                P[k]["dmg_src"][src] = P[k]["dmg_src"].get(src, 0) + d
                if m.group(4):
                    P[k]["combat"] += d
            if not m.group(4):
                ev(f"{src}: {d} Schaden an @{tgt}", k)
            continue
        m = re.match(r"Life: Life: @(\w) (-?\d+) > (-?\d+)", line)
        if m and m.group(1) in P:
            k, a, b = m.group(1), int(m.group(2)), int(m.group(3))
            P[k]["life"] = b
            if len(life[k]) < 200:
                life[k].append([rnd(), b])
            ev(f"Leben @{k}: {a} → {b}", k)
            continue
    if len(log) > 120:
        log = log[:60] + [{"turn": None, "round": None, "p": None, "ev": [[None, f"… {len(log) - 120} Züge ausgelassen …"]]}] + log[-60:]
    for k in keys:
        x = P[k]
        x["top_dmg"] = sorted(x.pop("dmg_src").items(), key=lambda kv: -kv[1])[:5]
        x["cast_names"] = sorted(x["cast_names"].items(), key=lambda kv: -kv[1])
    return {"first": first, "turns": turn, "rounds": rnd(), "p": P, "life": life, "log": log}


def decode_line(b):
    """Forge-Ausgabe: UTF-8; falls ein Java das ignoriert (ältere Windows-Versionen), Windows-1252."""
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", "replace")


def run_duel(job, cmd, cwd, a_tag):
    job["queued"] = True
    DUEL_SLOTS.acquire()
    job["queued"] = False
    try:
        if job.get("cancel"):
            return
        flags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW unter Windows
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=flags)
        job["pid"] = proc.pid
        buf = []
        for raw in proc.stdout:
            line = decode_line(raw).rstrip("\r\n")
            job["tail"] = (job.get("tail", []) + [line])[-15:]
            if line.startswith("Game Result:"):
                job["games"].append(parse_game(buf, line, a_tag))
                try:
                    job.setdefault("details", []).append(parse_detail(buf, job.get("tags") or {}, job.get("cmds") or {}))
                except Exception as e:
                    job.setdefault("details", []).append({"error": str(e)})
                buf = []
            elif "An unsupported card was requested" in line:
                um = re.search(r'requested: "(.+?)"', line)
                if um and um.group(1) not in job.setdefault("unsupported", []):
                    job["unsupported"].append(um.group(1))
            elif "Could not load deck" in line or "No deck found" in line:
                job["error"] = "Forge konnte ein Deck nicht laden: " + line
            else:
                buf.append(line)
                if len(buf) > 20000:
                    buf = buf[-20000:]
            if job.get("cancel"):
                proc.kill()
                break
        proc.wait()
        if not job["games"] and not job.get("error"):
            job["error"] = "Forge hat kein Ergebnis geliefert. Letzte Ausgabe: " + " | ".join(job.get("tail", [])[-5:])
    except Exception as e:
        job["error"] = f"Forge konnte nicht gestartet werden: {e}"
    finally:
        DUEL_SLOTS.release()
        job["done"] = True
        job["finished"] = time.time()
        summarize(job)
        shutil.rmtree(job.get("dir") or "", ignore_errors=True)


def summarize(job):
    gs = job["games"]
    keys = [x["k"] for x in job.get("players") or []] or ["a", "b"]
    res = {"draw": 0, "turns": {k: [] for k in keys}, "reasons": {k: {} for k in keys}, "effects": {k: {} for k in keys}}
    res.update({k: 0 for k in keys})
    for g in gs:
        w = g["winner"] or "draw"
        res[w] = res.get(w, 0) + 1
        if w in keys:
            if g["turn"]:
                res["turns"][w].append(g["turn"])
            if g["reason"]:
                res["reasons"][w][g["reason"]] = res["reasons"][w].get(g["reason"], 0) + 1
            if g["effect"]:
                res["effects"][w][g["effect"]] = res["effects"][w].get(g["effect"], 0) + 1
    for k in keys:
        t = res["turns"][k]
        res["turns"][k] = round(sum(t) / len(t), 1) if t else None
    res["stats"] = duel_stats(gs, job.get("details") or [], keys)
    job["summary"] = res


def duel_stats(games, details, keys):
    """Kennzahlen über alle Partien: Mulligans, Commander-Zug, Länder, Zauber, Schaden, wichtigste Karten."""
    out = {}
    pairs = [(g, d) for g, d in zip(games, details) if d and not d.get("error")]
    if not pairs:
        return None
    avg = lambda v: round(sum(v) / len(v), 1) if v else None
    for k in keys:
        ps = [(g, d["p"][k]) for g, d in pairs if k in d.get("p", {})]
        if not ps:
            continue
        won = [x for g, x in ps if g["winner"] == k]
        cards, dmg = {}, {}
        for g, x in ps:
            for c, q in x["cast_names"]:
                e = cards.setdefault(c, [0, 0, 0])  # Partien mit der Karte, davon gewonnen, Würfe gesamt
                e[0] += 1
                e[1] += g["winner"] == k
                e[2] += q
            for c, d in x["top_dmg"]:
                dmg[c] = dmg.get(c, 0) + d
        rate = len(won) / len(ps)
        key = [{"name": c, "games": v[0], "won": v[1], "casts": v[2], "rate": round(100 * v[1] / v[0])}
               for c, v in cards.items() if v[0] >= max(2, len(ps) // 4)]
        key.sort(key=lambda e: (-(e["won"] / e["games"] - rate) * e["games"] ** .5, -e["games"]))
        out[k] = {"games": len(ps), "mull": avg([7 - x["mull"] for _, x in ps]), "cmd_round": avg([x["cmd_round"] for _, x in ps if x["cmd_round"]]),
                  "cmd_never": sum(1 for _, x in ps if not x["cmd_casts"]), "cmd_casts": avg([x["cmd_casts"] for _, x in ps]),
                  "lands": avg([x["lands"] for _, x in ps]), "casts": avg([x["casts"] for _, x in ps]),
                  "dmg": avg([x["dmg_dealt"] for _, x in ps]), "combat": avg([x["combat"] for _, x in ps]),
                  "first": sum(1 for g, d in pairs if d.get("first") == k), "first_won": sum(1 for g, d in pairs if d.get("first") == k and g["winner"] == k),
                  "top_cast": sorted(({"name": c, "games": v[0], "casts": v[2]} for c, v in cards.items()), key=lambda e: (-e["games"], -e["casts"]))[:8],
                  "top_dmg": sorted(dmg.items(), key=lambda kv: -kv[1])[:6], "key": key[:5] if len(ps) >= 3 else [],
                  "rate": round(100 * rate)}
    return out


def playtest_decks(p, uid=0):
    """Karten beider Decks für den manuellen Spieltisch (Bild, Typ, Manakosten)."""
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    def pack(name, cmds, entries):
        cn = {r["name"] for r in cmds}
        card = lambda r: {"name": r["name"], "image": r["image"], "type": r["type_line"], "mana": r["mana_cost"], "cmc": r["cmc"]}
        lib = []
        for r, q in entries:
            if r["name"] not in cn:
                lib += [card(r)] * max(0, min(int(q), 99))
        ci = "".join(x for x in "WUBRG" if any(x in (r["color_identity"] or "") for r in cmds))
        return {"name": name, "cmds": [card(r) for r in cmds], "cards": lib, "ci": ci}
    mine, missing = entries_from_list(con, g("list"), g("commander"))
    if not mine:
        return {"error": "Bitte zuerst ein Deck laden."}
    out = {"mine": pack(g("deck_name") or "Mein Deck", resolve_cmds(con, g("commander")), mine), "missing": missing[:20]}
    o = opponent(con, p)
    if o:
        out["opp"] = pack(o["name"], o["cmds"], o["entries"])
    return out


def card_texts(p):
    """Typ, Regeltext, Manakosten, Stärke/Widerstand und Loyalität für die Textansicht der Spieltische."""
    try:
        names = [str(n) for n in json.loads((p.get("names") or ["[]"])[0])][:600]
    except ValueError:
        return {"error": "Ungültige Namensliste."}
    con = db()
    con.execute("CREATE TABLE IF NOT EXISTS card_stats(name TEXT PRIMARY KEY, pt TEXT, loyalty TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS card_tokens(card TEXT, token TEXT, type_line TEXT, sid TEXT)")
    out = {}
    for i in range(0, len(names), 400):
        part = names[i:i + 400]
        q = ",".join("?" * len(part))
        for n, t, tx, m, pt, loy in con.execute(f"SELECT c.name, c.type_line, c.oracle_text, c.mana_cost, s.pt, s.loyalty FROM cards c "
                                                f"LEFT JOIN card_stats s ON s.name = c.name WHERE c.name IN ({q})", part):
            out[n] = {"type": t, "text": tx or "", "mana": m or "", "pt": pt or "", "loy": loy or ""}
        for n, t in con.execute(f"SELECT token, type_line FROM card_tokens WHERE token IN ({q}) GROUP BY token", part):
            out.setdefault(n, {"type": t, "text": "", "mana": "", "pt": "", "loy": ""})
    return {"cards": out}


def forge_play(p, uid=0):
    """Lokal: beide Decks in Forge ablegen und die Forge-Oberfläche öffnen – dort spielt man selbst gegen die KI."""
    g = lambda k: (p.get(k) or [""])[0]
    if SERVER:
        return {"error": "Selbst in Forge spielen geht nur im lokalen Betrieb auf dem eigenen PC."}
    st = forge_status()
    if not st["ready"]:
        return {"error": st["message"]}
    con = db()
    con.row_factory = sqlite3.Row
    mine, _ = entries_from_list(con, g("list"), g("commander"))
    cmd = resolve_cmds(con, g("commander"))
    if not mine or not cmd:
        return {"error": "Bitte zuerst ein Deck mit Commander laden."}
    ddir = os.path.join(ENV("CDB_FORGE_USER_DIR"), "decks", "commander") if ENV("CDB_FORGE_USER_DIR") else forge_deck_dir()
    os.makedirs(ddir, exist_ok=True)
    clean = lambda x: re.sub(r"[^\w !.,+-]", "", x)[:50].strip() or "Deck"
    files = []
    n1 = "Manaschmiede - " + clean(g("deck_name") or "Mein Deck")
    write_dck(os.path.join(ddir, n1 + ".dck"), n1, cmd, mine)
    files.append(n1)
    o = opponent(con, p)
    if o and o["cmds"]:
        n2 = "Manaschmiede - Gegner " + clean(o["name"])
        write_dck(os.path.join(ddir, n2 + ".dck"), n2, o["cmds"], o["entries"])
        files.append(n2)
    started = False
    if g("start") != "0":
        try:
            subprocess.Popen(FORGE_WRAPPER + [st["java"]] + FORGE_JVM + ["-jar", st["jar"]], cwd=st["dir"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            started = True
        except Exception as e:
            return {"error": f"Forge ließ sich nicht starten: {e}", "decks": files, "dir": ddir}
    return {"ok": True, "started": started, "decks": files, "dir": ddir}


def duel_detail(p, uid=0):
    job = JOBS.get((p.get("job") or [""])[0])
    if not job or job.get("owner", 0) != uid:
        return {"error": "Unbekannter Duell-Auftrag."}
    i = int((p.get("game") or ["0"])[0] or 0)
    det = job.get("details") or []
    if not 0 <= i < len(det):
        return {"error": "Für diese Partie liegt kein Verlauf vor."}
    return {"game": i, "result": job["games"][i] if i < len(job["games"]) else None, "detail": det[i], "players": job.get("players")}


def duel_start(p, uid=0):
    g = lambda k: (p.get(k) or [""])[0]
    for k, j in list(JOBS.items()):  # alte Aufträge nach einer Stunde vergessen
        if j.get("finished") and j["finished"] < time.time() - 3600:
            JOBS.pop(k, None)
    if SERVER and any(j.get("owner") == uid and not j["done"] for j in JOBS.values()):
        return {"error": "Du hast bereits ein laufendes Duell. Bitte warten oder abbrechen."}
    st = forge_status()
    if not st["ready"]:
        return {"error": st["message"]}
    con = db()
    con.row_factory = sqlite3.Row
    mine, missing = entries_from_list(con, g("list"), g("commander"))
    opp = opponent(con, p)
    if not mine or not opp:
        return {"error": "Bitte zuerst ein eigenes Deck und einen Gegner (Precon oder eigenes Deck) wählen."}
    mine_cmd = resolve_cmds(con, g("commander"))
    if not mine_cmd:
        return {"error": "Für das Duell braucht dein Deck einen Commander."}
    if not opp["cmds"]:
        return {"error": "Für das Duell braucht auch das Gegnerdeck einen Commander."}
    # Commander-Runde zu dritt oder zu viert: ein oder zwei weitere Gegner (Precon-ID oder eigenes gespeichertes Deck)
    extra = []
    for spec in [x for x in g("extra").split(",") if x.strip()][:2]:
        kind, _, val = spec.strip().partition(":")
        if kind == "precon" and val.isdigit():
            o = opponent(con, {"precon": [val]})
        elif kind == "deck" and val.isdigit():
            d = deck_get(con, int(val), uid)
            o = opponent(con, {"opp_list": [d["list"]], "opp_commander": [d["commander"] or ""], "opp_name": [d["name"]]}) if d else None
        else:
            o = None
        if not o or not o["cmds"]:
            return {"error": f"Weiterer Gegner „{spec}“ nicht gefunden oder ohne Commander."}
        extra.append(o)
    n = max(1, min(int(g("games") or 10), MAX_GAMES))
    tmp = tempfile.mkdtemp(prefix="commander_duel_")
    clean = lambda x: re.sub(r"[^\w !.,+-]", "", x)[:60] or "Deck"
    label = lambda o: ("Precon " if o["kind"] == "precon" else "Gegner ") + clean(o["name"])
    write_dck(os.path.join(tmp, "A.dck"), "Mein Deck", mine_cmd, mine)
    write_dck(os.path.join(tmp, "B.dck"), label(opp), opp["cmds"], opp["entries"])
    files = ["A.dck", "B.dck"]
    for i, o in enumerate(extra):
        f = "CD"[i] + ".dck"
        write_dck(os.path.join(tmp, f), label(o) + f" ({i + 3})", o["cmds"], o["entries"])
        files.append(f)
    limit = max(30, min(int(g("timeout") or (900 if extra else 300)), 1200 if extra else 600))
    cmd = (FORGE_WRAPPER + [st["java"]] + FORGE_JVM + ["-jar", st["jar"], "sim", "-d", *files, "-D", tmp,
                                     "-n", str(n), "-f", "Commander", "-c", str(limit)])
    profs = ai_profiles(st["dir"])
    if g("ai") in profs and g("ai") != "Default":  # KI-Profil für dein Deck, die Gegner spielen mit „Default“
        cmd += ["-a", g("ai")] + ["Default"] * (len(files) - 1)
    if g("mc") in ("on", "max"):  # Vorausschau der KI (langsamer, spielt stärker)
        cmd += ["-mc", g("mc")]
    jid = hashlib.sha1(f"{tmp}{datetime.datetime.now()}".encode()).hexdigest()[:10]
    players = [{"k": "a", "name": "Dein Deck"}, {"k": "b", "name": label(opp)}] + \
              [{"k": "cd"[i], "name": label(o)} for i, o in enumerate(extra)]
    dnames = ["Mein Deck", label(opp)] + [label(o) + f" ({i + 3})" for i, o in enumerate(extra)]
    allcmds = [mine_cmd, opp["cmds"]] + [o["cmds"] for o in extra]
    tags = {pl["k"]: f"Ai({i + 1})-{dnames[i]}" for i, pl in enumerate(players)}
    cmds = {pl["k"]: sorted({r["name"] for r in allcmds[i]} | {r["name"].split(" // ")[0] for r in allcmds[i]}) for i, pl in enumerate(players)}
    job = JOBS[jid] = {"id": jid, "total": n, "games": [], "done": False, "precon": opp["name"], "opp": opp["name"],
                       "opp_kind": opp["kind"], "dir": tmp, "owner": uid, "queued": True, "players": players, "tags": tags,
                       "cmds": cmds, "details": []}
    threading.Thread(target=run_duel, args=(job, cmd, st["dir"], "Ai(1)-"), daemon=True).start()
    return {"job": jid, "total": n, "max_games": MAX_GAMES}


def duel_status(p, uid=0):
    job = JOBS.get((p.get("job") or [""])[0])
    if not job or job.get("owner", 0) != uid:
        return {"error": "Unbekannter Duell-Auftrag."}
    if not job["done"]:
        summarize(job)
    out = {k: v for k, v in job.items() if k not in ("dir", "pid", "owner", "details", "tags", "cmds")}
    out["has_detail"] = bool(job.get("details"))
    if job.get("queued"):
        out["waiting"] = sum(1 for j in JOBS.values() if j.get("queued") and not j["done"])
    if SERVER:
        out.pop("tail", None)
    return out


# ---------------------------------------------------------------- Proxy-Druck: Kopien beliebiger Karten (Bild oder Text), Rückseiten, Tokens
PROXY_LINE = re.compile(r"^\s*(?:(\d+)\s*x?\s+)?(.+?)(?:\s+\(([A-Za-z0-9]{2,6})\)(?:\s+([^\s*]+))?)?(?:\s+\*[FE]\*)?\s*$")


def proxy_back(row):
    """Rückseite doppelseitiger Karten (Transform, MDFC): Scryfall legt sie unter /back/ ab. Split- und Abenteuerkarten haben nur ein Bild."""
    img = row["image"] or ""
    if " // " not in row["name"] or " // " in (row["mana_cost"] or "") or "/front/" not in img:
        return None
    tl = row["type_line"] or ""
    if "Adventure" in tl or "Omen" in tl:
        return None
    return img.replace("/front/", "/back/")


def proxy_list(p, uid=0):
    """Kartenliste („2 Sol Ring“, optional „(C21) 263“ für einen bestimmten Druck) -> Kartenbilder und Texte für den Druck."""
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE IF NOT EXISTS card_stats(name TEXT PRIMARY KEY, pt TEXT, loyalty TEXT)")
    inv_tables(con)
    items, missing, total = [], [], 0
    for line in (g("list") or "").splitlines()[:400]:
        line = line.strip()
        if not line or line.startswith(("#", "//")) or line.lower() in ("deck", "commander", "sideboard", "maybeboard"):
            continue
        m = PROXY_LINE.match(line)
        if not m:
            continue
        q = max(1, min(int(m.group(1) or 1), 99))
        want = m.group(2).strip()
        hit, note = lookup(con, want)
        if hit and note and "nicht exakt" in note:  # nur Tippfehler und Vorderseiten zulassen, keine beliebigen Treffer
            nm = hit["name"].casefold()
            if not (nm.split(" // ")[0] == want.casefold() or difflib.SequenceMatcher(None, nm.split(" // ")[0], want.casefold()).ratio() >= 0.85):
                hit = None
        if not hit:
            missing.append(want)
            continue
        r = con.execute("SELECT * FROM cards WHERE name = ?", (hit["name"],)).fetchone() or hit
        st = con.execute("SELECT pt, loyalty FROM card_stats WHERE name = ?", (r["name"],)).fetchone()
        front, label = r["image"], None
        if m.group(3):
            pr = con.execute("SELECT * FROM prints WHERE name = ? AND set_code = ? AND (? = '' OR number = ?)",
                             (r["name"], m.group(3).upper(), m.group(4) or "", m.group(4) or "")).fetchone()
            if pr is None:
                try:
                    prints_of(con, r["name"])
                except Exception:
                    pass
                pr = con.execute("SELECT * FROM prints WHERE name = ? AND set_code = ? AND (? = '' OR number = ?)",
                                 (r["name"], m.group(3).upper(), m.group(4) or "", m.group(4) or "")).fetchone()
            if pr is not None and pr["image"]:
                front, label = pr["image"], f"{pr['set_code']} #{pr['number']}"
        back = proxy_back({"name": r["name"], "mana_cost": r["mana_cost"], "type_line": r["type_line"], "image": front}) if front else None
        items.append({"name": r["name"], "qty": q, "front": front, "back": back if g("backs") != "0" else None, "print": label,
                      "mana": r["mana_cost"] or "", "type": r["type_line"] or "", "text": r["oracle_text"] or "",
                      "pt": (st["pt"] if st else "") or "", "loy": (st["loyalty"] if st else "") or ""})
        total += q * (2 if back and g("backs") != "0" else 1)
    if g("tokens") == "1" and items:
        tk = deck_tokens({"list": ["\n".join(f"{x['qty']} {x['name']}" for x in items)], "commander": [""]})
        for t in tk.get("tokens") or []:
            items.append({"name": t["name"], "qty": 1, "front": t.get("image"), "back": None, "print": None, "token": True,
                          "mana": "", "type": t.get("type") or "Token", "text": "", "pt": "", "loy": ""})
            total += 1
    return {"items": items, "missing": missing, "cards": total, "pages": -(-total // 9)}


# ---------------------------------------------------------------- Kaufassistent: fehlende Karten planen, je Händler aufteilen, Budget, Precon-Check
BUY_SHOPS = ("cm", "to")


def buy_tables(con):
    con.execute("CREATE TABLE IF NOT EXISTS buy_prefs(owner INTEGER, name TEXT, set_code TEXT DEFAULT '', number TEXT DEFAULT '', "
                "foil INTEGER DEFAULT 0, shop TEXT DEFAULT '', skip INTEGER DEFAULT 0, PRIMARY KEY(owner, name))")


def buy_need(con, p, uid):
    """Bedarf je Quelle: deck (Liste), deck_id, shopping (alle Decks), wish (Wunschliste). -> ({name: menge}, {name: [decks]}, titel)"""
    g = lambda k: (p.get(k) or [""])[0]
    src = g("source") or "shopping"
    own = owned_map(con, uid) if g("owned") != "0" else {}
    need, where, title = {}, {}, ""
    if src == "shopping":
        sl = shopping_list(con, uid, share=g("share") != "0")
        for x in sl["items"]:
            q = x["missing"] if g("owned") != "0" else x["need"]
            need[x["name"]] = q
            where[x["name"]] = x["decks"]
        return need, where, "Alle Decks", sl["decks"]
    if src == "wish":
        wish_table(con)
        for n, q in con.execute("SELECT name, qty FROM wishlist WHERE owner = ?", (uid,)):
            m = q - own.get(n, 0) if g("owned") != "0" else q
            if m > 0:
                need[n] = m
                where[n] = ["Wunschliste"]
        return need, where, "Wunschliste", 0
    if src == "deck_id":
        d = deck_get(con, int(g("deck_id") or 0), uid)
        if not d:
            raise ValueError("Deck nicht gefunden.")
        text, cmd, title = d["list"], d["commander"] or "", d["name"]
    else:
        text, cmd, title = g("list"), g("commander"), g("deck_name") or "Aktuelles Deck"
    cnt = dict(list_counts(text))
    for c in [x.strip() for x in (cmd or "").split(" + ") if x.strip()]:
        cnt.setdefault(c, 1)
    for n, q in cnt.items():
        if is_basic(con, n):
            continue
        m = q - own.get(n, 0)
        if m > 0:
            need[n] = m
            where[n] = [title]
    return need, where, title, 1


def buy_plan(p, uid=0):
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    con.row_factory = sqlite3.Row
    buy_tables(con)
    inv_tables(con)
    try:
        need, where, title, ndecks = buy_need(con, p, uid)
    except ValueError as e:
        return {"error": str(e)}
    default_shop = g("default_shop") if g("default_shop") in BUY_SHOPS else "cm"
    try:
        budget = float(g("budget").replace(",", ".")) if g("budget").strip() else 0.0
    except ValueError:
        budget = 0.0
    prefs = {r["name"]: r for r in con.execute("SELECT * FROM buy_prefs WHERE owner = ?", (uid,))}
    cheap = eur_map(con, need)
    items = []
    for n, q in need.items():
        pf = prefs.get(n)
        pr = None
        if pf is not None and pf["set_code"]:
            pr = con.execute("SELECT * FROM prints WHERE set_code = ? AND number = ?", (pf["set_code"], pf["number"])).fetchone()
        foil = int(pf["foil"]) if pf is not None else 0
        price, src = print_price(con, pr, foil) if pr is not None else (None, None)
        if price is None and not (pr is not None and foil):
            price, src = cheap.get(n), "cheapest" if cheap.get(n) is not None else None
        cm = CM_LINK.format(pr["cm_id"]) if pr is not None and pr["cm_id"] else cm_link(n)
        if cm and foil:
            cm += "&isFoil=Y"
        items.append({"name": n, "qty": q, "decks": where.get(n, []), "print": {"set_code": pr["set_code"], "number": pr["number"],
                      "set_name": pr["set_name"], "image": pr["image"]} if pr is not None else None, "foil": foil,
                      "shop": (pf["shop"] if pf is not None and pf["shop"] in BUY_SHOPS else default_shop),
                      "skip": bool(pf["skip"]) if pf is not None else False, "price": price, "src": src,
                      "cheapest": cheap.get(n), "total": round(price * q, 2) if price is not None else None, "cm": cm})
    # Budget: Karten in wenigen Decks zuletzt, sonst die günstigsten zuerst – so passen möglichst viele Karten hinein
    order = sorted([x for x in items if not x["skip"]], key=lambda x: (-len(x["decks"]), x["total"] if x["total"] is not None else 1e9, x["name"]))
    spent = 0.0
    for x in order:
        t = x["total"] or 0
        x["fits"] = not budget or spent + t <= budget + 1e-9
        if x["fits"]:
            spent += t
    for x in items:
        if x["skip"]:
            x["fits"] = False
    items.sort(key=lambda x: (x["skip"], not x["fits"], x["shop"], -(x["total"] or 0), x["name"]))
    act = [x for x in items if not x["skip"]]
    shops = {}
    for x in act:
        s = shops.setdefault(x["shop"], {"cards": 0, "total": 0.0, "noprice": 0})
        s["cards"] += x["qty"]
        s["total"] = round(s["total"] + (x["total"] or 0), 2)
        s["noprice"] += int(x["price"] is None)
    total = round(sum(x["total"] or 0 for x in act), 2)
    # Cardmarket-Wants: beliebiger Druck als Liste zum Einfügen, bestimmter Druck/Foil einzeln über Produktlinks
    cm_any = [x for x in act if x["shop"] == "cm" and not x["print"] and not x["foil"] and x["fits"]]
    cm_spec = [x for x in act if x["shop"] == "cm" and (x["print"] or x["foil"]) and x["fits"]]
    out = {"title": title, "decks": ndecks, "items": items, "total": total, "budget": budget, "in_budget": round(spent, 2),
           "over": round(max(0.0, total - budget), 2) if budget else 0.0, "shops": shops,
           "cm_any_text": "\n".join(f"{x['qty']} {x['name']}" for x in cm_any), "cm_specific": len(cm_spec),
           "noprice": sum(1 for x in act if x["price"] is None), "precons": buy_precons(con, {x["name"]: x for x in act})}
    return out


def buy_precons(con, items):
    """Precons, die viele der fehlenden Karten enthalten – manchmal günstiger als Einzelkarten."""
    if not items or not has_precons(con):
        return []
    names = list(items)
    hit = {}
    for i in range(0, len(names), 900):
        part = names[i:i + 900]
        for pid, n in con.execute(f"SELECT precon_id, name FROM precon_cards WHERE name IN ({','.join('?' * len(part))})", part):
            hit.setdefault(pid, set()).add(n)
    out = []
    for pid, cov in hit.items():
        value = sum((items[n]["cheapest"] or 0) * min(items[n]["qty"], 1) for n in cov)
        if len(cov) < 3 and value < 10:
            continue
        pr = con.execute("SELECT id, name, set_name, commander FROM precons WHERE id = ?", (pid,)).fetchone()
        if not pr:
            continue
        allv = con.execute("SELECT sum(c.qty * coalesce(CAST(k.eur AS REAL), 0)) FROM precon_cards c LEFT JOIN cards k ON k.name = c.name "
                           "WHERE c.precon_id = ?", (pid,)).fetchone()[0] or 0
        out.append({"id": pr["id"], "name": pr["name"], "set": pr["set_name"], "commander": pr["commander"], "cards": sorted(cov),
                    "covered": len(cov), "value": round(value, 2), "precon_value": round(allv, 2)})
    out.sort(key=lambda x: (-x["value"], -x["covered"]))
    return out[:5]


def buy_set(p, uid=0):
    """Wahl je Karte merken: Druck (set_code/number oder leer = beliebig), Foil, Händler, überspringen."""
    g = lambda k: (p.get(k) or [""])[0]
    con = db()
    buy_tables(con)
    name = g("name")
    if not name:
        return {"error": "Karte fehlt."}
    cur = con.execute("SELECT set_code, number, foil, shop, skip FROM buy_prefs WHERE owner = ? AND name = ?", (uid, name)).fetchone()
    v = dict(zip(("set_code", "number", "foil", "shop", "skip"), cur or ("", "", 0, "", 0)))
    if "set_code" in p:
        v["set_code"], v["number"] = g("set_code").upper(), g("number")
    if "foil" in p:
        v["foil"] = 1 if g("foil") == "1" else 0
    if "shop" in p:
        v["shop"] = g("shop") if g("shop") in BUY_SHOPS else ""
    if "skip" in p:
        v["skip"] = 1 if g("skip") == "1" else 0
    con.execute("INSERT OR REPLACE INTO buy_prefs VALUES(?,?,?,?,?,?,?)", (uid, name, v["set_code"], v["number"], v["foil"], v["shop"], v["skip"]))
    con.commit()
    return buy_plan(p, uid)


def buy_done(p, uid=0):
    """Gekaufte Karten in die Sammlung übernehmen (mit gewähltem Druck), Wunschliste und gemerkte Wahl aufräumen."""
    g = lambda k: (p.get(k) or [""])[0]
    try:
        got = json.loads(g("items") or "[]")
        assert isinstance(got, list)
    except Exception:
        return {"error": "Ungültige Auswahl."}
    con = db()
    con.row_factory = sqlite3.Row
    buy_tables(con)
    wish_table(con)
    n = 0
    for it in got[:500]:
        name = str(it.get("name") or "")
        q = int(it.get("qty") or 1)
        if not name or q <= 0 or not con.execute("SELECT 1 FROM cards WHERE name = ?", (name,)).fetchone():
            continue
        inv_add(con, uid, {"name": name, "qty": q, "set_code": it.get("set_code") or "", "number": it.get("number") or "",
                           "foil": 1 if it.get("foil") else 0, "cond": "", "lang": ""})
        w = con.execute("SELECT qty FROM wishlist WHERE owner = ? AND name = ?", (uid, name)).fetchone()
        if w:
            if w[0] <= q:
                con.execute("DELETE FROM wishlist WHERE owner = ? AND name = ?", (uid, name))
            else:
                con.execute("UPDATE wishlist SET qty = qty - ? WHERE owner = ? AND name = ?", (q, uid, name))
        con.execute("DELETE FROM buy_prefs WHERE owner = ? AND name = ?", (uid, name))
        n += q
    con.commit()
    out = buy_plan(p, uid)
    out["added"] = n
    return out


def buy_csv(p, uid=0):
    r = buy_plan(p, uid)
    if r.get("error"):
        return r
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(["Anzahl", "Karte", "Edition", "Nummer", "Foil", "Händler", "Preis je Stück (EUR)", "Summe (EUR)", "Im Budget", "Decks", "Link"])
    for x in r["items"]:
        if x["skip"]:
            continue
        pr = x["print"] or {}
        w.writerow([x["qty"], x["name"], pr.get("set_code", ""), pr.get("number", ""), "ja" if x["foil"] else "", {"cm": "Cardmarket", "to": "Trader-online"}[x["shop"]],
                    f"{x['price']:.2f}".replace(".", ",") if x["price"] is not None else "", f"{x['total']:.2f}".replace(".", ",") if x["total"] is not None else "",
                    "ja" if x["fits"] else "nein", ", ".join(x["decks"]), x["cm"] or ""])
    return {"csv": buf.getvalue(), "file": "Kaufplan.csv"}


# ---------------------------------------------------------------- Messlabor: Deckvarianten und KI-Piloten per Forge messen
MAX_LAB_GAMES = max(4, int(ENV("CDB_MAX_LAB_GAMES", "200" if SERVER else "600")))
LAB_PROFILES = ("Default", "Cautious", "Reckless", "Experimental", "Hard", "Hardest")
LAB_MC = ("off", "on", "max")


def ai_profiles(forge_dir):
    """KI-Profile, die diese Forge-Version mitbringt (res/ai/*.ai)."""
    try:
        found = sorted(f[:-3] for f in os.listdir(os.path.join(forge_dir, "res", "ai")) if f.endswith(".ai"))
    except OSError:
        found = []
    return [x for x in LAB_PROFILES if x in found] + [x for x in found if x not in LAB_PROFILES] or ["Default"]


def wilson(w, n, z=1.645):
    """90-%-Vertrauensbereich einer Siegquote (Wilson), in Prozent."""
    if not n:
        return [0, 100]
    p = w / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * max(0, c - h)), round(100 * min(1, c + h))]


def lab_verdict(w1, n1, w0, n0):
    """Unterschied zur Ausgangsversion: z-Wert zweier Anteile; ab |z| 1,645 deutlich (90 %), ab 0,84 eine Tendenz (80 %)."""
    if not n1 or not n0:
        return 0.0, "noch keine Daten"
    if min(n1, n0) < 8:
        return 0.0, "zu wenige Partien für ein Urteil"
    p = (w1 + w0) / (n1 + n0)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n0)) if 0 < p < 1 else 0
    z = ((w1 / n1) - (w0 / n0)) / se if se else 0.0
    if z >= 1.645:
        v = "deutlich besser"
    elif z >= 0.84:
        v = "eher besser"
    elif z <= -1.645:
        v = "deutlich schlechter"
    elif z <= -0.84:
        v = "eher schlechter"
    else:
        v = "kein messbarer Unterschied"
    return round(z, 2), v


def lab_apply(text, out, add):
    """Deckliste als Text mit getauschten Karten (je Nennung eine Kopie)."""
    cnt = list_counts(text)
    low = {k.casefold(): k for k in cnt}
    front = {k.split(" // ")[0].casefold(): k for k in cnt}
    gone = []
    for n in out:
        k = low.get(n.casefold()) or front.get(n.casefold())
        if not k or cnt.get(k, 0) <= 0:
            gone.append(n)
            continue
        cnt[k] -= 1
    for n in add:
        cnt[n] = cnt.get(n, 0) + 1
    return "\n".join(f"{q} {k}" for k, q in cnt.items() if q > 0), gone


def lab_opponents(con, p, uid):
    """Gegnerfeld: Liste aus precon:ID / deck:ID (bis 4), sonst der oben gewählte Gegner."""
    g = lambda k: (p.get(k) or [""])[0]
    out = []
    for spec in [x.strip() for x in g("opps").split(",") if x.strip()][:4]:
        kind, _, val = spec.partition(":")
        o = None
        if spec == "cur":
            o = opponent(con, p)
        elif kind == "precon" and val.isdigit():
            o = opponent(con, {"precon": [val]})
        elif kind == "deck" and val.isdigit():
            d = deck_get(con, int(val), uid)
            o = opponent(con, {"opp_list": [d["list"]], "opp_commander": [d["commander"] or ""], "opp_name": [d["name"]]}) if d else None
        if not o or not o["cmds"]:
            raise ValueError(f"Gegner „{spec}“ nicht gefunden oder ohne Commander.")
        out.append(o)
    if not out:
        o = opponent(con, p)
        if o and o["cmds"]:
            out.append(o)
    return out


def lab_start(p, uid=0):
    g = lambda k: (p.get(k) or [""])[0]
    for k, j in list(JOBS.items()):
        if j.get("finished") and j["finished"] < time.time() - 3600:
            JOBS.pop(k, None)
    if SERVER and any(j.get("owner") == uid and not j["done"] for j in JOBS.values()):
        return {"error": "Du hast bereits ein laufendes Duell oder eine Messung. Bitte warten oder abbrechen."}
    st = forge_status()
    if not st["ready"]:
        return {"error": st["message"]}
    profiles = ai_profiles(st["dir"])
    con = db()
    con.row_factory = sqlite3.Row
    mode = "pilot" if g("mode") == "pilot" else "swap"
    mine_cmd = resolve_cmds(con, g("commander"))
    if not mine_cmd:
        return {"error": "Für die Messung braucht dein Deck einen Commander."}
    try:
        opps = lab_opponents(con, p, uid)
    except ValueError as e:
        return {"error": str(e)}
    if not opps:
        return {"error": "Bitte mindestens einen Gegner wählen."}
    ai = g("ai") if g("ai") in profiles else "Default"
    mc = g("mc") if g("mc") in LAB_MC else "off"
    variants = [{"key": "v0", "label": "Ausgangsversion" if mode == "swap" else f"KI „{ai}“", "out": [], "in": [], "ai": ai,
                 "list": g("list")}]
    if mode == "swap":
        try:
            raw = json.loads(g("variants") or "[]")
        except ValueError:
            return {"error": "Ungültige Varianten."}
        for i, v in enumerate(raw[:6]):
            out = [str(x).strip() for x in (v.get("out") or []) if str(x).strip()][:10]
            add = [str(x).strip() for x in (v.get("in") or []) if str(x).strip()][:10]
            if not out and not add:
                continue
            canon = []
            for x in add:
                r = con.execute("SELECT name FROM cards WHERE name = ? COLLATE NOCASE OR name LIKE ? COLLATE NOCASE LIMIT 1",
                                (x, x + " // %")).fetchone()
                if not r:
                    return {"error": "Unbekannte Karte: " + x}
                canon.append(r[0])
            add = canon
            text, gone = lab_apply(g("list"), out, add)
            if gone:
                return {"error": "Nicht im Deck: " + ", ".join(gone)}
            _, missing = entries_from_list(con, text, g("commander"))
            if missing:
                return {"error": "Unbekannte Karte: " + ", ".join(missing[:5])}
            label = str(v.get("label") or "").strip()[:80] or (" + ".join(add) + (" statt " + ", ".join(out) if out else ""))
            variants.append({"key": f"v{len(variants)}", "label": label, "out": out, "in": add, "ai": ai, "list": text})
        if len(variants) < 2:
            return {"error": "Bitte mindestens eine Variante (Karte raus → Karte rein) angeben."}
    else:
        want = [x for x in g("profiles").split(",") if x in profiles] or [x for x in profiles if x != ai][:3]
        for x in want:
            if x != ai:
                variants.append({"key": f"v{len(variants)}", "label": f"KI „{x}“", "out": [], "in": [], "ai": x, "list": g("list")})
        if len(variants) < 2:
            return {"error": "Bitte mindestens ein weiteres KI-Profil wählen."}
    n = max(2, int(g("games") or 10))
    total = n * len(variants) * len(opps)
    if total > MAX_LAB_GAMES:
        return {"error": f"Zu viele Partien ({total}). Erlaubt sind {MAX_LAB_GAMES}. Bitte weniger Partien, Varianten oder Gegner wählen."}
    ent0, missing0 = entries_from_list(con, g("list"), g("commander"))
    if not ent0:
        return {"error": "Leere Deckliste."}
    clean = lambda x: re.sub(r"[^\w !.,+-]", "", x)[:60] or "Deck"
    jid = "lab" + hashlib.sha1(f"{uid}{time.time()}{random.random()}".encode()).hexdigest()[:8]
    seed = int(g("seed")) if g("seed").isdigit() else random.randint(1, 10 ** 6)
    tasks = []
    for oi, o in enumerate(opps):
        for v in variants:
            tasks.append({"v": v["key"], "o": oi, "games": [], "done": False})
    job = JOBS[jid] = {
        "id": jid, "kind": "lab", "mode": mode, "owner": uid, "deck": g("deck_name")[:80] or "Mein Deck", "n": n, "total": total,
        "seed": seed, "mc": mc, "variants": [{k: v[k] for k in ("key", "label", "out", "in", "ai")} for v in variants],
        "opps": [{"name": ("Precon " if o["kind"] == "precon" else "") + o["name"]} for o in opps], "tasks": tasks,
        "done": False, "queued": True, "started": time.time(), "active": 0.0, "played": 0, "clock": max(60, min(int(g("timeout") or 300), 600))}
    lists = {v["key"]: v["list"] for v in variants}
    files = {"opps": opps, "mine_cmd": mine_cmd, "lists": lists, "commander": g("commander"), "clean": clean}
    workers = max(1, min(MAX_DUELS, len(tasks)))
    job["workers"] = workers
    for _ in range(workers):
        threading.Thread(target=lab_worker, args=(job, files, st), daemon=True).start()
    return lab_status({"job": [jid]}, uid)


def lab_worker(job, files, st):
    while not job.get("cancel"):
        with LAB_LOCK:
            t = next((x for x in job["tasks"] if not x.get("taken")), None)
            if t:
                t["taken"] = True
        if not t:
            break
        DUEL_SLOTS.acquire()
        job["queued"] = False
        t0 = t["t0"] = time.time()
        tmp = tempfile.mkdtemp(prefix="commander_lab_")
        try:
            if job.get("cancel"):
                break
            con = db()
            con.row_factory = sqlite3.Row
            ent, _ = entries_from_list(con, files["lists"][t["v"]], files["commander"])
            o = files["opps"][t["o"]]
            write_dck(os.path.join(tmp, "A.dck"), "Mein Deck", files["mine_cmd"], ent)
            write_dck(os.path.join(tmp, "B.dck"), "Gegner " + files["clean"](o["name"]), o["cmds"], o["entries"])
            v = next(x for x in job["variants"] if x["key"] == t["v"])
            cmd = (FORGE_WRAPPER + [st["java"]] + FORGE_JVM + ["-jar", st["jar"], "sim", "-d", "A.dck", "B.dck", "-D", tmp,
                   "-n", str(job["n"]), "-f", "Commander", "-c", str(job["clock"]), "-s", str(job["seed"] + t["o"]),
                   "-a", v["ai"], "Default", "-mc", job["mc"]])
            flags = 0x08000000 if os.name == "nt" else 0
            proc = subprocess.Popen(cmd, cwd=st["dir"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=flags)
            t["pid"] = proc.pid
            buf, tail = [], []
            for raw in proc.stdout:
                line = decode_line(raw).rstrip("\r\n")
                tail = (tail + [line])[-6:]
                if line.startswith("Game Result:"):
                    gm = parse_game(buf, line, "Ai(1)-")
                    t["games"].append({"w": gm["winner"], "turn": gm["turn"]})
                    with LAB_LOCK:
                        job["played"] += 1
                    buf = []
                elif "Could not load deck" in line or "No deck found" in line:
                    job["error"] = "Forge konnte ein Deck nicht laden: " + line
                elif "Unknown AI profile" in line:
                    job["error"] = "Forge kennt das KI-Profil nicht: " + line
                else:
                    buf.append(line)
                    if len(buf) > 20000:
                        buf = buf[-20000:]
                if job.get("cancel"):
                    proc.kill()
                    break
            proc.wait()
            if not t["games"] and not job.get("cancel") and not job.get("error"):
                job["error"] = "Forge hat kein Ergebnis geliefert. Letzte Ausgabe: " + " | ".join(tail[-4:])
        except Exception as e:
            job["error"] = f"Forge konnte nicht gestartet werden: {e}"
        finally:
            DUEL_SLOTS.release()
            shutil.rmtree(tmp, ignore_errors=True)
            t["done"] = True
            with LAB_LOCK:
                job["active"] += time.time() - t0
        if job.get("error"):
            job["cancel"] = True
    with LAB_LOCK:
        job["workers"] -= 1
        last = job["workers"] <= 0
    if last:
        job["done"] = True
        job["finished"] = time.time()
        res = lab_results(job)
        if job["played"]:
            try:
                con = db()
                lab_tables(con)
                cur = con.execute("INSERT INTO lab_runs(owner, created, deck, mode, result) VALUES(?,?,?,?,?)",
                                  (job["owner"], datetime.datetime.now().isoformat(sep=" ", timespec="minutes"), job["deck"], job["mode"],
                                   json.dumps(res, ensure_ascii=False)))
                con.commit()
                job["run_id"] = cur.lastrowid
            except Exception as e:
                print("Messlabor: Ergebnis nicht gespeichert:", e)


LAB_LOCK = threading.Lock()


def lab_tables(con):
    con.execute("CREATE TABLE IF NOT EXISTS lab_runs(id INTEGER PRIMARY KEY, owner INTEGER, created TEXT, deck TEXT, mode TEXT, result TEXT)")


def lab_results(job):
    """Siegquote je Variante (gesamt und je Gegner), Vergleich mit der Ausgangsversion, Urteil."""
    rows = []
    for v in job["variants"]:
        per, w, n, d, turns = [], 0, 0, 0, []
        for oi, o in enumerate(job["opps"]):
            gs = [g for t in job["tasks"] if t["v"] == v["key"] and t["o"] == oi for g in t["games"]]
            ww = sum(1 for g in gs if g["w"] == "a")
            per.append({"opp": o["name"], "wins": ww, "games": len(gs), "rate": round(100 * ww / len(gs)) if gs else None})
            w += ww
            n += len(gs)
            d += sum(1 for g in gs if g["w"] == "draw")
            turns += [g["turn"] for g in gs if g["w"] == "a" and g["turn"]]
        rows.append({"key": v["key"], "label": v["label"], "out": v["out"], "in": v["in"], "ai": v["ai"], "wins": w, "games": n,
                     "draws": d, "rate": round(100 * w / n) if n else None, "ci": wilson(w, n), "per": per,
                     "turn": round(sum(turns) / len(turns), 1) if turns else None})
    base = rows[0]
    for r in rows[1:]:
        r["delta"] = (r["rate"] - base["rate"]) if r["rate"] is not None and base["rate"] is not None else None
        r["z"], r["verdict"] = lab_verdict(r["wins"], r["games"], base["wins"], base["games"])
    best = max(rows[1:], key=lambda r: (r.get("z") or 0), default=None)
    if best and (best.get("z") or 0) >= 0.84:
        tip = (f"Empfehlung: „{best['label']}“, {best['verdict']} ({best['rate']} % statt {base['rate']} % Siege)."
               if job["mode"] == "swap" else f"Empfehlung: Dein Deck mit KI-Profil „{best['ai']}“ testen ({best['rate']} % statt {base['rate']} %).")
    elif job["played"] >= job["total"]:
        tip = "Keine Variante ist messbar besser. Mehr Partien je Variante machen kleinere Unterschiede sichtbar."
    else:
        tip = ""
    return {"mode": job["mode"], "deck": job["deck"], "n": job["n"], "opps": job["opps"], "rows": rows, "tip": tip,
            "played": job["played"], "total": job["total"], "seed": job["seed"], "mc": job["mc"]}


def lab_eta(job):
    """Restzeit: bisherige Rechenzeit je Partie × verbleibende Partien ÷ parallele Plätze; vorher ein grober Richtwert."""
    left = job["total"] - job["played"]
    if left <= 0 or job["done"]:
        return 0, "fertig"
    running = sum(time.time() - (t.get("t0") or time.time()) for t in job["tasks"] if t.get("taken") and not t["done"])
    if job["played"] >= 2:
        per = (job["active"] + running) / job["played"]
        return round(left * per / max(1, min(MAX_DUELS, len(job["tasks"])))), "gemessen"
    per = 15 if job["mc"] == "off" else 35 if job["mc"] == "on" else 60  # gemessen mit Forge 2.0.16, 1 gegen 1
    tasks_left = sum(1 for t in job["tasks"] if not t["done"])
    return round((left * per + tasks_left * 15) / max(1, min(MAX_DUELS, len(job["tasks"])))), "geschätzt"


def lab_status(p, uid=0):
    job = JOBS.get((p.get("job") or [""])[0])
    if not job or job.get("owner", 0) != uid or job.get("kind") != "lab":
        return {"error": "Unbekannte Messung."}
    eta, how = lab_eta(job)
    out = {"job": job["id"], "done": job["done"], "played": job["played"], "total": job["total"], "eta": eta, "eta_kind": how,
           "queued": job.get("queued"), "error": job.get("error"), "cancelled": bool(job.get("cancel") and not job.get("error")),
           "elapsed": round(time.time() - job["started"]), "result": lab_results(job), "run_id": job.get("run_id")}
    if job.get("queued"):
        out["waiting"] = sum(1 for j in JOBS.values() if j.get("queued") and not j["done"])
    return out


def lab_api(path, p, uid=0):
    g = lambda k: (p.get(k) or [""])[0]
    if path == "/api/lab_start":
        return lab_start(p, uid)
    if path == "/api/lab_status":
        return lab_status(p, uid)
    if path == "/api/lab_cancel":
        job = JOBS.get(g("job"))
        if job and job.get("owner", 0) == uid and job.get("kind") == "lab":
            job["cancel"] = True
            for t in job["tasks"]:
                if t.get("pid") and not t["done"]:
                    try:
                        os.kill(t["pid"], 9)
                    except OSError:
                        pass
        return {"ok": True}
    con = db()
    lab_tables(con)
    if path == "/api/lab_list":
        rows = con.execute("SELECT id, created, deck, mode, result FROM lab_runs WHERE owner = ? ORDER BY id DESC LIMIT 30", (uid,)).fetchall()
        out = []
        for i, c, d, m, r in rows:
            r = json.loads(r)
            out.append({"id": i, "created": c, "deck": d, "mode": m, "tip": r.get("tip"), "played": r.get("played"),
                        "variants": len(r.get("rows") or [])})
        st = forge_status()
        return {"runs": out, "profiles": ai_profiles(st["dir"]) if st["ready"] else ["Default"], "max": MAX_LAB_GAMES,
                "workers": MAX_DUELS, "ready": st["ready"]}
    if path == "/api/lab_get":
        r = con.execute("SELECT result FROM lab_runs WHERE id = ? AND owner = ?", (int(g("id") or 0), uid)).fetchone()
        return json.loads(r[0]) if r else {"error": "Unbekannte Messung."}
    if path == "/api/lab_delete":
        con.execute("DELETE FROM lab_runs WHERE id = ? AND owner = ?", (int(g("id") or 0), uid))
        con.commit()
        return {"ok": True}
    return {"error": "Unbekannte Aktion."}


PAGE = """<!doctype html><meta charset=utf-8><title>Manaschmiede (Version 60)</title>
<link rel=manifest href=/manifest.webmanifest><meta name=theme-color content="#1a130e">
<link rel=icon href=/icon-192.png><link rel=apple-touch-icon href=/icon-192.png><meta name=mobile-web-app-capable content=yes>
<style>body{font:15px Calibri,Arial,sans-serif;max-width:1100px;margin:20px auto;padding:0 12px}
input,select,textarea,button{padding:5px;margin:2px;font:inherit}table{border-collapse:collapse;width:100%;margin-top:12px}
td,th{border-bottom:1px solid #ccc;padding:5px;text-align:left}.gc{color:#c0362c;font-weight:bold}
.ac{position:relative;display:inline-block}
.ac ul{position:absolute;z-index:10;left:2px;right:2px;top:100%;margin:0;padding:0;list-style:none;background:#fff;
 border:1px solid #999;max-height:300px;overflow-y:auto;box-shadow:0 2px 6px #0003;min-width:320px}
.ac li{padding:4px 7px;cursor:pointer}.ac li.on,.ac li:hover{background:#f3d9d6}
.hint{color:#666;font-size:13px}.info{color:#666;font-size:13px;margin-top:-8px}input[readonly]{background:#eee}
.view button{border:1px solid #c0362c;background:#fff;color:#c0362c;cursor:pointer;border-radius:4px}
.view button.on{background:#c0362c;color:#fff}
.grid{display:flex;flex-wrap:wrap;gap:8px}.grid a,.grid .ph{position:relative;width:146px;display:block;text-decoration:none}
.grid img{width:146px;height:204px;object-fit:cover;border-radius:7px;display:block;background:#e8e8e8}
.grid .ph{height:204px;border:1px solid #bbb;border-radius:7px;padding:6px;box-sizing:border-box;color:#333;background:#f6f6f6}
.grid .q{position:absolute;top:30px;right:4px;background:#000c;color:#fff;border-radius:10px;padding:1px 8px;font-weight:bold}
.grid .g{position:absolute;bottom:6px;left:4px;background:#c0362c;color:#fff;border-radius:4px;padding:0 5px;font-size:12px}
.chips button{border:1px solid #bbb;background:#f6f6f6;border-radius:14px;cursor:pointer;margin:3px}
.duel td.w{background:#e3f1e3;font-weight:bold}.duel td.l{color:#888}.big{font-size:18px;font-weight:bold}
#pv{position:fixed;inset:0;z-index:80;background:#f4f1ea;overflow:auto;padding:8px 12px}body.pvopen{overflow:hidden}
#pv .pvbar{position:sticky;top:-8px;background:inherit;padding:6px 0;z-index:3;border-bottom:1px solid #9995}
.pvp{border:1px solid #9996;border-radius:8px;margin:8px 0;padding:6px}.pvp.act{border:2px solid #c0362c}
.pvhead,.pvtools{display:flex;flex-wrap:wrap;gap:4px;align-items:center}.pvlife{font-size:20px;font-weight:bold}
.pvrow{display:flex;flex-wrap:wrap;gap:5px;min-height:40px;align-items:flex-start;margin:4px 0;padding:3px;border-radius:6px;background:#0000000d}
.pvlab{width:100%;font-size:12px;opacity:.75}.pvc{position:relative;width:84px;cursor:pointer;transition:transform .15s}
.pvc img{width:84px;height:117px;border-radius:5px;display:block;object-fit:cover}
.pvc>span{display:block;width:84px;height:117px;border:1px solid #999;border-radius:5px;font-size:11px;padding:3px;box-sizing:border-box;background:#fff8;overflow:hidden}
.pvc.tap{transform:rotate(90deg) translateX(-14px);margin:0 18px}.pvc.cmd img{outline:2px solid #b8891f}.pvc.sel{z-index:5}
.pvcnt,.pvtax{position:absolute;top:4px;right:4px;background:#000c;color:#fff;border-radius:9px;padding:0 6px;font-size:12px}.pvtax{background:#b8891f}
.pvmenu{position:absolute;top:100%;left:0;z-index:6;background:#fff;border:1px solid #888;border-radius:6px;padding:4px;width:150px;box-shadow:0 3px 8px #0005}
.pvmenu button{display:block;width:100%;margin:2px 0;text-align:left}.pvmull{margin:6px 0}#pvpile{border:2px solid #b8891f;border-radius:8px;padding:6px;margin:8px 0}
body.mtg #pv{background:#140f0b}body.mtg .pvmenu{background:#221811;border-color:#a8843a}body.mtg .pvrow{background:#ffffff0d}body.mtg .pvc>span{background:#2a2018;color:#eadfc8}
@media(max-width:700px){.pvc,.pvc img,.pvc>span{width:62px}.pvc img,.pvc>span{height:86px}}
.invimg{width:34px;height:47px;object-fit:cover;border-radius:3px}#invtab select{max-width:150px}.printrow img{width:73px;height:102px}

.shops{display:inline-flex;gap:3px;vertical-align:middle}.shoplnk{display:inline-block;font-size:10px;font-weight:bold;line-height:1;padding:3px 5px;border-radius:9px;text-decoration:none;border:1px solid currentColor}.shoplnk.scm{color:#1f6fb2}.shoplnk.sto{color:#b0401f}.shoplnk.scc{color:#6b3fb0}body.mtg .shoplnk.scm{color:#7fb6ea}body.mtg .shoplnk.sto{color:#f09a7a}body.mtg .shoplnk.scc{color:#c3a4f0}.shopset{font-size:13px;margin:6px 0}.shopset label{margin-right:8px}
#cmpbox{display:none}section.page>details.tabbox>summary{display:none}
.sw{border:1px solid #888;background:#fff;border-radius:4px;cursor:pointer;padding:0 6px;margin-left:6px;font-size:13px}
.grid .sw{position:absolute;bottom:6px;right:4px;margin:0;background:#fffe}
.swapped img{outline:3px solid #2e8b57;outline-offset:-3px}.tag{color:#2e8b57;font-size:12px;margin-left:4px}
#dlg{display:none;position:fixed;inset:0;background:#0006;z-index:50}
#dlg>div{background:#fff;max-width:900px;margin:40px auto;padding:14px 18px;border-radius:8px;max-height:85vh;overflow-y:auto}
.alt{display:flex;gap:10px;align-items:center;border-bottom:1px solid #ddd;padding:6px 0}.alt img{width:73px;height:102px;border-radius:4px;object-fit:cover;background:#eee}
.alt .n{flex:1}.warn{color:#c0362c;font-weight:bold}
.cols{display:flex;gap:20px;flex-wrap:wrap}.cols>div{flex:1;min-width:320px}
.combo{border:1px solid #ddd;border-radius:6px;padding:6px 9px;margin:6px 0}.combo.win{border-left:4px solid #c0362c}
.bar{background:#eee;height:8px;border-radius:4px;overflow:hidden;width:160px;display:inline-block;vertical-align:middle}
.bar>i{display:block;height:8px;background:#c0362c}
:root{--pW:#f8f3d6;--pU:#a9d6f2;--pB:#c9bfbb;--pR:#f2a58a;--pG:#9fd1ac;--pC:#d6d0cc}
.mana{white-space:nowrap}.pip{display:inline-block;min-width:17px;height:17px;line-height:17px;border-radius:50%;text-align:center;
 font:bold 11px Arial,sans-serif;font-style:normal;color:#111;background:var(--pC);margin:0 1px;vertical-align:-3px;box-shadow:0 1px 1px #0006}
.pip.pW{background:var(--pW)}.pip.pU{background:var(--pU)}.pip.pB{background:var(--pB)}.pip.pR{background:var(--pR)}.pip.pG{background:var(--pG)}
button.primary{background:#c0362c;color:#fff;border:none;border-radius:5px;padding:7px 16px;font-weight:bold;cursor:pointer;box-shadow:0 2px 4px #0003}
button.primary:hover{filter:brightness(1.1)}
.savebox{border:2px solid #c0362c;border-radius:8px;padding:8px 12px;margin:10px 0;background:#fdf3f2}
#theme{position:fixed;top:10px;right:12px;z-index:60;border:1px solid #999;background:#fff;border-radius:16px;padding:4px 12px;cursor:pointer}
/* ---------- Optik im Magic-Stil */
body.mtg{background:#140f0b radial-gradient(ellipse at top,#3a2a1c 0%,#1a130e 55%,#0e0a07 100%) fixed;color:#eadfc8;
 font-family:Georgia,"Palatino Linotype","Book Antiqua",serif}
body.mtg h2,body.mtg h3,body.mtg h4{font-family:Cinzel,"Trajan Pro",Georgia,serif;color:#e2bd5b;letter-spacing:.5px;text-shadow:0 1px 2px #000}
body.mtg h2{font-size:30px;text-align:center;border-bottom:2px solid #8a6a2c;padding-bottom:10px;margin-top:34px}
body.mtg h2:before,body.mtg h2:after{content:" ✦ ";color:#a07d34}
body.mtg h3{border-bottom:1px solid #6b5123;padding-bottom:4px;margin-top:26px}
body.mtg hr{border:none;height:2px;background:linear-gradient(90deg,transparent,#a07d34,transparent);margin:28px 0}
body.mtg a{color:#f0c96a}body.mtg a:visited{color:#d9b25a}
body.mtg input,body.mtg select,body.mtg textarea{background:#241a12;color:#f3e8cf;border:1px solid #7a5c2e;border-radius:4px}
body.mtg input::placeholder,body.mtg textarea::placeholder{color:#9c8a6c}body.mtg input[readonly]{background:#33271b}
body.mtg button{background:linear-gradient(#5b3d1e,#3a2611);color:#f3d78a;border:1px solid #a8843a;border-radius:4px;cursor:pointer}
body.mtg button:hover{filter:brightness(1.2)}
body.mtg button.primary{background:linear-gradient(#f1d27a,#b8891f);color:#2a1a06;border:1px solid #f5e2a0;font-weight:bold;box-shadow:0 0 10px #d4a5304d}
body.mtg .savebox{background:#2a1f15;border-color:#c79a37;box-shadow:0 0 12px #c79a3733}
body.mtg td,body.mtg th{border-bottom:1px solid #4a3926}body.mtg th{color:#e2bd5b;font-family:Cinzel,Georgia,serif}
body.mtg .hint,body.mtg .info{color:#b4a283}body.mtg .warn{color:#ff8a72}body.mtg .gc{color:#ff8a72}body.mtg .tag{color:#8fd19a}
body.mtg .duel td.w{background:#2f4626;color:#d8f0c8}body.mtg .duel td.l{color:#8b7a62}
body.mtg .view button{background:#241a12;color:#e2bd5b;border-color:#a8843a}body.mtg .view button.on{background:#a8843a;color:#1b130b}
body.mtg .chips button{background:#2c2117;color:#eadfc8;border-color:#6b5123}
body.mtg .grid img{background:#2a2018;box-shadow:0 2px 6px #000a}body.mtg .grid .ph{background:#2a2018;border-color:#6b5123;color:#eadfc8}
body.mtg .grid .sw{background:#241a12ee;color:#f3d78a}
body.mtg .ac ul{background:#241a12;border-color:#a8843a}body.mtg .ac li.on,body.mtg .ac li:hover{background:#5b3d1e}
body.mtg #dlg>div{background:#221811;border:1px solid #a8843a}body.mtg .alt{border-color:#4a3926}
body.mtg .combo{border-color:#4a3926;background:#1f1610}body.mtg .combo.win{border-left-color:#e2bd5b}
body.mtg .bar{background:#3a2c1f}body.mtg .bar>i{background:#e2bd5b}
body.mtg details>summary{color:#e2bd5b;cursor:pointer}
body.mtg #theme{background:#241a12;color:#e2bd5b;border-color:#a8843a}
body.mtg .pip{box-shadow:0 1px 2px #000}
</style>
<style>
#helpbtn{position:fixed;top:10px;right:230px;z-index:60;border:1px solid #999;background:#fff;border-radius:16px;padding:4px 12px;cursor:pointer;font-weight:bold}
.qh{display:inline-block;width:20px;height:20px;line-height:20px;text-align:center;border-radius:50%;border:1px solid #999;
 font:bold 12px Arial,sans-serif;cursor:pointer;vertical-align:middle;margin-left:6px;background:#fff;color:#333;padding:0}
#help{display:none;position:fixed;inset:0;background:#0007;z-index:70}
#help>div{background:#fff;max-width:860px;margin:30px auto;padding:10px 24px 24px;border-radius:8px;max-height:88vh;overflow-y:auto;position:relative;line-height:1.45}
#help .x{position:sticky;top:0;float:right;font-size:18px}#help .htoc a{cursor:pointer;text-decoration:underline}
#help dt{font-weight:bold;margin-top:6px}#help code{background:#0001;padding:0 4px;border-radius:3px}
.updbar{border:1px solid #ccc;border-radius:6px;padding:5px 10px;margin:6px 0;font-size:13px;background:#f7f7f7}
.updbar .ok{color:#2e8b57}.updbar .no{color:#c0362c}
.rule{margin:5px 0;padding:3px 9px;border-left:3px solid #ccc;white-space:pre-line}.rule>b{cursor:pointer;text-decoration:underline;margin-right:6px}
.rule a.ref{cursor:pointer}.glo{margin:5px 0;padding:5px 9px;background:#0000000a;border-radius:5px;white-space:pre-line}
mark{background:#ffe27a}.toc1{font-weight:bold;margin-top:8px}.toc2{margin-left:18px;cursor:pointer;text-decoration:underline}
body.mtg #helpbtn,body.mtg .qh{background:#241a12;color:#e2bd5b;border-color:#a8843a}
body.mtg #help>div{background:#221811;border:1px solid #a8843a;color:#eadfc8}body.mtg #help code{background:#ffffff14}
body.mtg .updbar{background:#221811;border-color:#6b5123}body.mtg .updbar .ok{color:#8fd19a}body.mtg .updbar .no{color:#ff8a72}
body.mtg .rule{border-left-color:#8a6a2c}body.mtg .glo{background:#ffffff0d}body.mtg mark{background:#8a6a2c;color:#fff}
@media(max-width:700px){body{font-size:16px}#theme,#helpbtn{position:static;margin:4px}textarea{width:96%}.cols>div{min-width:0}
 table{font-size:13px}#help>div,#dlg>div{margin:8px;padding:8px 12px}input{max-width:92vw}}
</style>
<style>
.cicon{display:inline-block;width:11px;height:15px;border-radius:2px;border:1px solid #6b6b6b;margin-right:6px;vertical-align:-2px;cursor:zoom-in;
 background:linear-gradient(135deg,#d9d9d9 0%,#9a9a9a 100%);box-shadow:0 1px 1px #0004}
.cicon:hover{transform:scale(1.25)}
#cprev{position:fixed;display:none;z-index:90;width:250px;border-radius:12px;box-shadow:0 6px 22px #000a;pointer-events:none;background:#222}
body.mtg .cicon{border-color:#c79a37;background:linear-gradient(135deg,#7a4a1c 0%,#2a1a0c 60%,#c79a37 100%)}
#printarea{position:absolute;left:0;top:0;width:100%;min-height:100%;background:#fff;z-index:9000;padding:8px}
#printarea .noprint{padding:8px;background:#eee;margin-bottom:8px}
.ppage{display:grid;grid-template-columns:repeat(3,63mm);grid-auto-rows:88mm;gap:0;justify-content:center;page-break-after:always;margin-bottom:10mm}
.pcard{position:relative;width:63mm;height:88mm;overflow:hidden;outline:0.2mm dashed #999}.pcard img{width:100%;height:100%;object-fit:cover}
.pmark{position:absolute;bottom:1.5mm;left:50%;transform:translateX(-50%);font:bold 6.5pt sans-serif;color:#fff;background:#000c;padding:0 4px;border-radius:2px;white-space:nowrap}
#printarea:not(.pxcut) .pcard{outline:0}#printarea.pxgap .ppage{gap:2mm}#printarea.pxgray img{filter:grayscale(1)}
.ptextcard{background:#fff;border:0.3mm solid #333;box-sizing:border-box}.ptext{padding:3mm;font:7.5pt/1.25 Georgia,serif;color:#000;height:100%;box-sizing:border-box;display:flex;flex-direction:column;gap:1.5mm}
.ptext .pth{display:flex;justify-content:space-between;align-items:center;border-bottom:0.3mm solid #333;padding-bottom:1mm;font-size:9pt}.ptext .ptx{white-space:pre-wrap;flex:1;overflow:hidden}
.ptext .ptpt{align-self:flex-end;font-weight:bold;border:0.3mm solid #333;padding:0 2mm;margin-bottom:4mm}#pxstudio .pxnote,#pxstudio .pxsleeve{padding:8px;border-radius:6px;margin-bottom:8px;display:block}#pxstudio label{margin-right:6px}
body.printing>*:not(#printarea){display:none!important}
@media print{@page{size:A4;margin:8mm}#printarea .noprint{display:none}#printarea{position:static;padding:0}.ppage{margin:0}}
#tgame .pl{display:inline-block;vertical-align:top;border:2px solid #999;border-radius:10px;padding:8px;margin:4px;min-width:220px;text-align:center}
#tgame .pl.out{opacity:.45;border-style:dashed}#tgame .life{font-size:3em;font-weight:bold;line-height:1.1}
#tgame .pl button{min-width:44px;min-height:36px;margin:2px;font-size:1.05em}#tgame .cd{font-size:.9em;text-align:left;margin-top:4px}
#tgame .cd button{min-width:30px;min-height:28px;padding:0}
#tfield{-webkit-tap-highlight-color:transparent;position:relative;display:grid;gap:6px;height:min(80vh,780px);background:#0d0a08;padding:6px;border-radius:12px;user-select:none;-webkit-user-select:none;touch-action:manipulation}
#tfield:fullscreen{height:100vh;border-radius:0}#tfield .trow{display:grid;gap:6px;min-height:0}
#tfield .tp{position:relative;border-radius:14px;overflow:hidden;color:#fff;background:#333 center/cover no-repeat;min-height:0;box-shadow:inset 0 0 0 2px rgba(255,255,255,.12)}
#tfield .tp.act{box-shadow:inset 0 0 0 4px #f5d27a,0 0 14px rgba(245,210,122,.6)}#tfield .tp.out{filter:grayscale(1) brightness(.55)}
#tfield .tp.pick{animation:tpick .35s ease-in-out 3}@keyframes tpick{50%{filter:brightness(1.8)}}
#tfield .tpi{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(rgba(0,0,0,.35),rgba(0,0,0,.55))}
#tfield .rot .tpi{transform:rotate(180deg)}
#tfield .tpn{position:absolute;bottom:44px;left:0;right:0;text-align:center;font-weight:bold;text-shadow:0 1px 3px #000;font-size:clamp(.8em,2.2vh,1.2em);pointer-events:none}
#tfield .tpn small{display:block;font-weight:normal;opacity:.85;font-size:.8em}
#tfield .tl{font-size:clamp(2.2em,min(13vh,17vw),8em);font-weight:800;line-height:1;text-shadow:0 2px 8px #000;pointer-events:none;font-variant-numeric:tabular-nums}
#tfield .tz{position:absolute;top:0;bottom:0;width:50%;display:flex;align-items:center;font-size:2.2em;opacity:.35;cursor:pointer}
#tfield .tz.m{left:0;justify-content:flex-start;padding-left:4%}#tfield .tz.p{right:0;justify-content:flex-end;padding-right:4%}
#tfield .tz:active{background:rgba(255,255,255,.08)}
#tfield .tdl{position:absolute;top:18%;font-size:1.4em;font-weight:bold;text-shadow:0 1px 4px #000;pointer-events:none;opacity:0;transition:opacity .3s}
#tfield .tdl.on{opacity:1}#tfield .tdl.neg{color:#ff8a80}#tfield .tdl.pos{color:#9cf29c}
#tfield .tic{position:absolute;bottom:6px;left:0;right:0;display:flex;justify-content:center;gap:6px;z-index:2}
#tfield .tic button{background:rgba(0,0,0,.55);color:#fff;border:1px solid rgba(255,255,255,.3);border-radius:16px;padding:3px 10px;font-size:.95em;min-height:30px}
#tfield .tlost{position:absolute;top:62%;font-weight:bold;background:rgba(0,0,0,.6);padding:2px 10px;border-radius:8px;pointer-events:none}
#tfield .tov{position:absolute;inset:0;background:rgba(10,8,6,.94);z-index:3;overflow:auto;padding:30px 10px 10px;text-align:center;font-size:.95em}
#tfield .tov .r{display:flex;align-items:center;justify-content:center;gap:8px;margin:5px 0}
#tfield .tov button{min-width:40px;min-height:34px;font-size:1.05em}#tfield .tov .x{position:absolute;top:4px;right:6px}
#tfield .tcen{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:4;display:flex;gap:6px;align-items:center;background:rgba(20,15,11,.92);border:1px solid #a8843a;border-radius:22px;padding:4px 10px;color:#f1e3c6;white-space:nowrap}
#tfield .tcen button{background:transparent;color:#f1e3c6;border:0;font-size:1.15em;min-width:34px;min-height:34px;cursor:pointer}
#tgame .tvbar{margin:4px 0}
.inboxitem{padding:6px 0;border-bottom:1px solid rgba(168,132,58,.35)}#mainnav a[data-badge]:not([data-badge=''])::after,#mobmore a[data-badge]:not([data-badge=''])::after,#mobmorebtn[data-badge]:not([data-badge=''])::after{content:attr(data-badge);background:#c0362c;color:#fff;border-radius:9px;padding:0 6px;margin-left:4px;font-size:.8em}
.roombox{border:1px dashed #a8843a;border-radius:10px;padding:8px 12px;margin:8px 0}.roombox .tcode{font-family:monospace;font-size:1.5em;letter-spacing:3px;font-weight:bold;padding:0 6px}
.qrbox{background:#fff;display:inline-block;padding:6px;border-radius:8px;margin:6px 0;width:200px}.qrbox svg{width:100%;height:auto;display:block}
.tseats{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}.tseats button{padding:8px 12px}
.tothers{display:grid;grid-template-columns:repeat(auto-fit,minmax(92px,1fr));gap:6px;margin:6px 0}
.tother{border:1px solid #a8843a;border-radius:10px;padding:4px 6px;text-align:center;background:rgba(0,0,0,.25)}.tother b{display:block;font-size:.85em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tother .ol{display:block;font-size:1.8em;font-weight:800;line-height:1.1}.tother small{opacity:.85}.tother.act{box-shadow:0 0 0 3px #f5d27a}.tother.out{opacity:.45}
#tfield.solo{height:min(62vh,640px)}body.mob #tfield.solo{height:calc(100vh - 290px);min-height:300px}
@media (max-width:600px){#tfield .tcen{gap:2px;padding:2px 6px}#tfield .tcen button{min-width:28px;font-size:1em}#tfield .tz{font-size:1.6em}#tfield .tic button{padding:2px 7px;font-size:.85em}}body.mtg #tgame .pl{border-color:#a8843a;background:#241a12}
#top{text-align:center;margin-top:8px}#top h2{margin-bottom:4px}.wotc{margin:0 0 10px;font-size:.95em}
.recopt{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.owned{color:#3a9a4a;font-size:.85em}.recgap{margin:6px 0 10px}.recgcard{margin-left:14px}
details.subbox{border:1px solid rgba(168,132,58,.55);border-radius:10px;padding:6px 12px;margin:10px 0}details.subbox>summary{cursor:pointer;padding:4px 0}
#dropdock{position:fixed;left:0;right:0;bottom:0;z-index:300;display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:8px 10px;background:#1d150fee;border-top:2px solid #a8843a;color:#e2bd5b}
#dropdock .dz{border:1px dashed #a8843a;border-radius:8px;padding:6px 10px}#dropdock .dz.dropover{background:#a8843a;color:#140f0b}#dropdock .dzr{border-color:#c0362c}body:not(.mtg) #dropdock{background:#f4f4f4ee;color:#222}
.edbar{margin:8px 0;display:flex;flex-wrap:wrap;gap:4px;align-items:center}.selbar{flex-basis:100%;display:flex;flex-wrap:wrap;gap:4px;align-items:center;padding:4px 6px;border:1px dashed #a8843a;border-radius:8px}
.dgroup{border:1px solid transparent;border-radius:8px;padding:0 4px}.dgroup.dropover,#maybezone.dropover{border-color:#a8843a;background:rgba(168,132,58,.15)}.dragc{cursor:grab}.dragging{opacity:.4}
.stacks{display:flex;gap:10px;overflow-x:auto;align-items:flex-start;padding-bottom:8px}.stackcol{min-width:130px;width:130px}.sth{font-weight:bold;text-align:center;margin-bottom:4px}
.stc{position:relative;height:34px;cursor:pointer}.stc:last-child{height:auto}.stc img{width:130px;border-radius:6px;box-shadow:0 1px 4px #0008}.stc:hover{z-index:5}.stc:hover img{transform:translateY(-6px)}.stc.noimg{height:auto;border:1px solid #a8843a;border-radius:6px;padding:3px 6px;margin-bottom:3px;font-size:.88em}.stc .q{position:absolute;right:4px;top:2px;background:#000c;color:#fff;border-radius:6px;padding:0 4px;font-size:.8em}
body.mob .stackcol{min-width:96px;width:96px}body.mob .stc img{width:96px}body.mob .stc{height:26px}
.brb{display:inline-block;border:1px solid #a8843a;border-radius:8px;padding:0 6px;font-size:.85em;white-space:nowrap}.brb.brt{background:rgba(168,132,58,.25);font-weight:bold}.brb.brwarn{border-color:#c0362c}
.brbig{font-size:1.25em;margin:4px 0}.brtab td{vertical-align:top}.brtab td.no{color:#c0362c;font-weight:bold}.brtab td.ok{color:#3a9a4a}.brtarget{margin:8px 0;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.pctab .pcrow{cursor:pointer}.pctab .pcrow:hover{background:rgba(168,132,58,.15)}.pctab .pcset td{padding-top:10px;border-bottom:1px solid #a8843a}.pcbar{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
.pclist{columns:2;column-gap:24px;font-size:.92em}.pcg{break-inside:avoid;margin-bottom:8px}.gcm{color:#c0362c;font-size:.8em;font-weight:bold}@media(max-width:700px){.pclist{columns:1}.pctab td:nth-child(4),.pctab th:nth-child(4){display:none}}
#mobmore a[hidden],#mainnav a[hidden]{display:none!important}
.palert{max-width:720px;margin:12px auto;text-align:left;border:1px solid #a8843a;border-radius:10px;padding:8px 12px;background:rgba(168,132,58,.12)}
.palert .up{color:#3a9a4a}.palert .down{color:#c0362c}.hit{color:#3a9a4a;font-weight:bold}.wishadd,.folderedit{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:6px 0}
.ftable td,.ftable th{padding:2px 8px;text-align:left}.ftable td.r,.ftable th.r{text-align:right}.chips2 button{margin:2px}
.galf{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:6px 0 10px}.galci button{min-width:30px;padding:3px 6px;opacity:.45}.galci button.on{opacity:1;outline:2px solid #a8843a}
.galgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}.galcard{border:1px solid #a8843a;border-radius:10px;overflow:hidden;cursor:pointer;background:rgba(0,0,0,.18);display:flex;flex-direction:column}
.galcard .gimg{height:110px;background:#2a1f15 center 22%/cover no-repeat}.galcard .gb{padding:7px 9px;flex:1}.galcard .gn{font-weight:bold}.galcard .gm{font-size:.86em;opacity:.85;margin-top:3px}
.galcard .gt{display:flex;flex-wrap:wrap;gap:3px;margin-top:4px}.galcard .gt span,.galtags span{font-size:.78em;border:1px solid #a8843a;border-radius:8px;padding:0 5px}.galcard.hid{opacity:.5}
.galcom{border-top:1px solid rgba(168,132,58,.35);padding:5px 0}.galcom b{margin-right:6px}.gallist{columns:2;column-gap:20px;font-size:.92em}@media(max-width:700px){.gallist{columns:1}}
#mainnav{display:flex;flex-wrap:wrap;justify-content:center;gap:6px;margin:6px 0 12px}
#mainnav a{padding:6px 12px;border:1px solid #bbb;border-radius:18px;text-decoration:none;color:inherit;background:#f4f4f4;cursor:pointer}
#mainnav a.on{background:#2b5797;color:#fff;border-color:#2b5797}
#mainnav{position:sticky;top:0;z-index:50;padding:6px 0}body:not(.mtg) #mainnav{background:#fff}body.mtg #mainnav{background:#140f0b}
@media(max-width:700px){#mainnav{flex-wrap:nowrap;overflow-x:auto;justify-content:flex-start;-webkit-overflow-scrolling:touch}#mainnav a{white-space:nowrap}}
.hero{text-align:center;padding:28px 16px 18px;margin:8px auto 18px;max-width:860px;border-radius:16px;border:2px solid #bbb;background:linear-gradient(#fafafa,#eee)}
.herot{font-size:2.1em;margin:.3em 0}
.newbtn{display:inline-block;margin:10px auto 4px;padding:10px 18px;border-radius:24px;background:#2f7d3e;color:#fff!important;text-decoration:none;font-size:1.08em;box-shadow:0 2px 8px rgba(0,0,0,.35)}
.newbtn:hover{background:#3b9a4d}#mainnav a.navneu{background:#2f7d3e;color:#fff}
.guide{max-width:900px;margin:0 auto;line-height:1.5}.guide h3{margin-top:1.6em;border-bottom:2px solid #a8843a;padding-bottom:4px}
.gcard{background:rgba(255,255,255,.55);border:1px solid #c9b78f;border-radius:10px;padding:10px 16px;margin:10px 0}
body.mtg .gcard{background:rgba(30,22,16,.6);border-color:#6b5532}.gcard h4{margin:.2em 0 .4em}
.gpick{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;margin:12px 0}
.gbtn{display:block;padding:12px;border-radius:10px;border:2px solid #a8843a;text-decoration:none;color:inherit;background:rgba(255,255,255,.5)}
.gbtn b{display:block;font-size:1.08em}.gbtn span{font-size:.9em;opacity:.85}.gbtn.w{border-color:#c9b98f}.gbtn.u{border-color:#2f6fae}.gbtn.g{border-color:#3d7f45}.gbtn.r{border-color:#b5432f}
body.mtg .gbtn{background:rgba(30,22,16,.6)}
.gtab{border-collapse:collapse;width:100%}.gtab td,.gtab th{border-bottom:1px solid rgba(128,100,60,.35);padding:4px 8px;text-align:left;vertical-align:top}
.gsteps li,.gbig li{margin:.35em 0}.gcol{list-style:none;padding-left:0}.gcol li{margin:.3em 0}
.cibtns button,body.mtg .cibtns button{min-width:30px;height:30px;margin:0 2px;padding:0;border-radius:50%;border:2px solid transparent;opacity:.45;color:#111;font-weight:bold}
body.mtg #mainnav a.navneu:not(.on):not([aria-selected=true]){background:#2f7d3e;color:#fff;border-color:#5fbf6f}
.cibtns button.on,body.mtg .cibtns button.on{opacity:1;border-color:#f5d27a;box-shadow:0 0 6px #f5d27a}.cibtns button:disabled{opacity:.3}
.csugbox{margin:12px 0;padding:10px 14px;border:1px dashed #a8843a;border-radius:10px}
#csug .cgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px;margin-top:10px}
#csug .cc{border:1px solid #c9b78f;border-radius:10px;padding:8px;background:rgba(255,255,255,.5);display:flex;flex-direction:column;gap:4px}
body.mtg #csug .cc{background:rgba(30,22,16,.6);border-color:#6b5532}
#csug .cc img{width:100%;border-radius:8px;aspect-ratio:626/457;object-fit:cover;background:#2a2018}#csug .cc .ctake{margin-top:auto}
#csug .ctag{align-self:flex-start;font-size:.78em;padding:1px 8px;border-radius:10px;background:#e6dcc4;color:#3a2c1c}#csug .ctag.gem{background:#d9e4f5;color:#1d3d66}#csug .ctag.cheap{background:#dff0d8;color:#2f5f2f}#csug .csnav{margin-top:10px}
#csug .cc .why{font-size:.85em;color:#2f7d3e}body.mtg #csug .cc .why{color:#9cf29c}#csug .cc .tx{font-size:.82em;opacity:.85}.herosub{font-size:1.1em;max-width:640px;margin:0 auto 14px}
#wquick input{font-size:1.1em;padding:8px 10px;width:min(440px,100%);box-sizing:border-box}#wquick .ac{display:inline-block;width:min(440px,100%)}#wquick button{font-size:1.1em;padding:8px 18px;margin-top:6px}
.orbs{display:flex;justify-content:center;gap:12px}.orb{width:34px;height:34px;border-radius:50%;box-shadow:0 0 0 2px #0004 inset,0 2px 6px #0006}
.orb.w{background:radial-gradient(circle at 35% 30%,#fffbe6,#e8dcae)}.orb.u{background:radial-gradient(circle at 35% 30%,#bfe3ff,#1f6fb5)}
.orb.b{background:radial-gradient(circle at 35% 30%,#bdb3b0,#2b2422)}.orb.r{background:radial-gradient(circle at 35% 30%,#ffc2a8,#c3361d)}
.orb.g{background:radial-gradient(circle at 35% 30%,#c9f0c4,#1f7a3a)}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:16px;max-width:1000px;margin:0 auto}
.tile{display:flex;flex-direction:column;aspect-ratio:63/88;border-radius:12px;padding:8px;text-decoration:none;color:#222;border:6px solid #555;background:#ddd;box-shadow:0 3px 10px #0005;transition:transform .15s}
.tile:hover,.tile:focus{transform:translateY(-4px) rotate(-.5deg)}
.tile .tt{font-weight:bold;padding:4px 8px;border-radius:6px;background:#fff9;border:1px solid #0003}
.tile .ta{flex:1;display:flex;align-items:center;justify-content:center;font-size:3.2em;margin:6px 0;border-radius:6px;background:#0002;border:1px solid #0003}
.tile .tx{font-size:.88em;padding:6px 8px;border-radius:6px;background:#fffd;border:1px solid #0003;min-height:5.5em}
.tile.w{border-color:#d9cfa3;background:#f3ecd2}.tile.u{border-color:#2a6fb0;background:#cfe3f5}.tile.b{border-color:#2b2422;background:#a59e9b}
.tile.r{border-color:#b8381f;background:#f2c5b6}.tile.g{border-color:#1f7a3a;background:#c6e6c7}.tile.c{border-color:#8a8a8a;background:#d8d8d8}
body.mtg .hero{border-color:#a8843a;background:radial-gradient(ellipse at top,#3a2a18,#140f0b 70%);box-shadow:0 0 30px #a8843a33 inset}
body.mtg .herot{font-family:Cinzel,Georgia,serif;color:#e2bd5b;text-shadow:0 2px 6px #000}
body.mtg .tile{color:#1b140d}body.mtg .tile .tt{font-family:Cinzel,Georgia,serif;background:#f6ecd2;border-color:#7a5b26}
body.mtg .tile .tx{background:#f6ecd2;border-color:#7a5b26}body.mtg .tile .ta{background:radial-gradient(#ffffff55,#00000044)}
@media(max-width:700px){.tiles{grid-template-columns:repeat(2,1fr);gap:10px}.tile{aspect-ratio:auto;min-height:220px}.tile .ta{font-size:2.4em}.tile .tx{font-size:.8em}.herot{font-size:1.6em}}

body.mtg #mainnav a{background:#241a12;border-color:#a8843a;color:#e2bd5b}body.mtg #mainnav a.on{background:#a8843a;color:#140f0b}
#legal{margin-top:40px;padding:12px;border-top:1px solid #aaa;font-size:.85em;opacity:.9}#legal p{margin:4px 0}
body.mtg #legal{border-top-color:#8a6a2c}a.back{font-weight:bold}
.openline{padding:8px 12px;margin:6px 0 10px;border:1px dashed #999;border-radius:10px}body.mtg .openline{border-color:#a8843a}
.scanstage{margin:8px 0}.scanprev{max-width:100%;max-height:300px;border-radius:8px}
.scanlive{position:relative;display:inline-block;max-width:100%}.scanlive video{max-width:100%;max-height:60vh;border-radius:8px;display:block}
.scanframe{position:absolute;top:7%;bottom:7%;left:50%;aspect-ratio:63/88;transform:translateX(-50%);border:3px dashed #ffd24a;border-radius:10px;box-shadow:0 0 0 2000px #0006}
.scanframe::before{content:'';position:absolute;left:0;right:0;top:0;height:16%;border-bottom:2px solid #ffd24a}
.scanflash{position:absolute;left:50%;top:45%;transform:translate(-50%,-50%) scale(.9);background:#1d7a3acc;color:#fff;font-weight:bold;padding:10px 16px;border-radius:10px;opacity:0;transition:all .2s;pointer-events:none;text-align:center}
.scanflash.on{opacity:1;transform:translate(-50%,-50%) scale(1)}
.scanhit{display:flex;gap:12px;align-items:flex-start;margin:8px 0}.scanhit img{width:150px;border-radius:8px}.scanbtns{margin:6px 0}.scanbtns button{margin:3px 0}
.recentbox{max-width:860px;margin:0 auto 16px;text-align:center}.recentbox button{margin:3px}
.cname{white-space:nowrap}.tagchip{display:inline-block;font-size:.8em;padding:0 6px;border-radius:9px;background:#e7f1fb;color:#234;border:1px solid #9bc}
body.mtg .tagchip{background:#3a2c1c;color:#e2bd5b;border-color:#a8843a}.maybe{opacity:.85}.cname.miss{outline:2px dashed #c0362c;outline-offset:1px;border-radius:3px}
</style>
<style id=ptcss>
#pt{position:fixed;inset:0;z-index:200;background:#0f1a12;color:#f1e3c6;display:flex;flex-direction:column;font-size:15px;overflow:hidden}
#pt[hidden]{display:none}body.ptopen{overflow:hidden}
#pt .ptbar{display:flex;flex-wrap:wrap;gap:4px;align-items:center;padding:6px 8px;background:#1b140e;border-bottom:1px solid #a8843a}
#pt .ptbar .ptmore{display:none}#pt .ptbar button{padding:4px 9px;min-height:32px;border-radius:8px;border:1px solid #a8843a;background:#2a1f15;color:#f1e3c6;cursor:pointer}
#pt .ptinfo{margin-right:8px}#pt .ptlife{display:inline-flex;gap:4px;align-items:center;margin-right:6px}
#pt .ptnote{background:#a8843a;color:#1b140e;padding:6px 10px;font-weight:bold}
#pt .ptmain{flex:1;display:flex;min-height:0}
#pt .ptside{width:170px;padding:6px;display:flex;flex-direction:column;gap:6px;background:rgba(0,0,0,.25);overflow:auto}
#pt .ptzone{display:flex;justify-content:space-between;padding:8px;border-radius:8px;border:1px solid #a8843a;background:#2a1f15;color:#f1e3c6;cursor:pointer}
#pt .ptcz{border:1px dashed #a8843a;border-radius:8px;padding:4px;display:flex;flex-direction:column;align-items:center;gap:4px;font-size:.85em}
#pt .ptlog{font-size:.75em;opacity:.8;overflow:auto}
#pt .ptfield{flex:1;display:flex;flex-direction:column;gap:6px;padding:8px;overflow:auto;background:radial-gradient(ellipse at center,#1d3524 0%,#0f1a12 80%)}
#pt .ptrow{display:flex;flex-wrap:wrap;gap:8px;align-items:flex-start;min-height:120px;padding:6px;border-radius:10px;border:1px dashed rgba(168,132,58,.35)}
#pt .ptrow small{opacity:.5;align-self:center}
#pt .pthand{background:#1b140e;border-top:1px solid #a8843a;padding:4px 8px;max-height:40vh;overflow:auto}
#pt .pthand>div:first-child{font-size:.8em;opacity:.8}#pt .pthand .ptrow{flex-wrap:nowrap;overflow-x:auto;min-height:130px;border:0}
#pt .ptc{position:relative;width:88px;height:123px;flex:0 0 auto;border-radius:6px;background:#2a2018;border:1px solid #6b5532;cursor:pointer;overflow:hidden;transition:transform .15s;user-select:none;-webkit-user-select:none;touch-action:manipulation}
#pt .ptc img{width:100%;height:100%;object-fit:cover;display:block}#pt .ptc .ptn{position:absolute;left:0;right:0;bottom:0;font-size:10px;line-height:1.15;padding:2px 3px;background:rgba(0,0,0,.65);color:#fff}
#pt .ptc.tap{transform:rotate(90deg);margin:0 18px}#pt .ptc.tok{border:2px solid #9cf29c}
#pt .ptc .ptctr,#pt .ptc .pttax{position:absolute;top:3px;right:3px;background:#2f7d3e;color:#fff;border-radius:9px;padding:0 6px;font-size:12px}#pt .ptc .pttax{background:#a8843a;color:#1b140e;left:3px;right:auto}
#ptmenu{position:absolute;z-index:230;background:#241a12;border:1px solid #a8843a;border-radius:10px;padding:4px;display:flex;flex-direction:column;min-width:200px;box-shadow:0 6px 18px rgba(0,0,0,.6)}
#ptmenu button{text-align:left;padding:8px 10px;background:none;border:0;color:#f1e3c6;cursor:pointer;border-radius:6px}#ptmenu button:hover{background:#3a2c20}
#ptlist{position:absolute;left:5%;right:5%;top:8%;bottom:8%;z-index:220;background:#1b140e;border:1px solid #a8843a;border-radius:12px;padding:10px;overflow:auto;box-shadow:0 10px 30px rgba(0,0,0,.7)}
#ptlist .pth{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}#ptlist .ptgrid{display:flex;flex-wrap:wrap;gap:8px}
#ptlist .ptgrid>button{padding:6px 10px;border-radius:8px;border:1px solid #a8843a;background:#2a1f15;color:#f1e3c6}
@media (max-width:760px){#pt{font-size:14px}#pt .ptmain{flex-direction:column}#pt .ptside{width:auto;flex-direction:row;flex-wrap:wrap;align-items:flex-start}
 #pt .ptcz{flex-direction:row}#pt .ptlog{display:none}#pt .ptc{width:64px;height:90px}#pt .ptc.tap{margin:0 13px}#pt .ptrow{min-height:96px}
 #pt .ptbar button{padding:3px 7px;font-size:.88em}#pt .ptbar .ptsec{display:none}#pt .ptbar .ptmore{display:inline-block}#pt .ptinfo{width:100%}#pt .pthand .ptrow{min-height:96px}#ptlist{left:2%;right:2%;top:4%;bottom:4%}}
/* Handy: Kartengröße (A−/A+), Querformat, große Kartenansicht */
#pt{--cw:88px}#pv{--cw:84px}
@media(max-width:760px){#pt,#pv{--cw:64px}}
#pt .ptc{width:calc(var(--cw)*var(--tk,1));height:calc(var(--cw)*var(--tk,1)*1.4)}#pt .ptc.tap{margin:0 calc(var(--cw)*var(--tk,1)*.2)}
#pv .pvc,#pv .pvc img,#pv .pvc>span{width:calc(var(--cw)*var(--tk,1))}#pv .pvc img,#pv .pvc>span{height:calc(var(--cw)*var(--tk,1)*1.4)}
#pt .pthand .ptrow,#pt .ptrow{min-height:calc(var(--cw)*var(--tk,1)*1.4 + 10px)}
.rothint,#tquer{display:none}
@media(orientation:portrait) and (max-width:600px){.rothint{display:flex;flex-wrap:wrap;gap:6px;align-items:center;background:#a8843a;color:#1b140e;padding:6px 10px;font-weight:bold;font-size:13px}#tquer{display:inline-block}}
@media(orientation:landscape) and (max-height:520px){
 #pt,#pv{--cw:calc(28vh / 1.4 * 1)}#tquer{display:inline-block}
 #pt .ptbar,#pv .pvbar{flex-wrap:nowrap;overflow-x:auto;padding:3px 6px;gap:3px;white-space:nowrap}#pt .ptbar button,#pv .pvbar button{min-height:28px;padding:2px 7px;font-size:13px}
 #pt .ptbar .ptsec{display:inline-block}#pt .ptbar .ptmore{display:none}#pt .ptinfo{width:auto}
 #pt .ptmain{flex-direction:row}#pt .ptside{width:118px;flex-direction:column;flex-wrap:nowrap}#pt .ptcz{flex-direction:column}#pt .ptlog{display:none}
 #pt .ptfield{padding:4px;gap:4px}#pt .ptrow{gap:5px;padding:3px}#pt .pthand{max-height:44vh;padding:2px 6px}#pt .ptnote{padding:3px 8px}
 #pv{padding:4px 8px}#pv .pvp{margin:4px 0;padding:4px}#pv .pvhead,#pv .pvtools{font-size:13px;flex-wrap:nowrap;overflow-x:auto;white-space:nowrap}#pv>p.hint{display:none}}
#czoom{position:fixed;inset:0;z-index:400;background:rgba(0,0,0,.88);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;color:#eee;font-size:13px}
#czoom img{max-width:94vw;max-height:86vh;border-radius:14px;box-shadow:0 0 30px #000}
#czoom .cztext{background:#2a2018;color:#f1e3c6;padding:20px;border-radius:12px;font-size:18px;max-width:80vw;text-align:center}
.tnote{position:fixed;left:8px;right:8px;bottom:12px;z-index:450;background:#1b140e;color:#f1e3c6;border:1px solid #a8843a;border-radius:10px;padding:10px;font-size:14px}

/* Textansicht der Spieltische */
#pt .ptc.txt,#pv .pvc.txt{width:calc(var(--cw)*var(--tk,1)*1.55);height:auto;min-height:calc(var(--cw)*var(--tk,1)*.9);background:none}
#pt .ptc.txt.tap,#pv .pvc.txt.tap{transform:none;margin:0;opacity:.55}#pt .ptc.txt.tap .ctile,#pv .pvc.txt.tap .ctile{border-style:dashed}
#pt .ptc.txt.tap .ctile::after,#pv .pvc.txt.tap .ctile::after{content:'getappt';position:absolute;top:2px;right:4px;font-size:10px;font-weight:bold}
.ctile{position:relative;box-sizing:border-box;width:100%;min-height:inherit;border:1px solid #a8843a;border-radius:6px;padding:3px 5px 14px;background:#fffaf0;color:#1b140e;font-size:calc(11px*var(--tk,1));line-height:1.25;text-align:left}
body.mtg .ctile{background:#2a2018;color:#f1e3c6}
.ctile .cth{display:flex;flex-wrap:wrap;justify-content:space-between;gap:1px 3px;align-items:flex-start}.ctile .cth .mana{white-space:nowrap;flex-shrink:0;margin-left:auto}.ctile .cth b{font-size:calc(12px*var(--tk,1))}.ctile .mana .pip{width:1.05em;height:1.05em;font-size:.8em}
.ctile .cty{font-style:italic;opacity:.8;margin:1px 0;font-size:.95em}.ctile .ctx{white-space:pre-line;font-size:.92em}
.ctile .cpt{position:absolute;right:4px;bottom:2px;font-weight:bold;background:#a8843a;color:#1b140e;border-radius:4px;padding:0 4px}
.ptc.cmd .ctile,.pvc.cmd .ctile{border:2px solid #b8891f}
#czoom .ctile.big{width:min(92vw,420px);font-size:16px;padding:14px 16px 30px;max-height:84vh;overflow:auto}#czoom .ctile.big .cth b{font-size:20px}#czoom .ctile.big .cpt{font-size:16px;bottom:8px;right:10px}
/* Spieltisch im Arena-Stil */
#pv.ar{position:fixed;inset:0;z-index:200;padding:0;display:flex;flex-direction:column;overflow:hidden;user-select:none;-webkit-user-select:none;
 background:radial-gradient(ellipse at 50% 55%,#2d3b30 0%,#18201a 65%,#0c100d 100%);color:#eee;--cw:100px}#pv.ar[hidden]{display:none!important}#pv.ar button{font-family:inherit}#pv.ar .artop{display:flex;justify-content:space-between;align-items:center;padding:5px 10px;gap:6px;flex-shrink:0}#pv.ar .arinfo{display:flex;align-items:center;gap:8px;font-size:14px}#pv.ar .arphases{display:flex;gap:3px}#pv.ar .arph{width:28px;height:28px;border-radius:50%;border:1px solid #fff3;background:#0004;color:#bbb;padding:0;font-size:13px;min-height:0}#pv.ar .arph.on{background:#e0a744;color:#1b140e;border-color:#e0a744}#pv.ar .arphname{font-size:12px;opacity:.65}#pv.ar .artools{display:flex;gap:6px}#pv.ar .aricon{width:38px;height:38px;min-height:0;border-radius:50%;border:1px solid #fff3;background:#0006;color:#eee;font-size:17px;padding:0;display:inline-flex;align-items:center;justify-content:center}#pv.ar .aricon:hover{border-color:#e0a744}#pv.ar .arpl{display:flex;align-items:center;gap:8px;padding:4px 10px;flex-shrink:0}#pv.ar .arpl.top{background:#0003}#pv.ar .aravatar{position:relative;width:62px;height:62px;min-height:0;border-radius:50%;border:3px solid #666;background:radial-gradient(circle at 35% 30%,#4a3b2a,#1b140e);
 color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0;flex-shrink:0}#pv.ar .arpl.act .aravatar{border-color:#e0a744;box-shadow:0 0 16px #e0a744aa}#pv.ar .arlife{font-size:24px;line-height:1}#pv.ar .arname{font-size:9px;max-width:54px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;opacity:.75}#pv.ar .arbadge{position:absolute;top:-6px;right:-10px;background:#4b8a3a;border-radius:9px;padding:0 5px;font-size:11px;font-style:normal}#pv.ar .arbadge.cd{right:auto;left:-10px;background:#8a3a3a}#pv.ar .arpile{display:inline-flex;flex-direction:column;align-items:center;justify-content:center;width:40px;height:54px;min-height:0;border-radius:6px;border:1px solid #fff3;
 background:#0005;color:#eee;padding:0;font-size:16px;line-height:1.1}#pv.ar .arpile b{font-size:12px}#pv.ar .arcz{display:flex;gap:4px;align-items:center;min-width:30px;min-height:54px;border:1px dashed #e0a74466;border-radius:6px;padding:2px;justify-content:center}#pv.ar .arbacks{display:flex;align-items:center;margin-left:auto;padding-left:8px}#pv.ar .arbacks i{width:16px;height:24px;margin-left:-8px;border-radius:3px;background:linear-gradient(135deg,#5a3d22,#2a1b10);border:1px solid #a8843a}#pv.ar .arbacks b{margin-left:6px}#pv.ar .arfield{flex:1;display:flex;flex-direction:column;overflow:auto;padding:2px 10px;min-height:0}#pv.ar .arhalf{flex:1;display:flex;flex-direction:column;justify-content:flex-end;gap:6px;min-height:70px;border-radius:10px;padding:4px}#pv.ar .arhalf.top{justify-content:flex-start}#pv.ar .armid{height:2px;background:linear-gradient(90deg,transparent,#e0a74488,transparent);margin:4px 0;flex-shrink:0}#pv.ar .arrow{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;align-items:flex-end;min-height:10px}#pv.ar .arstack{position:relative;display:flex}#pv.ar .arstack .arc+.arc{margin-left:calc(var(--cw)*var(--tk,1)*-.45)}#pv.ar .arstackn{position:absolute;bottom:-4px;right:-4px;background:#000c;border-radius:8px;padding:0 5px;font-size:11px;z-index:5}#pv.ar .arempty{opacity:.35;font-size:13px;padding:16px}#pv.ar .arc{position:relative;width:calc(var(--cw)*var(--tk,1)*var(--bfk,.8));aspect-ratio:.716;border-radius:6px;cursor:pointer;touch-action:none;transition:transform .15s,box-shadow .15s;flex-shrink:0}#pv.ar .arc img{width:100%;height:100%;object-fit:cover;border-radius:6px;display:block;pointer-events:none;box-shadow:0 2px 6px #0009}#pv.ar .arc .arn{display:block;width:100%;height:100%;box-sizing:border-box;border:1px solid #a8843a;border-radius:6px;background:#2a2018;color:#f1e3c6;font-size:11px;padding:4px;overflow:hidden}#pv.ar .arc.sm{width:calc(var(--cw)*var(--tk,1)*var(--bfk,.8)*.72)}#pv.ar .arc.tap{transform:rotate(90deg) scale(.88);margin:0 calc(var(--cw)*var(--tk,1)*.13)}#pv.ar .arc.sel{box-shadow:0 0 0 3px #e0a744,0 0 18px #e0a744;border-radius:7px}#pv.ar .arc.cmd img,#pv.ar .arc.cmd .arn{outline:2px solid #e0a744}#pv.ar .arc.dragging{opacity:.3}#arghost{position:fixed;z-index:500;pointer-events:none;width:calc(var(--cw)*var(--tk,1)*.85);aspect-ratio:.716;transform:rotate(-5deg) scale(1.08);opacity:.92}#arghost img{width:100%;height:100%;border-radius:6px;object-fit:cover}#pv.ar .drop-on{outline:3px dashed #e0a744;outline-offset:2px;background:#e0a74418}#pv.ar .arcnt,#pv.ar .artax{position:absolute;top:3px;right:3px;background:#000c;color:#fff;border-radius:9px;padding:0 6px;font-size:12px;z-index:3}#pv.ar .artax{background:#b8891f}#pv.ar .arc.txt{aspect-ratio:auto;width:calc(var(--cw)*var(--tk,1)*1.25);min-height:calc(var(--cw)*var(--tk,1)*.6)}#pv.ar .arc.txt.sm{width:calc(var(--cw)*var(--tk,1)*1.05)}#pv.ar .arc.txt.tap{transform:none;margin:0;opacity:.55}#pv.ar .arc.txt.tap .ctile{border-style:dashed}#pv.ar .ctile{background:#2a2018;color:#f1e3c6;min-height:inherit}#pv.ar .arbottom{display:flex;align-items:flex-end;gap:8px;padding:4px 10px 8px;background:linear-gradient(0deg,#000a,transparent);flex-shrink:0}#pv.ar .arpl.me{flex-wrap:wrap;width:150px;justify-content:center;padding:0;gap:5px}#pv.ar .arhand{flex:1;display:flex;justify-content:center;align-items:flex-end;min-height:calc(var(--cw)*var(--tk,1)*.95);padding-top:10px;min-width:0;margin-bottom:calc(var(--cw)*var(--tk,1)*-.45)}#pv.ar .arhand .arc{width:calc(var(--cw)*var(--tk,1));margin-left:calc(var(--ov,0px)*-1);transform:rotate(var(--rot)) translateY(var(--lift));transform-origin:50% 130%}#pv.ar .arhand .arc:first-child{margin-left:0}#pv.ar .arhand .arc.txt{width:calc(var(--cw)*var(--tk,1)*1.3)}@media(hover:hover){#pv.ar .arhand .arc:hover{transform:translateY(-38%) scale(1.15);z-index:60!important}}#pv.ar .arhand .arc.sel{transform:translateY(-38%) scale(1.15);z-index:60!important}#pv.ar .argobox{display:flex;flex-direction:column;align-items:center;gap:6px;flex-shrink:0}#pv.ar .argo{min-width:124px;min-height:52px;border-radius:26px;border:0;background:linear-gradient(180deg,#f2b84f,#c47d16);color:#1b140e;font-weight:bold;font-size:16px;box-shadow:0 3px 10px #000a;padding:0 18px;cursor:pointer}#pv.ar .argo:hover{filter:brightness(1.1)}#pv.ar #arsel{position:absolute;left:50%;transform:translateX(-50%);top:52px;z-index:70;background:#1b140ef2;border:1px solid #e0a744;border-radius:12px;
 padding:6px 8px;display:flex;flex-wrap:wrap;gap:5px;align-items:center;max-width:94vw;box-shadow:0 4px 18px #000b}#pv.ar .arselname{margin-right:4px;max-width:200px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}#pv.ar #arsel button{min-height:34px;padding:2px 10px}#pv.ar #arsel{flex-wrap:nowrap;width:max-content}#pv.ar #arsel.open{flex-wrap:wrap;width:min(420px,94vw)}#pv.ar .arselname{font-size:14px}#pv.ar .armorelist{display:none;width:100%;flex-wrap:wrap;gap:5px}#pv.ar #arsel.open .armorelist{display:flex}#pv.ar #arsheet{position:absolute;top:50px;right:0;bottom:0;width:min(380px,92vw);z-index:90;background:#1b140ef8;border-left:1px solid #a8843a;overflow:auto;padding:10px 12px;box-shadow:-6px 0 20px #000a}#pv.ar .arsh{display:flex;justify-content:space-between;align-items:center;font-size:17px;margin-bottom:6px}#pv.ar .arsec{margin:8px 0;display:flex;flex-wrap:wrap;gap:6px;align-items:center}#pv.ar .arsec h4{width:100%;margin:4px 0 0;font-size:12px;opacity:.65;font-weight:normal;text-transform:uppercase;letter-spacing:.06em}#pv.ar .arsec .arbig{min-width:56px;min-height:44px;font-size:17px}#pv.ar .argrid{display:flex;flex-wrap:wrap;gap:6px}#pv.ar #arsheet table.duel{font-size:13px;color:#eee}#pv.ar #pvlog div{font-size:13px;padding:2px 0;border-bottom:1px solid #fff1}#pv.ar #armull{position:absolute;inset:0;z-index:80;background:#000c;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:10px;overflow:auto}#pv.ar #armull h3{margin:0}#pv.ar .armullrow{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}#pv.ar .armullrow .arc{width:min(calc(var(--cw)*var(--tk,1)*1.2),calc((100vw - 90px)/7),calc(42vh*.716))}#pv.ar .armullrow .arc.txt{width:calc(var(--cw)*var(--tk,1)*1.5)}#pv.ar .armullbtn{display:flex;gap:10px;align-items:center;flex-wrap:wrap;justify-content:center}#pv.ar .arsub{opacity:.8}#pv.ar .armullb{min-height:44px;border-radius:22px;padding:0 18px}#pv.ar .arsmall{font-size:12px}#pv.ar #artoast{position:absolute;top:50px;left:50%;transform:translateX(-50%);background:#000d;color:#f1e3c6;padding:5px 14px;border-radius:14px;font-size:13px;z-index:60;pointer-events:none;opacity:0;max-width:80vw;text-align:center}#pv.ar #artoast.fade{animation:artoast 2.8s ease}@keyframes artoast{0%{opacity:0}8%{opacity:1}75%{opacity:1}100%{opacity:0}}#pv.ar .arrot{display:none}@media(max-width:760px){#pv.ar{--cw:70px}#pv.ar .aravatar{width:50px;height:50px}#pv.ar .arlife{font-size:19px}#pv.ar .arpile{width:32px;height:44px;font-size:13px}#pv.ar .argo{min-width:96px;min-height:46px;font-size:14px}#pv.ar .arphname{display:none}#pv.ar .arpl.me{width:118px}}@media(orientation:portrait) and (max-width:600px){#pv.ar .arrot{display:inline-flex}#pv.ar #arsel,#pv.ar #arsel.open{flex-wrap:wrap;width:94vw;justify-content:center}#pv.ar .arselname{width:100%;max-width:none;text-align:center}#pv.ar .armullrow .arc{width:calc((100vw - 60px)/4)}#pv.ar .arph:not(.on){display:none}#pv.ar .arinfo{font-size:12px;gap:4px}#pv.ar .arbottom{flex-wrap:wrap}#pv.ar .arhand{order:3;width:100%;flex-basis:100%}#pv.ar .arpl.me{width:auto;flex-wrap:nowrap}#pv.ar .argobox{margin-left:auto;flex-direction:row}}@media(orientation:landscape) and (max-height:520px){#pv.ar #arsheet{top:36px}#pv.ar{--cw:26vh;--bfk:.62}#pv.ar .arhalf,#pv.ar .arhalf.top{flex-direction:row;align-items:center;justify-content:center;min-height:0}#pv.ar .arhalf .arrow{flex-wrap:nowrap}#pv.ar .arhalf.top .arrow.lands{order:0}#pv.ar .arfield{justify-content:center}#pv.ar .armid{margin:2px 0}#pv.ar .artop{padding:2px 8px}#pv.ar .aricon{width:30px;height:30px;font-size:14px}#pv.ar .arph{width:22px;height:22px;font-size:11px}#pv.ar .arphname{display:none}#pv.ar .aravatar{width:44px;height:44px;border-width:2px}#pv.ar .arlife{font-size:17px}#pv.ar .arname{display:none}#pv.ar .arpl.top{padding:2px 8px}#pv.ar .arpile{width:28px;height:38px;font-size:12px}#pv.ar .arcz{min-height:38px}#pv.ar .arbottom{padding:2px 8px 4px}#pv.ar .arpl.me{width:112px}#pv.ar .argo{min-height:42px;min-width:92px;font-size:14px}#pv.ar .arhand{padding-top:8px}#pv.ar #arsel{top:38px}}

/* Spielmatten und Avatar-Ring in den Farben des Decks */
#pv.ar{background:var(--matglow,none),radial-gradient(ellipse at 50% 55%,#2d3b30 0%,#18201a 65%,#0c100d 100%)}
#pv.ar[data-mat=colors]{background:var(--matglow,none),radial-gradient(ellipse at 50% 50%,#2a2622 0%,#16120f 70%,#0b0908 100%)}
#pv.ar[data-mat=felt]{background:repeating-linear-gradient(45deg,#ffffff05 0 2px,transparent 2px 6px),radial-gradient(ellipse at 50% 55%,#2f4a36 0%,#1a2a1e 65%,#0d150f 100%)}
#pv.ar[data-mat=parch]{background:radial-gradient(ellipse at 50% 45%,#5a4a32 0%,#3a2e1f 60%,#1e170f 100%);}
#pv.ar[data-mat=cmd]{background:linear-gradient(#0009,#000c),var(--matimg,none) center/cover no-repeat,#16120f}
#pv.ar .aravatar{border:3px solid transparent;background:radial-gradient(circle at 35% 30%,#4a3b2a,#1b140e) padding-box,var(--ring,#888) border-box}
#pv.ar .arpl.act .aravatar{box-shadow:0 0 16px #e0a744cc}
#pv.ar .arcz{align-items:flex-start;height:max-content}#pv.ar .armid{height:3px;background:linear-gradient(90deg,transparent,#f3ecd255,#2f74b855,#4a3f4855,#c8402c55,#2f7d4555,transparent)}
</style>
<style id=mobcss>
/* ---------- Handyansicht (body.mob): wird per Geräteerkennung oder von Hand gesetzt ---------- */
#layoutbtn{position:fixed;top:10px;right:330px;z-index:60;border:1px solid #999;background:#fff;border-radius:16px;padding:4px 10px;cursor:pointer}
body.mtg #layoutbtn{background:#241a12;color:#e2bd5b;border-color:#a8843a}
#mobnav,#mobmore{display:none}
body.mob{font-size:16px;padding-bottom:calc(68px + env(safe-area-inset-bottom));overflow-x:hidden}
body.mob #top{margin-top:2px}body.mob #top h2{font-size:1.3em;margin:.15em 0 .1em;padding-right:120px;text-align:left;white-space:nowrap}
body.mob .wotc{font-size:.72em;line-height:1.35;text-align:left;margin:0 0 6px;opacity:.85;position:static}
body.mob #mainnav{display:none}
body.mob #theme,body.mob #helpbtn,body.mob #layoutbtn{position:absolute;top:8px;margin:0;padding:0;width:34px;height:34px;min-height:0;font-size:0;z-index:70;border-radius:50%;overflow:hidden}
body.mob #theme::before{content:'🎨';font-size:17px}body.mob #helpbtn::before{content:'❓';font-size:17px}body.mob #layoutbtn::before{content:'📱';font-size:17px}
body.mob #helpbtn{right:8px}body.mob #theme{right:48px}body.mob #layoutbtn{right:88px}
body.mob #info{font-size:.7em;line-height:1.35;opacity:.7;margin:4px 0;position:static}
body.mob #upd{font-size:.8em;padding:4px 8px}body.mob #upd button{padding:2px 6px;min-height:0}
body.mob input:not([type=checkbox]):not([type=radio]):not([type=file]):not([type=range]),body.mob select,body.mob textarea{width:100%!important;max-width:100%!important;box-sizing:border-box;font-size:16px;margin:3px 0}
body.mob .ac{display:block;width:100%}
body.mob button:not(.qh){min-height:40px}body.mob .qh{min-height:0}
body.mob .pip,body.mob .cibtns button,body.mob #tfield button{min-height:0}
body.mob table:not(.gtab){display:block;overflow-x:auto;max-width:100%;-webkit-overflow-scrolling:touch}
body.mob img,body.mob svg{max-width:100%}body.mob svg{height:auto}
body.mob #out button,body.mob #cmp button{min-height:30px;padding:2px 7px;font-size:.85em;margin:1px}
body.mob #mydecks table,body.mob #mydecks tbody,body.mob #mydecks tr,body.mob #mydecks td{display:block;width:auto}
body.mob #mydecks thead,body.mob #mydecks tr:first-child th{display:none}
body.mob #mydecks tr{border:1px solid rgba(168,132,58,.5);border-radius:10px;padding:6px 8px;margin:8px 0}
body.mob #mydecks td{border:0;padding:1px 0}body.mob #mydecks td:first-child{font-weight:bold;font-size:1.05em}
body.mob #mydecks td:last-child{display:flex;flex-wrap:wrap;gap:4px;margin-top:4px}body.mob #mydecks td:last-child button{min-height:34px;padding:2px 8px;font-size:.88em}
body.mob h3{font-size:1.1em}
body.mob details.tabbox,body.mob .openline,body.mob .csugbox,body.mob .gcard{padding:8px 10px}
body.mob .openline{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
body.mob .hero{padding:14px 10px;margin:4px 0 12px}body.mob .orbs{display:none}body.mob .herot{font-size:1.45em}body.mob .herosub{font-size:.98em}
body.mob .tiles{grid-template-columns:1fr 1fr;gap:8px}
body.mob .tile{min-height:0;aspect-ratio:auto;padding:8px;display:flex;flex-direction:row;align-items:center;gap:8px}
body.mob .tile .ta{font-size:1.6em;order:-1;margin:0;padding:0;background:none;border:0;min-height:0;height:auto;width:auto;box-shadow:none}
body.mob .tile .tt{font-size:.92em;margin:0;padding:0;background:none;border:0;box-shadow:none}
body.mob .tile .tx{display:none}
body.mob .gpick{grid-template-columns:1fr 1fr}body.mob .gbtn{padding:8px}body.mob .gbtn span{display:none}
body.mob #csug .cgrid{grid-template-columns:1fr 1fr;gap:6px}body.mob #csug .cc .tx{display:none}
body.mob .cols{display:block}body.mob .cols>div{width:auto;min-width:0}
body.mob #legal{font-size:.68em;padding:8px}
body.mob #tfield{height:calc(100vh - 150px)}
body.mob #dlg>div,body.mob #help>div{margin:4px;padding:8px 10px;max-height:calc(100vh - 90px)}
body.mob #mobnav{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:80;background:#1b140e;border-top:1px solid #a8843a;padding:4px 2px calc(4px + env(safe-area-inset-bottom));justify-content:space-around}
body.mob:not(.mtg) #mobnav{background:#fafafa;border-top-color:#bbb}
#mobnav a,#mobnav button{flex:1;display:flex;flex-direction:column;align-items:center;gap:1px;font-size:.66em;text-decoration:none;color:#e2bd5b;background:none;border:0;padding:3px 0;min-height:48px;cursor:pointer;box-shadow:none}
body:not(.mtg) #mobnav a,body:not(.mtg) #mobnav button{color:#333}
#mobnav .i{font-size:1.75em;line-height:1.1}#mobnav .on{color:#fff;background:rgba(168,132,58,.35);border-radius:10px}
body:not(.mtg) #mobnav .on{background:#e6dcc4;color:#000}
#mobnav a.neu{color:#7bd88a}body:not(.mtg) #mobnav a.neu{color:#2f7d3e}
body.mob #mobmore.open{display:block;position:fixed;left:0;right:0;bottom:calc(60px + env(safe-area-inset-bottom));z-index:79;background:#241a12;border-top:1px solid #a8843a;padding:8px;box-shadow:0 -6px 18px rgba(0,0,0,.5)}
body.mob:not(.mtg) #mobmore.open{background:#fff;border-top-color:#bbb}
#mobmore a{display:block;padding:12px 10px;font-size:1.05em;text-decoration:none;color:inherit;border-bottom:1px solid rgba(128,100,60,.3)}
</style>
<meta name=viewport content="width=device-width, initial-scale=1">
<link rel=stylesheet href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&display=swap">
<button type=button id=layoutbtn title="Ansicht: automatisch / Handy / PC"></button><button type=button id=theme></button><button type=button id=helpbtn data-h=start>❓ Hilfe</button>
<div id=help><div><button type=button class=x id=helpx>✕ Schließen</button><h2 id=h-top>Hilfe zur Manaschmiede</h2>
<nav class=htoc><a data-h=start>Erste Schritte</a> · <a data-h=commander>Was ist Commander?</a> · <a data-h=bauen>Deck bauen</a> ·
<a data-h=anpassen>Deck anpassen</a> · <a data-h=import>Importieren &amp; Speichern</a> · <a data-h=export>Exportieren</a> ·
<a data-h=gegner>Gegner &amp; Vergleich</a> · <a data-h=combos>Combos</a> · <a data-h=brackets>Brackets</a> · <a data-h=precons>Precons</a> · <a data-h=duell>Duell mit Forge</a> ·
<a data-h=regeln>Regeln</a> · <a data-h=suche>Kartensuche</a> · <a data-h=update>Aktualisierung</a> · <a data-h=geraete>Handy &amp; andere Geräte</a> ·
<a data-h=begriffe>Begriffe</a> · <a data-h=probleme>Probleme lösen</a></nav>

<h3 id=h-start>Erste Schritte</h3>
<ol><li><b>Starten:</b> Doppelklick auf <code>Commander-DB starten.bat</code> (oder in der Eingabeaufforderung <code>python commander_db_vNN.py serve</code>, NN ist die Versionsnummer). Es öffnet sich ein schwarzes Fenster. <b>Lass es offen</b>, solange du die Datenbank benutzt. Der Browser öffnet die Seite automatisch (sonst <code>http://localhost:8000</code> eingeben).</li>
<li><b>Am Handy:</b> Die Manaschmiede erkennt Mobiltelefone und schaltet auf die Handyansicht um: Navigation als Leiste am unteren Rand (Start, Neu hier?, Deck, Duell, Tisch, ☰ Mehr), kompakter Kopf mit 📱 Ansicht, 🎨 Optik und ❓ Hilfe, Felder über die volle Breite. Mit dem Ansichts-Knopf (📱/🖥 oben rechts) wechselst du zwischen „automatisch“, „immer Handy“ und „immer PC“, was auf Tablets hilft.</li>
<li><b>Beim Start</b> prüft das Programm im Hintergrund, ob es neue Regeln, Precons oder Kartendaten gibt. Den Fortschritt siehst du oben im Balken. Du kannst währenddessen schon arbeiten.</li>
<li><b>Gespeichertes Deck weiterbearbeiten:</b> oben im Tab „Deck bauen“ bei „📂 Gespeichertes Deck öffnen“ auswählen, oder auf der Willkommen-Seite unter „Zuletzt gespeichert“ anklicken. Verwalten (Versionen, Teilen, Löschen) im Tab „Meine Decks“.</li>
<li><b>Ein erstes Deck:</b> auf der Willkommen-Seite (oder im Tab „Deck bauen“ bei „Commander“) einen Namen eintippen (z. B. „Atraxa“), Vorschlag anklicken und <b>Deck vorschlagen</b> drücken. Darunter erscheint ein vollständiges Deck mit 100 Karten.</li>
<li><b>Beenden:</b> das schwarze Fenster schließen (oder dort Strg+C drücken). Gespeicherte Decks bleiben erhalten.</li></ol>
<p><b>Aufbau der Seite:</b> Die Seite beginnt mit der <b>Willkommen-Seite</b>: dort einen Commander eintippen und „Deck bauen“ drücken oder eine der Karten anklicken. Oben führen die <b>Tabs</b> zu allen Bereichen: <b>Deck bauen</b> (Assistent und Deckansicht), <b>Gegner &amp; Duell</b> (Vergleich, Combos, Forge), <b>Meine Decks</b> (Import, gespeicherte Decks), <b>Sammlung</b>, <b>Spieltisch</b>, <b>Kartensuche</b> und <b>Regeln</b>. Die Zurück-Taste des Browsers springt zum vorigen Tab.</p>
<p>Überall auf der Seite findest du kleine <span class=qh>?</span>-Knöpfe. Ein Klick darauf öffnet die passende Stelle dieser Hilfe. Oben rechts lässt sich die Optik zwischen <b>Magic-Stil</b> und <b>neutral</b> umschalten.</p>

<h3 id=h-commander>Was ist Commander? (in einer Minute)</h3>
<ul><li>Jedes Deck hat <b>genau 100 Karten</b>, davon ist eine der <b>Commander</b>, meist eine legendäre Kreatur. Er liegt in der Kommandozone statt im Stapel und kann von dort jederzeit gespielt werden (jedes weitere Mal kostet er 2 Mana mehr).</li>
<li>Jede Karte darf nur <b>einmal</b> vorkommen. Ausgenommen sind Standardländer wie Wald oder Insel.</li>
<li>Die <b>Farbidentität</b> des Commanders bestimmt, welche Farben im Deck erlaubt sind. Ein grün-blauer Commander erlaubt nur grüne, blaue und farblose Karten.</li>
<li>Jeder beginnt mit <b>40 Lebenspunkten</b>. Wer von einem einzelnen Commander insgesamt <b>21 Kampfschaden</b> erhält, verliert ebenfalls.</li>
<li><b>Precons</b> sind die fertigen, offiziell verkauften Commander-Decks und eignen sich gut als Vergleichsmaßstab.</li>
<li><b>Brackets</b> (Stufen 1–5) beschreiben, wie stark ein Deck ist, damit am Tisch ähnlich starke Decks gegeneinander spielen.</li></ul>

<h3 id=h-bauen>Deck bauen lassen (Deckbau-Assistent)</h3>
<p>Alle Felder sind freiwillig, eine Angabe genügt.</p>
<ul><li><b>Commander:</b> beim Tippen erscheinen Vorschläge; Tippfehler werden toleriert. Die Farbidentität wird automatisch übernommen. <b>Zwei Commander</b> (Partner, Hintergrund) mit „ + “ trennen, z. B. „Thrasios, Triton Hero + Tymna the Weaver“.</li>
<li><b>Thema:</b> z. B. Mill, Lifegain, Tokens, Voltron. Das Deck wird um dieses Thema herum gebaut.</li>
<li><b>Noch kein Commander?</b> Lieblingsfarben über die Farbknöpfe (W U B R G ◇) anklicken und/oder ein Thema eintragen, deutsch oder englisch, z. B. „Drachen“, „Elfen“, „Tokens“, „Friedhof“, „Artefakte“, „Lebensgewinn“, auch Verzauberungs- und Artefakttypen wie „Sagen“, „Auren“ oder „Ausrüstungen“. „💡 Commander vorschlagen“ zeigt zwölf passende Commander mit Bild, Begründung und Regeltext. Jedes Mal kommt eine neue Mischung aus ⭐ beliebten Commandern, 💎 Geheimtipps (seltener gespielt) und 💶 günstigen Optionen, bei offenen Farben aus verschiedenen Farbkombinationen. Commander, die das Thema in ihrem Text ausdrücklich unterstützen, stehen als „passt genau“ vorne. „🔄 Andere Vorschläge“ zeigt weitere, noch nicht gezeigte Commander; „🔀 Neu mischen“ beginnt von vorn. Normalerweise müssen die Farben genau passen; „auch mit weniger Farben“ zeigt zusätzlich Commander mit einem Teil der Farben. „Keine Game Changer“ und „Höchstpreis je Karte“ gelten auch hier. Mit „✔ Diesen Commander nehmen“ wird er übernommen. Wird ein Deck ohne Commander vorgeschlagen, erscheinen die Vorschläge automatisch.</li>
<li><b>Farbidentität:</b> nur nötig, wenn du keinen Commander angibst (W = Weiß, U = Blau, B = Schwarz, R = Rot, G = Grün).</li>
<li><b>Karten, die ins Deck sollen:</b> eigene Lieblingskarten, eine pro Zeile. Mit dem Feld darüber und Enter fügst du sie hinzu.</li>
<li><b>Keine Game Changer:</b> lässt besonders starke Karten weg, sinnvoll für entspannte Runden.</li>
<li><b>Höchstpreis je Karte / Budget gesamt:</b> keine Karte über dem Höchstpreis bzw. das ganze Deck (ohne Standardländer) bleibt unter dem Budget. Karten ohne bekannten Preis werden dann nicht vorgeschlagen.</li>
<li><b>Nicht verfügbare Karten:</b> Karten, die du nicht besitzt oder nicht spielen willst. Sie werden nie vorgeschlagen; die Liste merkt sich der Browser.</li></ul>
<p>Zuerst wählt der Assistent Karten, die zum <b>Text des Commanders</b> passen (z. B. Marken, Spielsteine, Lebensgewinn oder seine Kreaturentypen). Diese Gruppe heißt „Synergie mit dem Commander“. Der Rest beruht auf der allgemeinen Beliebtheit (EDHREC). Bei mehreren Farben werden bevorzugt Länder genommen, die zwei oder mehr Deckfarben liefern. Das Ergebnis ist ein Startpunkt, das Feintuning bleibt bei dir.</p>

<h3 id=h-anpassen>Deck ansehen und anpassen</h3>
<ul><li><b>Ansicht:</b> „Liste“ (kompakt, mit Preisen und Links) oder „Kartenbilder“.</li>
<li><b>⇄ Tauschen:</b> zeigt passende Alternativen mit derselben Aufgabe (z. B. anderes Ramp). Filter: keine Game Changer, Höchstpreis. Optional wird die alte Karte als „nicht verfügbar“ gemerkt.</li>
<li><b>➕ Karte hinzufügen:</b> Namen eintippen und Vorschlag wählen. Die Karte wird geprüft (Commander-legal, passende Farbidentität, nicht doppelt) und unter „Manuell hinzugefügt“ einsortiert. Standardländer können mehrfach hinzugefügt werden.</li>
<li><b>✕ Entfernen, + / − bei Standardländern:</b> nimmt eine Karte heraus bzw. ändert die Anzahl eines Standardlands. Danach zeigt der Kopf des Decks an, wie viele Karten fehlen oder zu viel sind.</li>
<li><b>🏷 Tags:</b> eigene Kategorien je Karte (z. B. Ramp, Wincon). Sie erscheinen als Etiketten in der Liste und im Bereich „Nach Tags“ zusammengefasst.</li>
<li><b>↓ Maybe / Maybeboard:</b> Kandidaten, die (noch) nicht ins Deck zählen. Mit „↑ ins Deck“ holst du sie zurück; das Feld darüber nimmt neue Kandidaten auf.</li>
<li><b>Tokens und Spielmaterial:</b> listet alle Tokens, die Karten des Decks erzeugen, mit der erzeugenden Karte.</li>
<li><b>🖨 Proxys drucken:</b> Druckansicht in Originalgröße (63 × 88 mm, 9 je Seite, A4 oder Letter). Du findest sie im Deck, in der Sammlung unter „Proxy-Druck“ für beliebige Kartenlisten und im Kaufassistenten. Wahlweise Kartenbild oder tintensparende Textfassung, Rückseiten doppelseitiger Karten, Tokens, nur fehlende Karten, ein bestimmter Druck per „(SET) Nr“. <b>Nur Kopien zum privaten Testen:</b> keine echten Karten, nicht verkaufen oder als echt ausgeben, in Turnieren nicht erlaubt; jede Kopie trägt fest den Vermerk „PROXY – keine echte Karte“. Mit „Drucken / als PDF speichern“ entsteht eine PDF-Datei; beim Drucken 100 % bzw. „Tatsächliche Größe“ wählen. Kartenrückseiten werden nicht gedruckt: die ausgeschnittene Kopie zusammen mit einer echten, wertlosen Karte (z. B. Standardland) in eine Hülle stecken, Kopie nach vorne. Dann sehen alle Karten von hinten gleich aus, auch in durchsichtigen Hüllen.</li>
<li><b>💡 Empfehlungen, Lücken und Filter:</b> Unter „Lücken nach Funktion“ zählt das Programm Ramp, Kartenziehen, gezieltes Removal und Board-Wipes und vergleicht mit Richtwerten (etwa 10 / 10 / 8 / 3). Fehlt etwas, stehen je Funktion sechs passende, verbreitete Karten in deinen Farben darunter (➕ fügt sie ein). „nur aus meiner Sammlung“ zeigt nur Karten, die du besitzt; „höchstens … € je Karte“ setzt eine Preisgrenze (eigene Karten gelten als kostenlos). Im Server-Betrieb fließen auch die veröffentlichten Galerie-Decks der anderen Benutzer ein.</li>
<li><b>💡 Empfehlungen:</b> sucht ähnliche Decks (Precons, deine gespeicherten Decks und im Server-Betrieb die Galerie mit mindestens drei gemeinsamen Karten) und schlägt Karten vor, die dort oft mit deinen Karten zusammen gespielt werden oder zum Commander-Text passen. „Streichen erwägen“ nennt Karten mit wenig Rückhalt; mit 🏷 „Wincon“ oder „Combo“ markierte Karten werden nie vorgeschlagen. Decks mit guter Siegquote im Spielprotokoll zählen stärker.</li>
<li><b>Frust-Index:</b> eigene Schätzung aus dem Kartentext, wie sehr ein Deck Mitspieler ärgern kann (Massen-Landzerstörung, Extra-Züge, Stax, Diebstahl, Gegenzauber, Tutoren, Game Changer). Er ersetzt die Salt-Werte von EDHREC, für die es keine offizielle Schnittstelle gibt.</li>
<li><b>Preisentwicklung:</b> bei jeder Kartenaktualisierung (einmal täglich beim Start) werden geänderte Preise gesichert. Das Deck zeigt seinen Wert über die Zeit und die Karten mit den größten Änderungen der letzten 30 Tage.</li>
<li><b>Notizen / Primer:</b> freier Text zum Deck. Tags, Maybeboard und Notizen werden mit dem Deck gespeichert und beim Laden wiederhergestellt.</li>
<li><b>Alle Game Changer ersetzen:</b> tauscht alle auf einmal gegen die beste Alternative.</li>
<li><b>Manakurve:</b> wie viele Karten welche Kosten haben. Viele günstige Karten = schnelles Deck.</li>
<li><b>Preise</b> sind Euro-Richtwerte aus den Scryfall-Daten (Marktpreise von Cardmarket).</li>
<li><b>Manabasis:</b> zählt je Farbe die Quellen (Länder einschließlich Fetch- und Suchländern, Mana-Artefakte/-Kreaturen bis Manawert 2; Ramp-Zauber bis Manawert 3, die ein Land suchen, zählen halb) und berechnet, wie wahrscheinlich du jede Karte rechtzeitig wirken kannst. „Zu wenig Quellen“ heißt: mehr Länder oder Mana dieser Farbe einplanen. Die schwierigsten Karten stehen rechts.</li>
<li><b>Probehand:</b> zieht 7 zufällige Karten; „Karte ziehen“ simuliert die nächsten Züge, „Mulligan“ mischt neu (London-Mulligan). Darüber steht eine Statistik aus 20.000 Starthänden: wie oft die Hand behaltbar ist (2–5 Länder) und wie oft du in Zug 1–4 ein Land spielen kannst.</li>
<li><b>Deck-Editor:</b> „↶ Rückgängig“ / „↷ Wiederherstellen“ (auch Strg+Z / Strg+Y) nehmen jede Änderung an der Liste zurück (60 Schritte). Eigene Gruppen: eine Karte in eine andere Gruppe ziehen (beim Ziehen erscheint unten eine Leiste mit allen Gruppen, dem Maybeboard und „Entfernen“) oder bei der Karte ⇄ antippen und eine Gruppe wählen bzw. eine neue anlegen. Eigene Gruppen werden mit dem Deck gespeichert, auf der Teilen-Seite als Abschnitte gezeigt und beim Archidekt-Export als Kategorie mitgegeben. „☐ Mehrfachauswahl“ setzt Häkchen vor die Karten; die markierten Karten lassen sich gemeinsam verschieben, taggen, ins Maybeboard legen oder entfernen. Die Ansicht „Stapel“ zeigt die Karten als Bildstapel nach Manawert; antippen sucht Ersatz.</li>
<li><b>🎮 Testspielfeld:</b> spielt das Deck allein Zug für Zug durch (Goldfischen): Starthand behalten oder Mulligan (der erste ist frei), dann ziehen, Länder und Zauber spielen, Commander wirken (Steuer +2 pro Wurf). Der Spieltisch ist aufgebaut wie bei digitalen Kartenspielen: oben der Gegner (Leben, Stapel, verdeckte Hand), in der Mitte das Spielfeld (Kreaturen und Co. zur Mitte, Länder nach außen, gleiche Länder gestapelt), unten deine Hand als Fächer. Links unten dein Avatar mit Lebenspunkten, daneben 📚 Bibliothek, 🪦 Friedhof, 🌀 Exil und die Kommandozone; rechts unten der große Knopf „Zug beenden“ (Leertaste) und 🃏 zum Ziehen. Oben die Phasenleiste (antippen markiert die Phase, die aktuelle antippen = weiter). <b>Bedienen:</b> Karte antippen zeigt nur die passenden Aktionen (z. B. „Ausspielen“, „Tappen“, „Wirken“), „Mehr“ den Rest; Karten lassen sich auch ziehen: auf das Spielfeld, 🪦, 🌀, 📚, die Hand oder die Kommandozone. Zweimal antippen tappt, lange drücken oder Rechtsklick zeigt die Karte groß. Avatar antippen: Leben, Gift, Commander-Schaden. Alles Weitere liegt hinter ⚙: Spielmatte (Farben des Decks, Filz, Pergament, Bild des Commanders), Textansicht „Aa“, Kartengröße, Querformat, Tokens aus dem Deck, Würfel und Münze, Statistik, Protokoll, Partie beenden. Kurze Meldungen zeigen, was gerade passiert ist; ↶ nimmt Schritte zurück (Taste Z). Regeln prüft der Tisch nicht.</li>

<h3 id=h-import>Importieren und Speichern</h3>
<ul><li><b>Speichern:</b> im umrahmten Feld „💾 Deck speichern“ direkt unter der Deck-Überschrift einen Namen eingeben und <b>Speichern</b> klicken. Gleicher Name = altes Deck wird überschrieben.</li>
<li><b>Gespeicherte Decks</b> findest du im aufklappbaren Bereich „Deck importieren &amp; gespeicherte Decks“, mit den Knöpfen „Mein Deck“ (laden), „Gegner“ (als Gegner verwenden), „Versionen“ und „Löschen“ (zweimal klicken).</li>
<li><b>Teilen:</b> erzeugt einen Link auf eine Nur-Lese-Seite des gespeicherten Decks (mit Bildern, Tags, Notizen). „Link widerrufen“ macht ihn sofort ungültig. Im lokalen Betrieb funktioniert der Link nur auf dem PC bzw. im Heimnetz, im Server-Betrieb im Internet.</li>
<li><b>📤 Senden:</b> Im Server-Betrieb wählst du einen anderen Benutzer und optional eine Nachricht; das Deck landet in dessen Postfach („📥 Erhaltene Decks“ oben unter Meine Decks, mit Zähler am Menüpunkt) und wird dort mit „Übernehmen“ als eigenes Deck gespeichert (bei gleichem Namen mit „(von …)“) oder abgelehnt. Ohne Benutzerkonten (lokal oder im Heimnetz) erzeugt „Senden“ einen Link samt QR-Code, den du über „Senden über …“ z. B. per Messenger verschickst. Die andere Person fügt den Link in ihrer Manaschmiede unter „Deck importieren“ ins Link-Feld ein; das Deck wird komplett übernommen. Der Link funktioniert, solange deine Manaschmiede für die andere Person erreichbar ist.</li>
<li><b>Versionen:</b> jedes Mal, wenn du ein Deck mit geänderter Liste speicherst, wird die vorige Fassung aufgehoben (bis zu 30). Unter „Versionen“ siehst du, was seitdem dazugekommen oder weggefallen ist, und kannst eine alte Fassung wiederherstellen. Die aktuelle bleibt dabei ebenfalls als Version erhalten. Beim Speichern kannst du eine <b>Notiz zur Änderung</b> mitgeben; im Versionsfenster lassen sich <b>zwei beliebige Fassungen vergleichen</b>.</li>
<li><b>Deutsche Kartennamen:</b> Listen, Sammlungen und die Kartensuche verstehen auch deutsche (und andere fremdsprachige) Namen, z. B. „Blitzschlag“ → Lightning Bolt. Unbekannte Namen werden einmalig bei Scryfall nachgeschlagen und dann gemerkt; dafür ist eine Internetverbindung nötig.</li>
<li><b>Importieren:</b> eine Liste einfügen (z. B. aus Moxfield „Export“), eine Datei wählen (.txt, .dck, .dec, .csv, .json) oder einen Link angeben (Archidekt, MTGGoldfish, TappedOut, Deckstats; Moxfield blockiert Links oft, dann hilft es, die Liste zu kopieren). Dateien werden in jeder üblichen Zeichenkodierung erkannt, auch MTGO (.dek) und Cockatrice (.cod). Danach <b>Importieren</b>.</li>
<li>Die Vorschau zeigt, ob der Commander erkannt wurde, welche Karten nicht gefunden oder korrigiert wurden und ob etwas nicht zur Farbidentität passt. Den Commander kannst du dort ändern; Partner mit „ + “ trennen.</li></ul>

<h3 id=h-precons>Precons: fertige Commander-Decks</h3>
<ul><li>Der Bereich „🎁 Precons“ zeigt alle offiziellen Commander-Precons (vorkonstruierte Decks von Wizards of the Coast) mit vollständiger Deckliste, sortiert nach Set und Erscheinungsdatum. Die Listen kommen aus der frei verfügbaren Sammlung github.com/taw/magic-preconstructed-decks-data (auch Grundlage von mtg.wtf und MTGJSON) und werden mit den übrigen Daten automatisch aktualisiert.</li>
<li>Suche nach Deckname, Commander oder Set; die Farbknöpfe zeigen nur Decks, die höchstens diese Farben haben. Je Deck stehen Wert (Summe der Einzelkarten, ohne Standardländer), Bracket-Schätzung und, wenn du eine Sammlung angelegt hast, wie viel davon du schon besitzt.</li>
<li>Ein Deck antippen öffnet die Liste. „✏ Im Deck-Editor öffnen“ lädt es zum Anpassen (Analyse, Testspielfeld, Upgrades); „💾 In Meine Decks speichern“ legt eine eigene Kopie an; „⚔ Als Gegner“ setzt es für Vergleich und Forge-Duelle; „📥 Gekauft: in meine Sammlung“ fügt alle Karten deiner Sammlung hinzu (nach einer Rückfrage).</li>
<li>Sammlerversionen mit identischer Liste erscheinen nur einmal. Karten, die in der Kartendatenbank fehlen (z. B. ganz neue Promokarten), werden beim Deck genannt.</li></ul>
<h3 id=h-brackets>Brackets: die offiziellen Stärkestufen</h3>
<p>Mit den <b>Commander Brackets</b> (von Wizards of the Coast und dem Commander Format Panel, offiziell noch „Beta“) sprecht ihr vor der Partie ab, wie stark eure Decks sind, damit ähnlich starke Decks gegeneinander spielen. Sie helfen bei der Absprache und verbieten keine Karten.</p>
<table class=ftable><tr><th>Bracket</th><th>Was ihr erwarten könnt</th><th>Deckbau-Regeln</th></tr>
<tr><td><b>1 Exhibition</b></td><td>Thema oder Idee vor Stärke, kaum optimiert; Partien dauern mindestens etwa 9 Züge.</td><td>keine Game Changer, keine Massen-Landzerstörung, keine Extra-Züge, keine Zwei-Karten-Combos</td></tr>
<tr><td><b>2 Core</b></td><td>Unoptimiert und geradlinig, Siege kommen nach und nach und lassen sich stören; entspannt und gesellig; mindestens etwa 8 Züge.</td><td>keine Game Changer, keine Massen-Landzerstörung, keine absichtlichen Zwei-Karten-Combos, Extra-Züge nur wenige und nicht hintereinander</td></tr>
<tr><td><b>3 Upgraded</b></td><td>Verstärkt mit guter Synergie und Kartenqualität, kann Gegner stören; der Sieg kann in einem großen Zug kommen; mindestens etwa 6 Züge.</td><td>höchstens 3 Game Changer, keine Massen-Landzerstörung, keine Extra-Zug-Ketten, keine Zwei-Karten-Combos, die vor etwa Zug 6 gewinnen</td></tr>
<tr><td><b>4 Optimized</b></td><td>Tödlich, beständig und schnell, aber nicht auf das Turnier-Metagame ausgerichtet; mindestens etwa 4 Züge.</td><td>nur die Bannliste</td></tr>
<tr><td><b>5 cEDH</b></td><td>Für das kompetitive Metagame gebaut; Partien können in jedem Zug enden.</td><td>nur die Bannliste</td></tr></table>
<ul><li><b>Game Changer:</b> eine offizielle Liste besonders spielstarker Karten (zurzeit 53, Stand 9. Februar 2026, z. B. Rhystic Study, Smothering Tithe, Demonic Tutor). Sie sind nicht verboten, bestimmen aber das Bracket. Die Kennzeichnung kommt mit den Kartendaten von Scryfall und ist nach jeder Aktualisierung aktuell.</li>
<li><b>Massen-Landzerstörung / Mana-Entzug:</b> Karten wie Armageddon oder „Länder enttappen nicht“. In Bracket 1–3 sind sie nicht vorgesehen.</li>
<li><b>Extra-Züge:</b> wenige sind ab Bracket 2 in Ordnung, „Ketten“ (mehrere hintereinander oder in Schleife) erst ab Bracket 4. Das Programm wertet mehr als 3 Extra-Zug-Karten als Kette.</li>
<li><b>Zwei-Karten-Combos:</b> zwei Karten, die zusammen das Spiel entscheiden (z. B. unendlich Schaden). Bracket 3 erlaubt sie nur, wenn sie nicht schon vor etwa Zug 6 zusammenkommen. Die Manaschmiede prüft das automatisch über Commander Spellbook, sobald ein Deck geladen ist (braucht Internet; ohne Verbindung bleibt dieser Punkt offen und lässt sich mit „🔗 Combos erneut prüfen“ nachholen). Der früheste Zug ist eine Schätzung aus vielen gezogenen Probehänden.</li>
<li><b>So stuft die Manaschmiede ein:</b> In der Deckansicht zeigt „🎚 Bracket-Einstufung“ für jede Regel, was gefunden wurde, und daraus das niedrigste mögliche Bracket. Was ein Programm nicht sehen kann, bleibt offen: ob ein Deck ohne eingeschränkte Karten Bracket 1 oder 2 ist (Absicht) und ob ein starkes Deck 4 oder 5 ist (Turnier-Metagame). Deshalb legst du dein <b>Ziel-Bracket</b> selbst fest; es wird mit dem Deck gespeichert, steht als „B3“ in „Meine Decks“, in der Galerie (auch als Filter) und auf der Teilen-Seite. Ohne Angabe steht dort die Schätzung „≈B3“. Enthält das Deck Karten über dem gewählten Ziel, erscheint ⚠ mit den betreffenden Karten.</li>
<li><b>Am Tisch:</b> Sagt euer Bracket an und nennt Besonderheiten (Combos, Extra-Züge, starke Commander). Der offizielle Stand steht bei Wizards: <a href="https://magic.wizards.com/en/news/announcements/introducing-commander-brackets-beta" target=_blank rel=noopener>Einführung</a>, <a href="https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-february-9-2026" target=_blank rel=noopener>letzte Aktualisierung (9.2.2026)</a>.</li></ul>
<h3 id=h-galerie>Deck-Galerie (nur im Server-Betrieb)</h3>
<ul><li><b>Veröffentlichen:</b> unter „📂 Meine Decks“ beim Deck „🌍 Veröffentlichen“ antippen. Das Deck erscheint dann für alle angemeldeten Benutzer dieses Servers in der Galerie; noch einmal antippen zieht es zurück. Änderungen am Deck werden beim Speichern übernommen.</li>
<li><b>Suchen:</b> nach Commander, Deckname, Benutzer, Tags und Notizen; Farbfilter (höchstens/genau/mindestens diese Farben), Höchstpreis, Game Changer; sortiert nach neu, beliebt oder günstig.</li>
<li><b>Deck öffnen:</b> Liste, Notizen und Maybeboard ansehen, „♡“ für gefällt mir, „📥 In meine Decks kopieren“ (das Original bleibt unverändert), „⚔ Als Gegner“ und Kommentare schreiben. Eigene Kommentare und Kommentare am eigenen Deck kannst du löschen.</li>
<li><b>Administrator:</b> kann Decks mit „🚫 Ausblenden“ aus der Galerie nehmen und alle Kommentare löschen.</li></ul>
<h3 id=h-sammlung>Meine Sammlung</h3>
<ul><li><b>Importieren:</b> im Bereich „Meine Sammlung“ eine CSV-Datei aus ManaBox, Moxfield, Deckbox, Archidekt oder Dragon Shield wählen oder eine Liste einfügen. „Hinzufügen“ zählt die Karten zur vorhandenen Sammlung dazu, „Ersetzen“ beginnt neu. Nicht erkannte Namen werden angezeigt.</li>
<li><b>Besitzanteil:</b> bei jedem Deck steht, wie viel Prozent du besitzt und was fehlt (mit Preis). In der Liste markiert ✓ vorhandene Karten, ✗ fehlende und ⚠ Karten, die schon in einem anderen gespeicherten Deck stecken und von denen nicht genug Exemplare frei sind.</li>
<li><b>Deckbau aus der Sammlung:</b> im Assistenten „Sammlung: bevorzugen“ (eigene Karten zuerst) oder „nur eigene Karten“ wählen. Standardländer gelten immer als vorhanden.</li>
<li><b>📷 Karten scannen:</b> im Tab „Sammlung“ (oder in der Deckansicht neben „Hinzufügen“). Drei Wege: <b>Foto aufnehmen</b> (geht überall; am Handy öffnet sich die Kamera), <b>Live-Kamera</b> (im Browser nur über HTTPS bzw. am PC) und in der Android-App <b>„Mit der Handykamera scannen“</b> (Erkennung direkt auf dem Gerät, besonders schnell). Kartensprache einstellen, Karte formatfüllend und gerade aufnehmen. Erkannt wird der Name; bei Unsicherheit werden Alternativen angeboten. <b>Dauerscan:</b> in der Live-Kamera „🔁 Dauerscan starten“ (bzw. in der Android-App „Dauerscan mit der Handykamera“), dann die Karten nacheinander in den Rahmen legen; jede sicher erkannte Karte wird mit Ton automatisch in die Scanliste übernommen. Dieselbe Karte zählt erst wieder, wenn sie kurz aus dem Bild war; für mehrere gleiche Exemplare „+1“ tippen. Beim Einzelscan jede Karte mit „✓ Übernehmen“ in die Scanliste, Mengen mit + / − anpassen, am Ende „Zur Sammlung hinzufügen“ oder „Ins aktuelle Deck“. Beim allerersten Scan wird die Texterkennung einmalig geladen (rund 30 MB, Internet nötig), danach geht es ohne. Für sehr große Sammlungen sind spezialisierte Scanner-Apps (ManaBox, Delver Lens) schneller, und deren CSV lässt sich weiterhin importieren.</li><li><b>🛒 Einkaufsliste:</b> zählt alle Karten, die dir für deine gespeicherten Decks fehlen, mit Preis und Deckzuordnung. „Karten wandern zwischen Decks“ (Standard) rechnet mit der größten Menge in einem Deck, sonst bekommt jedes Deck eigene Exemplare. Die Liste lässt sich kopieren (das Format „1 Kartenname“ je Zeile versteht auch die Wunschliste auf Cardmarket) oder komplett auf die eigene Wunschliste setzen.</li>
<li><b>⭐ Wunschliste und Preisalarm:</b> Karten mit Anzahl und optionalem Zielpreis. Liegt der aktuelle Preis darunter, steht die Karte grün markiert in der Liste und als „🔔 Preisalarm“ auf der Startseite. Dort erscheinen auch Karten deiner Sammlung, deren Preis sich in etwa sieben Tagen um mindestens 20 % und 1 € verändert hat. Neue Preise kommen mit jeder Kartenaktualisierung.</li>
<li><b>📁 Ordner:</b> Teile der Sammlung ordnen (z. B. Tauschordner, Binder). Ein Ordner enthält nur Karten, die du besitzt, und höchstens so viele, wie du hast; die Karten bleiben dabei Teil der Sammlung.</li>
<li><b>🛒 Händler-Links:</b> Bei jeder Karte führen kleine Links direkt zum Händler: <b>CM</b> Cardmarket (günstigste Druckversion) und <b>TO</b> Trader-online (Suche nach der Karte). Bei Precons kommt <b>CC</b> cardcosmos dazu, das nur versiegelte Ware führt. „🛒 Bei Cardmarket kaufen“ in Einkaufs- und Wunschliste kopiert die ganze Liste und öffnet die Wants-Seite von Cardmarket: neue Liste anlegen, „Decklist hinzufügen“, einfügen. Der Shopping Wizard sucht dann die günstigste Händlerkombination. Anmeldung und Kauf laufen immer direkt beim Händler; die Manaschmiede überträgt keine Daten. Unter der Einkaufsliste lässt sich jeder Händler abschalten.</li>
<li><b>📚 Bestand nach Druck:</b> jede Zeile ist ein Druck deiner Karte mit Set, Sammlernummer, Foil (normal, Foil, Etched), Zustand (Cardmarket-Stufen MT, NM, EX, GD, LP, PL, PO), Sprache und Anzahl. Alles lässt sich direkt in der Tabelle ändern; ✎ öffnet die Liste aller Drucke der Karte mit Bild und Preis (normal und Foil). Einträge mit gleichen Angaben werden zusammengelegt, Anzahl 0 entfernt den Eintrag. Oben über der Tabelle: „Druck wählen …“ fügt eine Karte in einem bestimmten Druck hinzu. Beim <b>Import</b> werden Set, Nummer, Foil, Zustand und Sprache aus ManaBox, Moxfield, Deckbox, Archidekt und Dragon Shield übernommen, aus Textlisten „2 Counterspell (MH2) 267 *F*“. Die Druckdaten (Set-Name, Bild, Cardmarket-Nummer) holt das Programm von Scryfall; ist Scryfall gerade nicht erreichbar, bleiben die Angaben erhalten und lassen sich später mit „Druckdaten nachladen“ ergänzen. <b>Wert:</b> der Cardmarket-Preis genau dieses Drucks (Foil mit Foil-Preis), sonst der Scryfall-Preis des Drucks; ohne bekannten Druck gilt der günstigste Druck der Karte. Zustand und Sprache ändern den Wert nicht, weil die Cardmarket-Preisliste sie nicht unterscheidet. Für Deckbau, Besitzanteil, Einkaufsliste und Ordner zählt die Summe je Karte. Der Export „Als CSV herunterladen“ enthält alle Druckangaben und lässt sich wieder einlesen (auch von Moxfield, ManaBox, Archidekt).</li>
<li><b>🧭 Kaufassistent:</b> plant den Kauf fehlender Karten für ein Deck, alle Decks oder die Wunschliste. Mit Budget werden Karten, die in mehreren Decks stecken, zuerst eingeplant, danach die günstigsten; was nicht hineinpasst, ist markiert. Je Karte wählst du Druck und Foil, den Händler (Cardmarket oder Trader-online) oder „nicht kaufen“. Für Cardmarket kopiert der Assistent die Karten mit beliebigem Druck für die Wants-Liste; festgelegte Drucke und Foils legst du über die Produktlinks in den Warenkorb. Der Precon-Check zeigt Precons, die mehrere der fehlenden Karten enthalten. Gekaufte Karten ankreuzen und „als gekauft in die Sammlung“ übernehmen; die Wunschliste wird dabei gekürzt.</li>
<li><b>🖨 Proxy-Druck:</b> druckt Kopien beliebiger Kartenlisten zum privaten Testen, siehe „Proxys drucken“ unter „Deck ansehen und anpassen“.</li>
<li><b>📈 Wertverlauf:</b> der Wert der Sammlung je Stichtag (bei jeder Kartenaktualisierung) und zum Vergleich in Dollar.</li>
<li><b>Preisquellen und Budget-Tausch:</b> Euro-Preise kommen direkt aus der öffentlichen <b>Cardmarket-Preisliste</b>, die jeden Tag neu geladen wird. Als Preis einer Karte gilt der Trendpreis ihrer <b>günstigsten Druckversion</b>, also etwa der Betrag, den du für eine spielbare Kopie bezahlst. Ein Klick auf den Preis in der Kartensuche zeigt dazu Tiefstpreis, Durchschnitt über 1, 7 und 30 Tage, Foil-Preis und Zahl der Drucke; 🛒 öffnet die günstigste Druckversion auf Cardmarket. Ist die Preisliste einmal nicht erreichbar, gelten die zuletzt geladenen Cardmarket-Preise, ganz ohne Preisliste die Euro-Preise von Scryfall. Dollar-Preise (TCGplayer) liefert Scryfall. In der Deckansicht sucht „💸 Budget-Tausch“ für teure Karten (ab einstellbarem Preis, ohne eigene Karten) Ersatz mit gleicher Aufgabe für höchstens 30 % des Preises; ein Klick tauscht die Karte.</li></ul>

<h3 id=h-spieltisch>Spieltisch: Lebenszähler und Spielprotokoll</h3>
<ul><li><b>Partie starten:</b> Spielerzahl (2–6) und Startleben wählen, Namen eintragen und je Spieler ein gespeichertes Deck auswählen oder frei eintippen.</li>
<li><b>Tischansicht (Standard):</b> ein großes Feld je Spieler, die obere Reihe steht auf dem Kopf für die gegenüber Sitzenden (🔄 schaltet das ab). <b>Links tippen = −1, rechts tippen = +1, gedrückt halten = ±10</b> (wiederholt, solange der Finger liegt); die Änderung wird kurz angezeigt. Ist zum Spieler ein Deck mit Commander gespeichert oder ein Commander-Name eingetragen, erscheint dessen Kartenbild als Hintergrund. ☠/⚔ öffnet Gift, Commander-Schaden je Gegner, Monarch, „am Zug“ und Aufgeben. In der Mitte: 🎲 Startspieler auslosen, Zugzähler, ⏭ nächster Spieler, ⛶ Vollbild, 📋 Tabellenansicht.</li>
<li><b>📡 Gemeinsamer Tisch (mehrere Handys):</b> Alle Geräte müssen dieselbe Manaschmiede nutzen (Server oder PC im Heimnetz mit „im Netzwerk starten“). Eine Person startet die Partie, wählt unten „Dein Platz“ und tippt „📡 Tisch teilen“. Daraufhin erscheinen ein vierstelliger Code, ein QR-Code und ein Link. Die anderen geben im Spieltisch bei „📡 Einem Tisch beitreten“ den Code ein (oder scannen den QR-Code) und wählen ihren Platz. Jedes Handy zeigt dann das eigene Feld groß und die Mitspieler klein darüber; Leben, Gift, Commander-Schaden (trägt der Getroffene ein), Zug und Monarch werden innerhalb etwa einer Sekunde abgeglichen. Jeder kann nur sein eigenes Feld ändern. Fällt ein Handy aus, hakt der Gastgeber „alle Felder anzeigen und steuern“ an. Speichern oder Abbrechen beim Gastgeber beendet den Tisch für alle. Nach dem Neuladen verbindet sich ein Handy von selbst wieder; offene Tische verfallen nach 12 Stunden ohne Änderung.</li>
<li><b>Tabellenansicht:</b> mit 📋 umschaltbar (🃏 wieder zurück, die Wahl wird gemerkt): Gift (ab 10 verloren) und Commander-Schaden je Gegner (ab 21 verloren). Wer verloren hat, wird ausgegraut. „Nächster Zug“ zählt die Runden. Der Stand bleibt beim Neuladen erhalten; am Handy bleibt der Bildschirm an.</li>
<li><b>Partie beenden:</b> Sieger wählen (bleibt nur einer übrig, ist er vorausgewählt) und speichern. Die Statistik zeigt Partien, Siege und Siegquote je Deck und je Spieler sowie die letzten Partien.</li>
<li><b>Forge-Ergebnisse:</b> nach einem Duell mit „Ins Spielprotokoll übernehmen“ zählen die KI-Partien mit (als „Forge“ gekennzeichnet).</li>
<li><b>🏆 Spielabend:</b> Mitspieler eintragen und Tische auslosen. Die Manaschmiede bildet möglichst Vierertische, sonst Dreiertische, und vermeidet Paarungen, die es an diesem Abend schon gab. Den Sieger tippst du an, die Rangliste zählt nur Siege. Eine Saison ist optional und wertet mehrere Abende zusammen. Mitspieler öffnen den Link oder QR-Code am Handy und tragen Sieger ohne eigenes Konto ein. „Am Handy-Tisch spielen“ startet den Lebenszähler mit den Spielern des Tisches und meldet den Sieger beim Speichern zurück.</li></ul>

<h3 id=h-export>Exportieren und übertragen</h3>
<ul><li><b>→ Moxfield / → Archidekt:</b> die Liste wird in die Zwischenablage kopiert und die Seite geöffnet. Dort ein neues Deck anlegen, den Import öffnen und mit <b>Strg+V</b> einfügen. (Beide Seiten erlauben keinen direkten Upload durch andere Programme.)</li>
<li><b>Text kopieren:</b> passt für fast alle anderen Seiten und Apps.</li>
<li><b>Herunterladen:</b> als Textdatei, Forge-Deck (.dck) oder Tabelle (CSV).</li>
<li><b>In Forge-Deckordner speichern:</b> das Deck erscheint danach in Forge unter den Commander-Decks.</li></ul>

<h3 id=h-gegner>Gegner wählen und vergleichen</h3>
<ul><li>Gegner kann ein offizielles <b>Precon</b> sein (Suchfeld oder passende Vorschläge) oder ein <b>eigenes Deck</b> (Knöpfe „Eigene Decks als Gegner“ oder „Als Gegner verwenden“ beim Import).</li>
<li>Der <b>Vergleich</b> stellt Kennzahlen gegenüber: Ramp (Mana-Beschleunigung), Kartenvorteil, Entfernung, Massenentfernung, Länderzahl, Manawert, Game Changer, Tutoren, Kartenqualität. Grün markiert, wer vorne liegt. Der Vergleich rechnet nur mit den Decklisten; gespielt wird erst im Forge-Duell.</li>
<li><b>Ideen aus dem Gegnerdeck:</b> beliebte Karten, die dein Deck nicht hat und die zu deinen Farben passen.</li></ul>

<h3 id=h-combos>Combos</h3>
<p>Combos sind Kartenkombinationen, die zusammen etwas Außergewöhnliches bewirken, oft den sofortigen Sieg. Die Daten kommen von Commander Spellbook. Für jede Combo siehst du, wie wahrscheinlich du alle Teile bis Zug 6, 8 oder 10 zusammen hast (berechnet aus 1.500 simulierten Starthänden, ohne Störung durch Gegner). Früh mögliche Siegcombos heben die Bracket-Einstufung an.</p>
<p>Zusätzlich zeigt die Analyse die <b>Einstufung von Commander Spellbook</b> (Ruthless, Spicy, Powerful, Oddball, Core, Exhibition) mit Begründung, z. B. Anzahl der Game Changer und Zwei-Karten-Combos. Unter <b>„Fast vollständig“</b> stehen Combos, denen genau eine Karte fehlt. Mit dem Knopf „➕ … ins Deck“ fügst du sie direkt hinzu. Die fehlende Karte ist gestrichelt rot umrandet.</p>

<h3 id=h-duell>Direktes Duell mit Forge</h3>
<p>Forge ist ein kostenloses Programm, das Magic mit allen Regeln spielt. Hier spielen zwei Computer-Gegner deine beiden Decks komplett gegeneinander, Combos eingeschlossen.</p>
<ol><li><b>Einmalig einrichten:</b> Java 17 oder neuer installieren (z. B. von adoptium.net) und Forge von github.com/Card-Forge/forge/releases installieren.</li>
<li>Im Duell-Bereich den <b>Forge-Ordner</b> eintragen (den Ordner, in dem die Datei <code>forge-gui-desktop-…-jar-with-dependencies.jar</code> liegt) und <b>Speichern</b> drücken. Es sollte „Forge ist bereit.“ erscheinen.</li>
<li><b>Spielform:</b> „1 gegen 1“, „Commander-Runde zu dritt“ (ein weiterer Gegner) oder „Commander-Runde zu viert“ (zwei weitere Gegner), dazu jeweils passende Precons oder eigene Decks wählen. Mehrspieler-Partien dauern deutlich länger (1–10 Minuten je Partie); bei gleich starken Decks gewinnt jedes zu dritt etwa 33 %, zu viert etwa 25 %.</li>
<li><b>Precon wählen:</b> In der Liste „Precon auswählen“ stehen alle offiziellen Precons mit Namen, Commander und Farben, nach Set und Jahr geordnet; ganz oben die zu deinen Farben passenden. Wer den Namen kennt, kann auch im Suchfeld nach Precon, Commander oder Set suchen.</li>
<li>Anzahl Partien wählen (10 ist ein guter Anfang) und <b>Duell starten</b>. Die erste Partie dauert etwas länger, weil Forge startet. Danach dauert eine Partie 1 gegen 1 je nach Decks etwa 15 Sekunden bis 3 Minuten.</li></ol>
<p><b>⚙ KI-Einstellungen:</b> das KI-Profil deines Decks (die Gegner spielen mit „Default“) und die Vorausschau. Mit Vorausschau prüft die KI Züge vorher durch und spielt stärker, braucht aber länger: etwa 15 s je Partie ohne, 30 s mit und 50 s mit maximaler Vorausschau (1 gegen 1).</p>
<p><b>🔬 Messlabor:</b> misst, ob ein Kartentausch hilft oder mit welchem KI-Profil Forge dein Deck am besten spielt. Alle Varianten spielen gleich oft gegen dieselben Gegner (bis zu vier), mit gleichem Zufallsstart. Die Stufen Schnell, Standard, Gründlich und Sehr gründlich zeigen vorab die ungefähre Dauer; während der Messung siehst du die Restzeit. Das Ergebnis nennt die Siegquote mit 90-%-Bereich und ein Urteil („deutlich besser“, „eher schlechter“ usw., erst ab 8 Partien je Variante). Eine bessere Variante übernimmst du mit einem Klick ins Deck, ein besseres Profil als KI-Pilot für dieses Deck. Frühere Messungen bleiben gespeichert.</p>
<p><b>📊 Genaue Statistik:</b> unter dem Ergebnis eingeklappt. Je Deck: wie oft es begonnen (und dann gewonnen) hat, Ø Mulligans, in welcher Runde der Commander zuerst kam und wie oft er gewirkt wurde, Ø Länder und Zauber, Ø Schaden an Gegnern (davon im Kampf), die am häufigsten gewirkten Karten, die Karten mit dem meisten Schaden und „Schlüsselkarten“, mit denen das Deck deutlich öfter gewinnt als im Schnitt. Bei „Einzelne Partien“ zeigt <b>🔎 Verlauf</b> eine Partie Zug für Zug: Länder, Zauber, Commander, Angriffe, Schaden und Lebenspunkte, dazu ein Diagramm der Lebenspunkte. „Runde“ zählt die eigenen Züge eines Spielers.</p>
<p><b>🃏 Selbst spielen:</b> „Im Browser“ öffnet denselben Spieltisch mit deinem Deck und dem Gegner; du spielst beide Seiten. Nach „Zug beenden“ kommt der andere Spieler nach unten, ⇅ wechselt die Seite jederzeit. „Partie beenden“ (⚙) trägt das Ergebnis ins Spielprotokoll ein. Im lokalen Betrieb legt „🖥 In Forge selbst spielen“ beide Decks in Forge ab und öffnet Forge: dort links „Commander“ wählen, Spieler 1 ist dein Deck, Spieler 2 die KI mit dem Gegnerdeck. Forge prüft dabei alle Regeln.</p>
<p><b>📱 Am Handy:</b> quer gehalten ist der Tisch am besten lesbar; im Hochformat holt 📱 oben Vollbild und Querformat (Android/Chrome; auf dem iPhone das Handy drehen). Die Hand ragt nur halb ins Bild und hebt sich beim Antippen. Für kleine Bildschirme helfen „Aa“ (Textkacheln mit Regeltext und Stärke/Widerstand) und die Kartengröße im ⚙-Menü.</p>
<p><b>Ergebnis lesen:</b> Siege in Prozent, durchschnittlicher Siegzug, Siegart (z. B. Commander-Schaden, Combo) und welche Karte gewonnen hat. Die KI spielt solide, macht aber Fehler. Aussagekräftig sind deshalb erst Tendenzen über viele Partien. Wie die KI dein Deck am besten spielt und ob ein Kartentausch hilft, misst das 🔬 Messlabor unter dem Duell. Läuft eine Partie zu lange, wird sie als Unentschieden gewertet.</p>

<h3 id=h-regeln>Offizielle Regeln</h3>
<p>Die vollständigen <b>Comprehensive Rules</b> von Wizards of the Coast (englisch), automatisch in der neuesten Fassung. Suche nach</p>
<ul><li>einer <b>Regelnummer</b>: <code>903</code> (alle Commander-Regeln), <code>903.4</code> (eine Regel mit Unterregeln), <code>5</code> (ein ganzes Kapitel),</li>
<li>oder <b>Wörtern</b> (englisch): z. B. <code>color identity</code>, <code>commander tax</code>, <code>trample</code>. Treffer im Glossar stehen oben.</li></ul>
<p>Verweise wie „rule 702.19“ im Text sind anklickbar. Die Schnellknöpfe springen zu häufig gebrauchten Abschnitten. Für Bannliste und Brackets gibt es Links zu den offiziellen Seiten.</p>

<h3 id=h-suche>Kartensuche</h3>
<p>Suche nach Name oder Regeltext, Kartentyp, Stichwort (z. B. Flying), Farbidentität und Manawert. „Als Commander nutzbar“ zeigt nur mögliche Commander. Ergebnisse sind nach Beliebtheit sortiert, mit Preisen und einem Link zu Scryfall.</p>

<h3 id=h-update>Automatische Aktualisierung</h3>
<ul><li>Bei jedem Start wird geprüft: <b>Regeln</b> (neue Fassung bei Wizards?), <b>Precons</b> (neue Decklisten?) und <b>Kartendaten</b> (werden neu geladen, wenn sie älter als 7 Tage sind und Scryfall neuere hat).</li>
<li>Heruntergeladen wird nur, was sich geändert hat. Ohne Internet läuft alles mit den vorhandenen Daten weiter.</li>
<li>Mit <b>Jetzt aktualisieren</b> im Balken oben prüfst du sofort; <b>Alles neu laden</b> erzwingt einen frischen Download.</li>
<li>Gespeicherte Decks, Einstellungen und Forge-Ordner bleiben bei Aktualisierungen erhalten.</li></ul>

<h3 id=h-geraete>Handy, Tablet und andere Geräte</h3>
<ul><li><b>Im Heimnetz:</b> auf dem PC mit <code>Commander-DB im Netzwerk starten.bat</code> (oder <code>python commander_db_vNN.py serve --lan</code>) starten. Im schwarzen Fenster erscheint eine Adresse wie <code>http://192.168.178.23:8000/?key=…</code>. Diese Adresse im Browser von Handy oder Tablet öffnen (gleiches WLAN). Der Code im Link schützt vor fremdem Zugriff; danach merkt sich der Browser die Freigabe.</li>
<li>Windows fragt beim ersten Mal, ob Python im Netzwerk kommunizieren darf. Für <b>private Netzwerke</b> erlauben.</li>
<li>Duelle laufen dabei auf dem PC; das Handy zeigt nur die Ergebnisse.</li>
<li><b>Mac und Linux:</b> das Skript läuft dort genauso (Python 3 installieren, dann <code>python3 commander_db_vNN.py serve</code>).</li>
<li><b>Im Internet (Server):</b> läuft die Datenbank auf einem Server, öffnest du dessen Adresse (z. B. <code>https://commander.deine-domain.de</code>) und meldest dich mit Benutzername und Passwort an. Jeder Benutzer hat eigene gespeicherte Decks. Neue Benutzer legt der Administrator über „Benutzer verwalten“ an.</li>
<li><b>Als App installieren:</b> auf Android in Chrome die Serveradresse öffnen, dann „📲 Als App installieren“ (oder Menü ⋮ → „App installieren“). Unter Windows in Edge oder Chrome genauso über das Installieren-Symbol in der Adressleiste. Die App erscheint dann im App-Menü bzw. Startmenü und öffnet sich im eigenen Fenster.</li>
<li><b>Android-App (APK):</b> fragt beim ersten Start nach der Serveradresse und zeigt danach dieselben Inhalte; Dateien werden im Download-Ordner gespeichert.</li>
<li><b>Impressum und Datenschutz:</b> Ist der Server aus dem Internet erreichbar, trägt der Administrator unter „Impressum &amp; Datenschutz“ in der oberen Leiste Name, Anschrift und E-Mail ein. Die Seiten <code>/impressum</code> und <code>/datenschutz</code> sind in der Fußzeile verlinkt.</li></ul>

<h3 id=h-begriffe>Begriffe</h3>
<dl><dt>Ramp</dt><dd>Karten, die zusätzliches Mana bringen (z. B. Sol Ring, Länder suchen).</dd>
<dt>Kartenvorteil (Draw)</dt><dd>Karten, mit denen du zusätzliche Karten ziehst.</dd>
<dt>Entfernung (Removal)</dt><dd>Karten, die eine gegnerische Karte zerstören oder verbannen.</dd>
<dt>Massenentfernung (Wipe)</dt><dd>Entfernt viele oder alle Kreaturen/bleibenden Karten auf einmal.</dd>
<dt>Tutor</dt><dd>Durchsucht die Bibliothek nach einer bestimmten Karte.</dd>
<dt>Game Changer</dt><dd>Offizielle Liste besonders spielstarker Karten; sie bestimmen mit, in welches Bracket ein Deck gehört.</dd>
<dt>Bracket</dt><dd>Offizielle Stärkestufe 1 (sehr locker) bis 5 (Turnierniveau, cEDH).</dd>
<dt>Precon</dt><dd>Fertig gekauftes, offizielles Commander-Deck.</dd>
<dt>Farbidentität</dt><dd>Alle Farbsymbole auf der Karte, auch im Regeltext. Sie bestimmt die erlaubten Farben im Deck.</dd>
<dt>EDHREC-Rang</dt><dd>Wie oft eine Karte in Commander-Decks gespielt wird (kleiner = beliebter).</dd>
<dt>Mulligan</dt><dd>Neue Starthand ziehen, wenn die erste schlecht ist.</dd>
<dt>Combo</dt><dd>Karten, die zusammen eine besonders starke oder spielentscheidende Wirkung haben.</dd></dl>

<h3 id=h-probleme>Probleme lösen</h3>
<dl><dt>Die Seite lädt nicht / „Keine Verbindung zum Skript“</dt><dd>Das schwarze Fenster wurde geschlossen. Neu starten und die Seite neu laden (F5).</dd>
<dt>Eine Karte wird nicht gefunden</dt><dd>Englischen Kartennamen verwenden. Ganz neue Karten kommen mit der nächsten Kartendaten-Aktualisierung.</dd>
<dt>„Java ist zu alt“ / „Java nicht gefunden“</dt><dd>Java 17 oder neuer installieren und das Programm neu starten.</dd>
<dt>„Keine Datei forge-gui-desktop… gefunden“</dt><dd>Falscher Forge-Ordner. Im Explorer nach „forge-gui-desktop“ suchen und den Ordner der Datei eintragen.</dd>
<dt>Moxfield-Link funktioniert nicht</dt><dd>In Moxfield „Export“ → Liste kopieren und einfügen.</dd>
<dt>Combos „nicht erreichbar“</dt><dd>Keine Internetverbindung oder Commander Spellbook gerade nicht erreichbar. Später erneut versuchen.</dd>
<dt>Aktualisierung „fehlgeschlagen“</dt><dd>Meist fehlt kurz das Internet. Die alten Daten bleiben nutzbar; später „Jetzt aktualisieren“ klicken.</dd></dl>
<p class=hint>Kartendaten: Scryfall · Precons: mtg.wtf/MTGJSON · Combos: Commander Spellbook · Regeln: Wizards of the Coast · Regel-Engine: Forge. Magic: The Gathering ist eine Marke von Wizards of the Coast; dieses Programm ist ein privates Fan-Werkzeug ohne Verbindung zu Wizards.</p>
</div></div>
<header id=top><h2>Manaschmiede</h2>
<p class=wotc>Fan-Werkzeug für das Commander-Format von <b>Magic: The Gathering®</b> · Magic: The Gathering stammt von
<a href="https://magic.wizards.com/de" target=_blank rel=noopener>Wizards of the Coast</a></p>
<nav id=mainnav role=tablist><a href="#willkommen" data-v=willkommen>🏠 Willkommen</a><a href="#neu" data-v=neu class=navneu>🌱 Neu hier?</a><a href="#deck" data-v=deck>🛠 Deck bauen</a><a href="#gegner" data-v=gegner>⚔ Gegner &amp; Duell</a><a href="#decks" data-v=decks>📂 Meine Decks</a><a href="#galerie" data-v=galerie class=srvonly hidden>🌍 Galerie</a><a href="#precons" data-v=precons>🎁 Precons</a><a href="#sammlung" data-v=sammlung>📦 Sammlung</a><a href="#spieltisch" data-v=spieltisch>🎲 Spieltisch</a><a href="#suche" data-v=suche>🔎 Kartensuche</a><a href="#regeln" data-v=regeln>📖 Regeln</a></nav></header>
<p class=info id=info></p>
<div id=userbar class=hint></div>
<div id=upd class=updbar>Prüfe auf Aktualisierungen ...</div>
<section id=v-willkommen class=page>
<div class=hero>
<div class=orbs aria-hidden=true><span class="orb w"></span><span class="orb u"></span><span class="orb b"></span><span class="orb r"></span><span class="orb g"></span></div>
<h1 class=herot>Willkommen in der Manaschmiede!</h1>
<p class=herosub>Baue, teste und vergleiche deine Decks für das Commander-Format von <b>Magic: The Gathering</b>: 100 Karten, ein Commander und bis zu drei Gegner am Tisch.</p>
<form id=wquick autocomplete=off><span class=ac><input id=wcmd placeholder="Mit welchem Commander möchtest du spielen?" size=40></span>
<button class=primary>Deck bauen ✦</button></form>
<div id=palert class=palert hidden></div>
<p class=hint>Noch keine Idee? „Atraxa“, „Krenko“ oder „Edgar Markov“ eintippen oder <a href="#deck" id=wsug>💡 Commander nach Farbe und Thema vorschlagen lassen</a>.</p>
<a href="#neu" class=newbtn>🌱 <b>Neu bei Magic oder Commander?</b> Hier in Ruhe starten: Grundlagen, erstes Deck, erste Partie</a>
</div>
<div id=recent></div>
<div class=tiles>
<a class="tile w" href="#neu"><span class=tt>Neu hier?</span><span class=ta>🌱</span><span class=tx>Magic und Commander von Grund auf: Karten, Zugablauf, Commander-Regeln, erstes Deck und erste Partie.</span></a>
<a class="tile w" href="#deck"><span class=tt>Deck bauen</span><span class=ta>🛠</span><span class=tx>Der Assistent stellt ein vollständiges Deck zusammen, passend zu Commander, Budget und Sammlung. Danach frei anpassen.</span></a>
<a class="tile r" href="#gegner"><span class=tt>Gegner &amp; Duell</span><span class=ta>⚔</span><span class=tx>Mit offiziellen Precons oder eigenen Decks vergleichen, Combos finden und KI-Partien mit Forge spielen lassen.</span></a>
<a class="tile u" href="#decks"><span class=tt>Meine Decks</span><span class=ta>📂</span><span class=tx>Decks importieren (Moxfield, Archidekt, Dateien), speichern, Versionen vergleichen und teilen.</span></a>
<a class="tile g" href="#sammlung"><span class=tt>Sammlung</span><span class=ta>📦</span><span class=tx>Karten mit der Handykamera scannen oder aus ManaBox &amp; Co. übernehmen. Der Kaufassistent plant, was für ein Deck noch fehlt.</span></a>
<a class="tile b" href="#spieltisch"><span class=tt>Spieltisch</span><span class=ta>🎲</span><span class=tx>Lebenszähler mit Commander-Schaden und Gift, Spielprotokoll, Siegquoten je Deck und Spielabende mit Rangliste.</span></a>
<a class="tile c" href="#suche"><span class=tt>Kartensuche</span><span class=ta>🔎</span><span class=tx>Alle Commander-Karten nach Name, Text, Typ, Farbe und Manawert durchsuchen.</span></a>
<a class="tile c" href="#regeln"><span class=tt>Regeln</span><span class=ta>📖</span><span class=tx>Die offiziellen Comprehensive Rules von Wizards of the Coast mit Suche und Glossar.</span></a>
<a class="tile c" href="#" data-h=start><span class=tt>Hilfe</span><span class=ta>❓</span><span class=tx>Schritt für Schritt erklärt, auch für alle, die Commander noch nicht kennen.</span></a>
</div>
</section>
<section id=v-neu class=page hidden>
<div class=guide>
<h2>🌱 Neu hier? So kommst du ins Spiel</h2>
<p class=herosub style="margin-left:0">Du hast noch nie Magic gespielt oder kennst Magic, aber nicht Commander? Hier steht alles, was du für die erste Partie brauchst, in Ruhe zum Durchlesen und ohne Fachchinesisch.</p>
<div class=gpick>
<a href="#g-magic" class="gbtn w">✨ <b>Komplett neu bei Magic</b><span>Grundlagen: Karten, Mana, Zugablauf, Kampf</span></a>
<a href="#g-commander" class="gbtn u">👑 <b>Neu bei Commander</b><span>Ich kenne Magic. Was ist bei Commander anders?</span></a>
<a href="#g-deck" class="gbtn g">🛠 <b>Mein erstes Deck</b><span>Fertiges Deck oder selbst bauen</span></a>
<a href="#g-partie" class="gbtn r">🎲 <b>Die erste Partie</b><span>Schritt für Schritt vom Mischen bis zum Sieg</span></a>
</div>

<h3 id=g-magic>✨ Teil 1: Magic in zehn Minuten</h3>
<div class=gcard><h4>Worum geht es?</h4>
<p>Jede Person spielt mit einem eigenen Kartenstapel, dem <b>Deck</b>. Du spielst Länder, die dir <b>Mana</b> (die Energie für Zaubersprüche) geben, und mit diesem Mana wirkst du Kreaturen und Zauber. Ziel ist, dass die Gegner verlieren. Das passiert, wenn</p>
<ul><li>ihre <b>Lebenspunkte auf 0</b> fallen (im Commander-Format startet jede Person mit 40),</li>
<li>sie <b>10 Giftmarken</b> haben,</li>
<li>sie eine Karte ziehen müssen, aber ihre <b>Bibliothek</b> (der Nachziehstapel) leer ist,</li>
<li>oder eine Karte ausdrücklich sagt, dass jemand gewinnt oder verliert.</li></ul></div>

<div class=gcard><h4>Die fünf Farben</h4>
<p>Fast jede Karte gehört zu einer oder mehreren Farben. Jede Farbe hat ihren eigenen Stil:</p>
<ul class=gcol>
<li><span class="pip pW">W</span> <b>Weiß:</b> Ordnung und Gemeinschaft: viele kleine Kreaturen, Schutz, Lebenspunkte gewinnen, alles auf einmal zerstören.</li>
<li><span class="pip pU">U</span> <b>Blau:</b> Wissen und Kontrolle: Karten ziehen, gegnerische Zauber verhindern, Dinge zurück auf die Hand schicken.</li>
<li><span class="pip pB">B</span> <b>Schwarz:</b> Macht um jeden Preis: Kreaturen vernichten, Tote aus dem Friedhof zurückholen, Leben für Vorteile bezahlen.</li>
<li><span class="pip pR">R</span> <b>Rot:</b> Feuer und Tempo: direkter Schaden, schnelle Angriffe, Chaos.</li>
<li><span class="pip pG">G</span> <b>Grün:</b> Natur und Wachstum: große Kreaturen, zusätzliche Länder und viel Mana.</li>
<li><span class="pip pC">◇</span> <b>Farblos:</b> Artefakte und manche Kreaturen passen in jedes Deck.</li></ul>
<p>Das passende Land zu jeder Farbe: Ebene (Weiß), Insel (Blau), Sumpf (Schwarz), Gebirge (Rot), Wald (Grün).</p></div>

<div class=gcard><h4>Kartenarten</h4>
<table class=gtab>
<tr><th>Art</th><th>Was sie tut</th></tr>
<tr><td><b>Land</b></td><td>Gibt Mana. Du darfst <b>ein Land pro Zug</b> spielen, kostet nichts.</td></tr>
<tr><td><b>Kreatur</b></td><td>Bleibt liegen und kann angreifen und blocken. Unten rechts stehen <b>Stärke/Widerstandskraft</b>, z. B. 3/2: macht 3 Schaden, stirbt bei 2 Schaden.</td></tr>
<tr><td><b>Hexerei</b> (Sorcery)</td><td>Einmaliger Effekt, nur in deinem eigenen Zug, wenn sonst nichts passiert.</td></tr>
<tr><td><b>Spontanzauber</b> (Instant)</td><td>Einmaliger Effekt, <b>jederzeit</b>, auch im Zug der anderen als Reaktion.</td></tr>
<tr><td><b>Artefakt</b> und <b>Verzauberung</b></td><td>Bleiben liegen und wirken dauerhaft, z. B. zusätzliches Mana oder ein laufender Vorteil.</td></tr>
<tr><td><b>Planeswalker</b></td><td>Mächtige Verbündete mit Loyalität; einmal pro Zug eine ihrer Fähigkeiten nutzen. Können angegriffen werden.</td></tr>
</table></div>

<div class=gcard><h4>Mana und Kosten lesen</h4>
<p>Oben rechts auf der Karte stehen die <b>Manakosten</b>. Beispiel: <span class=mana><span class="pip pC">2</span><span class="pip pG">G</span></span> heißt: ein grünes Mana und zwei beliebige weitere. Um ein Land zu nutzen, <b>tappst</b> du es (drehst es quer). Getappte Karten sind für diese Runde verbraucht und werden zu Beginn deines nächsten Zuges wieder gerade gedreht („enttappt“).</p></div>

<div class=gcard><h4>Ein Zug läuft so ab</h4>
<ol class=gsteps>
<li><b>Enttappen:</b> alle deine Karten wieder gerade drehen.</li>
<li><b>Versorgung:</b> Effekte „zu Beginn deines Zuges“ passieren jetzt.</li>
<li><b>Ziehen:</b> eine Karte vom Deck nehmen.</li>
<li><b>Erste Hauptphase:</b> Land spielen, Kreaturen und andere Karten wirken.</li>
<li><b>Kampf:</b> Du wählst angreifende Kreaturen (sie werden getappt) und wen sie angreifen. Jeder Angegriffene darf mit ungetappten Kreaturen blocken. Ungeblockter Schaden geht auf die Lebenspunkte, geblockte Kreaturen kämpfen gegeneinander.</li>
<li><b>Zweite Hauptphase:</b> noch einmal Karten spielen (z. B. was du vor dem Angriff nicht zeigen wolltest).</li>
<li><b>Ende:</b> mehr als sieben Handkarten? Überzählige abwerfen. Schaden an Kreaturen verschwindet.</li></ol>
<p>Dann ist die nächste Person im Uhrzeigersinn dran.</p></div>

<div class=gcard><h4>Reagieren: der Stapel</h4>
<p>Wird etwas gewirkt, dürfen alle darauf antworten, etwa mit einem Spontanzauber. Antworten kommen „oben drauf“ und werden <b>zuerst</b> abgehandelt. Der zuletzt gewirkte Zauber wirkt also zuerst. Für den Anfang reicht: Bevor ein Zauber wirkt, kurz fragen, ob jemand reagieren möchte.</p></div>

<div class=gcard><h4>Häufige Fähigkeiten</h4>
<table class=gtab>
<tr><td><b>Flugfähigkeit</b></td><td>kann nur von Kreaturen mit Flugfähigkeit oder Reichweite geblockt werden</td></tr>
<tr><td><b>Eile</b></td><td>darf schon in dem Zug angreifen, in dem sie ins Spiel kommt</td></tr>
<tr><td><b>Wachsamkeit</b></td><td>wird beim Angreifen nicht getappt, kann also danach noch blocken</td></tr>
<tr><td><b>Trampelschaden</b></td><td>überzähliger Schaden geht trotz Blocker auf den Spieler</td></tr>
<tr><td><b>Todesberührung</b></td><td>schon 1 Schaden zerstört die getroffene Kreatur</td></tr>
<tr><td><b>Lebensverknüpfung</b></td><td>du gewinnst so viele Lebenspunkte, wie die Kreatur Schaden macht</td></tr>
<tr><td><b>Erstschlag</b></td><td>macht im Kampf zuerst Schaden</td></tr>
<tr><td><b>Fluchsicherheit</b></td><td>kann nicht zum Ziel gegnerischer Zauber werden</td></tr>
<tr><td><b>Unzerstörbar</b></td><td>wird durch Schaden und „zerstöre“-Effekte nicht vernichtet</td></tr>
</table>
<p class=hint>Alle Begriffe im Detail: <a href="#regeln">📖 Regeln</a> (Glossar und Suche).</p></div>

<h3 id=g-commander>👑 Teil 2: Was macht Commander besonders?</h3>
<div class=gcard><ul class=gbig>
<li><b>Ein Anführer:</b> Dein Deck hat einen <b>Commander</b>, meist eine legendäre Kreatur. Er liegt zu Beginn in der <b>Kommandozone</b> neben dem Spielfeld und kann von dort jederzeit gewirkt werden, als hättest du ihn auf der Hand.</li>
<li><b>100 Karten, jede nur einmal:</b> Das Deck hat genau 100 Karten einschließlich Commander. Jede Karte darf nur einmal vorkommen. Ausgenommen sind Standardländer (Ebene, Insel, Sumpf, Gebirge, Wald, Ödnis) und Karten, die es ausdrücklich erlauben.</li>
<li><b>Farbidentität:</b> Alle Karten müssen zu den Farben deines Commanders passen. Gezählt werden alle Manasymbole auf der Karte, auch im Regeltext. Ein rot-grüner Commander erlaubt also nur rote, grüne und farblose Karten.</li>
<li><b>40 Lebenspunkte</b> statt 20, und meist sitzen <b>drei oder vier Personen</b> am Tisch, jede gegen jede.</li>
<li><b>Commander-Steuer:</b> Stirbt dein Commander oder würde er ins Exil gehen, darfst du ihn stattdessen in die Kommandozone zurücklegen. Jedes weitere Wirken kostet <b>2 Mana mehr</b> als das letzte Mal.</li>
<li><b>Commander-Schaden:</b> Wer insgesamt <b>21 Kampfschaden von demselben Commander</b> erhalten hat, verliert, egal wie viele Lebenspunkte noch übrig sind.</li>
<li><b>Freier Mulligan:</b> Gefällt dir die Starthand nicht, mischst du neu und ziehst sieben Karten. In Partien mit mehreren Gegnern ist der erste Mulligan frei, danach legst du je Mulligan eine Karte unter das Deck.</li>
<li><b>Ziehen im ersten Zug:</b> In Partien mit mehr als zwei Personen zieht auch, wer anfängt, im ersten Zug eine Karte.</li></ul></div>

<div class=gcard><h4>Spielstärke absprechen</h4>
<p>Commander ist ein gemeinschaftliches Format: Alle sollen Spaß haben. Sprecht vor der Partie kurz ab, wie stark eure Decks sind („Rule 0“). Dafür gibt es offizielle <b>Brackets</b> (Stufen 1–5): von sehr gemütlichen Themendecks bis zu turnierstarken Decks. Viele fertige Precons liegen in Stufe 2 oder 3. Besonders starke Karten stehen auf der Liste der <b>Game Changer</b>. Die Manaschmiede markiert sie und kann sie beim Deckbau weglassen. Die Stufe deines Decks zeigt die Deckansicht unter „🎚 Bracket-Einstufung“ mit Begründung; die ausführliche Erklärung steht in der Hilfe unter „Brackets“.</p></div>

<div class=gcard><h4>Am Tisch mit mehreren</h4>
<ul><li>Greif nicht immer dieselbe Person an. Zum Ziel wird, wer vorne liegt.</li>
<li>Absprachen („Ich greife dich nicht an, wenn …“) sind erlaubt, aber nicht bindend.</li>
<li>Erkläre deine Karten, wenn jemand fragt, und lies sie bei Unsicherheit laut vor.</li>
<li>Lebenspunkte und Commander-Schaden offen führen. Der <a href="#spieltisch">🎲 Spieltisch</a> nimmt dir das ab.</li></ul></div>

<h3 id=g-deck>🛠 Teil 3: Dein erstes Deck</h3>
<div class=gcard><h4>Weg A: fertiges Deck (empfohlen für den Anfang)</h4>
<p>Vorkonstruierte Commander-Decks („<b>Precons</b>“) sind sofort spielbar und untereinander ausgeglichen. Unter <a href="#precons">🎁 Precons</a> findest du alle Precons mit Kartenliste, und unter <a href="#gegner">⚔ Gegner &amp; Duell</a> kannst du sie gegeneinander antreten lassen. So siehst du vor dem Kauf, welches dir liegt.</p></div>
<div class=gcard><h4>Weg B: selbst bauen mit dem Assistenten</h4>
<ol class=gsteps>
<li>Unter <a href="#deck">🛠 Deck bauen</a> die Lieblingsfarben anklicken und/oder ein Thema eintragen, z. B. „Drachen“, „Tokens“ oder „Friedhof“.</li>
<li><b>„💡 Commander vorschlagen“</b> zeigt passende Commander mit Bild. Einen auswählen.</li>
<li><b>„Deck vorschlagen“</b> stellt 100 Karten zusammen. Optional: Budget oder deine Sammlung berücksichtigen.</li>
<li>Deck speichern, mit der Probehand und dem 🎮 Testspielfeld ein paar Züge allein durchspielen und unter „Gegner &amp; Duell“ gegen Precons antreten lassen.</li></ol>
<p><b>Faustregel für ein ausgewogenes Deck:</b> etwa 36–38 Länder, 10 Karten für zusätzliches Mana („Ramp“), 10 zum Kartenziehen, 8–10 zum Entfernen einzelner Bedrohungen und 2–3, die das ganze Spielfeld räumen. Der Rest unterstützt das Thema deines Commanders. Die Manaschmiede prüft das und zeigt Lücken an.</p></div>

<h3 id=g-partie>🎲 Teil 4: Die erste Partie</h3>
<div class=gcard><ol class=gsteps>
<li><b>Aufbauen:</b> Commander offen in die Kommandozone legen, die übrigen 99 Karten mischen. Den <a href="#spieltisch">🎲 Spieltisch</a> öffnen, Namen eintragen, Partie starten.</li>
<li><b>Startspieler:</b> im Spieltisch 🎲 antippen, dann entscheidet das Los.</li>
<li><b>Starthand:</b> alle ziehen sieben Karten. Zu wenige oder zu viele Länder (gut sind 3–4)? Mulligan nehmen.</li>
<li><b>Spielen:</b> Reihum im Uhrzeigersinn. In den ersten Zügen Länder legen und Ramp spielen, dann den Commander wirken.</li>
<li><b>Leben zählen:</b> Im Spieltisch rechts tippen = +1, links = −1, gedrückt halten = ±10. Commander-Schaden über ⚔ eintragen.</li>
<li><b>Ende:</b> Wer zuletzt übrig ist, gewinnt. Sieger im Spieltisch wählen und speichern. Daraus entsteht deine Statistik.</li></ol></div>

<div class=gcard><h4>Kleines Wörterbuch</h4>
<table class=gtab>
<tr><td><b>Friedhof</b></td><td>Ablagestapel für zerstörte und benutzte Karten</td></tr>
<tr><td><b>Exil</b></td><td>Karten ganz aus dem Spiel entfernt</td></tr>
<tr><td><b>Bibliothek</b></td><td>dein Nachziehstapel</td></tr>
<tr><td><b>Ramp</b></td><td>Karten, die schneller mehr Mana bringen</td></tr>
<tr><td><b>Removal</b></td><td>Karten, die gegnerische Karten entfernen</td></tr>
<tr><td><b>Board Wipe</b></td><td>räumt alle Kreaturen (oder mehr) vom Feld</td></tr>
<tr><td><b>Token / Spielstein</b></td><td>durch Effekte erzeugte Kreatur oder Gegenstand ohne echte Karte</td></tr>
<tr><td><b>Staple</b></td><td>Karte, die in sehr vielen Decks steckt (z. B. Sol Ring)</td></tr>
<tr><td><b>Combo</b></td><td>wenige Karten, die zusammen sofort gewinnen oder Endloses erzeugen</td></tr>
<tr><td><b>Proxy</b></td><td>Platzhalter-Ausdruck zum Testen, druckbar im Deck und unter <a href="#sammlung">📦 Sammlung</a></td></tr>
</table></div>
<p class=hint>Noch Fragen? ❓ oben rechts erklärt jede Funktion der Manaschmiede. Das vollständige offizielle Regelwerk steht unter <a href="#regeln">📖 Regeln</a>.</p>
</div>
</section>
<section id=v-deck class=page hidden>
<div class=openline id=openbox><b>📂 Gespeichertes Deck öffnen:</b> <select id=opensel><option value="">Deck wählen …</option></select>
<button type=button id=openbtn class=primary>Öffnen</button> <a href="#decks">alle Decks verwalten</a></div>
<h3>Deckbau-Assistent <button type=button class=qh data-h=bauen>?</button></h3>
<p class=hint>Alle Felder sind optional, eine Angabe genügt. Namen werden beim Tippen vorgeschlagen.</p>
<form id=b autocomplete=off>
<span class=ac><input name=commander id=cmd placeholder="Commander (Partner: A + B)" size=34></span>
<input name=theme placeholder="Thema: Mill, Lifegain, Stompy ..." size=26 list=th>
<datalist id=th><option>Mill<option>Lifegain<option>Stompy<option>Tokens<option>Counters<option>Aristocrats<option>Spellslinger<option>Voltron</datalist>
<input name=ci id=ci placeholder="Farbidentität (z. B. WUB)" size=22>
<span id=cibtns class=cibtns></span> <span class=hint id=cihint></span><br>
<span class=ac><input id=add placeholder="Karte hinzufügen (Enter)" size=30></span><br>
<textarea name=cards id=cards rows=4 cols=70 placeholder="Karten, die ins Deck sollen (eine pro Zeile, optional)"></textarea><br>
<label><input type=checkbox name=nogc id=nogc value=1>Keine Game Changer vorschlagen</label> &nbsp;
<label>Höchstpreis je Karte € <input name=maxprice id=maxprice size=5 inputmode=decimal></label> &nbsp;
<label>Budget gesamt € <input name=budget id=budget size=6 inputmode=decimal></label> &nbsp;
<label>Sammlung: <select name=coll id=coll><option value="">nicht beachten</option><option value=prefer>bevorzugen</option><option value=only>nur eigene Karten</option></select></label><br>
<details id=exbox><summary>Nicht verfügbare Karten (<span id=excount>0</span>), werden nie vorgeschlagen</summary>
<span class=ac><input id=exadd placeholder="Karte hinzufügen (Enter)" size=30></span>
<button type=button id=exclear>Liste leeren</button><br>
<textarea name=exclude id=exclude rows=4 cols=70 placeholder="Eine Karte pro Zeile"></textarea></details>
<button class=primary>Deck vorschlagen</button></form>
<div id=csugbox class=csugbox><b>💡 Noch keinen Commander?</b> Farben oben anklicken und/oder ein Thema eintragen (z. B. Drachen, Sagen, Tokens, Friedhof, Lebensgewinn).
<button type=button id=csugbtn class=primary>Commander vorschlagen</button>
<label><input type=checkbox id=cfewer> auch mit weniger Farben</label><div id=csug></div></div>
<p class=view>Ansicht: <button type=button data-v=list>Liste</button><button type=button data-v=img>Kartenbilder</button><button type=button data-v=stack>Stapel</button></p>
<div id=out></div>
</section>
<section id=v-gegner class=page hidden>
<p id=nogegner class=hint>Zuerst im Tab <a href="#deck">„Deck bauen“</a> ein Deck erstellen oder unter <a href="#decks">„Meine Decks“</a> eines laden. Danach wählst du hier den Gegner.</p>
<div id=cmpbox><h3>Gegner wählen: Precon oder eigenes Deck <button type=button class=qh data-h=gegner>?</button></h3>
<p class=hint>Vergleicht die Deckwerte mit dem Gegnerdeck; darunter Combos und das Duell über Forge.</p>
<p id=oppinfo class=big></p>
<div class=chips id=oppdecks></div>
<div id=pmissing></div>
<label for=pall><b>Precon auswählen:</b></label> <select id=pall><option value="">Alle offiziellen Precons (nach Erscheinen sortiert)</option></select><br>
<span class=ac><input id=pq placeholder="… oder nach Precon, Commander oder Set suchen" size=44></span>
<div class=chips id=psugg></div>
<div id=cmp></div><div id=combos></div><div id=duel></div><div id=pview></div></div>
</section>
<section id=v-decks class=page hidden><h3>Deck importieren &amp; gespeicherte Decks <button type=button class=qh data-h=import>?</button></h3>
<details open class=tabbox id=impbox><summary><b>Deck importieren &amp; gespeicherte Decks</b> <span class=hint id=mycount></span> <button type=button class=qh data-h=import>?</button></summary>
<p class=hint>Liste einfügen (Moxfield, Archidekt, Arena, MTGO, TappedOut, Deckstats, Forge …), Datei wählen
(.txt, .dck, .dec, .dek, .cod, .csv, .json) oder Link angeben (Archidekt, Moxfield, MTGGoldfish, TappedOut, Deckstats).</p>
<textarea id=imptext rows=6 cols=70 placeholder="Deckliste einfügen, z. B. „1 Sol Ring“ je Zeile"></textarea><br>
<input type=file id=impfile accept=".txt,.dck,.dec,.dek,.cod,.csv,.json,.mwdeck"><br>
<input id=impurl size=60 placeholder="oder Link, z. B. https://archidekt.com/decks/123456">
<button type=button id=impgo class=primary>Importieren</button>
<div id=impres></div>
<div id=inbox></div>
<h4>Gespeicherte Decks</h4><div id=mydecks></div></details>
</section>
<section id=v-sammlung class=page hidden><h3>Meine Sammlung <span class=hint id=collsum2></span> <button type=button class=qh data-h=sammlung>?</button></h3>
<p><button type=button class=primary id=scanbtn>📷 Karten scannen</button> <span class=hint>Karten mit der Kamera erfassen und zur Sammlung oder ins Deck übernehmen.</span></p>
<details open class=tabbox id=collbox><summary><b>Meine Sammlung</b> <span class=hint id=collsum></span> <button type=button class=qh data-h=sammlung>?</button></summary>
<p class=hint>Export aus ManaBox, Moxfield, Deckbox, Archidekt, Dragon Shield (CSV) oder eine einfache Liste („4 Sol Ring“ je Zeile).</p>
<textarea id=colltext rows=5 cols=70 placeholder="Sammlung einfügen oder Datei wählen"></textarea><br>
<input type=file id=collfile accept=".csv,.txt,.tsv"><br>
<label><input type=radio name=collmode value=add checked> zur Sammlung hinzufügen</label>
<label><input type=radio name=collmode value=replace> Sammlung ersetzen</label>
<button type=button id=collgo class=primary>Sammlung importieren</button>
<button type=button id=collexp title="mit Set, Nummer, Foil, Zustand und Sprache, lesbar für Moxfield, ManaBox und Archidekt">Als CSV herunterladen</button> <button type=button id=collexpn>CSV nur mit Namen</button> <button type=button id=collclr>Sammlung leeren</button>
<div id=collres></div></details>
<details class=subbox id=invbox><summary><b>📚 Bestand nach Druck, Foil, Zustand</b> <span class=hint id=invsum></span></summary>
<p class=hint>Jede Zeile ist ein Druck deiner Karten. Druck, Foil, Zustand, Sprache und Anzahl lassen sich direkt ändern; Einträge mit gleichen Angaben werden zusammengelegt. Für Deckbau und Einkaufsliste zählt die Summe je Karte.</p>
<div class=invadd><span class=ac><input id=invname placeholder="Karte hinzufügen, z. B. Sol Ring" size=28></span> <button type=button id=invpick class=primary>Druck wählen …</button></div>
<div class=invfilter><input id=invq placeholder="Filter: Name oder Set-Code" size=22>
<select id=invsort><option value=name>nach Name</option><option value=value>nach Wert</option><option value=price>nach Preis je Stück</option><option value=set>nach Set</option><option value=new>zuletzt geändert</option></select>
<select id=invonly><option value="">alle</option><option value=unknown>ohne bekannten Druck</option><option value=foil>nur Foils</option></select></div>
<div id=invres></div></details>
<details class=subbox id=shopbox><summary><b>🛒 Einkaufsliste über alle Decks</b> <span class=hint id=shopsum></span></summary>
<p class=hint>Welche Karten fehlen dir für alle gespeicherten Decks zusammen? Standardländer zählen nicht.</p>
<label><input type=checkbox id=shopshare checked> Karten wandern zwischen Decks (sonst braucht jedes Deck eigene Exemplare)</label>
<button type=button class=primary id=shopgo>Einkaufsliste berechnen</button><div id=shopres></div></details>
<details class=subbox id=buybox><summary><b>🧭 Kaufassistent</b> <span class=hint>Budget, Druck &amp; Foil, Aufteilung auf Händler, Precon-Check</span></summary>
<p class=hint>Plant den Kauf fehlender Karten: für ein Deck, alle Decks oder die Wunschliste. Je Karte Druck, Foil und Händler wählbar; gekaufte Karten landen mit dem gewählten Druck in der Sammlung.</p>
<div id=buyctl></div><div id=buyres></div></details>
<details class=subbox id=pxbox><summary><b>🖨 Proxy-Druck</b> <span class=hint>Kopien beliebiger Karten zum Testen</span></summary>
<p class=hint>Druckt Kopien von Karten in Originalgröße, als Kartenbild oder tintensparend nur mit Text. <b>Nur Kopien zum privaten Testen, keine echten Karten:</b> jede Kopie trägt den Vermerk „PROXY – keine echte Karte“.</p>
<p class=hint>🃏 Die Kopie mit einer echten, wertlosen Karte (z. B. Standardland) in eine Hülle stecken. So sehen alle Karten von hinten gleich aus, auch in durchsichtigen Hüllen.</p>
<button type=button class=primary id=pxopen>🖨 Proxys zusammenstellen</button></details>
<details class=subbox id=wishbox><summary><b>⭐ Wunschliste &amp; Preisalarm</b> <span class=hint id=wishsum></span></summary>
<p class=hint>Karten, die du kaufen möchtest. Mit Zielpreis erscheint auf der Startseite ein Hinweis, sobald der Preis darunter fällt (geprüft bei jeder Kartenaktualisierung).</p>
<div class=wishadd><input id=wishname placeholder="Karte, z. B. Sol Ring" size=28><input id=wishqty size=3 value=1 inputmode=numeric title="Anzahl">
<label>Zielpreis <input id=wishtarget size=5 inputmode=decimal placeholder="€"> €</label><button type=button id=wishgo>⭐ Hinzufügen</button></div>
<div id=wishres></div></details>
<details class=subbox id=folderbox><summary><b>📁 Ordner</b> <span class=hint id=foldersum></span></summary>
<p class=hint>Teile deiner Sammlung ordnen, z. B. „Tauschordner“ oder „Binder 1“. Die Karten bleiben in der Sammlung; ein Ordner kann nur Karten enthalten, die du besitzt.</p>
<div id=folderlist></div>
<div class=folderedit><input id=foldername placeholder="Ordnername, z. B. Tauschordner" size=26 maxlength=40><br>
<textarea id=foldertext rows=3 cols=50 placeholder="Karten, eine je Zeile, z. B. „2 Sol Ring“"></textarea><br>
<button type=button id=folderadd class=primary>In den Ordner legen</button> <button type=button id=folderrem>Aus dem Ordner nehmen</button></div>
<div id=folderres></div></details>
<details class=subbox id=chistbox><summary><b>📈 Wertverlauf der Sammlung</b></summary><div id=chistres></div></details>
</section>
<section id=v-spieltisch class=page hidden><h3>Spieltisch: Lebenszähler &amp; Spielprotokoll <button type=button class=qh data-h=spieltisch>?</button></h3>
<details open class=tabbox id=tablebox><summary><b>🎲 Spieltisch: Lebenszähler &amp; Spielprotokoll</b> <span class=hint id=gamecount></span> <button type=button class=qh data-h=spieltisch>?</button></summary>
<div id=tsetup></div><div id=tgame></div><h4>Statistik</h4><div id=tstats></div></details>
<details class=gnwrap id=gnwrap><summary><b>🏆 Spielabend: gemischte Vierer-Tische &amp; Siege</b> <span class=hint>Mitspieler per Link/QR-Code, Rangliste, Saison optional</span></summary>
<div id=gnbox></div></details>
</section>
<section id=v-regeln class=page hidden>
<h3>Offizielle Regeln <button type=button class=qh data-h=regeln>?</button></h3>
<p class=hint id=rinfo></p>
<form id=rf autocomplete=off><input id=rq size=40 placeholder="Regelnummer (z. B. 903.4) oder Begriff (z. B. commander tax)">
<button class=primary>Suchen</button></form>
<p class=chips id=rquick></p>
<div id=rres></div>
</section>
<section id=v-galerie class=page hidden><h3>🌍 Deck-Galerie <button type=button class=qh data-h=galerie>?</button></h3>
<p class=hint id=galintro>Hier stehen die Decks, die Benutzer dieses Servers veröffentlicht haben. Eigene Decks veröffentlichst du unter „📂 Meine Decks“ mit „🌍 Veröffentlichen“.</p>
<form id=galf class=galf><input id=galq placeholder="Suche: Commander, Deckname, Benutzer, Thema (z. B. Goblins, Token)" size=44>
<span class=galci id=galci></span><select id=galcim title="Farbfilter"><option value=within>höchstens diese Farben</option><option value=exact>genau diese Farben</option><option value=contains>mindestens diese Farben</option></select>
<label>bis <input id=galeur size=5 inputmode=decimal placeholder="€"> €</label>
<select id=galgc title="Game Changer"><option value="">Game Changer: egal</option><option value=0>ohne Game Changer</option><option value=3>höchstens 3 Game Changer</option></select>
<select id=galbr title="Bracket"><option value="">Bracket: egal</option><option value=12>Bracket 1–2</option><option value=3>Bracket 3</option><option value=45>Bracket 4–5</option></select>
<select id=galsort><option value=new>neueste zuerst</option><option value=likes>beliebteste zuerst</option><option value=eur>günstigste zuerst</option></select>
<button class=primary id=galgo>🔎 Suchen</button></form>
<div id=galres></div></section>
<section id=v-precons class=page hidden><h3>🎁 Precons: fertige Commander-Decks <button type=button class=qh data-h=precons>?</button></h3>
<p class=hint id=pcintro>Alle offiziellen Commander-Precons mit vollständiger Deckliste. Antippen zeigt die Liste; von dort kannst du das Deck im Editor öffnen, speichern, als Gegner nehmen oder, wenn du es gekauft hast, in deine Sammlung übernehmen.</p>
<form id=pcf class=galf><input id=pcq placeholder="Suche: Deckname, Commander oder Set" size=36><span class=galci id=pcci></span>
<select id=pcset title="Set"><option value="">alle Sets</option></select>
<select id=pcsort><option value=new>neueste zuerst</option><option value=old>älteste zuerst</option><option value=eur>günstigste zuerst</option><option value=eurd>teuerste zuerst</option><option value=own>meiste Karten in meiner Sammlung</option></select></form>
<div id=pcres></div></section>
<section id=v-suche class=page hidden>
<h3>Kartensuche <button type=button class=qh data-h=suche>?</button></h3>
<form id=f autocomplete=off>
<span class=ac><input name=q id=q placeholder="Name oder Regeltext" size=28></span>
<input name=type placeholder="Typ (z. B. Creature)" size=18>
<input name=kw placeholder="Stichwort (z. B. Flying)" size=16>
<input name=ci placeholder="Farbidentität (z. B. WUB, C)" size=22>
<input name=cmin placeholder="MW min" size=6> <input name=cmax placeholder="MW max" size=6>
<label><input type=checkbox name=legal value=1 checked>Commander-legal</label>
<label><input type=checkbox name=commander value=1>Als Commander nutzbar</label>
<button>Suchen</button></form>
<table><thead><tr><th>Karte<th>Kosten<th>Typ<th>Farbid.<th>EDHREC<th>€<th>Links</thead><tbody id=r></tbody></table>
</section>
<div id=dlg><div id=dlgin></div></div><img id=cprev alt="">
<nav id=mobnav aria-label="Navigation"></nav><div id=mobmore></div>
<footer id=legal>
<p><b>Magic: The Gathering</b> ist ein Spiel von <b>Wizards of the Coast LLC</b>. Die Manaschmiede (Commander-Deckbau-Datenbank) ist inoffizieller Fan-Inhalt
im Sinne der <a href="https://company.wizards.com/en/legal/fancontentpolicy" target=_blank rel=noopener>Fan Content Policy</a>.
Nicht von Wizards of the Coast genehmigt oder unterstützt. Teile der verwendeten Materialien (Kartennamen, -texte, -bilder, Mana-Symbole,
Comprehensive Rules) sind Eigentum von Wizards of the Coast. ©Wizards of the Coast LLC.</p>
<p lang=en><i>Manaschmiede is unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards.
Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.</i></p>
<p>Kartendaten und Bilder: <a href="https://scryfall.com" target=_blank rel=noopener>Scryfall</a> · Euro-Preise: <a href="https://www.cardmarket.com" target=_blank rel=noopener>Cardmarket</a> (Preisliste) · Precons: MTGJSON / mtg.wtf ·
Combos: <a href="https://commanderspellbook.com" target=_blank rel=noopener>Commander Spellbook</a> · Regel-Engine: Forge ·
<a href="#regeln">Offizielle Regeln</a> · <a href="#willkommen">Startseite</a> · <a href="/impressum" target=_blank>Impressum</a> · <a href="/datenschutz" target=_blank>Datenschutz</a></p></footer>
<script>
const $=(t,x,h)=>{const e=document.createElement(t);if(x!=null)e.textContent=x;if(h){e.href=h;e.target='_blank'}return e};
const J=async(u,body)=>{try{const r=await fetch(u,body?{method:'POST',body:new URLSearchParams(body)}:undefined);
 if(r.status==401&&!u.startsWith('/api/login')){location.href='/login';return {error:'Bitte anmelden.'}}
 return await r.json()}catch(e){return {error:'Keine Verbindung zum Server. Läuft das Programm noch? ('+e.message+')'}}};
// Wer bin ich? (lokal: kein Login; Server: Benutzer, Admin-Rechte, Grenzen)
let ME={server:false,admin:true,max_games:100};const MEP=J('/api/me').then(m=>{if(!m.error)ME=m;return ME});
const E=id=>document.getElementById(id);
const P=(o,x,cls)=>{const e=$('p',x);if(cls)e.className=cls;o.append(e);return e};
// Läuft eine andere Version als diese Seite? Dann einmal frisch laden.
const PAGE_VERSION='60';
J('/api/version').then(v=>{if(v.version&&v.version!=PAGE_VERSION){
 try{if(sessionStorage.getItem('reloaded')!=v.version){sessionStorage.setItem('reloaded',v.version);location.reload()}}catch(e){location.reload()}}});
// ---- Kartensymbol mit Bildvorschau (Maus darüber, am Handy antippen)
const imgFor=(img,name)=>img||('https://api.scryfall.com/cards/named?format=image&version=normal&exact='+encodeURIComponent(name));
function cardIcon(img,name){const i=$('span');i.className='cicon';i.dataset.img=imgFor(img,name);i.setAttribute('aria-label','Kartenbild: '+name);return i}
function cardName(name,link,img){const w=$('span');w.className='cname';w.append(cardIcon(img,name),link?$('a',name,link):$('span',name));return w}
(()=>{let pinned=false;const pv=()=>E('cprev');
 const place=(x,y)=>{const p=pv(),w=250,h=350;let l=x+18,t=y-h/2;if(l+w>innerWidth-8)l=x-w-18;if(l<4)l=4;
  t=Math.max(6,Math.min(t,innerHeight-h-6));p.style.left=l+'px';p.style.top=t+'px'};
 const show=(el,x,y)=>{const p=pv();if(p.dataset.src!=el.dataset.img){p.src=el.dataset.img;p.dataset.src=el.dataset.img}p.style.display='block';place(x,y)};
 const hide=()=>{pv().style.display='none';pinned=false};
 document.addEventListener('mouseover',e=>{const el=e.target.closest&&e.target.closest('.cicon');if(el&&!pinned)show(el,e.clientX,e.clientY)});
 document.addEventListener('mousemove',e=>{if(!pinned&&pv().style.display=='block'&&e.target.closest&&e.target.closest('.cicon'))place(e.clientX,e.clientY)});
 document.addEventListener('mouseout',e=>{const el=e.target.closest&&e.target.closest('.cicon');if(el&&!pinned)pv().style.display='none'});
 document.addEventListener('click',e=>{const el=e.target.closest&&e.target.closest('.cicon');
  if(el){e.preventDefault();e.stopPropagation();const r=el.getBoundingClientRect();pinned=true;show(el,r.right,r.top+r.height/2)}else if(pinned)hide()},true);
 document.addEventListener('scroll',()=>{if(pinned)hide()},{passive:true});
})();
// Optik: Magic-Stil oder neutral (wird im Browser gemerkt)
let theme='mtg';try{theme=localStorage.getItem('theme')||'mtg'}catch(e){}
function setTheme(t){theme=t;document.body.classList.toggle('mtg',t=='mtg');
 E('theme').textContent=t=='mtg'?'Optik: Magic ✦ → neutral':'Optik: neutral → Magic ✦';try{localStorage.setItem('theme',t)}catch(e){}}
E('theme').onclick=()=>setTheme(theme=='mtg'?'neutral':'mtg');setTheme(theme);
// ---------- Endgerät erkennen: Handyansicht automatisch, von Hand umschaltbar ----------
let layoutPref='auto';try{layoutPref=localStorage.getItem('layout')||'auto'}catch(e){}
const UA_MOBILE=/Android|iPhone|iPod|Windows Phone|Mobile|CommanderDB-Android/i.test(navigator.userAgent);
function isPhone(){const w=window.innerWidth;if(layoutPref=='mobile')return true;if(layoutPref=='desktop')return false;
 return UA_MOBILE?w<1000:w<=760}
const MOBMAIN=[['willkommen','🏠','Start'],['neu','🌱','Neu hier?'],['deck','🛠','Deck'],['gegner','⚔','Duell'],['spieltisch','🎲','Tisch']];
const MOBMORE=[['decks','📂 Meine Decks'],['galerie','🌍 Galerie'],['precons','🎁 Precons'],['sammlung','📦 Sammlung'],['suche','🔎 Kartensuche'],['regeln','📖 Regeln']];
function buildMobNav(){const n=E('mobnav'),m=E('mobmore');if(!n||n.childElementCount)return;
 MOBMAIN.forEach(([v,i,t])=>{const a=$('a');a.href='#'+v;a.dataset.v=v;if(v=='neu')a.className='neu';const si=$('span',i);si.className='i';a.append(si,$('span',t));a.onclick=()=>m.classList.remove('open');n.append(a)});
 const mb=$('button');mb.type='button';mb.id='mobmorebtn';const si=$('span','☰');si.className='i';mb.append(si,$('span','Mehr'));
 mb.onclick=()=>m.classList.toggle('open');n.append(mb);
 MOBMORE.forEach(([v,t])=>{const a=$('a',t);a.href='#'+v;a.dataset.v=v;if(v=='galerie'){a.hidden=!(ME&&ME.server);MEP.then(x=>a.hidden=!x.server)}a.onclick=()=>m.classList.remove('open');m.append(a)});
 const hp=$('a','❓ Hilfe');hp.href='#';hp.onclick=e=>{e.preventDefault();m.classList.remove('open');E('helpbtn').click()};m.append(hp);
 markMobNav((location.hash||'#willkommen').slice(1))}
function markMobNav(v){if(v=='start')v='deck';document.querySelectorAll('#mobnav a').forEach(a=>a.classList.toggle('on',a.dataset.v==v));
 const mb=E('mobmorebtn');if(mb)mb.classList.toggle('on',MOBMORE.some(x=>x[0]==v))}
function applyLayout(){const ph=isPhone();document.body.classList.toggle('mob',ph);if(!ph&&E('mobmore'))E('mobmore').classList.remove('open');
 const b=E('layoutbtn');if(b){b.textContent=layoutPref=='auto'?(ph?'📱 auto':'🖥 auto'):(layoutPref=='mobile'?'📱 Handy':'🖥 PC');
  b.title='Ansicht: '+(layoutPref=='auto'?'automatisch ('+(ph?'Handy erkannt':'PC erkannt')+')':layoutPref=='mobile'?'immer Handy':'immer PC')+', antippen zum Wechseln'}
 if(ph)buildMobNav()}
E('layoutbtn').onclick=()=>{layoutPref=layoutPref=='auto'?(isPhone()?'desktop':'mobile'):layoutPref=='mobile'?'desktop':'auto';
 try{localStorage.setItem('layout',layoutPref)}catch(e){};applyLayout()};
window.addEventListener('resize',()=>{if(layoutPref=='auto')applyLayout()});
applyLayout();

// Manakosten „{2}{U}{W/B}“ als farbige Symbole
function manaEl(str){const s=$('span');s.className='mana';
 (str||'').split(' // ').forEach((part,k)=>{if(k)s.append(' // ');
  (part.match(/\\{[^}]+\\}/g)||[]).forEach(t=>{const v=t.slice(1,-1),cols=v.split('/').filter(x=>'WUBRGC'.includes(x)&&x.length==1);
   const i=$('i',cols.length==v.split('/').length&&cols.length?'':v.replace('/P','').replace(/^([WUBRG])\\/([WUBRG])$/,''));i.className='pip'+(cols.length==1?' p'+cols[0]:'');
   if(cols.length==2)i.style.background='linear-gradient(135deg,var(--p'+cols[0]+') 50%,var(--p'+cols[1]+') 50%)';
   i.title=t;s.append(i)})});return s}
let view=localStorage.getItem('view')||'list',deck=null,precon=null,opp=null,imp=null;

// Vorschlagsliste unter einem Eingabefeld: opts.get(text) liefert [{t:Anzeige,v:Wert}]
function ac(inp,opts){
 const ul=document.createElement('ul');ul.hidden=true;inp.parentNode.append(ul);
 let items=[],sel=-1,timer,seq=0;
 const show=()=>{ul.innerHTML='';items.forEach((it,i)=>{const li=$('li',it.t);if(i==sel)li.className='on';
   li.onmousedown=e=>{e.preventDefault();pick(it)};ul.append(li)});ul.hidden=!items.length};
 const pick=it=>{items=[];show();opts.pick(it.v,it)};
 inp.addEventListener('input',()=>{clearTimeout(timer);const v=inp.value.trim(),my=++seq;
  if(v.length<2){items=[];show();return}
  timer=setTimeout(async()=>{const d=await opts.get(v);if(my==seq){items=d;sel=-1;show()}},150)});
 inp.addEventListener('keydown',e=>{
  if(e.key=='ArrowDown'&&items.length){sel=(sel+1)%items.length;show();e.preventDefault()}
  else if(e.key=='ArrowUp'&&items.length){sel=(sel-1+items.length)%items.length;show();e.preventDefault()}
  else if(e.key=='Escape'){items=[];show()}
  else if(e.key=='Enter'){if(sel>=0){pick(items[sel]);e.preventDefault()}
   else if(opts.enter){opts.enter();e.preventDefault()}}});
 inp.addEventListener('blur',()=>setTimeout(()=>{items=[];show()},100));
}
const names=cmd=>async v=>(await J('/api/suggest?cmd='+(cmd?1:0)+'&q='+encodeURIComponent(v))).map(n=>({t:n,v:n}));

// Commander gewählt -> Farbidentität automatisch übernehmen
const cmd=E('cmd'),ci=E('ci'),cih=E('cihint');
async function setCommander(n){
 if(n!==undefined){const parts=cmd.value.split(' + ');parts[parts.length-1]=n;cmd.value=parts.join(' + ')}
 const v=cmd.value.trim();
 if(!v){ci.readOnly=false;ci.value='';cih.textContent='';ciBtns();return}
 const ds=await Promise.all(v.split(' + ').slice(0,2).map(x=>J('/api/card?commander=1&name='+encodeURIComponent(x.trim()))));
 if(ds.some(d=>!d.name)){ci.readOnly=false;cih.textContent='Commander nicht gefunden';ciBtns();return}
 cmd.value=ds.map(d=>d.name).join(' + ');
 ci.value=[...'WUBRG'].filter(c=>ds.some(d=>(d.ci||'').includes(c))).join('')||'C';ci.readOnly=true;ciBtns();
 cih.textContent='aus Commander übernommen'+(ds.every(d=>d.can_be_commander)?'':'. Achtung: kein gültiger Commander');
 if(ds.length==2){const pc=await J('/api/partner_check?commander='+encodeURIComponent(cmd.value));if(pc.error){cih.textContent+='. Achtung: '+pc.error;cih.className='warn'}else cih.className='hint'}
}
ac(cmd,{get:v=>names(true)(v.split(' + ').pop()),pick:setCommander});
cmd.addEventListener('change',()=>setCommander());
const add=E('add'),cards=E('cards');
const append=n=>{n=n.trim();if(!n)return;cards.value=(cards.value.trim()?cards.value.trim()+'\\n':'')+n;add.value=''};
ac(add,{get:names(false),pick:append,enter:()=>append(add.value)});
ac(E('q'),{get:names(false),pick:n=>{E('q').value=n;go()}});

// Karten als Liste oder als Bilder ausgeben
function swapBtn(gi,ci){const b=$('button','⇄ Tauschen');b.type='button';b.className='sw';
 b.onclick=e=>{e.preventDefault();e.stopPropagation();openSwap(gi,ci)};return b}
function cardsOut(o,groups,edit){
 if(view=='stack')return stackOut(o,groups,edit);
 const O=o;
 groups.forEach((g,gi)=>{const o=$('div');o.className='dgroup';o.dataset.g=g.name;O.append(o);
  if(edit&&g.name!='Commander')dropZone(o,n=>moveToGroup(n,g.name));
  o.append($('h4',g.name+' ('+g.cards.reduce((s,c)=>s+c.qty,0)+')'));
  const canSwap=c=>edit&&g.name!='Commander'&&!c.basic;
  if(view=='img'){const gr=$('div');gr.className='grid';o.append(gr);
   g.cards.forEach((c,ci)=>{const a=c.image?$('a',null,c.scryfall):$('div',c.name);if(c.swapped)a.classList.add('swapped');
    if(c.image){a.title=c.name+(c.eur!=null?' · '+c.eur.toFixed(2)+' €':'');
     const im=$('img');im.src=c.image;im.loading='lazy';im.alt=c.name;a.append(im)}else a.className='ph';
    if(c.qty>1){const q=$('span','×'+c.qty);q.className='q';a.append(q)}
    if(c.gc){const s=$('span','Game Changer');s.className='g';a.append(s)}
    if(canSwap(c))a.append(swapBtn(gi,ci));
    if(edit&&g.name!='Commander')dragSrc(a,c.name);
    gr.append(a)})}
  else g.cards.forEach((c,ci)=>{const r=$('div');r.dataset.name=c.name;
   if(edit&&g.name!='Commander'){dragSrc(r,c.name);if(DSEL.on){const cb=$('input');cb.type='checkbox';cb.className='selbox';cb.checked=DSEL.names.has(c.name);
    cb.onchange=()=>{cb.checked?DSEL.names.add(c.name):DSEL.names.delete(c.name);selBar()};r.append(cb,' ')}}
   r.append(c.qty+'x ');r.append(cardName(c.name,c.scryfall,c.image));
   if(c.gc){const s=$('span',' GC');s.className='gc';r.append(s)}
   if(c.swapped){const s=$('span','getauscht');s.className='tag';r.append(s)}
   r.append(' ',manaEl(c.mana),(c.eur!=null?'  · '+c.eur.toFixed(2)+' €':''));
   if(canSwap(c))r.append(swapBtn(gi,ci));
   if(c.tags&&c.tags.length)c.tags.forEach(t=>{const x=$('span',t);x.className='tagchip';r.append(' ',x)});
   if(edit&&g.name!='Commander'){const tb=$('button','🏷');tb.type='button';tb.className='sw';tb.title='Tags bearbeiten';tb.onclick=()=>tagDialog(c,g.name);
    const mb=$('button','↓ Maybe');mb.type='button';mb.className='sw';mb.title='ins Maybeboard';mb.onclick=()=>toMaybe(gi,ci);
    const mv=$('button','⇄');mv.type='button';mv.className='sw mvbtn';mv.title='in eine andere Gruppe verschieben';mv.onclick=()=>moveDialog([c.name]);r.append(tb,mb,mv)}
   if(edit&&c.basic){const pl=$('button','+');pl.type='button';pl.className='sw';pl.title='eines mehr';
    pl.onclick=()=>{c.qty++;deck.msg='„'+c.name+'“: jetzt '+c.qty+'.';recalc()};r.append(pl)}
   if(edit&&g.name!='Commander'){const x=$('button',c.basic?'−':'✕');x.type='button';x.className='sw';x.title=c.basic?'eines entfernen':'entfernen';
    x.onclick=()=>removeCard(gi,ci);r.append(x)}
   o.append(r)})})
}
// ---- Maybeboard, Tags, Notizen
function recBox(o){const hh=$('h4','Empfehlungen, Streichvorschläge und Frust-Index');hh.append(qBtn('anpassen'));o.append(hh);
 const b=$('button','💡 Empfehlungen berechnen');b.type='button';b.id='recbtn';const res=$('div');
 const ow=$('input');ow.type='checkbox';ow.id='recowned';const lo=$('label');lo.append(ow,' nur aus meiner Sammlung');
 const me=$('input');me.id='receur';me.size=5;me.inputmode='decimal';me.placeholder='€';const lm=$('label');lm.append(' höchstens ',me,' € je Karte');
 const opt=$('div');opt.className='recopt';opt.append(b,' ',lo,' ',lm);o.append(opt,res);
 b.onclick=async()=>{res.innerHTML='';P(res,'rechne ...','hint');
  const r=await J('/api/recommend',{list:deck.export,commander:deck.commander||'',extra:JSON.stringify(deckExtra()),owned:ow.checked?1:0,maxeur:me.value});res.innerHTML='';
  if(r.error){P(res,r.error,'warn');return}
  const f=r.frust;P(res,'Frust-Index: '+f.level+' ('+String(f.score).replace('.',',')+' Punkte)'+(f.hits.length?': '+f.hits.map(h=>h.label+': '+h.cards.length).join(', '):''),'big');
  if(f.hits.length){const d=$('details');d.append($('summary','Karten dazu'));f.hits.forEach(h=>d.append($('div',h.label+': '+h.cards.join(', '))));res.append(d)}
  P(res,f.hint,'hint');
  const cols=$('div');cols.className='cols';res.append(cols);
  const list=(title,items,act)=>{const c=$('div');c.id=title.startsWith('Ergänzen')?'recadd':'reccut';c.append($('h4',title));
   if(!items.length)P(c,'Keine Vorschläge, weil es zu wenig ähnliche Decks gibt.','hint');
   items.forEach(x=>{const r=$('div');r.append(cardName(x.name,x.scryfall,x.image),' ',manaEl(x.mana||''),x.eur!=null?'  · '+Number(x.eur).toFixed(2)+' €':'');
    if(x.owned){const ok=$('span',' ✓ Sammlung');ok.className='owned';r.append(ok)}
    const w=$('div',x.why);w.className='hint';r.append(act(x),w);c.append(r)});cols.append(c)};
  list('Ergänzen',r.add,x=>{const bt=$('button','➕');bt.type='button';bt.className='sw';bt.title='ins Deck';bt.onclick=()=>addCardToDeck(x.name);return bt});
  list('Streichen erwägen',r.cut,x=>{const bt=$('button','↓ Maybe');bt.type='button';bt.className='sw';bt.title='ins Maybeboard';
   bt.onclick=()=>{const gi=deck.groups.findIndex(g=>g.cards.some(c=>c.name==x.name));if(gi>=0)toMaybe(gi,deck.groups[gi].cards.findIndex(c=>c.name==x.name))};return bt});
  if(r.gaps){const gb=$('div');gb.id='recgaps';res.append(gb);gb.append($('h4','Lücken nach Funktion'));
   const ok=Object.entries(r.counts||{}).filter(([k])=>!r.gaps.some(g=>g.role==k));
   if(!r.gaps.length)P(gb,'Ramp, Kartenziehen, Removal und Board-Wipes erreichen die Richtwerte (10 / 10 / 8 / 3).','hint');
   r.gaps.forEach(g=>{const d=$('div');d.className='recgap';d.dataset.role=g.role;
    d.append($('b',g.label+': '+g.have+' von etwa '+g.target),$('span',', es fehlen '+(g.target-g.have)));
    if(!g.cards.length)P(d,r.owned_filter?'Keine passende Karte in deiner Sammlung.':'Keine passende Karte gefunden'+(r.maxeur?' (Preisgrenze)':'')+'.','hint');
    g.cards.forEach(x=>{const row=$('div');row.className='recgcard';row.append(cardName(x.name,x.scryfall,x.image),' ',manaEl(x.mana||''),x.eur!=null?'  · '+Number(x.eur).toFixed(2)+' €':'');
     if(x.owned){const o2=$('span',' ✓ Sammlung');o2.className='owned';row.append(o2)}
     const bt=$('button','➕');bt.type='button';bt.className='sw';bt.title='ins Deck';bt.onclick=()=>{addCardToDeck(x.name);bt.disabled=true};row.append(' ',bt);d.append(row)});gb.append(d)});
   P(gb,'Richtwerte für 100-Karten-Commander-Decks; je nach Strategie (z. B. viel Ramp beim Landfall, wenig Wipes bei Kreaturendecks) bewusst abweichen.','hint')}
  P(res,r.hint,'hint')}}
async function priceBox(o){const r=await J('/api/price_history',{list:deck.export,commander:deck.commander||''});if(r.error)return;
 o.append($('h4','Preisentwicklung'));if(!r.days.length){P(o,r.hint,'hint');return}
 const s=r.series,W=520,H=110,max=Math.max(...s.map(x=>x.value)),min=Math.min(...s.map(x=>x.value));
 const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 '+W+' '+H);svg.setAttribute('width',W);svg.id='pricesvg';
 const xp=i=>s.length<2?W/2:10+i*(W-20)/(s.length-1),yp=v=>max==min?H/2:H-12-(v-min)*(H-24)/(max-min);
 const pl=document.createElementNS(ns,'polyline');pl.setAttribute('points',s.map((x,i)=>xp(i)+','+yp(x.value)).join(' '));pl.setAttribute('fill','none');pl.setAttribute('stroke','currentColor');pl.setAttribute('stroke-width','2');svg.append(pl);
 s.forEach((x,i)=>{const c=document.createElementNS(ns,'circle');c.setAttribute('cx',xp(i));c.setAttribute('cy',yp(x.value));c.setAttribute('r',3);c.setAttribute('fill','currentColor');
  const t=document.createElementNS(ns,'title');t.textContent=x.day+': '+x.value.toFixed(2).replace('.',',')+' €';c.append(t);svg.append(c)});
 o.append(svg);const a=s[0],z=s[s.length-1];
 P(o,'Deckwert '+a.day+': '+a.value.toFixed(2).replace('.',',')+' € → '+z.day+': '+z.value.toFixed(2).replace('.',',')+' € ('+(z.value>=a.value?'+':'')+(z.value-a.value).toFixed(2).replace('.',',')+' €)','big');
 if(r.usd)P(o,'Zweite Preisquelle, TCGplayer (USA) über Scryfall: ca. '+r.usd.toFixed(2).replace('.',',')+' $'+(r.usd_missing?' ('+r.usd_missing+' Karten ohne Dollarpreis)':''),'hint');
 if(r.moves.length){const t=$('table');t.id='pricemoves';o.append($('div','Größte Änderungen seit '+r.since+':'),t);const hr=t.insertRow();['Karte','vorher','jetzt','Änderung'].forEach(x=>hr.append($('th',x)));
  r.moves.forEach(m=>{const tr=t.insertRow();tr.insertCell().append(cardName(m.name));[m.from.toFixed(2)+' €',m.to.toFixed(2)+' €',(m.diff>0?'+':'')+m.diff.toFixed(2)+' €'+(m.pct!=null?' ('+(m.pct>0?'+':'')+m.pct+' %)':'')].forEach(v=>tr.insertCell().textContent=v.replace(/\\./g,','))})}
 P(o,r.hint,'hint')}
async function tokenBox(o){const r=await J('/api/tokens',{list:deck.export,commander:deck.commander||''});
 const hh=$('h4','Tokens und Spielmaterial ('+(r.tokens||[]).length+')');hh.append(qBtn('anpassen'));o.append(hh);
 const pb=$('button','🖨 Proxys drucken');pb.type='button';pb.id='proxybtn';pb.onclick=()=>proxyDialog(r.tokens||[]);o.append(pb);
 if(r.hint)P(o,r.hint,'hint');
 if(!(r.tokens||[]).length){P(o,'Keine Karten im Deck erzeugen Tokens.','hint');return}
 const t=$('table');t.id='tokentab';o.append(t);const hr=t.insertRow();['Token','Typ','erzeugt von'].forEach(x=>hr.append($('th',x)));
 r.tokens.forEach(k=>{const tr=t.insertRow();const c=tr.insertCell();c.append(k.image?cardName(k.name,k.image,k.image):$('span',k.name));
  tr.insertCell().textContent=k.type||'–';tr.insertCell().textContent=k.from.join(', ')})}
// ---------- Proxy-Druck: Kopien zum privaten Testen – Bild- oder Textfassung, Rückseiten, Tokens, Schnittlinien
const PROXY_NOTE='Proxys sind Kopien bzw. Platzhalter zum privaten Testen und keine echten Karten. Nicht verkaufen, nicht tauschen und nicht als echte Karten ausgeben; in offiziellen Turnieren sind sie nicht erlaubt. Kartenbilder und -texte sind Eigentum von Wizards of the Coast (Bilder von Scryfall). Jede Kopie trägt deshalb fest den Vermerk „PROXY – keine echte Karte“, Kartenrückseiten werden nicht gedruckt.';
const PROXY_SLEEVE='Tipp für Hüllen: Die ausgeschnittene Kopie zusammen mit einer echten, wertlosen Karte (z. B. Standardland oder übrige Common) in eine Hülle stecken, Kopie nach vorne. So zeigt jede Karte die gleiche Rückseite, auch in durchsichtigen Hüllen, und die Kopie hat Dicke und Festigkeit einer echten Karte.';
let PXOPT={mode:'img',backs:true,cut:true,gap:false,gray:false,paper:'A4'};try{Object.assign(PXOPT,JSON.parse(localStorage.getItem('pxopt')||'{}'))}catch(e){}
function proxyDialog(tokens){proxyStudio({deck:true})}
async function proxyStudio(pre){pre=pre||{};const b=$('div');b.id='pxstudio';dlgOpen('🖨 Proxys drucken (Kopien zum Testen)').append(b);
 const note=$('div');note.className='warn pxnote';note.id='pxnote';note.append($('b','Nur Kopien: '),PROXY_NOTE);b.append(note);
 const sl=$('div');sl.className='tag pxsleeve';sl.id='pxsleeve';sl.append($('b','🃏 In die Hülle: '),PROXY_SLEEVE.replace('Tipp für Hüllen: ',''));b.append(sl);
 const ta=$('textarea');ta.id='pxlist';ta.rows=8;ta.style.width='100%';ta.placeholder='Eine Karte je Zeile, z. B.\\n1 Sol Ring\\n2 Lightning Bolt\\n1 Counterspell (MH2) 267   ← bestimmter Druck';
 const src=$('div');src.className='chips';const sb=(t,id,fn)=>{const x=$('button',t);x.type='button';x.id=id;x.onclick=fn;src.append(x)};
 const hasDeck=typeof deck!='undefined'&&deck&&deck.groups&&deck.groups.length;
 const deckText=(onlyMissing)=>deck.groups.flatMap(g=>g.cards).filter(c=>!c.basic).map(c=>c.qty+' '+c.name).join('\\n');
 if(hasDeck){sb('📂 Deck im Editor','pxsrcdeck',()=>{ta.value=deckText()});
  sb('📦 Nur fehlende Karten des Decks','pxsrcmiss',async()=>{const r=await J('/api/ownership',{list:deck.export,commander:deck.commander||'',deck_name:deck.name||''});
   if(!r.has_collection){ta.value=deckText();P(src,'Keine Sammlung importiert, deshalb sind alle Karten übernommen.','hint');return}ta.value=r.missing.map(n=>'1 '+n).join('\\n')})}
 if(BUY&&BUY.items&&BUY.items.length)sb('🧭 Aus dem Kaufplan','pxsrcbuy',()=>{ta.value=BUY.items.filter(x=>!x.skip).map(x=>x.qty+' '+x.name+(x.print?' ('+x.print.set_code+') '+x.print.number:'')).join('\\n')});
 b.append($('h4','Karten'),src,ta);
 const opts=$('div');opts.className='pxopts';b.append($('h4','Druck'),opts);
 const rad=(name,val,txt)=>{const l=$('label');const r=$('input');r.type='radio';r.name=name;r.value=val;r.checked=PXOPT[name]==val;r.id='px'+name+val;l.append(r,' '+txt+' ');return l};
 const ck=(k,txt)=>{const l=$('label');const c=$('input');c.type='checkbox';c.id='px'+k;c.checked=!!PXOPT[k];l.append(c,' '+txt+' ');return l};
 opts.append($('b','Fassung: '),rad('mode','img','Kartenbild'),rad('mode','text','Nur Text (spart Tinte, ohne Kartenbild)'),$('br'),
  ck('backs','Rückseiten doppelseitiger Karten mitdrucken'),ck('tokens','Tokens des Decks mitdrucken'),$('br'),
  ck('cut','Schnittlinien'),ck('gap','2 mm Abstand zwischen den Karten'),ck('gray','Graustufen'),$('br'),
  $('b','Papier: '),rad('paper','A4','A4'),rad('paper','Letter','US Letter'));
 E('pxtokens').checked=!!pre.deck&&PXOPT.tokens!==false;if(!hasDeck)E('pxtokens').parentNode.hidden=true;
 P(opts,'Originalgröße 63 × 88 mm, 9 Karten je Seite. Beim Drucken „Tatsächliche Größe“ bzw. 100 % wählen, nicht „An Seite anpassen“.','hint');
 const ok=$('input');ok.type='checkbox';ok.id='pxok';try{ok.checked=localStorage.getItem('pxok')=='1'}catch(e){}
 const okl=$('label');okl.id='pxokl';okl.append(ok,' Ich drucke nur Kopien für den privaten Gebrauch und gebe sie nicht als echte Karten aus.');
 const go=$('button','Druckansicht öffnen');go.type='button';go.className='primary';go.id='pxgo';const info=$('div');info.id='pxinfo';
 b.append(okl,$('br'),go,info);
 if(pre.text)ta.value=pre.text;else if(pre.deck&&hasDeck)ta.value=deckText();
 go.onclick=async()=>{if(!ok.checked){info.className='warn';info.textContent='Bitte zuerst bestätigen, dass du nur Kopien für den privaten Gebrauch druckst.';return}
  try{localStorage.setItem('pxok','1')}catch(e){}
  const o={mode:b.querySelector('input[name=mode]:checked').value,paper:b.querySelector('input[name=paper]:checked').value,backs:E('pxbacks').checked,
   tokens:E('pxtokens').checked,cut:E('pxcut').checked,gap:E('pxgap').checked,gray:E('pxgray').checked};PXOPT=o;try{localStorage.setItem('pxopt',JSON.stringify(o))}catch(e){}
  if(!ta.value.trim()){info.className='warn';info.textContent='Bitte Karten eintragen.';return}
  go.disabled=true;info.className='hint';info.textContent='Lade Karten …';
  const r=await J('/api/proxy_list',{list:ta.value,backs:o.backs?1:0,tokens:o.tokens&&hasDeck?1:0});go.disabled=false;
  if(r.error){info.className='warn';info.textContent=r.error;return}
  const cards=[];r.items.forEach(x=>{for(let i=0;i<x.qty;i++){cards.push(Object.assign({},x,{face:0}));if(x.back&&o.mode=='img')cards.push(Object.assign({},x,{face:1}))}});
  closeSwap();printProxies(cards,o,r.missing)}}
function pxText(x){const c=$('div');c.className='ptext';const h=$('div');h.className='pth';h.append($('b',x.name.split(' // ')[0]),manaEl((x.mana||'').split(' // ')[0]));c.append(h);
 c.append($('div',x.type));const t=$('div');t.className='ptx';t.textContent=x.text||'';c.append(t);
 if(x.pt||x.loy){const s=$('div',x.pt||('Loyalität '+x.loy));s.className='ptpt';c.append(s)}return c}
function printProxies(cards,o,miss){o=Object.assign({mode:'img',cut:true,gap:false,gray:false,paper:'A4'},o||{});miss=miss||[];
 let pa=E('printarea');if(!pa){pa=$('div');pa.id='printarea';document.body.append(pa)}pa.innerHTML='';
 pa.className=(o.cut?'pxcut ':'')+(o.gap?'pxgap ':'')+(o.gray?'pxgray':'');
 let ps=E('pxpage');if(!ps){ps=document.createElement('style');ps.id='pxpage';document.head.append(ps)}ps.textContent='@media print{@page{size:'+(o.paper=='Letter'?'letter':'A4')+';margin:8mm}}';
 const bar=$('div');bar.className='noprint';bar.append($('b',cards.length+' Kopien · '+Math.ceil(cards.length/9)+' Seiten '),' ');
 const pr=$('button','Drucken / als PDF speichern');pr.type='button';pr.className='primary';pr.id='pxprint';pr.onclick=()=>window.print();
 const cl=$('button','Schließen');cl.type='button';cl.id='pxclose';cl.onclick=()=>{pa.remove();document.body.classList.remove('printing')};bar.append(pr,' ',cl);
 bar.append($('div',PROXY_NOTE),$('div',PROXY_SLEEVE));if(miss.length)bar.append($('div','Nicht gefunden (nicht gedruckt): '+miss.join(', ')));pa.append(bar);
 for(let i=0;i<cards.length;i+=9){const pg=$('div');pg.className='ppage';cards.slice(i,i+9).forEach(x=>{const c=$('div');c.className='pcard'+(o.mode=='text'||!x.front?' ptextcard':'');
   const src=x.src||(x.face?x.back:x.front);
   if(o.mode=='text'||!src)c.append(pxText(x));else{const im=$('img');im.src=src;im.alt=x.name+(x.face?' (Rückseite)':'');im.onerror=()=>{im.remove();c.classList.add('ptextcard');c.prepend(pxText(x))};c.append(im)}
   const m=$('span','PROXY – keine echte Karte');m.className='pmark';c.append(m);pg.append(c)});pa.append(pg)}
 document.body.classList.add('printing');window.scrollTo(0,0)}
function deckExtra(){const tags={},grp={};deck.groups.forEach(g=>g.cards.forEach(c=>{if(c.tags&&c.tags.length)tags[c.name]=c.tags;if(c.grp)grp[c.name]=c.grp}));
 (deck.maybe||[]).forEach(c=>{if(c.tags&&c.tags.length)tags[c.name]=c.tags});
 return {maybe:(deck.maybe||[]).map(c=>c.name),tags:tags,notes:deck.primer||'',groups:grp,bracket:deck.bracketTarget||''}}
async function applyExtra(raw){let ex={};try{ex=JSON.parse(raw||'{}')}catch(e){}
 const tags=ex.tags||{};deck.groups.forEach(g=>g.cards.forEach(c=>{if(tags[c.name])c.tags=tags[c.name]}));
 Object.entries(ex.groups||{}).forEach(([n,gname])=>moveToGroup(n,gname,true));
 deck.primer=ex.notes||'';deck.bracketTarget=ex.bracket||'';
 deck.maybe=(await Promise.all((ex.maybe||[]).map(n=>J('/api/card_info?name='+encodeURIComponent(n))))).filter(c=>!c.error).map(c=>Object.assign(c,{qty:1,tags:tags[c.name]||[]}))}
function toMaybe(gi,ci){const g=deck.groups[gi],c=g.cards[ci];deck.maybe=deck.maybe||[];
 if(!deck.maybe.some(x=>x.name==c.name))deck.maybe.push(Object.assign({},c,{qty:1}));
 if(c.qty>1)c.qty--;else g.cards.splice(ci,1);if(!g.cards.length)deck.groups.splice(gi,1);
 deck.msg='„'+c.name+'“ ins Maybeboard verschoben.';recalc()}
function maybeBox(o){const m=deck.maybe||[];const hh=$('h4','Maybeboard ('+m.length+'): Kandidaten, die nicht mitzählen');hh.append(qBtn('anpassen'));o.append(hh);
 o.id='maybezone';dropZone(o,n=>{const gi=deck.groups.findIndex(g=>g.cards.some(c=>c.name==n));if(gi>=0)toMaybe(gi,deck.groups[gi].cards.findIndex(c=>c.name==n))});
 const row=$('div');const inp=$('input');inp.size=30;inp.placeholder='Karte fürs Maybeboard';inp.id='maybeadd';const sp=$('span');sp.className='ac';sp.append(inp);row.append(sp);o.append(row);
 const addM=async n=>{const c=await J('/api/card_info?name='+encodeURIComponent(n));if(c.error){deck.msg=c.error;showDeck();return}
  deck.maybe=deck.maybe||[];if(!deck.maybe.some(x=>x.name==c.name))deck.maybe.push(Object.assign(c,{qty:1,tags:[]}));inp.value='';showDeck()};
 ac(inp,{get:names(false),pick:addM});inp.addEventListener('keydown',e=>{if(e.key=='Enter'&&inp.value.trim()){e.preventDefault();addM(inp.value.trim())}});
 if(!m.length){P(o,'Leer. Mit „↓ Maybe“ bei einer Karte oder dem Feld oben fügst du Kandidaten hinzu.','hint');return}
 m.forEach((c,i)=>{const r=$('div');r.className='maybe';r.dataset.name=c.name;r.append(cardName(c.name,c.scryfall,c.image),' ',manaEl(c.mana),c.eur!=null?'  · '+c.eur.toFixed(2)+' €':'');
  (c.tags||[]).forEach(t=>{const x=$('span',t);x.className='tagchip';r.append(' ',x)});
  const up=$('button','↑ ins Deck');up.type='button';up.className='sw';up.onclick=async()=>{deck.maybe.splice(i,1);await addCardToDeck(c.name);
   const nc=deck.groups.flatMap(g=>g.cards).find(x=>x.name==c.name);if(nc&&c.tags)nc.tags=c.tags;showDeck()};
  const x=$('button','✕');x.type='button';x.className='sw';x.title='aus dem Maybeboard entfernen';x.onclick=()=>{deck.maybe.splice(i,1);showDeck()};
  r.append(up,x);o.append(r)})}
function tagBox(o){const map={};deck.groups.filter(g=>g.name!='Commander').forEach(g=>g.cards.forEach(c=>(c.tags||[]).forEach(t=>{(map[t]=map[t]||[]).push(c)})));
 const ks=Object.keys(map).sort();if(!ks.length)return;
 o.append($('h4','Nach Tags'));ks.forEach(t=>{const d=$('div');const b=$('b',t+' ('+map[t].reduce((s,c)=>s+c.qty,0)+'): ');d.append(b,map[t].map(c=>c.name).join(', '));o.append(d)})}
function notesBox(o){const hh=$('h4','Notizen / Primer');o.append(hh);const t=$('textarea');t.rows=4;t.cols=70;t.id='decknotes';
 t.placeholder='Spielweise, Mulligan-Regeln, Combos, Kaufliste … (wird mit dem Deck gespeichert)';t.value=deck.primer||'';t.oninput=()=>{deck.primer=t.value};o.append(t)}
function allTags(){const s=new Set(['Ramp','Kartenvorteil','Entfernung','Massenentfernung','Wincon','Combo','Schutz','Tutor','Synergie']);
 deck.groups.forEach(g=>g.cards.forEach(c=>(c.tags||[]).forEach(t=>s.add(t))));return [...s].sort()}
function tagDialog(c,gname){const b=dlgOpen('Tags für '+c.name);
 P(b,'Eigene Kategorien, mit Komma getrennt (z. B. „Ramp, Wincon“). Sie werden mit dem Deck gespeichert.','hint');
 const inp=$('input');inp.size=50;inp.id='tagin';inp.value=(c.tags||[]).join(', ');b.append(inp);
 const chips=$('div');b.append(chips);allTags().forEach(t=>{const x=$('button',t);x.type='button';x.className='tagchip';
  x.onclick=()=>{const cur=inp.value.split(',').map(v=>v.trim()).filter(Boolean);if(!cur.includes(t))cur.push(t);inp.value=cur.join(', ')};chips.append(x,' ')});
 const ok=$('button','Übernehmen');ok.type='button';ok.className='primary';ok.id='tagok';
 ok.onclick=()=>{c.tags=[...new Set(inp.value.split(',').map(v=>v.trim()).filter(Boolean))].slice(0,8);closeSwap();showDeck()};b.append($('p'),ok)}
function removeCard(gi,ci){const g=deck.groups[gi],c=g.cards[ci];
 if(c.qty>1)c.qty--;else g.cards.splice(ci,1);
 if(!g.cards.length)deck.groups.splice(gi,1);
 deck.msg='„'+c.name+'“ entfernt.';recalc()}
async function addCardToDeck(name){
 const c=await J('/api/card_info?name='+encodeURIComponent(name));
 if(c.error){deck.msg=c.error;showDeck();return}
 const all=deck.groups.flatMap(g=>g.cards);
 if(!c.legal){deck.msg=c.name+' ist im Commander-Format nicht legal und wurde nicht hinzugefügt.';showDeck();return}
 const dci=deck.ci||'';
 if([...(c.ci||'')].some(x=>!dci.includes(x))){deck.msg=c.name+' passt nicht zur Farbidentität ('+(dci||'farblos')+') und wurde nicht hinzugefügt.';showDeck();return}
 const have=all.find(x=>x.name==c.name);
 if(have&&!c.basic){deck.msg=c.name+' ist schon im Deck (Commander erlaubt jede Karte nur einmal).';showDeck();return}
 if(have){have.qty++}
 else{const gname=c.land?'Länder':'Manuell hinzugefügt';let g=deck.groups.find(x=>x.name==gname);
  if(!g){g={name:gname,cards:[]};const li=deck.groups.findIndex(x=>x.name=='Länder');
   if(gname=='Länder'||li<0)deck.groups.push(g);else deck.groups.splice(li,0,g)}
  g.cards.push(Object.assign(c,{qty:1,added:true}))}
 deck.msg='„'+c.name+'“ hinzugefügt'+(c.hint?' ('+c.hint+')':'')+'.';recalc()}
async function manaBox(o){const box=$('div');o.append(box);
 const r=await J('/api/manabase',{list:deck.export,commander:deck.commander||''});
 if(r.error||!r.colors){return}
 const hh=$('h4','Manabasis: Farbquellen');hh.append(qBtn('anpassen'));box.append(hh);
 P(box,r.lands+' Länder bei '+r.cards+' Karten · Ø Manawert der Nicht-Länder '+String(r.avg_mv).replace('.',','),'hint');
 if(!r.colors.length){P(box,'Keine farbigen Kosten im Deck.','hint');return}
 const t=$('table');box.append(t);const hr=t.insertRow();
 ['Farbe','Quellen','Karten mit der Farbe','Farbsymbole','Ø Chance rechtzeitig','Einschätzung','am schwierigsten'].forEach(x=>hr.append($('th',x)));
 for(const c of r.colors){const tr=t.insertRow();[c.label,c.sources,c.cards,c.pips,c.avg+' %'].forEach(x=>tr.insertCell().textContent=x);
  const st=tr.insertCell();st.textContent=c.status;st.className=c.avg>=90?'tag':(c.avg>=80?'hint':'warn');
  tr.insertCell().textContent=c.weak.slice(0,3).map(w=>w.name+' ('+w.prob+' %)').join(', ')||'–'}
 P(box,r.hint,'hint')}
// ================= Testspielfeld (Goldfish): Deck ausprobieren ohne Gegner =================
let PT=null;const PTU=[];
const ptId=()=>Math.random().toString(36).slice(2,9);
function ptCard(c,extra){return Object.assign({id:ptId(),name:c.name,image:c.image||'',land:!!c.land,mana:c.mana||'',cmc:c.cmc||0,scryfall:c.scryfall||'',tapped:false,ctr:0,token:false},extra||{})}
function ptNew(){if(!deck||!deck.groups){alert('Bitte zuerst ein Deck bauen oder öffnen.');return}pvStart(false)}
function ptNewClassic(){if(!deck||!deck.groups){alert('Bitte zuerst ein Deck bauen oder öffnen.');return}
 const lib=shuffle(libraryCards().map(c=>ptCard(c)));
 const cz=(deck.groups.find(g=>g.name=='Commander')||{cards:[]}).cards.map(c=>ptCard(c,{cmdr:true}));
 PT={name:deck.name||(cz[0]&&cz[0].name)||'Deck',lib:lib,hand:[],bf:[],gy:[],ex:[],cz:cz,turn:1,life:40,mull:0,mullBottom:0,casts:{},log:[]};
 PTU.length=0;ptDraw(7,true);ptLog('Partie gestartet, 7 Karten gezogen.');ptOpen()}
function ptSnap(){PTU.push(JSON.stringify(PT));if(PTU.length>40)PTU.shift()}
function ptUndo(){if(!PTU.length)return;PT=JSON.parse(PTU.pop());ptRender()}
function ptLog(t){PT.log.unshift('Zug '+PT.turn+': '+t);PT.log.length=Math.min(PT.log.length,60)}
function ptDraw(n,silent){for(let i=0;i<n;i++){const c=PT.lib.shift();if(!c){ptLog('Bibliothek leer, du würdest verlieren!');break}PT.hand.push(c)}if(!silent)ptLog(n+' Karte'+(n>1?'n':'')+' gezogen.')}
const PTZ={hand:'Hand',bf:'Spielfeld',gy:'Friedhof',ex:'Exil',lib:'Bibliothek',cz:'Kommandozone'};
function ptFind(id){for(const z of ['hand','bf','gy','ex','lib','cz']){const i=PT[z].findIndex(c=>c.id==id);if(i>=0)return [z,i]}return [null,-1]}
// Karte verschieben; pos: 'top' | 'bottom' (Bibliothek)
function ptMove(id,to,pos){ptSnap();const [z,i]=ptFind(id);if(!z)return;const c=PT[z].splice(i,1)[0];
 if(c.token&&to!='bf'){ptLog('Token „'+c.name+'“ verschwindet.');ptRender();return}
 c.tapped=false;if(to!='bf')c.ctr=0;
 if(to=='lib'){pos=='bottom'?PT.lib.push(c):PT.lib.unshift(c)}else PT[to].push(c);
 if(z=='cz'&&to=='bf'){PT.casts[c.name]=(PT.casts[c.name]||0)+1}
 ptLog(c.name+': '+PTZ[z]+' → '+PTZ[to]+(to=='lib'?(pos=='bottom'?' (unten)':' (oben)'):''));ptRender()}
function ptPlay(id){const [z,i]=ptFind(id);if(!z)return;const c=PT[z][i];
 if(PT.mullBottom>0&&z=='hand'){ptSnap();PT.hand.splice(i,1);PT.lib.push(c);PT.mullBottom--;ptLog(c.name+' unter die Bibliothek (Mulligan).');ptRender();return}
 if(c.land&&z=='hand'){const played=PT.bf.filter(x=>x.land&&x.playedTurn==PT.turn).length;c.playedTurn=PT.turn;if(played)ptLog('Hinweis: schon ein Land in diesem Zug gespielt.')}
 ptMove(id,'bf')}
function ptTap(id){const [z,i]=ptFind(id);if(z!='bf')return;ptSnap();PT.bf[i].tapped=!PT.bf[i].tapped;ptRender()}
function ptNext(){ptSnap();PT.turn++;PT.bf.forEach(c=>c.tapped=false);ptDraw(1,true);ptLog('Neuer Zug: enttappt, 1 Karte gezogen.');ptRender()}
function ptMull(){ptSnap();const n=PT.mull+1;PT.lib=shuffle(PT.lib.concat(PT.hand));PT.hand=[];ptDraw(7,true);PT.mull=n;PT.mullBottom=Math.max(0,n-1);
 ptLog('Mulligan '+n+(n==1?' (in Mehrspieler-Partien frei)':'')+': 7 neue Karten'+(PT.mullBottom?', lege '+PT.mullBottom+' unter die Bibliothek':'')+'.');ptRender()}
function ptShuffle(){ptSnap();PT.lib=shuffle(PT.lib);ptLog('Bibliothek gemischt.');ptRender()}
function ptToken(name,img){ptSnap();PT.bf.push({id:ptId(),name:name,image:img||'',land:false,mana:'',tapped:false,ctr:0,token:true});ptLog('Token „'+name+'“ erzeugt.');ptRender()}
function ptCtr(id,d){const [z,i]=ptFind(id);if(z!='bf')return;ptSnap();PT.bf[i].ctr=Math.max(0,(PT.bf[i].ctr||0)+d);ptRender()}
function ptCopy(id){const [z,i]=ptFind(id);if(z!='bf')return;const c=PT.bf[i];ptToken(c.name+' (Kopie)',c.image)}
// ---------- Darstellung ----------
// ---- Handy: Querformat, Kartengröße und große Kartenansicht für beide Spieltische
let TSIZE=1;try{TSIZE=parseFloat(localStorage.getItem('tsize'))||1}catch(e){}
const TSIZES=[.75,1,1.3,1.6];
function tableSize(d){const i=Math.max(0,Math.min(TSIZES.length-1,TSIZES.indexOf(TSIZE)+d));TSIZE=TSIZES[i<0?1:i];
 try{localStorage.setItem('tsize',TSIZE)}catch(e){}document.documentElement.style.setProperty('--tk',TSIZE)}
document.documentElement.style.setProperty('--tk',TSIZE);
async function tableLandscape(){let full=false,lock=false;
 try{if(!document.fullscreenElement&&document.documentElement.requestFullscreen){await document.documentElement.requestFullscreen({navigationUI:'hide'})}full=!!document.fullscreenElement}catch(e){}
 try{if(screen.orientation&&screen.orientation.lock){await screen.orientation.lock('landscape');lock=true}}catch(e){}
 if(!lock)tableNote('Dieses Gerät lässt die Drehung nicht automatisch zu (z. B. iPhone). Bitte das Handy quer halten'+(full?'.':' und die Bildschirmsperre für die Drehung ausschalten.'));
 return lock}
function tableExit(){try{if(screen.orientation&&screen.orientation.unlock)screen.orientation.unlock()}catch(e){}
 try{if(document.fullscreenElement)document.exitFullscreen()}catch(e){}}
function tableNote(t){const n=$('div',t);n.className='tnote';n.onclick=()=>n.remove();document.body.append(n);setTimeout(()=>n.remove(),6000)}
function rotHint(){const h=$('div');h.className='rothint';let off=false;try{off=localStorage.getItem('rothint')=='0'}catch(e){}if(off)return h;
 h.append('📱 Quer gehalten sind Hand und Spielfeld besser lesbar. ');
 const b=$('button','Quer + Vollbild');b.type='button';b.onclick=e=>{e.stopPropagation();tableLandscape()};
 const x=$('button','✕');x.type='button';x.title='Hinweis nicht mehr zeigen';x.onclick=e=>{e.stopPropagation();h.remove();try{localStorage.setItem('rothint','0')}catch(e){}};h.append(b,' ',x);return h}
// Textansicht: Karten als lesbare Kacheln (Name, Kosten, Typ, Regeltext, Stärke/Widerstand)
let TTEXT=false;try{TTEXT=localStorage.getItem('ttext')=='1'}catch(e){}
const CTX={};let CTXP=null;
function ttextRerender(){if(PT&&E('pt')&&!E('pt').hidden)ptRender();if(typeof PV!='undefined'&&PV&&E('pv')&&!E('pv').hidden)pvRender()}
function ttextNames(){const n=new Set();const add=c=>{if(c&&c.name)n.add(c.name)};
 if(PT&&E('pt')&&!E('pt').hidden)['hand','bf','gy','ex','cz'].forEach(z=>(PT[z]||[]).forEach(add));
 if(typeof PV!='undefined'&&PV&&E('pv')&&!E('pv').hidden)PV.pl.forEach(p=>['hand','bf','gy','ex','cz'].forEach(z=>(p[z]||[]).forEach(add)));
 return [...n].filter(x=>!(x in CTX))}
function ttextLoad(){if(!TTEXT||CTXP)return;const need=ttextNames();if(!need.length)return;
 CTXP=J('/api/card_texts',{names:JSON.stringify(need)}).then(r=>{need.forEach(n=>CTX[n]=(r.cards||{})[n]||{type:'',text:'',mana:'',pt:'',loy:''});CTXP=null;ttextRerender()}).catch(()=>{CTXP=null})}
function ttextToggle(){TTEXT=!TTEXT;try{localStorage.setItem('ttext',TTEXT?'1':'0')}catch(e){}ttextRerender();ttextLoad()}
function textTile(c,full){const x=CTX[c.name]||{};const t=$('div');t.className='ctile';
 const h=$('div');h.className='cth';h.append($('b',c.name));const m=x.mana||c.mana||'';if(m)h.append(manaEl(m));t.append(h);
 const ty=x.type||c.type||(c.token?'Token':'');if(ty)t.append(Object.assign($('div',ty),{className:'cty'}));
 let tx=x.text||'';if(!full&&tx.length>150)tx=tx.slice(0,140).replace(/\\s+\\S*$/,'')+' …';
 if(tx&&!(c.land&&!full&&/^\\(\\{T\\}: Add/.test(tx)))t.append(Object.assign($('div',tx),{className:'ctx'}));
 if(!(c.name in CTX)&&!full)t.append(Object.assign($('div','…'),{className:'ctx'}));
 const st=x.pt||x.loy;if(st)t.append(Object.assign($('div',st),{className:'cpt'}));return t}
function tableTools(B){return [B('Aa','Textansicht: Karten als lesbare Textkacheln statt Bildern',ttextToggle,'ttext'),B('📱 Quer','Vollbild und Querformat (Handy)',()=>tableLandscape(),'tquer'),B('A−','Karten kleiner',()=>{tableSize(-1)},'tsmall'),B('A+','Karten größer',()=>{tableSize(1)},'tbig')]}
function cardZoom(c){const old=E('czoom');if(old)old.remove();const z=$('div');z.id='czoom';z.onclick=()=>z.remove();
 if(TTEXT||!c.image){const tt=textTile(c,true);tt.classList.add('big');z.append(tt);z.append($('div','Antippen zum Schließen'));document.body.append(z);
  if(!(c.name in CTX))J('/api/card_texts',{names:JSON.stringify([c.name])}).then(r=>{CTX[c.name]=(r.cards||{})[c.name]||{};if(E('czoom')){z.remove();cardZoom(c)}});return}
 if(c.image){const im=$('img');im.src=c.image;im.alt=c.name;im.onerror=()=>{im.remove();z.prepend(txt())};z.append(im)}
 const txt=()=>{const t=$('div');t.className='cztext';t.append($('b',c.name),$('div',(c.mana||c.mana_cost||'')),$('div',c.type||c.type_line||''));return t};
 if(!c.image)z.append(txt());z.append($('div','Antippen zum Schließen'));document.body.append(z)}
function ptOpen(){let o=E('pt');if(!o){o=$('div');o.id='pt';document.body.append(o);
  document.addEventListener('keydown',e=>{if(!PT||!E('pt')||E('pt').hidden||/INPUT|TEXTAREA|SELECT/.test(e.target.tagName))return;
   const k=e.key.toLowerCase();if((e.ctrlKey||e.metaKey)&&k=='z'){e.preventDefault();ptUndo()}else if(k=='d')ptDrawBtn();else if(k=='n')ptNext();else if(k=='u'){ptSnap();PT.bf.forEach(c=>c.tapped=false);ptRender()}
   else if(k=='m')ptShuffle();else if(k=='z')ptUndo();else if(k=='escape')ptClose()})}
 o.hidden=false;document.body.classList.add('ptopen');ptRender()}
function ptClose(){const o=E('pt');if(o)o.hidden=true;document.body.classList.remove('ptopen');tableExit()}
function ptDrawBtn(){ptSnap();ptDraw(1);ptRender()}
function ptMenu(ev,items){ev.preventDefault();ev.stopPropagation();const old=E('ptmenu');if(old)old.remove();
 const m=$('div');m.id='ptmenu';items.forEach(([t,fn])=>{const b=$('button',t);b.type='button';b.onclick=e=>{e.stopPropagation();m.remove();fn()};m.append(b)});
 const x=$('button','✕ schließen');x.type='button';x.onclick=()=>m.remove();m.append(x);E('pt').append(m);
 const r=E('pt').getBoundingClientRect(),px=(ev.clientX||(ev.touches&&ev.touches[0].clientX)||r.width/2),py=(ev.clientY||(ev.touches&&ev.touches[0].clientY)||r.height/2);
 m.style.left=Math.max(4,Math.min(px,r.width-210))+'px';m.style.top=Math.max(4,Math.min(py,r.height-m.offsetHeight-8))+'px'}
function ptMenuFor(c,z){const it=[['🔍 Groß ansehen',()=>cardZoom(c)]];const id=c.id;
 if(z=='hand')it.push(['▶ Ausspielen',()=>ptPlay(id)]);
 if(z=='bf')it.push([c.tapped?'↺ Enttappen':'↻ Tappen',()=>ptTap(id)],['+1 Marke',()=>ptCtr(id,1)],['−1 Marke',()=>ptCtr(id,-1)],['⧉ Kopie als Token',()=>ptCopy(id)]);
 if(z!='hand')it.push(['✋ Auf die Hand',()=>ptMove(id,'hand')]);
 if(z!='bf'&&z!='hand')it.push(['▶ Aufs Spielfeld',()=>ptMove(id,'bf')]);
 if(z!='gy')it.push(['🪦 Friedhof',()=>ptMove(id,'gy')]);
 if(z!='ex')it.push(['🌀 Exil',()=>ptMove(id,'ex')]);
 it.push(['⬆ Oben auf die Bibliothek',()=>ptMove(id,'lib','top')],['⬇ Unter die Bibliothek',()=>ptMove(id,'lib','bottom')]);
 if(c.cmdr&&z!='cz')it.push(['👑 In die Kommandozone',()=>ptMove(id,'cz')]);
 return it}
function ptCardEl(c,z){const d=$('div');d.className='ptc'+(c.tapped?' tap':'')+(c.token?' tok':'')+(c.land?' land':'');d.dataset.id=c.id;d.title=c.name;
 if(c.image&&!c.token){const im=$('img');im.src=c.image;im.alt=c.name;im.loading='lazy';im.onerror=()=>{im.remove()};d.append(im)}else if(c.image){const im=$('img');im.src=c.image;im.alt=c.name;im.onerror=()=>im.remove();d.append(im)}
 const nm=$('span',c.name);nm.className='ptn';d.append(nm);
 if(TTEXT){d.innerHTML='';d.classList.add('txt');d.append(textTile(c))}
 if(c.ctr){const b=$('b','+'+c.ctr);b.className='ptctr';d.append(b)}
 let t=null,long=false;
 d.addEventListener('pointerdown',e=>{long=false;clearTimeout(t);t=setTimeout(()=>{long=true;ptMenu(e,ptMenuFor(c,z))},550)});
 ['pointerup','pointerleave','pointercancel'].forEach(ev=>d.addEventListener(ev,()=>clearTimeout(t)));
 d.addEventListener('contextmenu',e=>{clearTimeout(t);ptMenu(e,ptMenuFor(c,z))});
 d.addEventListener('click',e=>{if(long){long=false;return}if(z=='hand')ptPlay(c.id);else if(z=='bf')ptTap(c.id);else if(z=='cz')ptMove(c.id,'bf');else ptMenu(e,ptMenuFor(c,z))});
 return d}
function ptZoneList(z,title){const o=E('pt');const old=E('ptlist');if(old)old.remove();const w=$('div');w.id='ptlist';
 const h=$('div');h.className='pth';h.append($('b',title+' ('+PT[z].length+')'));const x=$('button','✕');x.type='button';x.onclick=()=>w.remove();h.append(x);w.append(h);
 const list=z=='lib'?PT.lib.slice().sort((a,b)=>a.name.localeCompare(b.name)):PT[z].slice().reverse();
 if(z=='lib')P(w,'Bibliothek durchsuchen: Karte antippen für Aktionen. Danach wird automatisch gemischt.','hint');
 const g=$('div');g.className='ptgrid';list.forEach(c=>{const el=ptCardEl(c,z);el.onclick=e=>{e.stopPropagation();ptMenu(e,ptMenuFor(c,z).map(([t,fn])=>[t,()=>{fn();if(z=='lib'){PT.lib=shuffle(PT.lib)}w.remove()}]))};g.append(el)});
 w.append(g);o.append(w)}
function ptTopX(){const n=parseInt(prompt('Wie viele Karten von oben ansehen?','3')||'0',10);if(!n)return;const o=E('pt');const old=E('ptlist');if(old)old.remove();
 const w=$('div');w.id='ptlist';const h=$('div');h.className='pth';h.append($('b','Oberste '+Math.min(n,PT.lib.length)+' Karten (oben = links)'));const x=$('button','✕ fertig');x.type='button';x.onclick=()=>{w.remove();ptRender()};h.append(x);w.append(h);
 P(w,'Für jede Karte wählen: oben lassen, unter die Bibliothek (Scry), in den Friedhof (Mahlen/Surveil), auf die Hand oder aufs Spielfeld.','hint');
 const g=$('div');g.className='ptgrid';PT.lib.slice(0,n).forEach(c=>{const el=ptCardEl(c,'lib');el.onclick=e=>{e.stopPropagation();ptMenu(e,[['✋ Auf die Hand',()=>{ptMove(c.id,'hand');el.remove()}],['▶ Aufs Spielfeld',()=>{ptMove(c.id,'bf');el.remove()}],['⬇ Unter die Bibliothek',()=>{ptMove(c.id,'lib','bottom');el.remove()}],['🪦 Friedhof',()=>{ptMove(c.id,'gy');el.remove()}],['🌀 Exil',()=>{ptMove(c.id,'ex');el.remove()}]])};g.append(el)});
 w.append(g);o.append(w)}
async function ptTokens(){const o=E('pt');const old=E('ptlist');if(old)old.remove();const w=$('div');w.id='ptlist';
 const h=$('div');h.className='pth';h.append($('b','Token erzeugen'));const x=$('button','✕');x.type='button';x.onclick=()=>w.remove();h.append(x);w.append(h);
 const f=$('div');const inp=$('input');inp.placeholder='Eigener Token, z. B. 1/1 Goblin';inp.id='pttokname';const ok=$('button','Erzeugen');ok.type='button';ok.onclick=()=>{if(inp.value.trim()){w.remove();ptToken(inp.value.trim())}};inp.onkeydown=e=>{if(e.key=='Enter')ok.click()};f.append(inp,' ',ok);w.append(f);
 o.append(w);const lst=$('div');lst.className='ptgrid';w.append(lst);P(lst,'Lade Tokens deines Decks …','hint');
 const cmd=(deck.groups.find(g=>g.name=='Commander')||{cards:[]}).cards.map(c=>c.name).join(' + ');
 const list=deck.groups.flatMap(g=>g.cards.map(c=>c.qty+' '+c.name)).join('\\n');
 const r=await J('/api/tokens',{list:list,commander:cmd});lst.innerHTML='';
 (r.tokens||[]).forEach(t=>{const b=$('button',(t.name+(t.type?' ('+t.type+')':'')));b.type='button';b.title='aus: '+(t.from||[]).join(', ');b.onclick=()=>{w.remove();ptToken(t.name,t.image||'')};lst.append(b)});
 if(!(r.tokens||[]).length)P(lst,'Keine Tokens im Deck erkannt. Oben kannst du einen eigenen eintragen.','hint')}
function ptRender(){setTimeout(ttextLoad,0);const o=E('pt');if(!o||!PT)return;const keepList=E('ptlist');o.innerHTML='';
 const bar=$('div');bar.className='ptbar';
 const B=(t,ti,fn,id)=>{const b=$('button',t);b.type='button';b.title=ti;if(id)b.id=id;b.onclick=fn;return b};
 const untapped=PT.bf.filter(c=>c.land&&!c.tapped).length,lands=PT.bf.filter(c=>c.land).length;
 const info=$('span');info.className='ptinfo';info.innerHTML='';info.append($('b','🎮 '+PT.name),' · Zug ',$('b',String(PT.turn)),' · Länder '+untapped+'/'+lands+' ungetappt');
 const life=$('span');life.className='ptlife';life.append(B('−','Leben −1',()=>{PT.life--;ptRender()},'ptlm'),$('b','❤ '+PT.life),B('+','Leben +1',()=>{PT.life++;ptRender()},'ptlp'));
 bar.append(info,life,B('🃏 Ziehen','Karte ziehen (D)',ptDrawBtn,'ptdraw'),B('⏭ Nächster Zug','Enttappen und ziehen (N)',ptNext,'ptnext'),B('↺ Alle enttappen','U',()=>{ptSnap();PT.bf.forEach(c=>c.tapped=false);ptRender()}),
  B('🔀 Mischen','M',ptShuffle),B('Mulligan','London-Mulligan',ptMull,'ptmull'),B('👁 Oberste X','Oberste Karten ansehen (Scry, Surveil, Mahlen)',ptTopX,'pttop'),B('🔎 Suchen','Bibliothek durchsuchen',()=>ptZoneList('lib','Bibliothek'),'ptsearch'),
  B('✨ Token','Token erzeugen',ptTokens,'pttok'),B('🎲','Würfeln (W6/W20) und Münze',()=>{const r6=1+Math.floor(Math.random()*6),r20=1+Math.floor(Math.random()*20);ptLog('Würfel: W6 = '+r6+', W20 = '+r20+', Münze: '+(Math.random()<.5?'Kopf':'Zahl'));ptRender()}),
  B('↶','Rückgängig (Z)',ptUndo,'ptundo'),B('⟲ Neu','Neue Partie',ptNew,'ptnew'),...tableTools(B),B('✕','Schließen (Esc)',ptClose,'ptclose'));
 [...bar.querySelectorAll('button')].forEach(b=>{if(!['ptdraw','ptnext','ptundo','ptclose','ptlm','ptlp','tquer','tsmall','tbig','ttext'].includes(b.id))b.classList.add('ptsec')});
 const more=B('⋯','Weitere Aktionen',e=>ptMenu(e,[...bar.querySelectorAll('button.ptsec')].map(b=>[b.textContent+(b.title&&b.textContent.length<3?' '+b.title:''),()=>b.click()])),'ptmore');more.className='ptmore';bar.insertBefore(more,bar.querySelector('#ptclose'));
 o.append(bar);o.append(rotHint());
 if(PT.mullBottom>0){const n=$('div','Mulligan: Tippe '+PT.mullBottom+' Handkarte'+(PT.mullBottom>1?'n':'')+' an, die unter die Bibliothek sollen.');n.className='ptnote';o.append(n)}
 const main=$('div');main.className='ptmain';
 const side=$('div');side.className='ptside';
 const zb=(z,t,fn)=>{const b=$('button');b.type='button';b.className='ptzone';b.id='ptz-'+z;b.append($('span',t),$('b',String(PT[z].length)));b.onclick=fn;return b};
 const czBox=$('div');czBox.className='ptcz';czBox.append($('div','👑 Kommandozone'));PT.cz.forEach(c=>{const el=ptCardEl(c,'cz');const tax=(PT.casts[c.name]||0)*2;if(tax){const t=$('b','+'+tax);t.className='pttax';t.title='Commander-Steuer';el.append(t)}czBox.append(el)});
 if(!PT.cz.length)czBox.append($('small','–'));
 side.append(czBox,zb('lib','📚 Bibliothek',()=>ptMenu({preventDefault(){},stopPropagation(){},clientX:120,clientY:200},[['🃏 Karte ziehen',ptDrawBtn],['👁 Oberste X ansehen',ptTopX],['🔎 Durchsuchen',()=>ptZoneList('lib','Bibliothek')],['🔀 Mischen',ptShuffle]])),
  zb('gy','🪦 Friedhof',()=>ptZoneList('gy','Friedhof')),zb('ex','🌀 Exil',()=>ptZoneList('ex','Exil')));
 const lg=$('div');lg.className='ptlog';PT.log.slice(0,8).forEach(l=>lg.append($('div',l)));side.append(lg);
 const field=$('div');field.className='ptfield';
 const r1=$('div');r1.className='ptrow';r1.dataset.row='perm';PT.bf.filter(c=>!c.land).forEach(c=>r1.append(ptCardEl(c,'bf')));if(!r1.childElementCount)r1.append($('small','Bleibende Karten (Kreaturen, Artefakte …)'));
 const r2=$('div');r2.className='ptrow lands';r2.dataset.row='lands';PT.bf.filter(c=>c.land).forEach(c=>r2.append(ptCardEl(c,'bf')));if(!r2.childElementCount)r2.append($('small','Länder'));
 field.append(r1,r2);main.append(side,field);o.append(main);
 const hand=$('div');hand.className='pthand';hand.append($('div','✋ Hand ('+PT.hand.length+'): antippen = ausspielen, gedrückt halten / Rechtsklick = weitere Aktionen'));
 const hr=$('div');hr.className='ptrow';PT.hand.forEach(c=>hr.append(ptCardEl(c,'hand')));hand.append(hr);o.append(hand);
 if(keepList)o.append(keepList)}

// ---- Öffentliche Deck-Galerie (Server-Betrieb)
const GAL={ci:new Set()};
function galEur(v){return v==null?'–':(Math.round(v*100)/100).toFixed(2).replace('.',',')+' €'}
function galInit(){const c=E('galci');if(!c||c.childElementCount)return;
 ['W','U','B','R','G','C'].forEach(x=>{const b=$('button');b.type='button';b.dataset.c=x;b.title={W:'Weiß',U:'Blau',B:'Schwarz',R:'Rot',G:'Grün',C:'farblos'}[x];
  b.className='pip p'+x;b.textContent=x=='C'?'◇':x;b.onclick=()=>{GAL.ci.has(x)?GAL.ci.delete(x):GAL.ci.add(x);b.classList.toggle('on',GAL.ci.has(x))};c.append(b)});
 E('galf').onsubmit=e=>{e.preventDefault();galSearch()}}
async function galSearch(){const o=E('galres');o.innerHTML='';P(o,'Suche …','hint');
 const r=await J('/api/gallery',{q:E('galq').value,ci:[...GAL.ci].join(''),cimode:E('galcim').value,maxeur:E('galeur').value,gc:E('galgc').value,bracket:E('galbr').value,sort:E('galsort').value});
 o.innerHTML='';if(r.error){P(o,r.error,'warn');return}
 if(!r.decks.length){P(o,r.total===0&&!E('galq').value&&!GAL.ci.size?'Noch keine Decks veröffentlicht. Veröffentliche eins unter „📂 Meine Decks“ mit „🌍 Veröffentlichen“.':'Keine Decks zu diesen Filtern.','hint');return}
 P(o,r.total+' Deck'+(r.total==1?'':'s')+(r.total>r.decks.length?', angezeigt werden die ersten '+r.decks.length:''),'hint');
 const g=$('div');g.className='galgrid';o.append(g);
 r.decks.forEach(d=>{const c=$('div');c.className='galcard'+(d.hidden?' hid':'');c.dataset.id=d.id;
  const im=$('div');im.className='gimg';if(d.image)im.style.backgroundImage='url("'+d.image+'")';
  const b=$('div');b.className='gb';const n=$('div',d.name);n.className='gn';
  const m=$('div');m.className='gm';m.append(manaEl((d.ci||'C').split('').map(x=>'{'+x+'}').join('')),' ');
  m.append((d.commander||'ohne Commander')+' · von '+d.owner);
  const m2=$('div','♥ '+d.likes+' · 💬 '+d.comments+' · '+galEur(d.eur)+' · '+d.cards+' Karten'+(d.gc?' · '+d.gc+' GC':'')+(d.hidden?' · ausgeblendet':''));m2.className='gm';
  if(d.bracket||d.bracket_est){m2.prepend(brBadge(d.bracket,d.bracket_est),' ')}
  const t=$('div');t.className='gt';(d.themes||[]).forEach(x=>t.append($('span',x)));
  b.append(n,m,m2,t);c.append(im,b);c.onclick=()=>galOpen(d.id);g.append(c)})}
async function galOpen(id){const d=await J('/api/gallery_deck?id='+id);await MEP;
 const b=dlgOpen(d.error?'Galerie':d.name);if(d.error){P(b,d.error,'warn');return}
 const h=$('p');h.append(manaEl((d.ci||'C').split('').map(x=>'{'+x+'}').join('')),' ');
 h.append($('b',d.commander||'ohne Commander'),' ',brBadge(d.bracket,d.bracket_est),' · von '+d.owner+' · veröffentlicht '+(d.pub_at||'')+' · '+d.cards+' Karten · '+galEur(d.eur)+(d.gc?' · '+d.gc+' Game Changer':''));b.append(h);
 if(d.themes&&d.themes.length){const t=$('div');t.className='galtags';d.themes.forEach(x=>t.append($('span',x),' '));b.append(t)}
 const bar=$('div');bar.style.margin='8px 0';
 const lk=$('button',(d.liked?'♥ ':'♡ ')+d.likes);lk.type='button';lk.id='gallike';lk.title='Gefällt mir';
 lk.onclick=async()=>{const r=await J('/api/gallery_like',{id:d.id});if(!r.error){lk.textContent=(r.liked?'♥ ':'♡ ')+r.likes;galSearch()}};
 const cp=$('button','📥 In meine Decks kopieren');cp.type='button';cp.className='primary';cp.id='galcopy';const msg=$('span');
 cp.onclick=async()=>{const r=await J('/api/gallery_copy',{id:d.id});msg.textContent=r.error?' '+r.error:' ✓ als „'+r.name+'“ gespeichert';if(!r.error){cp.disabled=true;myDecks(r.decks)}};
 const op=$('button','⚔ Als Gegner');op.type='button';op.onclick=()=>{closeSwap();useOpp({name:d.name,commander:d.commander,list:d.list})};
 bar.append(lk,' ',cp,' ',op);
 if(ME.admin){const hd=$('button',d.hidden?'👁 Wieder einblenden':'🚫 Ausblenden');hd.type='button';hd.id='galhide';
  hd.onclick=async()=>{const r=await J('/api/gallery_hide',{id:d.id,on:d.hidden?0:1});if(!r.error){d.hidden=r.hidden;hd.textContent=d.hidden?'👁 Wieder einblenden':'🚫 Ausblenden';galSearch()}};bar.append(' ',hd)}
 bar.append(msg);b.append(bar);
 if(d.notes){b.append($('h4','Notizen / Primer'));const nt=$('div');nt.style.whiteSpace='pre-wrap';nt.textContent=d.notes;b.append(nt)}
 b.append($('h4','Deckliste'));const ul=$('div');ul.className='gallist';
 (d.list||'').split('\\n').filter(x=>x.trim()).forEach(x=>ul.append($('div',x)));b.append(ul);
 if(d.maybe&&d.maybe.length){b.append($('h4','Maybeboard'));const mb=$('div');mb.className='gallist';d.maybe.forEach(x=>mb.append($('div',x)));b.append(mb)}
 b.append($('h4','Kommentare ('+d.comments.length+')'));const cl=$('div');cl.id='galcoms';b.append(cl);
 d.comments.forEach(c=>{const r=$('div');r.className='galcom';r.append($('b',c.user),$('small',c.at+' '));const tx=$('div',c.text);tx.style.whiteSpace='pre-wrap';r.append(tx);
  if(c.can_delete){const x=$('button','löschen');x.type='button';x.className='mini';x.onclick=async()=>{await J('/api/gallery_comment_delete',{cid:c.id});galOpen(d.id)};r.append(x)}cl.append(r)});
 if(!d.hidden){const ta=$('textarea');ta.id='galctext';ta.rows=2;ta.maxLength=500;ta.style.width='100%';ta.placeholder='Kommentar schreiben (höchstens 500 Zeichen)';
  const sb=$('button','💬 Kommentieren');sb.type='button';sb.id='galcsend';const em=$('span');
  sb.onclick=async()=>{const r=await J('/api/gallery_comment',{id:d.id,text:ta.value});if(r.error)em.textContent=' '+r.error;else{galOpen(d.id);galSearch()}};b.append(ta,sb,em)}}
MEP.then(m=>{document.querySelectorAll('.srvonly').forEach(x=>x.hidden=!m.server);
 if(!m.server){const a=document.querySelector('#mobmore a[data-v=galerie]');if(a)a.hidden=true}});

// ---- Sammlung: Einkaufsliste, Wunschliste, Ordner, Wertverlauf; Preisalarm; Budget-Tausch
const fe=v=>v==null?'–':Number(v).toFixed(2).replace('.',',')+' €';
const fu=v=>v==null?'':Number(v).toFixed(2).replace('.',',')+' $';
async function shopCalc(){const o=E('shopres');o.innerHTML='';P(o,'rechne …','hint');const r=await J('/api/shopping',{share:E('shopshare').checked?1:0});o.innerHTML='';
 if(r.error){P(o,r.error,'warn');return}
 if(!r.decks){P(o,'Noch keine Decks gespeichert.','hint');return}
 if(!r.has_collection)P(o,'Noch keine Sammlung importiert, deshalb fehlen alle Karten.','hint');
 E('shopsum').textContent='('+r.cards+' Karten, ca. '+fe(r.total)+')';
 P(o,r.items.length?r.cards+' fehlende Karten ('+r.items.length+' verschiedene) für '+r.decks+' Decks · zusammen ca. '+fe(r.total)+(r.noprice?' · '+r.noprice+' ohne Preis':''):'Dir fehlt keine Karte, alle Decks sind komplett.','big');
 if(CMAT&&r.items.length)P(o,'Preise: Cardmarket (Preisliste vom '+CMAT+', günstigste Druckversion). 🛒 öffnet die Karte auf Cardmarket.','hint');
 if(!r.items.length)return;
 const bar=$('p');const cp=$('button','📋 Liste kopieren');cp.type='button';cp.id='shopcopy';cp.onclick=async()=>{await copyText(r.text);cp.textContent='✓ kopiert'};
 const cmb=$('button','🛒 Bei Cardmarket kaufen');cmb.type='button';cmb.className='primary';cmb.id='shopcm';cmb.title='Liste kopieren und die Cardmarket-Wants öffnen';cmb.onclick=()=>cmWants(r.text,cmb);
 const wl=$('button','⭐ Alle auf die Wunschliste');wl.type='button';wl.id='shopwish';wl.onclick=async()=>{const x=await J('/api/wish_add',{text:r.text});wl.textContent='✓ '+x.added+' Karten auf der Wunschliste';wishShow(x)};
 bar.append(cmb,' ',cp,' ',wl);o.append(bar);o.append(shopSettings());
 const t=$('table');t.className='ftable';t.id='shoptable';o.append(t);const hr=t.insertRow();['Karte','fehlt','hast','Preis','zusammen','in Decks'].forEach((x,i)=>{const th=$('th',x);if(i>0&&i<5)th.className='r';hr.append(th)});
 r.items.slice(0,300).forEach(x=>{const tr=t.insertRow();const c0=tr.insertCell();c0.append(cardName(x.name),' ',cmA(x.cm,x.name));if(x.wish)c0.append(' ⭐');
  [x.missing,x.have,fe(x.eur),fe(x.total)].forEach(v=>{const c=tr.insertCell();c.className='r';c.textContent=v});tr.insertCell().textContent=x.decks.join(', ')});
 if(r.items.length>300)P(o,'… und '+(r.items.length-300)+' weitere (vollständig in der kopierten Liste).','hint')}
function wishShow(r){const o=E('wishres');o.innerHTML='';if(r.error){P(o,r.error,'warn');return}
 E('wishsum').textContent=r.items.length?'('+r.items.length+' Karten, ca. '+fe(r.total)+(r.hits?', '+r.hits+' unter Zielpreis':'')+')':'';
 if(r.unknown&&r.unknown.length)P(o,'Nicht gefunden: '+r.unknown.join(', '),'warn');
 if(!r.items.length){P(o,'Die Wunschliste ist leer.','hint');return}
 const wb=$('p');const wcm=$('button','🛒 Wunschliste bei Cardmarket kaufen');wcm.type='button';wcm.id='wishcm';wcm.onclick=()=>cmWants(r.items.map(x=>x.qty+' '+x.name).join('\\n'),wcm);wb.append(wcm);o.append(wb);
 const t=$('table');t.className='ftable';t.id='wishtable';o.append(t);const hr=t.insertRow();['Karte','Anzahl','Preis','Dollar','Zielpreis','',''].forEach((x,i)=>{const th=$('th',x);if(i>0&&i<5)th.className='r';hr.append(th)});
 r.items.forEach(x=>{const tr=t.insertRow();tr.dataset.name=x.name;const c0=tr.insertCell();c0.append(cardName(x.name),' ',cmA(x.cm,x.name));if(x.have)c0.append($('span',' (hast '+x.have+')'));
  const cq=tr.insertCell();cq.className='r';cq.textContent=x.qty;
  const ce=tr.insertCell();ce.className='r'+(x.hit?' hit':'');ce.textContent=fe(x.eur);
  const cu=tr.insertCell();cu.className='r';cu.textContent=fu(x.usd);
  const ct=tr.insertCell();ct.className='r';const ti=$('input');ti.size=5;ti.className='wtarget';ti.inputMode='decimal';ti.value=x.target!=null?String(x.target).replace('.',','):'';ti.placeholder='–';
  ti.onchange=async()=>wishShow(await J('/api/wish_set',{name:x.name,target:ti.value}));ct.append(ti,' €');
  tr.insertCell().textContent=x.hit?'🔔 unter Zielpreis':'';
  const cx=tr.insertCell();const rm=$('button','✕');rm.type='button';rm.className='mini';rm.title='von der Wunschliste nehmen';rm.onclick=async()=>wishShow(await J('/api/wish_set',{name:x.name,remove:1}));cx.append(rm)})}
async function folderOverview(sel){const r=await J('/api/folders');const o=E('folderlist');o.innerHTML='';
 E('foldersum').textContent=r.folders.length?'('+r.folders.length+')':'';
 if(!r.folders.length){P(o,'Noch keine Ordner.','hint');return}
 const ch=$('div');ch.className='chips2';r.folders.forEach(f=>{const b=$('button',f.name+' · '+f.cards+' Karten · '+fe(f.value));b.type='button';b.dataset.f=f.name;
  b.onclick=()=>{E('foldername').value=f.name;folderShow(f.name)};ch.append(b)});o.append(ch);if(sel)folderShow(sel)}
async function folderShow(name,r){r=r||await J('/api/folder',{folder:name});const o=E('folderres');o.innerHTML='';
 if(r.error){P(o,r.error,'warn');return}
 const msg=[];if(r.capped&&r.capped.length)msg.push('Auf den Bestand begrenzt: '+r.capped.join(', '));if(r.notown&&r.notown.length)msg.push('Nicht in deiner Sammlung: '+r.notown.join(', '));if(r.unknown&&r.unknown.length)msg.push('Unbekannt: '+r.unknown.join(', '));
 msg.forEach(m=>P(o,m,'warn'));
 o.append($('h4','📁 '+r.folder+': '+r.items.reduce((a,x)=>a+x.qty,0)+' Karten, ca. '+fe(r.value)));
 if(!r.items.length){P(o,'Der Ordner ist leer.','hint');return}
 const t=$('table');t.className='ftable';t.id='foldertable';o.append(t);r.items.forEach(x=>{const tr=t.insertRow();const c=tr.insertCell();c.className='r';c.textContent=x.qty+'×';tr.insertCell().append(cardName(x.name));const p=tr.insertCell();p.className='r';p.textContent=fe(x.eur)});
 const bar=$('p');const cp=$('button','📋 Ordner kopieren');cp.type='button';cp.onclick=async()=>{await copyText(r.text);cp.textContent='✓ kopiert'};
 const del=$('button','Ordner auflösen');del.type='button';del.id='folderdel';del.onclick=async()=>{if(del.textContent!='Wirklich?'){del.textContent='Wirklich?';return}await J('/api/folder_delete',{folder:r.folder});o.innerHTML='';folderOverview()};
 bar.append(cp,' ',del,$('span',' (die Karten bleiben in der Sammlung)'));o.append(bar)}
async function folderPut(mode){const r=await J('/api/folder_put',{folder:E('foldername').value,text:E('foldertext').value,mode:mode});
 if(!r.error)E('foldertext').value='';await folderOverview();folderShow(r.folder,r)}
async function collHistory(){const o=E('chistres');o.innerHTML='';const r=await J('/api/collection_history');
 if(!r.series.length){P(o,r.hint,'hint');return}
 const s=r.series,a=s[0],z=s[s.length-1];
 if(s.length>1){const ns='http://www.w3.org/2000/svg',W=520,H=110,max=Math.max(...s.map(x=>x.value)),min=Math.min(...s.map(x=>x.value)),svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox','0 0 '+W+' '+H);svg.setAttribute('width','100%');svg.style.maxWidth=W+'px';svg.id='chistsvg';
  const xp=i=>10+i*(W-20)/(s.length-1),yp=v=>max==min?H/2:H-12-(v-min)*(H-24)/(max-min);
  const pl=document.createElementNS(ns,'polyline');pl.setAttribute('points',s.map((x,i)=>xp(i)+','+yp(x.value)).join(' '));pl.setAttribute('fill','none');pl.setAttribute('stroke','currentColor');pl.setAttribute('stroke-width','2');svg.append(pl);
  s.forEach((x,i)=>{const c=document.createElementNS(ns,'circle');c.setAttribute('cx',xp(i));c.setAttribute('cy',yp(x.value));c.setAttribute('r',3);c.setAttribute('fill','currentColor');const t=document.createElementNS(ns,'title');t.textContent=x.day+': '+fe(x.value);c.append(t);svg.append(c)});o.append(svg)}
 P(o,'Sammlungswert '+a.day+': '+fe(a.value)+(s.length>1?' → '+z.day+': '+fe(z.value)+' ('+(z.value>=a.value?'+':'')+fe(z.value-a.value)+')':'')+(r.usd?' · in Dollar (TCGplayer): '+fu(r.usd):''),'big');
 P(o,r.hint,'hint')}
async function priceAlerts(){const o=E('palert');if(!o)return;const r=await J('/api/price_alerts');if(r.error)return;o.innerHTML='';
 if(!r.wish_hits.length&&!r.moves.length){o.hidden=true;return}o.hidden=false;
 o.append($('b','🔔 Preisalarm'));
 if(r.wish_hits.length){const d=$('div');d.id='palwish';d.append('Wunschliste unter Zielpreis: ');r.wish_hits.forEach((x,i)=>{if(i)d.append(', ');d.append(cardName(x.name),' '+fe(x.eur)+' (Ziel '+fe(x.target)+')')});o.append(d)}
 if(r.moves.length){const d=$('div');d.id='palmove';d.append('Starke Bewegung in deiner Sammlung seit '+r.since+': ');
  r.moves.slice(0,8).forEach((x,i)=>{if(i)d.append(', ');const sp=$('span',(x.diff>0?'▲ ':'▼ ')+fe(x.from)+' → '+fe(x.to)+' ('+(x.pct>0?'+':'')+x.pct+' %)');sp.className=x.diff>0?'up':'down';d.append(cardName(x.name),' ',sp)});o.append(d)}
 if(r.cm_at){const s2=$('div','Preise: Cardmarket (Preisliste vom '+r.cm_at+'); ohne eigenen Verlauf zählt der Trend gegenüber dem 30-Tage-Durchschnitt.');s2.className='hint';o.append(s2)}
 const go=$('a','→ zur Wunschliste');go.href='#sammlung';go.onclick=()=>setTimeout(()=>{E('wishbox').open=true;E('wishbox').scrollIntoView()},300);o.append(' ',go)}
async function budgetBox(o){const h=$('h4','💸 Budget-Tausch');o.append(h);
 const lim=$('input');lim.id='budmin';lim.size=4;lim.value='5';lim.inputMode='decimal';const b=$('button','Günstigere Alternativen suchen');b.type='button';b.id='budgo';
 const l=$('label');l.append('für Karten ab ',lim,' € ');const res=$('div');res.id='budres';o.append(l,b,res);
 b.onclick=async()=>{res.innerHTML='';P(res,'suche …','hint');const r=await J('/api/budget_swaps',{list:deck.export,commander:deck.commander||'',ci:deck.ci||'',min:lim.value});res.innerHTML='';
  if(r.error){P(res,r.error,'warn');return}
  if(!r.items.length){P(res,'Keine Karte ab '+fe(r.min)+' (ohne Commander und eigene Karten).','hint');return}
  P(res,'Mögliche Ersparnis mit der jeweils günstigsten Alternative: ca. '+fe(r.saving),'big');
  r.items.forEach(x=>{const d=$('div');d.className='budrow';d.dataset.name=x.name;d.append($('b',x.name),' '+fe(x.eur)+' → ');
   if(!x.alts.length)d.append($('span','keine günstige Alternative mit gleicher Aufgabe'));
   x.alts.forEach(a=>{const bt=$('button',a.name+' ('+fe(a.eur)+')');bt.type='button';bt.className='mini budswap';bt.title='„'+x.name+'“ durch „'+a.name+'“ ersetzen';
    bt.onclick=()=>{for(const g of deck.groups){const ci=g.cards.findIndex(c=>c.name==x.name);if(ci>=0){markOut(x.name);g.cards[ci]=Object.assign({},a,{qty:g.cards[ci].qty,swapped:true});recalc();return}}};d.append(bt,' ')});
   const w=$('div',x.reason);w.className='hint';d.append(w);res.append(d)});P(res,r.hint,'hint')}}
E('shopgo').onclick=shopCalc;
E('pxopen').onclick=()=>proxyStudio({});
E('buybox').addEventListener('toggle',()=>{if(E('buybox').open&&!E('buyctl').firstChild)buyInit()});

E('wishgo').onclick=async()=>{const r=await J('/api/wish_add',{text:(E('wishqty').value||'1')+' '+E('wishname').value,target:E('wishtarget').value});if(!r.error){E('wishname').value='';E('wishtarget').value=''}wishShow(r)};
E('folderadd').onclick=()=>folderPut('add');E('folderrem').onclick=()=>folderPut('remove');
E('wishbox').addEventListener('toggle',()=>{if(E('wishbox').open)J('/api/wishlist').then(wishShow)});
E('folderbox').addEventListener('toggle',()=>{if(E('folderbox').open)folderOverview()});
E('chistbox').addEventListener('toggle',()=>{if(E('chistbox').open)collHistory()});
J('/api/wishlist').then(r=>{if(r.items&&r.items.length)E('wishsum').textContent='('+r.items.length+' Karten'+(r.hits?', '+r.hits+' unter Zielpreis':'')+')'});
priceAlerts();

// ---- Deck-Editor: eigene Gruppen, Ziehen/Ablegen, Rückgängig, Mehrfachauswahl, Stapelansicht
const DH={stack:[],pos:-1,deck:null,skip:false},DSEL={on:false,names:new Set()};
function deckSnapshot(){return JSON.stringify({g:deck.groups,m:deck.maybe||[],p:deck.primer||''})}
function deckRecord(){if(DH.deck!==deck){DH.deck=deck;DH.stack=[];DH.pos=-1;DSEL.names.clear()}
 if(DH.skip){DH.skip=false;return}const s=deckSnapshot();if(DH.stack[DH.pos]===s)return;
 DH.stack=DH.stack.slice(0,DH.pos+1);DH.stack.push(s);if(DH.stack.length>60)DH.stack.shift();DH.pos=DH.stack.length-1;
 const u=E('dundo'),r=E('dredo');if(u)u.disabled=DH.pos<=0;if(r)r.disabled=true}
function deckRestore(i){const x=JSON.parse(DH.stack[i]);DH.pos=i;deck.groups=x.g;deck.maybe=x.m;deck.primer=x.p;DH.skip=true;deck.msg=i<DH.stack.length-1?'Rückgängig gemacht.':'Wiederhergestellt.';recalc()}
function deckUndo(){if(DH.pos>0)deckRestore(DH.pos-1)}
function deckRedo(){if(DH.pos<DH.stack.length-1)deckRestore(DH.pos+1)}
document.addEventListener('keydown',e=>{if(!(e.ctrlKey||e.metaKey)||E('pt')||!deck||deck.error||document.body.dataset.page!='deck')return;
 const t=e.target;if(t&&(t.tagName=='INPUT'||t.tagName=='TEXTAREA'||t.isContentEditable))return;
 const k=e.key.toLowerCase();if(k=='z'&&!e.shiftKey){e.preventDefault();deckUndo()}else if(k=='y'||(k=='z'&&e.shiftKey)){e.preventDefault();deckRedo()}});
function findCard(n){for(let gi=0;gi<deck.groups.length;gi++){const ci=deck.groups[gi].cards.findIndex(c=>c.name==n);if(ci>=0)return [gi,ci]}return null}
function moveToGroup(n,gname,quiet){gname=(gname||'').replace(/\\s+/g,' ').trim().slice(0,40);if(!gname||gname=='Commander')return;
 const f=findCard(n);if(!f)return;const [gi,ci]=f;const src=deck.groups[gi];if(src.name=='Commander'||src.name==gname)return;
 const c=src.cards.splice(ci,1)[0];let g=deck.groups.find(x=>x.name==gname);
 if(!g){g={name:gname,cards:[],custom:true};const li=deck.groups.findIndex(x=>x.name=='Länder');if(li<0)deck.groups.push(g);else deck.groups.splice(li,0,g)}
 c.grp=gname;g.cards.push(c);if(!src.cards.length)deck.groups.splice(deck.groups.indexOf(src),1);
 if(!quiet){deck.msg='„'+n+'“ → '+gname+'.';recalc()}}
function moveMany(names,gname){names.forEach(n=>moveToGroup(n,gname,true));DSEL.names.clear();deck.msg=names.length+' Karte(n) → '+gname+'.';recalc()}
function dragSrc(el,name){el.draggable=true;el.classList.add('dragc');el.addEventListener('dragstart',e=>{e.dataTransfer.setData('text/x-card',name);e.dataTransfer.effectAllowed='move';el.classList.add('dragging');dropDock(name)});
 el.addEventListener('dragend',()=>{el.classList.remove('dragging');setTimeout(()=>{const d=E('dropdock');if(d)d.remove()},50)})}
// Ablageleiste unten am Bildschirm, solange eine Karte gezogen wird – erreichbar, egal wie lang das Deck ist
function dropDock(name){let d=E('dropdock');if(d)d.remove();d=$('div');d.id='dropdock';d.append($('span','Ablegen in: '));
 const f=findCard(name),cur=f?deck.groups[f[0]].name:'';
 groupNames().filter(n=>n!=cur).forEach(n=>{const z=$('span',n);z.className='dz';z.dataset.g=n;dropZone(z,x=>moveToGroup(x,n));d.append(z)});
 if(deck.pendingGroup&&!groupNames().includes(deck.pendingGroup)){const z=$('span','➕ '+deck.pendingGroup);z.className='dz';z.dataset.g=deck.pendingGroup;dropZone(z,x=>{const g=deck.pendingGroup;deck.pendingGroup='';moveToGroup(x,g)});d.append(z)}
 const mz=$('span','↓ Maybeboard');mz.className='dz dzm';mz.dataset.g='__maybe';dropZone(mz,x=>{const ff=findCard(x);if(ff)toMaybe(ff[0],ff[1])});
 const rz=$('span','✕ Entfernen');rz.className='dz dzr';rz.dataset.g='__remove';dropZone(rz,x=>{const ff=findCard(x);if(ff){const g=deck.groups[ff[0]];g.cards.splice(ff[1],1);if(!g.cards.length)deck.groups.splice(ff[0],1);deck.msg='„'+x+'“ entfernt.';recalc()}});
 d.append(mz,rz);document.body.append(d)}
function dropZone(el,fn){el.addEventListener('dragover',e=>{if([...e.dataTransfer.types].includes('text/x-card')){e.preventDefault();el.classList.add('dropover')}});
 el.addEventListener('dragleave',e=>{if(!el.contains(e.relatedTarget))el.classList.remove('dropover')});
 el.addEventListener('drop',e=>{const n=e.dataTransfer.getData('text/x-card');el.classList.remove('dropover');if(n){e.preventDefault();e.stopPropagation();fn(n)}})}
function groupNames(){return deck.groups.map(g=>g.name).filter(n=>n!='Commander')}
function moveDialog(names){const b=dlgOpen(names.length==1?'„'+names[0]+'“ verschieben':names.length?names.length+' Karten verschieben':'Neue Gruppe');
 if(names.length){P(b,'In welche Gruppe?','hint');const ch=$('div');ch.className='chips2';[...new Set([...(deck.pendingGroup?[deck.pendingGroup]:[]),...groupNames()])].forEach(n=>{const x=$('button',n);x.type='button';x.dataset.g=n;
  x.onclick=()=>{closeSwap();names.length==1?moveToGroup(names[0],n):moveMany(names,n)};ch.append(x)});
  const mb=$('button','↓ Maybeboard');mb.type='button';mb.id='mvmaybe';mb.onclick=()=>{closeSwap();names.forEach(n=>{const f=findCard(n);if(f)toMaybe(f[0],f[1])})};ch.append(mb);b.append(ch)}
 const inp=$('input');inp.id='mvnew';inp.size=26;inp.maxLength=40;inp.placeholder='Name der neuen Gruppe, z. B. „Goblin-Erzeuger“';
 const ok=$('button',names.length?'In neue Gruppe':'Gruppe anlegen');ok.type='button';ok.className='primary';ok.id='mvok';
 const hint=P(b,names.length?'… oder eine neue Gruppe:':'Eine Gruppe entsteht, sobald eine Karte darin liegt. Name eingeben, dann Karten mit ⇄, Mehrfachauswahl oder per Ziehen hineinlegen.','hint');
 ok.onclick=()=>{const n=inp.value.trim();if(!n)return;closeSwap();if(names.length)moveMany(names,n);else{deck.pendingGroup=n;deck.msg='Gruppe „'+n+'“: jetzt Karten hineinlegen (⇄ oder Mehrfachauswahl).';showDeck()}};
 inp.onkeydown=e=>{if(e.key=='Enter')ok.click()};b.append(inp,' ',ok);setTimeout(()=>inp.focus(),50)}
function selBar(){const sb=E('selbar');if(!sb)return;sb.innerHTML='';const ns=[...DSEL.names];
 sb.append($('b',ns.length+' ausgewählt '));
 const all=$('button','alle');all.type='button';all.onclick=()=>{deck.groups.filter(g=>g.name!='Commander').forEach(g=>g.cards.forEach(c=>DSEL.names.add(c.name)));showDeck()};
 const none=$('button','keine');none.type='button';none.onclick=()=>{DSEL.names.clear();showDeck()};sb.append(all,' ',none,' ');
 if(!ns.length)return;
 const mv=$('button','⇄ Verschieben');mv.type='button';mv.id='selmove';mv.onclick=()=>moveDialog(ns);
 if(deck.pendingGroup){const pg=$('button','→ '+deck.pendingGroup);pg.type='button';pg.id='selpending';pg.onclick=()=>{const g=deck.pendingGroup;deck.pendingGroup='';DSEL.names.clear();moveMany(ns,g)};sb.append(pg,' ')}
 const tg=$('input');tg.id='seltag';tg.size=12;tg.placeholder='Tag';const ta=$('button','🏷 Tag setzen');ta.type='button';ta.id='seltagok';
 ta.onclick=()=>{const t=tg.value.trim();if(!t)return;deck.groups.forEach(g=>g.cards.forEach(c=>{if(DSEL.names.has(c.name)){c.tags=[...new Set([...(c.tags||[]),t])].slice(0,8)}}));deck.msg='Tag „'+t+'“ für '+ns.length+' Karten.';DSEL.names.clear();showDeck()};
 const my=$('button','↓ Maybeboard');my.type='button';my.id='selmaybe';my.onclick=()=>{ns.forEach(n=>{const f=findCard(n);if(f)toMaybe(f[0],f[1])});DSEL.names.clear();recalc()};
 const rm=$('button','✕ Entfernen');rm.type='button';rm.id='selremove';rm.onclick=()=>{if(rm.textContent!='Wirklich?'){rm.textContent='Wirklich?';return}
  ns.forEach(n=>{const f=findCard(n);if(f){const g=deck.groups[f[0]];g.cards.splice(f[1],1);if(!g.cards.length)deck.groups.splice(f[0],1)}});DSEL.names.clear();deck.msg=ns.length+' Karten entfernt.';recalc()};
 sb.append(mv,' ',tg,ta,' ',my,' ',rm)}
function stackOut(o,groups,edit){const cols={};let lands=[];
 groups.forEach(g=>g.cards.forEach(c=>{if(g.name=='Commander')(cols.C=cols.C||[]).push(c);else if(c.land)lands.push(c);else{const k=Math.min(Math.floor(c.cmc||0),7);(cols[k]=cols[k]||[]).push(c)}}));
 const wrap=$('div');wrap.className='stacks';wrap.id='stackview';o.append(wrap);
 const col=(title,cards)=>{if(!cards.length)return;const d=$('div');d.className='stackcol';d.append($('div',title+' ('+cards.reduce((s,c)=>s+c.qty,0)+')'));d.firstChild.className='sth';
  cards.sort((a,b)=>a.name.localeCompare(b.name)).forEach(c=>{const a=$('div');a.className='stc';a.dataset.name=c.name;a.title=c.name+(c.eur!=null?' · '+c.eur.toFixed(2)+' €':'');
   if(c.image){const im=$('img');im.src=c.image;im.loading='lazy';im.alt=c.name;im.onerror=()=>{im.remove();a.classList.add('noimg');a.prepend($('span',c.name))};a.append(im)}else{a.classList.add('noimg');a.append($('span',c.name))}
   if(c.qty>1){const q=$('span','×'+c.qty);q.className='q';a.append(q)}
   a.onclick=()=>{const f=findCard(c.name);if(f&&edit&&!c.basic&&deck.groups[f[0]].name!='Commander')openSwap(f[0],f[1])};if(edit&&!c.basic)dragSrc(a,c.name);d.append(a)});wrap.append(d)};
 col('Commander',cols.C||[]);for(let k=0;k<=7;k++)col(k==7?'7+':String(k),cols[k]||[]);col('Länder',lands);
 P(o,'Stapel nach Manawert. Karte antippen = Ersatz suchen; ins Maybeboard ziehen = verschieben. Gruppen und Tags siehst du in der Listenansicht.','hint')}

// ---- Bracket-Einstufung
const BRN={'1':'Exhibition','2':'Core','3':'Upgraded','4':'Optimized','5':'cEDH'};
function brBadge(tgt,est){const s=$('span');s.className='brb'+(tgt?' brt':'');
 if(tgt){s.textContent='B'+tgt;s.title='Bracket '+tgt+' ('+BRN[tgt]+'), vom Besitzer angegeben'+(est?'; Schätzung des Programms: '+est:'')}
 else if(est){s.textContent='≈B'+est;s.title='Bracket-Schätzung des Programms (ohne Combo-Prüfung): '+est}else s.textContent='–';
 if(tgt&&est){const lo=parseInt(est);if(lo>parseInt(tgt)){s.classList.add('brwarn');s.textContent+=' ⚠';s.title+='. Das Deck enthält Karten über diesem Bracket'}}
 return s}
let BRT=null;
async function bracketBox(o,combos){o.id='brbox';o.innerHTML='';const ex=deck.export;
 // Combos automatisch mitprüfen: einmal je Deckstand, kurz verzögert (bei schnellem Bearbeiten nur der letzte Stand)
 const same=deck.brCombos&&deck.brCombos.list==ex;
 if(!combos&&same&&!deck.brCombos.err)combos='cached';
 else if(!combos&&!same&&!deck.error){clearTimeout(BRT);BRT=setTimeout(()=>{const b=E('brbox');if(b&&deck.export==ex)bracketBox(b,true)},deck.brCombos?4000:800)}const hh=$('h4','🎚 Bracket-Einstufung');hh.append(qBtn('brackets'));o.append(hh);
 const res=$('div');o.append(res);P(res,combos?'prüfe Combos bei Commander Spellbook …':'prüfe …','hint');
 const r=await J('/api/bracket',{list:ex,commander:deck.commander||'',combos:combos?1:0});
 if(deck.export!=ex)return;res.innerHTML='';
 if(r.error){P(res,r.error,'warn');return}
 if(combos)deck.brCombos={list:ex,err:!!r.combo_error};
 const big=$('div');big.className='brbig';big.id='brresult';big.append($('b','Bracket '+r.bracket),' '+r.name);res.append(big);
 P(res,r.note,'hint');
 const t=$('table');t.className='ftable brtab';t.id='brrules';res.append(t);const hr=t.insertRow();['Regel','gefunden','erlaubt ab Bracket','Karten'].forEach(x=>hr.append($('th',x)));
 r.rules.forEach(x=>{const tr=t.insertRow();tr.dataset.k=x.key;const c0=tr.insertCell();c0.append($('b',x.label));const sm=$('div',x.rule);sm.className='hint';c0.append(sm);
  const c1=tr.insertCell();c1.textContent=x.key=='combo'&&!x.checked?'nicht geprüft':(x.count?String(x.count):'keine');c1.className=x.key=='combo'&&!x.checked?'':(x.min>2?'no':(x.count?'':'ok'));
  tr.insertCell().textContent=x.key=='combo'&&!x.checked?'–':x.ok_up_to;
  const c3=tr.insertCell();x.cards.forEach((n,i)=>{if(i)c3.append(', ');c3.append(x.key=='combo'?n:cardName(n))})});
 if(r.illegal&&r.illegal.length)P(res,'Nicht Commander-legal (gebannt): '+r.illegal.join(', '),'warn');
 if(r.combo_error)P(res,r.combo_error,'warn');
 const sb=r.spellbook;if(sb&&sb.name)P(res,'Zum Vergleich: Commander Spellbook stuft das Deck als „'+sb.name+'“ ein.','hint');
 // Ziel-Bracket des Besitzers
 const row=$('div');row.className='brtarget';const sel=$('select');sel.id='brtarget';
 [['','noch nicht festgelegt'],['1','1 Exhibition'],['2','2 Core'],['3','3 Upgraded'],['4','4 Optimized'],['5','5 cEDH']].forEach(([v,l])=>{const op=$('option',l);op.value=v;sel.append(op)});
 sel.value=deck.bracketTarget||'';const msg=$('span');msg.id='brmsg';
 const cmp=()=>{const tv=sel.value;msg.className='';if(!tv){msg.textContent=' Lege fest, in welchem Bracket du das Deck spielen willst. Das Ziel wird mit dem Deck gespeichert und in Galerie und Teilen-Seite gezeigt.';return}
  if(r.value>parseInt(tv)&&!(r.bracket=='1–2'&&tv=='1')){msg.className='warn';msg.textContent=' ⚠ Das Deck enthält Karten über Bracket '+tv+': '+r.rules.filter(x=>x.min>parseInt(tv)).map(x=>x.label+' ('+x.cards.slice(0,4).join(', ')+(x.cards.length>4?', …':'')+')').join('; ')+'.'}
  else if(parseInt(tv)>=4&&r.value<4){msg.className='hint';msg.textContent=' Keine Regel verbietet das. Ob das Deck wirklich so schnell und beständig ist, zeigen Testspiel, Statistik und Forge-Duelle.'}
  else{msg.className='ok';msg.textContent=' ✓ passt zu den prüfbaren Regeln'+(r.combos_checked?'':' (Combos noch ungeprüft)')+'.'}};
 sel.onchange=()=>{deck.bracketTarget=sel.value;cmp();deck.msg='Ziel-Bracket gesetzt, mit „Speichern“ übernehmen.'};
 row.append($('b','Mein Ziel-Bracket: '),sel,msg);res.append(row);cmp();
 if(!r.combos_checked){const bc=$('button',r.combo_error?'🔗 Combos erneut prüfen':'🔗 Combos jetzt prüfen');bc.type='button';bc.id='brcombos';bc.onclick=()=>{clearTimeout(BRT);bracketBox(o,true)};res.append(bc)}
 else{const sm=$('div','Combos geprüft mit Commander Spellbook'+(r.rules[3].count?'':', keine spielentscheidende Zwei-Karten-Combo gefunden')+'.');sm.className='hint';sm.id='brcombook';res.append(sm)}}

// ---- Precon-Übersicht
const PC={ci:new Set(),data:null};
async function pcInit(){const c=E('pcci');if(c.childElementCount)return pcRender();
 ['W','U','B','R','G','C'].forEach(x=>{const b=$('button');b.type='button';b.dataset.c=x;b.className='pip p'+x;b.textContent=x=='C'?'◇':x;b.title={W:'Weiß',U:'Blau',B:'Schwarz',R:'Rot',G:'Grün',C:'farblos'}[x]+' (höchstens diese Farben)';
  b.onclick=()=>{PC.ci.has(x)?PC.ci.delete(x):PC.ci.add(x);b.classList.toggle('on',PC.ci.has(x));pcRender()};c.append(b)});
 E('pcf').onsubmit=e=>{e.preventDefault()};['pcq','pcset','pcsort'].forEach(i=>E(i).addEventListener(i=='pcq'?'input':'change',pcRender));
 const o=E('pcres');P(o,'lade Precons …','hint');const r=await J('/api/precon_catalog');PC.data=r;
 if(!r.loaded){o.innerHTML='';P(o,'Die Precon-Decklisten sind noch nicht geladen (einmalig ca. 30 MB von GitHub).','hint');
  const b=$('button','Precon-Decklisten jetzt laden');b.type='button';b.className='primary';b.id='pcload';b.onclick=async()=>{b.disabled=true;b.textContent='Lade …';const x=await J('/api/load_precons',{});if(x.error){b.textContent=x.error;return}E('pcci').innerHTML='';pcInit()};o.append(b);return}
 const sets=[...new Set(r.precons.map(p=>p.set))];sets.forEach(x=>{const op=$('option',x);op.value=x;E('pcset').append(op)});
 if(r.has_collection&&!E('pcsort').dataset.d){E('pcsort').dataset.d=1}
 pcRender()}
function pcRender(){const o=E('pcres');const r=PC.data;if(!r||!r.loaded)return;o.innerHTML='';
 const q=E('pcq').value.trim().toLowerCase(),st=E('pcset').value,so=E('pcsort').value;
 let l=r.precons.filter(p=>(!q||(p.name+' '+p.commander+' '+p.set).toLowerCase().includes(q))&&(!st||p.set==st)
  &&(!PC.ci.size||[...p.ci.replace('C','')].every(c=>PC.ci.has(c))&&(p.ci!='C'||PC.ci.has('C'))));
 const srt={old:(a,b)=>a.date.localeCompare(b.date),eur:(a,b)=>a.eur-b.eur,eurd:(a,b)=>b.eur-a.eur,own:(a,b)=>(b.owned||0)-(a.owned||0)}[so];if(srt)l=[...l].sort(srt);
 P(o,l.length+' von '+r.precons.length+' Precons'+(r.at?' · Stand der Decklisten: '+r.at:''),'hint');
 if(!l.length)return;
 const t=$('table');t.className='ftable pctab';t.id='pctable';o.append(t);
 const hr=t.insertRow();['','Deck','Commander','Set','Wert','Bracket'].concat(r.has_collection?['hast']:[]).forEach((x,i)=>{const th=$('th',x);if(i==4||i==6)th.className='r';hr.append(th)});
 let last=null;
 l.forEach(p=>{if(so=='new'||so=='old'){if(p.set!=last){last=p.set;const sr=t.insertRow();sr.className='pcset';const c=sr.insertCell();c.colSpan=r.has_collection?7:6;c.append($('b',p.set),$('span',' · '+p.date))}}
  const tr=t.insertRow();tr.dataset.id=p.id;tr.className='pcrow';tr.onclick=()=>pcOpen(p.id);
  tr.insertCell().append(manaEl((p.ci||'C').split('').map(x=>'{'+x+'}').join('')));
  const cn=tr.insertCell();cn.append($('b',p.name));tr.insertCell().textContent=p.commander;tr.insertCell().textContent=so=='new'||so=='old'?p.date:p.set;
  const ce=tr.insertCell();ce.className='r';ce.textContent=fe(p.eur);tr.insertCell().append(brBadge('',p.bracket_est));
  if(r.has_collection){const co=tr.insertCell();co.className='r';co.textContent=(p.owned||0)+' %'}})}
async function pcOpen(id){const d=await J('/api/precon?id='+id);const meta=(PC.data&&PC.data.precons||[]).find(x=>x.id==id)||{};
 const b=dlgOpen(d.error?'Precon':d.name);if(d.error){P(b,d.error,'warn');return}
 const h=$('p');h.append(manaEl((d.ci||'C').split('').map(x=>'{'+x+'}').join('')),' ',$('b',d.commander),' · '+d.set+' · '+d.date+' · '+(meta.cards||'')+' Karten · ca. '+fe(meta.eur)+' ',brBadge('',meta.bracket_est));b.append(h);
 if(meta.owned!=null)P(b,'Davon in deiner Sammlung: '+meta.owned+' % (ohne Standardländer).','hint');
 const bar=$('div');bar.className='pcbar';const msg=$('div');msg.id='pcmsg';
 const ed=$('button','✏ Im Deck-Editor öffnen');ed.type='button';ed.className='primary';ed.id='pcedit';ed.onclick=()=>{closeSwap();location.hash='#deck';useMine({name:d.name,commander:d.commander,list:d.export})};
 const sv=$('button','💾 In Meine Decks speichern');sv.type='button';sv.id='pcsave';sv.onclick=async()=>{const x=await J('/api/deck_save',{name:d.name+' (Precon)',commander:d.commander,list:d.export,extra:'{}'});msg.textContent=x.error?'⚠ '+x.error:'✓ als „'+x.name+'“ gespeichert';msg.className=x.error?'warn':'ok';if(!x.error){sv.disabled=true;myDecks(x.decks)}};
 const op=$('button','⚔ Als Gegner');op.type='button';op.id='pcopp';op.onclick=()=>{const has=deck&&!deck.error;if(has)closeSwap();setOpp({kind:'precon',id:id,name:d.name,commander:d.commander,set:d.set});if(!has){msg.textContent='✓ als Gegner gesetzt. Jetzt ein eigenes Deck bauen oder laden, dann vergleichen oder in Forge spielen.';msg.className='ok'}};
 const cp=$('button','📋 Liste kopieren');cp.type='button';cp.onclick=async()=>{await copyText(d.export);cp.textContent='✓ kopiert'};
 const co=$('button','📥 Gekauft: in meine Sammlung');co.type='button';co.id='pccoll';co.title='Alle Karten dieses Precons zu deiner Sammlung hinzufügen';
 co.onclick=async()=>{if(co.dataset.ok!='1'){co.dataset.ok='1';co.textContent='Wirklich alle '+(meta.cards||'')+' Karten hinzufügen?';return}
  const x=await J('/api/precon_to_collection',{id:id});msg.textContent=x.error?'⚠ '+x.error:'✓ '+x.imported+' Karten in die Sammlung übernommen ('+x.imp_unique+' verschiedene).';msg.className=x.error?'warn':'ok';co.disabled=true;co.textContent='✓ übernommen';
  const r2=await J('/api/precon_catalog');PC.data=r2;pcRender()};
 bar.append(ed,' ',sv,' ',op,' ',cp,' ',co);b.append(bar,msg);
 {const sp=$('p');sp.id='pcshops';sp.append('🛒 Kaufen bei: ',sealedLinks(d.name));b.append(sp)}
 if(d.missing&&d.missing.length)P(b,'Nicht in der Kartendatenbank gefunden: '+d.missing.join(', '),'warn');
 const w=$('div');w.className='pclist';w.id='pclist';b.append(w);
 d.groups.forEach(g=>{const s=$('div');s.className='pcg';s.append($('h4',g.name+' ('+g.cards.reduce((a,c)=>a+c.qty,0)+')'));
  g.cards.forEach(c=>{const r=$('div');r.append(c.qty+'× ',cardName(c.name,c.scryfall,c.image));if(c.gc){const x=$('span',' GC');x.className='gcm';x.title='Game Changer';r.append(x)}s.append(r)});w.append(s)})}

// ---- Cardmarket-Preise einer Karte
async function cmShow(name){const d=await J('/api/cm',{name:name});const b=dlgOpen(name);
 if(!d.found){P(b,'Für diese Karte gibt es keinen Eintrag in der Cardmarket-Preisliste (z. B. digitale oder sehr neue Karten).','hint');return}
 const t=$('table');t.className='ftable';t.id='cmtab';b.append(t);
 [['Trendpreis, günstigste Druckversion',d.trend],['Tiefstpreis über alle Drucke',d.low],['Durchschnitt letzter Tag',d.avg1],['Durchschnitt 7 Tage',d.avg7],['Durchschnitt 30 Tage',d.avg30],['Foil, günstigster Trendpreis',d.foil]]
  .forEach(([l,v])=>{const tr=t.insertRow();tr.insertCell().textContent=l;const c=tr.insertCell();c.className='r';c.textContent=fe(v)});
 const tr=t.insertRow();tr.insertCell().textContent='Druckversionen bei Cardmarket';const c=tr.insertCell();c.className='r';c.textContent=d.prints;
 if(d.avg30&&d.trend){const ch=Math.round((d.trend-d.avg30)/d.avg30*100);P(b,'Trend gegenüber dem 30-Tage-Durchschnitt: '+(ch>0?'+':'')+ch+' %','hint')}
 const a=$('a','🛒 Günstigste Druckversion auf Cardmarket ansehen',d.url);a.target='_blank';a.rel='noopener';a.id='cmlink';b.append($('p'));b.lastChild.append(a);
 if(SHOPON.to){const tp=$('p');tp.append('Auch bei: ',cmA('',name));tp.querySelector('.scm')&&tp.querySelector('.scm').remove();b.append(tp)}
 P(b,'Preise: Cardmarket, Preisliste vom '+d.at+'. Durchschnitte und Trend beziehen sich auf die günstigste Druckversion; Tiefst- und Foil-Preis auf alle Drucke.','hint')}
// ---- Händler-Links: Nutzer kaufen direkt beim Händler (eigene Anmeldung dort); es werden keine Daten übertragen
const SHOPS={cm:{name:'Cardmarket',short:'CM',search:q=>'https://www.cardmarket.com/de/Magic/Products/Search?searchString='+encodeURIComponent(q)},
 to:{name:'Trader-online',short:'TO',search:q=>'https://www.trader-online.de/index.php?cl=search&searchparam='+encodeURIComponent(q)},
 cc:{name:'cardcosmos',short:'CC',sealed:true,search:q=>'https://cardcosmos.de/search?q='+encodeURIComponent(q)+'&type=product'}};
let SHOPON={cm:true,to:true,cc:true};try{Object.assign(SHOPON,JSON.parse(localStorage.getItem('shops')||'{}'))}catch(e){}
function shopA(k,url,title){const s=SHOPS[k];const a=$('a',s.short,url);a.target='_blank';a.rel='noopener';a.className='shoplnk s'+k;a.title=title||('Bei '+s.name+' ansehen. Anmeldung und Kauf laufen direkt beim Händler.');return a}
function cmA(url,name){const w=$('span');w.className='shops';
 if(SHOPON.cm&&(url||name)){const a=shopA('cm',url||SHOPS.cm.search(name),'Auf Cardmarket ansehen (günstigste Druckversion)');a.classList.add('cmlnk');w.append(a)}
 if(name)Object.keys(SHOPS).filter(k=>k!='cm'&&SHOPON[k]&&!SHOPS[k].sealed).forEach(k=>w.append(shopA(k,SHOPS[k].search(name))));
 return w.childElementCount?w:''}
function sealedLinks(q){const w=$('span');w.className='shops';Object.keys(SHOPS).filter(k=>SHOPON[k]).forEach(k=>w.append(shopA(k,SHOPS[k].search(q),'„'+q+'“ bei '+SHOPS[k].name+' suchen')));return w}
function shopSettings(){const w=$('div');w.className='shopset';w.append($('span','Händler-Links: '));
 Object.entries(SHOPS).forEach(([k,s])=>{const l=$('label');const c=$('input');c.type='checkbox';c.checked=!!SHOPON[k];c.id='shopon-'+k;
  c.onchange=()=>{SHOPON[k]=c.checked;try{localStorage.setItem('shops',JSON.stringify(SHOPON))}catch(e){}document.querySelectorAll('.shopset input#shopon-'+k).forEach(x=>x.checked=c.checked)};
  l.append(c,' '+s.name+(s.sealed?' (nur versiegelte Ware, z. B. Precons)':''));w.append(l,' ')});return w}
async function cmWants(text,btn){await copyText(text);window.open('https://www.cardmarket.com/de/Magic/Wants','_blank','noopener');
 if(btn)btn.textContent='✓ Liste kopiert, Cardmarket geöffnet';
 const n=$('div','Bei Cardmarket: neue Wants-Liste anlegen → „Decklist hinzufügen“ → Liste einfügen (Strg+V) → „Hinzufügen“. Danach findet der Shopping Wizard die günstigste Händlerkombination.');n.className='hint cmhow';
 if(btn&&!btn.parentNode.querySelector('.cmhow'))btn.parentNode.append(n)}

// Probehand und Starthand-Statistik (London-Mulligan)
function libraryCards(){return deck.groups.filter(g=>g.name!='Commander').flatMap(g=>g.cards.flatMap(c=>Array(c.qty).fill(c)))}
function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
function handStats(lib,n=20000){const dist=Array(8).fill(0);const drops=[0,0,0,0];let keep=0;
 for(let k=0;k<n;k++){const d=shuffle(lib);let l=0;for(let i=0;i<7;i++)if(d[i].land)l++;dist[l]++;if(l>=2&&l<=5)keep++;
  let seen=l;for(let t=1;t<=4;t++){if(t>1&&d[6+t-1]&&d[6+t-1].land)seen++;if(seen>=t)drops[t-1]++}}
 return {dist:dist.map(x=>Math.round(x/n*1000)/10),keep:Math.round(keep/n*1000)/10,drops:drops.map(x=>Math.round(x/n*100))}}
function handBox(o){const box=$('div');o.append(box);const hh=$('h4','Probehand & Starthand-Statistik');hh.append(qBtn('anpassen'));box.append(hh);
 const lib=libraryCards();if(lib.length<7){P(box,'Zu wenige Karten für eine Probehand.','hint');return}
 const st=handStats(lib);
 P(box,'Behaltbare Starthände (2–5 Länder): '+String(st.keep).replace('.',',')+' % · Landdrop in Zug 1/2/3/4 (als Startspieler): '+st.drops.join(' % / ')+' %','hint');
 const dist=$('div');dist.className='hint';dist.textContent='Länder in der Starthand: '+st.dist.map((v,i)=>i+': '+String(v).replace('.',',')+' %').join(' · ');box.append(dist);
 const row=$('p');box.append(row);const area=$('div');box.append(area);
 let d=[],pos=0,mull=0;
 const show=()=>{area.innerHTML='';const hand=d.slice(0,pos);
  const lands=hand.filter(c=>c.land).length;
  P(area,(mull?'Mulligan '+mull+': '+(7-mull)+' behalten, '+mull+' unter die Bibliothek · ':'')+hand.length+' Karten · '+lands+' Länder','big');
  const gr=$('div');gr.className='grid';area.append(gr);
  hand.forEach(c=>{const a=c.image?$('a',null,c.scryfall):$('div',c.name);if(c.image){const im=$('img');im.src=c.image;im.alt=c.name;im.title=c.name;a.append(im)}else a.className='ph';gr.append(a)})};
 const b0=$('button','🎮 Testspielfeld öffnen');b0.type='button';b0.className='primary';b0.id='ptopen';b0.title='Deck auf einem Spielfeld ohne Gegner durchspielen';b0.onclick=ptNew;
 const b1=$('button','🃏 Probehand ziehen');b1.type='button';b1.className='primary';
 const b2=$('button','Karte ziehen');b2.type='button';const b3=$('button','Mulligan');b3.type='button';
 b1.onclick=()=>{d=shuffle(lib);pos=7;mull=0;show()};
 b2.onclick=()=>{if(!d.length)return b1.onclick();if(pos<d.length)pos++;show()};
 b3.onclick=()=>{d=shuffle(lib);pos=7;mull=Math.min(mull+1,6);show()};
 row.append(b0,' ',b1,' ',b2,' ',b3)}
function setView(v){view=v;try{localStorage.setItem('view',v)}catch(e){}
 document.querySelectorAll('.view button').forEach(b=>b.classList.toggle('on',b.dataset.v==v));
 if(deck)showDeck();if(precon)showPrecon()}
document.querySelectorAll('.view button').forEach(b=>b.onclick=()=>setView(b.dataset.v));

function showDeck(){const d=deck,o=E('out');o.innerHTML='';
 const h=(t,x)=>{const e=$(t,x);o.append(e);return e};
 (d.notes||[]).forEach(n=>h('p','• '+n));
 if(d.error){h('p',d.error);E('cmpbox').style.display='none';return}
 h('h3',(d.name?'Mein Deck: '+d.name:'Deckvorschlag')+(d.commander?' für '+d.commander:''));
 const sv=h('div');sv.className='savebox';sv.append($('b','💾 Deck speichern: '));const sn=$('input');sn.size=36;sn.value=d.name||d.commander||'';sn.placeholder='Name zum Speichern';
 const sno=$('input');sno.size=30;sno.placeholder='Notiz zur Änderung (optional)';sno.id='savenote';
 const sb=$('button','Speichern');sb.type='button';sb.className='primary';const sm=$('span');sv.append(sn,' ',sno,' ',sb,sm);
 sb.onclick=async()=>{sb.disabled=true;sm.className='hint';sm.textContent=' speichere ...';
  const r=await J('/api/deck_save',{name:sn.value,commander:d.commander||'',list:d.export,note:sno.value,extra:JSON.stringify(deckExtra())});sb.disabled=false;sno.value='';
  if(r.error){sm.className='warn';sm.textContent=' '+r.error;return}
  d.name=r.name;sm.className='tag';sm.textContent=' ✓ Gespeichert als „'+r.name+'“, zu finden unter „Deck importieren & gespeicherte Decks“.';
  myDecks(r.decks)};
 exportBox(h('div'),()=>({name:sn.value||d.name||'',commander:d.commander||'',list:d.export,groups:JSON.stringify(deckExtra().groups)}));
 const n=d.groups.reduce((s,g)=>s+g.cards.reduce((t,c)=>t+c.qty,0),0);
 if(n!=100)P(o,'Das Deck hat gerade '+n+' statt 100 Karten.','warn');
 const gcs=d.groups.filter(g=>g.name!='Commander').reduce((s,g)=>s+g.cards.filter(c=>c.gc).length,0);
 if(gcs){const b=h('button','Alle '+gcs+' Game Changer ersetzen');b.type='button';b.onclick=replaceAllGC}
 if(d.groups[0]&&d.groups[0].name=='Commander'&&d.groups[0].cards[0].gc)P(o,'Hinweis: Der Commander selbst steht auf der Game-Changer-Liste.','hint');
 h('p','Geschätzte Kosten: ca. '+d.cost.total.toFixed(2)+' € ('+d.cost.priced+' Karten mit Preis, '+d.cost.missing+' ohne; Basic Lands nicht eingerechnet)');
 h('h4','Manakurve (ohne Länder)');
 const cv=h('div');cv.style.cssText='display:flex;gap:8px;align-items:flex-end';
 const mx=Math.max(...d.curve,1);
 d.curve.forEach((n,i)=>{const c=$('div');c.style.textAlign='center';const b=$('div');
  b.style.cssText='background:#c0362c;width:36px;height:'+Math.round(n/mx*80)+'px';c.append(String(n),b,i==7?'7+':String(i));cv.append(c)});
 const adr=h('div');adr.className='savebox';adr.append($('b','➕ Karte hinzufügen: '));
 const ain=$('input');ain.size=34;ain.placeholder='Kartenname eintippen und auswählen';const asp=$('span');asp.className='ac';asp.append(ain);
 const ab=$('button','Hinzufügen');ab.type='button';const sc=$('button','📷 Scannen');sc.type='button';sc.onclick=()=>scanDialog('deck');adr.append(asp,' ',ab,' ',sc);
 ac(ain,{get:names(false),pick:n=>{ain.value='';addCardToDeck(n)}});
 ab.onclick=()=>{if(ain.value.trim()){const v=ain.value.trim();ain.value='';addCardToDeck(v)}};
 ain.addEventListener('keydown',e=>{if(e.key=='Enter'){e.preventDefault();ab.onclick()}});
 if(d.msg){P(adr,d.msg,'hint');d.msg=''}
 const tb=h('div');tb.className='edbar';tb.id='edbar';
 const un=$('button','↶ Rückgängig');un.type='button';un.id='dundo';un.title='Strg+Z';un.disabled=DH.pos<=0;un.onclick=deckUndo;
 const re=$('button','↷ Wiederherstellen');re.type='button';re.id='dredo';re.title='Strg+Y';re.disabled=DH.pos>=DH.stack.length-1;re.onclick=deckRedo;
 const se=$('button',DSEL.on?'☑ Auswahl beenden':'☐ Mehrfachauswahl');se.type='button';se.id='dselect';se.onclick=()=>{DSEL.on=!DSEL.on;DSEL.names.clear();showDeck()};
 const ng=$('button','➕ Neue Gruppe');ng.type='button';ng.id='dnewgrp';ng.onclick=()=>moveDialog([]);
 tb.append(un,' ',re,' ',se,' ',ng,$('span',' Karten in eine Gruppe ziehen oder ⇄ antippen. Eigene Gruppen werden mit dem Deck gespeichert.'));tb.lastChild.className='hint';
 if(DSEL.on){const sb=$('div');sb.id='selbar';sb.className='selbar';tb.append(sb)}
 cardsOut(o,d.groups,true);if(DSEL.on)selBar();
 deckRecord();
 bracketBox(h('div'));recBox(h('div'));maybeBox(h('div'));tagBox(h('div'));notesBox(h('div'));tokenBox(h('div'));priceBox(h('div'));budgetBox(h('div'));
 ownBox(h('div'));manaBox(h('div'));handBox(h('div'));
 h('h4','Textliste zum Kopieren');const t=h('textarea');t.rows=10;t.cols=50;t.value=d.export;
 E('cmpbox').style.display='block'}
// Farbknöpfe für die Farbidentität (Einsteiger müssen keine Buchstaben kennen)
var CINAME={W:'Weiß',U:'Blau',B:'Schwarz',R:'Rot',G:'Grün',C:'Farblos'};
const DV=(x,c)=>{const e=$('div',x);if(c)e.className=c;return e};
function ciBtns(){const box=E('cibtns');if(!box)return;box.innerHTML='';const v=ci.value.toUpperCase();
 ['W','U','B','R','G','C'].forEach(c=>{const b=$('button');b.type='button';b.className='pip p'+c+(c=='C'?(v=='C'?' on':''):(v.includes(c)&&v!='C'?' on':''));b.textContent=c=='C'?'◇':c;b.title=CINAME[c];b.disabled=ci.readOnly;b.dataset.c=c;
  b.onclick=()=>{let x=ci.value.toUpperCase().replace(/[^WUBRGC]/g,'');if(c=='C')x=x=='C'?'':'C';else{x=x.replace('C','');x=x.includes(c)?x.replace(c,''):x+c}
   ci.value=[...'WUBRGC'].filter(k=>x.includes(k)).join('');ciBtns()};box.append(b)})}
ci.addEventListener('input',ciBtns);
let csShown=[],csKey='';
async function suggestCmd(auto,more){const box=E('csug');const th=(E('b').elements.theme.value||'').trim(),c=ci.readOnly?'':ci.value.trim();
 if(!th&&!c){box.innerHTML='';P(box,'Bitte mindestens eine Farbe anklicken oder ein Thema eintragen.','hint');return}
 const key=[c,th,E('cfewer').checked,E('nogc').checked,E('maxprice').value].join('|');if(!more||key!=csKey){csShown=[];csKey=key}
 box.textContent='Suche passende Commander ...';
 const q=new URLSearchParams({ci:c,theme:th,fewer:E('cfewer').checked?'1':'',nogc:E('nogc').checked?'1':'',maxeur:E('maxprice').value||'',limit:'12',seed:String(Math.floor(Math.random()*1e9)),shown:csShown.join('|')});
 const r=await J('/api/commander_suggest?'+q);box.innerHTML='';
 if(r.error){P(box,r.error,'hint');return}
  if(!r.cards.length&&csShown.length){P(box,'Alle '+r.total+' passenden Commander wurden schon gezeigt. „Neu mischen“ beginnt wieder von vorn.','hint');const rb=$('button','🔀 Neu mischen');rb.type='button';rb.onclick=()=>suggestCmd(false,false);box.append(rb);return}
 if(!r.cards.length){P(box,'Keine passenden Commander gefunden. Tipp: „auch mit weniger Farben“ anhaken, eine Farbe mehr wählen oder ein anderes Thema probieren.','hint');return}
 const cn=c?(c=='C'?'farblos':[...c].map(x=>CINAME[x]).join('-')):'alle Farben';
 csShown=csShown.concat(r.cards.map(x=>x.name));
 P(box,(auto?'Ein Commander ist im Format Pflicht. Hier passende Vorschläge: ':'')+r.total+' Commander passen ('+cn+(th?', Thema „'+th+'“':'')+'). Gemischte Auswahl aus beliebten Commandern, Geheimtipps und günstigen Optionen'+(csShown.length>r.cards.length?' ('+csShown.length+' von '+r.total+' gezeigt)':'')+':','hint');
 const g=DV('','cgrid');
 r.cards.forEach(x=>{const d=DV('','cc');if(x.image){const im=$('img');im.loading='lazy';im.alt=x.name;im.src=x.image.replace('/normal/','/art_crop/');d.append(im)}
  const nb=$('b');nb.append(cardName(x.name,null,x.image));d.append(nb);const m=$('div');m.append(manaEl(x.ci?[...x.ci].map(k=>'{'+k+'}').join(''):'{C}'),' ',x.type);d.append(m);
  if(x.tag){const tg=DV({beliebt:'⭐ beliebt',Geheimtipp:'💎 Geheimtipp','günstig':'💶 günstig'}[x.tag]||x.tag,'ctag '+(x.tag=='günstig'?'cheap':x.tag=='Geheimtipp'?'gem':'pop'));d.insertBefore(tg,d.firstChild)}
  if(x.why.length)d.append(DV('passt zu: '+x.why.join(', '),'why'));
  if(x.gc)d.append(DV('⚠ Game Changer (sehr stark)','why'));
  d.append(DV(x.text,'tx'));
  const bt=$('button','✔ Diesen Commander nehmen');bt.type='button';bt.className='primary ctake';bt.onclick=async()=>{cmd.value='';await setCommander(x.name);ciBtns();E('csug').innerHTML='';
   P(E('csug'),'Commander „'+x.name+'“ übernommen. Jetzt „Deck vorschlagen“ klicken.','hint');cmd.scrollIntoView({block:'center'})};
  d.append(bt);g.append(d)});box.append(g);
 const nav=DV('','csnav');const mb=$('button',r.left>0?'🔄 Andere Vorschläge ('+r.left+' weitere)':'🔀 Neu mischen');mb.type='button';mb.id='csmore';
 mb.onclick=()=>suggestCmd(false,r.left>0);nav.append(mb);if(r.left>0){const rb=$('button','🔀 Neu mischen');rb.type='button';rb.onclick=()=>suggestCmd(false,false);nav.append(' ',rb)}box.append(nav)}
E('csugbtn').onclick=()=>suggestCmd(false,false);ciBtns();
E('wsug').addEventListener('click',()=>setTimeout(()=>E('csugbox').scrollIntoView({block:'center'}),150));
async function bd(e){e.preventDefault();
 const p=new URLSearchParams(new FormData(E('b')));
 E('out').textContent='Deck wird zusammengestellt ...';
 deck=await J('/api/build?'+p);showDeck();
 if(!cmd.value.trim()&&deck&&!deck.error)suggestCmd(true);
 E('cmp').innerHTML='';E('pview').innerHTML='';precon=null;afterDeck()}
function afterDeck(){loadPrecons();oppInfo();if(opp&&deck&&!deck.error)runCompare(opp);else{['combos','duel'].forEach(x=>E(x).innerHTML='')}}

// Precons: Auswahl, Vergleich, Ansicht
const plabel=p=>p.name+' · '+p.commander+' ('+p.set+', '+p.date.slice(0,4)+')';
const CDE={W:'Weiß',U:'Blau',B:'Schwarz',R:'Rot',G:'Grün'};
const ciName=ci=>(ci&&ci!='C')?[...ci].map(c=>CDE[c]||c).join('-'):'farblos';
const plong=p=>p.name+' · Commander: '+p.commander+' · '+ciName(p.ci);
let PALL=null;const preconsAll=async()=>PALL||(PALL=await J('/api/precons_all'));
// Auswahlliste mit allen Precons, gruppiert nach Set; optional eigene Decks und „passend“-Gruppe davor
function fillPreconSelect(sel,all,opts={}){
 const keep=sel.querySelector('option[value=""]');sel.innerHTML='';if(keep)sel.append(keep);
 const grp=(label,items,pref)=>{if(!items.length)return;const g=document.createElement('optgroup');g.label=label;
  items.forEach(p=>{const o=$('option',plong(p));o.value=(pref||'')+p.id;g.append(o)});sel.append(g)};
 if(opts.match&&opts.match.length)grp('Passend zu deinen Farben',opts.match,opts.prefix);
 const sets=[];all.forEach(p=>{const k=p.set+' ('+(p.date||'').slice(0,4)+')';let e=sets.find(x=>x.k==k);if(!e)sets.push(e={k:k,items:[]});e.items.push(p)});
 sets.forEach(e=>grp(e.k,e.items,opts.prefix));
 if(opts.decks&&opts.decks.length){const g=document.createElement('optgroup');g.label='Eigene gespeicherte Decks';
  opts.decks.forEach(d=>{const o=$('option','Eigenes Deck: '+d.name+(d.commander?' · '+d.commander:''));o.value='deck:'+d.id;g.append(o)});sel.append(g)}}
async function loadPrecons(){
 const info=await J('/api/info'),m=E('pmissing');m.innerHTML='';
 if(!info.precons_at){m.append($('p','Die Precon-Decklisten sind noch nicht geladen (einmalig ca. 30 MB von GitHub).'));
  const b=$('button','Precon-Daten jetzt laden');b.type='button';m.append(b);
  b.onclick=async()=>{b.disabled=true;b.textContent='Lade ...';const r=await J('/api/load_precons',{});
   m.innerHTML='';m.append($('p',r.error||r.count+' Precons geladen.'));loadPrecons()};return}
 const s=E('psugg');s.innerHTML='';
 const [list,all]=await Promise.all([J('/api/precons?ci='+encodeURIComponent(deck.ci||'')),preconsAll()]);
 const sel=E('pall');fillPreconSelect(sel,all,{match:list.slice(0,8)});
 sel.onchange=()=>{const p=all.find(x=>String(x.id)==sel.value);if(p)setOpp({kind:'precon',id:p.id,name:p.name,commander:p.commander,set:p.set})};
 if(list.length){s.append($('span','Schnellwahl passend zu deinen Farben: '))}
 list.slice(0,8).forEach(p=>{const b=$('button');b.type='button';b.append($('b',p.name),' · '+p.commander+' ('+ciName(p.ci)+')');b.title=plabel(p);
  b.onclick=()=>setOpp({kind:'precon',id:p.id,name:p.name,commander:p.commander,set:p.set});s.append(b)})}
ac(E('pq'),{get:async v=>(await J('/api/precons?q='+encodeURIComponent(v))).map(p=>({t:plabel(p),v:p.id})),
 pick:(id,it)=>{E('pq').value=it.t;const p=(PALL||[]).find(x=>x.id==id);setOpp(p?{kind:'precon',id:p.id,name:p.name,commander:p.commander,set:p.set}:{kind:'precon',id:id,name:it.t})}});
const fmt=v=>v==null?'–':(typeof v=='number'&&!Number.isInteger(v)?v.toFixed(2):String(v));
const oppP=()=>opp.kind=='precon'?{precon:opp.id}:{opp_list:opp.list,opp_commander:opp.commander||'',opp_name:opp.name||''};
const mineP=()=>({list:deck.export,commander:deck.commander||'',ci:deck.ci||''});
function oppInfo(){E('oppinfo').textContent=opp?'Aktueller Gegner: '+(opp.kind=='precon'?'Precon „'+opp.name+'“'+(opp.commander?', Commander: '+opp.commander:'')+(opp.set?' ('+opp.set+')':''):opp.name):'Noch kein Gegner gewählt.';
 const sel=E('pall');if(sel)sel.value=opp&&opp.kind=='precon'?String(opp.id):''}
function setOpp(o){opp=o;oppInfo();E('pview').innerHTML='';precon=null;
 if(deck&&!deck.error){runCompare(opp);if(document.body.dataset.page!='gegner')goTab('gegner')}}
async function runCompare(o){
 const out=E('cmp');out.textContent='Vergleiche ...';
 const r=await J('/api/compare',Object.assign(mineP(),oppP()));
 out.innerHTML='';if(r.error){out.append($('p',r.error));return}
 const on=r.opp.kind=='precon'?'Precon':'Gegner';
 out.append($('h3','Dein Deck gegen „'+r.opp.name+'“ ('+(r.opp.commander||'ohne Commander')+')'));
 P(out,'Ergebnis '+r.score[0]+' : '+r.score[1],'big');
 out.append($('p',r.verdict));
 const t=$('table');t.className='duel';out.append(t);
 const hr=t.insertRow();['Kategorie','Dein Deck',on,'Hinweis'].forEach(x=>hr.append($('th',x)));
 const extra=[['Bracket-Schätzung','bracket'],['Kartenpreis gesamt (€)','price'],['Extra-Züge','extra'],['Massen-Landzerstörung','mld']];
 for(const x of r.rows){const tr=t.insertRow();tr.insertCell().textContent=x.label;
  const a=tr.insertCell(),b=tr.insertCell();a.textContent=fmt(x.a);b.textContent=fmt(x.b);
  if(x.win>0){a.className='w';b.className='l'}else if(x.win<0){b.className='w';a.className='l'}
  tr.insertCell().textContent=x.hint}
 for(const [l,k] of extra){const tr=t.insertRow();tr.insertCell().textContent=l;
  tr.insertCell().textContent=fmt(r.a[k]);tr.insertCell().textContent=fmt(r.b[k]);tr.insertCell().textContent=k=='price'?'nur Info':''}
 P(out,'Bracket-Schätzung nach Game Changern, Extra-Zügen und Landzerstörung; Combos siehe unten.','hint');
 out.append($('h4','Gemeinsame Karten ('+r.shared.length+')'));const shp=$('p');r.shared.forEach((n,k)=>{if(k)shp.append(', ');shp.append(cardName(n))});if(!r.shared.length)shp.append('keine');out.append(shp);
 if(r.ideas.length){const d=$('div');out.append(d);cardsOut(d,[{name:'Ideen aus dem Gegnerdeck (beliebt, nicht in deinem Deck)',cards:r.ideas}])}
 if(r.missing.length)P(out,'Nicht gefunden: '+r.missing.join(', '),'hint');
 const vb=$('button','Deckliste des Gegners anzeigen');vb.type='button';out.append(vb);
 loadCombos();duelBox();
 vb.onclick=async()=>{if(opp.kind=='precon')precon=await J('/api/precon?id='+opp.id);
  else{const v=await J('/api/deck_view',{list:opp.list,commander:opp.commander||''});
   precon=v.error?v:{name:opp.name,set:'eigenes Deck',date:'',groups:v.groups,export:v.export}}
  showPrecon()}}
function showPrecon(){const o=E('pview');o.innerHTML='';const p=precon;
 if(p.error){o.append($('p',p.error));return}
 o.append($('h3','Gegner: '+p.name+' ('+p.set+(p.date?', '+p.date:'')+')'));cardsOut(o,p.groups);
 o.append($('h4','Textliste'));const t=$('textarea');t.rows=8;t.cols=50;t.value=p.export;o.append(t)}

// ---- Export und Übertragung zu anderen Seiten
const SITES={moxfield:['Moxfield','https://moxfield.com/decks/personal','arena',
  'In Moxfield: „Create Deck“ (bzw. bestehendes Deck → „Bulk Edit“), Format Commander wählen und mit Strg+V einfügen.'],
 archidekt:['Archidekt','https://archidekt.com/','archidekt',
  'In Archidekt: neues Deck anlegen → „Import“ öffnen, mit Strg+V einfügen und „Save Changes“ klicken. Der Commander ist bereits markiert.']};
async function copyText(t){if(window.AndroidBridge&&AndroidBridge.copyText){AndroidBridge.copyText(t);return true}
 try{await navigator.clipboard.writeText(t);return true}catch(e){
 const ta=$('textarea');ta.value=t;document.body.append(ta);ta.select();let ok=false;try{ok=document.execCommand('copy')}catch(x){}ta.remove();return ok}}
function download(name,text){if(window.AndroidBridge&&AndroidBridge.saveFile){AndroidBridge.saveFile(name,text);return}
 const a=$('a');a.href=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'}));
 a.download=name;document.body.append(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},500)}
function exportBox(o,get){const hh=$('h4','Exportieren & übertragen');hh.append(qBtn('export'));o.append(hh);
 const msg=$('p');msg.className='hint';
 const row=$('div');o.append(row,msg);
 for(const [k,[label,url,fmt,how]] of Object.entries(SITES)){const b=$('button','→ '+label);b.type='button';b.title='Liste kopieren und '+label+' öffnen';row.append(b);
  b.onclick=async()=>{const w=window.open(url,'_blank');const r=await J('/api/export',Object.assign(get(),{fmt}));
   if(r.error){msg.className='warn';msg.textContent=r.error;return}
   const ok=await copyText(r.text);msg.className='hint';
   msg.textContent=(ok?'Deckliste ist kopiert. ':'Kopieren nicht möglich. Bitte die Datei unten herunterladen. ')+how+(w?'':' (Pop-up blockiert, bitte '+url+' selbst öffnen.)')}}
 const cp=$('button','Text kopieren');cp.type='button';row.append(cp);
 cp.onclick=async()=>{const r=await J('/api/export',Object.assign(get(),{fmt:'arena'}));
  msg.textContent=r.error||((await copyText(r.text))?'Deckliste (Arena-/Moxfield-Format) kopiert. Das Format passt für die meisten Seiten und Apps.':'Kopieren nicht möglich.')};
 const sel=$('select');[['arena','Datei: Moxfield/Arena (.txt)'],['archidekt','Datei: Archidekt (.txt)'],['text','Datei: einfache Liste (.txt)'],
  ['dck','Datei: Forge (.dck)'],['csv','Datei: CSV']].forEach(([v,t])=>{const op=$('option',t);op.value=v;sel.append(op)});
 const dl=$('button','Herunterladen');dl.type='button';row.append(' ',sel,dl);
 dl.onclick=async()=>{const r=await J('/api/export',Object.assign(get(),{fmt:sel.value}));
  if(r.error){msg.className='warn';msg.textContent=r.error;return}download(r.filename,r.text);msg.className='hint';msg.textContent='Datei „'+r.filename+'“ wird heruntergeladen.'};
 const fg=$('button','In Forge-Deckordner speichern');fg.type='button';if(!ME.server)row.append(' ',fg);
 fg.onclick=async()=>{const r=await J('/api/export',Object.assign(get(),{fmt:'forge'}));
  msg.className=r.error?'warn':'hint';msg.textContent=r.error||('Gespeichert: '+r.path+'. In Forge unter Commander-Decks auswählbar.')}}

// ---- Import und gespeicherte Decks
// Kodierung der Datei erkennen: UTF-8 (mit/ohne BOM), UTF-16, sonst Windows-1252 (ältere Windows-Programme)
function decodeFile(buf){const b=new Uint8Array(buf);
 if(b[0]==0xFF&&b[1]==0xFE)return new TextDecoder('utf-16le').decode(b.subarray(2));
 if(b[0]==0xFE&&b[1]==0xFF)return new TextDecoder('utf-16be').decode(b.subarray(2));
 if(b[0]==0xEF&&b[1]==0xBB&&b[2]==0xBF)return new TextDecoder('utf-8').decode(b.subarray(3));
 try{return new TextDecoder('utf-8',{fatal:true}).decode(b)}catch(e){return new TextDecoder('windows-1252').decode(b)}}
E('impfile').onchange=async()=>{const f=E('impfile').files[0];if(!f)return;
 E('imptext').value=decodeFile(await f.arrayBuffer());E('impfile').dataset.name=f.name;E('impurl').value=''};
E('impgo').onclick=async()=>{const o=E('impres');o.textContent='Importiere ...';
 imp=await J('/api/import',{text:E('imptext').value,url:E('impurl').value.trim(),filename:E('impfile').dataset.name||''});showImport()};
function showImport(){const o=E('impres'),r=imp;o.innerHTML='';
 if(r.error){P(o,r.error,'warn');return}
 P(o,r.count+' Karten erkannt'+(r.ci?' · Farbidentität '+r.ci:''),'big');
 const nm=$('input');nm.size=40;nm.value=r.name;const l1=$('div');l1.append('Deckname: ',nm);o.append(l1);
 const sp=$('span');sp.className='ac';const cm=$('input');cm.size=50;cm.value=r.commander;
 cm.placeholder='Commander (Partner mit „ + “ trennen)';sp.append(cm);const l2=$('div');l2.append('Commander: ',sp);o.append(l2);
 ac(cm,{get:names(true),pick:n=>{cm.value=n}});
 if(r.candidates.length){const ch=$('div');ch.className='chips';ch.append('Mögliche Commander (Klick fügt hinzu/entfernt): ');o.append(ch);
  r.candidates.slice(0,12).forEach(n=>{const b=$('button',n);b.type='button';ch.append(b);
   b.onclick=()=>{let l=cm.value.split(' + ').map(x=>x.trim()).filter(Boolean);
    l=l.includes(n)?l.filter(x=>x!=n):l.concat(n);cm.value=l.join(' + ')}})}
 r.notes.forEach(n=>P(o,'• '+n,'hint'));
 if(r.missing.length)P(o,'Nicht gefunden ('+r.missing.length+'): '+r.missing.join(', '),'warn');
 if(r.fixed.length){const d=$('details');d.append($('summary','Automatisch korrigierte Namen ('+r.fixed.length+')'));
  r.fixed.forEach(f=>d.append($('div',f)));o.append(d)}
 const cur=()=>({name:nm.value.trim(),commander:cm.value.trim(),list:r.list});
 const act=$('p');o.append(act);
 const b1=$('button','Als mein Deck verwenden');b1.type='button';b1.onclick=()=>useMine(cur());
 const b2=$('button','Als Gegner verwenden');b2.type='button';b2.onclick=()=>useOpp(cur(),act);
 const b3=$('button','💾 Speichern');b3.type='button';b3.className='primary';
 const sm=$('span');
 b3.onclick=async()=>{const x=await J('/api/deck_save',cur());
  if(x.error){sm.className='warn';sm.textContent=' '+x.error;return}
  sm.className='tag';sm.textContent=' ✓ Gespeichert als „'+x.name+'“';myDecks(x.decks)};
 act.append(b1,b2,b3,sm);exportBox(o,cur)}
async function useMine(d){E('out').textContent='Lade Deck ...';
 deck=await J('/api/deck_view',d);deck.name=d.name;if(d.extra&&!deck.error)await applyExtra(d.extra);showDeck();
 E('cmp').innerHTML='';E('pview').innerHTML='';precon=null;afterDeck();goTab('deck')}
function useOpp(d,where){setOpp({kind:'deck',name:d.name||d.commander||'Gegnerdeck',list:d.list,commander:d.commander});
 if(!(deck&&!deck.error)&&where)P(where,'Als Gegner gesetzt. Jetzt ein eigenes Deck vorschlagen oder laden.','hint')}
function shareDialog(d){const b=dlgOpen('Deck teilen: '+d.name);
 P(b,'Wer den Link hat, sieht das Deck als Nur-Lese-Seite (Karten, Bilder, Tags, Notizen, Maybeboard), auch ohne Anmeldung. Du kannst den Link jederzeit widerrufen.','hint');
 if(!ME.server)P(b,'Hinweis: Im lokalen Betrieb funktioniert der Link nur auf diesem PC bzw. im Heimnetz (Start mit „im Netzwerk“). Für Links im Internet den Server-Betrieb nutzen.','hint');
 const res=$('div');b.append(res);
 const show=r=>{res.innerHTML='';if(r.error){P(res,r.error,'warn');return}
  if(r.token){const url=location.origin+r.path;const inp=$('input');inp.size=60;inp.value=url;inp.readOnly=true;inp.id='shareurl';res.append(inp);
   const cp=$('button','Kopieren');cp.type='button';cp.onclick=async()=>{await copyText(url);cp.textContent='✓ kopiert'};
   const op=$('a','Öffnen',url);op.target='_blank';const off=$('button','Link widerrufen');off.type='button';off.id='shareoff';
   off.onclick=async()=>{show(await J('/api/deck_share',{id:d.id,on:0}));myDecks()};res.append(' ',cp,' ',op,$('p'),off)}
  else{const on=$('button','Link erzeugen');on.type='button';on.className='primary';on.id='shareon';
   on.onclick=async()=>{show(await J('/api/deck_share',{id:d.id,on:1}));myDecks()};res.append(on)}};
 show({token:d.shared?'?':'',path:''});if(d.shared)J('/api/deck_share',{id:d.id,on:1}).then(show)}
async function versionsDialog(id){const b=dlgOpen('Versionen');const r=await J('/api/deck_versions?id='+id);
 if(r.error){P(b,r.error,'warn');return}
 P(b,'Deck „'+r.deck.name+'“ · aktuelle Fassung: '+deck_count_js(r.deck.list)+' Karten. Ältere Fassungen werden beim Speichern automatisch gesichert (bis zu 30).','hint');
 if(!r.versions.length){P(b,'Noch keine älteren Fassungen. Sie entstehen, sobald du das Deck geändert speicherst.');return}
 const cmp=$('div');cmp.className='savebox';b.append(cmp);cmp.append($('b','Zwei Fassungen vergleichen: '));
 const opts=[{v:0,t:'aktuelle Fassung'}].concat(r.versions.map(v=>({v:v.vid,t:v.saved_at+(v.note?': '+v.note:'')})));
 const mk=(sel)=>{const s=$('select');opts.forEach(o=>{const op=$('option',o.t);op.value=o.v;s.append(op)});s.value=sel;return s};
 const sa=mk(r.versions[r.versions.length-1].vid),sb2=mk(0);sa.id='vcmpa';sb2.id='vcmpb';
 const go=$('button','Vergleichen');go.type='button';const res=$('div');
 cmp.append('von ',sa,' nach ',sb2,' ',go,res);
 go.onclick=async()=>{const x=await J('/api/deck_version_diff?id='+id+'&a='+sa.value+'&b='+sb2.value);res.innerHTML='';
  if(x.error){P(res,x.error,'warn');return}
  P(res,'Von '+x.from+' nach '+x.to+': dazugekommen '+(x.added.join(', ')||'–')+' · entfernt '+(x.removed.join(', ')||'–'))};
 for(const v of r.versions){const d=$('div');d.className='combo';b.append(d);
  d.append($('b','Fassung vom '+v.saved_at+' ('+v.count+' Karten)'+(v.note?': „'+v.note+'“':'')));
  d.append($('div','Seitdem dazugekommen: '+(v.added.join(', ')||'–')));
  d.append($('div','Seitdem entfernt: '+(v.removed.join(', ')||'–')));
  const rs=$('button','Diese Fassung wiederherstellen');rs.type='button';
  rs.onclick=async()=>{const x=await J('/api/deck_restore',{id:id,vid:v.vid});if(x.error){P(d,x.error,'warn');return}
   myDecks(x.decks);versionsDialog(id)};d.append(rs)}}
function deck_count_js(t){return (t||'').split('\\n').filter(l=>l.trim()).reduce((s,l)=>s+(parseInt(l)||1),0)}
function collSum(c){E('collsum2').textContent=E('collsum').textContent=c.unique?'('+c.unique+' verschiedene, '+c.total+' Karten, ca. '+c.value.toFixed(2).replace('.',',')+' €)':'(noch leer)';
 const is=E('invsum');if(is)is.textContent=c.unique?'('+(c.known||0)+' mit Druck, '+(c.unknown_print||0)+' ohne'+(c.foil?', '+c.foil+' Foil':'')+')':''}
// ---- Bestand nach Druck
const INV={page:0};const eur2=v=>v==null?'–':v.toFixed(2).replace('.',',')+' €';
const invKey=it=>({name:it.name,set_code:it.set_code,number:it.number,foil:it.foil,cond:it.cond,lang:it.lang});
async function invLoad(){const o=E('invres');if(!o)return;
 const r=await J('/api/inv?'+new URLSearchParams({q:E('invq').value,sort:E('invsort').value,only:E('invonly').value,page:INV.page}));INV.r=r;invRender(r)}
async function invSet(it,ch,qty){const r=await J('/api/inv_set',Object.assign({old:JSON.stringify(invKey(it)),new:JSON.stringify(ch||{})},qty!=null?{qty:qty}:{}));
 if(r.error){alertBox(r.error);return}J('/api/collection').then(collSum);invLoad()}
function invSel(opts,val,on){const s=$('select');opts.forEach(([v,t])=>{const o=$('option',t);o.value=v;if(String(v)==String(val))o.selected=true;s.append(o)});s.onchange=()=>on(s.value);return s}
function invRender(r){const o=E('invres');o.innerHTML='';
 if(!r.entries){P(o,'Noch keine Karten in der Sammlung. Importiere oben eine Liste oder füge hier einzelne Drucke hinzu.','hint');return}
 const sm=$('p');sm.id='invtotal';o.append(sm);sm.append($('b','Wert nach Druck: '+eur2(r.value_print)),' · würde man jede Karte im günstigsten Druck rechnen: '+eur2(r.value_cheap)+
  ' · '+r.known+' Karten mit bekanntem Druck, '+r.unknown+' ohne'+(r.foil?' · '+r.foil+' Foils':''));
 if(r.pending){const b=$('button','Druckdaten für '+r.pending+' Einträge nachladen');b.type='button';b.id='invresolve';
  b.onclick=async()=>{b.disabled=true;b.textContent='lade …';const x=await J('/api/inv_resolve',{});if(x.error)alertBox(x.error);invLoad();J('/api/collection').then(collSum)};sm.append(' ',b)}
 P(o,'Preise: Cardmarket'+(r.cm_at?' (Preisliste vom '+r.cm_at+')':'')+' je Druck und Foil, sonst Scryfall; ohne bekannten Druck gilt der günstigste Druck der Karte. Zustand und Sprache ändern den Wert nicht, weil die Cardmarket-Preisliste sie nicht unterscheidet.','hint');
 const t=$('table');t.id='invtab';o.append(t);const hr=t.insertRow();['','Karte','Druck','Foil','Zustand','Sprache','Anzahl','Preis','Wert',''].forEach(x=>hr.append($('th',x)));
 const conds=[['','–'],...r.conds.map(([c,n])=>[c,c+' ('+n+')'])],langs=[['','–'],...r.langs.map(([c,n])=>[c,n])];
 r.items.forEach(it=>{const tr=t.insertRow();tr.dataset.name=it.name;
  const c0=tr.insertCell();if(it.image){const im=$('img');im.src=it.image;im.loading='lazy';im.className='invimg';im.alt='';c0.append(im)}
  tr.insertCell().append(cardName(it.name));
  const c2=tr.insertCell();c2.className='invprint';c2.append(it.set_code?(it.set_code+(it.number?' #'+it.number:'')+(it.set_name?' · '+it.set_name:'')+(it.known?'':' (Daten fehlen)')):'unbekannt',' ');
  const pb=$('button','✎');pb.type='button';pb.className='sw invchg';pb.title='Druck wählen';pb.onclick=()=>invPrints(it.name,it);c2.append(pb);
  const fin=it.finishes||['nonfoil','foil','etched'];const fo=[[0,'normal'],[1,'Foil'],[2,'Etched']].filter(([v])=>v==it.foil||fin.includes(['nonfoil','foil','etched'][v]));
  tr.insertCell().append(invSel(fo,it.foil,v=>invSet(it,{foil:+v})));
  tr.insertCell().append(invSel(conds,it.cond,v=>invSet(it,{cond:v})));
  tr.insertCell().append(invSel(langs,it.lang,v=>invSet(it,{lang:v})));
  const q=$('input');q.type='number';q.min=0;q.value=it.qty;q.className='invqty';q.style.width='4em';q.onchange=()=>invSet(it,{},Math.max(0,parseInt(q.value)||0));tr.insertCell().append(q);
  const pc=tr.insertCell();pc.textContent=eur2(it.price);pc.title={cm:'Cardmarket-Preis dieses Drucks',scryfall:'Scryfall-Preis dieses Drucks',cheapest:'günstigster Druck der Karte (Druck unbekannt oder ohne Preis)'}[it.src]||'';
  if(it.src=='cheapest')pc.className='hint';
  tr.insertCell().textContent=eur2(it.value);
  const ac_=tr.insertCell();{const sl=cmA(it.cm,it.name);if(sl)ac_.append(sl,' ')}const del=$('button','✕');del.type='button';del.className='sw';del.title='Eintrag entfernen';
  del.onclick=()=>{if(del.textContent!='sicher?'){del.textContent='sicher?';return}invSet(it,{},0)};ac_.append(del)});
 if(r.count>r.per){const pg=$('p');o.append(pg);pg.append('Einträge '+(r.page*r.per+1)+'–'+Math.min(r.count,(r.page+1)*r.per)+' von '+r.count+' ');
  if(r.page>0)pg.append(Object.assign($('button','◀'),{type:'button',onclick:()=>{INV.page--;invLoad()}}));
  if((r.page+1)*r.per<r.count)pg.append(Object.assign($('button','▶'),{type:'button',onclick:()=>{INV.page++;invLoad()}}))}}
async function invPrints(name,it){const o=dlgOpen((it?'Druck ändern: ':'Druck wählen: ')+name);const w=P(o,'Lade die Drucke …','hint');
 const r=await J('/api/prints?name='+encodeURIComponent(name));w.remove();if(r.error){P(o,r.error,'warn');return}
 if(r.warn)P(o,r.warn+' Angezeigt werden die zuletzt geladenen Drucke.','hint');
 const top=$('div');o.append(top);let q=null,cond=null,lang=null;
 if(!it){q=$('input');q.type='number';q.min=1;q.value=1;q.style.width='4em';cond=invSel([['','Zustand –'],...CONDS_JS],'NM',()=>{});lang=invSel([['','Sprache –'],...LANGS_JS],'',()=>{});
  top.append('Anzahl ',q,' ',cond,' ',lang)}
 P(o,r.prints.length+' Drucke, neueste zuerst. Preise: Cardmarket je Druck (sonst Scryfall).','hint');
 const flt=$('input');flt.placeholder='Set oder Jahr filtern';flt.size=20;o.append(flt);const lst=$('div');lst.id='printlist';o.append(lst);
 const draw=()=>{lst.innerHTML='';const f=flt.value.toLowerCase();r.prints.filter(x=>!f||(x.set_name+' '+x.set_code+' '+(x.released||'')).toLowerCase().includes(f)).slice(0,150).forEach(x=>{
  const d=$('div');d.className='alt printrow';d.dataset.set=x.set_code;d.dataset.num=x.number;lst.append(d);
  if(x.image){const im=$('img');im.src=x.image;im.loading='lazy';im.alt='';d.append(im)}
  const n=$('div');n.className='n';d.append(n);n.append($('b',x.set_name+' ('+x.set_code+' #'+x.number+')'),$('div',(x.released||'')+(x.rarity?' · '+x.rarity:'')));
  n.append($('div','normal: '+eur2(x.eur)+' · Foil: '+eur2(x.eur_foil)));if(x.cm)n.append(cmA(x.cm));
  const pick=(foil)=>{const b=$('button',(it?'Diesen Druck':'Hinzufügen')+(foil?' (Foil)':''));b.type='button';b.className=foil?'':'primary';
   b.onclick=async()=>{if(it){await invSet(it,{set_code:x.set_code,number:x.number,foil:foil})}
    else{const a=await J('/api/inv_add',{item:JSON.stringify({name:name,set_code:x.set_code,number:x.number,foil:foil,qty:parseInt(q.value)||1,cond:cond.value,lang:lang.value})});
     if(a.error){alertBox(a.error);return}J('/api/collection').then(collSum);invLoad()}closeSwap()};return b};
  const bs=$('div');d.append(bs);if(x.finishes.includes('nonfoil'))bs.append(pick(0));if(x.finishes.includes('foil')||x.finishes.includes('etched'))bs.append(' ',pick(x.finishes.includes('foil')?1:2))})};
 flt.oninput=draw;draw()}
let CONDS_JS=[['MT','MT (Mint)'],['NM','NM (Near Mint)'],['EX','EX (Excellent)'],['GD','GD (Good)'],['LP','LP (Light Played)'],['PL','PL (Played)'],['PO','PO (Poor)']];
let LANGS_JS=[['EN','Englisch'],['DE','Deutsch'],['FR','Französisch'],['IT','Italienisch'],['ES','Spanisch'],['PT','Portugiesisch'],['JA','Japanisch'],['KO','Koreanisch'],['RU','Russisch'],['ZHS','Chinesisch (vereinfacht)'],['ZHT','Chinesisch (traditionell)']];
E('invbox').addEventListener('toggle',()=>{if(E('invbox').open)invLoad()});
['invq'].forEach(id=>{let tm;E(id).oninput=()=>{clearTimeout(tm);tm=setTimeout(()=>{INV.page=0;invLoad()},300)}});
['invsort','invonly'].forEach(id=>E(id).onchange=()=>{INV.page=0;invLoad()});
ac(E('invname'),{get:names(false),pick:n=>{E('invname').value=n;invPrints(n)},enter:()=>{if(E('invname').value.trim())invPrints(E('invname').value.trim())}});
E('invpick').onclick=()=>{const n=E('invname').value.trim();if(n)invPrints(n);else E('invname').focus()};
J('/api/collection').then(collSum);
E('collfile').onchange=async()=>{const f=E('collfile').files[0];if(f)E('colltext').value=decodeFile(await f.arrayBuffer())};
E('collgo').onclick=async()=>{const o=E('collres');o.innerHTML='';P(o,'importiere ...','hint');
 const r=await J('/api/collection_import',{text:E('colltext').value,mode:document.querySelector('input[name=collmode]:checked').value});o.innerHTML='';
 if(r.error){P(o,r.error,'warn');return}collSum(r);E('colltext').value='';
 P(o,'✓ '+r.imported+' Karten ('+r.imp_unique+' verschiedene) übernommen.','tag');
 if(r.fixed.length)P(o,'Korrigiert: '+r.fixed.join(', '),'hint');
 if(r.unknown_count)P(o,r.unknown_count+' nicht erkannt: '+r.unknown.join(', ')+(r.unknown_count>r.unknown.length?' …':''),'warn');
 if(r.with_print)P(o,r.with_print+' Karten mit Druckangabe (Set/Nummer), '+r.without_print+' ohne'+(r.prints_left?' · für '+r.prints_left+' Einträge fehlen noch Druckdaten (unten unter „📚 Bestand“ nachladen)':'')+'.','hint');
 if(r.prints_error)P(o,r.prints_error,'warn');
 if(E('invbox').open)invLoad();
 if(deck&&!deck.error)showDeck()};
E('collexp').onclick=async()=>{const r=await J('/api/collection_export');download('sammlung.csv',r.csv)};
E('collexpn').onclick=async()=>{const r=await J('/api/collection_export?fmt=names');download('sammlung-namen.csv',r.csv)};
E('collclr').onclick=async()=>{const b=E('collclr');if(b.textContent!='Wirklich leeren?'){b.textContent='Wirklich leeren?';return}
 b.textContent='Sammlung leeren';collSum(await J('/api/collection_clear',{}))};
async function ownBox(o){const r=await J('/api/ownership',{list:deck.export,commander:deck.commander||'',deck_name:deck.name||''});
 if(r.error||!r.has_collection)return;
 const b=$('div');b.className='savebox';o.append(b);
 b.append($('b','Sammlung: '),String(r.percent)+' % des Decks besitzt du'+(r.missing.length?' · es fehlen '+r.missing.length+' Karten (ca. '+r.missing_eur.toFixed(2).replace('.',',')+' €)':' · alles vorhanden'));
 if(r.shared.length)P(b,'Schon in anderen Decks verbaut (nicht genug Exemplare frei): '+r.shared.join(', '),'hint');
 if(r.missing.length){const bt=$('button','Fehlende Karten kopieren');bt.type='button';bt.onclick=async()=>{await copyText(r.missing.map(n=>'1 '+n).join('\\n'));bt.textContent='✓ kopiert'};
  const bk=$('button','🧭 Kauf planen');bk.type='button';bk.id='ownbuy';bk.onclick=async()=>{location.hash='#sammlung';await new Promise(r=>setTimeout(r,300));const bb=E('buybox');bb.open=true;await buyInit({source:'deck'});bb.scrollIntoView({behavior:'smooth'})};
  const bw=$('button','⭐ Fehlende auf die Wunschliste');bw.type='button';bw.id='ownwish';bw.onclick=async()=>{const x=await J('/api/wish_add',{text:r.missing.map(n=>'1 '+n).join('\\n')});bw.textContent='✓ '+x.added+' auf der Wunschliste'};b.append(bt,' ',bk,' ',bw)}
 document.querySelectorAll('#out [data-name]:not(.stc)').forEach(el=>{const c=r.cards[el.dataset.name];if(!c||c.basic)return;
  const t=$('span',c.owned?(c.free?' ✓':' ⚠ auch in '+c.other.join(', ')):' ✗ fehlt');t.className=c.owned?(c.free?'tag':'hint'):'warn';
  t.title=c.owned?c.owned+'× in deiner Sammlung':'nicht in deiner Sammlung';el.append(t)})}
// ---- Kartenscanner: Foto / Live-Kamera / Android-App-Kamera -> Texterkennung -> Kartenname
let ocrWorkers={},scanList=[];try{scanList=JSON.parse(localStorage.getItem('scanlist')||'[]')}catch(e){}
const scanSave=()=>{try{localStorage.setItem('scanlist',JSON.stringify(scanList))}catch(e){}};
const nativeScan=()=>!!(window.AndroidBridge&&AndroidBridge.hasScanner&&AndroidBridge.hasScanner());
function loadScript(src){return new Promise((ok,no)=>{if([...document.scripts].some(s=>s.src.endsWith(src)))return ok();const s=document.createElement('script');s.src=src;s.onload=ok;s.onerror=()=>no(new Error(src));document.head.append(s)})}
async function ocrWorker(lang,status){if(ocrWorkers[lang])return ocrWorkers[lang];
 let st=await J('/api/ocr_status');
 if(!st.ready){status('Texterkennung wird einmalig eingerichtet (rund 25 MB) …');st=await J('/api/ocr_prepare');if(st.error||!st.ready)throw new Error(st.error||'Texterkennung nicht verfügbar')}
 status('Texterkennung startet …');await loadScript('/ocr/tesseract.min.js');
 ocrWorkers[lang]=await Tesseract.createWorker(lang,1,{workerPath:'/ocr/worker.min.js',corePath:'/ocr/core',langPath:'/ocr/lang',workerBlobURL:false,gzip:true});
 return ocrWorkers[lang]}
// Bild aufbereiten: verkleinern, Graustufen, Kontrast (bessere Erkennung bei Handyfotos)
function prepCanvas(src,sx,sy,sw,sh,maxw,strong){const c=document.createElement('canvas');const sc=Math.min(1,(maxw||1600)/sw)*(sw<800?2:1);
 c.width=Math.round(sw*sc);c.height=Math.round(sh*sc);const x=c.getContext('2d');x.drawImage(src,sx,sy,sw,sh,0,0,c.width,c.height);
 const d=x.getImageData(0,0,c.width,c.height),a=d.data,g=new Float32Array(a.length/4),hist=new Uint32Array(256);
 for(let i=0,j=0;i<a.length;i+=4,j++){const v=.299*a[i]+.587*a[i+1]+.114*a[i+2];g[j]=v;hist[v|0]++}
 // Helligkeit auf 1 % … 99 % strecken – hilft bei dunklen oder kontrastarmen Handyfotos
 const n=g.length;let lo=0,hi=255,acc=0;for(let k=0;k<256;k++){acc+=hist[k];if(acc>n*.01){lo=k;break}}acc=0;for(let k=255;k>=0;k--){acc+=hist[k];if(acc>n*.01){hi=k;break}}
 const span=Math.max(20,hi-lo),f=strong?1.25:1;
 for(let i=0,j=0;i<a.length;i+=4,j++){let v=(g[j]-lo)*255/span;v=(v-128)*f+128;a[i]=a[i+1]=a[i+2]=v<0?0:v>255?255:v}
 x.putImageData(d,0,0);
 const pc=document.createElement('canvas'),pad=Math.round(Math.max(16,c.height*.12));pc.width=c.width+2*pad;pc.height=c.height+2*pad;
 const px=pc.getContext('2d');px.fillStyle='#fff';px.fillRect(0,0,pc.width,pc.height);px.drawImage(c,pad,pad);return pc}
// Helle Namensleiste im Ausschnitt suchen (Zeilen/Spalten mit überwiegend hellem Grund) und nur diese zurückgeben.
// Große dunkle Flächen (Kartenrand, Bild) stören die Texterkennung sonst erheblich.
function nameBar(src){const w=src.width,h=src.height,x=src.getContext('2d'),a=x.getImageData(0,0,w,h).data,lum=(i)=>a[i];
 const rowL=[];for(let y=0;y<h;y++){let n=0,c=0;for(let xx=Math.round(w*.1);xx<w*.9;xx+=2){c++;if(lum((y*w+xx)*4)>165)n++}rowL.push(n/c)}
 let best=null;for(let y=0;y<h;y++){if(rowL[y]<.55)continue;let e=y;while(e+1<h&&rowL[e+1]>=.45)e++;const hh=e-y+1;
  if(hh>=h*.06&&hh<=h*.7&&(!best||hh>best[1]-best[0]))best=[y,e];y=e}
 if(!best)return null;const [y0,y1]=best,bh=y1-y0+1;
 const colL=[];for(let xx=0;xx<w;xx++){let n=0,c=0;for(let y=y0;y<=y1;y+=2){c++;if(lum((y*w+xx)*4)>165)n++}colL.push(n/c)}
 // von außen nach innen: weißen Rand überspringen, dann dunklen Kartenrand bzw. Hintergrund überspringen
 let x0=0,x1=w-1;while(x0<w*.3&&colL[x0]>.9)x0++;while(x0<w*.35&&colL[x0]<.6)x0++;
 while(x1>w*.7&&colL[x1]>.9)x1--;while(x1>w*.65&&colL[x1]<.6)x1--;
 const m=Math.round(bh*.08),out=document.createElement('canvas'),pad=Math.round(bh*.3);out.width=x1-x0+1+2*pad;out.height=bh+2*pad;
 const o=out.getContext('2d');o.fillStyle='#fff';o.fillRect(0,0,out.width,out.height);
 o.drawImage(src,x0,Math.max(0,y0-m),x1-x0+1,Math.min(h-y0+m,bh+2*m),pad,pad-m,x1-x0+1,Math.min(h-y0+m,bh+2*m));return out}
// Schwarz-Weiß mit automatischer Schwelle (Otsu) – Tesseract scheitert sonst an grauen Randflächen
function binarize(src){const c=document.createElement('canvas');c.width=src.width;c.height=src.height;const x=c.getContext('2d');x.drawImage(src,0,0);
 const d=x.getImageData(0,0,c.width,c.height),a=d.data,hist=new Float64Array(256);for(let i=0;i<a.length;i+=4)hist[a[i]]++;
 const n=a.length/4;let sum=0;for(let k=0;k<256;k++)sum+=k*hist[k];let sb=0,wb=0,best=0,th=128;
 for(let k=0;k<256;k++){wb+=hist[k];if(!wb)continue;const wf=n-wb;if(!wf)break;sb+=k*hist[k];const mb=sb/wb,mf=(sum-sb)/wf,v=wb*wf*(mb-mf)*(mb-mf);if(v>best){best=v;th=k}}
 for(let i=0;i<a.length;i+=4){const v=a[i]>th?255:0;a[i]=a[i+1]=a[i+2]=v}x.putImageData(d,0,0);return c}
// Rahmenlinie der Namensleiste entfernen (Tesseract hält umrandeten Text sonst für eine Grafik)
function stripBox(c){const w=c.width,h=c.height,a=c.getContext('2d').getImageData(0,0,w,h).data,blk=(x,y)=>a[(y*w+x)*4]<128;
 const rowB=y=>{let n=0;for(let x=0;x<w;x++)if(blk(x,y))n++;return n/w};let y0=0,y1=h-1;
 for(let y=0;y<h*.45;y++)if(rowB(y)>.4)y0=y+2;for(let y=h-1;y>h*.55;y--)if(rowB(y)>.4)y1=y-2;if(y1-y0<h*.25){y0=0;y1=h-1}
 const colB=x=>{let n=0;for(let y=y0;y<=y1;y++)if(blk(x,y))n++;return n/(y1-y0+1)};let x0=0,x1=w-1;
 for(let x=0;x<w*.08;x++)if(colB(x)>.6)x0=x+2;for(let x=w-1;x>w*.92;x--)if(colB(x)>.6)x1=x-2;
 const P=30,o=document.createElement('canvas');o.width=x1-x0+1+2*P;o.height=y1-y0+1+2*P;const ox=o.getContext('2d');ox.fillStyle='#fff';ox.fillRect(0,0,o.width,o.height);
 ox.drawImage(c,x0,y0,x1-x0+1,y1-y0+1,P,P,x1-x0+1,y1-y0+1);return o}
async function readName(canvas,lang,status){const bar=nameBar(canvas),ok=l=>l.some(t=>/[A-Za-zÄÖÜäöü]{3}/.test(t));let lines=[];
 // mehrere Aufbereitungen der Namensleiste lesen; welcher Text passt, entscheidet der Server-Abgleich
 if(bar)for(const v of [stripBox(binarize(bar)),binarize(bar),bar])lines=lines.concat(await ocrLines(v,lang,status));
 if(!ok(lines))lines=lines.concat(await ocrLines(binarize(canvas),lang,status));
 return lines.filter(t=>/[A-Za-zÄÖÜäöü]{3}/.test(t))}
function rotCanvas(src,deg){const r=deg*Math.PI/180,c=document.createElement('canvas'),w=src.width,h=src.height;
 c.width=Math.round(Math.abs(w*Math.cos(r))+Math.abs(h*Math.sin(r)));c.height=Math.round(Math.abs(w*Math.sin(r))+Math.abs(h*Math.cos(r)));
 const x=c.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,c.width,c.height);x.translate(c.width/2,c.height/2);x.rotate(r);x.drawImage(src,-w/2,-h/2);return c}
async function ocrLines(canvas,lang,status){const w=await ocrWorker(lang,status);status('Erkenne Text …');
 const r=await w.recognize(canvas);return r.data.text.split('\\n').map(s=>s.trim()).filter(s=>s.length>1)}
function scanDialog(target){const b=dlgOpen('📷 Karten scannen');
 P(b,'Karte gerade und formatfüllend vor einen ruhigen Hintergrund halten, gutes Licht, der Kartenname muss gut lesbar sein. Erkannt wird der Name (englisch oder deutsch); notfalls Set-Kürzel und Sammlernummer unten links.','hint');
 const row=$('div');b.append(row);const lang=$('select');lang.id='scanlang';[['eng','englische Karten'],['deu','deutsche Karten']].forEach(([v,t])=>{const o=$('option',t);o.value=v;lang.append(o)});
 try{lang.value=localStorage.getItem('scanlang')||'eng'}catch(e){};lang.onchange=()=>{try{localStorage.setItem('scanlang',lang.value)}catch(e){}};
 row.append('Kartensprache: ',lang,' ');
 const stage=$('div');stage.className='scanstage';b.append(stage);const status=$('div');status.className='hint';status.id='scanstatus';b.append(status);
 const res=$('div');res.id='scanres';b.append(res);const lst=$('div');lst.id='scanlist';b.append(lst);
 const say=t=>status.textContent=t;
 const handle=async lines=>{say('Suche passende Karte …');const m=await J('/api/scan_match',{lines:JSON.stringify(lines),lang:lang.value});showMatch(m,lines)};
 const showMatch=(m,lines)=>{res.innerHTML='';say('');
  if(m.error||!m.best){P(res,'Keine Karte erkannt. Bitte näher heran, gerader halten oder für mehr Licht sorgen.'+(lines&&lines.length?' (gelesen: „'+lines.slice(0,3).join(' / ')+'“)':''),'warn');return}
  const card=c=>{const d=$('div');d.className='scanhit';if(c.image){const im=$('img');im.src=c.image;im.alt=c.name;d.append(im)}
   const t=$('div');t.append($('b',c.name),$('div',(c.type||'')+(c.eur!=null?' · '+c.eur.toFixed(2).replace('.',',')+' €':'')),$('div','erkannt über: '+c.via+' ('+Math.round(c.score*100)+' %)'));
   const ok=$('button','✓ Übernehmen');ok.type='button';ok.className='primary';ok.onclick=()=>{const e=scanList.find(x=>x.name==c.name);if(e)e.qty++;else scanList.push({name:c.name,qty:1});scanSave();showList();res.innerHTML='';say('„'+c.name+'“ übernommen. Nächste Karte scannen.')};
   t.append(ok);d.append(t);return d};
  res.append(card(m.best));if(!m.sure)P(res,'Nicht ganz sicher. Bitte prüfen oder eine Alternative wählen:','hint');
  if(m.alts.length){const al=$('div');al.append('Andere Möglichkeiten: ');m.alts.slice(0,4).forEach(a=>{const bt=$('button',a.name);bt.type='button';bt.onclick=()=>showMatch({best:a,alts:[],sure:true});al.append(bt,' ')});res.append(al)}};
 const showList=()=>{lst.innerHTML='';if(!scanList.length)return;lst.append($('h4','Gescannt ('+scanList.reduce((s,x)=>s+x.qty,0)+' Karten)'));
  scanList.forEach((x,i)=>{const r=$('div');r.append(x.qty+'× ',cardName(x.name),' ');
   const pl=$('button','+');pl.type='button';pl.className='sw';pl.onclick=()=>{x.qty++;scanSave();showList()};
   const mi=$('button','−');mi.type='button';mi.className='sw';mi.onclick=()=>{if(--x.qty<=0)scanList.splice(i,1);scanSave();showList()};r.append(pl,mi);lst.append(r)});
  const toC=$('button','📦 Zur Sammlung hinzufügen');toC.type='button';toC.className='primary';toC.id='scantocoll';
  toC.onclick=async()=>{const r=await J('/api/collection_import',{text:scanList.map(x=>x.qty+' '+x.name).join('\\n'),mode:'add'});if(r.error){P(lst,r.error,'warn');return}
   collSum(r);scanList=[];scanSave();showList();say('✓ '+r.imported+' Karten zur Sammlung hinzugefügt.')};
  lst.append($('p'),toC);
  if(deck&&!deck.error){const toD=$('button','🛠 Ins aktuelle Deck');toD.type='button';toD.onclick=async()=>{for(const x of scanList)await addCardToDeck(x.name);scanList=[];scanSave();showList();say('Karten ins Deck übernommen (siehe Tab „Deck bauen“).')};lst.append(' ',toD)}
  const clr=$('button','Liste leeren');clr.type='button';clr.onclick=()=>{scanList=[];scanSave();showList()};lst.append(' ',clr)};
 const btns=$('div');btns.className='scanbtns';row.after(btns);
 // 1) Android-App: Kamera + Texterkennung auf dem Gerät (ML Kit)
 if(window.AndroidBridge&&AndroidBridge.hasLiveScanner&&AndroidBridge.hasLiveScanner()){const d=$('button','🔁 Dauerscan mit der Handykamera');d.type='button';d.className='primary';d.id='scannativeauto';
  d.onclick=()=>{res.innerHTML='';say('Kameraansicht wird geöffnet …');window.onNativeScanList=r=>{try{r=typeof r=='string'?JSON.parse(r):r}catch(e){r={error:String(r)}}
   if(r.error){say(r.error);return}let n=0;(r.cards||[]).forEach(c=>{const e=scanList.find(x=>x.name==c.name);if(e)e.qty+=c.qty;else scanList.push({name:c.name,qty:c.qty});n+=c.qty});
   scanSave();showList();say(n?n+' Karte(n) aus dem Dauerscan übernommen.':'Dauerscan beendet, keine Karte erfasst.')};
   AndroidBridge.scanLive(lang.value)};btns.append(d,' ')}
 if(nativeScan()){const a=$('button','📱 Mit der Handykamera scannen');a.type='button';if(!(window.AndroidBridge&&AndroidBridge.hasLiveScanner&&AndroidBridge.hasLiveScanner()))a.className='primary';
  a.onclick=()=>{res.innerHTML='';say('Kamera wird geöffnet …');window.onNativeScan=r=>{try{r=typeof r=='string'?JSON.parse(r):r}catch(e){r={error:String(r)}}
   if(r.error){say(r.error);return}const lines=(r.lines||[]).sort((p,q)=>p.top-q.top).map(l=>l.text);handle(lines)};AndroidBridge.scanCard()};btns.append(a,' ')}
 // 2) Foto aufnehmen bzw. Bild wählen (geht überall, auch ohne HTTPS)
 const fi=$('input');fi.type='file';fi.accept='image/*';fi.setAttribute('capture','environment');fi.id='scanfile';fi.style.display='none';
 const fb=$('button',nativeScan()?'🖼 Foto (Browser-Erkennung)':'📷 Foto aufnehmen / Bild wählen');fb.type='button';if(!nativeScan())fb.className='primary';fb.onclick=()=>fi.click();btns.append(fi,fb,' ');
 fi.onchange=async()=>{const f=fi.files[0];fi.value='';if(!f)return;stage.innerHTML='';res.innerHTML='';say('Bild wird geladen …');const img=new Image();img.src=URL.createObjectURL(f);await img.decode();
  const pv=$('img');pv.src=img.src;pv.className='scanprev';stage.append(pv);
  try{const W=img.naturalWidth,H=img.naturalHeight;
   // zuerst nur das obere Drittel (Name), bei Unsicherheit das ganze Bild
   let lines=await readName(prepCanvas(img,0,0,W,Math.round(H*.33)),lang.value,say);
   let m=await J('/api/scan_match',{lines:JSON.stringify(lines),lang:lang.value});
   if(!m.sure){const all=await ocrLines(prepCanvas(img,0,0,W,H),lang.value,say);lines=lines.concat(all);m=await J('/api/scan_match',{lines:JSON.stringify(lines),lang:lang.value})}
   if(!m.sure){const top=await ocrLines(prepCanvas(img,0,0,W,Math.round(H*.5),2400,true),lang.value,say);lines=top.concat(lines);m=await J('/api/scan_match',{lines:JSON.stringify(lines),lang:lang.value})}
   for(const deg of [-8,8,-4,4]){if(m.sure)break;say('Karte liegt schräg? Versuche gedreht ('+deg+'°) …');
    const rl=await ocrLines(rotCanvas(prepCanvas(img,0,0,W,Math.round(H*.5),1800,true),deg),lang.value,say);lines=rl.concat(lines);m=await J('/api/scan_match',{lines:JSON.stringify(lines),lang:lang.value})}
   showMatch(m,lines)}catch(e){say('Texterkennung fehlgeschlagen: '+(e&&e.message||e))}};
 // 3) Live-Kamera im Browser (nur über HTTPS oder auf diesem PC möglich)
 if(navigator.mediaDevices&&navigator.mediaDevices.getUserMedia&&window.isSecureContext){const lb=$('button','🎥 Live-Kamera');lb.type='button';btns.append(lb);
  lb.onclick=async()=>{stage.innerHTML='';let st;try{st=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment',width:{ideal:1920},height:{ideal:1080}}})}catch(e){say('Kamera nicht verfügbar: '+e.message);return}
   const wrap=$('div');wrap.className='scanlive';const v=document.createElement('video');v.autoplay=true;v.playsInline=true;v.muted=true;v.srcObject=st;const fr=$('div');fr.className='scanframe';wrap.append(v,fr);stage.append(wrap);
   const cap=$('button','⦿ Erkennen');cap.type='button';cap.className='primary';cap.id='scancap';const stop=$('button','Kamera aus');stop.type='button';
   const auto=$('button','🔁 Dauerscan starten');auto.type='button';auto.id='scanauto';const plus=$('button','+1 gleiche Karte');plus.type='button';plus.id='scanplus';plus.disabled=true;
   const flash=$('div');flash.className='scanflash';flash.id='scanflash';wrap.append(flash);
   const end=()=>{running=false;st.getTracks().forEach(t=>t.stop());stage.innerHTML=''};stop.onclick=end;stage.append(cap,' ',auto,' ',plus,' ',stop);
   // Dauerscan: etwa jede Sekunde den Namensbereich lesen; eine Karte zählt, wenn sie zweimal hintereinander sicher erkannt wurde.
   // Dieselbe Karte zählt erst wieder, nachdem sie aus dem Bild war (oder per „+1“).
   let running=false,last='',seen=0,added='',gone=0,count=0,plusName='';
   const beep=()=>{try{const a=new (window.AudioContext||window.webkitAudioContext)(),o=a.createOscillator(),g=a.createGain();o.frequency.value=880;g.gain.value=.08;o.connect(g);g.connect(a.destination);o.start();setTimeout(()=>{o.stop();a.close()},120)}catch(e){}
    try{navigator.vibrate&&navigator.vibrate(80)}catch(e){}};
   const addCard=n=>{const e=scanList.find(x=>x.name==n);if(e)e.qty++;else scanList.push({name:n,qty:1});scanSave();showList();count++;beep();
    flash.textContent='✓ '+n;flash.classList.add('on');setTimeout(()=>flash.classList.remove('on'),900);say('Dauerscan läuft, '+count+' Karte(n) erfasst. Nächste Karte in den Rahmen legen.')};
   plus.onclick=()=>{if(plusName)addCard(plusName)};
   const tick=async()=>{if(!running||!document.body.contains(wrap))return;const W=v.videoWidth,H=v.videoHeight;
    if(W){const fh=H*.86,fw=Math.min(W,fh*63/88*1.18),fx=(W-fw)/2,fy=(H-fh)/2;
     try{const ny=Math.max(0,fy-fh*.04);const lines=await readName(prepCanvas(v,fx,ny,fw,fh*.2),lang.value,()=>{});const m=lines.length?await J('/api/scan_match',{lines:JSON.stringify(lines),lang:lang.value}):{sure:false};
      if(m.sure&&m.best){gone=0;const n=m.best.name;seen=(n==last)?seen+1:1;last=n;
       if(seen>=2&&n!=added){added=n;plusName=n;plus.disabled=false;plus.textContent='+1 '+n;addCard(n)}}
      else{seen=0;last='';if(++gone>=2)added=''}}catch(e){say('Texterkennung fehlgeschlagen: '+(e&&e.message||e));running=false;auto.textContent='🔁 Dauerscan starten'}}
    if(running)setTimeout(tick,350)};
   auto.onclick=async()=>{running=!running;auto.textContent=running?'⏸ Dauerscan anhalten':'🔁 Dauerscan starten';res.innerHTML='';
    if(running){say('Dauerscan läuft. Karte in den Rahmen legen, Name oben im hellen Streifen.');try{await ocrWorker(lang.value,say)}catch(e){say(String(e&&e.message||e));running=false;return}tick()}
    else say('Dauerscan angehalten, '+count+' Karte(n) erfasst.')};
   const obs=new MutationObserver(()=>{if(!document.body.contains(wrap)){st.getTracks().forEach(t=>t.stop());obs.disconnect()}});obs.observe(document.body,{childList:true,subtree:true});
   cap.onclick=async()=>{const W=v.videoWidth,H=v.videoHeight;if(!W)return;res.innerHTML='';const fh=H*.86,fw=Math.min(W,fh*63/88*1.18),fx=(W-fw)/2,fy=(H-fh)/2;
    try{const ny=Math.max(0,fy-fh*.04);let lines=await readName(prepCanvas(v,fx,ny,fw,fh*.2),lang.value,say);let m=await J('/api/scan_match',{lines:JSON.stringify(lines),lang:lang.value});
     if(!m.sure){lines=lines.concat(await ocrLines(prepCanvas(v,fx,fy,fw,fh),lang.value,say));m=await J('/api/scan_match',{lines:JSON.stringify(lines),lang:lang.value})}
     showMatch(m,lines)}catch(e){say('Texterkennung fehlgeschlagen: '+(e&&e.message||e))}}}}
 else if(!nativeScan())P(btns,'Live-Kamera im Browser nur über HTTPS (Server-Betrieb) oder direkt am PC möglich; „Foto aufnehmen“ funktioniert überall.','hint');
 showList()}
function quickDecks(list){const sel=E('opensel'),cur=sel.value;sel.innerHTML='';
 const o0=$('option',list.length?'– Deck wählen ('+list.length+' gespeichert) –':'– noch keine Decks gespeichert –');o0.value='';sel.append(o0);
 list.forEach(d=>{const o=$('option',d.name+(d.commander&&d.commander!=d.name?' · '+d.commander:'')+' ('+d.count+' Karten, '+d.saved_at+')');o.value=d.id;sel.append(o)});sel.value=cur;
 const r=E('recent');r.innerHTML='';if(!list.length)return;
 const box=$('div');box.className='recentbox';box.append($('b','Zuletzt gespeichert: '));
 [...list].sort((a,b)=>(b.saved_at||'').localeCompare(a.saved_at||'')).slice(0,5).forEach(d=>{const bt=$('button','📂 '+d.name);bt.type='button';
  bt.title=(d.commander||'')+' · '+d.count+' Karten · '+d.saved_at;bt.onclick=async()=>useMine(await J('/api/deck_get?id='+d.id));box.append(bt,' ')});r.append(box)}
E('scanbtn').onclick=()=>scanDialog('sammlung');
E('openbtn').onclick=async()=>{const v=E('opensel').value;if(!v){E('opensel').focus();return}useMine(await J('/api/deck_get?id='+v))};
E('opensel').onchange=()=>{if(E('opensel').value)E('openbtn').onclick()};
async function myDecks(list){list=list||await J('/api/decks');
 if(list.error){E('mydecks').textContent=list.error;return}
 quickDecks(list);
 E('mycount').textContent=list.length?'('+list.length+' gespeichert)':'';
 const o=E('mydecks');o.innerHTML='';const c=E('oppdecks');c.innerHTML='';
 if(!list.length){o.append($('p','Noch keine Decks gespeichert.'));return}
 c.append($('span','Eigene Decks als Gegner: '));
 const t=$('table');o.append(t);
 const hr=t.insertRow();['Deck','Commander','Karten','Bracket','Gespeichert',''].forEach(x=>hr.append($('th',x)));
 for(const d of list){const tr=t.insertRow();[d.name,d.commander||'–',d.count].forEach(x=>tr.insertCell().textContent=x);
  const bcell=tr.insertCell();bcell.className='dbr';bcell.append(brBadge(d.bracket,d.bracket_est));tr.insertCell().textContent=d.saved_at;
  const a=tr.insertCell();const get=()=>J('/api/deck_get?id='+d.id);
  const b1=$('button','Mein Deck');b1.type='button';b1.onclick=async()=>useMine(await get());
  const b2=$('button','Gegner');b2.type='button';b2.onclick=async()=>useOpp(await get(),E('impres'));
  const bv=$('button','Versionen');bv.type='button';bv.onclick=()=>versionsDialog(d.id);
  const bs=$('button',d.shared?'🔗 Geteilt':'Teilen');bs.type='button';bs.onclick=()=>shareDialog(d);
  const bx=$('button','📤 Senden');bx.type='button';bx.className='dsend';bx.onclick=()=>sendDialog(d);
  const bp=$('button',d.public?'🌍 Veröffentlicht':'🌍 Veröffentlichen');bp.type='button';bp.className='dpub srvonly';bp.hidden=!ME.server;
  bp.title=d.public?'Steht in der Galerie. Antippen zieht es zurück':'In die öffentliche Galerie dieses Servers stellen';
  bp.onclick=async()=>{const r=await J('/api/deck_public',{id:d.id,on:d.public?0:1});if(r.error){bp.textContent='⚠ '+r.error;return}myDecks()};
  const b3=$('button','Löschen');b3.type='button';
  b3.onclick=async()=>{if(b3.textContent!='Wirklich?'){b3.textContent='Wirklich?';return}myDecks(await J('/api/deck_delete',{id:d.id}))};
  a.append(b1,b2,bv,bs,bx,bp,b3);
  const ch=$('button',d.name);ch.type='button';ch.title=d.commander||'';ch.onclick=async()=>useOpp(await get());c.append(ch)}}
myDecks();oppInfo();
// ---- Decks senden: im Server-Betrieb an andere Benutzer (Postfach), sonst als Link an eine andere Manaschmiede
async function sendDialog(d){await MEP;const b=dlgOpen('Deck senden: '+d.name);
 if(ME.server){const nl=await J('/api/user_names');const names=nl.names||[];
  if(!names.length){P(b,'Auf diesem Server gibt es noch keine anderen Benutzer. Der Administrator kann sie unter „Benutzer verwalten“ anlegen.','hint')}
  else{P(b,'Das Deck landet im Postfach des Empfängers („📥 Erhaltene Decks“ unter Meine Decks) und kann dort übernommen oder abgelehnt werden. Dein eigenes Deck bleibt unverändert.','hint');
   const to=$('select');to.id='sendto';names.forEach(n=>{const op=$('option',n);op.value=n;to.append(op)});
   const msg=$('input');msg.id='sendmsg';msg.size=40;msg.maxLength=300;msg.placeholder='Nachricht (optional), z. B. „Probier das mal gegen Atraxa“';
   const go=$('button','📤 Senden');go.type='button';go.className='primary';go.id='sendgo';const res=$('div');
   go.onclick=async()=>{const r=await J('/api/deck_send',{id:d.id,to:to.value,msg:msg.value});res.innerHTML='';
    if(r.error)P(res,r.error,'warn');else{P(res,'✓ An '+r.to+' gesendet.');go.disabled=true}};
   const l1=$('div');l1.append('An: ',to);b.append(l1,msg,$('br'),go,res)}
  P(b,'Für Leute ohne Zugang zu diesem Server: „Teilen“ erzeugt einen Link, den sie in ihrer eigenen Manaschmiede unter „Meine Decks“ importieren können.','hint');return}
 P(b,'Hier gibt es keine Benutzerkonten. Du sendest deshalb einen Link: Die andere Person öffnet ihn im Browser oder fügt ihn in ihrer Manaschmiede unter „📂 Meine Decks → Deck importieren“ in das Link-Feld ein. Das Deck wird dann komplett übernommen.','hint');
 P(b,'Der Link funktioniert nur, solange deine Manaschmiede läuft und für die andere Person erreichbar ist (gleiches Heimnetz mit „im Netzwerk starten“ oder Server).','hint');
 const res=$('div');b.append(res);let r=await J('/api/deck_share',{id:d.id,on:1});if(r.error){P(res,r.error,'warn');return}
 const url=location.origin+r.path;const inp=$('input');inp.id='sendlink';inp.readOnly=true;inp.value=url;inp.size=48;
 const cp=$('button','Link kopieren');cp.type='button';cp.onclick=()=>{try{navigator.clipboard.writeText(url);cp.textContent='✓ kopiert'}catch(e){inp.select()}};
 res.append(inp,' ',cp);if(navigator.share){const sh=$('button','Senden über …');sh.type='button';sh.onclick=()=>navigator.share({title:'Deck: '+d.name,text:'Mein Commander-Deck „'+d.name+'“ aus der Manaschmiede',url:url}).catch(()=>{});res.append(' ',sh)}
 const qr=$('div');qr.className='qrbox';res.append($('br'),qr);roomQR(qr,url);myDecks()}
async function inboxShow(){await MEP;const o=E('inbox');if(!o)return;o.innerHTML='';if(!ME.server)return;
 const r=await J('/api/inbox');const it=r.items||[];const nb=document.querySelector('#mainnav a[data-v=decks]');
 if(nb)nb.dataset.badge=it.length?String(it.length):'';const mb2=document.querySelector('#mobmore a[data-v=decks]');if(mb2)mb2.dataset.badge=it.length?String(it.length):'';const mbb=E('mobmorebtn');if(mbb)mbb.dataset.badge=it.length?String(it.length):'';if(!it.length)return;
 const box=$('div');box.className='roombox inboxbox';box.append($('h4','📥 Erhaltene Decks ('+it.length+')'));
 it.forEach(x=>{const d=$('div');d.className='inboxitem';d.append($('b',x.name),' · '+(x.commander||'ohne Commander')+' · '+x.cards+' Karten · von ',$('b',x.from),' · '+x.sent_at);
  if(x.msg){const m=$('div','„'+x.msg+'“');m.className='hint';d.append(m)}
  const ac=$('button','✔ Übernehmen');ac.type='button';ac.className='primary inacc';ac.onclick=async()=>{const q=await J('/api/inbox_accept',{id:x.id});if(q.error){P(d,q.error,'warn');return}
   await myDecks();await inboxShow();P(E('inbox'),'✓ „'+q.name+'“ ist jetzt unter deinen Decks.','hint')};
  const dc=$('button','Ablehnen');dc.type='button';dc.className='indec';dc.onclick=async()=>{await J('/api/inbox_decline',{id:x.id});inboxShow()};
  d.append($('br'),ac,' ',dc);box.append(d)});o.append(box)}
inboxShow();setInterval(()=>{if(document.visibilityState=='visible')inboxShow()},60000);

// ---- Combos (Commander Spellbook)
function comboList(o,rep,title){const box=$('div');o.append(box);box.append($('h4',title));
 if(rep.error){P(box,rep.error,'warn');return}
 P(box,rep.count+' Combos gefunden, davon '+rep.win_count+' spielentscheidend · Bracket-Schätzung mit Combos: '+rep.bracket,'hint');
 const sb=rep.spellbook||{};
 if(sb.error)P(box,sb.error,'hint');
 else if(sb.name){const why=[sb.game_changers.length?sb.game_changers.length+' Game Changer':'',sb.two_card_combos?sb.two_card_combos+' Zwei-Karten-Combo(s)':'',
   sb.mass_land_denial.length?'Massen-Landzerstörung':'',sb.extra_turns.length?'Extra-Züge':'',sb.locks?'Lock-Combos':'',sb.banned.length?'gebannte Karten':''].filter(Boolean);
  P(box,'Einstufung von Commander Spellbook: '+sb.name+(why.length?' ('+why.join(', ')+')':''),'big')}
 if(!rep.combos.length)P(box,'Keine bekannten Combos im Deck.');
 for(const c of rep.combos.slice(0,25)){const d=$('div');d.className='combo'+(c.win?' win':'');box.append(d);
  const t=$('div');const tb=$('b');c.cards.forEach((u,k)=>{if(k)tb.append(' + ');tb.append(cardName(u.name))});t.append(tb);d.append(t);
  d.append($('div','Ergebnis: '+c.produces.join(', ')));
  if(c.requires.length)d.append($('div','Benötigt zusätzlich: '+c.requires.join(', ')));
  d.append($('div','Mana: '+(c.mana||'–')+(c.mana_value?' · Mana-Wert gesamt '+c.mana_value:'')+' · Einstufung (Spellbook): '+c.tag_name));
  const w=$('div');w.append('Zusammen bis Zug 6 / 8 / 10: '+c.by6+' % / '+c.by8+' % / '+c.by10+' % ');
  const b=$('span');b.className='bar';const i=$('i');i.style.width=(c.by10||0)+'%';b.append(i);w.append(b);d.append(w);
  if(c.prereq)P(d,'Voraussetzungen: '+c.prereq,'hint');
  const l=$('a','Ablauf bei Commander Spellbook',c.url);d.append(l)}
 if(rep.almost&&rep.almost.length){box.append($('h4','Fast vollständig, es fehlt eine Karte ('+rep.almost_count+')'));
  P(box,'Combos, denen genau eine Karte fehlt (passend zur Farbidentität). Du kannst sie bewusst ergänzen oder bewusst weglassen.','hint');
  for(const c of rep.almost.slice(0,12)){const d=$('div');d.className='combo'+(c.win?' win':'');box.append(d);
   const t=$('div');const tb=$('b');c.cards.forEach((u,k)=>{if(k)tb.append(' + ');const nm=cardName(u.name);if(c.missing.includes(u.name))nm.classList.add('miss');tb.append(nm)});t.append(tb);d.append(t);
   d.append($('div','Fehlt: '+c.missing.join(', ')+' · Ergebnis: '+c.produces.join(', ')+' · Einstufung: '+c.tag_name));
   if(title=='Dein Deck'&&deck&&!deck.error){const b=$('button','➕ '+c.missing[0]+' ins Deck');b.type='button';
    b.onclick=async()=>{await addCardToDeck(c.missing[0]);b.disabled=true;b.textContent='✓ '+c.missing[0]+' ist jetzt im Deck'};d.append(b)}
   d.append(' ',$('a','Ablauf',c.url))}}}
const qBtn=k=>{const b=$('button','?');b.type='button';b.className='qh';b.dataset.h=k;return b};
const h3q=(t,k)=>{const h=$('h3',t);h.append(qBtn(k));return h};
async function loadCombos(){const o=E('combos');o.innerHTML='';o.append(h3q('Combos im Vergleich','combos'));
 P(o,'Suche Combos bei Commander Spellbook ...','hint');
 const r=await J('/api/combos',Object.assign(mineP(),oppP()));
 o.innerHTML='';o.append(h3q('Combos im Vergleich','combos'));
 P(o,'Quelle: Commander Spellbook. Wahrscheinlichkeiten: Simulation von 1500 Starthänden je Deck (London-Mulligan, ein Land pro Zug, Ramp und Tutoren berücksichtigt, ohne Störung durch den Gegner).','hint');
 const cols=$('div');cols.className='cols';o.append(cols);
 comboList(cols,r.mine,'Dein Deck');if(r.theirs)comboList(cols,r.theirs,'Gegner: '+(r.opp_name||''))}

// ---- Direktes Duell über Forge
let duelTimer=null;
let DUELGEN=0;
async function duelBox(){const gen=++DUELGEN;const o=E('duel');o.innerHTML='';o.append(h3q('Direktes Duell (Regel-Engine Forge)','duell'));
 P(o,'Dein Deck gegen „'+opp.name+'“: Beide Decks spielen mehrere komplette Partien Commander 1-gegen-1 (40 Leben, Commander-Schaden, Commander-Steuer), KI gegen KI. Jede Karte wird mit ihren echten Fähigkeiten ausgeführt, auch Combos.','hint');
 const man=$('div');man.className='savebox';man.id='manualbox';o.append(man);
 man.append($('b','🃏 Selbst gegeneinander spielen'),' ',pvBtn('Im Browser: Dein Deck gegen „'+opp.name+'“',()=>pvStart(true),'primary'));
 P(man,'Du spielst beide Seiten am Spieltisch im Browser: Starthand und Mulligan, Ziehen, Ausspielen, Angriffe, Leben und Commander-Schaden, mit Protokoll und Statistik. Regeln prüft der Spieltisch nicht.','hint');
 const st=await J('/api/forge');await MEP;if(gen!=DUELGEN)return;
 if(!ME.server&&st.ready){const fb=pvBtn('🖥 In Forge selbst gegen die KI spielen',async()=>{fb.disabled=true;const r=await J('/api/forge_play',Object.assign(mineP(),oppP(),{deck_name:deck&&deck.name||''}));fb.disabled=false;
   const msg=E('forgeplaymsg')||man.appendChild(Object.assign($('p'),{id:'forgeplaymsg'}));
   msg.className=r.error?'warn':'hint';msg.textContent=r.error||('Forge '+(r.started?'startet gleich (beim ersten Mal etwa eine Minute)':'ist vorbereitet')+'. Die Decks liegen dort unter Commander: '+r.decks.join(' und ')+
    '. In Forge links „Commander“ wählen, bei Spieler 1 dein Deck, bei Spieler 2 „KI“ und den Gegner, dann „Spiel starten“. Forge prüft dabei alle Regeln.')});
  man.append(' ',fb)}
 const cfg=$('div');o.append(cfg);
 if(ME.server){P(cfg,st.ready?'Forge ist auf dem Server bereit.':'Forge ist auf dem Server nicht eingerichtet. Bitte den Administrator fragen.',st.ready?'hint':'warn');if(!st.ready)return}
 else{
 const inp=$('input');inp.size=60;inp.placeholder='Forge-Ordner, z. B. C:\\Forge';inp.value=st.dir||'';cfg.append('Forge-Ordner: ',inp);
 const sv=$('button','Speichern');sv.type='button';cfg.append(sv);
 P(cfg,st.message,st.ready?'hint':'warn');
 if(!st.ready)P(cfg,'Einmalig nötig: Java 17+ (z. B. adoptium.net) und Forge (github.com/Card-Forge/forge/releases, Archiv entpacken). Dann hier den entpackten Ordner angeben.','hint');
 sv.onclick=async()=>{await J('/api/forge_dir',{dir:inp.value});duelBox()};
 if(!st.ready)return}
 const run=$('div');o.append(run);
 const mode=$('select');mode.id='duelmode';[['2','1 gegen 1'],['3','Commander-Runde zu dritt'],['4','Commander-Runde zu viert']].forEach(([v,t])=>{const op=$('option',t);op.value=v;mode.append(op)});
 const xb=$('div');xb.style.display='none';
 run.append('Spielform: ',mode,xb);
 const [pl,dl,all]=await Promise.all([J('/api/precons?ci='+encodeURIComponent(deck.ci||'')),J('/api/decks'),preconsAll()]);if(gen!=DUELGEN)return;
 const decks=Array.isArray(dl)?dl:(dl.decks||[]);
 const mkSel=(id,def)=>{const s=$('select');s.id=id;fillPreconSelect(s,all,{match:pl.slice(0,8),prefix:'precon:',decks:decks});
  if(s.options.length>def)s.selectedIndex=def;return s};
 const s3=mkSel('duelp3',1),s4=mkSel('duelp4',2),l4=$('div','Spieler 4: '),xh=$('p');xh.className='hint';
 xb.append($('div','Spieler 3: '),s3,l4,s4,xh);
 mode.onchange=()=>{const m=+mode.value;xb.style.display=m>2?'':'none';l4.style.display=s4.style.display=m==4?'':'none';
  xh.textContent=(m==4?'Vier Decks am Tisch: dein Deck, der oben gewählte Gegner und zwei weitere.':'Drei Decks am Tisch: dein Deck, der oben gewählte Gegner und ein weiterer.')+
   ' Eine Partie dauert hier meist 1–10 Minuten; nach 15 Minuten wertet Forge sie als Unentschieden.';
  if(m>2&&+n.value>5)n.value='3'};
 run.append($('br'));
 {const li=await J('/api/lab_list');if(gen!=DUELGEN)return;const ai=$('select');ai.id='duelai';(li.profiles||['Default']).forEach(x=>ai.append(new Option(x,x)));const pil=labPilot();if(pil)ai.value=pil;
  const dmc=$('select');dmc.id='duelmc';[['off','aus (ca. 15 s je Partie)'],['on','an (ca. 30 s je Partie)'],['max','maximal (ca. 50 s je Partie)']].forEach(([v,t])=>dmc.append(new Option(t,v)));
  const kd=$('details');kd.id='duelki';kd.append($('summary','⚙ KI-Einstellungen'+(pil?' (KI-Pilot: '+pil+')':'')),'KI-Profil deines Decks: ',ai,'  Vorausschau: ',dmc);
  P(kd,'Die Gegner spielen mit „Default“. Mit Vorausschau prüft die KI mögliche Züge vorher durch. Sie spielt dann stärker, braucht aber länger. Zeiten gelten für 1 gegen 1; Runden zu dritt oder viert dauern deutlich länger.','hint');run.append(kd)}
 const n=$('input');n.size=4;n.type='number';n.min=1;n.max=ME.max_games||100;n.value=String(Math.min(10,ME.max_games||10));
 run.append('Anzahl Partien (max. '+(ME.max_games||100)+'): ',n,' ');
 const go=$('button','Duell starten');go.type='button';run.append(go);
 const res=$('div');o.append(res);
 go.onclick=async()=>{go.disabled=true;res.innerHTML='';
  const j=await J('/api/duel_start',Object.assign(mineP(),oppP(),{games:n.value,extra:mode.value=='4'?s3.value+','+s4.value:mode.value=='3'?s3.value:'',ai:E('duelai').value,mc:E('duelmc').value}));
  if(j.error){P(res,j.error,'warn');go.disabled=false;return}
  const stop=$('button','Abbrechen');stop.type='button';run.append(stop);
  stop.onclick=()=>J('/api/duel_cancel',{job:j.job});
  clearInterval(duelTimer);
  const poll=async()=>{const s=await J('/api/duel_status?job='+j.job);showDuel(res,s);
   if(s.done){clearInterval(duelTimer);go.disabled=false;stop.remove()}};
  duelTimer=setInterval(poll,2500);poll()};
 labBox(o,gen)}
// ---------- Kaufassistent: Bedarf je Händler, Druck/Foil, Budget, Precon-Check, gekauft → Sammlung
let BUY=null,BUYP=null;
const eur=v=>v==null?'–':v.toFixed(2).replace('.',',')+' €',nK=n=>n+(n==1?' Karte':' Karten');
async function buyInit(pre){const box=E('buybox');if(!box)return;const c=E('buyctl');c.innerHTML='';
 const src=$('select');src.id='buysrc';src.append(new Option('Alle gespeicherten Decks','shopping'),new Option('Wunschliste','wish'));
 if(typeof deck!='undefined'&&deck&&deck.export)src.append(new Option('Deck im Editor: '+(deck.name||deck.commander||'ohne Namen'),'deck'));
 const dl=await J('/api/decks');(Array.isArray(dl)?dl:(dl.decks||[])).forEach(d=>src.append(new Option('Deck: '+d.name,'deck_id:'+d.id)));
 const bud=$('input');bud.id='buybudget';bud.size=6;bud.placeholder='z. B. 50';bud.inputMode='decimal';
 const shop=$('select');shop.id='buyshop';shop.append(new Option('Cardmarket','cm'),new Option('Trader-online','to'));
 const own=$('input');own.type='checkbox';own.id='buyowned';own.checked=true;const ol=$('label');ol.append(own,' Eigene Sammlung abziehen');
 const go=$('button','🧭 Kaufplan erstellen');go.type='button';go.className='primary';go.id='buygo';
 c.append('Was kaufen? ',src,'  Budget (€, optional): ',bud,'  Standard-Händler: ',shop,' ',ol,' ',go);
 try{const s=JSON.parse(localStorage.getItem('buyset')||'{}');if(s.budget)bud.value=s.budget;if(s.shop)shop.value=s.shop}catch(e){}
 if(pre&&pre.source){src.value=pre.source}
 go.onclick=()=>{try{localStorage.setItem('buyset',JSON.stringify({budget:bud.value,shop:shop.value}))}catch(e){}buyLoad()};
 if(pre)buyLoad()}
function buyParams(){const v=E('buysrc').value;const p={budget:E('buybudget').value,default_shop:E('buyshop').value,owned:E('buyowned').checked?1:0};
 if(v=='deck')Object.assign(p,{source:'deck',list:deck.export,commander:deck.commander||'',deck_name:deck.name||''});
 else if(v.startsWith('deck_id:'))Object.assign(p,{source:'deck_id',deck_id:v.slice(8)});else p.source=v;return p}
async function buyLoad(extra,url){const o=E('buyres');if(!extra)o.innerHTML='<p class=hint>Berechne …</p>';
 const r=await J(url||'/api/buy_plan',Object.assign(buyParams(),extra||{}));BUY=r;buyRender(r)}
function buyRender(r){const o=E('buyres');o.innerHTML='';if(r.error){P(o,r.error,'warn');return}
 if(r.added)P(o,'✔ '+nK(r.added)+' in die Sammlung übernommen.','tag');
 const act=r.items.filter(x=>!x.skip);
 if(!r.items.length){P(o,'Für „'+r.title+'“ fehlt keine Karte.','tag');return}
 const sm=$('div');sm.className='buysum';sm.id='buysum';o.append(sm);
 sm.append($('b',nK(act.reduce((a,x)=>a+x.qty,0))+' für '+eur(r.total)),' · '+r.title);
 Object.entries(r.shops).forEach(([k,s])=>sm.append($('div',SHOPS[k].name+': '+nK(s.cards)+', '+eur(s.total)+(s.noprice?' (+'+s.noprice+' ohne Preis)':''))));
 if(r.budget){const b=$('div');b.id='buybud';b.className=r.over?'warn':'tag';
  b.textContent='Budget '+eur(r.budget)+': '+(r.over?eur(r.in_budget)+' passen hinein, '+nK(act.filter(x=>!x.fits).length)+' ('+eur(r.over)+' darüber) sind markiert. Karten, die in mehreren Decks stecken, haben Vorrang, danach die günstigsten.':'alles passt ('+eur(r.budget-r.total)+' übrig).');sm.append(b)}
 if(r.noprice)P(sm,nK(r.noprice)+' ohne bekannten Preis sind nicht eingerechnet.','hint');
 // Tabelle
 const t=$('table');t.id='buytab';t.className='duel';o.append(t);const h=t.insertRow();
 const all=$('input');all.type='checkbox';all.title='Alle auswählen';all.onchange=()=>t.querySelectorAll('.buyck').forEach(c=>c.checked=all.checked);
 const th0=$('th');th0.append(all);h.append(th0);['Anz.','Karte','Druck','Händler','Preis','Summe',''].forEach(x=>h.append($('th',x)));
 r.items.forEach(x=>{const tr=t.insertRow();tr.dataset.name=x.name;if(x.skip)tr.className='buyskip';else if(!x.fits)tr.className='buyover';
  const ck=$('input');ck.type='checkbox';ck.className='buyck';ck.disabled=x.skip;tr.insertCell().append(ck);
  tr.insertCell().textContent=x.qty;const nc=tr.insertCell();nc.append(cardName(x.name));if(x.decks.length>1)nc.append($('div',x.decks.length+' Decks: '+x.decks.join(', ')));
  if(!x.fits&&!x.skip)nc.append($('div','über Budget'));
  const pc=tr.insertCell();const pb=$('button',(x.print?x.print.set_code+' #'+x.print.number:'beliebig')+(x.foil?' ✨':''));pb.type='button';pb.className='buyprint';
  pb.title=x.print?x.print.set_name:'Günstigste Druckversion, zum Festlegen klicken';pb.onclick=()=>buyPrint(x);pc.append(pb);
  const sc=tr.insertCell();const ss=$('select');ss.className='buyshopsel';ss.append(new Option('CM','cm'),new Option('TO','to'));ss.value=x.shop;
  ss.onchange=()=>buyLoad({name:x.name,shop:ss.value},'/api/buy_set');sc.append(ss);
  tr.insertCell().textContent=eur(x.price)+(x.src=='cheapest'&&x.print?' *':'');tr.insertCell().textContent=eur(x.total);
  const lc=tr.insertCell();const url=x.shop=='cm'?(x.cm||SHOPS.cm.search(x.name)):SHOPS.to.search(x.name);
  const a=shopA(x.shop,url,x.shop=='cm'?(x.print||x.foil?'Produktseite des gewählten Drucks'+(x.foil?' (Foil)':''):'Günstigste Druckversion auf Cardmarket'):'Bei Trader-online suchen');lc.append(a,' ');
  const sk=$('button',x.skip?'↺':'✕');sk.type='button';sk.className='buyskipbtn';sk.title=x.skip?'Wieder einplanen':'Nicht kaufen (z. B. schon bestellt)';
  sk.onclick=()=>buyLoad({name:x.name,skip:x.skip?0:1},'/api/buy_set');lc.append(sk)});
 // Je Händler
 const hd=$('div');hd.id='buyshops';o.append(hd);
 if(r.shops.cm){const b=$('div');b.className='savebox';b.append($('b','Cardmarket: '));
  if(r.cm_any_text){const cb=$('button','🛒 Liste kopieren & Wants öffnen');cb.type='button';cb.id='buycmwants';cb.onclick=()=>cmWants(r.cm_any_text,cb);b.append(cb,' ',$('span',nK(r.cm_any_text.split('\\n').length)+' mit beliebigem Druck'))}
  if(r.cm_specific)P(b,nK(r.cm_specific)+' mit festgelegtem Druck oder Foil bitte einzeln über den CM-Link in der Tabelle in den Warenkorb legen, weil die Wants-Liste keine Drucke kennt.','hint');hd.append(b)}
 if(r.shops.to){const b=$('div');b.className='savebox';const tl=act.filter(x=>x.shop=='to'&&x.fits);b.append($('b','Trader-online: '),nK(tl.length)+'. Über die TO-Links in der Tabelle suchen und in den Warenkorb legen. ');
  const cb=$('button','Liste kopieren');cb.type='button';cb.id='buytocopy';cb.onclick=async()=>{await copyText(tl.map(x=>x.qty+' '+x.name).join('\\n'));cb.textContent='✓ kopiert'};b.append(cb);hd.append(b)}
 // Precon-Check
 if(r.precons.length){const d=$('details');d.id='buyprecons';d.className='subbox';keepOpen(d);d.append($('summary','📦 Precon-Check: '+r.precons.length+' Precons enthalten mehrere der fehlenden Karten'));
  P(d,'Manchmal ist ein Precon günstiger als die Einzelkarten. Vergleiche den Kaufpreis beim Händler mit dem Wert der fehlenden Karten.','hint');
  r.precons.forEach(pc=>{const row=$('div');row.className='buypc';row.append($('b',pc.name),' ('+pc.set+') enthält '+pc.covered+' fehlende Karten im Wert von '+eur(pc.value)+' · Einzelkartenwert des ganzen Precons '+eur(pc.precon_value)+' ',sealedLinks(pc.name));
   row.append($('div',pc.cards.join(', ')));d.append(row)});o.append(d)}
 // Abschluss
 const f=$('p');const done=$('button','✔ Ausgewählte als gekauft in die Sammlung');done.type='button';done.id='buydone';
 done.onclick=async()=>{const sel=[...t.querySelectorAll('tr')].filter(tr=>tr.querySelector('.buyck:checked')).map(tr=>{const x=r.items.find(i=>i.name==tr.dataset.name);
   return {name:x.name,qty:x.qty,set_code:x.print?x.print.set_code:'',number:x.print?x.print.number:'',foil:x.foil}});
  if(!sel.length){alert('Bitte zuerst gekaufte Karten ankreuzen.');return}buyLoad({items:JSON.stringify(sel)},'/api/buy_done')};
 const cs=$('button','CSV herunterladen');cs.type='button';cs.id='buycsv';cs.onclick=async()=>{const x=await J('/api/buy_csv',buyParams());if(x.csv)download(x.file,x.csv)};
 const px=$('button','🖨 Als Proxy drucken');px.type='button';px.id='buyproxy';px.title='Kopien zum Testen, bis die echten Karten da sind';px.onclick=()=>proxyStudio({text:act.map(x=>x.qty+' '+x.name+(x.print?' ('+x.print.set_code+') '+x.print.number:'')).join('\\n')});
 f.append(done,' ',cs,' ',px);o.append(f);
 P(o,'Preise: Cardmarket-Preisliste (Trend) bzw. Scryfall; * = Preis der günstigsten Druckversion, weil für den gewählten Druck keiner vorliegt. Trader-online liefert keine Preisliste, dort gilt der Preis im Shop. Anmeldung und Kauf laufen direkt beim Händler.','hint')}
async function buyPrint(x){const b=dlgOpen('Druck für '+x.name);const any=$('button','Beliebiger Druck (günstigster)');any.type='button';any.id='buyany';
 any.onclick=()=>{closeSwap();buyLoad({name:x.name,set_code:'',number:'',foil:0},'/api/buy_set')};b.append(any);
 const l=$('div');l.id='buyprints';b.append(l);P(l,'Lade Drucke …','hint');const r=await J('/api/prints?name='+encodeURIComponent(x.name));l.innerHTML='';
 if(r.error){P(l,r.error,'warn');return}if(r.warn)P(l,r.warn,'hint');
 const t=$('table');l.append(t);r.prints.forEach(pr=>{const tr=t.insertRow();tr.className='buyprow';tr.insertCell().textContent=pr.set_name+' ('+pr.set_code+' #'+pr.number+')';tr.insertCell().textContent=(pr.released||'').slice(0,4);
  const c=tr.insertCell();const mk=(foil,price)=>{const bt=$('button',(foil?'✨ Foil ':'Normal ')+eur(price));bt.type='button';bt.className=foil?'buyfoil':'buynorm';
   bt.onclick=()=>{closeSwap();buyLoad({name:x.name,set_code:pr.set_code,number:pr.number,foil:foil?1:0},'/api/buy_set')};c.append(bt,' ')};
  if(pr.finishes.includes('nonfoil'))mk(0,pr.eur);if(pr.finishes.includes('foil')||pr.finishes.includes('etched'))mk(1,pr.eur_foil)})}
// ---------- Messlabor: Kartentausch oder KI-Profil per Forge messen, mit Restzeit
let LABT=null,LABINFO=null,LABLAST=null;
const fmtDur=s=>{s=Math.max(0,Math.round(s||0));if(s<60)return 'unter 1 Min.';const m=Math.round(s/60);if(m<60)return 'ca. '+m+' Min.';return 'ca. '+Math.floor(m/60)+' Std. '+(m%60?(m%60)+' Min.':'')};
function deckCardNames(){return deck.groups.flatMap(g=>g.cards).filter(c=>!c.basic).map(c=>c.name)}
async function labBox(o,gen){let ready=false;const wrap=$('details');wrap.id='labwrap';wrap.className='subbox';o.append(wrap);keepOpen(wrap);
 wrap.append($('summary','🔬 Messlabor: Änderungen und KI-Profile mit Forge messen'));
 const body=$('div');wrap.append(body);
 const info=LABINFO=await J('/api/lab_list');if(gen!=DUELGEN){wrap.remove();return}if(info.error){P(body,info.error,'warn');return}
 P(body,'Forge spielt jede Variante gleich oft gegen dieselben Gegner, mit gleichem Zufallsstart. Ergebnis: Siegquote mit 90-%-Bereich und ein Urteil, ob die Änderung messbar hilft.','hint');
 const mode=$('select');mode.id='labmode';[['swap','Kartentausch messen'],['pilot','Bestes KI-Profil für dein Deck finden']].forEach(([v,t])=>mode.append(new Option(t,v)));
 const vbox=$('div');vbox.id='labvars';const pbox=$('div');pbox.id='labprof';
 body.append($('b','Was messen? '),mode,vbox,pbox);
 // Varianten
 const vrows=$('div');const addVar=(out,inn)=>{if(vrows.children.length>=6)return;const r=$('div');r.className='labvar';
  const o1=$('input');o1.className='labout';o1.placeholder='raus (Karte im Deck)';o1.size=26;o1.value=out||'';o1.setAttribute('list','labdeckcards');
  const i1=$('input');i1.className='labin';i1.placeholder='rein (neue Karte)';i1.size=26;i1.value=inn||'';
  const x=$('button','✕');x.type='button';x.title='Variante entfernen';x.onclick=()=>{r.remove();est()};
  const iw=$('span');iw.className='ac';iw.append(i1);r.append(o1,' → ',iw,' ',x);vrows.append(r);try{ac(i1,{get:names(false),pick:v=>{i1.value=v;est()}})}catch(e){}o1.oninput=i1.oninput=est;est()};
 const dl=$('datalist');dl.id='labdeckcards';deckCardNames().forEach(n=>dl.append(new Option(n)));
 const av=$('button','+ Variante');av.type='button';av.id='labaddvar';av.onclick=()=>addVar();
 const sg=$('button','💡 Vorschläge übernehmen');sg.type='button';sg.id='labsugg';sg.title='Je eine Ergänzung aus den Empfehlungen gegen einen Streichkandidaten';
 sg.onclick=async()=>{sg.disabled=true;const r=await J('/api/recommend',{list:deck.export,commander:deck.commander||'',extra:JSON.stringify(deckExtra())});sg.disabled=false;
  if(r.error){P(vbox,r.error,'warn');return}vrows.innerHTML='';const k=Math.min(3,(r.add||[]).length,(r.cut||[]).length);
  for(let i=0;i<k;i++)addVar(r.cut[i].name,r.add[i].name);if(!k)P(vbox,'Keine passenden Vorschläge gefunden.','hint')};
 vbox.append(dl,vrows,av,' ',sg);P(vbox,'Je Zeile eine Variante. Mehrere Karten mit Komma trennen (z. B. „Shock, Opt → Lightning Bolt, Ponder“).','hint');addVar();
 // KI-Profile
 const base=$('select');base.id='labbase';info.profiles.forEach(x=>base.append(new Option(x,x)));
 const cks=$('span');info.profiles.forEach(x=>{const l=$('label');const c=$('input');c.type='checkbox';c.value=x;c.className='labpf';c.checked=['Cautious','Reckless','Experimental'].includes(x);c.onchange=est;l.append(c,' '+x+' ');cks.append(l)});
 pbox.append('Ausgangsprofil: ',base,$('br'),'Vergleichen mit: ',cks);P(pbox,'Die Gegner spielen immer mit „Default“. Das beste Profil kannst du danach für Duelle mit diesem Deck übernehmen.','hint');
 mode.onchange=()=>{vbox.hidden=mode.value!='swap';pbox.hidden=mode.value!='pilot';est()};pbox.hidden=true;
 // Gegner
 const [pl,dl2,all]=await Promise.all([J('/api/precons?ci='+encodeURIComponent(deck.ci||'')),J('/api/decks'),preconsAll()]);if(gen!=DUELGEN){wrap.remove();return}
 const decks=Array.isArray(dl2)?dl2:(dl2.decks||[]);const obox=$('div');obox.id='labopps';
 const addOpp=first=>{if(obox.querySelectorAll('select').length>=4)return;const s=$('select');s.className='labopp';
  fillPreconSelect(s,all,{match:pl.slice(0,8),prefix:'precon:',decks:decks});
  if(first){const c=new Option('Aktueller Gegner: '+opp.name,'cur');s.prepend(c);s.value='cur'}else if(s.options.length>obox.children.length)s.selectedIndex=obox.children.length;
  const r=$('div');r.append(s);if(!first){const x=$('button','✕');x.type='button';x.onclick=()=>{r.remove();est()};r.append(' ',x)}obox.append(r);s.onchange=est;est()};
 const ao=$('button','+ Gegner');ao.type='button';ao.id='labaddopp';ao.onclick=()=>addOpp(false);
 body.append($('h4','Gegnerfeld'),obox,ao);
 // Umfang
 const n=$('input');n.type='number';n.id='labn';n.min=2;n.max=100;n.value=10;n.size=4;n.oninput=est;
 const mc=$('select');mc.id='labmc';[['off','aus (ca. 15 s je Partie)'],['on','an (ca. 30 s je Partie)'],['max','maximal, wie Forge am PC (ca. 50 s je Partie)']].forEach(([v,t])=>mc.append(new Option(t,v)));mc.onchange=est;
 const es=$('p');es.id='labest';es.className='hint';
 const go=$('button','▶ Messung starten');go.type='button';go.className='primary';go.id='labgo';
 const stop=$('button','Abbrechen');stop.type='button';stop.id='labstop';stop.hidden=true;
 // Umfang als Stufe mit ungefährer Dauer; „Eigene Einstellung“ für Partien und Vorausschau von Hand
 const LABPRE=[{k:'quick',t:'Schnell',n:10,mc:'off',pf:'few',d:'10 Partien je Variante und Gegner, ohne Vorausschau. Zeigt grobe Tendenzen und große Unterschiede.'},
  {k:'std',t:'Standard',n:20,mc:'off',pf:'all',d:'20 Partien, alle KI-Profile. Erkennt Unterschiede ab etwa 25 Prozentpunkten zuverlässig.'},
  {k:'deep',t:'Gründlich',n:40,mc:'off',pf:'all',d:'40 Partien, alle KI-Profile. Macht auch kleinere Unterschiede sichtbar.'},
  {k:'max',t:'Sehr gründlich',n:30,mc:'on',pf:'all',d:'30 Partien mit Vorausschau: die KI prüft Züge vorher durch und spielt stärker, dauert etwa doppelt so lange je Partie.'},
  {k:'custom',t:'Eigene Einstellung',d:'Partien und Vorausschau selbst festlegen.'}];
 const pre=$('select');pre.id='labpreset';LABPRE.forEach(x=>pre.append(new Option(x.t,x.k)));const pd=$('p');pd.className='hint';pd.id='labpredesc';
 const man=$('span');man.id='labmanual';man.append('Partien je Variante und Gegner: ',n,'  KI-Vorausschau: ',mc);
 const FEW=['Cautious','Reckless','Experimental'];
 const preProfs=x=>x.pf=='few'?FEW.filter(f=>info.profiles.includes(f)&&f!=base.value):info.profiles.filter(f=>f!=base.value);
 const durOf=(nv,nvar,nop,m)=>{const tot=nv*nvar*nop;return [tot,(tot*({off:15,on:35,max:60}[m]||15)+nvar*nop*15)/Math.max(1,info.workers||1)]};
 function applyPre(){const x=LABPRE.find(y=>y.k==pre.value);pd.textContent=x.d;man.hidden=x.k!='custom';if(x.k=='custom'){est();return}
  n.value=x.n;mc.value=x.mc;if(mode.value=='pilot')pbox.querySelectorAll('.labpf').forEach(c=>c.checked=preProfs(x).includes(c.value));est()}
 function preLabels(){const nop=obox.children.length||1;[...pre.options].forEach(o=>{const x=LABPRE.find(y=>y.k==o.value);if(x.k=='custom'){o.textContent=x.t;return}
  const nvar=1+(mode.value=='swap'?variants().length:preProfs(x).length);const [tot,sec]=durOf(x.n,nvar,nop,x.mc);
  o.textContent=x.t+': '+(nvar<2?'?':fmtDur(sec))+' ('+tot+' Partien)'+(tot>info.max?' · über der Grenze':'');o.disabled=tot>info.max&&o.value!=pre.value})}
 pre.onchange=applyPre;n.addEventListener('input',()=>{pre.value='custom';pd.textContent=LABPRE[4].d});mc.addEventListener('change',()=>{pre.value='custom';pd.textContent=LABPRE[4].d});
 base.addEventListener('change',()=>{pbox.querySelectorAll('.labpf').forEach(c=>{c.disabled=c.value==base.value;if(c.disabled)c.checked=false});if(pre.value!='custom')applyPre()});
 pbox.querySelectorAll('.labpf').forEach(c=>{c.disabled=c.value==base.value;if(c.disabled)c.checked=false});
 mode.addEventListener('change',()=>{if(pre.value!='custom')applyPre()});
 body.append($('h4','Umfang'),pre,man,pd,es,go,' ',stop);
 const out=$('div');out.id='labout';body.append(out);if(LABLAST&&LABLAST.result)labShow(out,LABLAST);
 const arch=$('details');arch.id='labarch';arch.append($('summary','📁 Frühere Messungen ('+info.runs.length+')'));body.append(arch);labArchive(arch,info.runs,out);
 function variants(){return [...vrows.children].map(r=>({out:r.querySelector('.labout').value.split(',').map(x=>x.trim()).filter(Boolean),in:r.querySelector('.labin').value.split(',').map(x=>x.trim()).filter(Boolean)})).filter(v=>v.out.length||v.in.length)}
 function profs(){return [...pbox.querySelectorAll('.labpf:checked')].map(c=>c.value).filter(x=>x!=base.value)}
 function est(){if(!ready)return;const nv=Math.max(2,+n.value||2),nvar=1+(mode.value=='swap'?variants().length:profs().length),nop=obox.children.length||1;
  const tot=nv*nvar*nop,per={off:15,on:35,max:60}[mc.value]||15;
  es.textContent=nvar<2?'Bitte mindestens eine Variante angeben.':tot+' Partien ('+nvar+' Varianten × '+nop+' Gegner × '+nv+') · voraussichtlich '+fmtDur((tot*per+nvar*nop*15)/Math.max(1,info.workers||1))+(tot>info.max?', mehr als erlaubt ('+info.max+')':'');
  go.disabled=nvar<2||tot>info.max;preLabels()}
 ready=true;addOpp(true);pre.value='quick';applyPre();
 go.onclick=async()=>{const specs=[...obox.querySelectorAll('select')].map(s=>s.value);
  const prm=Object.assign(mineP(),oppP(),{mode:mode.value,games:n.value,mc:mc.value,opps:specs.join(','),deck_name:deck&&deck.name||'',
   variants:JSON.stringify(variants()),ai:mode.value=='pilot'?base.value:(labPilot()||'Default'),profiles:profs().join(',')});
  go.disabled=true;out.innerHTML='';const j=await J('/api/lab_start',prm);if(j.error){P(out,j.error,'warn');go.disabled=false;return}
  stop.hidden=false;stop.onclick=()=>J('/api/lab_cancel',{job:j.job});
  clearInterval(LABT);const poll=async()=>{const s=await J('/api/lab_status?job='+j.job);labShow(E('labout'),s);if(s.done||s.error&&!s.result){clearInterval(LABT);go.disabled=false;stop.hidden=true;
   if(s.done){const r=await J('/api/lab_list');arch.querySelector('summary').textContent='📁 Frühere Messungen ('+r.runs.length+')';labArchive(arch,r.runs,out)}}};
  LABT=setInterval(poll,4000);labShow(E('labout'),j)}}
function labPilot(){try{return localStorage.getItem('aipilot:'+((deck&&deck.name)||deck.commander||''))||''}catch(e){return ''}}
function labShow(o,s){if(!o)return;LABLAST=s;o.innerHTML='';if(s.error&&!s.result){P(o,s.error,'warn');return}
 const pr=$('div');pr.className='labprog';const bar=$('progress');bar.max=s.total;bar.value=s.played;bar.id='labbar';
 const txt=s.done?(s.cancelled?'Abgebrochen nach '+s.played+' von '+s.total+' Partien.':'Fertig: '+s.played+' Partien in '+fmtDur(s.elapsed).replace('ca. ','')+'.')
  :(s.queued?'Wartet auf einen freien Forge-Platz'+(s.waiting>1?' ('+s.waiting+' Aufträge in der Warteschlange)':'')+' …':s.played+' von '+s.total+' Partien · noch '+fmtDur(s.eta)+(s.eta_kind=='geschätzt'?' (grob geschätzt)':''));
 const tx=$('span',' '+txt);tx.id='labeta';pr.append(bar,tx);o.append(pr);if(s.error)P(o,s.error,'warn');
 if(s.result)labTable(o,s.result)}
function labTable(o,r){const t=$('table');t.className='duel';t.id='labres';o.append(t);
 const h=t.insertRow();['Variante','Siege','Siegquote (90-%-Bereich)','Unterschied','Urteil',''].forEach(x=>h.append($('th',x)));
 r.rows.forEach((x,i)=>{const tr=t.insertRow();tr.dataset.key=x.key;tr.insertCell().textContent=x.label;tr.insertCell().textContent=x.wins+' von '+x.games+(x.draws?' ('+x.draws+' unentsch.)':'');
  tr.insertCell().textContent=x.rate==null?'–':x.rate+' % ('+x.ci[0]+'–'+x.ci[1]+' %)';
  tr.insertCell().textContent=i==0?'Basis':(x.delta==null?'–':(x.delta>0?'+':'')+x.delta+' Pkt.');
  const v=tr.insertCell();v.textContent=i==0?'':x.verdict||'';if(/besser/.test(x.verdict||''))v.className='w';else if(/schlechter/.test(x.verdict||''))v.className='l';
  const c=tr.insertCell();if(i>0&&/besser/.test(x.verdict||'')){const b=$('button',x.applied?'✔ übernommen':r.mode=='swap'?'Ins Deck übernehmen':'Als KI-Pilot merken');b.type='button';b.className='labapply';b.disabled=!!x.applied;
   b.onclick=async()=>{x.applied=true;if(r.mode=='swap'){for(const n of x.out){const gi=deck.groups.findIndex(g=>g.cards.some(c=>c.name.toLowerCase()==n.toLowerCase()||c.name.split(' // ')[0].toLowerCase()==n.toLowerCase()));
      if(gi>=0)removeCard(gi,deck.groups[gi].cards.findIndex(c=>c.name.toLowerCase()==n.toLowerCase()||c.name.split(' // ')[0].toLowerCase()==n.toLowerCase()))}
     for(const n of x.in)await addCardToDeck(n);b.textContent='✔ übernommen, Deck speichern nicht vergessen';b.disabled=true}
    else{try{localStorage.setItem('aipilot:'+((deck&&deck.name)||deck.commander||''),x.ai)}catch(e){}const sel=E('duelai');if(sel)sel.value=x.ai;b.textContent='✔ gemerkt';b.disabled=true}};c.append(b)}});
 if(r.tip)P(o,r.tip,'tag');
 if(r.opps.length>1||r.rows.some(x=>x.turn)){const d=$('details');d.id='labper';d.append($('summary','Je Gegner und Siegrunde'));o.append(d);keepOpen(d);
  const t2=$('table');t2.className='duel';d.append(t2);const h2=t2.insertRow();['Variante',...r.opps.map(x=>x.opp||x.name),'Ø Siegzug'].forEach(x=>h2.append($('th',x)));
  r.rows.forEach(x=>{const tr=t2.insertRow();tr.insertCell().textContent=x.label;x.per.forEach(p=>tr.insertCell().textContent=p.games?p.wins+'/'+p.games+' ('+p.rate+' %)':'–');tr.insertCell().textContent=x.turn==null?'–':String(x.turn).replace('.',',')})}
 P(o,'Urteil: „deutlich“ heißt 90 % Sicherheit, „eher“ 80 %. Unter 8 Partien je Variante gibt es kein Urteil. Forge spielt nicht wie Menschen. Das Ergebnis zeigt, wie die Änderung in KI-Partien wirkt.','hint')}
function labArchive(d,runs,out){[...d.querySelectorAll('.labrun')].forEach(x=>x.remove());
 runs.forEach(r=>{const row=$('div');row.className='labrun';const a=$('a',r.created+' · '+r.deck+' · '+(r.mode=='swap'?'Kartentausch':'KI-Profile')+' · '+r.played+' Partien');a.href='#';
  a.onclick=async e=>{e.preventDefault();const x=await J('/api/lab_get',{id:r.id});out.innerHTML='';if(x.error){P(out,x.error,'warn');return}out.append($('h4','Messung vom '+r.created));labTable(out,x)};
  const del=$('button','✕');del.type='button';del.title='Messung löschen';del.onclick=async()=>{await J('/api/lab_delete',{id:r.id});row.remove()};
  row.append(a,' ',del);if(r.tip)row.append($('div',r.tip));d.append(row)})}
const DOPEN={};
function keepOpen(d){if(DOPEN[d.id])d.open=true;d.addEventListener('toggle',()=>{DOPEN[d.id]=d.open})}
function duelStats(o,st,PL,s){const d=$('details');d.id='duelstats';d.className='subbox';o.append(d);keepOpen(d);
 d.append($('summary','📊 Genaue Statistik der Partien'));
 P(d,'Ausgewertet aus dem Spielprotokoll von Forge. „Runde“ zählt die eigenen Züge eines Spielers (Runde 3 = sein dritter Zug).','hint');
 const t=$('table');t.className='duel';t.id='duelstattab';d.append(t);
 const hr=t.insertRow();['',...PL.map(x=>x.name)].forEach(x=>hr.append($('th',x)));
 const v=(k,f)=>{const x=st[k];return x?f(x):'–'},n1=x=>x==null?'–':String(x).replace('.',',');
 const row=(lab,f,hint)=>{const tr=t.insertRow();const c=tr.insertCell();c.textContent=lab;if(hint)c.title=hint;PL.forEach(p=>tr.insertCell().textContent=v(p.k,f))};
 row('Partien begonnen (davon gewonnen)',x=>x.first+' ('+x.first_won+')');
 row('Ø Mulligans',x=>n1(x.mull));
 row('Commander zuerst gewirkt, Ø Runde',x=>n1(x.cmd_round)+(x.cmd_never?' · '+x.cmd_never+'× nie':''));
 row('Ø Commander-Würfe je Partie',x=>n1(x.cmd_casts),'Mehr als 1 heißt: der Commander wurde entfernt und neu gewirkt (Commander-Steuer).');
 row('Ø gespielte Länder',x=>n1(x.lands));
 row('Ø gewirkte Zauber',x=>n1(x.casts));
 row('Ø Schaden an Gegnern (davon Kampf)',x=>n1(x.dmg)+' ('+n1(x.combat)+')');
 const lst=(k,f)=>{const tr=t.insertRow();tr.insertCell().textContent=k;return tr};
 const tr1=lst('Am häufigsten gewirkt');PL.forEach(p=>{const c=tr1.insertCell();const x=st[p.k];if(!x){c.textContent='–';return}
  x.top_cast.forEach(e=>c.append($('div',e.name+': in '+e.games+' von '+x.games+' Partien')))});
 const tr2=lst('Meister Schaden');PL.forEach(p=>{const c=tr2.insertCell();const x=st[p.k];if(!x||!x.top_dmg.length){c.textContent='–';return}
  x.top_dmg.forEach(e=>c.append($('div',e[0]+': '+e[1])))});
 const tr3=lst('Schlüsselkarten');tr3.cells[0].title='Karten, mit denen das Deck deutlich öfter gewinnt als im Schnitt (ab 3 Partien).';
 PL.forEach(p=>{const c=tr3.insertCell();const x=st[p.k];if(!x||!x.key.length){c.textContent='–';return}
  x.key.forEach(e=>c.append($('div',e.name+': '+e.won+' von '+e.games+' gewonnen ('+e.rate+' % statt '+x.rate+' %)')))});
 P(d,'Schlüsselkarten sind nur ein Hinweis, denn bei wenigen Partien spielt der Zufall mit. „🔎 Verlauf“ bei einer Partie zeigt jeden Zug.','hint')}
async function duelGame(job,i,PL){const r=await J('/api/duel_detail?job='+job+'&game='+i);const o=dlgOpen('Partie '+(i+1)+': Verlauf');
 if(r.error){P(o,r.error,'warn');return}const d=r.detail,nm=k=>{const x=PL.find(p=>p.k==k);return x?x.name:k};
 const fix=t=>t.replace(/@([a-f])/g,(_,k)=>nm(k));
 const g=r.result||{};P(o,'Sieger: '+(g.winner&&g.winner!='draw'?nm(g.winner):'Unentschieden')+(g.turn?' in Runde '+g.turn:'')+(g.reason?', '+g.reason:'')+
  ' · begonnen hat '+nm(d.first)+' · '+d.turns+' Züge insgesamt','big');
 const t=$('table');t.className='duel';o.append(t);const hr=t.insertRow();['',...PL.map(x=>x.name)].forEach(x=>hr.append($('th',x)));
 const row=(l,f)=>{const tr=t.insertRow();tr.insertCell().textContent=l;PL.forEach(p=>{const x=d.p[p.k];tr.insertCell().textContent=x?f(x):'–'})};
 row('Starthand',x=>x.mull+' Karten'+(x.mull<7?' ('+(7-x.mull)+' Mulligan)':''));
 row('Commander gewirkt',x=>x.cmd_round?'Runde '+x.cmd_round+(x.cmd_casts>1?', insgesamt '+x.cmd_casts+'×':''):'nie');
 row('Länder / Zauber',x=>x.lands+' / '+x.casts);row('Angriffe',x=>String(x.attacks));
 row('Schaden ausgeteilt / erlitten',x=>x.dmg_dealt+' / '+x.dmg_taken);row('Leben am Ende',x=>String(x.life));
 row('Meister Schaden',x=>x.top_dmg.map(e=>e[0]+' '+e[1]).join(', ')||'–');
 o.append(lifeChart(d.life,PL,d.rounds));
 const tl=$('details');tl.open=true;tl.append($('summary','Zug für Zug'));o.append(tl);
 const lt=$('table');lt.id='duellog';tl.append(lt);
 d.log.forEach(z=>{const tr=lt.insertRow();const c0=tr.insertCell();c0.textContent=z.turn?'Zug '+z.turn+' (Runde '+z.round+')':'';
  const c1=tr.insertCell();c1.textContent=z.p?nm(z.p):'';const c2=tr.insertCell();
  if(!z.ev.length)c2.append($('span','– nichts Besonderes –'));z.ev.forEach(e=>{const sp=$('div',fix(e[1]));if(e[1].startsWith('Commander'))sp.style.fontWeight='bold';c2.append(sp)})});
 P(o,'Ausgelassen sind Phasenwechsel, Manaproduktion und ausgelöste Fähigkeiten; Schaden zwischen Kreaturen steht nicht einzeln da.','hint')}
function lifeChart(life,PL,rounds){const W=560,H=170,mx=Math.max(1,rounds||1);let lo=0,hi=40;
 Object.values(life).forEach(a=>a.forEach(p=>{lo=Math.min(lo,p[1]);hi=Math.max(hi,p[1])}));
 const X=r=>30+r/mx*(W-40),Y=v=>10+(hi-v)/(hi-lo||1)*(H-30),cols=['#c0362c','#2e7bc4','#2e8b57','#b8891f'];
 let svg='<svg id=lifechart viewBox="0 0 '+W+' '+H+'" width="100%" style="max-width:'+W+'px"><line x1=30 x2='+(W-10)+' y1='+Y(0)+' y2='+Y(0)+' stroke="#888" stroke-dasharray="3 3"/>'+
  '<text x=2 y='+(Y(hi)+4)+' font-size=10 fill="currentColor">'+hi+'</text><text x=2 y='+(Y(0)+4)+' font-size=10 fill="currentColor">0</text>'+
  '<text x='+(W-60)+' y='+(H-4)+' font-size=10 fill="currentColor">Runde '+mx+'</text>';
 PL.forEach((p,i)=>{const a=life[p.k];if(!a)return;let pts=[],last=40;a.forEach(q=>{pts.push(X(q[0])+','+Y(last));pts.push(X(q[0])+','+Y(q[1]));last=q[1]});pts.push(X(mx)+','+Y(last));
  svg+='<polyline fill=none stroke-width=2 stroke="'+cols[i%4]+'" points="'+pts.join(' ')+'"/>'});
 svg+='</svg>';const w=$('div');w.innerHTML='<b>Lebenspunkte</b> '+PL.map((p,i)=>'<span style="color:'+cols[i%4]+'">■ '+H_(p.name)+'</span>').join(' ')+'<br>'+svg;return w}
const H_=t=>String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function showDuel(o,s){o.innerHTML='';
 if(s.queued&&!s.done){P(o,'Wartet auf einen freien Platz, andere Duelle laufen gerade ('+(s.waiting||1)+' in der Warteschlange).','big');return}
 P(o,(s.done?'Fertig: ':'Läuft: ')+s.games.length+' von '+s.total+' Partien'+(s.done?'':' (der erste Start von Forge dauert etwa eine Minute)'),'big');
 if(s.error)P(o,s.error,'warn');
 if(s.unsupported&&s.unsupported.length)P(o,'Achtung: Forge kennt '+s.unsupported.length+' Karte(n) noch nicht und spielt ohne sie: '+
  'meist sehr neue Karten, die erst eine neuere Forge-Version enthält: '+s.unsupported.join(', ')+'. Das Ergebnis ist deshalb nur eingeschränkt aussagekräftig.','warn');
 const m=s.summary;if(!m||!s.games.length)return;
 const PL=s.players||[{k:'a',name:'Dein Deck'},{k:'b',name:(s.opp_kind=='precon'?'Precon ':'Gegner ')+s.opp}];
 const t=$('table');t.className='duel';t.id='dueltab';o.append(t);
 const row=(...c)=>{const tr=t.insertRow();c.forEach(x=>tr.insertCell().textContent=x);return tr};
 const hr=t.insertRow();['',...PL.map(x=>x.name)].forEach(x=>hr.append($('th',x)));
 const tr=row('Siege',...PL.map(x=>m[x.k]+' ('+Math.round(m[x.k]/s.games.length*100)+' %)'));
 const best=Math.max(...PL.map(x=>m[x.k]));if(PL.filter(x=>m[x.k]==best).length==1)tr.cells[1+PL.findIndex(x=>m[x.k]==best)].className='w';
 row('Unentschieden / Zeitlimit',...PL.map(()=>m.draw));
 row(PL.length>2?'Ø Siegzug (Züge aller Spieler zusammen)':'Ø Siegzug (Züge beider Spieler zusammen)',...PL.map(x=>m.turns[x.k]??'–'));
 const fmtR=r=>Object.entries(r).map(([k,v])=>k+': '+v).join(', ')||'–';
 row('Siegarten',...PL.map(x=>fmtR(m.reasons[x.k])));
 row('Siege durch Karte',...PL.map(x=>fmtR(m.effects[x.k])));
 if(PL.length>2)P(o,'Zum Vergleich: Bei '+(PL.length==3?'drei':'vier')+' gleich starken Decks gewinnt jedes etwa '+Math.round(100/PL.length)+' % der Partien.','hint');
 const nm=k=>{const x=PL.find(p=>p.k==k);return x?x.name:'Unentschieden'};
 if(m.stats)duelStats(o,m.stats,PL,s);
 const gl=$('details');gl.id='duelgames';o.append(gl);gl.append($('summary','Einzelne Partien'));keepOpen(gl);
 s.games.forEach((g,i)=>{const d=$('div','Partie '+(i+1)+': '+nm(g.winner)+
  (g.turn?' in Zug '+g.turn:'')+(g.reason?', '+g.reason:'')+(g.effect?' ('+g.effect+')':'')+' ');gl.append(d);
  if(s.has_detail){const b=$('button','🔎 Verlauf');b.type='button';b.className='sw dueldet';b.onclick=()=>duelGame(s.id,i,PL);d.append(b)}});
 P(o,'Hinweis: Die KI spielt solide, macht aber Fehler. Aussagekräftig sind deshalb erst Tendenzen über viele Partien.','hint');
 if(s.done&&!s.logged){const lb=$('button','Ins Spielprotokoll übernehmen');lb.type='button';lb.id='duellog';
  lb.onclick=async()=>{const me=deck&&deck.name?deck.name:'Mein Deck',op=(s.opp_kind=='precon'?'Precon ':'')+s.opp;
   const ps=PL.map((x,i)=>({name:'Forge-KI '+'ABCD'[i],deck:i==0?me:x.name.replace(/^(Precon|Gegner) /,'')}));
   const r=await J('/api/game_save',{games:JSON.stringify(s.games.map(g=>({players:ps,winner:PL.findIndex(x=>x.k==g.winner),turns:g.turn||0,source:'forge'})))});
   if(r.error){P(o,r.error,'warn');return}s.logged=true;lb.replaceWith($('span','✓ '+r.saved+' Partien übernommen'));tableStats(r)};o.append(lb)}}

// ---- Manuelles Testduell: Spieltisch im Browser (du ziehst, spielst und greifst selbst an)
let PV=null,PVH=[];let pvUid=0;
const pvShuf=a=>{for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};
const pvCard=c=>Object.assign({},c,{id:++pvUid,tap:false,cnt:0});
const pvLand=c=>/Land/.test((c.type||'').split(' // ')[0]);
function pvPlayer(d){const p={name:d.name,ci:d.ci||'',lib:pvShuf(d.cards.map(pvCard)),hand:[],bf:[],gy:[],ex:[],cz:d.cmds.map(c=>Object.assign(pvCard(c),{cmd:true,casts:0})),
 life:40,poison:0,cdmg:{},mull:0,kept:false,landsTurn:0,st:{lands:0,casts:0,cmdRound:null,cmdCasts:0,draws:0}};
 for(let i=0;i<7&&p.lib.length;i++)p.hand.push(p.lib.pop());return p}
function pvSave(){try{localStorage.setItem('pvgame',JSON.stringify(PV))}catch(e){}}
function pvSnap(){PVH.push(JSON.stringify(PV));if(PVH.length>40)PVH.shift()}
function pvLog(t){PV.log.push([PV.turn,t]);if(PV.log.length>600)PV.log.shift()}
const pvRound=()=>PV.turn?Math.ceil(PV.turn/PV.pl.length):0;
async function pvStart(withOpp){const r=await J('/api/playtest',Object.assign(mineP(),withOpp?oppP():{},{deck_name:deck&&deck.name||''}));
 if(r.error){alertBox(r.error);return}
 PV={pl:[pvPlayer(r.mine)].concat(withOpp&&r.opp?[pvPlayer(r.opp)]:[]),act:Math.random()<.5||!withOpp?0:1,turn:0,log:[],view:0,menu:null,pile:null,bottom:null,done:null,
  missing:r.missing||[]};PVH=[];
 pvLog('Neue Testpartie: '+PV.pl.map(p=>p.name).join(' gegen ')+'. Jeder hat 7 Karten gezogen: behalten oder Mulligan (der erste ist frei).');pvOpen()}
function alertBox(t){const o=dlgOpen('Hinweis');P(o,t,'warn')}
function pvOpen(){let o=E('pv');if(!o){o=document.createElement('div');o.id='pv';document.body.append(o)}o.hidden=false;document.body.classList.add('pvopen');pvRender()}
function pvClose(){const o=E('pv');if(o)o.hidden=true;document.body.classList.remove('pvopen');pvSave();tableExit()}
function pvDo(f){pvSnap();PV.menu=null;PV.sel=null;f();pvSave();pvRender();const l=PV.log[PV.log.length-1];if(l&&typeof arToast=='function')arToast(l[1])}
function pvMove(p,c,from,to,where){const i=p[from].findIndex(x=>x.id==c.id);if(i<0)return;p[from].splice(i,1);
 if(to!='bf'){c.tap=false;c.cnt=0}
 if(c.tok&&to!='bf'){pvLog(p.name+': Token '+c.name+' verschwindet');return}
 if(to=='lib'){where=='bottom'?p.lib.unshift(c):p.lib.push(c)}else p[to].push(c)}
const ZN={hand:'Hand',bf:'Spielfeld',gy:'Friedhof',ex:'Exil',lib:'Bibliothek',cz:'Kommandozone'};
function pvPlay(p,c,from){pvMove(p,c,from,'bf');
 if(pvLand(c)){p.landsTurn++;p.st.lands++;pvLog(p.name+' spielt Land '+c.name+(p.landsTurn>1?' (schon das '+p.landsTurn+'. Land in diesem Zug)':''))}
 else{p.st.casts++;pvLog(p.name+' spielt '+c.name+(from!='hand'?' (aus '+ZN[from]+')':''))}}
function pvCastCmd(p,c){const tax=2*(c.casts||0);c.casts=(c.casts||0)+1;p.st.cmdCasts++;if(p.st.cmdRound==null)p.st.cmdRound=pvRound()||1;
 pvMove(p,c,'cz','bf');p.st.casts++;pvLog(p.name+' wirkt Commander '+c.name+(tax?' (Commander-Steuer +'+tax+')':''))}
function pvDraw(p,n){for(let i=0;i<n;i++){if(!p.lib.length){pvLog(p.name+' kann nicht ziehen, die Bibliothek ist leer!');return}p.hand.push(p.lib.pop());p.st.draws++}}
function pvMull(i){const p=PV.pl[i];pvDo(()=>{p.lib.push(...p.hand);p.hand=[];pvShuf(p.lib);pvDraw(p,7);p.st.draws-=7;p.mull++;
 pvLog(p.name+' nimmt einen Mulligan ('+p.mull+'.'+(p.mull==1?', frei':'')+')')})}
function pvKeep(i){const p=PV.pl[i];pvDo(()=>{const n=Math.max(0,p.mull-1);if(n){PV.bottom={p:i,n};pvLog(p.name+' behält und legt '+n+' Karte(n) unter die Bibliothek')}
 else{p.kept=true;pvLog(p.name+' behält '+p.hand.length+' Karten')}pvBegin()})}
function pvBegin(){if(PV.turn||!PV.pl.every(p=>p.kept))return;PV.turn=1;const p=PV.pl[PV.act];PV.view=PV.act;
 pvLog('Zug 1: '+p.name+' beginnt'+(PV.pl.length>1?' (zieht im ersten Zug keine Karte)':''))}
function pvNext(){pvDo(()=>{const n=PV.pl.length;PV.act=(PV.act+1)%n;PV.turn++;PV.phase=0;const p=PV.pl[PV.act];p.landsTurn=0;
 p.bf.forEach(c=>c.tap=false);pvDraw(p,1);PV.view=PV.act;pvLog('Zug '+PV.turn+' (Runde '+pvRound()+'): '+p.name+' enttappt und zieht')})}
function pvBtn(t,f,cls){const b=$('button',t);b.type='button';if(cls)b.className=cls;b.onclick=e=>{e.stopPropagation();f()};return b}
function pvStats(){const t=$('table');t.className='duel';t.id='pvstats';const hr=t.insertRow();['',...PV.pl.map(p=>p.name)].forEach(x=>hr.append($('th',x)));
 const row=(l,f)=>{const tr=t.insertRow();tr.insertCell().textContent=l;PV.pl.forEach(p=>tr.insertCell().textContent=f(p))};
 row('Mulligans',p=>String(p.mull));row('Commander zuerst gewirkt',p=>p.st.cmdRound?'Runde '+p.st.cmdRound+(p.st.cmdCasts>1?', '+p.st.cmdCasts+'× insgesamt':''):'noch nicht');
 row('Länder gespielt',p=>String(p.st.lands));row('Zauber gespielt',p=>String(p.st.casts));row('Karten gezogen (ohne Starthand)',p=>String(p.st.draws));
 row('Leben',p=>String(p.life));row('Karten in Bibliothek',p=>String(p.lib.length));return t}
async function pvFinish(w){PV.done={winner:w};pvLog('Partie beendet nach '+pvRound()+' Runden'+(w>=0?', gewonnen hat '+PV.pl[w].name:''));pvSave();
 if(w>=0&&PV.pl.length>1){const r=await J('/api/game_save',{games:JSON.stringify([{players:PV.pl.map((p,i)=>({name:i?'Gegner (manuell)':'Ich',deck:p.name})),winner:w,turns:pvRound(),source:'manuell'}])});
  PV.done.saved=!r.error;PV.done.msg=r.error||'✓ Ins Spielprotokoll übernommen'}pvRender()}
// ---- Spieltisch im Arena-Stil (allein oder zu zweit): Gegner oben, Spielfeld Mitte, Hand als Fächer unten,
// ein großer Knopf für den Zug, alles Weitere hinter ⚙. Karten ziehen (Drag & Drop), antippen = Aktionen, lange drücken = groß.
const PHASES=[['⟳','Enttappen, Versorgung, Ziehen'],['☀','Hauptphase 1'],['⚔','Kampf'],['☾','Hauptphase 2'],['⏹','Ende']];
let AR={drag:null};
function arMe(){return PV.view||0}
const MCOL={W:'#f3ecd2',U:'#2f74b8',B:'#4a3f48',R:'#c8402c',G:'#2f7d45'};
let ARMAT='colors';try{ARMAT=localStorage.getItem('armat')||'colors'}catch(e){}
function arRing(ci){const c=(ci||'').split('').filter(x=>MCOL[x]);if(!c.length)return '#8a8a8a';if(c.length==1)return MCOL[c[0]];
 const st=360/c.length;return 'conic-gradient('+c.map((x,i)=>MCOL[x]+' '+(i*st)+'deg '+((i+1)*st)+'deg').join(',')+')'}
function arMat(o){const me=PV.pl[arMe()],op=arOpp()!=null?PV.pl[arOpp()]:null;o.dataset.mat=ARMAT;o.style.removeProperty('--matimg');
 const glow=(ci,pos)=>(ci||'').split('').filter(x=>MCOL[x]).map((x,i,a)=>'radial-gradient(ellipse at '+(a.length>1?(15+70*i/(a.length-1)):50)+'% '+pos+',' +MCOL[x]+'55 0%,transparent 55%)');
 if(ARMAT=='colors'){const g=[...glow(me.ci,'100%'),...(op?glow(op.ci,'0%'):[])];o.style.setProperty('--matglow',g.join(',')||'none')}
 else o.style.setProperty('--matglow','none');
 if(ARMAT=='cmd'){const c=me.cz[0]||me.bf.find(x=>x.cmd);const img=c&&c.image?c.image.replace('/normal/','/art_crop/').replace('/large/','/art_crop/'):'';if(img)o.style.setProperty('--matimg','url("'+img+'")')}}
function arOpp(){return PV.pl.length>1?1-arMe():null}
function arToast(t){const o=E('pv');if(!o)return;let x=E('artoast');if(!x){x=$('div');x.id='artoast';o.append(x)}x.textContent=t;x.classList.remove('fade');void x.offsetWidth;x.classList.add('fade')}
function arDo(f,toast){pvSnap();PV.sel=null;if(PV.sheet&&!['life','lib'].includes(PV.sheet.kind))PV.sheet=null;f();pvSave();pvRender();const l=PV.log[PV.log.length-1];if(toast!==false&&l)arToast(l[1])}
function arIcon(t,title,fn,cls,id){const b=$('button',t);b.type='button';b.title=title;b.setAttribute('aria-label',title);b.className='aricon'+(cls?' '+cls:'');if(id)b.id=id;
 b.onclick=e=>{e.stopPropagation();fn(e)};return b}
// --- Karte
function arCard(p,c,zone,pi,small){const d=$('div');d.className='arc'+(c.tap?' tap':'')+(c.cmd?' cmd':'')+(c.tok?' tok':'')+(small?' sm':'')+
  (PV.sel&&PV.sel.id==c.id?' sel':'');d.dataset.id=c.id;d.dataset.zone=zone;d.dataset.pi=pi;d.title=c.name;
 if(TTEXT){d.classList.add('txt');d.append(textTile(c))}
 else if(c.image){d.append(Object.assign($('span',c.name),{className:'arn'}));const im=$('img');im.src=c.image;im.loading='lazy';im.alt=c.name;im.draggable=false;im.onerror=()=>im.remove();d.append(im)}
 else d.append(Object.assign($('span',c.name),{className:'arn'}));
 if(c.cnt)d.append(Object.assign($('b',(c.cnt>0?'+':'')+c.cnt),{className:'arcnt',title:'Marken'}));
 if(zone=='cz'&&c.casts)d.append(Object.assign($('b','+'+2*c.casts),{className:'artax',title:'Commander-Steuer'}));
 arPointer(d,p,c,zone,pi);return d}
function arPointer(d,p,c,zone,pi){let lt=null,sx=0,sy=0,long=false,moved=false;
 d.addEventListener('contextmenu',e=>{e.preventDefault();cardZoom(c)});
 d.addEventListener('pointerdown',e=>{if(e.button>0)return;sx=e.clientX;sy=e.clientY;long=false;moved=false;clearTimeout(lt);
  lt=setTimeout(()=>{if(!moved){long=true;cardZoom(c)}},550);
  const mv=ev=>{if(Math.abs(ev.clientX-sx)+Math.abs(ev.clientY-sy)>14&&!moved&&!long&&['hand','bf','cz','gy','ex'].includes(zone)&&!(PV.bottom)){moved=true;clearTimeout(lt);arDragStart(d,p,c,zone,pi,ev)}
   if(moved)arDragMove(ev)};
  const up=ev=>{document.removeEventListener('pointermove',mv);document.removeEventListener('pointerup',up);document.removeEventListener('pointercancel',up);clearTimeout(lt);
   if(moved){arDragEnd(ev);return}if(long)return;arClick(p,c,zone,pi)};
  document.addEventListener('pointermove',mv);document.addEventListener('pointerup',up);document.addEventListener('pointercancel',up)});
 }
function arClick(p,c,zone,pi){if(PV.bottom&&zone=='hand'&&PV.bottom.p==pi){arDo(()=>{pvMove(p,c,'hand','lib','bottom');PV.bottom.n--;pvLog(p.name+' legt eine Karte unter die Bibliothek');
   if(!PV.bottom.n){p.kept=true;PV.bottom=null;pvBegin()}},false);return}
 const now=Date.now();if(zone=='bf'&&AR.last&&AR.last.id==c.id&&now-AR.last.t<400){AR.last=null;arDo(()=>{c.tap=!c.tap;pvLog(p.name+': '+c.name+(c.tap?' getappt':' enttappt'))},false);return}
 AR.last={id:c.id,t:now};PV.sel=PV.sel&&PV.sel.id==c.id?null:{pi,id:c.id,zone};pvRender()}
// --- Drag & Drop: Karte auf Spielfeld, Friedhof, Exil, Bibliothek, Hand oder Kommandozone ziehen
function arDragStart(d,p,c,zone,pi,ev){const g=d.cloneNode(true);g.id='arghost';g.classList.remove('sel');document.body.append(g);
 AR.drag={p,c,zone,pi,g,src:d};d.classList.add('dragging');arDragMove(ev)}
function arDragMove(ev){const dr=AR.drag;if(!dr)return;dr.g.style.left=(ev.clientX-30)+'px';dr.g.style.top=(ev.clientY-40)+'px';
 document.querySelectorAll('.drop-on').forEach(x=>x.classList.remove('drop-on'));const t=arTarget(ev);if(t)t.classList.add('drop-on')}
function arTarget(ev,dr){dr=dr||AR.drag;dr.g.style.display='none';const el=document.elementFromPoint(ev.clientX,ev.clientY);dr.g.style.display='';
 const t=el&&el.closest('[data-drop]');return t&&+t.dataset.pi==dr.pi?t:null}
function arDragEnd(ev){const dr=AR.drag;AR.drag=null;if(!dr)return;const t=arTarget({clientX:ev.clientX,clientY:ev.clientY},dr);
 dr.g.remove();document.querySelectorAll('.drop-on').forEach(x=>x.classList.remove('drop-on'));dr.src.classList.remove('dragging');
 if(!t)return;const to=t.dataset.drop,{p,c,zone}=dr;if(to==zone)return;
 arDo(()=>{if(to=='bf'){if(zone=='cz')pvCastCmd(p,c);else pvPlay(p,c,zone)}
  else if(to=='cz'){if(!c.cmd)return;pvMove(p,c,zone,'cz');pvLog(p.name+': '+c.name+' zurück in die Kommandozone')}
  else{pvMove(p,c,zone,to);pvLog(p.name+': '+c.name+' → '+ZN[to])}})}
// --- Aktionsleiste der gewählten Karte (wenige, klare Knöpfe; Rest unter „Mehr“)
function arSelBar(){const s=PV.sel;if(!s)return null;const p=PV.pl[s.pi];const c=(p[s.zone]||[]).find(x=>x.id==s.id);if(!c){PV.sel=null;return null}
 const w=$('div');w.id='arsel';w.onclick=e=>e.stopPropagation();w.append(Object.assign($('b',c.name),{className:'arselname'}));
 const a=(t,f,cls)=>w.append(pvBtn(t,()=>arDo(f),cls));const z=s.zone;
 if(z=='hand'){a(pvLand(c)?'Land spielen':'Ausspielen',()=>pvPlay(p,c,'hand'),'primary');a('Abwerfen',()=>{pvMove(p,c,'hand','gy');pvLog(p.name+' wirft '+c.name+' ab')})}
 if(z=='cz')a('Wirken'+(c.casts?' (+'+2*c.casts+')':''),()=>pvCastCmd(p,c),'primary');
 if(z=='bf'){a(c.tap?'Enttappen':'Tappen',()=>{c.tap=!c.tap},'primary');a('+1',()=>c.cnt++);a('−1',()=>c.cnt--)}
 if(['gy','ex','lib'].includes(z))a('Aufs Spielfeld',()=>pvPlay(p,c,z),'primary');
 if(z!='hand'&&z!='cz')a('Hand',()=>{pvMove(p,c,z,'hand');pvLog(p.name+': '+c.name+' → Hand')});
 w.append(pvBtn('🔍',()=>cardZoom(c),'aricon'));
 const more=pvBtn('Mehr ▾',()=>{w.classList.toggle('open')},'armore');w.append(more);
 const m=$('div');m.className='armorelist';w.append(m);const b=(t,f)=>m.append(pvBtn(t,()=>arDo(f)));
 ['gy','ex'].filter(x=>x!=z).forEach(x=>{b('→ '+ZN[x],()=>{pvMove(p,c,z,x);pvLog(p.name+': '+c.name+' → '+ZN[x])})});
 if(z!='lib'){b('→ Bibliothek oben',()=>{pvMove(p,c,z,'lib');pvLog(p.name+': '+c.name+' oben auf die Bibliothek')});b('→ Bibliothek unten',()=>{pvMove(p,c,z,'lib','bottom');pvLog(p.name+': '+c.name+' unter die Bibliothek')})}
 if(c.cmd&&z!='cz')b('→ Kommandozone',()=>{pvMove(p,c,z,'cz');pvLog(p.name+': Commander '+c.name+' zurück in die Kommandozone')});
 if(z=='bf')b('Kopie als Token',()=>{p.bf.push(Object.assign(pvCard({name:c.name+' (Kopie)',image:c.image,type:c.type}),{tok:true}));pvLog(p.name+' kopiert '+c.name)});
 w.append(pvBtn('✕',()=>{PV.sel=null;pvRender()},'aricon arx'));return w}
// --- Spielerleiste: Avatar mit Leben, Stapel, Kommandozone
function arPlayerBar(pi,top){const p=PV.pl[pi];const w=$('div');w.className='arpl'+(top?' top':' me')+(PV.act==pi&&PV.turn?' act':'');w.id='arpl'+pi;
 const av=$('button');av.type='button';av.className='aravatar';av.id='arav'+pi;av.style.setProperty('--ring',arRing(p.ci));av.title=p.name+': Leben, Gift, Commander-Schaden';
 av.append(Object.assign($('b',String(p.life)),{className:'arlife'}),Object.assign($('span',p.name),{className:'arname'}));
 if(p.poison)av.append(Object.assign($('i','☠'+p.poison),{className:'arbadge'}));
 const cd=Object.values(p.cdmg||{}).reduce((a,b)=>Math.max(a,b),0);if(cd)av.append(Object.assign($('i','⚔'+cd),{className:'arbadge cd',title:'höchster Commander-Schaden'}));
 av.onclick=e=>{e.stopPropagation();PV.sheet={kind:'life',pi};pvRender()};w.append(av);
 const pile=(z,ic,title,fn)=>{const b=$('button');b.type='button';b.className='arpile';b.dataset.drop=z;b.dataset.pi=pi;b.id='arz-'+z+pi;b.title=title;
  b.append($('span',ic),$('b',String(p[z].length)));b.onclick=e=>{e.stopPropagation();fn()};return b};
 w.append(pile('lib','📚','Bibliothek: antippen für Aktionen',()=>{PV.sheet={kind:'lib',pi};pvRender()}),
  pile('gy','🪦','Friedhof',()=>{PV.sheet={kind:'pile',pi,zone:'gy'};pvRender()}),pile('ex','🌀','Exil',()=>{PV.sheet={kind:'pile',pi,zone:'ex'};pvRender()}));
 const cz=$('div');cz.className='arcz';cz.dataset.drop='cz';cz.dataset.pi=pi;cz.title='Kommandozone';p.cz.forEach(c=>cz.append(arCard(p,c,'cz',pi,true)));if(!p.cz.length)cz.append($('span','👑'));w.append(cz);
 if(top&&pi!=arMe()){const h=$('div');h.className='arbacks';h.title='Hand: '+p.hand.length+' Karten';for(let i=0;i<Math.min(p.hand.length,10);i++)h.append($('i'));h.append($('b',String(p.hand.length)));w.append(h)}
 return w}
// --- Spielfeld einer Seite: Kreaturen & Co. zur Mitte, Länder nach außen
function arHalf(pi,top){const p=PV.pl[pi];const h=$('div');h.className='arhalf'+(top?' top':'');h.dataset.drop='bf';h.dataset.pi=pi;h.id='arbf'+pi;
 const perm=$('div');perm.className='arrow perm';p.bf.filter(c=>!pvLand(c)).forEach(c=>perm.append(arCard(p,c,'bf',pi)));
 const lands=$('div');lands.className='arrow lands';
 const grp={};p.bf.filter(pvLand).forEach(c=>{(grp[c.name]=grp[c.name]||[]).push(c)});
 Object.values(grp).forEach(g=>{const st=$('div');st.className='arstack';g.forEach(c=>st.append(arCard(p,c,'bf',pi,true)));if(g.length>1)st.append(Object.assign($('b','×'+g.length),{className:'arstackn'}));lands.append(st)});
 if(!p.bf.length)perm.append(Object.assign($('span','Karten hierher ziehen oder antippen → Ausspielen'),{className:'arempty'}));
 top?h.append(lands,perm):h.append(perm,lands);return h}
// --- Hand als Fächer
function arHand(pi){const p=PV.pl[pi];const h=$('div');h.className='arhand';h.dataset.drop='hand';h.dataset.pi=pi;h.id='arhand';
 const n=p.hand.length;p.hand.forEach((c,i)=>{const el=arCard(p,c,'hand',pi);const m=(n-1)/2,off=i-m;
  el.style.setProperty('--rot',(n>1?off*Math.min(4,24/n):0)+'deg');el.style.setProperty('--lift',(Math.abs(off)*Math.min(5,30/n))+'px');el.style.zIndex=i+1;h.append(el)});
 requestAnimationFrame(()=>{const w=h.clientWidth,cw=h.firstChild?h.firstChild.offsetWidth:80;const ov=n>1?Math.max(-cw*.15,(n*cw-w+20)/(n-1)):0;h.style.setProperty('--ov',Math.max(0,ov)+'px')});
 return h}
// --- Seitenmenü (⚙, Protokoll, Statistik, Stapel, Leben, Tokens, Ende)
function arSheet(){const s=PV.sheet;if(!s)return null;const w=$('div');w.id='arsheet';w.onclick=e=>e.stopPropagation();
 const head=$('div');head.className='arsh';w.append(head);const title=$('b');head.append(title,pvBtn('✕',()=>{PV.sheet=null;pvRender()},'aricon arx'));
 const sec=t=>{const d=$('div');d.className='arsec';if(t)d.append($('h4',t));w.append(d);return d};
 const btn=(o,t,f,cls,id)=>{const b=pvBtn(t,f,cls);if(id)b.id=id;o.append(b);return b};
 const me=PV.pl[s.pi!=null?s.pi:arMe()];
 if(s.kind=='menu'){title.textContent='Menü';
  let a=sec('Spielmatte');[['colors','Farben des Decks'],['felt','Klassischer Filz'],['parch','Pergament'],['cmd','Bild des Commanders']].forEach(([k,t])=>btn(a,(ARMAT==k?'✓ ':'')+t,()=>{ARMAT=k;try{localStorage.setItem('armat',k)}catch(e){}pvRender()},'','armat-'+k));
  a=sec('Ansicht');btn(a,(TTEXT?'✓ ':'')+'Aa Textansicht',()=>{ttextToggle()},'','ttext');btn(a,'A−',()=>{tableSize(-1);pvRender()},'','tsmall');btn(a,'A+',()=>{tableSize(1);pvRender()},'','tbig');btn(a,'📱 Quer + Vollbild',()=>tableLandscape(),'','tquer');
  if(PV.pl.length>1)btn(a,'⇅ Seite wechseln (Hand von '+PV.pl[1-arMe()].name+')',()=>{PV.view=1-arMe();PV.sel=null;PV.sheet=null;pvRender()},'','arswap');
  a=sec('Aktionen');btn(a,'✨ Token erzeugen',()=>{PV.sheet={kind:'tokens',pi:arMe()};pvRender()},'','artok');btn(a,'↺ Alle enttappen',()=>arDo(()=>{me.bf.forEach(c=>c.tap=false);pvLog(me.name+' enttappt alles')}));
  btn(a,'🎲 Würfeln / Münze',()=>arDo(()=>pvLog('Würfel: W6 = '+(1+Math.floor(Math.random()*6))+', W20 = '+(1+Math.floor(Math.random()*20))+', Münze: '+(Math.random()<.5?'Kopf':'Zahl'))),'','ardice');
  a=sec('Partie');btn(a,'📊 Statistik',()=>{PV.sheet={kind:'stats'};pvRender()},'','arstats');btn(a,'📜 Protokoll',()=>{PV.sheet={kind:'log'};pvRender()},'','arlog');
  if(!PV.turn&&PV.pl.length>1)btn(a,'Startspieler: '+PV.pl[PV.act].name+' ⇄',()=>arDo(()=>{PV.act=1-PV.act;pvLog('Startspieler: '+PV.pl[PV.act].name)}));
  btn(a,'🏁 Partie beenden',()=>{PV.sheet={kind:'end'};pvRender()},'','arend');btn(a,'⟲ Neue Partie',()=>pvStart(PV.pl.length>1),'','arnew');
  a=sec('Bedienung');a.append(Object.assign($('div','Karte antippen: Aktionen · ziehen: auf Spielfeld, 🪦, 🌀, 📚 oder Hand legen · lange drücken / Rechtsklick: groß ansehen · Doppelklick bzw. zweimal antippen: tappen. Tasten: Leertaste = Zug beenden, D = ziehen, T = tappen, Z = rückgängig, Esc = schließen. Regeln prüft der Tisch nicht.'),{className:'hint'}));
  if(PV.missing.length)a.append(Object.assign($('div','Nicht gefunden und weggelassen: '+PV.missing.join(', ')),{className:'hint'}))}
 if(s.kind=='life'){const p=PV.pl[s.pi];title.textContent=p.name;
  let a=sec('Leben: '+p.life);[-5,-1,1,5].forEach(d=>btn(a,(d>0?'+':'')+d,()=>arDo(()=>{p.life+=d;pvLog(p.name+': Leben '+(p.life-d)+' → '+p.life)}),'arbig'));
  a=sec('Gift: '+p.poison);btn(a,'−1',()=>arDo(()=>{p.poison=Math.max(0,p.poison-1);pvLog(p.name+': '+p.poison+' Giftmarken')}));btn(a,'+1',()=>arDo(()=>{p.poison++;pvLog(p.name+': '+p.poison+' Giftmarken'+(p.poison>=10?', verloren!':''))}));
  PV.pl.forEach((q,qi)=>{if(qi==s.pi)return;const v=p.cdmg[qi]||0;const b=sec('Commander-Schaden von '+q.name+': '+v);
   btn(b,'+1 (kostet 1 Leben)',()=>arDo(()=>{p.cdmg[qi]=v+1;p.life--;pvLog(p.name+': 1 Commander-Schaden von '+q.name+' (gesamt '+(v+1)+')'+(v+1>=21?', 21 erreicht, verloren!':''))}))})}
 if(s.kind=='lib'){const p=PV.pl[s.pi];title.textContent='📚 Bibliothek: '+p.lib.length+' Karten';const a=sec('');
  btn(a,'🃏 Karte ziehen',()=>arDo(()=>{pvDraw(p,1);pvLog(p.name+' zieht eine Karte')}),'primary','ardraw2');btn(a,'🔀 Mischen',()=>arDo(()=>{pvShuf(p.lib);pvLog(p.name+' mischt')}));
  const n=$('input');n.type='number';n.min=1;n.max=20;n.value=3;n.style.width='3.5em';const b2=$('div');b2.className='arsec';b2.append('Oberste ',n,' ');
  b2.append(pvBtn('ansehen',()=>{PV.sheet={kind:'pile',pi:s.pi,zone:'lib',top:Math.max(1,parseInt(n.value)||3)};pvRender()}));w.append(b2);
  btn(a,'🔎 Durchsuchen',()=>{PV.sheet={kind:'pile',pi:s.pi,zone:'lib'};pvLog(p.name+' durchsucht die Bibliothek');pvRender()},'','arsearch')}
 if(s.kind=='pile'){const p=PV.pl[s.pi];let list=p[s.zone];if(s.top)list=list.slice(-s.top).reverse();else if(s.zone=='lib')list=list.slice().reverse();
  title.textContent=(s.top?'Oberste '+s.top+' Karten':ZN[s.zone])+': '+p.name+' ('+list.length+')';
  if(s.top)w.append(Object.assign($('div','Links die oberste. Karte antippen → Aktionen (z. B. unter die Bibliothek für Scry).'),{className:'hint'}));
  const g=$('div');g.className='argrid';list.forEach(c=>g.append(arCard(p,c,s.zone,s.pi,true)));if(!list.length)g.append($('span','leer'));w.append(g);
  if(s.zone=='lib'&&!s.top)w.append(pvBtn('Schließen und mischen',()=>{PV.sheet=null;arDo(()=>{pvShuf(p.lib);pvLog(p.name+' mischt')})}))}
 if(s.kind=='tokens'){const p=PV.pl[s.pi];title.textContent='✨ Token für '+p.name;const a=sec('');const inp=$('input');inp.placeholder='z. B. 1/1 Goblin';inp.id='artokname';
  a.append(inp,pvBtn('Erzeugen',()=>{const v=inp.value.trim()||'Token';PV.sheet=null;arDo(()=>{p.bf.push(Object.assign(pvCard({name:v,type:'Token'}),{tok:true}));pvLog(p.name+' erzeugt Token '+v)})},'primary'));
  const l=sec('Tokens aus dem Deck');l.id='artoklist';l.append(Object.assign($('span','lade …'),{className:'hint'}));
  const names=[...new Set(['lib','hand','bf','gy','ex','cz'].flatMap(z=>p[z].map(c=>c.name)))];
  J('/api/tokens',{list:names.map(n=>'1 '+n).join('\\n'),commander:p.cz.map(c=>c.name).join(' + ')}).then(r=>{l.innerHTML='';l.append($('h4','Tokens aus dem Deck'));
   (r.tokens||[]).forEach(t=>l.append(pvBtn(t.name+(t.type?' ('+t.type+')':''),()=>{PV.sheet=null;arDo(()=>{p.bf.push(Object.assign(pvCard({name:t.name,image:t.image||'',type:t.type||'Token'}),{tok:true}));pvLog(p.name+' erzeugt Token '+t.name)})},'artokbtn')));
   if(!(r.tokens||[]).length)l.append(Object.assign($('span','Keine Tokens im Deck erkannt.'),{className:'hint'}))})}
 if(s.kind=='stats'){title.textContent='📊 Statistik';w.append(pvStats())}
 if(s.kind=='log'){title.textContent='📜 Protokoll ('+PV.log.length+')';const l=$('div');l.id='pvlog';PV.log.slice().reverse().slice(0,300).forEach(e=>l.append($('div',(e[0]?'Zug '+e[0]+': ':'')+e[1])));w.append(l)}
 if(s.kind=='end'){title.textContent='🏁 Partie beenden';const a=sec('Wer hat gewonnen?');a.id='pvend';PV.pl.forEach((p,i)=>btn(a,p.name,()=>{PV.sheet={kind:'done'};pvFinish(i)},'primary'));
  btn(a,'ohne Wertung',()=>{PV.sheet={kind:'done'};pvFinish(-1)})}
 if(s.kind=='done'&&PV.done){title.textContent='Partie beendet';w.append(Object.assign($('p',(PV.done.winner>=0?'Sieger: '+PV.pl[PV.done.winner].name+'. ':'')+(PV.done.msg||'')),{className:'big'}),pvStats());
  w.append(pvBtn('⟲ Neue Partie',()=>pvStart(PV.pl.length>1),'primary'))}
 return w}
// --- Starthand / Mulligan
function arMull(){const i=PV.bottom?PV.bottom.p:PV.pl.findIndex(p=>!p.kept);if(i<0)return null;const p=PV.pl[i];
 const w=$('div');w.id='armull';w.onclick=e=>e.stopPropagation();
 w.append($('h3',PV.pl.length>1?'Starthand: '+p.name:'Deine Starthand'));
 w.append(Object.assign($('div',PV.bottom?'Tippe '+PV.bottom.n+' Karte'+(PV.bottom.n>1?'n':'')+' an, die unter die Bibliothek '+(PV.bottom.n>1?'kommen':'kommt')+'.':(p.mull?p.mull+'. Mulligan'+(p.mull==1?' (frei)':'')+' · ':'')+p.hand.length+' Karten · '+p.hand.filter(pvLand).length+' Länder'),{className:'arsub'}));
 const r=$('div');r.className='armullrow';p.hand.forEach(c=>r.append(arCard(p,c,'hand',i)));w.append(r);
 if(!PV.bottom){const b=$('div');b.className='armullbtn';b.append(pvBtn('Behalten',()=>pvKeep(i),'argo'),pvBtn('Mulligan',()=>pvMull(i),'armullb'));
  if(PV.pl.length>1&&!PV.turn&&i==0)b.append(pvBtn('Beginnt: '+PV.pl[PV.act].name+' ⇄',()=>arDo(()=>{PV.act=1-PV.act;pvLog('Startspieler: '+PV.pl[PV.act].name)}),'arsmall'));w.append(b)}
 return w}
// --- Gesamtansicht
function pvRender(){const o=E('pv');if(!o||!PV)return;setTimeout(ttextLoad,0);o.innerHTML='';o.className='ar'+(PV.pl.length>1?' duel':' solo');arMat(o);o.scrollTop=0;o.onscroll=()=>{if(o.scrollTop)o.scrollTop=0};
 o.onclick=()=>{if(PV.sel||PV.sheet){PV.sel=null;PV.sheet=null;pvRender()}};
 const me=arMe(),op=arOpp(),pm=PV.pl[me];
 const top=$('div');top.className='artop';o.append(top);
 const info=$('div');info.className='arinfo';info.append($('b',PV.turn?'Zug '+PV.turn:'Start'),PV.turn&&PV.pl.length>1?' · Runde '+pvRound():'');
 if(PV.turn){const ph=$('div');ph.className='arphases';PHASES.forEach(([ic,t],k)=>{const b=pvBtn(ic,()=>{PV.phase=(PV.phase||0)==k?(k+1)%PHASES.length:k;pvSave();pvRender()},'arph'+((PV.phase||0)==k?' on':''));b.title=t;ph.append(b)});
  info.append(ph,Object.assign($('span',PHASES[PV.phase||0][1]),{className:'arphname'}))}
 top.append(info);
 const tr=$('div');tr.className='artools';
 if(op!=null)tr.append(arIcon('⇅','Seite wechseln: die andere Hand zeigen',()=>{PV.view=1-me;PV.sel=null;pvRender()},'','arswapq'));
 tr.append(arIcon('↶','Rückgängig (Z)',()=>{if(!PVH.length)return;PV=JSON.parse(PVH.pop());pvSave();pvRender()},'','arundo'),
  Object.assign(arIcon('📱','Quer + Vollbild',()=>tableLandscape(),'arrot','tquer2')),
  arIcon('⚙','Menü: Ansicht, Tokens, Würfel, Statistik, Protokoll, Partie beenden',()=>{PV.sheet=PV.sheet&&PV.sheet.kind=='menu'?null:{kind:'menu'};pvRender()},'','armenu'),
  arIcon('✕','Schließen (Esc), die Partie bleibt gespeichert',pvClose,'','arclose'));
 top.append(tr);
 if(op!=null)o.append(arPlayerBar(op,true));
 const field=$('div');field.className='arfield';o.append(field);
 if(op!=null)field.append(arHalf(op,true),Object.assign($('div'),{className:'armid'}));
 field.append(arHalf(me,false));
 const bot=$('div');bot.className='arbottom';o.append(bot);
 bot.append(arPlayerBar(me,false),arHand(me));
 const go=$('div');go.className='argobox';
 if(PV.turn&&!PV.done){const mine=PV.act==me;
  go.append(pvBtn('🃏',()=>arDo(()=>{pvDraw(pm,1);pvLog(pm.name+' zieht eine Karte')}),'aricon ardraw'));
  const g=pvBtn(PV.pl.length>1?(mine?'Zug beenden':'Weiter: '+PV.pl[PV.act].name):'Nächster Zug',pvNext,'argo');g.id='argo';g.title='Leertaste';go.append(g)}
 else if(PV.done)go.append(pvBtn('⟲ Neue Partie',()=>pvStart(PV.pl.length>1),'argo'));
 bot.append(go);
 const sb=arSelBar();if(sb)o.append(sb);
 const m=(!PV.turn||PV.bottom)&&!PV.done?arMull():null;if(m)o.append(m);
 const sh=arSheet();if(sh)o.append(sh)}
document.addEventListener('keydown',e=>{const o=E('pv');if(!o||o.hidden||!PV||/INPUT|TEXTAREA|SELECT/.test((e.target.tagName||'')))return;
 const k=e.key.toLowerCase();
 if(k=='escape'){e.preventDefault();if(PV.sheet||PV.sel){PV.sheet=null;PV.sel=null;pvRender()}else if(E('czoom'))E('czoom').remove();else pvClose()}
 else if(k==' '&&PV.turn&&!PV.done){e.preventDefault();pvNext()}
 else if(k=='d'&&PV.turn){const p=PV.pl[arMe()];arDo(()=>{pvDraw(p,1);pvLog(p.name+' zieht eine Karte')})}
 else if(k=='z'){if(PVH.length){PV=JSON.parse(PVH.pop());pvSave();pvRender()}}
 else if(k=='t'&&PV.sel&&PV.sel.zone=='bf'){const p=PV.pl[PV.sel.pi];const c=p.bf.find(x=>x.id==PV.sel.id);if(c)arDo(()=>{c.tap=!c.tap},false)}});

function pvResume(){try{const s=JSON.parse(localStorage.getItem('pvgame')||'null');if(s&&s.pl){PV=s;PVH=[];pvUid=Math.max(pvUid,...PV.pl.flatMap(p=>[...p.lib,...p.hand,...p.bf,...p.gy,...p.ex,...p.cz].map(c=>c.id)),0);pvOpen();return true}}catch(e){}return false}

// ---- Spieltisch
let tg=null;try{tg=JSON.parse(localStorage.getItem('tablegame')||'null')}catch(e){}
const tgStore=()=>{try{localStorage.setItem('tablegame',JSON.stringify(tg))}catch(e){}};
const tgSave=()=>{tgStore();if(tg&&tg.room&&!roomApplying)roomPushSoon()};
// ---------- Gemeinsamer Tisch: mehrere Geräte, jedes steuert sein eigenes Feld ----------
let roomApplying=false,roomLoopId=0,roomPushT=null,roomInflight=false,roomPendingRender=false;window.tPress=false;
const tClient=()=>{let c='';try{c=localStorage.getItem('tclient')||''}catch(e){}if(!c){c=Math.random().toString(36).slice(2)+Date.now().toString(36);try{localStorage.setItem('tclient',c)}catch(e){}}return c};
const RGLOB=['turn','active','monarch','rot','start'];
const pJSON=p=>JSON.stringify({name:p.name,deck:p.deck,life:p.life,poison:p.poison,cmd:p.cmd,conceded:!!p.conceded});
function roomSnap(){tg.room.synced=tg.players.map(pJSON);tg.room.gsync=JSON.stringify(RGLOB.map(k=>tg[k]))}
function roomApply(r){if(!tg||!tg.room)return;if(r.error){tg.room.lost=r.error;tgStore();tableGame();return}
 const R=tg.room;R.lost='';R.ver=r.ver;R.claims=r.claims||{};R.closed=r.closed||'';if(r.seat!=null)R.seat=r.seat;R.host=!!r.host;
 const st=r.state||{};const dirty=new Set();(tg.players||[]).forEach((p,i)=>{if(R.synced&&R.synced[i]!==pJSON(p))dirty.add(i)});
 const gdirty=R.gsync&&R.gsync!==JSON.stringify(RGLOB.map(k=>tg[k]));
 roomApplying=true;try{
  const np=(st.players||[]).map((q,i)=>dirty.has(i)&&tg.players[i]?tg.players[i]:{name:q.name,deck:q.deck,life:q.life,poison:q.poison,cmd:q.cmd||{},conceded:!!q.conceded});
  const synced=(st.players||[]).map(q=>pJSON({name:q.name,deck:q.deck,life:q.life,poison:q.poison,cmd:q.cmd||{},conceded:!!q.conceded}));
  tg.players=np;if(!gdirty)RGLOB.forEach(k=>{if(k in st)tg[k]=st[k]});
  R.synced=synced;R.gsync=JSON.stringify(RGLOB.map(k=>st[k]));tgStore()}finally{roomApplying=false}
 if(window.tPress){roomPendingRender=true}else tableGame()}
async function roomLoop(){const my=++roomLoopId;while(tg&&tg.room&&my==roomLoopId&&!tg.room.closed){
 const r=await J('/api/room_get?'+new URLSearchParams({code:tg.room.code,since:tg.room.ver||0,client:tClient()}));
 if(my!=roomLoopId||!tg||!tg.room)return;
 if(r.error&&!/nicht gefunden/.test(r.error)){tg.room.lost='Verbindung unterbrochen, versuche erneut …';tableGame();await new Promise(z=>setTimeout(z,2500));continue}
 roomApply(r);if(r.error)return}}
function roomPushSoon(){clearTimeout(roomPushT);roomPushT=setTimeout(roomPush,120)}
async function roomPush(){if(!tg||!tg.room||tg.room.closed)return;if(roomInflight){roomPushSoon();return}
 const R=tg.room,pl={};tg.players.forEach((p,i)=>{if(!R.synced||R.synced[i]!==pJSON(p))if(R.host||i==R.seat)pl[i]=p});
 const gl={};RGLOB.forEach(k=>{gl[k]=tg[k]===undefined?null:tg[k]});
 const gch=R.gsync!==JSON.stringify(RGLOB.map(k=>tg[k]));if(!Object.keys(pl).length&&!gch)return;
 roomInflight=true;const r=await J('/api/room_push',{code:R.code,client:tClient(),players:JSON.stringify(pl),glob:JSON.stringify(gch?gl:{})});roomInflight=false;
 if(r&&!r.error){/* gesendete Stände gelten als abgeglichen, sofern seither nicht erneut geändert */
  Object.keys(pl).forEach(i=>{if(R.synced)R.synced[i]=JSON.stringify(JSON.parse(pJSON(pl[i])))});if(gch)R.gsync=JSON.stringify(RGLOB.map(k=>tg[k]));roomApply(r)}}
async function roomCreate(seat){const st={players:tg.players.map(p=>JSON.parse(pJSON(p))),seat:seat};RGLOB.forEach(k=>{if(tg[k]!=null)st[k]=tg[k]});
 const r=await J('/api/room_create',{state:JSON.stringify(st),client:tClient()});if(r.error){alert(r.error);return}
 tg.room={code:r.code,host:true,seat:seat,ver:r.ver,claims:{[seat]:tClient()}};roomSnap();tgStore();roomLoop();tableGame()}
const roomLink=c=>location.origin+location.pathname+'?join='+c+'#spieltisch';
async function roomJoin(code,box){code=(code||'').trim().toUpperCase();if(!code)return;box.innerHTML='';P(box,'Verbinde mit Tisch '+code+' …','hint');
 const r=await J('/api/room_get?'+new URLSearchParams({code:code,since:0,client:tClient(),wait:'0'}));box.innerHTML='';
 if(r.error){P(box,r.error,'warn');return}if(r.closed){P(box,'Diese Partie ist bereits beendet.','warn');return}
 P(box,'Welcher Platz bist du?');const g=$('div');g.className='tseats';
 r.state.players.forEach((p,i)=>{const taken=r.claims[i]&&r.claims[i]!=tClient();const b=$('button',p.name+(p.deck?' · '+p.deck:'')+(taken?' (vergeben)':''));b.type='button';b.disabled=!!taken;b.dataset.seat=i;
  b.onclick=async()=>{const c=await J('/api/room_claim',{code:code,seat:i,client:tClient()});if(c.error){P(box,c.error,'warn');return}
   tg={players:[],turn:1,start:Date.now(),room:{code:code,host:false,seat:i,ver:0}};roomApplying=true;roomApplying=false;roomApply(c);tableSetup();roomLoop();tableGame();
   try{history.replaceState(null,'',location.pathname+'#spieltisch')}catch(e){}};g.append(b)});box.append(g)}
function roomLeave(){roomLoopId++;tg=null;tgStore();tableSetup();tableGame()}
// nach Neuladen: Verbindung zum gemeinsamen Tisch wieder aufnehmen
if(tg&&tg.room&&!tg.room.closed)setTimeout(()=>{if(tg&&tg.room)roomLoop()},300);
function roomQR(el,text){const draw=()=>{try{const q=qrcode(0,'M');q.addData(text);q.make();el.innerHTML=q.createSvgTag({cellSize:4,margin:2,scalable:true})}catch(e){el.textContent=''}};
 if(window.qrcode)draw();else{const sc=document.createElement('script');sc.src='/qr.js';sc.onload=draw;document.head.append(sc)}}
// Gastgeber-Bereich: Code, QR, Teilnehmer; vor dem Teilen fragen, welcher Platz der eigene ist
function roomHostBox(o){const b=$('div');b.className='roombox';
 if(!tg.room){b.append($('b','📡 Gemeinsamer Tisch: '),'Mitspieler steuern ihr Feld vom eigenen Handy. Dein Platz: ');const ss=$('select');ss.id='tmyseat';
  tg.players.forEach((p,i)=>{const op=$('option',p.name);op.value=i;ss.append(op)});const go=$('button','📡 Tisch teilen');go.type='button';go.id='troom';go.className='primary';
  go.onclick=()=>roomCreate(+ss.value);b.append(ss,' ',go);o.append(b);return}
 const R=tg.room,n=tg.players.length,con=Object.keys(R.claims||{}).length;
 b.append($('b','📡 Tisch '),$('span',R.code),' · '+con+' von '+n+' verbunden ');b.querySelector('span').className='tcode';b.querySelector('span').id='tcode';
 const det=$('details');det.className='roomqr';const sm=$('summary','QR-Code & Link zum Beitreten');det.append(sm);const qr=$('div');qr.className='qrbox';const ln=$('input');ln.readOnly=true;ln.value=roomLink(R.code);ln.size=40;
 const cp=$('button','Link kopieren');cp.type='button';cp.onclick=()=>{try{navigator.clipboard.writeText(ln.value);cp.textContent='✓ kopiert'}catch(e){ln.select()}};
 det.addEventListener('toggle',()=>{if(det.open&&!qr.innerHTML)roomQR(qr,ln.value)});
 det.append(qr,ln,' ',cp);if(navigator.share){const sh=$('button','Teilen …');sh.type='button';sh.onclick=()=>navigator.share({title:'Manaschmiede: Tisch '+R.code,url:ln.value}).catch(()=>{});det.append(' ',sh)}
 const who=$('div');who.className='hint';who.textContent='Plätze: '+tg.players.map((p,i)=>p.name+(R.claims&&R.claims[i]?(R.claims[i]==tClient()?' (du)':' ✓'):' –')).join(' · ');
 const al=$('label');const cb=$('input');cb.type='checkbox';cb.id='tall';cb.checked=!!R.all;cb.onchange=()=>{R.all=cb.checked;tgStore();tableGame()};al.append(cb,' alle Felder anzeigen und steuern (z. B. wenn ein Handy ausfällt)');
 b.append(det,who,al);o.append(b)}
function roomGuestBox(o){const b=$('div');b.className='roombox';const R=tg.room;
 b.append($('b','📡 Tisch '+R.code),' · du spielst als ',$('b',(tg.players[R.seat]||{}).name||'?'),' ');
 const lv=$('button','Tisch verlassen');lv.type='button';lv.id='tleave';lv.onclick=()=>{if(lv.textContent!='Wirklich verlassen?'){lv.textContent='Wirklich verlassen?';return}roomLeave()};b.append(lv);
 P(b,'Speichern und Sieger wählen macht der Gastgeber.','hint');o.append(b)}
// Ansicht am eigenen Handy: eigenes Feld groß, Mitspieler klein darüber
function tableShared(o){const R=tg.room,me=R.seat;const n=tg.players.length;
 const ot=$('div');ot.className='tothers';tg.players.forEach((p,i)=>{if(i==me)return;const c=$('div');c.className='tother'+(lostWhy(p)?' out':'')+(tg.active==i?' act':'');c.dataset.i=i;
  const cm=Math.max(0,...Object.values(p.cmd||{}));c.append($('b',p.name+(tg.monarch==i?' 👑':'')),$('span',String(p.life)),$('small',(p.poison?'☠'+p.poison+' ':'')+(cm?'⚔'+cm:'')));
  c.querySelector('span').className='ol';ot.append(c)});o.append(ot);
 const f=$('div');f.id='tfield';f.className='solo';const row=$('div');row.className='trow';row.style.gridTemplateColumns='1fr';row.append(tPanel(me));f.append(row);
 const c=$('div');c.className='tcen';const cb=(t,ti,id,fn)=>{const b=$('button',t);b.type='button';b.title=ti;b.id=id;b.onclick=e=>{e.stopPropagation();fn()};return b};
 const tn=$('b','Zug '+tg.turn);tn.id='tturn';
 c.append(tn,cb('⏭','Nächster Zug','tnext',()=>{let k=tg.active||0;for(let s2=0;s2<n;s2++){k=(k+1)%n;if(!lostWhy(tg.players[k]))break}tg.active=k;tg.turn++;tgSave();tableGame()}),
  cb('⛶','Vollbild','tfull',()=>{try{document.fullscreenElement?document.exitFullscreen():f.requestFullscreen()}catch(e){}}));
 f.append(c);o.append(f)}
let wake=null;const keepAwake=async on=>{try{if(on&&navigator.wakeLock&&!wake)wake=await navigator.wakeLock.request('screen');if(!on&&wake){wake.release();wake=null}}catch(e){}};
async function tableSetup(){const o=E('tsetup');o.innerHTML='';if(tg){o.style.display='none';return}o.style.display='';
 {const jb=$('div');jb.className='roombox';jb.append($('b','📡 Einem Tisch beitreten: '));const ci2=$('input');ci2.id='tjoincode';ci2.size=6;ci2.maxLength=4;ci2.placeholder='Code';ci2.style.textTransform='uppercase';
  const jg=$('button','Beitreten');jg.type='button';jg.id='tjoin';const jr=$('div');jr.id='tjoinres';jg.onclick=()=>roomJoin(ci2.value,jr);ci2.onkeydown=e=>{if(e.key=='Enter')jg.click()};
  jb.append(ci2,' ',jg,jr);P(jb,'Code oder QR-Code vom Gastgeber eingeben oder unten selbst eine Partie starten und mit „📡 Tisch teilen“ freigeben.','hint');o.append(jb);
  const jq=new URLSearchParams(location.search).get('join');if(jq&&!o.dataset.auto){o.dataset.auto=1;ci2.value=jq;roomJoin(jq,jr)}}
 const dl=await J('/api/decks');const decks=Array.isArray(dl)?dl:(dl.decks||[]);
 const n=$('select');n.id='tn';[2,3,4,5,6].forEach(k=>{const op=$('option',k+' Spieler');op.value=k;n.append(op)});n.value=4;
 const lf=$('input');lf.id='tlife';lf.size=4;lf.value=40;
 const rows=$('div');const mk=()=>{rows.innerHTML='';for(let i=0;i<+n.value;i++){const r=$('div');const nm=$('input');nm.size=14;nm.placeholder='Spieler '+(i+1);nm.className='tpname';
   const dk=$('input');dk.size=28;dk.placeholder='Deck (gespeichert oder frei)';dk.className='tpdeck';dk.setAttribute('list','tdecklist');r.append(nm,' ',dk);rows.append(r)}};
 n.onchange=mk;mk();const dlist=$('datalist');dlist.id='tdecklist';decks.forEach(d=>{const op=$('option');op.value=d.name;dlist.append(op)});
 const go=$('button','▶ Partie starten');go.type='button';go.className='primary';go.id='tstart';
 go.onclick=()=>{const life=Math.max(1,parseInt(lf.value)||40);const ps=[...rows.children].map((r,i)=>({name:r.querySelector('.tpname').value.trim()||'Spieler '+(i+1),
   deck:r.querySelector('.tpdeck').value.trim(),life:life,poison:0,cmd:{}}));tg={players:ps,turn:1,start:Date.now()};tgSave();tableSetup();tableGame()};
 o.append($('label','Spielerzahl: '),n,' ',$('label',' Startleben: '),lf,rows,dlist,go)}
function lostWhy(p){if(p.conceded)return 'aufgegeben';if(p.life<=0)return 'Leben 0';if(p.poison>=10)return '10 Gift';
 const c=Object.entries(p.cmd).find(([k,v])=>v>=21);return c?'21 Commander-Schaden von '+tg.players[+c[0]].name:''}
let tview='tisch';try{tview=localStorage.getItem('tableview')||'tisch'}catch(e){}
const setTview=v=>{tview=v;try{localStorage.setItem('tableview',v)}catch(e){};tableGame()};
// Farben ohne Kartenbild: nach Farbidentität des Commanders, sonst feste Reihenfolge
const TCOL={W:'#c9b98f',U:'#2f6fae',B:'#3a3340',R:'#b5432f',G:'#3d7f45'},TPAL=['#7a3b8f','#2f6fae','#b5432f','#3d7f45','#a8843a','#4a5a6a'];
const tArt={};async function tArtFor(p){const k=(p.deck||'').toLowerCase();if(!k)return null;if(k in tArt)return tArt[k];tArt[k]=null;
 try{let cmd=p.deck;const dl=await J('/api/decks');const d=(Array.isArray(dl)?dl:(dl.decks||[])).find(x=>x.name.toLowerCase()==k);if(d&&d.commander)cmd=d.commander.split(' // ')[0].split(' + ')[0].trim();
  const c=await J('/api/card?name='+encodeURIComponent(cmd));if(c&&c.name)tArt[k]={img:(c.image||'').replace('/normal/','/art_crop/'),ci:c.ci||''}}catch(e){}
 return tArt[k]}
function tPanelBg(el,p,i){el.style.backgroundColor=TPAL[i%TPAL.length];tArtFor(p).then(a=>{if(!a)return;
 if(a.img)el.style.backgroundImage='url("'+a.img+'")';else if(a.ci){const cs=[...a.ci].map(c=>TCOL[c]).filter(Boolean);if(cs.length==1)el.style.backgroundColor=cs[0];else if(cs.length)el.style.backgroundImage='linear-gradient(135deg,'+cs.join(',')+')'}})}
function tableGame(){const o=E('tgame');o.innerHTML='';if(!tg){keepAwake(false);return}keepAwake(true);
 if(tg.room&&tg.room.closed){const b=$('div');b.className='roombox';b.append($('b','🏁 '+tg.room.closed));
  const ok=$('button','OK');ok.type='button';ok.className='primary';ok.id='tclosedok';ok.onclick=roomLeave;b.append(' ',ok);o.append(b);return}
 if(tg.room&&tg.room.lost){P(o,'⚠ '+tg.room.lost,'warn');if(/nicht gefunden/.test(tg.room.lost)){const lv=$('button','Tisch verlassen');lv.type='button';lv.onclick=roomLeave;o.append(lv);return}}
 if(tg.room&&!tg.room.host){roomGuestBox(o);if(tg.room.seat==null){P(o,'Kein Platz gewählt.','warn');return}tableShared(o);return}
 if(tview=='tisch'){if(tg.room&&!tg.room.all){roomHostBox(o);tableShared(o);tableEnd(o);return}tableTisch(o);return}
 const vb=$('div');vb.className='tvbar';const tv=$('button','🃏 Tischansicht');tv.type='button';tv.id='tvtisch';tv.onclick=()=>setTview('tisch');vb.append(tv);o.append(vb);
 const bar=$('div');bar.append($('b','Zug '+tg.turn+' '));const nx=$('button','Nächster Zug');nx.type='button';nx.id='tnext';nx.onclick=()=>{tg.turn++;tgSave();tableGame()};bar.append(nx);o.append(bar);
 tg.players.forEach((p,i)=>{const d=$('div');const why=lostWhy(p);d.className='pl'+(why?' out':'');d.dataset.i=i;
  d.append($('b',p.name),p.deck?$('div',p.deck):'');const lv=$('div',String(p.life));lv.className='life';d.append(lv);
  const bt=(t,f,cls)=>{const b=$('button',t);b.type='button';if(cls)b.className=cls;b.onclick=()=>{f();tgSave();tableGame()};return b};
  d.append(bt('−5',()=>p.life-=5),bt('−1',()=>p.life--,'tminus'),bt('+1',()=>p.life++,'tplus'),bt('+5',()=>p.life+=5));
  const ps=$('div','Gift: '+p.poison+' ');ps.append(bt('−',()=>p.poison=Math.max(0,p.poison-1)),bt('+',()=>p.poison++,'tpois'));d.append(ps);
  const cd=$('div');cd.className='cd';cd.append($('div','Commander-Schaden erhalten von:'));
  tg.players.forEach((q,j)=>{if(j==i)return;const v=p.cmd[j]||0;const r=$('div',q.name+': '+v+' ');
   r.append(bt('−',()=>{p.cmd[j]=Math.max(0,v-1);p.life++}),bt('+',()=>{p.cmd[j]=v+1;p.life--},'tcmd'));cd.append(r)});d.append(cd);
  if(why)d.append($('div','verloren: '+why));else d.append(bt('aufgeben',()=>p.conceded=true));
  o.append(d)});
 tableEnd(o)}
function tableEnd(o){if(tg.room&&!tg.room.host)return;if(tview!='tisch'||(tg.room&&tg.room.all)||!tg.room)roomHostBox(o);const alive=tg.players.map((p,i)=>[p,i]).filter(([p])=>!lostWhy(p));
 const end=$('div');end.className='savebox';end.append($('b','Partie beenden: '));const ws=$('select');ws.id='twinner';
 const o0=$('option','kein Sieger / Unentschieden');o0.value=-1;ws.append(o0);tg.players.forEach((p,i)=>{const op=$('option',p.name);op.value=i;ws.append(op)});
 if(alive.length==1)ws.value=alive[0][1];const nt=$('input');nt.size=30;nt.placeholder='Notiz (optional)';nt.id='tnote';
 const sv=$('button','Speichern');sv.type='button';sv.className='primary';sv.id='tsave';
 sv.onclick=async()=>{const r=await J('/api/game_save',{games:JSON.stringify([{players:tg.players.map(p=>({name:p.name,deck:p.deck})),winner:+ws.value,turns:tg.turn,note:nt.value}])});
  if(r.error){P(end,r.error,'warn');return}gnFromTable(+ws.value>=0?tg.players[+ws.value].name:'');if(tg.room){roomLoopId++;J('/api/room_close',{code:tg.room.code,client:tClient(),result:'Partie beendet'+(+ws.value>=0?', Sieger: '+tg.players[+ws.value].name:'')+'.'})}tg=null;tgSave();tableSetup();tableGame();tableStats(r)};
 const ab=$('button','Abbrechen ohne Speichern');ab.type='button';ab.onclick=()=>{if(ab.textContent!='Wirklich abbrechen?'){ab.textContent='Wirklich abbrechen?';return}if(tg.room){roomLoopId++;J('/api/room_close',{code:tg.room.code,client:tClient(),result:'Partie abgebrochen.'})}tg=null;tgSave();tableSetup();tableGame()};
 end.append(ws,' ',nt,' ',sv,' ',ab);o.append(end)}
// ---------- Spielabend: Spieler, gemischte Vierer-Tische, Siege, Rangliste, optionale Saison
let GN=null,GNL=null;
async function gnInit(){const box=E('gnbox');if(!box)return;GNL=await J('/api/gn_list');gnHome()}
function gnStand(rows){const t=$('table');t.className='gnst';const h=t.insertRow();['Platz','Spieler','Siege','Partien','Quote'].forEach(x=>h.append($('th',x)));
 rows.forEach(e=>{const tr=t.insertRow();[e.rank+'.',e.name,e.wins,e.games,e.rate+' %'].forEach(v=>tr.insertCell().textContent=v)});
 if(!rows.length){const tr=t.insertRow();const c=tr.insertCell();c.colSpan=5;c.textContent='Noch keine Ergebnisse.'}return t}
function gnHome(){const box=E('gnbox');box.innerHTML='';GN=null;const L=GNL||{nights:[],seasons:[],known:[]};
 const nb=$('button','➕ Neuer Spielabend');nb.type='button';nb.className='primary';nb.id='gnnew';nb.onclick=gnNewForm;box.append(nb);
 if(L.nights.length){const t=$('table');t.id='gnlist';box.append($('h4','Bisherige Spielabende'),t);
  L.nights.forEach(n=>{const tr=t.insertRow();const a=$('a',n.name);a.href='#';a.onclick=async e=>{e.preventDefault();gnShow(await J('/api/gn_get',{id:n.id}))};
   tr.insertCell().append(a);[n.created.slice(0,10),n.season?'Saison '+n.season:'',n.players+' Spieler',n.rounds+' Runden',n.closed?'abgeschlossen':'läuft'].forEach(x=>tr.insertCell().textContent=x)})}
 if(L.seasons.length){const sel=$('select');sel.id='gnseason';sel.append(new Option('Gesamtwertung aller Abende',''));L.seasons.forEach(x=>sel.append(new Option('Saison '+x,x)));
  const out=$('div');sel.onchange=async()=>{const r=await J('/api/gn_list',{season:sel.value});out.innerHTML='';out.append(gnStand(sel.value?r.season.standings:r.all))};
  box.append($('h4','Rangliste'),sel,out);out.append(gnStand(L.all||[]))}
 else if((L.all||[]).length){box.append($('h4','Gesamtwertung'),gnStand(L.all))}}
function gnNewForm(){const box=E('gnbox');box.innerHTML='';const L=GNL||{known:[],seasons:[]};
 box.append($('h4','Neuer Spielabend'));
 const nm=$('input');nm.id='gnname';nm.placeholder='Name, z. B. Commander-Freitag';nm.size=30;
 const se=$('input');se.id='gnseas';se.placeholder='Saison (optional)';se.size=16;se.setAttribute('list','gnseasl');
 const dl=$('datalist');dl.id='gnseasl';L.seasons.forEach(x=>dl.append(new Option(x)));
 const ta=$('textarea');ta.id='gnplayers';ta.rows=6;ta.cols=30;ta.placeholder='Mitspieler, einer pro Zeile';
 const chips=$('p');chips.className='chips';L.known.forEach(k=>{const c=$('button',k);c.type='button';c.onclick=()=>{const v=ta.value.split('\\n').map(x=>x.trim()).filter(Boolean);if(!v.some(x=>x.toLowerCase()==k.toLowerCase())){v.push(k);ta.value=v.join('\\n')}};chips.append(c)});
 const lg=$('input');lg.type='checkbox';lg.id='gnlog';lg.checked=true;const ll=$('label');ll.append(lg,' Ergebnisse auch ins Spielprotokoll übernehmen');
 const ok=$('button','Anlegen');ok.type='button';ok.className='primary';ok.id='gncreate';const back=$('button','Zurück');back.type='button';back.onclick=gnHome;const m=$('p');
 box.append(nm,' ',se,dl,$('br'),ta,$('br'));if(L.known.length)box.append($('span','Bekannte Spieler: '),chips);box.append(ll,$('br'),ok,' ',back,m);
 ok.onclick=async()=>{const r=await J('/api/gn_create',{name:nm.value,season:se.value,log:lg.checked?1:0,players:JSON.stringify(ta.value.split('\\n'))});
  if(r.error){m.className='warn';m.textContent=r.error;return}GNL=null;gnShow(r)}}
function gnUrl(){return location.origin+'/n/'+GN.night.code}
function gnShow(d){if(d.error){P(E('gnbox'),d.error,'warn');return}GN=d;const box=E('gnbox');box.innerHTML='';const n=d.night;
 const nm={};d.players.forEach(p=>nm[p.idx]=p.name);
 const head=$('div');head.className='gnhead';head.append($('b','🏆 '+n.name),' ',$('span',(n.season?'Saison '+n.season+' · ':'')+n.created.slice(0,10)+(n.closed?' · abgeschlossen':'')));box.append(head);
 // Teilen: QR-Code + Link für Mitspieler (ohne Anmeldung)
 const sh=$('details');sh.id='gnshare';sh.append($('summary','📱 Mitspieler-Link & QR-Code'));const q=$('div');q.className='gnqr';const u=$('code',gnUrl());
 const cp=$('button','Link kopieren');cp.type='button';cp.onclick=()=>copyText(gnUrl(),cp);sh.append(q,u,' ',cp,
  $('p','Wer den Link hat, sieht Tische und Rangliste und kann Sieger eintragen, auch ohne Konto. Ergebnisse erscheinen hier automatisch.'));
 sh.ontoggle=()=>{if(sh.open&&!q.firstChild)roomQR(q,gnUrl())};box.append(sh);
 // Spieler
 const pl=$('details');pl.id='gnpl';pl.append($('summary','👥 Spieler ('+d.players.filter(p=>p.active).length+' anwesend)'));
 d.players.forEach(p=>{const row=$('div');row.className='gnp';const cb=$('input');cb.type='checkbox';cb.checked=!!p.active;cb.disabled=!!n.closed;
  cb.onchange=async()=>gnShow(await J('/api/gn_player',{id:n.id,idx:p.idx,active:cb.checked?1:0}));
  const dk=$('input');dk.placeholder='Deck (optional)';dk.value=p.deck||'';dk.size=22;dk.disabled=!!n.closed;
  dk.onchange=async()=>{GN=await J('/api/gn_player',{id:n.id,idx:p.idx,deck:dk.value})};
  const lb=$('label');lb.append(cb,' '+p.name);row.append(lb,' ',dk);pl.append(row)});
 if(!n.closed){const ad=$('input');ad.placeholder='Spieler hinzufügen';ad.id='gnadd';const ab=$('button','+');ab.type='button';
  const add=async()=>{if(ad.value.trim())gnShow(await J('/api/gn_player',{id:n.id,name:ad.value.trim()}))};ab.onclick=add;ad.onkeydown=e=>{if(e.key=='Enter')add()};pl.append(ad,ab)}
 box.append(pl);
 // Runden
 const acts=$('p');if(!n.closed){const rb=$('button',d.rounds.length?'🎲 Nächste Runde auslosen':'🎲 Erste Runde auslosen');rb.type='button';rb.className='primary';rb.id='gnround';
  rb.onclick=async()=>{let r=await J('/api/gn_round',{id:n.id});if(r.warn){if(!confirm(r.warn))return;r=await J('/api/gn_round',{id:n.id,force:1})}gnShow(r);
   if(r.repeats)arToastMsg('Nicht alle Paarungen ließen sich vermeiden, einige treffen sich erneut.')};acts.append(rb);
  if(d.rounds.length){const ud=$('button','Letzte Runde verwerfen');ud.type='button';ud.id='gnundo';ud.onclick=async()=>{if(confirm('Letzte Runde samt Ergebnissen verwerfen?'))gnShow(await J('/api/gn_round_delete',{id:n.id}))};acts.append(' ',ud)}}
 box.append(acts);
 d.rounds.slice().reverse().forEach((r,ri)=>{const det=$('details');det.className='gnround';det.open=ri==0;det.append($('summary','Runde '+r.round+': '+r.pods.filter(p=>p.winner!=null).length+'/'+r.pods.length+' Tische fertig'));
  r.pods.forEach(p=>{const pd=$('div');pd.className='gnpod';pd.append($('b','Tisch '+p.tab+': '));
   p.seats.forEach(s=>{const b=$('button',(p.winner==s?'👑 ':'')+nm[s]);b.type='button';b.className=p.winner==s?'gnwin':'';b.disabled=!!n.closed;b.dataset.pod=p.id;b.dataset.seat=s;
    b.onclick=async()=>gnShow(await J('/api/gn_report',{id:n.id,pod:p.id,winner:p.winner==s?'none':s}));pd.append(b)});
   const dr=$('button','Unentschieden');dr.type='button';dr.className=p.winner==-1?'gnwin':'';dr.disabled=!!n.closed;dr.onclick=async()=>gnShow(await J('/api/gn_report',{id:n.id,pod:p.id,winner:p.winner==-1?'none':-1}));pd.append(dr);
   const pt=$('button','▶ Am Handy-Tisch spielen');pt.type='button';pt.title='Öffnet den Testtisch mit diesen Spielern';pt.disabled=!!n.closed;pt.onclick=()=>gnPlay(p,nm);pd.append(pt);det.append(pd)});box.append(det)});
 box.append($('h4','Rangliste dieses Abends'),gnStand(d.standings));
 if(d.season)box.append($('h4','Saison '+d.season.name+' ('+d.season.nights+' Abende)'),gnStand(d.season.standings));
 const ft=$('p');const cl=$('button',n.closed?'Wieder öffnen':'✔ Abend abschließen');cl.type='button';cl.id='gnclose';cl.onclick=async()=>gnShow(await J('/api/gn_set',{id:n.id,closed:n.closed?0:1}));
 const del=$('button','Löschen');del.type='button';del.onclick=async()=>{if(!confirm('Spielabend samt Ergebnissen löschen?'))return;await J('/api/gn_delete',{id:n.id});GNL=null;gnInit()};
 const bk=$('button','← Übersicht');bk.type='button';bk.onclick=gnInit;ft.append(cl,' ',del,' ',bk);box.append(ft);gnPoll()}
let GNT=null;function gnPoll(){clearTimeout(GNT);GNT=setTimeout(async()=>{if(!GN||!E('gnbox')||!E('gnbox').offsetParent)return;if(document.activeElement&&E('gnbox').contains(document.activeElement)&&document.activeElement.tagName=='INPUT'){gnPoll();return}
 const r=await J('/api/gn_get',{id:GN.night.id});if(!r.error&&JSON.stringify(r.rounds)!=JSON.stringify(GN.rounds))gnShow(r);else gnPoll()},15000)}
function arToastMsg(t){if(typeof arToast=='function'&&E('pv')&&!E('pv').hidden)arToast(t);else alert(t)}
function gnPlay(pod,nm){const names=pod.seats.map(s=>nm[s]);const dk={};GN.players.forEach(p=>dk[p.idx]=p.deck||'');const decks=pod.seats.map(s=>dk[s]);
 try{localStorage.setItem('gnpod',JSON.stringify({night:GN.night.id,pod:pod.id,names}))}catch(e){}
 const tg=E('tsetup');if(tg&&typeof tableSetupNames=='function'){tableSetupNames(names,decks)}else{copyText(names.join(', '))}
 const tb=E('tablebox');if(tb){tb.open=true;tb.scrollIntoView({behavior:'smooth'})}}
// Ergebnis vom Lebenszähler-Tisch an den Spielabend melden (wenn der Tisch aus einem Spielabend gestartet wurde)
async function gnFromTable(winnerName){let g=null;try{g=JSON.parse(localStorage.getItem('gnpod')||'null')}catch(e){}
 if(!g||!winnerName)return false;const d=await J('/api/gn_get',{id:g.night});if(d.error)return false;
 const p=d.players.find(x=>x.name==winnerName);const pod=d.rounds.flatMap(r=>r.pods).find(x=>x.id==g.pod);if(!p||!pod||pod.winner!=null)return false;
 await J('/api/gn_report',{id:g.night,pod:g.pod,winner:p.idx,fromtable:1});try{localStorage.removeItem('gnpod')}catch(e){}if(GN&&GN.night.id==g.night)gnShow(await J('/api/gn_get',{id:g.night}));return true}
// ---------- Impressum & Datenschutz (Administrator)
async function legalDialog(){const b=dlgOpen('Impressum & Datenschutz');const L=await J('/api/legal');if(L.error){P(b,L.error,'warn');return}
 P(b,'Diese Angaben erscheinen auf /impressum und /datenschutz. Pflicht für einen aus dem Internet erreichbaren Server: Name, ladungsfähige Anschrift, E-Mail.','hint');
 const f=[['legal_name','Name (Vor- und Nachname)'],['legal_addr','Anschrift (Straße, PLZ Ort)',1],['legal_mail','E-Mail'],['legal_phone','Telefon (optional)'],['legal_host','Hosting (z. B. „einem eigenen Server in Deutschland“)'],['legal_extra','Weitere Angaben (optional)',1]];
 const ins={};f.forEach(([k,l,ml])=>{const i=$(ml?'textarea':'input');i.id='lg-'+k;i.value=L[k]||'';if(ml){i.rows=2}i.style.width='100%';ins[k]=i;const lb=$('label');lb.append($('span',l),$('br'),i);b.append(lb,$('br'))});
 const sv=$('button','Speichern');sv.type='button';sv.className='primary';sv.id='lgsave';const m=$('p');b.append(sv,' ',$('a','Impressum ansehen','/impressum'),' · ',$('a','Datenschutz ansehen','/datenschutz'),m);
 b.querySelectorAll('a').forEach(a=>a.target='_blank');
 sv.onclick=async()=>{const o={};for(const k in ins)o[k]=ins[k].value;const r=await J('/api/legal',o);m.className=r.error?'warn':'tag';m.textContent=r.error||'Gespeichert.'}}
function tableSetupNames(names,decks){const n=E('tn');if(!n){setTimeout(()=>tableSetupNames(names,decks),300);return}n.value=Math.min(6,Math.max(2,names.length));n.onchange();
 [...document.querySelectorAll('#tsetup .tpname')].forEach((x,i)=>x.value=names[i]||'');[...document.querySelectorAll('#tsetup .tpdeck')].forEach((x,i)=>x.value=(decks||[])[i]||'');
 const h=E('tsetup');let b=E('gnhint');if(!b){b=$('p');b.id='gnhint';b.className='hint';h.prepend(b)}b.textContent='🏆 Tisch aus dem Spielabend. Der Sieger wird beim Speichern automatisch eingetragen.'}
// Tischansicht: ein großes Feld je Spieler; links tippen −1, rechts +1, halten ±10 (wiederholt)
function tableTisch(o){const n=tg.players.length;if(tg.active==null)tg.active=0;if(tg.rot==null)tg.rot=true;
 const f=$('div');f.id='tfield';const bot=Math.ceil(n/2),top=n-bot;
 f.style.gridTemplateRows=top?'1fr 1fr':'1fr';
 const mkRow=(idx,rot)=>{const r=$('div');r.className='trow'+(rot?' rot':'');r.style.gridTemplateColumns='repeat('+idx.length+',1fr)';idx.forEach(i=>r.append(tPanel(i)));return r};
 const botIdx=[...Array(bot).keys()],topIdx=[...Array(top).keys()].map(k=>bot+k).reverse();
 if(top)f.append(mkRow(topIdx,tg.rot));f.append(mkRow(botIdx,false));
 const c=$('div');c.className='tcen';const cb=(t,ti,id,fn)=>{const b=$('button',t);b.type='button';b.title=ti;b.id=id;b.onclick=e=>{e.stopPropagation();fn()};return b};
 const tn=$('b','Zug '+tg.turn);tn.id='tturn';
 c.append(cb('🎲','Startspieler auslosen','tdice',()=>{const al=tg.players.map((p,i)=>i).filter(i=>!lostWhy(tg.players[i]));const k=al[Math.floor(Math.random()*al.length)];
   tg.active=k;tgSave();tableGame();const el=document.querySelector('#tfield .tp[data-i="'+k+'"]');if(el)el.classList.add('pick')}),
  tn,cb('⏭','Nächster Zug (nächster Spieler am Zug)','tnext',()=>{let k=tg.active;for(let s=0;s<n;s++){k=(k+1)%n;if(!lostWhy(tg.players[k]))break}tg.active=k;tg.turn++;tgSave();tableGame()}),
  cb('🔄','obere Reihe drehen (gegenüber sitzend)','trot',()=>{tg.rot=!tg.rot;tgSave();tableGame()}),
  cb('⛶','Vollbild','tfull',()=>{try{document.fullscreenElement?document.exitFullscreen():f.requestFullscreen()}catch(e){}}),
  cb('📋','Tabellenansicht','tvliste',()=>{if(document.fullscreenElement)document.exitFullscreen();setTview('liste')}));
 f.append(c);o.append(f);P(o,'Links tippen = −1, rechts tippen = +1, gedrückt halten = ±10. ☠/⚔ öffnet Gift, Commander-Schaden und weitere Zähler. 🎲 lost den Startspieler aus.','hint');
 tableEnd(o)}
function tPanel(i){const p=tg.players[i],why=lostWhy(p),d=$('div');d.className='tp'+(why?' out':'')+(tg.active==i?' act':'');d.dataset.i=i;tPanelBg(d,p,i);
 const w=$('div');w.className='tpi';d.append(w);const nm=$('div',p.name+(tg.monarch==i?' 👑':''));nm.className='tpn';if(p.deck)nm.append($('small',p.deck));
 const lv=$('div',String(p.life));lv.className='tl';const dl=$('div');dl.className='tdl';w.append(nm,lv,dl);
 let acc=0,accT=null;const show=dv=>{acc+=dv;dl.textContent=(acc>0?'+':'')+acc;dl.className='tdl on '+(acc<0?'neg':'pos');clearTimeout(accT);accT=setTimeout(()=>{acc=0;dl.className='tdl'},1600)};
 const change=dv=>{p.life+=dv;lv.textContent=p.life;show(dv);tgSave();const nw=!!lostWhy(p);if(nw!=d.classList.contains('out'))tableGame()};
 [['m','−',-1],['p','+',1]].forEach(([cl,sym,sg])=>{const z=$('div',sym);z.className='tz '+cl;z.dataset.d=sg;let t=null,iv=null,held=false;
  const stop=()=>{clearTimeout(t);clearInterval(iv);t=iv=null;if(window.tPress){window.tPress=false;if(roomPendingRender){roomPendingRender=false;setTimeout(tableGame,0)}}};
  z.addEventListener('pointerdown',e=>{e.preventDefault();window.tPress=true;held=false;stop();t=setTimeout(()=>{held=true;change(10*sg);iv=setInterval(()=>change(10*sg),450)},500)});
  z.addEventListener('pointerup',e=>{if(t||iv){const h=held;stop();if(!h)change(sg)}});
  ['pointerleave','pointercancel'].forEach(ev=>z.addEventListener(ev,stop));z.addEventListener('contextmenu',e=>e.preventDefault());w.append(z)});
 if(why){const l=$('div','💀 '+why);l.className='tlost';w.append(l)}
 const ic=$('div');ic.className='tic';const cmax=Math.max(0,...Object.values(p.cmd));
 const ib=(t,id,fn)=>{const b=$('button',t);b.type='button';b.className=id;b.onclick=e=>{e.stopPropagation();fn()};b.addEventListener('pointerdown',e=>e.stopPropagation());return b};
 ic.append(ib('☠ '+p.poison,'tpo',()=>tOverlay(d,i)),ib('⚔ '+cmax,'tco',()=>tOverlay(d,i)));w.append(ic);return d}
function tOverlay(d,i){const p=tg.players[i],w=d.querySelector('.tpi'),ov=$('div');ov.className='tov';
 const x=$('button','✕');x.type='button';x.className='x';x.onclick=e=>{e.stopPropagation();tableGame()};ov.append(x,$('b',p.name));
 const row=(lab,get,set,cls)=>{const r=$('div');r.className='r';const v=$('span',String(get()));v.style.minWidth='2em';
  const b=(t,dv,c)=>{const bb=$('button',t);bb.type='button';if(c)bb.className=c;bb.onclick=e=>{e.stopPropagation();set(dv);v.textContent=get();tgSave()};return bb};
  r.append($('span',lab),b('−',-1),v,b('+',1,cls));ov.append(r)};
 row('☠ Gift',()=>p.poison,dv=>p.poison=Math.max(0,p.poison+dv),'tovpois');
 ov.append($('div','⚔ Commander-Schaden erhalten von (zieht auch Leben ab):'));
 tg.players.forEach((q,j)=>{if(j==i)return;row(q.name,()=>p.cmd[j]||0,dv=>{const v=p.cmd[j]||0;if(v+dv<0)return;p.cmd[j]=v+dv;p.life-=dv},'tovcmd')});
 const r2=$('div');r2.className='r';const mo=$('button',tg.monarch==i?'👑 Monarch abgeben':'👑 Monarch');mo.type='button';mo.onclick=e=>{e.stopPropagation();tg.monarch=tg.monarch==i?null:i;tgSave();tableGame()};
 const cq=$('button',p.conceded?'↩ Aufgabe zurücknehmen':'🏳 aufgeben');cq.type='button';cq.onclick=e=>{e.stopPropagation();p.conceded=!p.conceded;tgSave();tableGame()};
 const ac=$('button','am Zug');ac.type='button';ac.onclick=e=>{e.stopPropagation();tg.active=i;tgSave();tableGame()};
 r2.append(mo,cq,ac);ov.append(r2);ov.addEventListener('pointerdown',e=>e.stopPropagation());w.append(ov)}
function tableStats(r){const o=E('tstats');o.innerHTML='';E('gamecount').textContent=r.count?'('+r.count+' Partien)':'';
 if(!r.count){P(o,'Noch keine Partien gespeichert.','hint');return}
 const tab=(title,list,id)=>{o.append($('div',title));const t=$('table');t.id=id;o.append(t);const hr=t.insertRow();['Name','Partien','Siege','Siegquote'].forEach(x=>hr.append($('th',x)));
  list.forEach(e=>{const tr=t.insertRow();[e.name,e.games,e.wins,e.rate+' %'].forEach(v=>tr.insertCell().textContent=v)})};
 if(r.decks.length)tab('Je Deck:',r.decks,'tstatdecks');tab('Je Spieler:',r.players,'tstatplayers');
 const gl=$('details');gl.append($('summary','Letzte Partien'));o.append(gl);
 r.recent.forEach(g=>{const d=$('div',g.at+(g.source=='forge'?' · Forge':'')+' · '+g.players.map((p,i)=>(i==g.winner?'🏆 ':'')+p.name+(p.deck?' ('+p.deck+')':'')).join(' · ')+(g.turns?' · '+g.turns+' Züge':'')+(g.note?' · '+g.note:''));
  const x=$('button','✕');x.type='button';x.className='sw';x.title='Partie löschen';x.onclick=async()=>tableStats(await J('/api/game_delete',{id:g.id}));d.append(' ',x);gl.append(d)})}
E('tablebox').addEventListener('toggle',()=>{if(E('tablebox').open){tableSetup();tableGame();J('/api/games').then(tableStats)}});
J('/api/games').then(r=>{E('gamecount').textContent=r.count?'('+r.count+' Partien)':''});
if(tg)E('tablebox').open=true;

// ---- Karten tauschen
const exl=E('exclude');
function exList(){return exl.value.split('\\n').map(x=>x.trim()).filter(Boolean)}
function exSave(){const l=[...new Set(exList())];exl.value=l.join('\\n');E('excount').textContent=l.length;
 try{localStorage.setItem('exclude',exl.value)}catch(e){}}
try{exl.value=localStorage.getItem('exclude')||''}catch(e){}
try{E('nogc').checked=localStorage.getItem('nogc')=='1'}catch(e){}
E('nogc').onchange=()=>{try{localStorage.setItem('nogc',E('nogc').checked?'1':'0')}catch(e){}};
exSave();exl.addEventListener('change',exSave);
E('exclear').onclick=()=>{exl.value='';exSave()};
ac(E('exadd'),{get:names(false),pick:n=>{exl.value+=(exl.value.trim()?'\\n':'')+n;E('exadd').value='';exSave()},
 enter:()=>{const v=E('exadd').value.trim();if(v){exl.value+=(exl.value.trim()?'\\n':'')+v;E('exadd').value='';exSave()}}});

function deckNames(){return deck.groups.flatMap(g=>g.cards.map(c=>c.name))}
function recalc(){const all=deck.groups.flatMap(g=>g.cards);
 deck.curve=[0,0,0,0,0,0,0,0];let tot=0,pr=0,mi=0;
 for(const c of all){if(!c.land)deck.curve[Math.min(Math.floor(c.cmc||0),7)]+=c.qty;
  if(c.basic)continue;if(c.eur!=null){tot+=c.eur*c.qty;pr++}else mi++}
 deck.cost={total:tot,priced:pr,missing:mi};
 deck.export=deck.groups.flatMap(g=>g.cards.map(c=>c.qty+' '+c.name)).join('\\n');
 showDeck();if(opp)runCompare(opp)}
async function fetchAlts(c,g,o){return J('/api/alternatives',{name:c.name,group:g.name,ci:deck.ci||'',
 deck:deckNames().join('\\n'),exclude:exList().join('\\n'),nogc:o.nogc?1:0,maxeur:o.maxeur||'',limit:o.limit||12})}
function addBasic(){const l=deck.groups.find(g=>g.name=='Länder');const b=l&&l.cards.filter(c=>c.basic).sort((x,y)=>y.qty-x.qty)[0];
 if(b){b.qty++;return true}return false}
function markOut(name){if(E('dlgun')&&E('dlgun').checked){exl.value+=(exl.value.trim()?'\\n':'')+name;exSave()}}
function closeSwap(){E('dlg').style.display='none'}
E('dlg').onclick=e=>{if(e.target.id=='dlg')closeSwap()};
document.addEventListener('keydown',e=>{if(e.key=='Escape')closeSwap()});
async function openSwap(gi,ci){
 const g=deck.groups[gi],c=g.cards[ci],box=E('dlgin');E('dlg').style.display='block';
 box.innerHTML='';box.append($('h3','Ersatz für '+c.name));
 const opt=$('div');box.append(opt);
 opt.innerHTML='<label><input type=checkbox id=dlgnogc> keine Game Changer</label> &nbsp; '+
  '<label>max. Preis € <input id=dlgmax size=5></label> &nbsp; '+
  '<label><input type=checkbox id=dlgun> „'+c.name.replace(/[<>&]/g,'')+'“ als nicht verfügbar merken</label>';
 E('dlgnogc').checked=E('nogc').checked||c.gc;
 const act=$('p');box.append(act);
 const rm=$('button','Ohne Ersatz entfernen');rm.type='button';act.append(rm);
 const bl=$('button','Durch Standardland ersetzen');bl.type='button';act.append(bl);
 const cl=$('button','Abbrechen');cl.type='button';act.append(cl);cl.onclick=closeSwap;
 rm.onclick=()=>{markOut(c.name);g.cards.splice(ci,1);closeSwap();recalc()};
 bl.onclick=()=>{markOut(c.name);g.cards.splice(ci,1);if(!addBasic())P(E('out'),'Kein Standardland im Deck gefunden.','warn');closeSwap();recalc()};
 const list=$('div');box.append(list);
 async function load(){list.textContent='Suche Alternativen ...';
  const r=await fetchAlts(c,g,{nogc:E('dlgnogc').checked,maxeur:E('dlgmax').value});
  list.innerHTML='';if(r.error){list.append($('p',r.error));return}
  P(list,'Vorschläge: '+r.reason+'.','hint');
  if(!r.cards.length)P(list,'Keine passenden Alternativen gefunden. Vielleicht die Filter lockern?');
  for(const a of r.cards){const row=$('div');row.className='alt';
   if(a.image){const im=$('img');im.src=a.image;im.loading='lazy';row.append(im)}
   const n=$('div');n.className='n';n.append(cardName(a.name,a.scryfall,a.image));
   n.append(' ',manaEl(a.mana),(a.eur!=null?' · '+a.eur.toFixed(2)+' €':' · ohne Preis'));
   if(a.gc){const s=$('span',' Game Changer');s.className='gc';n.append(s)}row.append(n);
   const t=$('button','Übernehmen');t.type='button';row.append(t);
   t.onclick=()=>{markOut(c.name);g.cards[ci]=Object.assign({},a,{qty:c.qty,swapped:true});closeSwap();recalc()};
   list.append(row)}}
 E('dlgnogc').onchange=load;E('dlgmax').onchange=load;load()}
async function replaceAllGC(){
 const todo=[];deck.groups.forEach((g,gi)=>{if(g.name!='Commander')g.cards.forEach((c,ci)=>{if(c.gc)todo.push([gi,ci])})});
 let done=0,fail=[];
 for(const [gi,ci] of todo){const g=deck.groups[gi],c=g.cards[ci];
  const r=await fetchAlts(c,g,{nogc:true,limit:1});
  if(r.cards&&r.cards.length){g.cards[ci]=Object.assign({},r.cards[0],{qty:c.qty,swapped:true});done++}else fail.push(c.name)}
 recalc();P(E('out'),done+' Game Changer ersetzt'+(fail.length?'; kein Ersatz für: '+fail.join(', '):'')+'.','hint')}

async function go(e){e&&e.preventDefault();
 const p=new URLSearchParams(new FormData(E('f')));
 const d=await J('/api/search?'+p),b=E('r');b.innerHTML='';
 for(const c of d){const tr=b.insertRow(),n=tr.insertCell();n.append(cardName(c.name,null,c.image));
  if(c.gc){const g=$('span',' GC');g.className='gc';n.append(g)}
  tr.insertCell().append(manaEl(c.mana));
  for(const v of [c.type,c.ci,c.rank??''])tr.insertCell().textContent=v;
  const pc=tr.insertCell();if(c.eur!=null){const pb=$('a',c.eur.toFixed(2).replace('.',','));pb.href='#';pb.className='cmprice';pb.title='Cardmarket-Preise anzeigen';pb.onclick=e=>{e.preventDefault();cmShow(c.name)};pc.append(pb)}
  const l=tr.insertCell();l.append($('a','Scryfall',c.scryfall));if(c.cardmarket&&SHOPON.cm){l.append(' · ',$('a','Cardmarket',c.cardmarket))}if(SHOPON.to){const a=$('a','Trader-online',SHOPS.to.search(c.name));a.target='_blank';a.rel='noopener';a.className='tolnk';l.append(' · ',a)}}}
// ---- Benutzer (Server), App-Installation
let installEv=null;
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();installEv=e;userBar()});
if('serviceWorker' in navigator&&(location.protocol=='https:'||location.hostname=='localhost'||location.hostname=='127.0.0.1'))
 navigator.serviceWorker.register('/sw.js').catch(()=>{});
function dlgOpen(title){const box=E('dlgin');E('dlg').style.display='block';box.innerHTML='';box.append($('h3',title));
 const x=$('button','Schließen');x.type='button';x.onclick=closeSwap;box.append(x);return box}
async function userBar(){await MEP;const o=E('userbar');o.innerHTML='';
 if(ME.server&&ME.name){o.append('Angemeldet als ',$('b',ME.name),' · ');
  const pw=$('a','Passwort ändern');pw.href='#';pw.onclick=e=>{e.preventDefault();pwDialog()};o.append(pw);
  if(ME.admin){o.append(' · ');const um=$('a','Benutzer verwalten');um.href='#';um.onclick=e=>{e.preventDefault();usersDialog()};o.append(um);
   o.append(' · ');const lg=$('a','Impressum & Datenschutz');lg.href='#';lg.id='legallink';lg.onclick=e=>{e.preventDefault();legalDialog()};o.append(lg)}
  o.append(' · ');const lo=$('a','Abmelden');lo.href='#';lo.onclick=async e=>{e.preventDefault();await J('/api/logout',{});location.href='/login'};o.append(lo)}
 if(window.AndroidBridge&&AndroidBridge.changeServer){if(o.childNodes.length)o.append(' · ');const cs=$('a','Server ändern');cs.href='#';
  cs.onclick=e=>{e.preventDefault();AndroidBridge.changeServer()};o.append(cs)}
 if(installEv){if(o.childNodes.length)o.append(' · ');const ib=$('button','📲 Als App installieren');ib.type='button';ib.className='primary';
  ib.onclick=async()=>{installEv.prompt();await installEv.userChoice;installEv=null;userBar()};o.append(ib)}}
function pwDialog(){const b=dlgOpen('Passwort ändern');const f=$('div');b.append(f);
 const o=$('input');o.type='password';o.placeholder='bisheriges Passwort';const n=$('input');n.type='password';n.placeholder='neues Passwort (mind. 8 Zeichen)';
 const n2=$('input');n2.type='password';n2.placeholder='neues Passwort wiederholen';const ok=$('button','Ändern');ok.type='button';ok.className='primary';const m=$('p');
 f.append(o,$('br'),n,$('br'),n2,$('br'),ok,m);
 ok.onclick=async()=>{if(n.value!=n2.value){m.className='warn';m.textContent='Die neuen Passwörter stimmen nicht überein.';return}
  const r=await J('/api/password',{old:o.value,new:n.value});m.className=r.error?'warn':'tag';m.textContent=r.error||'Passwort geändert.'}}
async function usersDialog(){const b=dlgOpen('Benutzer verwalten');const list=$('div');b.append(list);
 const render=us=>{list.innerHTML='';if(us.error){P(list,us.error,'warn');return}
  const t=$('table');list.append(t);const hr=t.insertRow();['Benutzer','Rolle','Angelegt',''].forEach(x=>hr.append($('th',x)));
  us.forEach(u=>{const tr=t.insertRow();[u.name,u.admin?'Administrator':'Benutzer',u.created||''].forEach(x=>tr.insertCell().textContent=x);
   const c=tr.insertCell();if(u.name!=ME.name){const d=$('button','Löschen');d.type='button';
    d.onclick=async()=>{if(d.textContent!='Wirklich? (Decks werden mitgelöscht)'){d.textContent='Wirklich? (Decks werden mitgelöscht)';return}render(await J('/api/user_delete',{id:u.id}))};c.append(d)}})};
 render(await J('/api/users'));
 b.append($('h4','Benutzer anlegen oder Passwort neu setzen'));
 const nm=$('input');nm.placeholder='Benutzername';const pw=$('input');pw.type='password';pw.placeholder='Passwort (mind. 8 Zeichen)';
 const ad=$('input');ad.type='checkbox';const al=$('label');al.append(ad,' Administrator');
 const sv=$('button','Speichern');sv.type='button';sv.className='primary';const m=$('p');b.append(nm,pw,al,sv,m);
 sv.onclick=async()=>{const r=await J('/api/user_save',{name:nm.value,pw:pw.value,admin:ad.checked?1:0});
  if(r.error){m.className='warn';m.textContent=r.error;return}m.className='tag';m.textContent='Gespeichert.';pw.value='';render(r)}}
userBar();
E('gnwrap').addEventListener('toggle',()=>{if(E('gnwrap').open&&!E('gnbox').firstChild)gnInit()});

// ---- Hilfe
function openHelp(k){E('help').style.display='block';const el=E('h-'+(k||'top'));if(el)el.scrollIntoView();}
E('helpx').onclick=()=>E('help').style.display='none';
E('help').onclick=e=>{if(e.target.id=='help')E('help').style.display='none'};
document.addEventListener('keydown',e=>{if(e.key=='Escape')E('help').style.display='none'});
document.addEventListener('click',e=>{const b=e.target.closest('[data-h]');if(b){e.preventDefault();e.stopPropagation();openHelp(b.dataset.h)}},true);
try{if(!localStorage.getItem('helpSeen')){localStorage.setItem('helpSeen','1');openHelp('start')}}catch(e){}

// ---- Automatische Aktualisierung
let updTimer=null,updWasRunning=false;
async function updStatus(){const s=await J('/api/update_status'),o=E('upd');o.innerHTML='';
 if(s.error){o.textContent=s.error;return}
 const items=Object.values(s.items||{});
 o.append($('b',s.running?'⟳ Prüfe auf Aktualisierungen: ':(s.done?'Aktualisierung'+(s.at?' ('+s.at+')':'')+': ':'Aktualisierung: ')));
 if(!items.length&&!s.running)o.append('beim Start übersprungen. ');
 items.forEach(it=>{const sp=$('span',it.label+': '+it.status);sp.className=it.ok===false?'no':it.ok?'ok':'';o.append(sp,' · ')});
 if(s.next){const nx=$('span','nächste automatische Prüfung: '+s.next+' · ');nx.id='updnext';o.append(nx)}
 await MEP;if(!s.running&&ME.admin){const b=$('button','Jetzt aktualisieren');b.type='button';b.onclick=()=>startUpd(0);
  const f=$('button','Alles neu laden');f.type='button';f.title='Regeln, Precons und Kartendaten neu herunterladen';f.onclick=()=>startUpd(1);o.append(b,f)}
 if(s.running){updWasRunning=true;clearTimeout(updTimer);updTimer=setTimeout(updStatus,2500)}
 else if(updWasRunning){updWasRunning=false;infoLine();if(items.some(i=>/neu geladen/.test(i.status))){rules(E('rq').value);if(deck&&!deck.error)loadPrecons()}}}
async function startUpd(force){await J('/api/update',{force});updWasRunning=true;setTimeout(updStatus,500)}
updStatus();

// ---- Offizielle Regeln
const RQ=[['Inhalt',''],['Commander-Regeln','903'],['Goldene Regeln','101'],['Spielablauf','500'],['Stapel & Auflösen','405'],
 ['Schlüsselwörter','702'],['Farbidentität','903.4'],['Commander-Steuer','903.8'],['Commander-Schaden','903.10a']];
RQ.forEach(([t,q])=>{const b=$('button',t);b.type='button';b.onclick=()=>{E('rq').value=q;rules(q)};E('rquick').append(b)});
[['Commander-Format (offiziell)','https://magic.wizards.com/en/formats/commander'],['Bannliste','https://magic.wizards.com/en/banned-restricted-list'],
 ['Brackets & Game Changer','https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-february-9-2026']]
 .forEach(([t,u])=>{E('rquick').append(' ',$('a',t,u))});
function richText(el,text,words){const re=/(\\b\\d{3}\\.\\d+[a-z]?\\b|\\brules? \\d{3}(?:\\.\\d+[a-z]?)?\\b)/g;let last=0,m;
 const plain=t=>{if(!words.length){el.append(t);return}
  const wr=new RegExp('('+words.map(w=>w.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')).join('|')+')','gi');let l=0,x;
  while((x=wr.exec(t))){el.append(t.slice(l,x.index));el.append($('mark',x[0]));l=x.index+x[0].length}el.append(t.slice(l))};
 while((m=re.exec(text))){plain(text.slice(last,m.index));const n=m[0].replace(/rules? /,'');const a=$('a',m[0]);a.className='ref';a.href='#';
  a.onclick=e=>{e.preventDefault();E('rq').value=n;rules(n);E('rres').scrollIntoView()};el.append(a);last=m.index+m[0].length}
 plain(text.slice(last))}
async function rules(q){const o=E('rres');o.textContent='Suche ...';
 const r=await J('/api/rules?q='+encodeURIComponent(q||''));o.innerHTML='';
 const ri=E('rinfo');ri.innerHTML='';ri.append('Comprehensive Rules von Wizards of the Coast (englisch)'+(r.version?', gültig ab '+r.version:'')+' · ');
 ri.append($('a','Originalseite',r.source||'https://magic.wizards.com/en/rules'));
 if(r.error){P(o,r.error,'warn');return}
 const words=/^\\d/.test(q||'')?[]:(q||'').split(/\\s+/).filter(w=>w.length>1);
 if(r.toc){r.rules.forEach(x=>{const d=$('div',(x.num.length==1?x.num+'. ':x.num+' ')+x.text);
   d.className=x.num.length==1?'toc1':'toc2';if(x.num.length==3)d.onclick=()=>{E('rq').value=x.num;rules(x.num)};o.append(d)});return}
 r.glossary.forEach(g=>{const d=$('div');d.className='glo';d.append($('b','Glossar: '+g.term),' ');richText(d,g.text,words);o.append(d)});
 if(!r.rules.length&&!r.glossary.length)P(o,'Keine Treffer. Tipp: englische Begriffe verwenden, z. B. „trample“ oder „mulligan“.','hint');
 if(r.total>r.rules.length)P(o,r.total+' Treffer, angezeigt werden die ersten '+r.rules.length+'. Die Suche lässt sich genauer eingrenzen.','hint');
 r.rules.forEach(x=>{const d=$('div');d.className='rule';const b=$('b',x.num);b.onclick=()=>{E('rq').value=x.num;rules(x.num)};
  d.append(b);richText(d,x.text,words);o.append(d)})}
E('rf').onsubmit=e=>{e.preventDefault();rules(E('rq').value.trim())};
// Tabs der Seite (über die Adresse #name erreichbar, Zurück-Taste funktioniert)
let rulesLoaded=false;const PAGES=['willkommen','neu','deck','gegner','decks','galerie','precons','sammlung','spieltisch','suche','regeln'];
function showView(v){if(v=='start')v='deck';if(!PAGES.includes(v))v='willkommen';
 document.querySelectorAll('section.page').forEach(x=>x.hidden=x.id!='v-'+v);
 document.querySelectorAll('#mainnav a[data-v]').forEach(a=>{a.classList.toggle('on',a.dataset.v==v);a.setAttribute('aria-selected',a.dataset.v==v)});markMobNav(v);
 document.body.dataset.page=v;
 if(v=='regeln'&&!rulesLoaded){rulesLoaded=true;rules('')}
 if(v=='galerie'){galInit();galSearch()}
 if(v=='precons')pcInit();
 if(v=='spieltisch'){tableSetup();tableGame();J('/api/games').then(tableStats)}
 if(v=='gegner'){const ok=!!(deck&&!deck.error);E('nogegner').hidden=ok;E('cmpbox').style.display=ok?'block':'none'}}
function goTab(v){if(location.hash!='#'+v)location.hash=v;else showView(v)}
window.addEventListener('hashchange',()=>{showView(location.hash.slice(1));window.scrollTo(0,0)});
// Sprungmarken innerhalb der Einsteiger-Seite (#g-…) nicht als Seitenwechsel behandeln
document.addEventListener('click',e=>{const a=e.target.closest&&e.target.closest('a[href^="#g-"]');if(!a)return;e.preventDefault();const t=E(a.getAttribute('href').slice(1));if(t)t.scrollIntoView({behavior:'smooth',block:'start'})});
showView(location.hash.slice(1));
document.querySelectorAll('.tile[data-h]').forEach(t=>t.onclick=e=>{e.preventDefault();openHelp(t.dataset.h)});
ac(E('wcmd'),{get:names(true),pick:n=>{E('wcmd').value=n}});
E('wquick').onsubmit=e=>{e.preventDefault();const v=E('wcmd').value.trim();goTab('deck');if(v){E('cmd').value=v;setCommander().then(()=>E('b').requestSubmit())}};


E('b').onsubmit=bd;E('f').onsubmit=go;go();setView(view);
function infoLine(){J('/api/info').then(d=>{E('info').textContent='Version '+PAGE_VERSION+' · '+d.count+' Karten · Scryfall-Stand: '+d.source_date
 +(d.precons_at?' · Precons: '+d.precons_at:'')+(d.rules_version?' · Regeln gültig ab '+d.rules_version:'')
 +(d.cm_at?' · Preise: Cardmarket (Preisliste vom '+d.cm_at+')':' · Preise: Scryfall');CMAT=d.cm_at||''})}
let CMAT='';
infoLine();
</script>"""


LAN_KEY = ""

# ---------------------------------------------------------------- Gemeinsamer Spieltisch (mehrere Geräte)
# Räume liegen nur im Arbeitsspeicher; nach 12 Stunden ohne Änderung werden sie verworfen.
ROOMS, ROOM_LOCK = {}, threading.Condition()
ROOM_GLOBALS = ("turn", "active", "monarch", "rot", "start", "life0")
QR_JS_Z = "eNrFXFtz48pxfvevoGAvF1gMKdwIXiFld08cb7yb2GePHxKZpwoiQQpnKUAGQWlliS4/5CFVechbfmCq8j/y9VyAAQlqXeVctlYkMJeenu6enu6eHp6fd97nd49Fur4pO+bC6niOM+78Ov7j7ib9knfeFvE2+dn5eedjukiybbLs7LJlUnTKm6Tz6cMPnY0onvzsPi46fygW+TKJVrtsUaZ5ZlpPVFrWBSUrRFkSlSyL1lfFnOVRtttsWBo5LBaPu+hqzlbR054tDrrm2rv1tMoLk4AVUZY8ANMifkQxSyJnmszKaWJHrvVUXCXzRv1UdcvQLkO7jNpRs6tszhHYF0m5K7JOsTfTKHiT2O7QYhvTYQ59pb2heHAYHi22NS12g78lR5ElF9Gw270nRAhWFMXdrhlHd2bCMrazLPZgxmi3Z5uDuSm0kqjnAv9oKCaQrswzs7RR0HOfn9NZhGfLqueAxhk1FrOws6odnp+fzfwK7edXeJlHzixKul1ACoGSE0WoD/FpPT+jJut2s6om4TUJajzVJ+h2PdUqAPo3OpsVOmU0mpaztIdPQkcQACjMr8I5IMunqHzlRZFTc6JAt4J3K/RuIfAW3fhTVIhue7ZtH/tdf52Uv4nLMimy3+TblDdILFaA0cWs7G+SbF3eiDEOhEDVcSpyCU2jkqQzxlc2n4ILCqt0fhXPq/67qOdNd7MIHzrYFRWvqHhFxehl79DPXs1REUU7EJZ/0suKv+AThN91u/hc7ffs/oSo80m+e/+rHx7vkn/Y3V4nBU1RTMMdaROIo7Oy23WjyCwuLrKua03zq09xedNfbXJAy859CxL/yrdB954/j+I9DXIAqA1I3ecIHoDs2fKkYGezmf9cgKb6JD5kq5ymsMPIu5k7EIR8ElRUo8cXFzsafTcLL/MrkHI0j1aT3WxEb7Yr30HmnjuwZTWfzwHUNogEYzRH113PFVDHosQdUJHtCtBVAYGmkUZ8mLNyzx5eWMpgDZDCnIc0Q6g1PvdP8fbLL1UfaI0FNZouLpzpohd5XIywABcQfrwDy2kNdI0ZrWfedC21g5LLbH616K3ngnKb6MzF1JRcA84molmXoN3FxUWMmVsMfRm6WLz2bGOxCki0YT1OJBoc1UQ8moK1x4AmRCOxZg7XMpn1lPWiBEq3l0yviyT+socI3DUIwpIa+yx6S/P//vO7Tb74shU6M4+uoUCxA0zTWaKWYqpJcoJVN837d7vSjDn5sM2gR4CudeFH3g/F7+q3D9m7tNw2OpWYedx/KNIyMXNrLxaxw3WRwCBrYICpZxi9v4zL+H2+y0rSBfnRCNbF6M3OKm+K/MGgTbAjYHTy+6TAAnnod0zDbulmGxeGja62YRkch7Y2wSxCk25XTNbBvKctzV6NzoC/xRuhxDxzhYadnrXiSyBpg+AwPT9kI6JmezvLknBNd4h2U7lBnpJ6h/QRuIodUtt6C0lXi/b5llKxVNV7Qw0UENuaA1gtvKDMy3jDS3qraRZxZXQbf4VUr0imqvecLSBd6KENu6p3H7GgqF4NLZYWqRksBW8w6JZcX+1WK2hb62qNHZU259VULDUub39bFHnxPi+KZFH+Jt88ZvltGm9gUGGn/GISMLbRpbTnWv3bfGluBCJxE73DpkwgGR8iyemzjdb2TaOD3i6W89heRM4lb/a2NLfWxNlz2b+Xsi8GKBrQ720Qeq0Tms94qSF6D4OmASETXWvd22Rog9DQLMurh3kkSc0eqIUGK/8WrPgYVtyAJQV1uYcQZNZ+uurHy+V3EKRWm5RU6XT7kJaLG7OIiudn491jmRjW0wJGsIHdNinShTFJok9kR3JtN+VVbzd3N3FW1389qOdgUH57UP7rOPsppYqPdcUyWcW7TTkRugQikkwMu9jvsPy2N7RRCit5z1b9dPtdXHw5mArUUymVc/n8XMjHQuimTmkbDOAUYbhFVswJmNCQu03CGa1bWLJtSq1u4y8NAx+jJTNXt8JcWICBAwPQ1s2WQ62fNbX+rta5tlL6u/9dpb9uKP1CR2BNcv8X6HxSy2tL7HrwaPYL6FzWapo6ZIRKz2QkPRO0RpE1FduiwD/fQnmkWUn6SRri5UVGW3AZZYCRWJpzYlnEkQWGL5Mf4usNPtYHwlCSDHhTId6GQSO/npXUtrMtHzcoe81QZnSu8wJuXe8hXZY3k45z93Wqini7SSfLs2RqNBov8s0mvoPz11FPqsEdVlmarSWg27hYp9mkY9hYVfd5uuxgZlFxGbwpJwV2QLTh/V4bFwKbWXmdLx8vjANX7VBGTUtaqaJPoXXA3jPN2zrk1EFQYfn/QAJHzdXoyHEMu6wpYHRuEnLEj4qv48WXdYE5LGnIvEADqlAqAFtebl0aP3f4P2Ni/HzF/4neirrnF6+nnFTnRCslSLJEUJzJN5IQNKnE6/P9+lC4GBxasVRzuOpTI7/+CVufEUUljPp81cGMoRCzcnvlzLn8mnmkl1n9RbLZfE7/mECu876gEJZI3o83FBzI+2VabqDvhAyzY9FhJpi3LQuQuR42uXwqk6/lJNlPsHie9lafXqOEfz0/8wBD0k+XsuSSnqHoReiit0y2iyK9ozkaE94WHtHRGJkcI9tPMm2MTB8jozFEyWXWGINPS0DnCzNlMduxBbb4Y3l9U9remwKxAkPI9iIyNlw0mNNxGH/q9OoC8fhHCMeGRHx7v+7A/txiNpHh9l2j8/V2k20j46Ys7ybn5w8PD/0Hv58X63NEfZxztMdiQNe8v13EGxKCS8OYvBayioVir+3Xd1+VlNYFvNPrzn2aPLzLv0YGcOlQnQE5RgujIxvcFck2Ke6Tt9s7yMr3MegcGV8/pdk/4a9zmySlAKUoKXn0ulPktFDT27UBuUrjHnCD8CTL60dC4tG8IhJzvs77P0GBmhgZXCnSW2hJIPB6YnCawNqu4V9CCRAvOuAUh0JAqPWFeKE2UE9YDtTqwpAwFFIzTVgqEIkOIqlBaG0rQK9nZCwq4rqO86qmrHhbpfDtjIcbbFtGZ0GExdcjfWEtCxB3sHI7NDjsAmcat+m8uDaiYghUIffclpbc46mUSsxS7huCbJ+gu1Pqa3H7YWcvKtuKsDCgSoscloFRFnG2vYsLLHKF/vUGykshDFJAynTVQtbY777/2LpxtSx6uZedXCpZVMCySHqVifMBkbek3pW5N0puM2yibreY5TyixWNcuYr8aGENs+hl1nlJVpdemojSyhHSSXbpTFylXN29tkd/uG1Rot+aanZ6qjlpBWXIEWlpfbCcFtq2WJBI5LRFNMgsHW7i2WvRVK1tessaNdUqb1QlFJGjaqhpWfdIZqmo5t9gtrHn2D+eiGJhAcgwrbK7ksqdyaKyv7iJC7gpsI6kOZ5JI3xmTBC/M7qbcmrolvSFLF8flHdleXx716gglcAr/rDL6y7K9kZNtq8trZrNgpZvP7//8OHY7DY5J11r5llHDjKxueJveelNhCvFd1GWM+wBkfvmmNPgcwnHmFzeuFdii3gy/vM//hX/oUPok9Fnh7/8GS8dVfMv9ELlHYMizY1efz7Rq6P3uVE7jgiexhQ19QQHs4P1sbPO3crfVqW2K8sFm2MZzI4E1ju54hDg2sl1iEfNmmmuNQ6JVBH6Q68fdrddALDdBoi8FcRlSsaUMaEvjsiNHZUz0f0iWlxuYPVP1uR3oML4fVYZSfErr9stL8iB3u6uhT2AQMyNlN5eDB/dFh5xbMOzF3sQkdeanOjiWntE/qYlQmzNte/Vaq6SjZM6YAd1R7JRQDbkCYc+Pmc6DiuO6zpESOIyoumS1Q1WcVbn0REVoQqpg4w4x8ICTzGHnTwdEExR/DnBkEyAEjzFacrWjtLL9WQjQmDceC+FrQ5GbG2dFafJCUWLfQdm+Q+5t3yfZ9woa65S7tV70zpUdUxYObMEM7Otpj+RACXbKvu0r33mvsOBAS62uoncsZlo+T02eTMjfY2/gp/9rPbTsi/m8ENOwYEtQrPNAooOb6MnpZHa1SjOyb6pRt/D5hSqtBAhBApoZZofCfNVjgKEpbnfQK0tVNLi5SbRZ37qdXz+l4Av8ZLsi5VJceVSBkphS1cbGMLoImAIX2JaxX0POsbC2Z6KoC0GQDwdn7PZ6DmjVlcC8f6qyG/fy7mbMVXvcDixor3JpRB2flYFRHIYqWdRR4uJpHsuBMalodPPaYl6HrBCyq1iRa6fJemgcj6fdOZ6I0vyJLWmyWabVOHuagfMrfnUyPg5j+ZaXXImxhYocikhxNbEVI+I8COYq7E7tqyJfAXnNdYfb0LQKB6oGkCrjGi/+Thx2aeJw3478dmvJh7tJlh1aLdFu/vIx3FPgBDgADH/kD3ilOMdzoqiK5DjKmTuiH95nvgK+ZfviK9A1jFftgpYoBqyQLT1RmwgmztsIHr4HhuMJAgWaj1YGFYvIzZ01MvAYcOgBsKGo+oFUW+vehmxUVjDZWOnRoEN8R40ALLxqAGTuY5XdQjYyEFBWCPMRgFzXacxGAqCxoAoGB0OwlzPOxoIhdVcB54oBHzfacwMhajw6zEcMSgq/NERJsyV5NexQWHYOjpzJWPANkI1lBVoIPmk0wEDolKxTaMHKlBZc5F6eLICoMKwFU3mgruk+1zfH2CtDsdDH6qjfWU6U+csKqcWnfuyEmsDIcpqBTCTohfWwXnkCUjlbObCc8K23UuhUC/ouKX4MUpms6pMQfbcgef9aPIez6Ty86Nz2xcG8dQgWTVIVg2SVYPwps+FBH5w8t0Ar+Z7VeL8UrbXzyAbjaXJXQqTu7OZtB73iEKTfEJ+Lr/ndnXn5qXWnVJvun2xafHKr5vefxsHrfXyxdaaHVKee5atvRc4xG7M5uHl2bxBSoJNn9rgdy+jWndpDPT4zV6+LWmt+jUPCq7jJaKM2y9SCnBmUO4lo9uPpk6I3xfzyp1TgksjjQZ2U/8Wg6V3m0eTmrD3gPwVWS0WNba0BXUUJz92lFxp87uOdSBrsSID1hkv2KmCsXhfTfjXQhWP2s9Lyj1tpx2MVcy84elRvINRXFcNowrCaXNAIPbCiE88XaeYBXA2RDVt2XSAMz2JQ3CIg/9NHLxTOCiWVwcJp5TMsdkrj21h+hbCqG/avoW0Z1SpyNcqdfsXpkOPsg6gX3dV6lJm7+gIqoB3YO8sPUHGpQQZVybI2CvZCk96Jszzcxxpo9g72HAr7jbw8730YoBniCilpAwsLYWloMQoNQ05BRTVRtkCZQ30KdmCapk2nNteDiTcU+31Gmw88IECfOKknbBsYHiMXyjwO0Dr7GjgRoF3WOAfFgRHQAaHTUJL0DGQaVkNputUDQXWp1GUNNMKvMMC/7AgOAIyOGwSCk5IFPUDvFOotiJqrvVzYUDj2j++3pqIuL5ZnxfnRW/gWOeDN66zJ5l+355rVp+Ae4OQUswOChpHfSXlILoz+I/CzUbxDK20Snz0gvmP9DUQX6H4Gs011xymvFTHV9RrHiUyRPi03uTrho/IT4FdqYOo1uRHA1blbwEEDAHS4XU/mcSBeI/DzSUaTxRcRISvVfR4mdr+6OS4Co5lcJumClTnS6Xs66iXyvSQJ9Hy1TbOST2+4FbqDi7XCjT5KZ3iudoJoZbjqWICic2Ti3SvrJcIOcmucqJ6Tqkc2gQY0ZIyJCYt1lMiSSZ3t8nxEblKXtoztVlOvpWwmumn2HZ5mPchZt9oJESgqZ0b/cQMkdFq5/MfI7lR44ukIJMJIMghtWVRKYtyq97HvyBOTpmW2FgOxaqBS68x8MxRgc9My+08GBnWQu9gZBRhoidoojiYHU8xISZmFfp68Ki98SE1tKlDVOrJJ5g8z84pLV3AaT5vj8MbVzCHyCEaw1cRT2H15KsnURkEwu/lT96oevLUk+w6hMMzUE8B9YCbPIDbUz0JwFBa8LB4IZww31NPHnUB3IEcF04gOYO8OhyywBdwfPhkzCOHj48rSlxZIoDB6QpHHFjgM2+onvhkxdOAt4OjOpTtxsx3BTQ4angX4/A6fwxUGGYK/07MyvVcNhbTgnsKnw/fLtoJUGhGJYFbDUgdZYkYGA4qcCb0fXIS4U6CAkBBoMq9S0JhKIgnSjxZ4tdTRK/RkIVilHDMZ1YRPxRTpnExuFOVDEQJH50I7LKRy+kNrxdcgC/rsoHLK4kpNOwA5PU5sgKRkYYIpsHGHqOHIRv7fJjjKWG+nsOAwJB5BBvslHQOKjq7RHKH2o9ET0yGk5eX8ElQ+4GA4CrGBxXj8YpaFzN0NQqDMpwFAxYOwALq6koSDyoSyyJPFtE0AMUZE31d7tqPRryMwyBYoQj8DMj7RzhhCNmH6Oqghjooj0sbQHk+G485BeD+A12fIiY8XgG8DznGW9B8fKKgXGcuLSUHA4o4BF8hriPAEP8Bhk9Jsg/dFf88SXV3WJGdwEM8QVoSTsKPKDSW0hRU0oQuEtwxtHEFjThA5KKePOTBF4wvoBCzhuDXQIDjokAMHQlVMlYLLaxWmt86V59rA6IDLQHOBVexYVCzYSCl3XV0cedohBw9EpWhwKWCo2YZVrOk2XFh4cIrlZlLqNJ0AIZCTrKv4uRQYkMiJtHx68UbKELTrAaejJUFgnFE0CHFAoUkSThBPa1QiURQiQS+qCPRFE+jKiAnBIwAKglzWxBz5Py8an4jEflyOJm0RSkR9CsE1TxBMAWO9MWRyDpKGEhNEFe4sICyQmaDSmZF3LJBf1/CIUmp8RNkI/wGPq0pMfLhigI06H9fxuj4/uIq/DCUws+v6McxVQT0JTyvBhjICfuuvtwFQJQpgEOlfriADKWcgeECYC0orkTQH9YIjhWCYQVvUCs2R9NsREDBEqeWGbUSvHopeEqNoKziSa0sfQ2kJ1nijSuegHNSaFoA1kQk6gmAujoi2il95CjiaYtUTdYftABqqHElxqQ0KnEZK9TGx/wIwrbJhq0gayyD4EihD5QGcCsJpGi0XMNDbQ2T0ucMAe8UQ/zx8SKuFkng6otYQiSVWoEMJUS/VgtBqCA6NUQJMAwadGxbJmrVufWyC8YtEINjOlaIkYVTg3TlAiHbqQI5Op52oLBEOwWSNp4W5QWtKuY9rKftH2sb0u1i3sN63mMFhzObFDW3J5X+wjqteFOtZ403FUjFmzkrWo8TnyorO9GyzZH3kNRJuDjpTvas2VZLKq7haomJzbQfGYJLZAhu3f84qVzZ4A1SGXCI78ynsvLTcaVbVf72uNKrKn91XOnP6+QSXrffczynuoecW3Ust9h2rmlenb/plNWRAWJ8CfzlRAvoYnIfk/tkg6ra6UqRwSc80XMfUTocxon8+fTwllp+5ePuCcyjhXyExbKRj1gyN+h1M1tRNoRrxeIAEUmIbFN7ijFYQo7zdYtfNJdZz0/V7YkWn7nkLrXucVdS0YjM19dOxEWmhC4yDXvFq1GXzv6RET5pv4/SCAcl6nYMBwIIyO/quXQdSvPsRdy6BdeCj4PKui5Rp+2HyKqIA0+LKAXtKKxOubC4Z/Uc4ayMxn9FR7V0Ll2L9Z59asRthR8dM3Fr9kmmtbfj1xKeKFviEzwV/kRwIhFxYNurs+Ktkqfc5zhirrMvMoZQHvxzhPHxFPlE5fo2hnrsZVHkXp7qT/fQAjqcrht7glxtrT20HoJVlCtw4rCvNSGiiFznTWGnppZZpp9ZNI8OsSSRYYnrE0BkFhljQ0U1ymZCQA+tDlIExPpF0keyjjcdquvwuHwdQ2BfW1i7+79mrXvE2mDwhugtyZMhIKK/cj65Luez1+Bzzaq6KwuPWfRXEJW6vq27/vPprm8Puto4rWmeu1D2l+zti2MV4xd1yVCUvKpLRqLkTV0iDqIMuyoJxFGV0atLxCmS0a9LxEETQp1ViTjlQbJQVRIcnOoci5EuR7fRscJcMcr6aeQRmTwE+oJgJd8QrOwvEixKEswaN6yFYGR0iXqkRdHyPfvYgvniGHOeAdX//PcfPpMEnGVyc9z+lG5xFaPsbHd3d3lRJsu+MT072nyQ4vZf//5vBpce76wKPj8/+6OhF57RDuLMKTOoxHmn9QJsCmsLY4Lf1E3/Clr+6U9mtS971ssEzYUia6xUudPwlB76wQKe+CRfyDbBVH3fGY2qe/rOGGcRuJ/LS6f1AeVgGDhVq9DxB9VxZUPm4pLu7AC0xYP02RSggnEw9PZZ5I69N2ZGmUZdYGDZMq2MSbbDZ7XoMom35zfEikbs/9QotZTgrtl3JwyKJ041kpCGxVDW2U6FIu3nG/CwyYd+1Zty1RqvPGtK9uQCqNsT3KZM6D4WnZLi1ke1wTQD8ZkMvuuA+SlDhRMX8Vamt+5cOqBmPh8glnyl8KB5u2VV5ofjqS2HUseR43plTF8aPrlwaCtHQ2ZwM4UfvagtCcVzo2YatqjPLZtbyZo3gp8op29ycNID0o2m4jrhRVRJC707ZBeLEXB+K+RnlyGID+MXP0eChM8OUuKQaJn0IaP5XohKoaWQE1DK/TEiSqFTmwchQwBx84j2h/Mff7/9xTl+8QLHh8i1CZ9j82B74antobg8iHvNEJe8x4W/Um09pMyl2Pniw50vHKjda1wdkZS9cECojYeqDs5gXTke2l5I9cFI1Q+GdXUwsgcer/a1OYWiaKgX+ZJmi4YhggX24YVL+qd+sYUuHWgHbW+EQtwi+Sj9Ch+kARALJr8q8PMpJQ5p2pRd2ddWhGn83YdfjoaxQSqkXr10s6DxnlXvfE1QDmWjwPmfeyW99pcXqGmwwxk433j/xgzlaTfsf9Mjr0Ib3Woon8qGzi9IKK2XMIdZgIRPXpqLc169dQ2ppdOJSn1akhJTwzpaDPUGh/Nw0gyubdITnbwiOx3StDMteZWpEDeXUrqzbbZm9sKIP11bYMWeriUHgPvAdPMOPu939DM+kbnCT18gM4Tu27OnQ5FV16vJbcNvLcjNTPulB6FMpwsbB+ZQZ6smB7qUDrh4XgMvHKSPeguRjUgPNBwlpKyfKf9vwZA+Am262mBL0zXlgtSxDnUNClvTG3mzmdbcVPwigIPc3LZp51fbuRCbLR2fb2d507pYvtCLeoCiC2TWx2m2Ne/tpXWJ3whYTkyFQdpPkYD/9R9X9MMAGdF/iwueOBkmU4SyduR7ROyH+WFyp1yyieBZwHtp1bn+7WBVeSJeOJ3Av01f2xBN7I+7YxsCvyolgxIYsqZtJvaeenKZsoiWu7vOl+SRx1fIcYcO5O46o5m0O2oS2YZ9oudMMDVKWwsRDTqLomZ6RaKpbvWrKQd5LzItC1f7SnGTL+srzWymWLkJfUqxj0ngp5mkY1xrkhaSVZfXKSveIG/i0GMGF1vXpxn63ZIMlaMdET9RYFUGaTnzwmq/Gtj8un05G2i7oRfa46EoDrXigWcHIyoOPW3Lg2tFRfrGGAz3gptZYxfM66UU6aJAxChpJQrzOiOOjxhPOMHKRiJMKmNHIV/KIWXdcSE8+GmEgptPKa37sFfQVWZOS1jGr3xSILX69nsoknovF3oPRIXFQqCVFdfyowzYWPM9vwcRN4Wfq5MFLnnK5c0T0naa6lhdLeZVDGRXrSGD4q2T9DZeJ+frdDW9hpOKSDjufO7rqxoQHXGZucVjuzJ+98MveyNj3paA/JdfY7FP3WLJ6N7EZXWbYZLNPCeoCuCWPMM0o0Pj0TOkjzcYDLxxiHvZFzCh/CBQbT0voLYuT1vnvbqhr3WE1WhD5MPBwA9tEwliHhXzjG7+fGiPVzcuAofDHSm4rqcAHw2i/55DSTeDNAIZ6qW++YEAQZohhCi++/Ht8lI8mqBhaU2ObuHDToZNsYUU3vJsz74siEr6+QjzWKAEX/fW9L8Bca+O9w=="  # qrcode-generator 1.4.4, © Kazuhiko Arase, MIT-Lizenz (komprimiert)


def room_clean():
    now = time.time()
    for k in [k for k, r in ROOMS.items() if now - r["updated"] > 12 * 3600]:
        del ROOMS[k]


def room_valid_player(pl):
    try:
        cmd = {str(int(k)): max(0, min(999, int(v))) for k, v in (pl.get("cmd") or {}).items()}
        return {"name": str(pl.get("name") or "")[:40], "deck": str(pl.get("deck") or "")[:120],
                "life": max(-999, min(9999, int(pl.get("life", 40)))), "poison": max(0, min(99, int(pl.get("poison") or 0))),
                "cmd": cmd, "conceded": bool(pl.get("conceded"))}
    except Exception:
        return None


def room_create(state, client, uid):
    try:
        st = json.loads(state)
        players = [room_valid_player(x) for x in st.get("players", [])][:6]
    except Exception:
        return {"error": "Ungültiger Spielstand."}
    if len(players) < 2 or None in players:
        return {"error": "Ungültiger Spielstand."}
    with ROOM_LOCK:
        room_clean()
        if len(ROOMS) > 500:
            return {"error": "Zu viele offene Tische. Bitte später erneut versuchen."}
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        code = "".join(secrets.choice(alphabet) for _ in range(4))
        while code in ROOMS:
            code = "".join(secrets.choice(alphabet) for _ in range(4))
        g = {k: st.get(k) for k in ROOM_GLOBALS if k in st}
        seat = st.get("seat", 0) if isinstance(st.get("seat"), int) else 0
        ROOMS[code] = {"state": {"players": players, **g}, "ver": 1, "host": client, "uid": uid, "claims": {str(seat): client},
                       "closed": "", "updated": time.time()}
        return {"ok": True, "code": code, "ver": 1}


def room_view(r, client):
    return {"state": r["state"], "ver": r["ver"], "claims": r["claims"], "host": r["host"] == client,
            "seat": next((int(k) for k, v in r["claims"].items() if v == client), None), "closed": r["closed"]}


def room_get(code, since, client, wait=True):
    code = code.upper()
    deadline = time.time() + (20 if wait else 0)
    with ROOM_LOCK:
        while True:
            r = ROOMS.get(code)
            if not r:
                return {"error": "Tisch nicht gefunden. Entweder ist der Code falsch oder der Tisch wurde beendet."}
            if r["ver"] > since or time.time() >= deadline:
                return room_view(r, client)
            ROOM_LOCK.wait(max(0.1, deadline - time.time()))


def room_claim(code, seat, client):
    with ROOM_LOCK:
        r = ROOMS.get(code.upper())
        if not r:
            return {"error": "Tisch nicht gefunden."}
        if r["closed"]:
            return {"error": "Diese Partie ist bereits beendet."}
        if not (0 <= seat < len(r["state"]["players"])):
            return {"error": "Ungültiger Platz."}
        cur = r["claims"].get(str(seat))
        if cur and cur != client and cur != "":
            return {"error": "Dieser Platz ist schon vergeben."}
        for k in [k for k, v in r["claims"].items() if v == client]:
            del r["claims"][k]
        r["claims"][str(seat)] = client
        r["ver"] += 1; r["updated"] = time.time(); ROOM_LOCK.notify_all()
        return room_view(r, client)


def room_push(code, client, players, glob, full=False):
    with ROOM_LOCK:
        r = ROOMS.get(code.upper())
        if not r:
            return {"error": "Tisch nicht gefunden."}
        if r["closed"]:
            return room_view(r, client)
        host = r["host"] == client
        mine = {int(k) for k, v in r["claims"].items() if v == client}
        try:
            players = json.loads(players or "{}")
            glob = json.loads(glob or "{}")
        except Exception:
            return {"error": "Ungültige Daten."}
        st = r["state"]
        if full and host and isinstance(players, list):
            pl = [room_valid_player(x) for x in players][:6]
            if len(pl) >= 2 and None not in pl:
                st["players"] = pl
        else:
            for k, v in (players.items() if isinstance(players, dict) else []):
                try:
                    i = int(k)
                except ValueError:
                    continue
                if 0 <= i < len(st["players"]) and (host or i in mine):
                    pv = room_valid_player(v)
                    if pv:
                        st["players"][i] = pv
        for k, v in (glob.items() if isinstance(glob, dict) else []):
            if k in ROOM_GLOBALS and (host or k in ("turn", "active", "monarch")):
                st[k] = v if isinstance(v, (int, bool)) or v is None else None
        r["ver"] += 1; r["updated"] = time.time(); ROOM_LOCK.notify_all()
        return room_view(r, client)


def room_close(code, client, result):
    with ROOM_LOCK:
        r = ROOMS.get(code.upper())
        if not r or r["host"] != client:
            return {"error": "Nur der Gastgeber kann den Tisch beenden."}
        r["closed"] = (result or "Partie beendet.")[:200]
        r["ver"] += 1; r["updated"] = time.time(); ROOM_LOCK.notify_all()
        return {"ok": True}


# ---------------------------------------------------------------- Decks senden (Postfach zwischen Benutzern)
def inbox_table(con):
    con.execute("CREATE TABLE IF NOT EXISTS deck_inbox(id INTEGER PRIMARY KEY, to_uid INTEGER, from_uid INTEGER, from_name TEXT, "
                "name TEXT, commander TEXT, list TEXT, extra TEXT, msg TEXT, sent_at TEXT)")


def deck_send(con, did, to_name, msg, uid, uname):
    decks_table(con); users_tables(con); inbox_table(con)
    d = con.execute("SELECT name, commander, list, extra FROM decks WHERE id = ? AND owner = ?", (did, uid)).fetchone()
    if not d:
        return {"error": "Deck nicht gefunden."}
    u = con.execute("SELECT id, name FROM users WHERE name = ?", (to_name.strip(),)).fetchone()
    if not u:
        return {"error": f"Benutzer „{to_name}“ gibt es nicht."}
    if u[0] == uid:
        return {"error": "Das Deck liegt schon bei dir, an dich selbst musst du es nicht senden."}
    if con.execute("SELECT count(*) FROM deck_inbox WHERE to_uid = ?", (u[0],)).fetchone()[0] >= 100:
        return {"error": f"Das Postfach von {u[1]} ist voll (100 Decks)."}
    con.execute("INSERT INTO deck_inbox(to_uid, from_uid, from_name, name, commander, list, extra, msg, sent_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (u[0], uid, uname, d[0], d[1], d[2], d[3] or "", msg.strip()[:300],
                 datetime.datetime.now().isoformat(sep=" ", timespec="minutes")))
    con.commit()
    return {"ok": True, "to": u[1]}


def inbox_list(con, uid):
    inbox_table(con)
    return {"items": [{"id": r[0], "from": r[1], "name": r[2], "commander": r[3], "cards": sum(int(m.group(1)) for m in re.finditer(r"^(\d+)", r[4] or "", re.M)),
                       "msg": r[5], "sent_at": r[6]}
                      for r in con.execute("SELECT id, from_name, name, commander, list, msg, sent_at FROM deck_inbox WHERE to_uid = ? ORDER BY id DESC", (uid,))]}


def inbox_accept(con, iid, uid, new_name=""):
    inbox_table(con); decks_table(con)
    r = con.execute("SELECT name, commander, list, extra, from_name FROM deck_inbox WHERE id = ? AND to_uid = ?", (iid, uid)).fetchone()
    if not r:
        return {"error": "Nicht gefunden."}
    base = (new_name.strip() or r[0])[:70]
    name, k = base, 1
    while con.execute("SELECT 1 FROM decks WHERE owner = ? AND name = ?", (uid, name)).fetchone():
        k += 1
        name = f"{base} (von {r[4]})" if k == 2 else f"{base} (von {r[4]}, {k - 1})"
    con.execute("INSERT INTO decks(owner, name, commander, list, saved_at, note, extra) VALUES(?,?,?,?,?,?,?)",
                (uid, name[:80], r[1], r[2], datetime.datetime.now().isoformat(sep=" ", timespec="minutes"), f"Erhalten von {r[4]}", r[3] or ""))
    con.execute("DELETE FROM deck_inbox WHERE id = ?", (iid,))
    con.commit()
    return {"ok": True, "name": name, "decks": deck_list(con, uid)}


# ---------------------------------------------------------------- Öffentliche Deck-Galerie
def gallery_tables(con):
    decks_table(con)
    con.execute("CREATE TABLE IF NOT EXISTS deck_likes(deck_id INTEGER, uid INTEGER, PRIMARY KEY(deck_id, uid))")
    con.execute("CREATE TABLE IF NOT EXISTS deck_comments(id INTEGER PRIMARY KEY, deck_id INTEGER, uid INTEGER, uname TEXT, "
                "text TEXT, at TEXT)")


def deck_meta(con, commander, lst, extra):
    """Kennzahlen für die Galerie: Farben, Wert, Kartenzahl, Game Changer, Themen (aus den Tags)."""
    con.row_factory = sqlite3.Row
    ent, _ = entries_from_list(con, lst, commander)
    cmds = resolve_cmds(con, commander)
    src = cmds if cmds else [r for r, _ in ent]
    ci = "".join(x for x in ORDER if any(x in (r["color_identity"] or "") for r in src))
    eur = sum((float(r["eur"]) if r["eur"] not in (None, "") else 0) * q for r, q in ent if not r["type_line"].startswith("Basic"))
    gc = sum(q for r, q in ent if r["game_changer"])
    tags = {}
    try:
        for v in (json.loads(extra or "{}").get("tags") or {}).values():
            for t in v:
                tags[t] = tags.get(t, 0) + 1
    except Exception:
        pass
    themes = [t for t, _ in sorted(tags.items(), key=lambda x: -x[1])[:6]]
    img = cmds[0]["image"] if cmds and cmds[0]["image"] else ""
    est = bracket_check(con, ent, {r["name"] for r in cmds})["bracket"] if ent else ""
    try:
        tgt = json.loads(extra or "{}").get("bracket") or ""
    except Exception:
        tgt = ""
    con.row_factory = None
    return {"bracket": tgt, "bracket_est": est, "ci": ci or "C", "eur": round(eur, 2), "cards": sum(q for _, q in ent), "gc": gc, "themes": themes, "image": img}


def deck_public(con, did, on, uid=0):
    gallery_tables(con)
    r = con.execute("SELECT commander, list, extra, public FROM decks WHERE id = ? AND owner = ?", (did, uid)).fetchone()
    if not r:
        return {"error": "Deck nicht gefunden."}
    if on:
        meta = deck_meta(con, r[0], r[1], r[2])
        if meta["cards"] < 10:
            return {"error": "Das Deck hat zu wenige Karten für die Galerie."}
        con.execute("UPDATE decks SET public = 1, pub_at = CASE WHEN public = 1 AND pub_at <> '' THEN pub_at ELSE ? END, pub_meta = ? "
                    "WHERE id = ?", (datetime.datetime.now().isoformat(sep=" ", timespec="minutes"), json.dumps(meta), did))
    else:
        con.execute("UPDATE decks SET public = 0 WHERE id = ?", (did,))
    con.commit()
    return {"ok": True, "public": bool(on)}


def gallery_refresh(con, owner, name):
    """Nach dem Speichern eines veröffentlichten Decks die Kennzahlen neu berechnen."""
    gallery_tables(con)
    r = con.execute("SELECT id, commander, list, extra FROM decks WHERE owner = ? AND name = ? AND public = 1", (owner, name)).fetchone()
    if r:
        con.execute("UPDATE decks SET pub_meta = ? WHERE id = ?", (json.dumps(deck_meta(con, r[1], r[2], r[3])), r[0]))
        con.commit()


def gallery_list(con, p, uid=0, admin=False):
    g = lambda k: (p.get(k) or [""])[0].strip()
    gallery_tables(con); users_tables(con)
    rows = con.execute("SELECT d.id, d.name, d.commander, d.pub_at, d.pub_meta, d.hidden, d.owner, coalesce(u.name, 'lokal'), d.extra, "
                       "(SELECT count(*) FROM deck_likes l WHERE l.deck_id = d.id), "
                       "(SELECT count(*) FROM deck_likes l WHERE l.deck_id = d.id AND l.uid = ?), "
                       "(SELECT count(*) FROM deck_comments c WHERE c.deck_id = d.id) "
                       "FROM decks d LEFT JOIN users u ON u.id = d.owner WHERE d.public = 1" + ("" if admin else " AND d.hidden = 0"),
                       (uid,)).fetchall()
    q = g("q").lower()
    cols = "".join(x for x in g("ci").upper() if x in "WUBRGC")
    mode = g("cimode") or "within"
    maxeur = float(g("maxeur").replace(",", ".") or 0) if re.fullmatch(r"[\d.,]*", g("maxeur")) else 0
    gcmax = g("gc")
    out = []
    for i, n, c, at, meta, hid, own, oname, extra, likes, mine, ncom in rows:
        try:
            m = json.loads(meta or "{}")
        except Exception:
            m = {}
        dci = m.get("ci", "")
        if q:
            hay = " ".join([n or "", c or "", oname or "", " ".join(m.get("themes") or [])]).lower()
            try:
                hay += " " + (json.loads(extra or "{}").get("notes") or "")[:2000].lower()
            except Exception:
                pass
            if not all(w in hay for w in q.split()):
                continue
        if cols:
            want = set(cols) - {"C"} if cols != "C" else set()
            have = set(dci) - {"C"}
            if mode == "exact" and have != want or mode == "within" and not have <= want or mode == "contains" and not want <= have:
                continue
        if maxeur and (m.get("eur") or 0) > maxeur:
            continue
        if gcmax == "0" and m.get("gc"):
            continue
        if gcmax == "3" and (m.get("gc") or 0) > 3:
            continue
        bf = g("bracket")
        if bf:
            b = m.get("bracket") or {"1–2": "2", "4–5": "4"}.get(m.get("bracket_est") or "", m.get("bracket_est") or "")
            if bf == "12" and b not in ("1", "2") or bf in ("3",) and b != "3" or bf == "45" and b not in ("4", "5"):
                continue
        out.append({"id": i, "name": n, "commander": c, "owner": oname, "mine": own == uid, "pub_at": at, "likes": likes,
                    "liked": bool(mine), "comments": ncom, "hidden": bool(hid), **m})
    srt = g("sort") or "new"
    if srt == "likes":
        out.sort(key=lambda x: (-x["likes"], x["pub_at"] or ""), reverse=False)
    elif srt == "eur":
        out.sort(key=lambda x: x.get("eur") or 0)
    else:
        out.sort(key=lambda x: x["pub_at"] or "", reverse=True)
    return {"total": len(out), "decks": out[:60]}


def gallery_deck(con, did, uid=0, admin=False):
    gallery_tables(con); users_tables(con)
    r = con.execute("SELECT d.id, d.name, d.commander, d.list, d.extra, d.pub_at, d.pub_meta, d.hidden, d.owner, coalesce(u.name, 'lokal') "
                    "FROM decks d LEFT JOIN users u ON u.id = d.owner WHERE d.id = ? AND d.public = 1", (did,)).fetchone()
    if not r or (r[7] and not admin):
        return {"error": "Dieses Deck ist nicht (mehr) öffentlich."}
    try:
        ex = json.loads(r[4] or "{}")
    except Exception:
        ex = {}
    com = [{"id": c[0], "user": c[1], "text": c[2], "at": c[3], "can_delete": admin or c[4] == uid or r[8] == uid}
           for c in con.execute("SELECT id, uname, text, at, uid FROM deck_comments WHERE deck_id = ? ORDER BY id", (did,))]
    likes = con.execute("SELECT count(*) FROM deck_likes WHERE deck_id = ?", (did,)).fetchone()[0]
    liked = bool(con.execute("SELECT 1 FROM deck_likes WHERE deck_id = ? AND uid = ?", (did, uid)).fetchone())
    try:
        m = json.loads(r[6] or "{}")
    except Exception:
        m = {}
    return {"id": r[0], "name": r[1], "commander": r[2], "list": r[3], "notes": ex.get("notes") or "", "maybe": ex.get("maybe") or [],
            "extra": r[4] or "", "pub_at": r[5], "owner": r[9], "mine": r[8] == uid, "hidden": bool(r[7]), "likes": likes, "liked": liked,
            "comments": com, **m}


def gallery_like(con, did, uid):
    gallery_tables(con)
    if not con.execute("SELECT 1 FROM decks WHERE id = ? AND public = 1 AND hidden = 0", (did,)).fetchone():
        return {"error": "Dieses Deck ist nicht öffentlich."}
    if con.execute("SELECT 1 FROM deck_likes WHERE deck_id = ? AND uid = ?", (did, uid)).fetchone():
        con.execute("DELETE FROM deck_likes WHERE deck_id = ? AND uid = ?", (did, uid))
    else:
        con.execute("INSERT INTO deck_likes VALUES(?,?)", (did, uid))
    con.commit()
    return {"ok": True, "likes": con.execute("SELECT count(*) FROM deck_likes WHERE deck_id = ?", (did,)).fetchone()[0],
            "liked": bool(con.execute("SELECT 1 FROM deck_likes WHERE deck_id = ? AND uid = ?", (did, uid)).fetchone())}


def gallery_comment(con, did, text, uid, uname):
    gallery_tables(con)
    text = (text or "").strip()
    if not text:
        return {"error": "Der Kommentar ist leer."}
    if not con.execute("SELECT 1 FROM decks WHERE id = ? AND public = 1 AND hidden = 0", (did,)).fetchone():
        return {"error": "Dieses Deck ist nicht öffentlich."}
    if con.execute("SELECT count(*) FROM deck_comments WHERE deck_id = ?", (did,)).fetchone()[0] >= 200:
        return {"error": "Zu diesem Deck gibt es schon 200 Kommentare."}
    last = con.execute("SELECT at FROM deck_comments WHERE uid = ? ORDER BY id DESC LIMIT 1", (uid,)).fetchone()
    now = datetime.datetime.now()
    if SERVER and last and (now - datetime.datetime.fromisoformat(last[0])).total_seconds() < 5:
        return {"error": "Bitte kurz warten, bevor du den nächsten Kommentar schreibst."}
    con.execute("INSERT INTO deck_comments(deck_id, uid, uname, text, at) VALUES(?,?,?,?,?)",
                (did, uid, uname, text[:500], now.isoformat(sep=" ", timespec="seconds")))
    con.commit()
    return {"ok": True}


def gallery_comment_delete(con, cid, uid, admin=False):
    gallery_tables(con)
    r = con.execute("SELECT c.uid, d.owner FROM deck_comments c JOIN decks d ON d.id = c.deck_id WHERE c.id = ?", (cid,)).fetchone()
    if not r or not (admin or uid in (r[0], r[1])):
        return {"error": "Diesen Kommentar kannst du nicht löschen."}
    con.execute("DELETE FROM deck_comments WHERE id = ?", (cid,))
    con.commit()
    return {"ok": True}


def gallery_copy(con, did, uid, admin=False, new_name=""):
    d = gallery_deck(con, did, uid, admin)
    if d.get("error"):
        return d
    base = (new_name.strip() or d["name"])[:70]
    name, k = base, 1
    while con.execute("SELECT 1 FROM decks WHERE owner = ? AND name = ?", (uid, name)).fetchone():
        k += 1
        name = f"{base} (von {d['owner']})" if k == 2 else f"{base} (von {d['owner']}, {k - 1})"
    con.execute("INSERT INTO decks(owner, name, commander, list, saved_at, note, extra) VALUES(?,?,?,?,?,?,?)",
                (uid, name[:80], d["commander"], d["list"], datetime.datetime.now().isoformat(sep=" ", timespec="minutes"),
                 f"Aus der Galerie von {d['owner']}", d["extra"]))
    con.commit()
    return {"ok": True, "name": name, "decks": deck_list(con, uid)}


def gallery_hide(con, did, on):
    gallery_tables(con)
    con.execute("UPDATE decks SET hidden = ? WHERE id = ?", (1 if on else 0, did))
    con.commit()
    return {"ok": True, "hidden": bool(on)}


def shared_text(tok):
    """Geteiltes Deck als Text (Forge-Format) – zum Importieren in einer anderen Manaschmiede."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,40}", tok or ""):
        return None
    con = db()
    try:
        decks_table(con)
        d = con.execute("SELECT name, commander, list FROM decks WHERE share = ? AND share <> ''", (tok,)).fetchone()
        if not d:
            return None
        cmds = [c.strip() for c in (d[1] or "").split(" + ") if c.strip()]
        lines, main = [f"Name={d[0]}", "[Commander]"] + [f"1 {c}" for c in cmds], []
        for ln in (d[2] or "").splitlines():
            m = re.match(r"^\s*(\d+)\s*x?\s+(.+?)\s*$", ln)
            if m and m.group(2) not in cmds:
                main.append(f"{m.group(1)} {m.group(2)}")
        return "\n".join(lines + ["[Main]"] + main) + "\n"
    finally:
        con.close()


def lan_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("192.168.0.1", 9))  # es wird nichts gesendet; ermittelt nur die eigene Adresse im Heimnetz
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "IP-ADRESSE-DES-PCS"


class H(BaseHTTPRequestHandler):
    def route(self, path, p):
        g = lambda k: (p.get(k) or [""])[0].strip()
        uid = self.user["id"] if self.user else 0
        admin = (not SERVER) or bool(self.user and self.user["admin"])
        if SERVER and path in ("/api/shutdown", "/api/forge_dir"):
            return {"error": "Auf dem Server nicht verfügbar."}
        if not admin and path in ("/api/update", "/api/load_precons", "/api/users", "/api/user_save", "/api/user_delete"):
            return {"error": "Nur für Administratoren."}
        con = db()
        con.row_factory = sqlite3.Row
        try:
            if path == "/api/proxy_list":
                return proxy_list(p, uid)
            if path == "/api/buy_plan":
                return buy_plan(p, uid)
            if path == "/api/buy_set":
                return buy_set(p, uid)
            if path == "/api/buy_done":
                return buy_done(p, uid)
            if path == "/api/buy_csv":
                return buy_csv(p, uid)
            if path.startswith("/api/lab_"):
                return lab_api(path, p, uid)
            if path.startswith("/api/gn_"):
                if path in ("/api/gn_view",) or (path == "/api/gn_report" and g("code")):
                    return gn_api(path, p, uid)
                if SERVER and not self.user:
                    return {"error": "Bitte anmelden.", "login": True}
                return gn_api(path, p, uid)
            if path == "/api/legal":
                if not admin:
                    return {"error": "Nur für Administratoren."}
                return legal_save(p) if any(k in p for k in LEGAL_KEYS) else legal_get()
            if path == "/api/room_create":
                return room_create(g("state"), g("client"), uid)
            if path == "/api/room_get":
                con.close()
                return room_get(g("code"), int(g("since") or 0), g("client"), g("wait") != "0")
            if path == "/api/room_claim":
                return room_claim(g("code"), int(g("seat") or -1), g("client"))
            if path == "/api/room_push":
                return room_push(g("code"), g("client"), g("players"), g("glob"), g("full") == "1")
            if path == "/api/room_close":
                return room_close(g("code"), g("client"), g("result"))
            if path == "/api/user_names":
                if not SERVER:
                    return {"names": []}
                users_tables(con)
                return {"names": [r[0] for r in con.execute("SELECT name FROM users WHERE id <> ? ORDER BY name COLLATE NOCASE", (uid,))]}
            if path == "/api/deck_send":
                if not SERVER or not self.user:
                    return {"error": "Senden an Benutzer gibt es nur im Server-Betrieb. Hier bitte „Als Link senden“ nutzen."}
                return deck_send(con, int(g("id") or 0), g("to"), g("msg"), uid, self.user["name"])
            if path == "/api/deck_public":
                return deck_public(con, int(g("id") or 0), g("on") == "1", uid)
            if path == "/api/gallery":
                return gallery_list(con, p, uid, admin)
            if path == "/api/gallery_deck":
                return gallery_deck(con, int(g("id") or 0), uid, admin)
            if path == "/api/gallery_like":
                return gallery_like(con, int(g("id") or 0), uid)
            if path == "/api/gallery_comment":
                return gallery_comment(con, int(g("id") or 0), g("text"), uid, self.user["name"] if self.user else "Ich")
            if path == "/api/gallery_comment_delete":
                return gallery_comment_delete(con, int(g("cid") or 0), uid, admin)
            if path == "/api/gallery_copy":
                return gallery_copy(con, int(g("id") or 0), uid, admin, g("name"))
            if path == "/api/gallery_hide":
                if not admin:
                    return {"error": "Nur der Administrator kann Decks ausblenden."}
                return gallery_hide(con, int(g("id") or 0), g("on") == "1")
            if path == "/api/inbox":
                return inbox_list(con, uid) if SERVER else {"items": []}
            if path == "/api/inbox_accept":
                return inbox_accept(con, int(g("id") or 0), uid, g("name"))
            if path == "/api/inbox_decline":
                inbox_table(con)
                con.execute("DELETE FROM deck_inbox WHERE id = ? AND to_uid = ?", (int(g("id") or 0), uid))
                con.commit()
                return inbox_list(con, uid)
            if path == "/api/me":
                return {"server": SERVER, "name": self.user["name"] if self.user else None, "admin": admin,
                        "max_games": MAX_GAMES, "version": APP_VERSION}
            if path == "/api/logout":
                if self.user:
                    users_tables(con)
                    con.execute("DELETE FROM sessions WHERE token = ?", (self.token,))
                    con.commit()
                self.clear_cookie = True
                return {"ok": True}
            if path == "/api/password":
                if not self.user:
                    return {"error": "Nicht angemeldet."}
                r = con.execute("SELECT pw FROM users WHERE id = ?", (uid,)).fetchone()
                if not r or not pw_check(g("old"), r[0]):
                    return {"error": "Das bisherige Passwort stimmt nicht."}
                user_set(self.user["name"], (p.get("new") or [""])[0])
                self.new_token = session_new(uid)
                return {"ok": True}
            if path == "/api/users":
                return users_list()
            if path == "/api/user_save":
                user_set(g("name"), (p.get("pw") or [""])[0], admin=g("admin") == "1")
                return users_list()
            if path == "/api/user_delete":
                if int(g("id") or 0) == uid:
                    return {"error": "Du kannst dich nicht selbst löschen."}
                users_tables(con)
                decks_table(con)
                con.execute("DELETE FROM users WHERE id = ?", (int(g("id") or 0),))
                con.execute("DELETE FROM sessions WHERE uid = ?", (int(g("id") or 0),))
                con.execute("DELETE FROM decks WHERE owner = ?", (int(g("id") or 0),))
                collection_table(con)
                con.execute("DELETE FROM collection WHERE owner = ?", (int(g("id") or 0),))
                inv_tables(con)
                con.execute("DELETE FROM coll_items WHERE owner = ?", (int(g("id") or 0),))
                wish_table(con); folder_table(con); gallery_tables(con)
                con.execute("DELETE FROM wishlist WHERE owner = ?", (int(g("id") or 0),))
                con.execute("DELETE FROM coll_folders WHERE owner = ?", (int(g("id") or 0),))
                con.execute("DELETE FROM deck_likes WHERE uid = ? OR deck_id NOT IN (SELECT id FROM decks)", (int(g("id") or 0),))
                con.execute("DELETE FROM deck_comments WHERE deck_id NOT IN (SELECT id FROM decks)")
                games_table(con)
                con.execute("DELETE FROM games WHERE owner = ?", (int(g("id") or 0),))
                con.commit()
                return users_list()
            if path == "/api/build":
                return build(p, uid)
            if path == "/api/collection":
                return collection_summary(con, uid)
            if path == "/api/shopping":
                return shopping_list(con, uid, g("share") != "0")
            if path == "/api/wishlist":
                return wish_list(con, uid)
            if path == "/api/wish_add":
                t = g("target").replace(",", ".")
                return wish_add(con, uid, g("text"), float(t) if re.fullmatch(r"\d+(\.\d+)?", t) else None)
            if path == "/api/wish_set":
                t, q = g("target").replace(",", "."), g("qty")
                return wish_set(con, uid, g("name"), int(q) if q.isdigit() else None,
                                (float(t) if re.fullmatch(r"\d+(\.\d+)?", t) else 0.0) if "target" in p else None, g("remove") == "1")
            if path == "/api/folders":
                return folder_overview(con, uid)
            if path == "/api/folder":
                return folder_get(con, uid, g("folder"))
            if path == "/api/folder_put":
                return folder_put(con, uid, g("folder"), g("text"), g("mode") or "add")
            if path == "/api/folder_delete":
                folder_table(con)
                con.execute("DELETE FROM coll_folders WHERE owner = ? AND folder = ?", (uid, g("folder")))
                con.commit()
                return folder_overview(con, uid)
            if path == "/api/collection_history":
                return collection_history(con, uid)
            if path == "/api/price_alerts":
                return price_alerts(con, uid)
            if path == "/api/budget_swaps":
                return budget_swaps(p, uid)
            if path == "/api/collection_import":
                return collection_import(p, uid)
            if path == "/api/collection_clear":
                collection_table(con)
                con.execute("DELETE FROM collection WHERE owner = ?", (uid,))
                con.execute("DELETE FROM coll_items WHERE owner = ?", (uid,))
                folder_table(con)
                con.execute("DELETE FROM coll_folders WHERE owner = ?", (uid,))
                con.commit()
                return collection_summary(con, uid)
            if path == "/api/scan_match":
                return scan_match(p)
            if path == "/api/ocr_status":
                return ocr_status()
            if path == "/api/ocr_prepare":
                return ocr_prepare()
            if path == "/api/collection_export":
                return {"csv": collection_export(con, uid, g("fmt") or "prints")}
            if path == "/api/inv":
                return inv_list(con, uid, g("q"), g("sort") or "name", int(g("page") or 0), g("only"))
            if path == "/api/inv_set":
                inv_tables(con)
                old, new = json.loads(g("old") or "{}"), json.loads(g("new") or "{}")
                if not old.get("name"):
                    return {"error": "Eintrag fehlt."}
                for k in ("set_code", "number", "cond", "lang"):
                    old.setdefault(k, "")
                old["foil"] = int(old.get("foil") or 0)
                if "foil" in new:
                    new["foil"] = int(new["foil"] or 0)
                if "set_code" in new:
                    new["set_code"] = (new["set_code"] or "").upper()
                n = inv_move(con, uid, old, new, qty=g("qty") if g("qty") != "" else None)
                coll_rebuild(con, uid)
                return {"changed": n, **inv_totals(con, uid)}
            if path == "/api/inv_add":
                it = json.loads(g("item") or "{}")
                hit = lookup(con, it.get("name") or "")[0] if it.get("name") else None
                if not hit:
                    return {"error": "Karte nicht gefunden."}
                it["name"] = hit["name"]
                inv_add(con, uid, it)
                return {"ok": True, "name": hit["name"], **inv_totals(con, uid)}
            if path == "/api/prints":
                hit = lookup(con, g("name"))[0]
                if not hit:
                    return {"error": "Karte nicht gefunden."}
                return prints_of(con, hit["name"], g("force") == "1")
            if path == "/api/inv_resolve":
                return inv_resolve(con, uid)
            if path == "/api/recommend":
                return recommend(p, uid)
            if path == "/api/deck_share":
                return deck_share(con, int(g("id") or 0), g("on") == "1", uid)
            if path == "/api/games":
                return games_overview(con, uid)
            if path == "/api/game_save":
                return game_save(p, uid)
            if path == "/api/game_delete":
                games_table(con)
                con.execute("DELETE FROM games WHERE id = ? AND owner = ?", (int(g("id") or 0), uid))
                con.commit()
                return games_overview(con, uid)
            if path == "/api/price_history":
                return price_history(p)
            if path == "/api/tokens":
                return deck_tokens(p)
            if path == "/api/ownership":
                return ownership(p, uid)
            if path == "/api/search":
                return search(p)
            if path == "/api/commander_suggest":
                return suggest_commanders(p)
            if path == "/api/suggest":
                return find_names(con, g("q"), g("cmd") == "1")
            if path == "/api/card":
                r, _ = lookup(con, g("name"), g("commander") == "1")
                return {"name": r["name"], "ci": r["color_identity"], "can_be_commander": bool(r["can_be_commander"]),
                        "legal": bool(r["commander_legal"]), "image": r["image"] or ""} if r else {}
            if path == "/api/info":
                return {k: v for k, v in con.execute("SELECT key, value FROM meta")}
            if path == "/api/precons_all":
                if not has_precons(con):
                    return []
                return [{"id": r[0], "name": r[1], "set": r[2], "date": r[3] or "", "commander": r[4], "ci": r[5]}
                        for r in con.execute("SELECT id, name, set_name, release_date, commander, color_identity FROM precons "
                                             "ORDER BY release_date DESC, set_name, name")]
            if path == "/api/precons":
                return precon_list(con, g("q"), g("ci").upper()) if has_precons(con) else []
            if path == "/api/precon":
                return precon_view(p)
            if path == "/api/cm":
                return cm_info(con, g("name"))
            if path == "/api/precon_catalog":
                return precon_catalog(con, uid)
            if path == "/api/precon_to_collection":
                return precon_to_collection(con, int(g("id") or 0), uid)
            if path == "/api/alternatives":
                return alternatives(p)
            if path == "/api/combos":
                return combos_for(p)
            if path == "/api/bracket":
                return bracket_for(p, uid)
            if path == "/api/forge":
                return forge_status()
            if path == "/api/forge_dir":
                setting("forge_dir", g("dir").strip().strip('"'))
                return forge_status()
            if path == "/api/duel_start":
                return duel_start(p, uid)
            if path == "/api/playtest":
                return playtest_decks(p, uid)
            if path == "/api/card_texts":
                return card_texts(p)
            if path == "/api/forge_play":
                return forge_play(p, uid)
            if path == "/api/duel_detail":
                return duel_detail(p, uid)
            if path == "/api/duel_status":
                return duel_status(p, uid)
            if path == "/api/duel_cancel":
                j = JOBS.get(g("job"))
                j = j if j and j.get("owner", 0) == uid else None
                if j:
                    j["cancel"] = True
                return {"ok": bool(j)}
            if path == "/api/compare":
                return compare(p)
            if path == "/api/import":
                return import_deck(p)
            if path == "/api/deck_view":
                return deck_view(p)
            if path == "/api/decks":
                return deck_list(con, uid)
            if path == "/api/deck_save":
                r = deck_save(p, uid)
                if r.get("ok"):
                    con.execute("UPDATE decks SET bracket_est = ? WHERE owner = ? AND name = ?",
                                (bracket_quick(db(), g("commander"), g("list")), uid, r["name"]))
                    con.commit()
                    gallery_refresh(con, uid, r["name"])
                    r["decks"] = deck_list(con, uid)
                return r
            if path == "/api/deck_get":
                return deck_get(con, int(g("id") or 0), uid) or {"error": "Deck nicht gefunden."}
            if path == "/api/deck_delete":
                decks_table(con)
                gallery_tables(con)
                did = int(g("id") or 0)
                if con.execute("SELECT 1 FROM decks WHERE id = ? AND owner = ?", (did, uid)).fetchone():
                    con.execute("DELETE FROM deck_likes WHERE deck_id = ?", (did,))
                    con.execute("DELETE FROM deck_comments WHERE deck_id = ?", (did,))
                con.execute("DELETE FROM decks WHERE id = ? AND owner = ?", (did, uid))
                con.commit()
                return deck_list(con, uid)
            if path == "/api/version":
                return {"version": APP_VERSION, "pid": os.getpid()}
            if path == "/api/shutdown":
                if self.client_address[0] != "127.0.0.1":
                    return {"error": "nur lokal erlaubt"}
                threading.Timer(0.3, lambda: os._exit(0)).start()
                return {"ok": True}
            if path == "/api/card_info":
                r, hint = lookup(con, g("name"))
                if not r:
                    return {"error": f"Karte „{g('name')}“ nicht gefunden."}
                d = card_dict(r)
                d.update(ci=r["color_identity"], legal=bool(r["commander_legal"]), basic=r["type_line"].startswith("Basic"),
                         type=r["type_line"], hint=hint)
                if d["basic"]:
                    d["eur"] = None
                return d
            if path == "/api/manabase":
                return mana_analysis(p)
            if path == "/api/deck_versions":
                return deck_versions(con, int(g("id") or 0), uid)
            if path == "/api/deck_version_diff":
                return deck_version_diff(con, int(g("id") or 0), int(g("a") or 0), int(g("b") or 0), uid)
            if path == "/api/partner_check":
                cm = resolve_cmds(con, g("commander"))
                return {"ok": True} if len(cm) != 2 else ({"error": partner_problem(cm)} if partner_problem(cm) else {"ok": True})
            if path == "/api/deck_restore":
                return deck_restore(con, int(g("id") or 0), int(g("vid") or 0), uid)
            if path == "/api/rules":
                return rules_query(p)
            if path == "/api/update_status":
                return UPDATE
            if path == "/api/update":
                threading.Thread(target=auto_update, args=(g("force") == "1",), daemon=True).start()
                return {"started": True}
            if path == "/api/export":
                return deck_export(p)
            if path == "/api/load_precons":
                return {"count": do_precons()}
            return None
        finally:
            con.close()

    PUBLIC = {"/login", "/api/login", "/api/version", "/manifest.webmanifest", "/sw.js", "/offline", "/api/gn_view", "/api/gn_report",
              "/icon-192.png", "/icon-512.png", "/icon-maskable-512.png", "/favicon.ico"}

    def client_ip(self):
        fwd = self.headers.get("X-Forwarded-For") if SERVER else None
        return (fwd.split(",")[0].strip() if fwd else self.client_address[0])

    def send(self, body, ct, code=200, extra=()):
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache"); self.send_header("Expires", "0")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        if SERVER:
            self.send_header("X-Frame-Options", "DENY")
        for k, v in extra:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def cookie(self, name):
        for part in (self.headers.get("Cookie") or "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == name:
                return v
        return ""

    def session_cookie(self, token, age):
        secure = "; Secure" if self.headers.get("X-Forwarded-Proto", "") == "https" else ""
        return ("Set-Cookie", f"cdbsess={token}; Max-Age={age}; Path=/; HttpOnly; SameSite=Lax{secure}")

    def answer(self, path, p):
        if path.startswith("/d/") and path.endswith(".txt"):  # geteiltes Deck als Text (zum Import in einer anderen Manaschmiede)
            t = shared_text(path[3:-4])
            if t is None:
                return self.send(b"not found", "text/plain", 404)
            return self.send(t.encode(), "text/plain; charset=utf-8", extra=[("X-Robots-Tag", "noindex"), ("Access-Control-Allow-Origin", "*")])
        if path in ("/impressum", "/datenschutz"):
            return self.send(legal_page(path[1:]).encode(), "text/html; charset=utf-8")
        if path.startswith("/n/") and len(path) <= 12:  # Spielabend für Mitspieler: ohne Anmeldung, über den Code
            return self.send(GN_PAGE.encode(), "text/html; charset=utf-8", extra=[("X-Robots-Tag", "noindex")])
        if path == "/qr.js":
            return self.send(zlib.decompress(base64.b64decode(QR_JS_Z)), "text/javascript")
        if path.startswith("/d/"):  # geteilte Decks: öffentlich lesbar, ohne Anmeldung und ohne Zugangscode
            page = shared_page(path[3:])
            if page is None:
                return self.send("<!doctype html><meta charset=utf-8><h3>Dieser Link ist ungültig oder wurde widerrufen.</h3>".encode(),
                                 "text/html; charset=utf-8", 404)
            return self.send(page.encode(), "text/html; charset=utf-8", extra=[("X-Robots-Tag", "noindex")])
        if LAN_KEY and not (path == "/api/gn_view" or (path == "/api/gn_report" and (p.get("code") or [""])[0])):
            ok = self.cookie("cdbkey") == LAN_KEY or (p.get("key") or [""])[0] == LAN_KEY
            if not ok:
                body = ("<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'>"
                        "<h3>Zugangscode fehlt</h3><p>Bitte den vollständigen Link aus dem Fenster auf dem PC öffnen "
                        "(er endet mit <code>?key=…</code>).</p>").encode()
                return self.send(body, "text/html; charset=utf-8", 403)
        # App-Dateien (für „Zum Startbildschirm hinzufügen“ / Installation als App)
        if path == "/manifest.webmanifest":
            return self.send(json.dumps(manifest()).encode(), "application/manifest+json")
        if path.startswith("/ocr/"):  # Dateien der Texterkennung (nur die bekannten, keine beliebigen Pfade)
            rel = path[5:]
            if rel not in ocr_files() or not os.path.isfile(os.path.join(OCR_DIR, rel)):
                return self.send(b"not found", "text/plain", 404)
            ct = "application/wasm" if rel.endswith(".wasm") else ("text/javascript" if rel.endswith(".js") else "application/octet-stream")
            with open(os.path.join(OCR_DIR, rel), "rb") as f:
                return self.send(f.read(), ct)
        if path == "/sw.js":
            return self.send((SW_JS % APP_VERSION).encode(), "text/javascript", extra=[("Service-Worker-Allowed", "/")])
        if path in ("/icon-192.png", "/icon-512.png", "/icon-maskable-512.png", "/favicon.ico"):
            size = 192 if "192" in path or path == "/favicon.ico" else 512
            return self.send(app_icon(size, "maskable" in path), "image/png")
        if path == "/offline":
            return self.send(OFFLINE_PAGE.encode(), "text/html; charset=utf-8")
        self.user, self.token, self.clear_cookie, self.new_token = None, "", False, None
        extra = []
        if SERVER:
            if path == "/api/login":
                token, err = login(p, self.client_ip())
                if not token:
                    return self.send(json.dumps({"error": err}).encode(), "application/json", 401)
                return self.send(b'{"ok": true}', "application/json", extra=[self.session_cookie(token, SESSION_DAYS * 86400)])
            if path == "/login":
                return self.send(LOGIN_PAGE.encode(), "text/html; charset=utf-8")
            self.token = self.cookie("cdbsess")
            self.user = session_user(self.token)
            if not self.user and path not in self.PUBLIC:
                if path.startswith("/api/"):
                    return self.send(json.dumps({"error": "Bitte anmelden.", "login": True}).encode(), "application/json", 401)
                return self.send(b"", "text/html", 302, extra=[("Location", "/login")])
        try:
            res = self.route(path, p)
        except ValueError as e:
            res = {"error": str(e)}
        except Exception as e:
            res = {"error": "Interner Fehler. Bitte erneut versuchen." if SERVER else f"Fehler: {e}"}
            if SERVER:
                print(f"Fehler bei {path}: {e!r}")
        if self.clear_cookie:
            extra.append(self.session_cookie("", 0))
        if self.new_token:
            extra.append(self.session_cookie(self.new_token, SESSION_DAYS * 86400))
        if LAN_KEY:
            extra.append(("Set-Cookie", f"cdbkey={LAN_KEY}; Max-Age=31536000; SameSite=Strict; Path=/"))
        if res is None:
            self.send(PAGE.encode(), "text/html; charset=utf-8", extra=extra)
        else:
            self.send(json.dumps(res).encode(), "application/json", extra=extra)

    def do_GET(self):
        u = urlparse(self.path)
        self.answer(u.path, parse_qs(u.query))

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 5_000_000:
            return self.send(json.dumps({"error": "Anfrage zu groß."}).encode(), "application/json", 413)
        self.answer(urlparse(self.path).path, parse_qs(self.rfile.read(n).decode("utf-8")))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["import", "precons", "serve", "update", "adduser"])
    ap.add_argument("name", nargs="?", help="Benutzername (für adduser)")
    ap.add_argument("--admin", action="store_true", help="adduser: Benutzer wird Administrator")
    ap.add_argument("--no-update", action="store_true", help="beim Start nicht nach Updates suchen")
    ap.add_argument("--lan", action="store_true", help="auch für Handy/Tablet im Heimnetz erreichbar (mit Zugangscode)")
    ap.add_argument("--no-browser", action="store_true", help="Browser nicht automatisch öffnen")
    ap.add_argument("--file")
    ap.add_argument("--port", type=int, default=int(ENV("CDB_PORT", "8000")))
    a = ap.parse_args()
    if a.cmd == "import":
        do_import(a.file)
        try:
            do_precons()
        except Exception as e:
            print(f"Precons konnten nicht geladen werden ({e}). Später mit 'precons' nachholen.")
    elif a.cmd == "precons":
        do_precons(a.file)
    elif a.cmd == "adduser":
        if not a.name:
            sys.exit("Bitte einen Benutzernamen angeben: adduser NAME [--admin]")
        pw = ENV("CDB_NEW_PASSWORD") or getpass.getpass(f"Passwort für {a.name}: ")
        try:
            user_set(a.name, pw, admin=True if a.admin else None)
            print(f"Benutzer „{a.name}“ gespeichert.")
        except ValueError as e:
            sys.exit(str(e))
    elif a.cmd == "update":
        upgrade_db()
        print("Prüfe auf Updates ...")
        auto_update(force=False)
    else:
        os.makedirs(DATA_DIR, exist_ok=True)
        has_cards = False
        try:
            has_cards = bool(db().execute("SELECT 1 FROM cards LIMIT 1").fetchone())
        except sqlite3.Error:
            pass
        if not has_cards:
            print("Noch keine Kartendaten vorhanden. Sie werden jetzt einmalig von Scryfall geladen (1–3 Minuten) ...")
            wait = 30
            while True:
                try:
                    do_import(None)
                    break
                except (Exception, SystemExit) as e:
                    if not SERVER:
                        raise
                    print(f"Kartendaten konnten nicht geladen werden ({e}). Neuer Versuch in {wait} Sekunden ...")
                    time.sleep(wait)
                    wait = min(wait * 2, 600)
            try:
                do_precons()
            except Exception as e:
                print(f"Precons konnten nicht geladen werden ({e}). Sie werden später automatisch nachgeholt.")
        upgrade_db()
        ensure_price_baseline()
        try:
            db().execute("PRAGMA journal_mode=WAL")  # Lesen und Schreiben gleichzeitig möglich
        except Exception:
            pass
        if not a.no_update:
            print("Prüfe im Hintergrund auf neue Regeln, Precons und Kartendaten ...")
            threading.Thread(target=auto_update, daemon=True).start()
        UPDATE["max_age"] = CARDS_MAX_AGE_DAYS
        if UPDATE_HOUR is not None and (SERVER or ENV("CDB_DAILY_UPDATE", "") == "1"):
            threading.Thread(target=update_scheduler, daemon=True).start()
            print(f"Tägliche Prüfung auf neue Daten um {UPDATE_HOUR}:07 Uhr; Kartendaten werden ab {CARDS_MAX_AGE_DAYS} Tag(en) Alter neu geladen.")
        host = "127.0.0.1"
        if SERVER:
            ensure_admin()
            host, a.no_browser, a.lan = ENV("CDB_HOST", "0.0.0.0"), True, False
        if a.lan:
            LAN_KEY = setting("lan_key") or setting("lan_key", hashlib.sha1(os.urandom(16)).hexdigest()[:12])
            host = "0.0.0.0"
        srv = None
        ThreadingHTTPServer.daemon_threads = True
        try:
            srv = ThreadingHTTPServer((host, a.port), H)
        except OSError:
            if SERVER:
                raise
            other = None
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{a.port}/api/version", timeout=3) as r:
                    other = json.loads(r.read()).get("version")
            except Exception:
                pass
            if other:  # eine Version mit Abschaltfunktion läuft noch -> beenden und Port übernehmen
                print(f"Auf Port {a.port} läuft noch Version {other}, sie wird beendet ...")
                try:
                    urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{a.port}/api/shutdown", data=b""), timeout=3)
                except Exception:
                    pass
                for _ in range(20):
                    try:
                        srv = ThreadingHTTPServer((host, a.port), H)
                        break
                    except OSError:
                        __import__("time").sleep(0.5)
            if srv is None:
                for port in range(a.port + 1, a.port + 20):
                    try:
                        srv = ThreadingHTTPServer((host, port), H)
                        print(f"Port {a.port} ist von einem anderen (älteren) Programm belegt. "
                              f"verwende Port {port}. Tipp: alte Fenster der Datenbank schließen.")
                        a.port = port
                        break
                    except OSError:
                        continue
            if srv is None:
                sys.exit("Kein freier Port gefunden. Bitte alle Fenster der Datenbank schließen und neu starten.")
        if LAN_KEY:
            print("\nZugriff von Handy/Tablet im selben WLAN: diesen Link dort öffnen")
            print(f"    http://{lan_ip()}:{a.port}/?key={LAN_KEY}\n")
            print("(Windows fragt eventuell nach einer Firewall-Freigabe: für private Netzwerke erlauben.)")
        print(f"Manaschmiede (Version {APP_VERSION}) läuft auf http://localhost:{a.port}  (dieses Fenster offen lassen; Beenden mit Strg+C)")
        if not a.no_browser:
            import webbrowser
            threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{a.port}/" + (f"?key={LAN_KEY}" if LAN_KEY else ""))).start()
        srv.serve_forever()
