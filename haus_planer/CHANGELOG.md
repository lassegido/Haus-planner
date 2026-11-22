# Änderungen

## 1.12.0
- Zeitraum per Kalender: ein Feld statt zwei Datumsfelder, Start und Ende nacheinander antippen; dazu „Heute“, „Diese Woche“, „Nächste Woche“
- „Verantwortlich“ erlaubt mehrere Personen (Antippen zum An- und Abwählen, neue Personen per „+ Person“); Filter, Gruppierung und Zähler berücksichtigen alle
- Spalte und Status heißen wieder „Offen“ (statt „Zu starten“)
- Aufgabendialog neu geordnet: oben Titel, Zeitraum, Verantwortlich, Status, Tags, Projekt; Checkliste, Notizen, Wiederholen/Abhängigkeiten, Dateien und Verlauf als aufklappbare Gruppen, die sich bei Inhalt von selbst öffnen
- Heutiges Datum richtet sich nach deiner Zeitzone
## 1.11.0
- Neu: feine Linienicons neben den Tags (Board, Liste, Filter, Start). Sie werden automatisch zugeordnet: zuerst über Stichworte, mit eingetragenem KI-Schlüssel wählt die KI das passende Symbol; gespeichert im Tag-Verzeichnis, nicht von Hand wählbar
- Gleichzeitiges Bearbeiten: Wurde eine Aufgabe in der Zwischenzeit von jemand anderem geändert, wird nicht stillschweigend überschrieben, sondern gefragt („Trotzdem speichern“)
- Datenformat mit Versionsnummer (schema 2) und Aufgabenversion (v); alte Dateien bleiben lesbar
- Zusätzlich zu den 30 Tagessicherungen jetzt eine Sicherung pro Monat (24 Monate)
- Backups bis 25 MB lassen sich einspielen (vorher 2 MB); Speichern wird auf den Datenträger abgesichert (fsync)
- Board: Spalte „Erledigt“ zeigt die 20 neuesten, der Rest per Knopf
## 1.10.0
- Einstellungen neu: gruppierte Liste mit Untermenüs (Darstellung, Farbdesign, Akzentfarbe, Schriftart, Ich bin) und Vorschau; Änderungen gelten sofort
- Ruhigeres Design: Beschriftungen ohne Großbuchstaben, neutrale Board-Spalten, Tags als Text mit Farbpunkt, flache Startkarte, keine Farbleiste unter den Kennzahlen
- Texte gekürzt und vereinfacht; Startseite heißt jetzt „Start“, kürzerer Startbildschirm

## 1.9.0
- Neu: 5 Farbdesigns (Portofino, Wald, Beere, Graphit, Sand), jeweils in Hell und Dunkel
- Einstellungen mit Live-Vorschau oben: Farbdesign, Akzentfarbe, Hell/Dunkel und Schriftart lassen sich ausprobieren und mit „Übernehmen“ speichern oder mit „Verwerfen“ zurücknehmen
- Akzentfarbe „Passend zum Farbdesign“ als Standard

## 1.8.2
- Standardschrift ist jetzt Figtree (Einstellungen → Schriftart, dort lässt sich wieder auf Systemschrift oder andere wechseln)

## 1.8.1
- Outlook-Anbindung und die Backlog-Spalte wieder entfernt. Vorhandene Backlog-Aufgaben erscheinen unter „Zu starten". Der .ics-Export unter Export bleibt
- Gleich große Auswahlfelder, Farbkonzept und Schriftwahl aus 1.8.0 bleiben

## 1.8.0
- Neue Spalte „Backlog" (grau) vor „Zu starten"; „Offen" heißt jetzt „Zu starten". Backlog-Aufgaben zählen nicht als überfällig und lösen keine Erinnerung aus. Bestehende Aufgaben bleiben unverändert („Offen" wird zu „Zu starten")
- Auswahlfelder einheitlich: Optionen eines Reglers sind gleich breit (Tage / Monate / Jahre), Eingabefelder im Formular gleich hoch
- Farben je Feldtyp: Status in Statusfarben, Zuständig in Personenfarben (Melanie, Lasse, Andere), Projekt mit Projektfarbe, Personen-Punkte in der Seitenleiste
- Schriftart wählbar (Einstellungen): Systemschrift als Standard, dazu Figtree, Plus Jakarta Sans, DM Sans, Manrope und Inter
- Outlook: Termine aus einem veröffentlichten Outlook-ICS-Link erscheinen im Kalender (zuschaltbar), und die Aufgaben gibt es als ICS-Link zum Einbinden in Outlook (beides nur im Add-on)
- Kalender: Board-Punkte am Handy und Kalender-Punkte kollidieren nicht mehr

## 1.7.0
- KI-Assistent in der Aufgabe („Mit KI ausfüllen"): schlägt Notizen und Checklistenpunkte vor, du wählst aus, was übernommen wird. Im Add-on über einen eigenen Anthropic-API-Schlüssel (Konfiguration: `anthropic_api_key`)
- App-Symbol und Vollbild: Manifest, Symbole und Handy-Metadaten; über den optionalen direkten Port (Netzwerk) lässt sich der Haus-planner auf dem Home-Bildschirm ablegen

## 1.6.0
- Verlauf und Kommentare an jeder Aufgabe: Status-, Termin- und Zuständigkeits-Änderungen werden automatisch festgehalten, Kommentare mit Name (Einstellungen → „Ich bin")
- Kalender: Monatsansicht mit Tagesliste und Schnellanlage, Export als .ics für Apple, Google oder Outlook
- Fotos und Dateien an Aufgaben (nur im Home-Assistant-Add-on): Fotos werden verkleinert, alles liegt auf dem Server und im Share-Ordner

## 1.5.0
- Einstellungen (Regler-Symbol oben rechts): Darstellung Automatisch / Hell / Dunkel und sieben Akzentfarben
- Archiv und Papierkorb: Erledigtes archivieren, Gelöschtes bleibt 30 Tage im Papierkorb und lässt sich zurückholen
- Mehrfachauswahl (Knopf „Auswählen"): Status, Zuständig, Projekt, Archivieren oder Löschen für mehrere Aufgaben auf einmal
- Tastaturkürzel am Computer (N, /, 1–4, S, A, Entf, H, Esc)
- Home Assistant: tägliche Erinnerung aufs Handy (Add-on → Konfiguration → Benachrichtigungsdienst) und Sensoren `sensor.haus_planner_offen`, `_in_arbeit`, `_ueberfaellig`, `_heute_faellig`

## 1.4.0
- Wiederkehrende Aufgaben: täglich bis jährlich; beim Erledigen legt der Haus-planner automatisch die nächste an
- Projekte (mit Farbe, Fortschritt auf der Startseite, Filter und Gruppierung) und Meilensteine (Raute im Zeitstrahl)
- Zeitstrahl: Balken per Ziehen verschieben, Anfang/Ende ziehen, Abhängigkeiten per Ziehen verbinden (am Handy: lange drücken)
- Tags und Projekte gemeinsam verwalten

## 1.3.1
- Aufgaben-Formular neu gestaltet: Zuständig und Status als Auswahlleisten, einheitlich hohe Felder, nichts mehr abgeschnitten oder überlappend (auch auf kleinen Handys), größere Checklisten- und Abhängigkeits-Zeilen, Löschen als Symbol auf dem Handy

## 1.3.0
- Tags statt Freitext-Bereich: mehrere Tags pro Aufgabe auswählen oder direkt neu eingeben, jeder Tag mit eigener Farbe (10 Pastell- und Portofino-Farben)
- Tags verwalten: Farbe ändern, umbenennen (gilt für alle Aufgaben), löschen, neue anlegen
- Filter über die Tag-Leiste in Board, Liste und Zeitstrahl (mehrere Tags gleichzeitig, „Ohne Tag“)
- Gruppieren nach Tag oder Person in Liste und Zeitstrahl
- Bisherige Bereiche werden automatisch zu Tags, Aufgaben und Daten bleiben erhalten
- Excel, PDF und JSON-Backup enthalten die Tags

## 1.2.0
- Startseite mit Fortschrittsring, Überfälligem, Wochenübersicht und Auslastung pro Person; Begrüßung nach Tageszeit
- Kurzer Startbildschirm beim Öffnen
- Karten neu geordnet: Status als Kreis links (antippen schaltet weiter, mit „Rückgängig“), Person als Kürzel rechts, einheitliche Fußzeile
- Handy: Plus-Knopf sitzt in der Leiste statt über den Karten, Kopfzeilen-Knöpfe einheitlich
- Schlanke Bewegung: Einblenden beim Wechseln der Ansicht, hochzählende Zahlen, wachsende Balken, kleine Rückmeldung beim Statuswechsel (bei „Bewegung reduzieren“ aus)

## 1.1.1
- Umbenennung: Haus-Planer heißt jetzt durchgehend Haus-planner (Slug und Datenordner bleiben unverändert, Daten bleiben erhalten)

## 1.1.0
- Neues Design (Portofino-Farben), angepasst an Handy, iPad und Desktop
- Zeitstrahl mit Tage-, Monate- und Jahre-Ansicht, Wochentage, fixierte Beschriftung
- Personenfilter, Zurück-Knopf auf Karten
- Datensicherung zusätzlich im Ordner share/haus_planer, automatische Wiederherstellung
