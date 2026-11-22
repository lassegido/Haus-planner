# Arbeitsanweisung für Claude: Haus-planner

Haus-Aufgaben-Tool von Lasse und Melanie (Kanban, Liste, Gantt). Sprache der Oberfläche und aller Texte: natürliches Deutsch. Lasse bevorzugt Kennzahlen zuerst, kompakte visuelle Signale, kurze Antworten.

## Zwei Versionen, eine Quelle

- **Master:** `src/haus-planner.html`. Das ist die Claude-Version (nutzt `window.claude.use("db")` und `"downloads"`). Änderungen am Aussehen oder Verhalten macht man **nur hier**.
- **Add-on:** `haus_planer/index.html` und `haus_planer/VERSION` werden von `tools/build.py` erzeugt. **Nie von Hand ändern.**
- Beide Versionen müssen nach jeder Änderung aktualisiert werden: Add-on über Git, Claude-Link über das Artifact-Tool (Artifact "Haus-planner" per `list` finden und dieselbe Datei auf dessen URL veröffentlichen).

## Ablauf bei jeder Änderung

1. `src/haus-planner.html` bearbeiten. Serverseitige Änderungen in `haus_planer/server.py`.
2. `version` in `haus_planer/config.yaml` erhöhen (z. B. 1.1.0 → 1.1.1; neue Funktion: 1.2.0). Ohne neue Version zeigt Home Assistant kein Update an.
3. Eintrag oben in `haus_planer/CHANGELOG.md`.
4. `python3 tools/build.py` ausführen. Das Skript bricht mit Fehler ab, wenn Claude-spezifischer Code in die Add-on-Version geraten würde.
5. Testen: Server lokal starten, z. B. `DATA_DIR=/tmp/d SHARE_DIR=/tmp/s INDEX=haus_planer/index.html VERSION_FILE=haus_planer/VERSION PORT=8097 python3 haus_planer/server.py`, Seite mit Playwright in Handy-, iPad- und Desktop-Größe prüfen, JS-Syntax mit `node --check`.
6. Committen und pushen (alle geänderten Dateien: `src/`, `haus_planer/`).
7. Claude-Artifact mit `src/haus-planner.html` aktualisieren.

## Harte Regeln

- **Datenhaltung nicht verändern, ohne Rücksicht auf bestehende Daten.** Echte Aufgaben liegen im Add-on unter `/data/tasks.json` und gespiegelt unter `/share/haus_planer/`. Änderungen am Datenformat nur abwärtskompatibel (alte Dateien müssen lesbar bleiben, `clean()` in `server.py` ergänzen statt Felder zu entfernen).
- Nie Daten aus `/data` oder `/share` ins Repository einchecken. Das Repository ist öffentlich.
- Name überall **Haus-planner** (so heißt auch das Repository). Technische Bezeichner bleiben `haus_planer` (Slug, Ordner, `share/haus_planer`): nicht umbenennen.
- `slug` in `config.yaml` (`haus_planer`) nicht ändern, sonst ist es für Home Assistant ein neues Add-on mit leerem Datenordner.
- Oberfläche muss auf Handy, iPad (hochkant und quer) und Desktop funktionieren. Keine festen Pixelbreiten für das Layout, Schriftgrößen relativ.
- Farben: Portofino-Palette (D35526, FDAF54, F5F3EB, 6CB6E4, 387CA3). Offen = Himmelblau, In Arbeit = Orange, Erledigt = Meerblau, Überfällig = Ziegelrot. Kein typischer KI-Look (keine Verläufe, kein Glas, keine Emojis in der Oberfläche).
- Home-Assistant-Add-on: Ingress, deshalb in `index.html` nur **relative** Pfade (`api/tasks`, nicht `/api/tasks`).
- Dem Nutzer nach jedem Update sagen: Version in HA unter *Add-on-Store → ⋮ → Nach Updates suchen* → *Aktualisieren*; ehrlich benennen, was nur im Test-Browser und nicht auf echten Geräten geprüft wurde.
