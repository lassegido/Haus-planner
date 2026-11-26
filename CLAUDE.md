# Arbeitsanweisung für Claude: Planner

Haus-Aufgaben-Tool von Lasse und Melanie (Kanban, Liste, Gantt). Sprache der Oberfläche und aller Texte: natürliches Deutsch, so formuliert, wie man es auf Deutsch sagen würde (Satzbau und Wortwahl nicht aus dem Englischen übertragen, keine englischen Begriffe, wenn es ein gängiges deutsches Wort gibt: Sicherung statt Backup). Ausnahmen: Eigennamen (GIPHY, Gemini), gewollte Jugendsprache in den Sprüchen, „Board“ (ausdrücklicher Wunsch, ab 1.42 statt „Tafel“) und der Stempel „BUSTED!“. Lasse bevorzugt Kennzahlen zuerst, kompakte visuelle Signale, kurze Antworten.

## Zwei Versionen, eine Quelle

- **Quellen:** `src/seite.html` (HTML-Gerüst), `src/style.css` (alle Stile), `src/js/*.js` (JavaScript, nach Dateinamen aneinandergehängt, ein gemeinsames Skript). Änderungen am Aussehen oder Verhalten macht man **nur hier**. Dateien mit `.claude.js` gelten nur für die Claude-Version (Claude-Datenbank, Downloads), ihr Gegenstück `.addon.js` nur für das Add-on (Server).
- **Erzeugt, nie von Hand ändern:** `artifact/planner.html` (Claude-Version) sowie `planner/index.html` und `planner/VERSION` (Add-on), alle von `tools/build.py`.
- Beide Versionen müssen nach jeder Änderung aktualisiert werden: Add-on über Git, Claude-Link über das Artifact-Tool (Artifact "Planner" per `list` finden und `artifact/planner.html` auf dessen URL veröffentlichen).

## Ablauf bei jeder Änderung

Lageplan, Datenformat und „Wenn du X änderst, prüfe Y“: siehe `ARCHITEKTUR.md`.

1. **Vorher Folgen benennen:** Dem Nutzer kurz sagen, was die Änderung berühren kann (Ansichten, Daten, Erinnerungen, Alexa, Claude-Version) und wie riskant sie ist. Tabelle in `ARCHITEKTUR.md` nutzen.
2. Quellen in `src/` bearbeiten. Serverseitige Änderungen in `planner/server.py`.
3. **Test dazu schreiben oder anpassen**, bevor die Änderung als fertig gilt: Oberfläche in `tools/e2e/test_*.py`, Server in `tools/test_server.py`, Home Assistant/Alexa in `tools/test_ha.py`. Kein Prüfskript nur im Notizordner.
4. Eintrag oben in `planner/CHANGELOG.md` (`## <neue Version>`).
5. `python3 tools/release.py <neue Version>` (z. B. 1.32.0 → 1.32.1; neue Funktion: 1.33.0). Setzt die Nummer in `config.yaml`, baut und führt `tools/check.py` aus. Ohne neue Version zeigt Home Assistant kein Update an.
6. Committen und pushen (`src/`, `planner/`, `tools/`). Der GitHub-Prüflauf (`.github/workflows/check.yml`) wiederholt alle Prüfungen.
7. Claude-Artifact mit `artifact/planner.html` aktualisieren.
8. Dem Nutzer sagen: was neu ist, Folgen je Änderung, was nur im Test-Browser und was nicht auf echten Geräten geprüft wurde (`PRUEFLISTE.md`).

Zwischendurch: `python3 tools/build.py` (erzeugt Add-on-Version, prüft Vertrag und JS-Syntax), `python3 tools/test_browser.py <Teil des Namens>` für einzelne Browser-Tests, `SHOT_DIR=/tmp/shots` für Bildschirmfotos.

## Harte Regeln

- **Datenhaltung nicht verändern, ohne Rücksicht auf bestehende Daten.** Echte Aufgaben liegen im Add-on unter `/data/tasks.json` und gespiegelt unter `/share/planner/`. Änderungen am Datenformat nur abwärtskompatibel (alte Dateien müssen lesbar bleiben, `clean()` in `server.py` ergänzen statt Felder zu entfernen).
- Nie Daten aus `/data` oder `/share` ins Repository einchecken. Das Repository ist öffentlich.
- Name überall **Planner**. Ordner, Slug und Sensor-IDs heißen `planner`. Der alte Slug war `haus_planer`; dessen Spiegel `/share/haus_planer/` übernimmt der Server beim ersten Start einmalig. Das GitHub-Repository heißt `lassegido/planner` (die alte Adresse `Haus-planner` leitet GitHub weiter; in Home Assistant eingetragene alte URL funktioniert deshalb weiter).
- `slug` in `config.yaml` (`planner`) nicht mehr ändern, sonst ist es für Home Assistant ein neues Add-on mit leerem Datenordner. Die Browser-Einstellungen heißen weiterhin `haus-*` (localStorage), damit gespeicherte Einstellungen nicht verloren gehen.
- Oberfläche muss auf Handy, iPad (hochkant und quer) und Desktop funktionieren. Keine festen Pixelbreiten für das Layout, Schriftgrößen relativ.
- Home-Assistant-Add-on: Ingress, deshalb in `index.html` nur **relative** Pfade (`api/tasks`, nicht `/api/tasks`).
- Dem Nutzer nach jedem Update sagen: Version in HA unter *Add-on-Store → ⋮ → Nach Updates suchen* → *Aktualisieren*; ehrlich benennen, was nur im Test-Browser und nicht auf echten Geräten geprüft wurde.

## Gestaltungskonzept (ab 1.27, verbindlich)

Grundlage: Apple Human Interface Guidelines (Farbe, Dark Mode), WCAG 2.2 (Kontrast), NN/g (wenige Farben, feste Bedeutung).

- **iOS-Muster:** Große Überschrift, darunter eine Zeile Zusammenfassung. Rechts höchstens drei runde Knöpfe: Suche, Filter (mit Zähler), ⋯-Menü. Sortieren, Gruppieren, Auswählen, Tags, Archiv, Export und Einstellungen liegen im ⋯-Menü, nicht als Leiste. Nie zweizeilige Bedienleisten.
- **Blätter:** Kopfzeile Abbrechen · Titel · Fertig/Speichern (oben, nicht unten), gruppierte Felder auf `--grp`, Löschen als rote Zeile ganz unten. Nach unten wischen schließt.
- **Listen auf dem Handy:** gruppierte iOS-Liste (`.igrp`), Ring links, Titel, eine Metazeile, Fälligkeit rechts. Wischen rechts = erledigt, links = Papierkorb.
- **Nicht geschafft (ab 1.42):** kein eigener Status, sondern `status:"done"` + `fail:true` (`isFail`, `isOk`, `stName` in `00-grundlagen.js`). Gilt überall als abgeschlossen, zählt aber nie als erledigt (Ring, Prozent, Abzeichen, Woche) und macht den Tag für die Serie nicht voll. Neue Zählungen mit `isOk` statt `status==="done"`, Nenner ohne `isFail`.
- **Farbe:** Pro Farbwelt genau eine Akzentfarbe (`--acc`) für Bedienelemente. Statusfarben sind fest und in jeder Farbwelt gleich: Offen = Himmelblau, In Arbeit = Orange, Erledigt = Meerblau, Überfällig = Ziegelrot. Status nie nur über Farbe zeigen (Ring, Halbkreis, Haken). Keine Akzentfarbe, die wie ein Status aussieht (darum keine rote Akzentfarbe).
- **Startseite darf verspielt sein, alles andere nicht:** Reihenfolge der Startseite: Tageskarte (Begrüßung, Ring, Serie, Woche, Meme) → Eingabe → Umschalter + Liste → nächstes Abzeichen → Überblick zugeklappt. Nichts darf sich beim Öffnen vor die Seite legen; groß nur auf Antippen oder beim Feiern. Eine Botschaft pro Karte: immer motivierend, nie Scheitern-Memes (`GIF_BAD`). Einzige gewollte Ausnahme: „BUSTED!“ (`busted()`), nur wenn man selbst auf der Startseite „Nicht geschafft“ wählt, verschwindet von selbst; über dem GIF steht ein motivierender Satz, der den Grund nur andeutet (keine Frage, keine Erklärung „weil …“). Liste, Board, Zeitstrahl, Kalender bleiben sachlich (keine Sprüche, GIFs, Konfetti). Der Schalter „Sprüche, GIFs und Konfetti“ (`funOn`) schaltet alle drei ab. Höchstens ein GIF pro Tag, Gemini für Sprüche höchstens einmal am Tag.
- **Anpassung nur kuratiert:** Darstellung (Automatisch/Hell/Dunkel), Farbwelt (Portofino, Polarlicht, Wald, Lagune, Orchidee, Feige, Schiefer; frühere Salbei/Beere/Graphit werden über `DES_OLD` umgestellt), Schrift (Figtree, Systemschrift, Fraunces + Figtree). Keine freien Farbwähler. Neue Farbwelten nur mit Hell- und Dunkel-Werten (alle Einträge aus `DK`, auch `--acc2` für den Verlauf und `--acc3` als Ring-Ende), im Stil von Polarlicht (getönte Flächen, kräftige Leiste, sichtbarer Verlauf), keine rote, orange oder gelbe Akzentfarbe und nach Kontrastprüfung: Text ≥ 4,5 : 1 auf `--bg` und `--grp`, Platzhalter ≥ 3 : 1, Akzent als Textknopf ≥ 4,5 : 1, Knopftext auf `--acc` und `--acc2` ≥ 4,5 : 1. `tools/e2e/test_farbwelten.py` prüft das automatisch.
- **Tiefe (ab 1.40):** Flächen bekommen Tiefe nur über die Werte aus der 1.40-Schicht am Ende von `style.css`: `--sh1` (liegt auf), `--sh2` (schwebt, z. B. beim Darüberfahren), `--hi` (Lichtkante oben), `--surf-grad` (hauchdünner Flächenverlauf), `--acc-grad` (Akzent → `--acc2`). Verläufe nur auf Akzentflächen (Ring, Hauptknopf, Neu-Knopf, Leiste), nie auf Text oder Statusfarben. Bei `background:` als Kurzform an Karten/Spalten in Dunkel-Regeln stattdessen `background-color` nehmen, sonst verschwindet der Verlauf.
- **Bedienbarkeit:** Tippflächen ≥ 44 pt (2,85 rem), Eingabefelder ≥ 16 px Schrift (sonst zoomt iOS), Tastatur nur bei neuen Aufgaben automatisch öffnen.
- **Tempo:** Karten und Zeilen mit `content-visibility:auto`; Touch-Handler auf `document` passiv lassen.
- **Sicherheit:** Server prüft Host-Header (Schutz vor DNS-Rebinding), Schreibzugriffe brauchen `X-Planner: 1`, KI-Schlüssel wird nie an den Browser ausgeliefert. `tools/check.py` muss grün sein.

## Wartbarkeit (ab 1.32)

- **Tempo bremsen:** Neue Funktionen nur mit Test. Vor großen Umbauten erst auf echten Geräten prüfen lassen (`PRUEFLISTE.md`).
- **CSS:** Neue Regeln ans Ende von `src/style.css` mit Versionskommentar; bestehende Klassen nicht an einer weiteren Stelle erneut gestalten, sondern die vorhandene Regel ändern. Kein `!important` ohne Kommentar, warum. `python3 tools/css_audit.py` findet tote und überschriebene Regeln; jede CSS-Aufräumung mit `tools/style_diff.py` (vorher `save`, nachher `compare`) absichern.
- **Fremdcode:** Bibliotheken und Schriften liegen im Add-on (`planner/vendor/`), nicht im Internet. Die Claude-Version lädt sie weiter vom CDN.
- **Fehler sichtbar machen:** Skriptfehler im Browser schickt das Add-on an `api/log`; sie stehen im Add-on-Protokoll in Home Assistant.
