# Commander-DB – Android-App

Die App zeigt die Oberfläche deines Commander-DB-Servers (gleiche Inhalte wie im Browser) und ergänzt
Android-Funktionen: Exporte werden unter **Downloads/Commander-DB** gespeichert, „Text kopieren“ nutzt die
Zwischenablage, Decklisten lassen sich als Datei importieren, externe Links (Scryfall, Moxfield …) öffnen im Browser.

Beim ersten Start fragt die App nach der Serveradresse (z. B. `https://commander.deine-domain.de`).
Ändern lässt sie sich später über den Link **„Server ändern“** oben auf der Seite.

## Kartenscanner in der App
Ab Version 29 hat die App einen eingebauten Kartenscanner: im Tab **Sammlung** auf **„📷 Karten scannen“** und dann
**„📱 Mit der Handykamera scannen“** tippen. Die Kamera-App des Handys öffnet sich; nach dem Foto erkennt
**Google ML Kit** den Text direkt auf dem Gerät (ohne Internet, kostenlos, keine Kamera-Berechtigung nötig), die
Commander-DB ordnet den Kartennamen zu. Das Modell wird beim Bauen in die APK eingebunden (APK rund 10 MB größer).
### Dauerscan (ab Version 30)
**„🔁 Dauerscan mit der Handykamera“** öffnet eine eigene Kameraansicht mit Kartenrahmen. Karten einfach nacheinander
in den Rahmen legen – jede sicher erkannte Karte wird mit Ton und Vibration gezählt (sie muss zweimal hintereinander
gleich gelesen werden). Dieselbe Karte zählt erst wieder, nachdem sie aus dem Bild war; für mehrere gleiche Karten
gibt es **„+1“**. **„✓ Fertig“** (oder die Zurück-Taste) übernimmt alles in die Scanliste der Webseite.
Beim ersten Start fragt Android nach der Kameraberechtigung. Die Texterkennung läuft auf dem Handy, der Abgleich
des Kartennamens über den Server (Internet bzw. WLAN zum Server nötig).

Ohne APK (Variante A, Browser) funktioniert der Scanner ebenfalls – dann über „Foto aufnehmen“ mit der Texterkennung
im Browser.

## Variante A – ohne APK: als Web-App installieren (empfohlen, keine Bauschritte)
1. Auf dem Android-Gerät in **Chrome** die Serveradresse öffnen und anmelden.
2. Auf **„📲 Als App installieren“** tippen (oder Menü ⋮ → „App installieren“ / „Zum Startbildschirm hinzufügen“).
3. Die App erscheint im App-Menü und öffnet sich im eigenen Fenster. Updates kommen automatisch vom Server.

## Variante B – APK automatisch bei GitHub bauen lassen (ohne Android Studio)
1. Kostenloses Konto auf github.com anlegen, ein neues (privates) Repository erstellen.
2. Den kompletten Inhalt dieses Pakets hochladen (Ordner `android` und `.github` müssen dabei sein).
3. Im Repository auf **Actions** → **Android-App bauen** → **Run workflow** klicken.
4. Nach ca. 5 Minuten beim fertigen Lauf unter **Artifacts** „Manaschmiede-APK“ herunterladen und entpacken.
5. `app-debug.apk` aufs Handy kopieren und öffnen (Installation aus „unbekannten Quellen“ einmalig erlauben).

## Variante C – mit Android Studio
Ordner `android` in Android Studio öffnen → **Build → Build App Bundle(s) / APK(s) → Build APK(s)**.

## Optional: signierte Release-Version (z. B. für den Play Store)
Schlüssel erzeugen: `keytool -genkeypair -v -keystore release.jks -alias commanderdb -keyalg RSA -keysize 2048 -validity 10000`
Dann in GitHub unter *Settings → Secrets and variables → Actions* anlegen:
`CDB_KEYSTORE_BASE64` (Inhalt von `base64 release.jks`), `CDB_KEYSTORE_PASSWORD`, `CDB_KEY_ALIAS`, `CDB_KEY_PASSWORD`.
Der Workflow baut dann zusätzlich `app-release.apk`. Den Schlüssel gut aufbewahren – ohne ihn sind keine Updates möglich.
