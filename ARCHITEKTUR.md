# Architektur des Planners

Kurzer Lageplan für alle, die am Planner arbeiten (Mensch oder KI). Ergänzt `CLAUDE.md` (Arbeitsregeln) und `planner/DOCS.md` (Bedienung).

## Überblick

```
iPhone / iPad / Mac ──► Home Assistant (Ingress, Anmeldung) ──► Add-on „Planner“ (planner/server.py, Port 8099)
Echo Show (?anzeige) ─┘                                         │  /data/tasks.json, settings.json, prefs.json, ai_usage.json
                                                                │  /share/planner/ (Spiegel + Sicherungen)
                                                                ├─► Home Assistant: Sensoren, Mitteilungen, Alexa (REST + WebSocket)
                                                                └─► Google Gemini (nur für KI-Vorschläge, Schlüssel bleibt im Add-on)
Claude-Artifact (artifact/planner.html) ─► Claude-Datenbank (window.claude.use)   ← zweite, unabhängige Version
```

## Dateien

| Datei | Rolle | Von Hand ändern? |
|---|---|---|
| `src/seite.html` | HTML-Gerüst: Kopf, Seitenleiste, Dialoge. Platzhalter für CSS und JavaScript | ja |
| `src/style.css` | alle Stile | ja |
| `src/js/*.js` | JavaScript, nach Dateinamen aneinandergehängt (siehe unten) | ja |
| `artifact/planner.html` | Claude-Version, von `tools/build.py` erzeugt, wird als Artifact veröffentlicht | **nein** |
| `planner/index.html`, `planner/VERSION` | Add-on-Oberfläche, von `tools/build.py` erzeugt | **nein** |
| `planner/server.py` | Server (nur Python-Standardbibliothek): Daten, Prüfung, Sicherungen, Home Assistant, Alexa, KI | ja |
| `planner/vendor/` | PDF-/Excel-Bibliothek und Schriften fürs Add-on, von `tools/vendor.py` (GitHub-Lauf „Fremdcode holen“) | **nein** |
| `planner/config.yaml` | Add-on-Beschreibung für Home Assistant, **Versionsnummer** | ja |
| `planner/CHANGELOG.md`, `planner/DOCS.md` | Änderungen und Anleitung, in Home Assistant sichtbar | ja |
| `tools/build.py` | Setzt beide Versionen zusammen, prüft Vertrag, JS-Syntax und Fremdcode-Prüfsummen | ja |
| `tools/check.py`, `tools/release.py` | alle Prüfungen in einem Lauf; neue Version setzen, bauen, prüfen | ja |
| `tools/test_server.py`, `tools/test_ha.py`, `tools/test_browser.py` + `tools/e2e/` | Tests | ja |
| `tools/css_audit.py`, `tools/style_diff.py` | totes CSS finden; Aussehen vorher/nachher vergleichen | ja |

## Die zwei Versionen und der Build

Die Oberfläche existiert nur einmal (`src/`). `tools/build.py` setzt `src/seite.html`, `src/style.css` und `src/js/*.js` zusammen. Unterschiede zwischen Claude-Version und Add-on stehen in Dateipaaren:

| Paar | Claude (`.claude.js`) | Add-on (`.addon.js`) |
|---|---|---|
| `10-speicher` | Claude-Datenbank (`window.claude.use("db")`), sonst Browser-Speicher | Server über `api/…`, Abgleich alle 5 s, persönliche Einstellungen je HA-Benutzer, KI über den Server |
| `95-download` | Claude-Downloads | Teilen-Menü auf dem iPhone, sonst Download |

Zusätzlich bekommt das Add-on: Angaben für „Zum Home-Bildschirm“, die Fehlermeldung an `api/log` und lokale Bibliotheken/Schriften (Zeile `const LIB=` in `40-darstellung.js`).

**Vertrag** (prüft `build.py` bei jedem Lauf):
- Zu jeder `.claude.js` gibt es eine `.addon.js` und umgekehrt.
- Was die Claude-Variante auf oberster Ebene definiert, definiert auch die Add-on-Variante (Ausnahmen in `ARTIFACT_ONLY`).
- Jede Funktion, die eine Add-on-Variante aufruft, existiert in der fertigen Seite.
- Beide Seiten bestehen `node --check`; das Add-on enthält keinen Claude-Code und lädt nichts aus dem Internet.

Gemeinsame Schnittstelle von `10-speicher`: `prefGet`, `prefSet`, `USER`, `init`, `saveTask`, `delTask`, `saveReg`, `saveMany`, `aiAvail`, `aiJson`.

## JavaScript in `src/js/`

Alle Dateien bilden **ein** Skript (keine Module): Namen sind überall sichtbar, Funktionsdeklarationen gelten in der ganzen Seite. Die Nummer bestimmt die Reihenfolge.

| Datei | Inhalt |
|---|---|
| `00-grundlagen.js` | Zustand (`RAW`, `tasks`, `reg`, Filter), Datums- und Hilfsfunktionen |
| `10-speicher.*.js` | Laden und Speichern (siehe oben) |
| `20-schnelleingabe.js` | Parser `parseQuick` (gleiche Regeln wie `parse_quick` im Server), Datumserkennung |
| `30-start-zeitstrahl.js` | Startseite-Hilfen, Wiederholung, Balken im Zeitstrahl ziehen |
| `40-darstellung.js` | Hell/Dunkel, Farbwelten, Schriften, Fremdcode-Adressen `LIB` |
| `50-einstellungen.js` | Archiv, Papierkorb, Einstellungen (persönlich / für alle) |
| `60-auswahl-gesten.js` | Mehrfachauswahl, Gedrückt halten, kein Text-Markieren, Tastatur |
| `70-verlauf-dateien-ki.js` | Verlauf und Kommentare, Fotos/Dateien, Kalender, KI-Assistent |
| `80-tags.js` | Tags, Tag-Symbole, Tag-Auswahl, Tags verwalten |
| `85-ansichten.js` | `render()`, Startseite, Board, Liste, Zeitstrahl, Echo-Ansicht |
| `90-aufgabenblatt.js` | Aufgabenblatt: Personen, Zeitraum, Checkliste, Abhängigkeiten mit Suche |
| `93-ios.js` | iOS-Verhalten: Aktionsblatt, Kontextmenü, Wischen, Ziehen zum Aktualisieren, ⋯-Menü |
| `95-download.*.js`, `96-export.js` | Export (PDF, Excel, Backup, Import) |
| `99-start.js` | Ereignisse verbinden, `init()` |

## CSS in `src/style.css`

Grundgerüst, dann Schichten je Version (`/* 1.2: … */` bis `/* 1.32: … */`). Spätere Schichten überschreiben frühere. Neue Regeln kommen ans Ende, mit Versionskommentar. Farben nur über Variablen (`--acc`, `--grp`, Status `--sky`, `--sun`, `--sea`, `--brick`). Aufräumen nur mit `tools/css_audit.py` und Absicherung durch `tools/style_diff.py`.

## Server (`planner/server.py`)

- `ThreadingHTTPServer`; eine Sperre `LOCK` (wiedereintrittsfähig) schützt `tasks.json`.
- **Datenformat**: `{"schema": 2, "rev": n, "tags": [...], "tasks": [...]}`. Jede Aufgabe läuft beim Speichern durch `clean()` (Pflichtfelder, Längen, Datumsprüfung). Felder: `id title tags proj ms rec spawned who status prio start end notes deps checklist arch del delAt log files v`. `v` zählt Änderungen je Aufgabe; mit Kopfzeile `X-Check: 1` lehnt der Server veraltete Stände ab (409).
- **Sicherungen**: täglich und monatlich unter `/data/backups` und `/share/planner/`.
- **Schnittstellen**: `GET api/tasks` · `POST api/task`, `api/import`, `api/tags` · `DELETE api/task/<id>` · Dateien `api/file/…` · `api/me` (persönliche Einstellungen) · `api/quick`, `api/voice`, `api/speech` (Siri, Assist, Alexa) · `api/ai` · `api/ha-settings`, `api/ha-test`, `api/ha-notify` · `api/log` (Fehler aus dem Browser).
- **Hintergrund**: `ha_loop` (Sensoren, tägliche Erinnerung), `ws_loop` (WebSocket zu Home Assistant: Abhaken-Knöpfe aus Mitteilungen, Alexa-Sprachbefehle).

## Sicherheit

- Zugriff normalerweise nur über Home Assistant (Ingress, mit Anmeldung). Port 8099 ist optional und hat **keine** Anmeldung: nur im Heimnetz, nie ins Internet weiterleiten.
- Host-Header-Prüfung gegen DNS-Rebinding (`host_ok`), Schreibzugriffe nur mit `X-Planner: 1`.
- Benutzerkennung (`X-Remote-User-*`) wird nur von der Ingress-Adresse 172.30.32.2 geglaubt.
- Der Gemini-Schlüssel wird nie an den Browser ausgeliefert; KI-Nutzung ist pro Tag und Stunde begrenzt.
- Das Repository ist öffentlich: keine Daten aus `/data` oder `/share` einchecken, keine Schlüssel in Tests.

## Tests

| Befehl | Prüft | Dauer |
|---|---|---|
| `python3 tools/build.py --check` | erzeugte Dateien aktuell, Vertrag, JS-Syntax, Fremdcode-Prüfsummen | ~7 s |
| `python3 tools/test_server.py` | Datenprüfung, Schreibschutz, Host-Prüfung, KI-Limits, Schnelleingabe, Benutzer | ~2 s |
| `python3 tools/test_ha.py` | Erinnerung je Person, Abhaken aus der Mitteilung, Alexa (mit nachgebautem Home Assistant) | ~17 s |
| `python3 tools/test_browser.py` | Oberfläche in Chromium auf Handy, iPad, Desktop (Gesten, Blätter, Schnelleingabe, KI, Benutzer, Export, Echo-Ansicht, Claude-Version) | ~1 min |
| `python3 tools/style_diff.py save/compare` | berechnete Stile in 115 Zuständen vorher/nachher (für CSS-Umbauten) | ~4 min |
| `python3 tools/check.py` | alles oben | ~1,5 min |

Nicht abgedeckt (nur auf echten Geräten prüfbar, siehe `PRUEFLISTE.md`): Safari/WKWebView auf dem iPhone, echte Mitteilungen, echte Alexa-Spracherkennung, echtes Gemini.

## Wenn du X änderst, prüfe Y

| Änderung | Mögliche Auswirkung | Prüfen |
|---|---|---|
| CSS-Regel ändern oder entfernen | Spätere Schichten überschreiben frühere; dieselbe Klasse wird an mehreren Stellen gestaltet | `tools/style_diff.py` vorher/nachher; gewollte Änderungen mit Bildschirmfotos prüfen (`SHOT_DIR=… tools/test_browser.py`) |
| `.claude.js`-Datei | Add-on weicht ab | `build.py` meldet fehlende Namen; `.addon.js` nachziehen |
| Schnelleingabe (JS `parseQuick`) | Siri/Alexa erkennen anders als die App | `test_browser.py schnell` vergleicht beide Parser |
| `clean()` oder Datenformat | Bestehende Aufgaben könnten Felder verlieren | Nur ergänzen, nie Felder entfernen; `test_server.py` |
| Erinnerung, Alexa, WebSocket | Mitteilungen an falsche Person, doppelte Sprachbefehle | `test_ha.py` |
| Neue Schnittstelle im Server | Schreibschutz vergessen | `X-Planner`-Prüfung gilt für alle POST/DELETE in `guard()`; Test ergänzen |
| Persönliche Einstellung (neuer Schlüssel) | Wird nicht je Benutzer gespeichert | In `PREF_KEYS` (Server) und `PK` (`src/js/10-speicher.addon.js`) eintragen |
| Bibliothek oder Schrift | Add-on lädt sie lokal | Adresse in `tools/vendor.py` und `LIB` ändern, GitHub-Lauf „Fremdcode holen“ |
