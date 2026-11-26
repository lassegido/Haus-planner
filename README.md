# Planner

Aufgaben als Liste, Board und Zeitstrahl für zu Hause. Läuft als Home-Assistant-Add-on auf dem eigenen Gerät. Dieses Repository enthält nur den **Code**. Die Aufgaben selbst liegen nie hier, sondern auf deinem Home Assistant.

## Einrichtung (einmalig)

1. **Repository anlegen:** Auf github.com ein kostenloses Konto erstellen, dann *New repository* → Name `planner` → **Public** → ohne README anlegen. (Öffentlich ist nötig, damit Home Assistant es ohne Zugangsdaten laden kann. Es steht kein persönlicher Inhalt drin.)
2. **Code hochladen:** Das ZIP entpacken und den **Inhalt** des Ordners `planner` (also `planner`, `src`, `tools`, `repository.yaml`, `README.md`, `CLAUDE.md`) auf der Repository-Seite per *Add file → Upload files* hineinziehen und *Commit changes* klicken.
3. **URL prüfen:** In `repository.yaml` steht bereits `https://github.com/lassegido/planner`. Passt der Name nicht zu deinem Konto, die Datei öffnen → Stift-Symbol → anpassen → *Commit changes*.
4. **In Home Assistant hinzufügen:** *Einstellungen → Add-ons → Add-on-Store → ⋮ (oben rechts) → Repositories* → `https://github.com/lassegido/planner` einfügen → *Hinzufügen*. Unten erscheint **Planner** → *Installieren* → *Starten* → *In Seitenleiste anzeigen*.

## Daten vom bisherigen lokalen Add-on übernehmen

Das Add-on aus dem Repository ist für Home Assistant ein **neues** Add-on mit eigenem Datenordner. Die Aufgaben kommen so mit:

1. Das bisherige lokale Add-on auf Version 1.1.0 bringen und einmal starten. Es kopiert die Daten nach `share/planner/`.
2. In der App zur Sicherheit *Export → Backup-Datei (JSON)* speichern.
3. Das bisherige lokale Add-on **stoppen** (nicht gleichzeitig laufen lassen).
4. Das Add-on aus dem Repository installieren und starten. Es findet keine eigenen Daten, aber den Spiegel in `share/planner/`, und holt sie automatisch zurück.
5. Prüfen, ob alle Aufgaben da sind. Erst dann das alte lokale Add-on deinstallieren.

Fehlt etwas: in der App *Export → Backup einspielen* und die JSON-Datei aus Schritt 2 wählen.

## Updates

- Neuer Code liegt auf GitHub und `version` in `planner/config.yaml` ist erhöht.
- In Home Assistant: *Add-on-Store → ⋮ → Nach Updates suchen*, dann beim Planner **Aktualisieren**. Home Assistant prüft auch von selbst regelmäßig.
- Die Aufgaben bleiben erhalten (Datenordner `/data` und Spiegel `share/planner/`).
- Die installierte Version steht in der App unter *Export* ganz unten.

## Arbeiten mit Claude

Siehe `CLAUDE.md` und `ARCHITEKTUR.md`. Kurz: Claude ändert die Quellen in `src/` (und bei Bedarf `planner/server.py`), schreibt einen Test dazu, erhöht mit `python3 tools/release.py <Version>` die Version (baut und prüft alles) und pusht. Der Link in Claude (Artifact) wird aus `artifact/planner.html` aktualisiert. Jeder Push wird auf GitHub unter *Actions* geprüft.

## Aufbau

| Pfad | Zweck |
|---|---|
| `src/` | Quellen der Oberfläche: `seite.html` (Gerüst), `style.css`, `js/*.js` – hier wird gearbeitet |
| `tools/build.py` | setzt daraus `artifact/planner.html` (Claude) und `planner/index.html` (Add-on) zusammen |
| `tools/check.py` | alle Prüfungen (Server, Home Assistant, Browser) |
| `planner/` | das Home-Assistant-Add-on (Server, Oberfläche, Konfiguration) |
| `repository.yaml` | macht das Repository für Home Assistant erkennbar |
