# Planner

Aufgaben, Board, Liste und Zeitstrahl für zu Hause. Läuft komplett lokal auf deinem Home Assistant.

## Wo liegen meine Daten?

- **Hauptspeicher:** `/data/tasks.json` im Add-on. Dieser Ordner bleibt bei **Update** und **Neu bauen** erhalten.
- **Tägliche Kopien:** `/data/backups` (die letzten 30 Tage).
- **Spiegel außerhalb des Add-ons:** Bei jeder Änderung wird zusätzlich nach `share/planner/` kopiert (`tasks-latest.json` und tägliche Kopien). Der Ordner ist über die Samba-Freigabe `share` erreichbar und bleibt sogar nach einer Deinstallation erhalten.
- **Automatische Wiederherstellung:** Findet das Add-on beim Start keine Daten, aber `share/planner/tasks-latest.json` (oder den alten Spiegel `share/haus_planer/tasks-latest.json` aus Version 1.13 und älter), spielt es diese Datei selbst wieder ein, samt Dateianhängen.
- Außerdem sind die Daten in euren normalen Home-Assistant-Backups enthalten.

## Update einspielen

Der Code kommt von GitHub. Wenn dort eine neue Version liegt:

1. **Einstellungen → Add-ons → Add-on-Store → ⋮ (oben rechts) → Nach Updates suchen.**
2. Beim Planner auf **Aktualisieren** klicken.
3. In der App unter **Export** steht unten die installierte Version.

Die Aufgaben bleiben dabei erhalten. **Nicht deinstallieren**, um zu aktualisieren: Nur beim Deinstallieren werden die Daten im Add-on gelöscht.

## Wiederherstellen

- **Aus einer Backup-Datei:** In der App **Export → Backup einspielen** und die JSON-Datei wählen.
- **Aus dem Spiegel:** Die gewünschte Datei aus `share/planner/` in der App über „Backup einspielen" laden.

## Von unterwegs

Zugriff von außen nur über Nabu Casa oder ein VPN (z. B. Tailscale).

## Erinnerungen aufs Handy

1. Im Planner **Einstellungen → Home Assistant → Erinnerung** öffnen.
2. Die Geräte auswählen, die erinnert werden sollen (alle Benachrichtigungsdienste der Home-Assistant-App werden automatisch gefunden). Mehrere sind möglich.
3. Unter **Uhrzeit** die Zeit der täglichen Erinnerung wählen (Standard 08:00, in der Zeitzone von Home Assistant). Sie kommt nur, wenn etwas heute fällig oder überfällig ist.
4. Mit **Testnachricht senden** auf derselben Seite prüfen, ob es ankommt. Ein Neustart ist nicht nötig.

**Direkt abhaken:** Auf dem iPhone die Erinnerung lang drücken (oder nach unten ziehen). Dann erscheinen bis zu vier Knöpfe „Erledigt: …“ für die wichtigsten fälligen Aufgaben, Prio 1 zuerst. Ein Druck setzt die Aufgabe auf erledigt und aktualisiert die Mitteilung. Ein Antippen der Mitteilung öffnet den Planner. Wiederkehrende und blockierte Aufgaben haben keinen Knopf, die erledigt man in der App. Voraussetzung ist, dass das Add-on mit Home Assistant verbunden ist (im Add-on-Protokoll steht dann „Verbindung zu Home Assistant für Mitteilungs-Knöpfe steht“).

## Sensoren

Der Planner legt in Home Assistant fünf Sensoren an, die jede Minute aktualisiert werden: `sensor.planner_offen`, `sensor.planner_in_arbeit`, `sensor.planner_ueberfaellig`, `sensor.planner_heute_faellig` und `sensor.planner_prio1` (offene Aufgaben mit Prio 1). Das Attribut `aufgaben` enthält die Titel. Abschalten mit `sensors: false` in der Konfiguration.

## Persönlich oder für alle

Öffnest du den Planner über die Home-Assistant-App, weiß er, wer angemeldet ist. **Nur für dich** gelten Darstellung, Farbwelt, Schrift, „Ich bin“ und die Startseiten-Auswahl (gespeichert je Home-Assistant-Benutzer in `/data/prefs.json`, also auf all deinen Geräten gleich). **Für alle** gelten Aufgaben, Erinnerungs-Geräte, Alexa, Sensoren und der KI-Schlüssel. Über Port 8099 (ohne Anmeldung) gelten persönliche Einstellungen nur für das jeweilige Gerät.

Erinnerung: Unter Einstellungen → Erinnerung die Geräte wählen. Jedes Gerät gehört zu einer Person (aus dem Gerätenamen erraten, antippen zum Ändern) und erinnert an deren Aufgaben und an Aufgaben ohne Zuständigkeit.

## Schnelleingabe

Auf der Startseite oben einfach tippen und mit Enter anlegen, oder im Titel einer neuen Aufgabe. Erkannt wird:

| Eingabe | Bedeutung |
|---|---|
| `heute`, `morgen`, `übermorgen`, `Sa`, `Freitag`, `12.12.`, `in 3 Tagen`, `nächste Woche`, `Wochenende` | Datum |
| `bis Fr` | von heute bis zu diesem Tag |
| `#Garten` | Tag (Anfang genügt, `#gart` findet „Garten“; Leerzeichen als `_`) |
| `+Schöner_Wohnen` | Projekt |
| `@Melanie` | verantwortlich (mehrere möglich) |
| `!1`, `!2`, `!3` | Priorität |

Beispiel: `Zaun streichen Sa #Garten !1 @Melanie`. Unter dem Feld siehst du vor dem Anlegen, was erkannt wurde.

**Frühere Aufgaben als Vorlage** (wie im Apple Kalender): Beim Tippen erscheinen bis zu vier frühere Aufgaben, deren Titel so beginnt (ab drei Zeichen auch ein Wort mitten im Titel), auch erledigte und archivierte. Gibt es einen Titel mehrfach, zählt die jüngste Aufgabe. Antippen übernimmt Tags, Projekt, Person, Priorität, Dauer, Wiederholung, Notizen und die Checkliste (alle Punkte wieder offen); Datum ab heute oder ab dem getippten Tag. Was du selbst tippst (`Sa`, `@Melanie`, `#Tag`), hat Vorrang. Nicht übernommen: Abhängigkeiten, Verlauf, Kommentare und Dateien. Auf der Startseite öffnet sich danach das Aufgabenblatt zum Prüfen, im Blatt gibt es „Rückgängig“. Enter legt wie gewohnt ohne Vorlage an.

**Wiederholen** (im Aufgabenblatt unter „Wiederholen und Abhängigkeiten“): Schnellauswahl oder „Benutzerdefiniert …“ mit Abstand (alle n Tage/Wochen/Monate/Jahre), Wochentagen (z. B. Di und Do), bei Monaten „am 12.“ oder „am 2. Dienstag“ bzw. „am letzten Freitag“ und optionalem Enddatum. Beim Erledigen legt der Planner die nächste Aufgabe an; nach dem Enddatum nicht mehr.

**Motivation:** Auf der Startseite zeigen eine Serie (Tage in Folge mit vollem Tagesring), „Gemeinsam diese Woche“ (wer wie viel erledigt hat, aus dem Verlauf) und Abzeichen den Fortschritt. Ist die letzte Aufgabe des Tages erledigt, gibt es Konfetti. Gespeichert wird dafür nichts extra; alles wird aus den Aufgaben berechnet. Dazu ein Spruch passend zur Lage; mit Gemini-Schlüssel werden die Sprüche einmal am Tag neu geschrieben (eine Anfrage, nur wenn weniger als die Hälfte des Tageslimits verbraucht ist, gespeichert in `/data/sprueche.json`). Die Themen stehen in `MEME_THEMES` in `server.py`.

**Ring auf der Startseite:** zeigt nur den heutigen Tag der oben gewählten Person („Meine“, eine andere Person oder „Alle“): überfällige, heute anstehende und heute erledigte Aufgaben.

## Per Sprache: Siri-Kurzbefehl

Braucht den direkten Port 8099 (siehe unten) und funktioniert im Heimnetz.

1. App **Kurzbefehle** → **+** → Aktion **Diktieren** (Sprache Deutsch).
2. Aktion **Inhalt von URL abrufen**: URL `http://<IP-von-Home-Assistant>:8099/api/quick`, Methode **POST**, Header `X-Planner` = `1`, Hauptteil **JSON** mit Feld `text` = *Diktierter Text* (optional Feld `who` = `Lasse`).
3. Aktion **Wörterbuchwert abrufen**: Schlüssel `speech`, dann **Text sprechen**.
4. Kurzbefehl „Planner“ nennen. Dann: „Hey Siri, Planner“ → „Rasen mähen Samstag Hashtag Garten“. Siri antwortet z. B. „‚Rasen mähen‘ ist für Sa, 28.11. eingetragen.“

Tipp: Gesprochen wird „Hashtag Garten“ oft als „#Garten“ erkannt. Ohne Tag geht es immer.

## Per Sprache: Home Assistant Assist

In `configuration.yaml` (IP anpassen):

```yaml
rest_command:
  planner_neu:
    url: "http://<IP-von-Home-Assistant>:8099/api/quick"
    method: POST
    headers:
      X-Planner: "1"
    content_type: "application/json"
    payload: '{"text": {{ text | tojson }}}'

intent_script:
  PlannerNeu:
    action:
      - action: rest_command.planner_neu
        data:
          text: "{{ text }}"
    speech:
      text: "Steht im Planner."
```

Und `custom_sentences/de/planner.yaml`:

```yaml
language: "de"
intents:
  PlannerNeu:
    data:
      - sentences:
          - "(Planner|Aufgabe) {text}"
          - "neue Aufgabe {text}"
lists:
  text:
    wildcard: true
```

Danach Home Assistant neu starten und zu Assist sagen: „Neue Aufgabe Dachrinne reinigen morgen“.

## Alexa

Mit der Home-Assistant-Integration **Alexa Devices** (seit Home Assistant 2025.6, ohne Zusatzkonto bei Amazon-Entwicklern) hört der Planner auf deine Echo-Geräte.

1. Home Assistant: Einstellungen → Geräte & Dienste → Integration hinzufügen → **Alexa Devices**. Mit dem Amazon-Konto anmelden; Amazon verlangt die Zwei-Faktor-Anmeldung per Authenticator-App (SMS reicht nicht).
2. Planner: ⋯ → Einstellungen → **Alexa** → **An**. Nach ein paar Sekunden steht dort, wie viele Echos gefunden wurden.
3. Sprechen:
   - „Alexa, Planner Rasen mähen am Samstag Tag Garten“ legt an
   - „Alexa, Planner was steht heute an“ bzw. „Alexa, Planner Woche“ liest vor
   - „Alexa, Planner Fenster putzen ist erledigt“ hakt ab

Alexa selbst kennt den Befehl nicht und sagt das kurz; danach antwortet der Planner auf demselben Echo. Erkennt Alexa deine Stimme (Stimmprofil in der Alexa-App), wird die Aufgabe dir zugewiesen. Gesprochene Tags und Projekte („Tag Garten“) werden nur erkannt, wenn es sie schon gibt.

## Anzeige für Echo Show und Wandbildschirme

`http://<IP-von-Home-Assistant>:8099/?anzeige` zeigt Uhrzeit, heute fällige und überfällige Aufgaben und die nächsten Termine, groß und ohne Bedienleisten. Zusätze: `&wer=Lasse` (nur eine Person), `&dunkel` oder `&hell`. Abhaken per Tippen auf den Kreis. Den fertigen Link gibt es unter Einstellungen → Anzeige für Echo Show.

Am Echo Show: „Alexa, öffne Silk“, Adresse eingeben, als Lesezeichen speichern. Der Echo Show kehrt nach einer Weile zu seinem Startbildschirm zurück; das lässt sich von außen nicht verhindern.

## Siri: vorlesen und abhaken

Neben `api/quick` (nur anlegen) gibt es `api/voice`: gleiche Einrichtung wie beim Kurzbefehl oben, versteht zusätzlich „heute“, „Woche“ und „… ist erledigt“. Mit `GET api/speech?when=heute&who=Lasse` bekommst du nur den Vorlesetext.

## KI-Assistent (Google Gemini, kostenlos)

In jeder Aufgabe schlägt „Mit KI ausfüllen“ Notizen und Checklistenpunkte vor. Du entscheidest, was übernommen wird. Neue Tags bekommen außerdem ein passendes Symbol.

1. Auf [aistudio.google.com/apikey](https://aistudio.google.com/apikey) mit dem Google-Konto einen API-Schlüssel erstellen (kostenlos, ohne Kreditkarte).
2. Im Planner: **⋯ → Einstellungen → KI-Assistent**, Schlüssel einfügen, **Sichern**, dann **Verbindung testen**. Alternativ geht es in der Add-on-Konfiguration bei `gemini_api_key`; der Schlüssel aus dem Planner hat Vorrang.
3. Der Schlüssel liegt nur auf deinem Home Assistant (`/data/settings.json`) und wird nie an den Browser zurückgegeben.
4. Der kostenlose Tarif hat Tageslimits (bei Flash-Lite grob einige hundert Anfragen pro Tag, Google ändert das gelegentlich). Der Planner begrenzt selbst auf 40 Anfragen pro Stunde. Gesendet wird nur der Aufgabentext.

## Auf den Home-Bildschirm (App-Symbol, Vollbild)

Der Zugriff über Home Assistant (Ingress) braucht dessen Anmeldung und lässt sich nicht als eigene App ablegen. Dafür gibt es einen optionalen direkten Port:

1. Im Add-on unter **Netzwerk** den Port `8099` eintragen (z. B. 8099) und speichern.
2. Auf dem iPhone in Safari `http://<IP-von-Home-Assistant>:8099` öffnen, dann **Teilen → Zum Home-Bildschirm**.

Achtung: Dieser Port hat **keine Anmeldung**. Erlaubt sind nur Aufrufe über eine IP-Adresse, `homeassistant.local`, Namen ohne Punkt, typische Heimnetz-Endungen (`.local`, `.lan`, `.fritz.box`, `.home.arpa` …) und die in Home Assistant eingetragene interne und externe Adresse. Das schützt vor fremden Webseiten (DNS-Rebinding). Jeder im Heimnetz kann ihn öffnen. Nur aktivieren, wenn dein Netz vertrauenswürdig ist, und nie ins Internet weiterleiten.


## Daten und Grenzen

- Alle Aufgaben liegen in `/data/tasks.json` (Format-Version 2) und werden bei jedem Speichern nach `/share/planner/` gespiegelt.
- Sicherungen: 30 Tage täglich, 24 Monate je eine pro Monat (`tasks-monat-JJJJ-MM.json`), in `/data/backups` und im Share.
- Bearbeiten zwei Personen dieselbe Aufgabe gleichzeitig, fragt die App beim Speichern nach, statt still zu überschreiben.
- Richtwert: bis etwa 500 aktive Aufgaben bleibt alles flüssig. Erledigtes lässt sich in den Einstellungen archivieren; Archivierte zählen nicht zu den aktiven.
- Fotos und Dateien liegen in `/data/files`; es gibt kein Gesamtlimit, Speicherplatz bitte gelegentlich prüfen.
- Schriften sowie PDF- und Excel-Bibliothek liegen im Add-on. Der Planner lädt nichts aus dem Internet (außer KI-Anfragen an Google, wenn eingerichtet).

## Wenn etwas nicht funktioniert

Skriptfehler aus der App landen im **Add-on-Protokoll** (Einstellungen → Add-ons → Planner → Protokoll) als Zeile „Browser-Fehler: …“ mit Ansicht, Version und Gerät. Diese Zeilen bitte bei einer Fehlermeldung mitschicken. Pro Stunde werden höchstens 30 Meldungen angenommen.
