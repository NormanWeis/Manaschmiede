# Englische Sprachfassung (Wörterbuch)

Die Manaschmiede ist auf Deutsch geschrieben. Die englische Fassung entsteht so:

- **Feste Seiten** (Hauptseite, Hilfe, „Neu hier?“, Anmeldung, Spielabend, Impressum, Datenschutz) übersetzt der
  Server vor dem Senden: ganze Textblöcke (`tsv/hb*.tsv`, `tsv/sb.tsv`), einzelne Texte und Attribute.
- **Texte aus dem Programm** (Meldungen, Knöpfe, Dialoge) übersetzt `/i18n.js` im Browser mit demselben Wörterbuch:
  erst genaue Treffer, dann Muster (`rx.tsv`, z. B. für Sätze mit Zahlen oder Kartennamen), dann bekannte Teilstücke.

Dateien:

| Datei | Inhalt |
|---|---|
| `tsv/u*.tsv`, `tsv/x*.tsv` | `Deutsch<TAB>Englisch`, ein Text je Zeile |
| `tsv/py.tsv` | Nummer aus `pieces_v0.json` (Abschnitt `py`) `<TAB>` Englisch |
| `tsv/hb*.tsv`, `tsv/sb.tsv` | Nummer aus `hblocks_v0.json` bzw. `blocks_v0.json` `<TAB>` englischer HTML-Block |
| `rx.tsv` | regulärer Ausdruck `<TAB>` Ersatz mit `$1`, `$2` |
| `fixes.tsv` | Korrekturen am deutschen Text, die auf die Schlüssel angewendet werden |

Neue oder geänderte Texte: Zeile in einer `tsv/x*.tsv` ergänzen (Blöcke mit `B:` vor dem deutschen Text), dann

```
python3 build_dict.py                      # erzeugt en.json
python3 embed.py ../windows/commander_db_vNN.py   # schreibt das Wörterbuch in das Programm (I18N_Z)
```
