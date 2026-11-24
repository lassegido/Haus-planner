# Architektur des Planners

Kurzer Lageplan für alle, die am Planner arbeiten (Mensch oder KI). Ergänzt `CLAUDE.md` (Arbeitsregeln) und `planner/DOCS.md` (Bedienung).

## Überblick

```
iPhone / iPad / Mac ──► Home Assistant (Ingress, Anmeldung) ──► Add-on „Planner“ (planner/server.py, Port 8099)
Echo Show (?anzeige) ─┘                                         │  /data/tasks.json, settings.json, prefs.json, ai_usage.json
                                                                │  /share/planner/ (Spiegel + Sicherungen)
                                                                ├─► Home Assistant: Sensoren, Mitteilungen, Alexa (REST + WebSocket)
                                                                └─► Google Gemini (nur für KI-Vorschläge, Schlüssel bleibt im Add-on)
Claude-Artifact (src/planner.html) ─► Claude-Datenbank (window.claude.use)   ← zweite, unabhängige Version
```

## Dateien

| Datei | Rolle | Von Hand ändern? |
|---|---|---|
| `src/planner.html` | **Master** der Oberfläche: HTML, CSS, JavaScript in einer Datei. Läuft direkt als Claude-Artifact. | ja |
| `planner/index.html`, `planner/VERSION` | Add-on-Oberfläche, von `tools/build.py` erzeugt | **nein** |
| `planner/server.py` | Server (nur Python-Standardbibliothek): Daten, Prüfung, Sicherungen, Home Assistant, Alexa, KI | ja |
| `planner/config.yaml` | Add-on-Beschreibung für Home Assistant, **Versionsnummer** | ja |
| `planner/CHANGELOG.md`, `planner/DOCS.md` | Änderungen und Anleitung, in Home Assistant sichtbar | ja |
| `tools/build.py` | Erzeugt die Add-on-Version, prüft den Vertrag zwischen beiden Versionen und die JS-Syntax | ja |
| `tools/check.py` | Alle Prüfungen in einem Lauf (auch im GitHub-Prüflauf) | ja |
| `tools/release.py` | Neue Version: Nummer setzen, bauen, alles prüfen | ja |
| `tools/test_server.py`, `tools/test_ha.py`, `tools/test_browser.py` + `tools/e2e/` | Tests | ja |

## Die zwei Versionen und der Build

Die Oberfläche existiert nur einmal (`src/planner.html`). Der Unterschied zwischen Claude-Version und Add-on steckt in einem Block zwischen den Kommentaren `/* Speicher: gemeinsame Datenbank, sonst lokal */` und `/* Anzeige */`. `tools/build.py` ersetzt diesen Block durch die Server-Version (`STORAGE` in `build.py`), ersetzt `dl()` (Teilen-Menü auf dem iPhone) und ergänzt die Angaben für „Zum Home-Bildschirm“.

**Vertrag** (prüft `build.py` bei jedem Lauf):
- Jeder Name, den der Claude-Block auf oberster Ebene definiert, muss auch in `STORAGE` stehen. Ausnahmen in `ARTIFACT_ONLY`.
- Jede Funktion, die `STORAGE` aufruft, muss in der Datei existieren.
- Beide Dateien müssen `node --check` bestehen.

Gemeinsame Schnittstelle des Blocks: `prefGet`, `prefSet`, `USER`, `init`, `saveTask`, `delTask`, `saveReg`, `saveMany`, `aiAvail`, `aiJson`. Alles andere in der Oberfläche ist für beide Versionen gleich.

## Aufbau von `src/planner.html`

Eine Datei, gegliedert durch Kommentar-Überschriften (`/* … */` am Zeilenanfang). Reihenfolge:

1. **CSS** (Zeilen ~19–1020): Grundgerüst, dann Schichten je Version (`/* 1.2: … */` bis `/* 1.32: … */`). Spätere Schichten überschreiben frühere. Neue Regeln kommen ans Ende, mit Versionskommentar. Farben nur über Variablen (`--acc`, `--grp`, Status `--sky`, `--sun`, `--sea`, `--brick`).
2. **HTML** (bis ~1120): Seitenleiste, Kopfzeile, `#main`, Dialoge (`<dialog id="dlg">` Aufgabe, `dlf` Filter, `dls` Einstellungen, `dsh` Aktionsblatt, …).
3. **JavaScript** (ab ~1122): Zustand (`RAW`, `tasks`, `reg`), Speicher-Block, Schnelleingabe-Parser, Ansichten (`render()` → Start, Board, Liste, Zeitstrahl, Kalender), Einstellungen, Gesten, Aufgabenblatt.

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
| `python3 tools/build.py --check` | erzeugte Dateien aktuell, Vertrag, JS-Syntax | ~7 s |
| `python3 tools/test_server.py` | Datenprüfung, Schreibschutz, Host-Prüfung, KI-Limits, Schnelleingabe, Benutzer | ~2 s |
| `python3 tools/test_ha.py` | Erinnerung je Person, Abhaken aus der Mitteilung, Alexa (mit nachgebautem Home Assistant) | ~17 s |
| `python3 tools/test_browser.py` | Oberfläche in Chromium auf Handy, iPad, Desktop (Gesten, Blätter, Schnelleingabe, KI, Benutzer, Echo-Ansicht, Claude-Version) | ~1 min |
| `python3 tools/check.py` | alles oben | ~1,5 min |

Nicht abgedeckt (nur auf echten Geräten prüfbar, siehe `PRUEFLISTE.md`): Safari/WKWebView auf dem iPhone, echte Mitteilungen, echte Alexa-Spracherkennung, echtes Gemini.

## Wenn du X änderst, prüfe Y

| Änderung | Mögliche Auswirkung | Prüfen |
|---|---|---|
| CSS-Regel ändern oder entfernen | Spätere Schichten überschreiben frühere; dieselbe Klasse wird an mehreren Stellen gestaltet | Bildschirmfotos Handy/iPad/Desktop, hell und dunkel (`SHOT_DIR=… tools/test_browser.py`) |
| Speicher-Block in `src` | Add-on-Version weicht ab | `build.py` meldet fehlende Namen; `STORAGE` nachziehen |
| Schnelleingabe (JS `parseQuick`) | Siri/Alexa erkennen anders als die App | `test_browser.py schnell` vergleicht beide Parser |
| `clean()` oder Datenformat | Bestehende Aufgaben könnten Felder verlieren | Nur ergänzen, nie Felder entfernen; `test_server.py` |
| Erinnerung, Alexa, WebSocket | Mitteilungen an falsche Person, doppelte Sprachbefehle | `test_ha.py` |
| Neue Schnittstelle im Server | Schreibschutz vergessen | `X-Planner`-Prüfung gilt für alle POST/DELETE in `guard()`; Test ergänzen |
| Persönliche Einstellung (neuer Schlüssel) | Wird nicht je Benutzer gespeichert | In `PREF_KEYS` (Server) und `PK` (`build.py`) eintragen |
