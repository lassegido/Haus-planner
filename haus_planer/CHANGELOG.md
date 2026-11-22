# Änderungen

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
