#!/usr/bin/env python3
"""Commander-Datenbank auf Basis der Scryfall-Bulk-Daten (SQLite + lokale Suche).

  python commander_db_v9.py import            # lädt "Oracle Cards" von Scryfall + Precons, baut cards.db
  python commander_db_v9.py import --file x.json   # statt Download eine lokale JSON-Datei nutzen
  python commander_db_v9.py precons           # nur die Precon-Decklisten (neu) laden
  python commander_db_v9.py serve             # Oberfläche unter http://localhost:8000 (prüft beim Start auf Updates)
  python commander_db_v9.py serve --no-update # ohne Update-Prüfung starten
  python commander_db_v9.py update            # Regeln, Precons und Kartendaten jetzt aktualisieren
Nur Python-Standardbibliothek, keine Installation nötig.

Version 2: Namensvorschläge beim Tippen und Tippfehler-Toleranz, Farbidentität wird aus dem
Commander übernommen, alle Eingaben optional, Preise als Zahl, Importdatum, Grist-Fix.
Version 3: Deckansicht mit Kartenbildern, Vergleich mit offiziellen Commander-Precons
(Decklisten: github.com/taw/magic-preconstructed-decks-data, auch Grundlage von mtg.wtf/MTGJSON).
Version 4: Karten gezielt tauschen oder entfernen (mit Alternativen gleicher Aufgabe), Option ohne
Game Changer, Liste nicht verfügbarer Karten, bessere Ramp-Erkennung.
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
import argparse, csv, datetime, difflib, io, gzip, hashlib, json, os, random, re, shutil, sqlite3, subprocess, sys, tempfile, threading, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards.db")  # liegt neben dem Skript
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
    now = datetime.datetime.now().isoformat(sep=" ", timespec="minutes")
    con.executemany("INSERT OR REPLACE INTO meta VALUES(?,?)",
                    [("imported_at", now), ("source_date", source_date or "unbekannt"), ("count", str(len(rows)))])
    con.commit()
    print(f"{len(rows)} Karten in {DB} gespeichert.")


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


def lookup(con, name, commander=False):
    """Liefert (Karte, Hinweis). Bei mehreren gleichnamigen Karten wird die Commander-legale bevorzugt."""
    pref = "ORDER BY commander_legal DESC, can_be_commander DESC, edhrec_rank IS NULL, edhrec_rank LIMIT 1"
    r = con.execute(f"SELECT * FROM cards WHERE name = ? COLLATE NOCASE {pref}", (name,)).fetchone()
    if r:
        return r, None
    hits = find_names(con, name, commander, 1) or (find_names(con, name, False, 1) if commander else [])
    if not hits:
        return None, None
    r = con.execute(f"SELECT * FROM cards WHERE name = ? {pref}", (hits[0],)).fetchone()
    return r, f"„{name}“ nicht exakt gefunden – verwendet: {r['name']}."


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
    sql = "SELECT name,mana_cost,cmc,type_line,color_identity,edhrec_rank,eur,scryfall_uri,cardmarket_uri,game_changer FROM cards"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY edhrec_rank IS NULL, edhrec_rank, name LIMIT 100"
    con = db()
    keys = "name mana cmc type ci rank eur scryfall cardmarket gc".split()
    rows = [dict(zip(keys, r)) for r in con.execute(sql, args)]
    for r in rows:
        r["eur"] = float(r["eur"]) if r["eur"] not in (None, "") else None
    return rows


def card_dict(r, qty=1):
    eur = r["eur"]
    return {"name": r["name"], "mana": r["mana_cost"], "cmc": r["cmc"], "qty": qty,
            "eur": float(eur) if eur not in (None, "") else None, "image": r["image"],
            "scryfall": r["scryfall_uri"], "cardmarket": r["cardmarket_uri"], "gc": bool(r["game_changer"]),
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
}
ALIAS = {"lebensgewinn": "lifegain", "opfer": "aristocrats", "marken": "counters", "zauber": "spellslinger"}
FIXED = [  # Name, Ziel-Anzahl, SQL-Bedingung (Nicht-Länder)
    ("Ramp", 10, "(oracle_text LIKE '%Add {%' OR oracle_text LIKE '%Add one mana%' OR oracle_text LIKE '%Add two mana%' OR oracle_text LIKE '%basic land card%') AND cmc <= 3"),
    ("Kartenvorteil", 9, "(oracle_text LIKE '%draw a card%' OR oracle_text LIKE '%draw two%' OR oracle_text LIKE '%draw three%')"),
    ("Entfernung", 8, "(oracle_text LIKE '%destroy target%' OR oracle_text LIKE '%exile target%')"),
    ("Massenentfernung", 3, "(oracle_text LIKE '%destroy all%' OR oracle_text LIKE '%exile all%')"),
]
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


def build(p):
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
    cmd = one(g("commander"), True) if g("commander") else None
    if g("commander") and not cmd:
        notes.append(f"Commander „{g('commander')}“ nicht gefunden – Deck wird ohne Commander vorgeschlagen.")
    elif cmd and not cmd["can_be_commander"]:
        notes.append(f"{cmd['name']} gilt nach meiner Näherung nicht als Commander – bitte prüfen.")
    if cmd and not cmd["commander_legal"]:
        notes.append(f"{cmd['name']} ist im Commander-Format nicht legal (gebannt).")
    own, chosen = [], set([cmd["name"]] if cmd else [])
    nogc = g("nogc") == "1"
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
    if cmd:
        ci = cmd["color_identity"]
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
        notes.append("Deine eigenen Karten enthalten Game Changer – diese wurden trotz Filter übernommen.")
    if excluded:
        notes.append(f"{len(excluded)} als nicht verfügbar markierte Karten wurden ausgeschlossen.")
    for r in own:
        if any(x not in ci for x in r["color_identity"]):
            notes.append(f"{r['name']} passt nicht zur Farbidentität ({ci or 'farblos'}).")

    def pick(sql, args, n):
        if n <= 0:
            return []
        where, a = ["commander_legal = 1", "type_line NOT LIKE 'Basic%'"], []
        for x in ORDER:
            if x not in ci:
                where.append("color_identity NOT LIKE ?"); a.append(f"%{x}%")
        if nogc:
            where.append("game_changer = 0")
        block = chosen | excluded
        if block:
            where.append("name NOT IN (%s)" % ",".join("?" * len(block))); a += list(block)
        rows = con.execute(f"SELECT * FROM cards WHERE {' AND '.join(where)} AND {sql} "
                           f"ORDER BY edhrec_rank IS NULL, edhrec_rank LIMIT {int(n)}", a + args).fetchall()
        chosen.update(r["name"] for r in rows)
        return rows

    groups = [("Deine Karten", own)] if own else []
    nonland = lambda: sum(1 for _, rs in groups for r in rs if not island(r))
    for name, n, sql in FIXED:
        groups.append((name, pick(f"{NL} AND {sql}", [], n)))
    tsql, targs = theme_sql(g("theme"))
    if tsql:
        groups.append((f"Thema: {g('theme')}", pick(f"{NL} AND {tsql}", targs, 57 - nonland())))
    else:
        notes.append("Kein Thema angegeben – es wurden allgemein beliebte Karten gewählt.")
    groups.append(("Weitere beliebte Karten", pick(NL, [], 63 - nonland())))

    own_l = sum(1 for r in own if island(r))
    lands_total = 99 - nonland()
    util = pick("type_line LIKE '%Land%'", [], max(0, min(8, lands_total - own_l)))
    allr = [r for _, rs in groups for r in rs] + util
    nb = lands_total - own_l - len(util)
    spells = [r for r in allr if not island(r)] + ([cmd] if cmd else [])
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

    out = ([{"name": "Commander", "cards": [card_dict(cmd)]}] if cmd else [])
    out += [{"name": n, "cards": [card_dict(r) for r in rs]} for n, rs in groups if rs]
    out.append({"name": "Länder", "cards": [card_dict(r) for r in util] + [basic_dict(con, n, k) for n, k in basics]})
    curve = [0] * 8
    for r in allr:
        if not island(r):
            curve[min(int(r["cmc"]), 7)] += 1
    priced = [float(r["eur"]) for r in allr + ([cmd] if cmd else []) if r["eur"] not in (None, "")]
    total = len(allr) + sum(k for _, k in basics)
    if total < 99:
        notes.append(f"Es konnten nur {total} von 99 Karten gefunden werden.")
    notes.append("Die Auswahl folgt der allgemeinen EDHREC-Beliebtheit, nicht commanderspezifischen Daten – bitte prüfen.")
    lines = [f"{c['qty']} {c['name']}" for gr in out for c in gr["cards"]]
    return {"commander": cmd["name"] if cmd else None, "ci": ci, "notes": notes, "groups": out, "curve": curve,
            "cost": {"total": sum(priced), "priced": len(priced), "missing": len(allr) + (1 if cmd else 0) - len(priced)},
            "export": "\n".join(lines)}


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
    if m["mld"] or gc > 3:
        bracket = "4"
    elif gc or m["extra"] >= 3:
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
        raise ValueError(f"Nur {len(rules)} Regeln erkannt – Datei unvollständig?")
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
        return dict(meta, error="Die Regeln sind noch nicht geladen – oben auf „Jetzt aktualisieren“ klicken.", rules=[], glossary=[])
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
UPDATE = {"running": False, "done": False, "items": {}, "at": ""}
CARDS_MAX_AGE_DAYS = 7


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
        return f"aktuell genug (Stand {local}{'; neuere Daten von ' + remote + ' werden ab 7 Tagen Alter geladen' if remote > local else ''})"
    do_import(None)
    return f"neu geladen: Stand {setting('source_date')}, {setting('count')} Karten"


def auto_update(force=False, parts=("rules", "precons", "cards")):
    if UPDATE["running"]:
        return
    UPDATE.update(running=True, done=False, items={})
    labels = {"rules": "Regeln", "precons": "Precons", "cards": "Kartendaten"}
    for k in parts:
        UPDATE["items"][k] = {"label": labels[k], "status": "wird geprüft ...", "ok": None}
    for k, fn in (("rules", update_rules), ("precons", update_precons), ("cards", update_cards)):
        if k not in parts:
            continue
        try:
            UPDATE["items"][k].update(status=fn(force), ok=True)
        except Exception as e:
            UPDATE["items"][k].update(status=f"Prüfung fehlgeschlagen ({e}) – die vorhandenen Daten werden weiter genutzt.", ok=False)
        print(f"  {labels[k]}: {UPDATE['items'][k]['status']}")
    UPDATE.update(running=False, done=True, at=datetime.datetime.now().isoformat(sep=" ", timespec="minutes"))
    setting("updated_at", UPDATE["at"])

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
    if "deckstats.net/decks/" in u:
        return "text", http_get(u.split("?")[0] + "?include_comments=1&export_txt=1")
    body = http_get(u)
    if body.lstrip().startswith("{"):
        return "json", json.loads(body)
    if "<html" in body[:500].lower():
        raise RuntimeError("Diese Seite liefert keine Deckliste als Text. Bitte auf der Seite die Exportfunktion nutzen "
                           "und die Liste hier einfügen oder als Datei hochladen.")
    return "text", body


def import_deck(p):
    """Erkennt Format und Commander, gleicht alle Namen mit der Datenbank ab."""
    g = lambda k: (p.get(k) or [""])[0]
    text, url, fname = g("text"), g("url").strip(), g("filename")
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
                    notes.append("Commander aus dem abgesetzten Block der Liste erkannt – bitte prüfen.")
                    break
    candidates = [n for n in rows if can(n)]
    if not cmds and candidates:
        first = lookup(con, raw[0][1])[0]
        if first and first["name"] in candidates:
            cmds = [first["name"]]
            notes.append("Kein Commander markiert – die erste Karte wurde angenommen, bitte prüfen.")
        else:
            notes.append("Kein Commander markiert – bitte unten auswählen.")
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
    con.execute("CREATE TABLE IF NOT EXISTS decks(id INTEGER PRIMARY KEY, name TEXT UNIQUE, commander TEXT, list TEXT, saved_at TEXT)")


def deck_save(p):
    g = lambda k: (p.get(k) or [""])[0].strip()
    if not g("list"):
        return {"error": "Leere Deckliste."}
    name = g("name") or g("commander") or "Mein Deck"
    con = db()
    decks_table(con)
    con.execute("INSERT INTO decks(name, commander, list, saved_at) VALUES(?,?,?,?) ON CONFLICT(name) DO UPDATE SET "
                "commander = excluded.commander, list = excluded.list, saved_at = excluded.saved_at",
                (name, g("commander"), g("list"), datetime.datetime.now().isoformat(sep=" ", timespec="minutes")))
    con.commit()
    return {"ok": True, "name": name, "decks": deck_list(con)}


def deck_count(text):
    return sum(int(re.match(r"\s*(\d*)", l).group(1) or 1) for l in (text or "").splitlines() if l.strip())


def deck_list(con):
    decks_table(con)
    return [{"id": i, "name": n, "commander": c, "saved_at": t, "count": deck_count(l)}
            for i, n, c, l, t in con.execute("SELECT id, name, commander, list, saved_at FROM decks ORDER BY name COLLATE NOCASE")]


def deck_get(con, did):
    decks_table(con)
    r = con.execute("SELECT id, name, commander, list FROM decks WHERE id = ?", (did,)).fetchone()
    return {"id": r[0], "name": r[1], "commander": r[2], "list": r[3]} if r else None


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
        text = "\n".join([f"1x {r['name']} [Commander{{top}}]" for r in cmds] + [f"{q}x {r['name']}" for r, q in main])
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
    return {"name": pr["name"], "set": pr["set_name"], "date": pr["release_date"], "groups": groups,
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
        return {"error": "Kein eigenes Deck zum Vergleichen – bitte zuerst ein Deck vorschlagen oder laden."}
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
        verdict = f"Dein Deck liegt in {sa} von {len(DUEL)} Kategorien vorn – auf dem Papier stärker als „{nm}“."
    elif sb > sa:
        verdict = f"„{nm}“ liegt in {sb} von {len(DUEL)} Kategorien vorn – dein Deck hat dort Nachholbedarf."
    else:
        verdict = f"Ausgeglichen: beide Decks gewinnen gleich viele Kategorien ({sa}:{sb})."
    if a["bracket"] != b["bracket"]:
        verdict += f" Achtung: unterschiedliche Bracket-Schätzung ({a['bracket']} gegen {b['bracket']})."
    return {"opp": {"kind": opp["kind"], "id": opp.get("id"), "name": nm, "set": opp["set"], "commander": opp["commander"]},
            "rows": rows, "score": [sa, sb], "verdict": verdict, "a": a, "b": b,
            "shared": shared, "ideas": [card_dict(r) for r in ideas], "missing": miss_a + opp["missing"]}


# ---------------------------------------------------------------- Combos (Commander Spellbook)
SPELLBOOK = "https://backend.commanderspellbook.com/find-my-combos"
BRACKET_TAG = {"R": "Ruthless", "S": "Spicy", "P": "Powerful", "O": "Oddball", "C": "Core", "E": "Exhibition", "B": "gebannt"}


def fetch_combos(con, commanders, main):
    """Alle in der Liste enthaltenen Combos laut Commander Spellbook (mit Zwischenspeicher)."""
    key = hashlib.sha1(json.dumps([sorted(commanders), sorted(main)]).encode()).hexdigest()
    con.execute("CREATE TABLE IF NOT EXISTS combo_cache(key TEXT PRIMARY KEY, data TEXT, fetched_at TEXT)")
    hit = con.execute("SELECT data FROM combo_cache WHERE key = ?", (key,)).fetchone()
    if hit:
        return json.loads(hit[0])
    body = json.dumps({"main": [{"card": n, "quantity": q} for n, q in main],
                       "commanders": [{"card": n, "quantity": 1} for n in commanders]}).encode()
    included, url, pages = [], SPELLBOOK + "?limit=100", 0
    while url and pages < 20:
        req = urllib.request.Request(url, data=body, method="POST",
                                     headers=dict(HEADERS, **{"Content-Type": "application/json"}))
        with urllib.request.urlopen(req, timeout=60) as r:
            page = json.loads(r.read())
        included += (page.get("results") or {}).get("included") or []
        url, pages = page.get("next"), pages + 1
    combos = []
    for v in included:
        uses = [{"name": u["card"]["name"], "zones": u.get("zoneLocations") or [],
                 "commander": bool(u.get("mustBeCommander"))} for u in v.get("uses") or []]
        combos.append({
            "id": v.get("id"), "cards": uses,
            "requires": [t["template"]["name"] for t in v.get("requires") or []],
            "produces": [f["feature"]["name"] for f in v.get("produces") or []],
            "mana": v.get("manaNeeded") or "", "mana_value": v.get("manaValueNeeded") or 0,
            "tag": v.get("bracketTag") or "", "steps": v.get("description") or "",
            "prereq": " ".join(x for x in (v.get("easyPrerequisites"), v.get("notablePrerequisites")) if x),
            "url": f"https://commanderspellbook.com/combo/{v.get('id')}/"})
    con.execute("INSERT OR REPLACE INTO combo_cache VALUES(?,?,?)",
                (key, json.dumps(combos), datetime.datetime.now().isoformat(sep=" ", timespec="minutes")))
    con.commit()
    return combos


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
        combos = fetch_combos(con, list(commander_names), main)
    except Exception as e:
        return {"error": f"Combo-Datenbank nicht erreichbar ({e}). Internetverbindung prüfen.", "combos": []}
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
    return {"combos": combos, "bracket_floor": floor, "count": len(combos), "win_count": sum(c["win"] for c in combos)}


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
FORGE_JVM = ("-Xmx4096m -Dio.netty.tryReflectionSetAccessible=true -Dfile.encoding=UTF-8 "
             + " ".join(f"--add-opens {m}=ALL-UNNAMED" for m in (
                 "java.desktop/java.beans", "java.desktop/javax.swing.border", "java.desktop/javax.swing.event",
                 "java.desktop/sun.swing", "java.desktop/java.awt.image", "java.desktop/java.awt.color",
                 "java.desktop/sun.awt.image", "java.desktop/javax.swing", "java.desktop/java.awt",
                 "java.base/java.util", "java.base/java.lang", "java.base/java.lang.reflect", "java.base/java.text",
                 "java.desktop/java.awt.font", "java.base/jdk.internal.misc", "java.base/sun.nio.ch",
                 "java.base/java.nio", "java.base/java.math", "java.base/java.util.concurrent", "java.base/java.net"))).split()
JOBS = {}


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
    manual = setting("java_path")
    if manual and os.path.exists(manual):
        return manual, java_version(manual)
    best = (None, 0)
    for j in java_candidates():
        v = java_version(j)
        if v > best[1]:
            best = (j, v)
    return best


def forge_status():
    d = setting("forge_dir")
    java, ver = java_info()
    jar = None
    if d and os.path.isdir(d):
        jars = sorted(f for f in os.listdir(d) if f.startswith("forge-gui-desktop") and f.endswith("jar-with-dependencies.jar"))
        jar = jars[-1] if jars else None
    msg = []
    if not java:
        msg.append("Java nicht gefunden – bitte Java 17 oder neuer installieren.")
    elif ver < 17:
        msg.append(f"Java {ver} ist zu alt – Forge braucht Java 17 oder neuer.")
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
           ("21 damage from generals", "Commander-Schaden (21)"),
           ("life total reached 0", "Lebenspunkte auf 0"),
           ("10 poison counters", "Giftmarken (10)"),
           ("empty library", "Bibliothek leer (Mill)"),
           ("due to effect of spell", "Niederlage durch Karteneffekt"),
           ("conceded", "Aufgegeben")]


def parse_game(buf, winner_line, a_tag):
    """Wertet die Ausgabe eines Spiels aus (Forge druckt das Spielprotokoll in umgekehrter Reihenfolge)."""
    g = {"winner": None, "turn": None, "reason": None, "effect": None}
    if "ended in a Draw" in winner_line:
        g["winner"] = "draw"
    else:
        mt = re.search(r"ended in \d+ ms\. (.+) has won!", winner_line)
        if mt:
            g["winner"] = "a" if mt.group(1).startswith(a_tag) else "b"
    for line in buf:
        t = re.match(r"^\s*Turn (\d+)\s*$", line)
        if t and g["turn"] is None:
            g["turn"] = int(t.group(1))
        for key, label in REASONS:
            if key in line and g["reason"] is None:
                g["reason"] = label
                e = re.search(r"(?:effect of|by spell) (?:spell )?'+(.+?)'+\s*$", line)  # Kartenname kann ' enthalten
                g["effect"] = e.group(1) if e else None
    if "Stopping slow match as draw" in "\n".join(buf):
        g["reason"] = "Zeitlimit erreicht (als Unentschieden gewertet)"
    return g


def run_duel(job, cmd, cwd, a_tag):
    try:
        flags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW unter Windows
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace", creationflags=flags)
        job["pid"] = proc.pid
        buf = []
        for line in proc.stdout:
            line = line.rstrip("\n")
            job["tail"] = (job.get("tail", []) + [line])[-15:]
            if line.startswith("Game Result:"):
                job["games"].append(parse_game(buf, line, a_tag))
                buf = []
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
        job["done"] = True
        summarize(job)


def summarize(job):
    gs = job["games"]
    res = {"a": 0, "b": 0, "draw": 0, "turns": {"a": [], "b": []}, "reasons": {"a": {}, "b": {}}, "effects": {"a": {}, "b": {}}}
    for g in gs:
        w = g["winner"] or "draw"
        res[w] = res.get(w, 0) + 1
        if w in ("a", "b"):
            if g["turn"]:
                res["turns"][w].append(g["turn"])
            if g["reason"]:
                res["reasons"][w][g["reason"]] = res["reasons"][w].get(g["reason"], 0) + 1
            if g["effect"]:
                res["effects"][w][g["effect"]] = res["effects"][w].get(g["effect"], 0) + 1
    for k in ("a", "b"):
        t = res["turns"][k]
        res["turns"][k] = round(sum(t) / len(t), 1) if t else None
    job["summary"] = res


def duel_start(p):
    g = lambda k: (p.get(k) or [""])[0]
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
    n = max(1, min(int(g("games") or 10), 100))
    tmp = tempfile.mkdtemp(prefix="commander_duel_")
    clean = lambda x: re.sub(r"[^\w !.,+-]", "", x)[:60] or "Deck"
    write_dck(os.path.join(tmp, "A.dck"), "Mein Deck", mine_cmd, mine)
    write_dck(os.path.join(tmp, "B.dck"), ("Precon " if opp["kind"] == "precon" else "Gegner ") + clean(opp["name"]),
              opp["cmds"], opp["entries"])
    cmd = ([st["java"]] + FORGE_JVM + ["-jar", st["jar"], "sim", "-d", "A.dck", "B.dck", "-D", tmp,
                                     "-n", str(n), "-f", "Commander", "-c", str(int(g("timeout") or 300))])
    jid = hashlib.sha1(f"{tmp}{datetime.datetime.now()}".encode()).hexdigest()[:10]
    job = JOBS[jid] = {"id": jid, "total": n, "games": [], "done": False, "precon": opp["name"], "opp": opp["name"],
                       "opp_kind": opp["kind"], "dir": tmp}
    threading.Thread(target=run_duel, args=(job, cmd, st["dir"], "Ai(1)-"), daemon=True).start()
    return {"job": jid, "total": n}


def duel_status(p):
    job = JOBS.get((p.get("job") or [""])[0])
    if not job:
        return {"error": "Unbekannter Duell-Auftrag."}
    if not job["done"]:
        summarize(job)
    return {k: v for k, v in job.items() if k not in ("dir", "pid")}


PAGE = """<!doctype html><meta charset=utf-8><title>Commander-Datenbank</title>
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
#cmpbox{display:none}
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
<meta name=viewport content="width=device-width, initial-scale=1">
<link rel=stylesheet href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&display=swap">
<button type=button id=theme></button><button type=button id=helpbtn data-h=start>❓ Hilfe</button>
<div id=help><div><button type=button class=x id=helpx>✕ Schließen</button><h2 id=h-top>Hilfe zur Commander-Datenbank</h2>
<nav class=htoc><a data-h=start>Erste Schritte</a> · <a data-h=commander>Was ist Commander?</a> · <a data-h=bauen>Deck bauen</a> ·
<a data-h=anpassen>Deck anpassen</a> · <a data-h=import>Importieren &amp; Speichern</a> · <a data-h=export>Exportieren</a> ·
<a data-h=gegner>Gegner &amp; Vergleich</a> · <a data-h=combos>Combos</a> · <a data-h=duell>Duell mit Forge</a> ·
<a data-h=regeln>Regeln</a> · <a data-h=suche>Kartensuche</a> · <a data-h=update>Aktualisierung</a> · <a data-h=geraete>Handy &amp; andere Geräte</a> ·
<a data-h=begriffe>Begriffe</a> · <a data-h=probleme>Probleme lösen</a></nav>

<h3 id=h-start>Erste Schritte</h3>
<ol><li><b>Starten:</b> Doppelklick auf <code>Commander-DB starten.bat</code> (oder in der Eingabeaufforderung <code>python commander_db_v9.py serve</code>). Ein schwarzes Fenster öffnet sich – <b>dieses Fenster offen lassen</b>, solange du die Datenbank benutzt. Der Browser öffnet die Seite automatisch (sonst <code>http://localhost:8000</code> eingeben).</li>
<li><b>Beim Start</b> prüft das Programm im Hintergrund, ob es neue Regeln, Precons oder Kartendaten gibt. Den Fortschritt siehst du oben im Balken. Du kannst währenddessen schon arbeiten.</li>
<li><b>Ein erstes Deck:</b> oben bei „Commander“ einen Namen eintippen (z. B. „Atraxa“), Vorschlag anklicken und <b>Deck vorschlagen</b> drücken. Fertig – darunter erscheint ein vollständiges Deck mit 100 Karten.</li>
<li><b>Beenden:</b> das schwarze Fenster schließen (oder dort Strg+C drücken). Gespeicherte Decks bleiben erhalten.</li></ol>
<p>Überall auf der Seite findest du kleine <span class=qh>?</span>-Knöpfe. Ein Klick darauf öffnet die passende Stelle dieser Hilfe. Oben rechts lässt sich die Optik zwischen <b>Magic-Stil</b> und <b>neutral</b> umschalten.</p>

<h3 id=h-commander>Was ist Commander? (in einer Minute)</h3>
<ul><li>Jedes Deck hat <b>genau 100 Karten</b>, davon ist eine der <b>Commander</b> – meist eine legendäre Kreatur. Er liegt nicht im Stapel, sondern kann jederzeit aus der Kommandozone gespielt werden (jedes weitere Mal kostet er 2 Mana mehr).</li>
<li>Jede Karte darf nur <b>einmal</b> vorkommen – außer Standardländern wie Wald oder Insel.</li>
<li>Die <b>Farbidentität</b> des Commanders bestimmt, welche Farben im Deck erlaubt sind. Ein grün-blauer Commander erlaubt nur grüne, blaue und farblose Karten.</li>
<li>Jeder beginnt mit <b>40 Lebenspunkten</b>. Wer von einem einzelnen Commander insgesamt <b>21 Kampfschaden</b> erhält, verliert ebenfalls.</li>
<li><b>Precons</b> sind die fertigen, offiziell verkauften Commander-Decks – gut als Vergleichsmaßstab.</li>
<li><b>Brackets</b> (Stufen 1–5) beschreiben, wie stark ein Deck ist, damit am Tisch ähnlich starke Decks gegeneinander spielen.</li></ul>

<h3 id=h-bauen>Deck bauen lassen (Deckbau-Assistent)</h3>
<p>Alle Felder sind freiwillig – eine Angabe genügt.</p>
<ul><li><b>Commander:</b> beim Tippen erscheinen Vorschläge; Tippfehler werden toleriert. Die Farbidentität wird automatisch übernommen.</li>
<li><b>Thema:</b> z. B. Mill, Lifegain, Tokens, Voltron – das Deck wird um dieses Thema herum gebaut.</li>
<li><b>Farbidentität:</b> nur nötig, wenn du keinen Commander angibst (W = Weiß, U = Blau, B = Schwarz, R = Rot, G = Grün).</li>
<li><b>Karten, die ins Deck sollen:</b> eigene Lieblingskarten, eine pro Zeile. Mit dem Feld darüber und Enter fügst du sie bequem hinzu.</li>
<li><b>Keine Game Changer:</b> lässt besonders starke Karten weg – sinnvoll für entspannte Runden.</li>
<li><b>Nicht verfügbare Karten:</b> Karten, die du nicht besitzt oder nicht spielen willst. Sie werden nie vorgeschlagen; die Liste merkt sich der Browser.</li></ul>
<p>Die Vorschläge beruhen auf der allgemeinen Beliebtheit (EDHREC) – sie sind ein guter Startpunkt, aber kein Ersatz für eigenes Feintuning.</p>

<h3 id=h-anpassen>Deck ansehen und anpassen</h3>
<ul><li><b>Ansicht:</b> „Liste“ (kompakt, mit Preisen und Links) oder „Kartenbilder“.</li>
<li><b>⇄ Tauschen:</b> zeigt passende Alternativen mit derselben Aufgabe (z. B. anderes Ramp). Filter: keine Game Changer, Höchstpreis. Optional wird die alte Karte als „nicht verfügbar“ gemerkt.</li>
<li><b>Alle Game Changer ersetzen:</b> tauscht alle auf einmal gegen die beste Alternative.</li>
<li><b>Manakurve:</b> wie viele Karten welche Kosten haben. Viele günstige Karten = schnelles Deck.</li>
<li><b>Preise</b> stammen von Cardmarket (über Scryfall) und sind Richtwerte.</li></ul>

<h3 id=h-import>Importieren und Speichern</h3>
<ul><li><b>Speichern:</b> im umrahmten Feld „💾 Deck speichern“ direkt unter der Deck-Überschrift einen Namen eingeben und <b>Speichern</b> klicken. Gleicher Name = altes Deck wird überschrieben.</li>
<li><b>Gespeicherte Decks</b> findest du im aufklappbaren Bereich „Deck importieren &amp; gespeicherte Decks“ – mit den Knöpfen „Mein Deck“ (laden), „Gegner“ (als Gegner verwenden) und „Löschen“ (zweimal klicken).</li>
<li><b>Importieren:</b> eine Liste einfügen (z. B. aus Moxfield „Export“), eine Datei wählen (.txt, .dck, .dec, .csv, .json) oder einen Link angeben (Archidekt, MTGGoldfish, TappedOut, Deckstats; Moxfield blockiert Links oft – dann die Liste kopieren). Danach <b>Importieren</b>.</li>
<li>Die Vorschau zeigt, ob der Commander erkannt wurde, welche Karten nicht gefunden oder korrigiert wurden und ob etwas nicht zur Farbidentität passt. Den Commander kannst du dort ändern; Partner mit „ + “ trennen.</li></ul>

<h3 id=h-export>Exportieren und übertragen</h3>
<ul><li><b>→ Moxfield / → Archidekt:</b> die Liste wird in die Zwischenablage kopiert und die Seite geöffnet. Dort ein neues Deck anlegen, den Import öffnen und mit <b>Strg+V</b> einfügen. (Beide Seiten erlauben keinen direkten Upload durch andere Programme.)</li>
<li><b>Text kopieren:</b> passt für fast alle anderen Seiten und Apps.</li>
<li><b>Herunterladen:</b> als Textdatei, Forge-Deck (.dck) oder Tabelle (CSV).</li>
<li><b>In Forge-Deckordner speichern:</b> das Deck erscheint danach in Forge unter den Commander-Decks.</li></ul>

<h3 id=h-gegner>Gegner wählen und vergleichen</h3>
<ul><li>Gegner kann ein offizielles <b>Precon</b> sein (Suchfeld oder passende Vorschläge) oder ein <b>eigenes Deck</b> (Knöpfe „Eigene Decks als Gegner“ oder „Als Gegner verwenden“ beim Import).</li>
<li>Der <b>Vergleich</b> stellt Kennzahlen gegenüber: Ramp (Mana-Beschleunigung), Kartenvorteil, Entfernung, Massenentfernung, Länderzahl, Manawert, Game Changer, Tutoren, Kartenqualität. Grün markiert, wer vorne liegt. Das ist eine Papier-Analyse, keine Spielsimulation.</li>
<li><b>Ideen aus dem Gegnerdeck:</b> beliebte Karten, die dein Deck nicht hat und die zu deinen Farben passen.</li></ul>

<h3 id=h-combos>Combos</h3>
<p>Combos sind Kartenkombinationen, die zusammen etwas Außergewöhnliches bewirken – oft sofortigen Sieg. Die Daten kommen von Commander Spellbook. Für jede Combo siehst du, wie wahrscheinlich du alle Teile bis Zug 6, 8 oder 10 zusammen hast (berechnet aus 1.500 simulierten Starthänden, ohne Störung durch Gegner). Früh mögliche Siegcombos heben die Bracket-Einstufung an.</p>

<h3 id=h-duell>Direktes Duell mit Forge</h3>
<p>Forge ist ein kostenloses Programm, das Magic mit allen Regeln spielt. Hier spielen zwei Computer-Gegner deine beiden Decks komplett gegeneinander – inklusive Combos.</p>
<ol><li><b>Einmalig einrichten:</b> Java 17 oder neuer installieren (z. B. von adoptium.net) und Forge von github.com/Card-Forge/forge/releases installieren.</li>
<li>Im Duell-Bereich den <b>Forge-Ordner</b> eintragen – den Ordner, in dem die Datei <code>forge-gui-desktop-…-jar-with-dependencies.jar</code> liegt – und <b>Speichern</b>. Es sollte „Forge ist bereit.“ erscheinen.</li>
<li>Anzahl Partien wählen (10 ist ein guter Anfang) und <b>Duell starten</b>. Die erste Partie dauert etwas länger, weil Forge startet. Eine Partie dauert meist 0,5–3 Minuten.</li></ol>
<p><b>Ergebnis lesen:</b> Siege in Prozent, durchschnittlicher Siegzug, Siegart (z. B. Commander-Schaden, Combo) und welche Karte gewonnen hat. Die KI spielt solide, aber nicht perfekt – aussagekräftig sind Tendenzen über viele Partien. Läuft eine Partie zu lange, wird sie als Unentschieden gewertet.</p>

<h3 id=h-regeln>Offizielle Regeln</h3>
<p>Die vollständigen <b>Comprehensive Rules</b> von Wizards of the Coast (englisch), automatisch in der neuesten Fassung. Suche nach</p>
<ul><li>einer <b>Regelnummer</b>: <code>903</code> (alle Commander-Regeln), <code>903.4</code> (eine Regel mit Unterregeln), <code>5</code> (ein ganzes Kapitel),</li>
<li>oder <b>Wörtern</b> (englisch): z. B. <code>color identity</code>, <code>commander tax</code>, <code>trample</code>. Treffer im Glossar stehen oben.</li></ul>
<p>Verweise wie „rule 702.19“ im Text sind anklickbar. Die Schnellknöpfe springen zu häufig gebrauchten Abschnitten. Für Bannliste und Brackets gibt es Links zu den offiziellen Seiten.</p>

<h3 id=h-suche>Kartensuche</h3>
<p>Suche nach Name oder Regeltext, Kartentyp, Stichwort (z. B. Flying), Farbidentität und Manawert. „Als Commander nutzbar“ zeigt nur mögliche Commander. Ergebnisse sind nach Beliebtheit sortiert, mit Preisen und Links zu Scryfall und Cardmarket.</p>

<h3 id=h-update>Automatische Aktualisierung</h3>
<ul><li>Bei jedem Start wird geprüft: <b>Regeln</b> (neue Fassung bei Wizards?), <b>Precons</b> (neue Decklisten?) und <b>Kartendaten</b> (werden neu geladen, wenn sie älter als 7 Tage sind und Scryfall neuere hat).</li>
<li>Es wird nur heruntergeladen, wenn sich wirklich etwas geändert hat. Ohne Internet läuft alles mit den vorhandenen Daten weiter.</li>
<li>Mit <b>Jetzt aktualisieren</b> im Balken oben prüfst du sofort; <b>Alles neu laden</b> erzwingt einen frischen Download.</li>
<li>Gespeicherte Decks, Einstellungen und Forge-Ordner bleiben bei Aktualisierungen erhalten.</li></ul>

<h3 id=h-geraete>Handy, Tablet und andere Geräte</h3>
<ul><li><b>Im Heimnetz:</b> auf dem PC mit <code>Commander-DB im Netzwerk starten.bat</code> (oder <code>python commander_db_v9.py serve --lan</code>) starten. Im schwarzen Fenster erscheint eine Adresse wie <code>http://192.168.178.23:8000/?key=…</code> – diese im Browser von Handy oder Tablet öffnen (gleiches WLAN). Der Code im Link schützt vor fremdem Zugriff; danach merkt sich der Browser die Freigabe.</li>
<li>Windows fragt beim ersten Mal, ob Python im Netzwerk kommunizieren darf – für <b>private Netzwerke</b> erlauben.</li>
<li>Duelle laufen dabei auf dem PC; das Handy zeigt nur die Ergebnisse.</li>
<li><b>Mac und Linux:</b> das Skript läuft dort genauso (Python 3 installieren, dann <code>python3 commander_db_v9.py serve</code>).</li></ul>

<h3 id=h-begriffe>Begriffe</h3>
<dl><dt>Ramp</dt><dd>Karten, die zusätzliches Mana bringen (z. B. Sol Ring, Länder suchen).</dd>
<dt>Kartenvorteil (Draw)</dt><dd>Karten, mit denen du zusätzliche Karten ziehst.</dd>
<dt>Entfernung (Removal)</dt><dd>Karten, die eine gegnerische Karte zerstören oder verbannen.</dd>
<dt>Massenentfernung (Wipe)</dt><dd>Entfernt viele oder alle Kreaturen/bleibenden Karten auf einmal.</dd>
<dt>Tutor</dt><dd>Durchsucht die Bibliothek nach einer bestimmten Karte.</dd>
<dt>Game Changer</dt><dd>Offizielle Liste besonders spielstarker Karten; sie bestimmen mit, in welches Bracket ein Deck gehört.</dd>
<dt>Bracket</dt><dd>Offizielle Stärkestufe 1 (sehr locker) bis 5 (Turnierniveau, cEDH).</dd>
<dt>Precon</dt><dd>Fertig gekauftes, offizielles Commander-Deck.</dd>
<dt>Farbidentität</dt><dd>Alle Farbsymbole auf der Karte, auch im Regeltext – bestimmt die erlaubten Farben im Deck.</dd>
<dt>EDHREC-Rang</dt><dd>Wie oft eine Karte in Commander-Decks gespielt wird (kleiner = beliebter).</dd>
<dt>Mulligan</dt><dd>Neue Starthand ziehen, wenn die erste schlecht ist.</dd>
<dt>Combo</dt><dd>Karten, die zusammen eine besonders starke oder spielentscheidende Wirkung haben.</dd></dl>

<h3 id=h-probleme>Probleme lösen</h3>
<dl><dt>Die Seite lädt nicht / „Keine Verbindung zum Skript“</dt><dd>Das schwarze Fenster wurde geschlossen. Neu starten und die Seite neu laden (F5).</dd>
<dt>Eine Karte wird nicht gefunden</dt><dd>Englischen Kartennamen verwenden. Ganz neue Karten kommen mit der nächsten Kartendaten-Aktualisierung.</dd>
<dt>„Java ist zu alt“ / „Java nicht gefunden“</dt><dd>Java 17 oder neuer installieren und das Programm neu starten.</dd>
<dt>„Keine Datei forge-gui-desktop… gefunden“</dt><dd>Falscher Forge-Ordner. Im Explorer nach „forge-gui-desktop“ suchen und den Ordner der Datei eintragen.</dd>
<dt>Moxfield-Link funktioniert nicht</dt><dd>In Moxfield „Export“ → Liste kopieren und einfügen.</dd>
<dt>Combos „nicht erreichbar“</dt><dd>Keine Internetverbindung oder Commander Spellbook gerade nicht erreichbar – später erneut versuchen.</dd>
<dt>Aktualisierung „fehlgeschlagen“</dt><dd>Meist fehlt kurz das Internet. Die alten Daten bleiben nutzbar; später „Jetzt aktualisieren“ klicken.</dd></dl>
<p class=hint>Kartendaten: Scryfall · Precons: mtg.wtf/MTGJSON · Combos: Commander Spellbook · Regeln: Wizards of the Coast · Regel-Engine: Forge. Magic: The Gathering ist eine Marke von Wizards of the Coast; dieses Programm ist ein privates Fan-Werkzeug ohne Verbindung zu Wizards.</p>
</div></div>
<h2>Commander-Deckbau-Datenbank</h2>
<p class=info id=info></p>
<div id=upd class=updbar>Prüfe auf Aktualisierungen ...</div>
<h3>Deckbau-Assistent <button type=button class=qh data-h=bauen>?</button></h3>
<p class=hint>Alle Felder sind optional – eine Angabe genügt. Namen werden beim Tippen vorgeschlagen.</p>
<form id=b autocomplete=off>
<span class=ac><input name=commander id=cmd placeholder="Commander" size=30></span>
<input name=theme placeholder="Thema: Mill, Lifegain, Stompy ..." size=26 list=th>
<datalist id=th><option>Mill<option>Lifegain<option>Stompy<option>Tokens<option>Counters<option>Aristocrats<option>Spellslinger<option>Voltron</datalist>
<input name=ci id=ci placeholder="Farbidentität (z. B. WUB)" size=22>
<span class=hint id=cihint></span><br>
<span class=ac><input id=add placeholder="Karte hinzufügen (Enter)" size=30></span><br>
<textarea name=cards id=cards rows=4 cols=70 placeholder="Karten, die ins Deck sollen (eine pro Zeile, optional)"></textarea><br>
<label><input type=checkbox name=nogc id=nogc value=1>Keine Game Changer vorschlagen</label><br>
<details id=exbox><summary>Nicht verfügbare Karten (<span id=excount>0</span>) – werden nie vorgeschlagen</summary>
<span class=ac><input id=exadd placeholder="Karte hinzufügen (Enter)" size=30></span>
<button type=button id=exclear>Liste leeren</button><br>
<textarea name=exclude id=exclude rows=4 cols=70 placeholder="Eine Karte pro Zeile"></textarea></details>
<button class=primary>Deck vorschlagen</button></form>
<details id=impbox><summary><b>Deck importieren &amp; gespeicherte Decks</b> <span class=hint id=mycount></span> <button type=button class=qh data-h=import>?</button></summary>
<p class=hint>Liste einfügen (Moxfield, Archidekt, Arena, MTGO, TappedOut, Deckstats, Forge …), Datei wählen
(.txt, .dck, .dec, .csv, .json) oder Link angeben (Archidekt, Moxfield, MTGGoldfish, TappedOut, Deckstats).</p>
<textarea id=imptext rows=6 cols=70 placeholder="Deckliste einfügen, z. B. „1 Sol Ring“ je Zeile"></textarea><br>
<input type=file id=impfile accept=".txt,.dck,.dec,.csv,.json,.mwdeck"><br>
<input id=impurl size=60 placeholder="oder Link, z. B. https://archidekt.com/decks/123456">
<button type=button id=impgo class=primary>Importieren</button>
<div id=impres></div>
<h4>Gespeicherte Decks</h4><div id=mydecks></div></details>
<div id=dlg><div id=dlgin></div></div>
<p class=view>Ansicht: <button type=button data-v=list>Liste</button><button type=button data-v=img>Kartenbilder</button></p>
<div id=out></div>
<div id=cmpbox><hr><h3>Gegner wählen: Precon oder eigenes Deck <button type=button class=qh data-h=gegner>?</button></h3>
<p class=hint>Vergleicht die Deckwerte mit dem Gegnerdeck; darunter Combos und das Duell über Forge.</p>
<p id=oppinfo class=big></p>
<div class=chips id=oppdecks></div>
<div id=pmissing></div>
<span class=ac><input id=pq placeholder="Precon oder Commander suchen" size=36></span> <span class=hint>oder ein offizielles Precon:</span>
<div class=chips id=psugg></div>
<div id=cmp></div><div id=combos></div><div id=duel></div><div id=pview></div></div>
<hr>
<h3>Offizielle Regeln <button type=button class=qh data-h=regeln>?</button></h3>
<p class=hint id=rinfo></p>
<form id=rf autocomplete=off><input id=rq size=40 placeholder="Regelnummer (z. B. 903.4) oder Begriff (z. B. commander tax)">
<button class=primary>Suchen</button></form>
<p class=chips id=rquick></p>
<div id=rres></div>
<hr>
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
<script>
const $=(t,x,h)=>{const e=document.createElement(t);if(x!=null)e.textContent=x;if(h){e.href=h;e.target='_blank'}return e};
const J=async(u,body)=>{try{const r=await fetch(u,body?{method:'POST',body:new URLSearchParams(body)}:undefined);
 return await r.json()}catch(e){return {error:'Keine Verbindung zum Skript – läuft „serve“ noch? ('+e.message+')'}}};
const E=id=>document.getElementById(id);
const P=(o,x,cls)=>{const e=$('p',x);if(cls)e.className=cls;o.append(e);return e};
// Optik: Magic-Stil oder neutral (wird im Browser gemerkt)
let theme='mtg';try{theme=localStorage.getItem('theme')||'mtg'}catch(e){}
function setTheme(t){theme=t;document.body.classList.toggle('mtg',t=='mtg');
 E('theme').textContent=t=='mtg'?'Optik: Magic ✦ → neutral':'Optik: neutral → Magic ✦';try{localStorage.setItem('theme',t)}catch(e){}}
E('theme').onclick=()=>setTheme(theme=='mtg'?'neutral':'mtg');setTheme(theme);
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
 if(n!==undefined)cmd.value=n;
 const v=cmd.value.trim();
 if(!v){ci.readOnly=false;ci.value='';cih.textContent='';return}
 const d=await J('/api/card?commander=1&name='+encodeURIComponent(v));
 if(!d.name){ci.readOnly=false;cih.textContent='Commander nicht gefunden';return}
 cmd.value=d.name;ci.value=d.ci||'C';ci.readOnly=true;
 cih.textContent='aus Commander übernommen'+(d.can_be_commander?'':' – Achtung: kein gültiger Commander');
}
ac(cmd,{get:names(true),pick:setCommander});
cmd.addEventListener('change',()=>setCommander());
const add=E('add'),cards=E('cards');
const append=n=>{n=n.trim();if(!n)return;cards.value=(cards.value.trim()?cards.value.trim()+'\\n':'')+n;add.value=''};
ac(add,{get:names(false),pick:append,enter:()=>append(add.value)});
ac(E('q'),{get:names(false),pick:n=>{E('q').value=n;go()}});

// Karten als Liste oder als Bilder ausgeben
function swapBtn(gi,ci){const b=$('button','⇄ Tauschen');b.type='button';b.className='sw';
 b.onclick=e=>{e.preventDefault();e.stopPropagation();openSwap(gi,ci)};return b}
function cardsOut(o,groups,edit){
 groups.forEach((g,gi)=>{o.append($('h4',g.name+' ('+g.cards.reduce((s,c)=>s+c.qty,0)+')'));
  const canSwap=c=>edit&&g.name!='Commander'&&!c.basic;
  if(view=='img'){const gr=$('div');gr.className='grid';o.append(gr);
   g.cards.forEach((c,ci)=>{const a=c.image?$('a',null,c.scryfall):$('div',c.name);if(c.swapped)a.classList.add('swapped');
    if(c.image){a.title=c.name+(c.eur!=null?' · '+c.eur.toFixed(2)+' €':'');
     const im=$('img');im.src=c.image;im.loading='lazy';im.alt=c.name;a.append(im)}else a.className='ph';
    if(c.qty>1){const q=$('span','×'+c.qty);q.className='q';a.append(q)}
    if(c.gc){const s=$('span','Game Changer');s.className='g';a.append(s)}
    if(canSwap(c))a.append(swapBtn(gi,ci));
    gr.append(a)})}
  else g.cards.forEach((c,ci)=>{const r=$('div');r.append(c.qty+'x ');r.append(c.scryfall?$('a',c.name,c.scryfall):$('span',c.name));
   if(c.gc){const s=$('span',' GC');s.className='gc';r.append(s)}
   if(c.swapped){const s=$('span','getauscht');s.className='tag';r.append(s)}
   r.append(' ',manaEl(c.mana),(c.eur!=null?'  · '+c.eur.toFixed(2)+' €':''));
   if(c.cardmarket){r.append(' · ');r.append($('a','Cardmarket',c.cardmarket))}
   if(canSwap(c))r.append(swapBtn(gi,ci));
   o.append(r)})})
}
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
 const sb=$('button','Speichern');sb.type='button';sb.className='primary';const sm=$('span');sv.append(sn,sb,sm);
 sb.onclick=async()=>{sb.disabled=true;sm.className='hint';sm.textContent=' speichere ...';
  const r=await J('/api/deck_save',{name:sn.value,commander:d.commander||'',list:d.export});sb.disabled=false;
  if(r.error){sm.className='warn';sm.textContent=' '+r.error;return}
  d.name=r.name;sm.className='tag';sm.textContent=' ✓ Gespeichert als „'+r.name+'“ – zu finden unter „Deck importieren & gespeicherte Decks“.';
  myDecks(r.decks)};
 exportBox(h('div'),()=>({name:sn.value||d.name||'',commander:d.commander||'',list:d.export}));
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
 cardsOut(o,d.groups,true);
 h('h4','Textliste zum Kopieren');const t=h('textarea');t.rows=10;t.cols=50;t.value=d.export;
 E('cmpbox').style.display='block'}
async function bd(e){e.preventDefault();
 const p=new URLSearchParams(new FormData(E('b')));
 E('out').textContent='Deck wird zusammengestellt ...';
 deck=await J('/api/build?'+p);showDeck();
 E('cmp').innerHTML='';E('pview').innerHTML='';precon=null;afterDeck()}
function afterDeck(){loadPrecons();oppInfo();if(opp&&deck&&!deck.error)runCompare(opp);else{['combos','duel'].forEach(x=>E(x).innerHTML='')}}

// Precons: Auswahl, Vergleich, Ansicht
const plabel=p=>p.name+' – '+p.commander+' ('+p.set+', '+p.date.slice(0,4)+')';
async function loadPrecons(){
 const info=await J('/api/info'),m=E('pmissing');m.innerHTML='';
 if(!info.precons_at){m.append($('p','Die Precon-Decklisten sind noch nicht geladen (einmalig ca. 30 MB von GitHub).'));
  const b=$('button','Precon-Daten jetzt laden');b.type='button';m.append(b);
  b.onclick=async()=>{b.disabled=true;b.textContent='Lade ...';const r=await J('/api/load_precons',{});
   m.innerHTML='';m.append($('p',r.error||r.count+' Precons geladen.'));loadPrecons()};return}
 const s=E('psugg');s.innerHTML='';
 const list=await J('/api/precons?ci='+encodeURIComponent(deck.ci||''));
 if(list.length){s.append($('span','Passend zu deinen Farben: '))}
 list.slice(0,8).forEach(p=>{const b=$('button',p.name+' ('+p.ci+')');b.type='button';b.title=plabel(p);b.onclick=()=>setOpp({kind:'precon',id:p.id,name:p.name});s.append(b)})}
ac(E('pq'),{get:async v=>(await J('/api/precons?q='+encodeURIComponent(v))).map(p=>({t:plabel(p),v:p.id})),
 pick:(id,it)=>{E('pq').value=it.t;setOpp({kind:'precon',id:id,name:it.t})}});
const fmt=v=>v==null?'–':(typeof v=='number'&&!Number.isInteger(v)?v.toFixed(2):String(v));
const oppP=()=>opp.kind=='precon'?{precon:opp.id}:{opp_list:opp.list,opp_commander:opp.commander||'',opp_name:opp.name||''};
const mineP=()=>({list:deck.export,commander:deck.commander||'',ci:deck.ci||''});
function oppInfo(){E('oppinfo').textContent=opp?'Aktueller Gegner: '+(opp.kind=='precon'?'Precon ':'')+opp.name:'Noch kein Gegner gewählt.'}
function setOpp(o){opp=o;oppInfo();E('pview').innerHTML='';precon=null;
 if(deck&&!deck.error){runCompare(opp);E('cmpbox').scrollIntoView({behavior:'smooth'})}}
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
 out.append($('h4','Gemeinsame Karten ('+r.shared.length+')'));out.append($('p',r.shared.join(', ')||'keine'));
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
async function copyText(t){try{await navigator.clipboard.writeText(t);return true}catch(e){
 const ta=$('textarea');ta.value=t;document.body.append(ta);ta.select();let ok=false;try{ok=document.execCommand('copy')}catch(x){}ta.remove();return ok}}
function download(name,text){const a=$('a');a.href=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'}));
 a.download=name;document.body.append(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},500)}
function exportBox(o,get){const hh=$('h4','Exportieren & übertragen');hh.append(qBtn('export'));o.append(hh);
 const msg=$('p');msg.className='hint';
 const row=$('div');o.append(row,msg);
 for(const [k,[label,url,fmt,how]] of Object.entries(SITES)){const b=$('button','→ '+label);b.type='button';b.title='Liste kopieren und '+label+' öffnen';row.append(b);
  b.onclick=async()=>{const w=window.open(url,'_blank');const r=await J('/api/export',Object.assign(get(),{fmt}));
   if(r.error){msg.className='warn';msg.textContent=r.error;return}
   const ok=await copyText(r.text);msg.className='hint';
   msg.textContent=(ok?'Deckliste ist kopiert. ':'Kopieren nicht möglich – bitte die Datei unten herunterladen. ')+how+(w?'':' (Pop-up blockiert – bitte '+url+' selbst öffnen.)')}}
 const cp=$('button','Text kopieren');cp.type='button';row.append(cp);
 cp.onclick=async()=>{const r=await J('/api/export',Object.assign(get(),{fmt:'arena'}));
  msg.textContent=r.error||((await copyText(r.text))?'Deckliste (Arena-/Moxfield-Format) kopiert – passt für die meisten Seiten und Apps.':'Kopieren nicht möglich.')};
 const sel=$('select');[['arena','Datei: Moxfield/Arena (.txt)'],['archidekt','Datei: Archidekt (.txt)'],['text','Datei: einfache Liste (.txt)'],
  ['dck','Datei: Forge (.dck)'],['csv','Datei: CSV']].forEach(([v,t])=>{const op=$('option',t);op.value=v;sel.append(op)});
 const dl=$('button','Herunterladen');dl.type='button';row.append(' ',sel,dl);
 dl.onclick=async()=>{const r=await J('/api/export',Object.assign(get(),{fmt:sel.value}));
  if(r.error){msg.className='warn';msg.textContent=r.error;return}download(r.filename,r.text);msg.className='hint';msg.textContent='Datei „'+r.filename+'“ wird heruntergeladen.'};
 const fg=$('button','In Forge-Deckordner speichern');fg.type='button';row.append(' ',fg);
 fg.onclick=async()=>{const r=await J('/api/export',Object.assign(get(),{fmt:'forge'}));
  msg.className=r.error?'warn':'hint';msg.textContent=r.error||('Gespeichert: '+r.path+' – in Forge unter Commander-Decks auswählbar.')}}

// ---- Import und gespeicherte Decks
E('impfile').onchange=async()=>{const f=E('impfile').files[0];if(!f)return;
 E('imptext').value=await f.text();E('impfile').dataset.name=f.name;E('impurl').value=''};
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
 deck=await J('/api/deck_view',d);deck.name=d.name;showDeck();
 E('cmp').innerHTML='';E('pview').innerHTML='';precon=null;afterDeck();E('out').scrollIntoView({behavior:'smooth'})}
function useOpp(d,where){setOpp({kind:'deck',name:d.name||d.commander||'Gegnerdeck',list:d.list,commander:d.commander});
 if(!(deck&&!deck.error)&&where)P(where,'Als Gegner gesetzt – jetzt ein eigenes Deck vorschlagen oder laden.','hint')}
async function myDecks(list){list=list||await J('/api/decks');
 if(list.error){E('mydecks').textContent=list.error;return}
 E('mycount').textContent=list.length?'('+list.length+' gespeichert)':'';
 const o=E('mydecks');o.innerHTML='';const c=E('oppdecks');c.innerHTML='';
 if(!list.length){o.append($('p','Noch keine Decks gespeichert.'));return}
 c.append($('span','Eigene Decks als Gegner: '));
 const t=$('table');o.append(t);
 const hr=t.insertRow();['Deck','Commander','Karten','Gespeichert',''].forEach(x=>hr.append($('th',x)));
 for(const d of list){const tr=t.insertRow();[d.name,d.commander||'–',d.count,d.saved_at].forEach(x=>tr.insertCell().textContent=x);
  const a=tr.insertCell();const get=()=>J('/api/deck_get?id='+d.id);
  const b1=$('button','Mein Deck');b1.type='button';b1.onclick=async()=>useMine(await get());
  const b2=$('button','Gegner');b2.type='button';b2.onclick=async()=>useOpp(await get(),E('impres'));
  const b3=$('button','Löschen');b3.type='button';
  b3.onclick=async()=>{if(b3.textContent!='Wirklich?'){b3.textContent='Wirklich?';return}myDecks(await J('/api/deck_delete',{id:d.id}))};
  a.append(b1,b2,b3);
  const ch=$('button',d.name);ch.type='button';ch.title=d.commander||'';ch.onclick=async()=>useOpp(await get());c.append(ch)}}
myDecks();oppInfo();

// ---- Combos (Commander Spellbook)
function comboList(o,rep,title){const box=$('div');o.append(box);box.append($('h4',title));
 if(rep.error){P(box,rep.error,'warn');return}
 P(box,rep.count+' Combos gefunden, davon '+rep.win_count+' spielentscheidend · Bracket-Schätzung mit Combos: '+rep.bracket,'hint');
 if(!rep.combos.length)P(box,'Keine bekannten Combos im Deck.');
 for(const c of rep.combos.slice(0,25)){const d=$('div');d.className='combo'+(c.win?' win':'');box.append(d);
  const t=$('div');t.append($('b',c.cards.map(u=>u.name).join(' + ')));d.append(t);
  d.append($('div','Ergebnis: '+c.produces.join(', ')));
  if(c.requires.length)d.append($('div','Benötigt zusätzlich: '+c.requires.join(', ')));
  d.append($('div','Mana: '+(c.mana||'–')+(c.mana_value?' · Mana-Wert gesamt '+c.mana_value:'')+' · Einstufung (Spellbook): '+c.tag_name));
  const w=$('div');w.append('Zusammen bis Zug 6 / 8 / 10: '+c.by6+' % / '+c.by8+' % / '+c.by10+' % ');
  const b=$('span');b.className='bar';const i=$('i');i.style.width=(c.by10||0)+'%';b.append(i);w.append(b);d.append(w);
  if(c.prereq)P(d,'Voraussetzungen: '+c.prereq,'hint');
  const l=$('a','Ablauf bei Commander Spellbook',c.url);d.append(l)}}
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
async function duelBox(){const o=E('duel');o.innerHTML='';o.append(h3q('Direktes Duell (Regel-Engine Forge)','duell'));
 P(o,'Dein Deck gegen „'+opp.name+'“: Beide Decks spielen mehrere komplette Partien Commander 1-gegen-1 (40 Leben, Commander-Schaden, Commander-Steuer) – KI gegen KI. Jede Karte wird mit ihren echten Fähigkeiten ausgeführt, auch Combos.','hint');
 const st=await J('/api/forge');
 const cfg=$('div');o.append(cfg);
 const inp=$('input');inp.size=60;inp.placeholder='Forge-Ordner, z. B. C:\\Forge';inp.value=st.dir||'';cfg.append('Forge-Ordner: ',inp);
 const sv=$('button','Speichern');sv.type='button';cfg.append(sv);
 P(cfg,st.message,st.ready?'hint':'warn');
 if(!st.ready)P(cfg,'Einmalig nötig: Java 17+ (z. B. adoptium.net) und Forge (github.com/Card-Forge/forge/releases, Archiv entpacken). Dann hier den entpackten Ordner angeben.','hint');
 sv.onclick=async()=>{await J('/api/forge_dir',{dir:inp.value});duelBox()};
 if(!st.ready)return;
 const run=$('div');o.append(run);
 const n=$('input');n.size=4;n.value='10';run.append('Anzahl Partien: ',n,' ');
 const go=$('button','Duell starten');go.type='button';run.append(go);
 const res=$('div');o.append(res);
 go.onclick=async()=>{go.disabled=true;res.innerHTML='';
  const j=await J('/api/duel_start',Object.assign(mineP(),oppP(),{games:n.value}));
  if(j.error){P(res,j.error,'warn');go.disabled=false;return}
  const stop=$('button','Abbrechen');stop.type='button';run.append(stop);
  stop.onclick=()=>J('/api/duel_cancel',{job:j.job});
  clearInterval(duelTimer);
  const poll=async()=>{const s=await J('/api/duel_status?job='+j.job);showDuel(res,s);
   if(s.done){clearInterval(duelTimer);go.disabled=false;stop.remove()}};
  duelTimer=setInterval(poll,2500);poll()}}
function showDuel(o,s){o.innerHTML='';
 P(o,(s.done?'Fertig: ':'Läuft: ')+s.games.length+' von '+s.total+' Partien'+(s.done?'':' (der erste Start von Forge dauert etwa eine Minute)'),'big');
 if(s.error)P(o,s.error,'warn');
 const m=s.summary;if(!m||!s.games.length)return;
 const t=$('table');t.className='duel';o.append(t);
 const row=(...c)=>{const tr=t.insertRow();c.forEach(x=>tr.insertCell().textContent=x);return tr};
 const hr=t.insertRow();['','Dein Deck',(s.opp_kind=='precon'?'Precon ':'Gegner ')+s.opp].forEach(x=>hr.append($('th',x)));
 const tr=row('Siege',m.a+' ('+Math.round(m.a/s.games.length*100)+' %)',m.b+' ('+Math.round(m.b/s.games.length*100)+' %)');
 if(m.a>m.b){tr.cells[1].className='w'}else if(m.b>m.a){tr.cells[2].className='w'}
 row('Unentschieden / Zeitlimit',m.draw,m.draw);
 row('Ø Siegzug (eigene Züge)',m.turns.a??'–',m.turns.b??'–');
 const fmtR=r=>Object.entries(r).map(([k,v])=>k+': '+v).join(', ')||'–';
 row('Siegarten',fmtR(m.reasons.a),fmtR(m.reasons.b));
 row('Siege durch Karte',fmtR(m.effects.a),fmtR(m.effects.b));
 const gl=$('details');o.append(gl);gl.append($('summary','Einzelne Partien'));
 s.games.forEach((g,i)=>gl.append($('div','Partie '+(i+1)+': '+(g.winner=='a'?'Dein Deck':g.winner=='b'?'Gegner':'Unentschieden')+
  (g.turn?' in Zug '+g.turn:'')+(g.reason?' – '+g.reason:'')+(g.effect?' ('+g.effect+')':''))));
 P(o,'Hinweis: Die KI spielt solide, aber nicht perfekt – aussagekräftig sind Tendenzen über viele Partien.','hint')}

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
  if(!r.cards.length)P(list,'Keine passenden Alternativen gefunden – Filter lockern?');
  for(const a of r.cards){const row=$('div');row.className='alt';
   if(a.image){const im=$('img');im.src=a.image;im.loading='lazy';row.append(im)}
   const n=$('div');n.className='n';n.append(a.scryfall?$('a',a.name,a.scryfall):$('span',a.name));
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
 for(const c of d){const tr=b.insertRow(),n=tr.insertCell();n.append($('span',c.name));
  if(c.gc){const g=$('span',' GC');g.className='gc';n.append(g)}
  tr.insertCell().append(manaEl(c.mana));
  for(const v of [c.type,c.ci,c.rank??'',c.eur!=null?c.eur.toFixed(2):''])tr.insertCell().textContent=v;
  const l=tr.insertCell();l.append($('a','Scryfall',c.scryfall));
  if(c.cardmarket){l.append(' · ');l.append($('a','Cardmarket',c.cardmarket))}}}
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
 items.forEach(it=>{const sp=$('span',it.label+' – '+it.status);sp.className=it.ok===false?'no':it.ok?'ok':'';o.append(sp,' · ')});
 if(!s.running){const b=$('button','Jetzt aktualisieren');b.type='button';b.onclick=()=>startUpd(0);
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
 r.glossary.forEach(g=>{const d=$('div');d.className='glo';d.append($('b','Glossar: '+g.term),' – ');richText(d,g.text,words);o.append(d)});
 if(!r.rules.length&&!r.glossary.length)P(o,'Keine Treffer. Tipp: englische Begriffe verwenden, z. B. „trample“ oder „mulligan“.','hint');
 if(r.total>r.rules.length)P(o,r.total+' Treffer, angezeigt werden die ersten '+r.rules.length+' – Suche genauer eingrenzen.','hint');
 r.rules.forEach(x=>{const d=$('div');d.className='rule';const b=$('b',x.num);b.onclick=()=>{E('rq').value=x.num;rules(x.num)};
  d.append(b);richText(d,x.text,words);o.append(d)})}
E('rf').onsubmit=e=>{e.preventDefault();rules(E('rq').value.trim())};rules('');

E('b').onsubmit=bd;E('f').onsubmit=go;go();setView(view);
function infoLine(){J('/api/info').then(d=>{E('info').textContent=d.count+' Karten · Scryfall-Stand: '+d.source_date
 +(d.precons_at?' · Precons: '+d.precons_at:'')+(d.rules_version?' · Regeln gültig ab '+d.rules_version:'')})}
infoLine();
</script>"""


LAN_KEY = ""


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
        con = db()
        con.row_factory = sqlite3.Row
        try:
            if path == "/api/build":
                return build(p)
            if path == "/api/search":
                return search(p)
            if path == "/api/suggest":
                return find_names(con, g("q"), g("cmd") == "1")
            if path == "/api/card":
                r, _ = lookup(con, g("name"), g("commander") == "1")
                return {"name": r["name"], "ci": r["color_identity"], "can_be_commander": bool(r["can_be_commander"]),
                        "legal": bool(r["commander_legal"])} if r else {}
            if path == "/api/info":
                return {k: v for k, v in con.execute("SELECT key, value FROM meta")}
            if path == "/api/precons":
                return precon_list(con, g("q"), g("ci").upper()) if has_precons(con) else []
            if path == "/api/precon":
                return precon_view(p)
            if path == "/api/alternatives":
                return alternatives(p)
            if path == "/api/combos":
                return combos_for(p)
            if path == "/api/forge":
                return forge_status()
            if path == "/api/forge_dir":
                setting("forge_dir", g("dir").strip().strip('"'))
                return forge_status()
            if path == "/api/duel_start":
                return duel_start(p)
            if path == "/api/duel_status":
                return duel_status(p)
            if path == "/api/duel_cancel":
                j = JOBS.get(g("job"))
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
                return deck_list(con)
            if path == "/api/deck_save":
                return deck_save(p)
            if path == "/api/deck_get":
                return deck_get(con, int(g("id") or 0)) or {"error": "Deck nicht gefunden."}
            if path == "/api/deck_delete":
                decks_table(con)
                con.execute("DELETE FROM decks WHERE id = ?", (int(g("id") or 0),))
                con.commit()
                return deck_list(con)
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

    def answer(self, path, p):
        if LAN_KEY:
            ck = self.headers.get("Cookie") or ""
            ok = f"cdbkey={LAN_KEY}" in ck or (p.get("key") or [""])[0] == LAN_KEY
            if not ok:
                body = ("<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'>"
                        "<h3>Zugangscode fehlt</h3><p>Bitte den vollständigen Link aus dem Fenster auf dem PC öffnen "
                        "(er endet mit <code>?key=…</code>).</p>").encode()
                self.send_response(403); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
                self.wfile.write(body)
                return
        try:
            res = self.route(path, p)
        except Exception as e:
            res = {"error": f"Fehler: {e}"}
        if res is None:
            body, ct = PAGE.encode(), "text/html; charset=utf-8"
        else:
            body, ct = json.dumps(res).encode(), "application/json"
        self.send_response(200); self.send_header("Content-Type", ct)
        if LAN_KEY:
            self.send_header("Set-Cookie", f"cdbkey={LAN_KEY}; Max-Age=31536000; SameSite=Strict; Path=/")
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        self.answer(u.path, parse_qs(u.query))

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        self.answer(urlparse(self.path).path, parse_qs(self.rfile.read(n).decode("utf-8")))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["import", "precons", "serve", "update"])
    ap.add_argument("--no-update", action="store_true", help="beim Start nicht nach Updates suchen")
    ap.add_argument("--lan", action="store_true", help="auch für Handy/Tablet im Heimnetz erreichbar (mit Zugangscode)")
    ap.add_argument("--no-browser", action="store_true", help="Browser nicht automatisch öffnen")
    ap.add_argument("--file")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    if a.cmd == "import":
        do_import(a.file)
        try:
            do_precons()
        except Exception as e:
            print(f"Precons konnten nicht geladen werden ({e}) – später mit 'precons' nachholen.")
    elif a.cmd == "precons":
        do_precons(a.file)
    elif a.cmd == "update":
        upgrade_db()
        print("Prüfe auf Updates ...")
        auto_update(force=False)
    else:
        upgrade_db()
        try:
            db().execute("PRAGMA journal_mode=WAL")  # Lesen und Schreiben gleichzeitig möglich
        except Exception:
            pass
        if not a.no_update:
            print("Prüfe im Hintergrund auf neue Regeln, Precons und Kartendaten ...")
            threading.Thread(target=auto_update, daemon=True).start()
        host = "127.0.0.1"
        if a.lan:
            LAN_KEY = setting("lan_key") or setting("lan_key", hashlib.sha1(os.urandom(16)).hexdigest()[:12])
            host = "0.0.0.0"
            print("\nZugriff von Handy/Tablet im selben WLAN – diesen Link dort öffnen:")
            print(f"    http://{lan_ip()}:{a.port}/?key={LAN_KEY}\n")
            print("(Windows fragt eventuell nach einer Firewall-Freigabe: für private Netzwerke erlauben.)")
        try:
            srv = ThreadingHTTPServer((host, a.port), H)
        except OSError:
            sys.exit(f"Port {a.port} ist belegt – läuft die Datenbank schon in einem anderen Fenster? "
                     f"Sonst mit --port 8001 starten.")
        print(f"Läuft auf http://localhost:{a.port}  (dieses Fenster offen lassen; Beenden mit Strg+C)")
        if not a.no_browser:
            import webbrowser
            threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{a.port}/" + (f"?key={LAN_KEY}" if LAN_KEY else ""))).start()
        srv.serve_forever()
