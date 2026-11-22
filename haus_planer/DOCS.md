# Haus-planner

Aufgaben, Board, Liste und Zeitstrahl für zu Hause. Läuft komplett lokal auf deinem Home Assistant.

## Wo liegen meine Daten?

- **Hauptspeicher:** `/data/tasks.json` im Add-on. Dieser Ordner bleibt bei **Update** und **Neu bauen** erhalten.
- **Tägliche Kopien:** `/data/backups` (die letzten 30 Tage).
- **Spiegel außerhalb des Add-ons:** Bei jeder Änderung wird zusätzlich nach `share/haus_planer/` kopiert (`tasks-latest.json` und tägliche Kopien). Der Ordner ist über die Samba-Freigabe `share` erreichbar und bleibt sogar nach einer Deinstallation erhalten.
- **Automatische Wiederherstellung:** Findet das Add-on beim Start keine Daten, aber `share/haus_planer/tasks-latest.json`, spielt es diese Datei selbst wieder ein.
- Außerdem sind die Daten in euren normalen Home-Assistant-Backups enthalten.

## Update einspielen

Der Code kommt von GitHub. Wenn dort eine neue Version liegt:

1. **Einstellungen → Add-ons → Add-on-Store → ⋮ (oben rechts) → Nach Updates suchen.**
2. Beim Haus-planner auf **Aktualisieren** klicken.
3. In der App unter **Export** steht unten die installierte Version.

Die Aufgaben bleiben dabei erhalten. **Nicht deinstallieren**, um zu aktualisieren: Nur beim Deinstallieren werden die Daten im Add-on gelöscht.

## Wiederherstellen

- **Aus einer Backup-Datei:** In der App **Export → Backup einspielen** und die JSON-Datei wählen.
- **Aus dem Spiegel:** Die gewünschte Datei aus `share/haus_planer/` in der App über „Backup einspielen" laden.

## Von unterwegs

Zugriff von außen nur über Nabu Casa oder ein VPN (z. B. Tailscale).

## Erinnerungen aufs Handy

1. **Einstellungen → Add-ons → Haus-planner → Konfiguration.**
2. Bei **notify_service** den Namen des Benachrichtigungsdienstes der Home-Assistant-App eintragen, z. B. `mobile_app_iphone_von_lasse` (zu finden unter Entwicklerwerkzeuge → Aktionen, Suche nach „notify."). Mehrere Geräte durch Komma trennen.
3. **reminder_time** ist die Uhrzeit der täglichen Erinnerung (Standard 08:00, in der Zeitzone von Home Assistant). Sie kommt nur, wenn etwas heute fällig oder überfällig ist.
4. Speichern und das Add-on neu starten. In der App unter **Einstellungen** gibt es einen Knopf „Testbenachrichtigung senden".

## Sensoren

Der Haus-planner legt in Home Assistant vier Sensoren an, die jede Minute aktualisiert werden: `sensor.haus_planner_offen`, `sensor.haus_planner_in_arbeit`, `sensor.haus_planner_ueberfaellig` und `sensor.haus_planner_heute_faellig`. Das Attribut `aufgaben` enthält die Titel. Abschalten mit `sensors: false` in der Konfiguration.
