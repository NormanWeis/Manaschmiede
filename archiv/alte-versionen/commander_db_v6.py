#!/usr/bin/env python3
"""Commander-Datenbank auf Basis der Scryfall-Bulk-Daten (SQLite + lokale Suche).

  python commander_db_v6.py import            # lädt "Oracle Cards" von Scryfall + Precons, baut cards.db
  python commander_db_v6.py import --file x.json   # statt Download eine lokale JSON-Datei nutzen
  python commander_db_v6.py precons           # nur die Precon-Decklisten (neu) laden
  python commander_db_v6.py serve             # Oberfläche unter http://localhost:8000
Nur Python-Standardbibliothek, keine Installation nötig.

Version 2: Namensvorschläge beim Tippen und Tippfehler-Toleranz, Farbidentität wird aus dem
Commander übernommen, alle Eingaben optional, Preise als Zahl, Importdatum, Grist-Fix.
Version 3: Deckansicht mit Kartenbildern, Vergleich mit offiziellen Commander-Precons
(Decklisten: github.com/taw/magic-preconstructed-decks-data, auch Grundlage von mtg.wtf/MTGJSON).
Version 4: Karten gezielt tauschen oder entfernen (mit Alternativen gleicher Aufgabe), Option ohne
Game Changer, Liste nicht verfügbarer Karten, bessere Ramp-Erkennung.
Version 6: findet das neueste installierte Java automatisch (auch wenn Java 8 im PATH vorne steht).
Version 5: Combos beider Decks (Commander Spellbook) mit Wahrscheinlichkeit je Zug und Bracket-Regel,
direktes Duell beider Decks über die Regel-Engine Forge (KI gegen KI, Commander 1-gegen-1).
Eine mit Version 1 gebaute cards.db wird beim ersten 'serve' automatisch umgestellt.
"""
import argparse, datetime, difflib, gzip, hashlib, json, os, random, re, shutil, sqlite3, subprocess, sys, tempfile, threading, urllib.request
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
    rows = [to_row(c) for c in data if c.get("layout") not in SKIP_LAYOUTS]
    con = sqlite3.connect(DB)
    con.executescript("DROP TABLE IF EXISTS cards;" + SCHEMA)
    con.executemany("INSERT OR REPLACE INTO cards VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    now = datetime.datetime.now().isoformat(sep=" ", timespec="minutes")
    con.executemany("INSERT OR REPLACE INTO meta VALUES(?,?)",
                    [("imported_at", now), ("source_date", source_date or "unbekannt"), ("count", str(len(rows)))])
    con.commit()
    print(f"{len(rows)} Karten in {DB} gespeichert.")


def upgrade_db():
    """Bringt eine mit der alten Skriptversion gebaute cards.db auf den neuen Stand (einmalig, ohne Download)."""
    con = sqlite3.connect(DB)
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
    con = sqlite3.connect(DB)
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
    con = sqlite3.connect(DB)
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
    con = sqlite3.connect(DB)
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


def do_precons(path=None):
    """Lädt alle offiziellen Commander-Precons (Datenquelle: mtg.wtf / MTGJSON, ca. 30 MB)."""
    if path:
        raw = open(path, "rb").read()
    else:
        print("Lade Precon-Decklisten (ca. 30 MB) ...")
        raw = fetch(PRECON_URL)
    data = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    con = sqlite3.connect(DB)
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
    con.executescript("""DROP TABLE IF EXISTS precons; DROP TABLE IF EXISTS precon_cards;
      CREATE TABLE precons(id INTEGER PRIMARY KEY, name TEXT, set_name TEXT, release_date TEXT, commander TEXT, color_identity TEXT);
      CREATE TABLE precon_cards(precon_id INTEGER, name TEXT, qty INTEGER, is_commander INTEGER);
      CREATE INDEX idx_pc ON precon_cards(precon_id);""")
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


def entries_from_list(con, text, commander=""):
    """Textliste („1 Sol Ring“ je Zeile) -> [(Kartenzeile, Anzahl)]; der Commander zählt genau einmal."""
    rows, qty, missing = {}, {}, []
    cmd = lookup(con, commander, True)[0] if commander else None
    if cmd:
        rows[cmd["name"]], qty[cmd["name"]] = cmd, 1
    for line in text.splitlines():
        mt = re.match(r"^\s*(?:(\d+)\s*x?\s+)?(.+?)\s*$", line)
        if not mt:
            continue
        r = lookup(con, mt.group(2))[0]
        if not r:
            missing.append(mt.group(2))
        elif cmd and r["name"] == cmd["name"]:
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
    con = sqlite3.connect(DB)
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
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    if not has_precons(con):
        return {"error": "Precon-Daten fehlen – bitte zuerst laden."}
    pr = con.execute("SELECT * FROM precons WHERE id = ?", (int(g("precon") or 0),)).fetchone()
    if not pr:
        return {"error": "Bitte ein Precon auswählen."}
    mine, miss_a = entries_from_list(con, g("list"), g("commander").strip())
    if not mine:
        return {"error": "Kein eigenes Deck zum Vergleichen – bitte zuerst ein Deck vorschlagen lassen."}
    theirs, miss_b = precon_entries(con, pr["id"])
    a, b = analyze(mine), analyze([(r, q) for r, q, _ in theirs])
    rows, sa, sb = duel(a, b)
    na, nb = {r["name"] for r, _ in mine}, {r["name"]: r for r, _, _ in theirs}
    basic = lambda r: front_type(r).startswith("Basic")
    shared = sorted(n for n in na & set(nb) if not basic(nb[n]))
    ideas = sorted((r for n, r in nb.items() if n not in na and "Land" not in front_type(r) and r["edhrec_rank"]
                    and all(c in (g("ci") or ORDER) for c in r["color_identity"])),
                   key=lambda r: r["edhrec_rank"])[:12]
    if sa > sb:
        verdict = f"Dein Deck liegt in {sa} von {len(DUEL)} Kategorien vorn – auf dem Papier stärker als „{pr['name']}“."
    elif sb > sa:
        verdict = f"„{pr['name']}“ liegt in {sb} von {len(DUEL)} Kategorien vorn – dein Deck hat dort Nachholbedarf."
    else:
        verdict = f"Ausgeglichen: beide Decks gewinnen gleich viele Kategorien ({sa}:{sb})."
    if a["bracket"] != b["bracket"]:
        verdict += f" Achtung: unterschiedliche Bracket-Schätzung ({a['bracket']} gegen {b['bracket']})."
    return {"precon": {"id": pr["id"], "name": pr["name"], "set": pr["set_name"], "commander": pr["commander"]},
            "rows": rows, "score": [sa, sb], "verdict": verdict, "a": a, "b": b,
            "shared": shared, "ideas": [card_dict(r) for r in ideas], "missing": miss_a + miss_b}


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
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    mine, _ = entries_from_list(con, g("list"), g("commander").strip())
    out = {"mine": combo_report(con, mine, {g("commander").strip()} if g("commander").strip() else set())}
    if g("precon") and has_precons(con):
        theirs, _ = precon_entries(con, int(g("precon")))
        cmds = {r["name"] for r, q, ic in theirs if ic}
        out["theirs"] = combo_report(con, [(r, q) for r, q, _ in theirs], cmds)
    for k, rep in list(out.items()):  # Bracket-Schätzung mit Combo-Regel nachschärfen
        if rep.get("combos") is not None:
            ent = mine if k == "mine" else [(r, q) for r, q, _ in theirs]
            base = analyze(ent)["bracket"]
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
    con = sqlite3.connect(DB)
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
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cmd_name = g("commander").strip()
    mine, missing = entries_from_list(con, g("list"), cmd_name)
    pr = con.execute("SELECT * FROM precons WHERE id = ?", (int(g("precon") or 0),)).fetchone() if has_precons(con) else None
    if not mine or not pr:
        return {"error": "Bitte zuerst ein Deck vorschlagen und ein Precon wählen."}
    theirs, _ = precon_entries(con, pr["id"])
    mine_cmd = [r for r, _ in mine if r["name"] == cmd_name]
    if not mine_cmd:
        return {"error": "Für das Duell braucht dein Deck einen Commander."}
    n = max(1, min(int(g("games") or 10), 100))
    tmp = tempfile.mkdtemp(prefix="commander_duel_")
    write_dck(os.path.join(tmp, "A.dck"), "Mein Deck", mine_cmd, mine)
    write_dck(os.path.join(tmp, "B.dck"), "Precon " + re.sub(r"[^\w !.,-]", "", pr["name"]),
              [r for r, q, ic in theirs if ic], [(r, q) for r, q, ic in theirs])
    cmd = ([st["java"]] + FORGE_JVM + ["-jar", st["jar"], "sim", "-d", "A.dck", "B.dck", "-D", tmp,
                                     "-n", str(n), "-f", "Commander", "-c", str(int(g("timeout") or 300))])
    jid = hashlib.sha1(f"{tmp}{datetime.datetime.now()}".encode()).hexdigest()[:10]
    job = JOBS[jid] = {"id": jid, "total": n, "games": [], "done": False, "precon": pr["name"], "dir": tmp}
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
.bar>i{display:block;height:8px;background:#c0362c}</style>
<h2>Commander-Deckbau-Datenbank</h2>
<p class=info id=info></p>
<h3>Deckbau-Assistent</h3>
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
<button>Deck vorschlagen</button></form>
<div id=dlg><div id=dlgin></div></div>
<p class=view>Ansicht: <button type=button data-v=list>Liste</button><button type=button data-v=img>Kartenbilder</button></p>
<div id=out></div>
<div id=cmpbox><hr><h3>Gegen Precon antreten</h3>
<p class=hint>Vergleicht die Deckwerte mit einem offiziellen Commander-Precon (keine Spielsimulation).</p>
<div id=pmissing></div>
<span class=ac><input id=pq placeholder="Precon oder Commander suchen" size=36></span>
<div class=chips id=psugg></div>
<div id=cmp></div><div id=combos></div><div id=duel></div><div id=pview></div></div>
<hr>
<h3>Kartensuche</h3>
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
const J=async(u,body)=>(await fetch(u,body?{method:'POST',body:new URLSearchParams(body)}:undefined)).json();
const E=id=>document.getElementById(id);
const P=(o,x,cls)=>{const e=$('p',x);if(cls)e.className=cls;o.append(e);return e};
let view=localStorage.getItem('view')||'list',deck=null,precon=null;

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
   r.append(' '+c.mana+(c.eur!=null?'  · '+c.eur.toFixed(2)+' €':''));
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
 h('h3','Deckvorschlag'+(d.commander?' für '+d.commander:''));
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
 E('cmp').innerHTML='';E('pview').innerHTML='';precon=null;lastPrecon=null;loadPrecons()}

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
 list.slice(0,8).forEach(p=>{const b=$('button',p.name+' ('+p.ci+')');b.type='button';b.title=plabel(p);b.onclick=()=>runCompare(p.id);s.append(b)})}
ac(E('pq'),{get:async v=>(await J('/api/precons?q='+encodeURIComponent(v))).map(p=>({t:plabel(p),v:p.id})),
 pick:(id,it)=>{E('pq').value=it.t;runCompare(id)}});
const fmt=v=>v==null?'–':(typeof v=='number'&&!Number.isInteger(v)?v.toFixed(2):String(v));
let lastPrecon=null;
async function runCompare(id){lastPrecon=id;
 const o=E('cmp');o.textContent='Vergleiche ...';
 const r=await J('/api/compare',{precon:id,list:deck.export,commander:deck.commander||'',ci:deck.ci||''});
 o.innerHTML='';if(r.error){o.append($('p',r.error));return}
 o.append($('h3','Dein Deck gegen „'+r.precon.name+'“ ('+r.precon.commander+')'));
 P(o,'Ergebnis '+r.score[0]+' : '+r.score[1],'big');
 o.append($('p',r.verdict));
 const t=$('table');t.className='duel';o.append(t);
 const hr=t.insertRow();['Kategorie','Dein Deck','Precon','Hinweis'].forEach(x=>hr.append($('th',x)));
 const extra=[['Bracket-Schätzung','bracket'],['Kartenpreis gesamt (€)','price'],['Extra-Züge','extra'],['Massen-Landzerstörung','mld']];
 for(const x of r.rows){const tr=t.insertRow();tr.insertCell().textContent=x.label;
  const a=tr.insertCell(),b=tr.insertCell();a.textContent=fmt(x.a);b.textContent=fmt(x.b);
  if(x.win>0){a.className='w';b.className='l'}else if(x.win<0){b.className='w';a.className='l'}
  tr.insertCell().textContent=x.hint}
 for(const [l,k] of extra){const tr=t.insertRow();tr.insertCell().textContent=l;
  tr.insertCell().textContent=fmt(r.a[k]);tr.insertCell().textContent=fmt(r.b[k]);tr.insertCell().textContent=k=='price'?'nur Info':''}
 P(o,'Bracket-Schätzung nach Game Changern, Extra-Zügen und Landzerstörung; Kombos werden nicht erkannt.','hint');
 o.append($('h4','Gemeinsame Karten ('+r.shared.length+')'));o.append($('p',r.shared.join(', ')||'keine'));
 if(r.ideas.length){const d=$('div');o.append(d);cardsOut(d,[{name:'Ideen aus dem Precon (beliebt, nicht in deinem Deck)',cards:r.ideas}])}
 if(r.missing.length)P(o,'Nicht gefunden: '+r.missing.join(', '),'hint');
 const vb=$('button','Precon-Deckliste anzeigen');vb.type='button';o.append(vb);
 loadCombos(id);duelBox(id);
 vb.onclick=async()=>{precon=await J('/api/precon?id='+id);showPrecon()}}
function showPrecon(){const o=E('pview');o.innerHTML='';const p=precon;
 if(p.error){o.append($('p',p.error));return}
 o.append($('h3','Precon: '+p.name+' ('+p.set+', '+p.date+')'));cardsOut(o,p.groups);
 o.append($('h4','Textliste'));const t=$('textarea');t.rows=8;t.cols=50;t.value=p.export;o.append(t)}

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
async function loadCombos(id){const o=E('combos');o.innerHTML='';o.append($('h3','Combos im Vergleich'));
 P(o,'Suche Combos bei Commander Spellbook ...','hint');
 const r=await J('/api/combos',{precon:id,list:deck.export,commander:deck.commander||''});
 o.innerHTML='';o.append($('h3','Combos im Vergleich'));
 P(o,'Quelle: Commander Spellbook. Wahrscheinlichkeiten: Simulation von 1500 Starthänden je Deck (London-Mulligan, ein Land pro Zug, Ramp und Tutoren berücksichtigt, ohne Störung durch den Gegner).','hint');
 const cols=$('div');cols.className='cols';o.append(cols);
 comboList(cols,r.mine,'Dein Deck');if(r.theirs)comboList(cols,r.theirs,'Precon')}

// ---- Direktes Duell über Forge
let duelTimer=null;
async function duelBox(id){const o=E('duel');o.innerHTML='';o.append($('h3','Direktes Duell (Regel-Engine Forge)'));
 P(o,'Beide Decks spielen mehrere komplette Partien Commander 1-gegen-1 (40 Leben, Commander-Schaden, Commander-Steuer) – KI gegen KI. Jede Karte wird mit ihren echten Fähigkeiten ausgeführt, auch Combos.','hint');
 const st=await J('/api/forge');
 const cfg=$('div');o.append(cfg);
 const inp=$('input');inp.size=60;inp.placeholder='Forge-Ordner, z. B. C:\\Forge';inp.value=st.dir||'';cfg.append('Forge-Ordner: ',inp);
 const sv=$('button','Speichern');sv.type='button';cfg.append(sv);
 P(cfg,st.message,st.ready?'hint':'warn');
 if(!st.ready)P(cfg,'Einmalig nötig: Java 17+ (z. B. adoptium.net) und Forge (github.com/Card-Forge/forge/releases, Archiv entpacken). Dann hier den entpackten Ordner angeben.','hint');
 sv.onclick=async()=>{await J('/api/forge_dir',{dir:inp.value});duelBox(id)};
 if(!st.ready)return;
 const run=$('div');o.append(run);
 const n=$('input');n.size=4;n.value='10';run.append('Anzahl Partien: ',n,' ');
 const go=$('button','Duell starten');go.type='button';run.append(go);
 const res=$('div');o.append(res);
 go.onclick=async()=>{go.disabled=true;res.innerHTML='';
  const j=await J('/api/duel_start',{precon:id,list:deck.export,commander:deck.commander||'',games:n.value});
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
 const hr=t.insertRow();['','Dein Deck','Precon '+s.precon].forEach(x=>hr.append($('th',x)));
 const tr=row('Siege',m.a+' ('+Math.round(m.a/s.games.length*100)+' %)',m.b+' ('+Math.round(m.b/s.games.length*100)+' %)');
 if(m.a>m.b){tr.cells[1].className='w'}else if(m.b>m.a){tr.cells[2].className='w'}
 row('Unentschieden / Zeitlimit',m.draw,m.draw);
 row('Ø Siegzug (eigene Züge)',m.turns.a??'–',m.turns.b??'–');
 const fmtR=r=>Object.entries(r).map(([k,v])=>k+': '+v).join(', ')||'–';
 row('Siegarten',fmtR(m.reasons.a),fmtR(m.reasons.b));
 row('Siege durch Karte',fmtR(m.effects.a),fmtR(m.effects.b));
 const gl=$('details');o.append(gl);gl.append($('summary','Einzelne Partien'));
 s.games.forEach((g,i)=>gl.append($('div','Partie '+(i+1)+': '+(g.winner=='a'?'Dein Deck':g.winner=='b'?'Precon':'Unentschieden')+
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
 showDeck();if(lastPrecon)runCompare(lastPrecon)}
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
   n.append(' '+a.mana+(a.eur!=null?' · '+a.eur.toFixed(2)+' €':' · ohne Preis'));
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
  for(const v of [c.mana,c.type,c.ci,c.rank??'',c.eur!=null?c.eur.toFixed(2):''])tr.insertCell().textContent=v;
  const l=tr.insertCell();l.append($('a','Scryfall',c.scryfall));
  if(c.cardmarket){l.append(' · ');l.append($('a','Cardmarket',c.cardmarket))}}}
E('b').onsubmit=bd;E('f').onsubmit=go;go();setView(view);
J('/api/info').then(d=>{E('info').textContent=d.count+' Karten · importiert: '+d.imported_at+' · Scryfall-Stand: '+d.source_date
 +(d.precons_at?' · Precons geladen: '+d.precons_at:'')})
</script>"""


class H(BaseHTTPRequestHandler):
    def route(self, path, p):
        g = lambda k: (p.get(k) or [""])[0].strip()
        con = sqlite3.connect(DB)
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
            if path == "/api/load_precons":
                return {"count": do_precons()}
            return None
        finally:
            con.close()

    def answer(self, path, p):
        try:
            res = self.route(path, p)
        except Exception as e:
            res = {"error": f"Fehler: {e}"}
        if res is None:
            body, ct = PAGE.encode(), "text/html; charset=utf-8"
        else:
            body, ct = json.dumps(res).encode(), "application/json"
        self.send_response(200); self.send_header("Content-Type", ct); self.end_headers(); self.wfile.write(body)

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
    ap.add_argument("cmd", choices=["import", "precons", "serve"])
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
    else:
        upgrade_db()
        print(f"Läuft auf http://localhost:{a.port}  (Beenden mit Strg+C)")
        ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
