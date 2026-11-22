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

## KI-Assistent

In jeder Aufgabe schlägt „Mit KI ausfüllen" Notizen und Checklistenpunkte vor. Du entscheidest, was übernommen wird.

1. Unter [console.anthropic.com](https://console.anthropic.com) einen API-Schlüssel erstellen.
2. Im Add-on unter **Konfiguration** bei `anthropic_api_key` eintragen und neu starten.
3. Die Nutzung kostet Geld (abgerechnet von Anthropic, pro Anfrage meist nur Bruchteile eines Cents mit dem Standardmodell `claude-haiku-5-5`). Es wird nur der Aufgabentext gesendet, keine anderen Daten.

## Auf den Home-Bildschirm (App-Symbol, Vollbild)

Der Zugriff über Home Assistant (Ingress) braucht dessen Anmeldung und lässt sich nicht als eigene App ablegen. Dafür gibt es einen optionalen direkten Port:

1. Im Add-on unter **Netzwerk** den Port `8099` eintragen (z. B. 8099) und speichern.
2. Auf dem iPhone in Safari `http://<IP-von-Home-Assistant>:8099` öffnen, dann **Teilen → Zum Home-Bildschirm**.

Achtung: Dieser Port hat **keine Anmeldung**. Jeder im Heimnetz kann ihn öffnen. Nur aktivieren, wenn dein Netz vertrauenswürdig ist, und nie ins Internet weiterleiten.

## Outlook-Kalender

**Termine aus Outlook im Kalender sehen (Import):**
1. Outlook im Web → Einstellungen → Kalender → Freigegebene Kalender → **Kalender veröffentlichen** → ICS-Link kopieren. (In manchen Firmenkonten sperrt der Administrator das Veröffentlichen.)
2. In der App unter **Einstellungen → Outlook-Kalender** einfügen und speichern. Die Termine werden alle 30 Minuten aktualisiert und lassen sich im Kalender mit dem Knopf „Outlook" ein- und ausblenden. Sie sind nur lesbar.

**Aufgaben in Outlook sehen (Link zum Einbinden):**
1. Im Add-on unter **Netzwerk** den Port 8099 aktivieren.
2. In den Einstellungen den Link kopieren, den Namen im Link durch die IP von Home Assistant ersetzen.
3. Outlook am Computer oder Mac: Kalender hinzufügen → Aus dem Internet.

Outlook im Web und in der Handy-App rufen Abo-Links über Microsoft-Server ab und erreichen dein Heimnetz nicht. Der Link ist durch einen langen Schlüssel geschützt, der Port ansonsten ungeschützt: nur im vertrauenswürdigen Heimnetz nutzen, nie ins Internet weiterleiten.
