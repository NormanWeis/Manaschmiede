# Manaschmiede als Android-App

Die App zeigt die Oberfläche deines Manaschmiede-Servers, also dieselben Inhalte wie im Browser, und ergänzt
Android-Funktionen: Exporte landen unter Downloads/Commander-DB, „Text kopieren“ nutzt die Zwischenablage,
Decklisten lassen sich als Datei importieren, und externe Links (Scryfall, Moxfield …) öffnen im Browser.

Beim ersten Start fragt die App nach der Serveradresse (z. B. `https://commander.deine-domain.de`).
Später lässt sie sich über den Link „Server ändern“ oben auf der Seite ändern.

## Kartenscanner in der App
Seit Version 29 hat die App einen eingebauten Kartenscanner: im Tab Sammlung „📷 Karten scannen“ und dann
„📱 Mit der Handykamera scannen“ tippen. Die Kamera-App des Handys öffnet sich. Nach dem Foto liest Google ML Kit
den Text direkt auf dem Gerät (ohne Internet, kostenlos, ohne Kamera-Berechtigung), und die Manaschmiede ordnet
den Kartennamen zu. Das Modell wird beim Bauen in die APK eingebunden, die dadurch rund 10 MB größer ist.

### Dauerscan (seit Version 30)
„🔁 Dauerscan mit der Handykamera“ öffnet eine eigene Kameraansicht mit Kartenrahmen. Du legst die Karten
nacheinander in den Rahmen. Jede sicher erkannte Karte wird mit Ton und Vibration gezählt; dafür muss sie zweimal
hintereinander gleich gelesen werden. Dieselbe Karte zählt erst wieder, nachdem sie aus dem Bild war; für mehrere
gleiche Karten gibt es „+1“. „✓ Fertig“ oder die Zurück-Taste übernimmt alles in die Scanliste der Webseite.
Beim ersten Start fragt Android nach der Kameraberechtigung. Die Texterkennung läuft auf dem Handy, den
Kartennamen gleicht der Server ab (Internet bzw. WLAN zum Server nötig).

Ohne APK (Variante A, Browser) funktioniert der Scanner auch, dann über „Foto aufnehmen“ mit der Texterkennung im Browser.

## Variante A: ohne APK als Web-App installieren (empfohlen, ohne Bauschritte)
1. Auf dem Android-Gerät in Chrome die Serveradresse öffnen und anmelden.
2. „📲 Als App installieren“ tippen (oder Menü ⋮ → „App installieren“ bzw. „Zum Startbildschirm hinzufügen“).
3. Die App erscheint im App-Menü und öffnet sich im eigenen Fenster. Updates kommen automatisch vom Server.

## Variante B: APK automatisch bei GitHub bauen lassen (ohne Android Studio)
1. Ein kostenloses Konto auf github.com anlegen und ein neues (privates) Repository erstellen.
2. Den kompletten Inhalt dieses Pakets hochladen; die Ordner `android` und `.github` müssen dabei sein.
3. Im Repository Actions → „Android-App bauen“ → Run workflow anklicken.
4. Nach etwa 5 Minuten beim fertigen Lauf unter Artifacts „Manaschmiede-APK“ herunterladen und entpacken.
5. `app-debug.apk` aufs Handy kopieren und öffnen (Installation aus „unbekannten Quellen“ einmalig erlauben).

## Variante C: mit Android Studio
Den Ordner `android` in Android Studio öffnen und Build → Build App Bundle(s) / APK(s) → Build APK(s) wählen.

## Optional: signierte Release-Version (z. B. für den Play Store)
Schlüssel erzeugen: `keytool -genkeypair -v -keystore release.jks -alias commanderdb -keyalg RSA -keysize 2048 -validity 10000`
Dann in GitHub unter Settings → Secrets and variables → Actions anlegen:
`CDB_KEYSTORE_BASE64` (Inhalt von `base64 release.jks`), `CDB_KEYSTORE_PASSWORD`, `CDB_KEY_ALIAS`, `CDB_KEY_PASSWORD`.
Der Workflow baut dann zusätzlich `app-release.apk`. Bewahre den Schlüssel gut auf, denn ohne ihn sind keine Updates möglich.
