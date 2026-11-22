# Arbeitsanweisung für Claude: Planner

Haus-Aufgaben-Tool von Lasse und Melanie (Kanban, Liste, Gantt). Sprache der Oberfläche und aller Texte: natürliches Deutsch. Lasse bevorzugt Kennzahlen zuerst, kompakte visuelle Signale, kurze Antworten.

## Zwei Versionen, eine Quelle

- **Master:** `src/planner.html`. Das ist die Claude-Version (nutzt `window.claude.use("db")` und `"downloads"`). Änderungen am Aussehen oder Verhalten macht man **nur hier**.
- **Add-on:** `planner/index.html` und `planner/VERSION` werden von `tools/build.py` erzeugt. **Nie von Hand ändern.**
- Beide Versionen müssen nach jeder Änderung aktualisiert werden: Add-on über Git, Claude-Link über das Artifact-Tool (Artifact "Planner" per `list` finden und dieselbe Datei auf dessen URL veröffentlichen).

## Ablauf bei jeder Änderung

1. `src/planner.html` bearbeiten. Serverseitige Änderungen in `planner/server.py`.
2. `version` in `planner/config.yaml` erhöhen (z. B. 1.1.0 → 1.1.1; neue Funktion: 1.2.0). Ohne neue Version zeigt Home Assistant kein Update an.
3. Eintrag oben in `planner/CHANGELOG.md`.
4. `python3 tools/build.py` ausführen. Das Skript bricht mit Fehler ab, wenn Claude-spezifischer Code in die Add-on-Version geraten würde.
5. Testen: Server lokal starten, z. B. `DATA_DIR=/tmp/d SHARE_DIR=/tmp/s INDEX=planner/index.html VERSION_FILE=planner/VERSION PORT=8097 python3 planner/server.py`, Seite mit Playwright in Handy-, iPad- und Desktop-Größe prüfen, JS-Syntax mit `node --check`.
6. Committen und pushen (alle geänderten Dateien: `src/`, `planner/`).
7. Claude-Artifact mit `src/planner.html` aktualisieren.

## Harte Regeln

- **Datenhaltung nicht verändern, ohne Rücksicht auf bestehende Daten.** Echte Aufgaben liegen im Add-on unter `/data/tasks.json` und gespiegelt unter `/share/planner/`. Änderungen am Datenformat nur abwärtskompatibel (alte Dateien müssen lesbar bleiben, `clean()` in `server.py` ergänzen statt Felder zu entfernen).
- Nie Daten aus `/data` oder `/share` ins Repository einchecken. Das Repository ist öffentlich.
- Name überall **Planner**. Ordner, Slug und Sensor-IDs heißen `planner`. Der alte Slug war `haus_planer`; dessen Spiegel `/share/haus_planer/` übernimmt der Server beim ersten Start einmalig. Das GitHub-Repository heißt noch `Haus-planner` (Umbenennung steht bei Lasse aus; solange die URL in `repository.yaml` nicht ändern).
- `slug` in `config.yaml` (`planner`) nicht mehr ändern, sonst ist es für Home Assistant ein neues Add-on mit leerem Datenordner. Die Browser-Einstellungen heißen weiterhin `haus-*` (localStorage), damit gespeicherte Einstellungen nicht verloren gehen.
- Oberfläche muss auf Handy, iPad (hochkant und quer) und Desktop funktionieren. Keine festen Pixelbreiten für das Layout, Schriftgrößen relativ.
- Farben: Portofino-Palette (D35526, FDAF54, F5F3EB, 6CB6E4, 387CA3). Offen = Himmelblau, In Arbeit = Orange, Erledigt = Meerblau, Überfällig = Ziegelrot. Kein typischer KI-Look (keine Verläufe, kein Glas, keine Emojis in der Oberfläche).
- Home-Assistant-Add-on: Ingress, deshalb in `index.html` nur **relative** Pfade (`api/tasks`, nicht `/api/tasks`).
- Dem Nutzer nach jedem Update sagen: Version in HA unter *Add-on-Store → ⋮ → Nach Updates suchen* → *Aktualisieren*; ehrlich benennen, was nur im Test-Browser und nicht auf echten Geräten geprüft wurde.
