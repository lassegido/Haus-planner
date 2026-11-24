# Änderungen

## 1.33.0
- **Frühere Aufgaben als Vorlage** (wie im Apple Kalender): Beim Eintippen eines Titels, im Aufgabenblatt und in der Schnelleingabe auf der Startseite, erscheinen frühere Aufgaben mit gleichem Anfang. Antippen übernimmt Tags, Projekt, Person, Priorität, Dauer, Wiederholung, Notizen und die Checkliste (Punkte wieder offen). Datum ab heute oder ab dem getippten Tag; Getipptes wie `@Melanie` hat Vorrang. Abhängigkeiten, Verlauf und Dateien bleiben bei der alten Aufgabe.
- **Ring auf der Startseite zeigt nur heute:** überfällige, heute anstehende und heute erledigte Aufgaben der oben gewählten Person (standardmäßig „Meine“), z. B. „Heute: 2 von 5 erledigt“. Die Übersichten darunter zählen weiter alles.
- „Rückgängig“ im Hinweis unten funktioniert jetzt auch, während ein Blatt offen ist (vorher nicht antippbar).
- Verlaufseinträge aus Mitteilungen und von Alexa stehen mit der richtigen Uhrzeit im Verlauf (vorher eine Stunde zu spät angezeigt).

## 1.32.0
- **Suche bei Abhängigkeiten:** Im Aufgabenblatt unter „Wiederholen und Abhängigkeiten“ gibt es ein Suchfeld (Titel, Projekt, Tag, Person; mehrere Wörter möglich). Gewählte Aufgaben bleiben beim Suchen sichtbar. Aufgaben, die von der aktuellen abhängen, sind gesperrt (sonst entstünde ein Kreis).
- **Schneller und unabhängig vom Internet:** Schriften sowie PDF- und Excel-Bibliothek liegen jetzt im Add-on. Die PDF-Bibliothek bremst den Start nicht mehr, sie lädt erst beim Öffnen von „Export und Backup“.
- **Fehler sichtbar:** Skriptfehler aus der App erscheinen im Add-on-Protokoll („Browser-Fehler: …“).
- Unter der Haube: Oberfläche in Dateien aufgeteilt, ungenutzte Gestaltungsregeln entfernt (Aussehen nachweislich unverändert), Server-Schnittstellen aufgeräumt, 83 automatische Oberflächen-Tests und ein Prüflauf auf GitHub bei jeder Änderung.

## 1.31.1
- Gedrückt halten auf einer Karte öffnet nur noch das Menü und markiert keinen Text mehr (auch nicht den Titel im Menü). In Eingabefeldern bleibt Markieren und Einsetzen möglich.

## 1.31.0
- **Persönlich je Benutzer:** Der Planner erkennt beim Öffnen über die Home-Assistant-App, wer angemeldet ist. Darstellung, Farbwelt, Schrift, „Ich bin“ und die Auswahl auf der Startseite gelten je Person auf all ihren Geräten. Wählt Melanie eine andere Farbwelt, bleibt Lasses Design unverändert. „Ich bin“ wird beim ersten Öffnen automatisch gesetzt.
- **Erinnerung je Person:** Unter Einstellungen → Erinnerung gehört jedes gewählte Gerät zu einer Person (automatisch aus dem Gerätenamen, z. B. „iPhone von Lasse“ → Lasse; antippen zum Ändern). Jedes Gerät erinnert nur an die Aufgaben seiner Person und an Aufgaben ohne Zuständigkeit, mit passenden Abhaken-Knöpfen.
- **Einstellungen getrennt:** „Nur für dich“ und „Für alle im Haushalt“ (Aufgaben, Home Assistant, Erinnerung, Alexa, KI-Schlüssel).
- Fehler behoben: interne Sperre konnte sich beim Speichern von Einstellungen selbst blockieren.

## 1.30.1
- KI-Seite: Hinweis ergänzt, dass der Gemini-Schlüssel für alle Nutzer des Planners auf diesem Home Assistant gilt (nicht nur für das Gerät, auf dem er eingetragen wurde).

## 1.30.0
- Checkliste umsortieren: Punkt am Griff links (sechs Punkte) gedrückt halten und an die neue Stelle ziehen. Die Reihenfolge wird mit der Aufgabe gespeichert.
- KI-Vorschlag anpassen: Unter dem Vorschlag schreibst du, was anders sein soll (z. B. „Wände sind schon verputzt“), und tippst „Neu vorschlagen“. Die KI berücksichtigt alle Hinweise dieser Runde. Jede Anpassung zählt als eine KI-Anfrage.

## 1.29.0
- **Alexa:** Mit der Home-Assistant-Integration „Alexa Devices“ hört der Planner auf Echo-Befehle, die mit „Planner“ beginnen: Aufgaben anlegen, „was steht heute an“ und „Woche“ vorlesen, „… ist erledigt“ abhaken. Die Antwort kommt auf demselben Echo; mit Stimmprofil wird die Aufgabe der sprechenden Person zugewiesen. Schalter unter Einstellungen → Alexa.
- **Anzeige für Echo Show und Wandbildschirme:** `?anzeige` zeigt Uhrzeit, Heute und Als Nächstes groß und ohne Bedienleisten, optional nur für eine Person und dunkel. Link unter Einstellungen → Anzeige für Echo Show.
- **Gesprochene Eingaben:** „am Samstag“, „am zwölften Dezember“, „in drei Tagen“, „kommende Woche“, „Tag Garten“, „Projekt Haus“, „Priorität eins“ werden erkannt, in der Schnelleingabe wie per Sprache.
- **Siri:** Neuer Endpunkt `api/voice` (anlegen, vorlesen, abhaken) und `api/speech` (nur vorlesen).

## 1.28.0
Schneller im Alltag:
- **Schnelleingabe:** Auf der Startseite oben tippen und mit Enter anlegen, auch im Titel einer neuen Aufgabe. Erkannt werden Datum (heute, morgen, Sa, 12.12., in 3 Tagen, nächste Woche, bis Fr), #Tag, +Projekt, @Person und !1 bis !3. Eine Vorschau zeigt vorher, was erkannt wurde.
- **Startseite rund um „Heute“:** Kacheln für Heute, 7 Tage, In Arbeit und Überfällig mit Zahlen. Antippen zeigt die Liste darunter, abhakbar und wischbar. Die Übersicht (Fortschritt, Projekte, Tags, Personen) folgt darunter.
- **Per Sprache:** Neuer Endpunkt `api/quick` für einen Siri-Kurzbefehl und Home-Assistant-Assist. Anleitung in der Dokumentation, Siri liest die Bestätigung vor.
- **Einstieg:** Beim ersten Start fragt die App, wer das Gerät nutzt, und zeigt einen Tipp. Nach dem Speichern einer Änderung oder dem Anlegen gibt es „Rückgängig“.
- **KI sparsam:** Tageslimit des Planners (Flash-Lite 100, Flash 15 Anfragen), höchstens 20 pro Stunde, Zähler übersteht Neustarts. Meldet Google ein Limit, ruht die KI bis zum nächsten Tag. Tag-Symbole werden je Tag nur einmal angefragt. Verbrauch steht in Einstellungen → KI-Assistent.
- **Fehler behoben:** „Heute“ wurde in UTC berechnet, kurz nach Mitternacht galt deshalb noch der Vortag.

## 1.27.3
- KI-Schlüssel im neuen Google-Format („AQ.…“, mit Punkt) wird jetzt angenommen. Bisher wurde nur das alte Format „AIza…“ akzeptiert.

## 1.27.2
- KI-Seite: Nach „Schlüssel sichern“ steht das Ergebnis direkt unter dem Feld, und die Verbindung wird gleich getestet. Ein unvollständiger Schlüssel wird mit Hinweis abgewiesen.
- Hinweise (z. B. „Rückgängig“) erscheinen jetzt auch über geöffneten Blättern. Vorher lagen sie dahinter und waren unsichtbar.

## 1.27.1
- KI-Schlüssel: Das Feld ist jetzt ein normales, sichtbares Textfeld statt eines Passwortfelds (auf dem iPhone ließ sich dort schlecht einfügen und man sah nichts). Dazu ein Knopf „Aus Zwischenablage einfügen“; Leerzeichen, Zeilenumbrüche und Anführungszeichen werden entfernt.
- Wischen zum Schließen startet nicht mehr in Eingabefeldern, damit langes Drücken zum Einsetzen funktioniert.

## 1.27.0
Neu gestaltet nach iOS-Mustern (Apple-Richtlinien, WCAG-Kontrast):
- Kopfzeile aufgeräumt: Titel, eine Zeile Zusammenfassung, rechts nur Suche, Filter und ⋯. Sortieren, Gruppieren, Auswählen, Tags, Archiv, Export und Einstellungen stecken im ⋯-Menü (mit Untermenüs). Keine zweizeiligen Leisten mehr.
- Liste auf dem Handy als gruppierte iOS-Liste mit Ring, Titel, Metazeile und Fälligkeit.
- Alle Blätter einheitlich: oben Abbrechen · Titel · Fertig/Speichern, Felder in Gruppen, Löschen als rote Zeile unten. Notizen direkt unter dem Titel, Meilenstein als Schalter. Beim Öffnen einer bestehenden Aufgabe springt die Tastatur nicht mehr auf.
- Auswahlmodus mit drei klaren Aktionen (Status, Person, Mehr).
- Startseite: Personenwahl als Segment-Umschalter. Fortschrittsbalken bei Projekten, Tags und Personen wieder sichtbar (Fehler seit 1.18).
- Erscheinungsbild auf drei kuratierte Optionen reduziert: Darstellung, Farbwelt (Portofino, Salbei, Beere, Graphit) und Schrift (Figtree, Systemschrift, Fraunces mit Figtree). Alle Farbwelten auf Kontrast geprüft; Statusfarben bleiben überall gleich. Die freie Akzentfarbe entfällt.
- Tippflächen mindestens 44 pt, Eingabefelder mindestens 16 px (kein Zoomen beim Antippen auf dem iPhone).
- KI-Assistent: eigene Seite in den Einstellungen mit Status, Verbindungstest, Modellwahl und Feld für den Gemini-Schlüssel (wird nur auf dem Home Assistant gespeichert und nie angezeigt).
- Sicherheit: Schutz gegen DNS-Rebinding auf Port 8099 (fremde Hostnamen werden abgewiesen), zusätzliche Sicherheits-Header, strengere Prüfung von Datum, Abhängigkeiten und Checkliste, Ende vor Start wird korrigiert, mehrere Verantwortliche werden nicht mehr nach 60 Zeichen abgeschnitten.

## 1.26.1
- Aktionsblatt: Die dicken blauen Linien (Fokusrahmen) sind weg, die Felder heben sich im Dunkelmodus klarer ab, „In den Papierkorb“ ist besser lesbar.
- Dunkelmodus: Karten und Spalten im Board haben mehr Kontrast, Datumsangaben und Nebentexte sind heller.

## 1.26.0
- Deutlich flüssiger bei vielen Aufgaben: Liste und Board bauen sich etwa sechsmal schneller auf (nur sichtbare Karten werden gezeichnet), Datumsangaben werden zwischengespeichert, nach dem Speichern wird nicht mehr doppelt neu gezeichnet.
- Wischen und Ziehen blockieren das normale Scrollen nicht mehr.
- Menü beim Gedrückthalten auf drei Einträge gekürzt: Bearbeiten, Auswählen, Papierkorb. Status ändern geht per Wischen oder Tippen auf den Kreis.
- Zeitstrahl: Prio-Marke aus der schmalen Beschriftung entfernt, damit mehr vom Titel lesbar bleibt. Leerer Abstand unter „Priorität“ im Aufgaben-Dialog entfernt.

## 1.25.0
- Zeilen nach rechts wischen = erledigt (bei erledigten: wieder öffnen), nach links wischen = Papierkorb, jeweils mit Rückgängig. Gilt für die Liste und die Startseite.
- Aufgabe gedrückt halten öffnet ein Menü: Auswählen, Bearbeiten, Duplizieren, Status, Papierkorb.
- Bestätigungen (endgültig löschen, Papierkorb leeren, Tag oder Projekt löschen, Import) erscheinen als Aktionsblatt von unten.
- Aufgaben-Dialog, Einstellungen, Archiv und Tag-Verwaltung lassen sich nach unten ziehen schließen. Beim Aufgaben-Dialog fragt ein Blatt nach, wenn du etwas geändert hast.
- Nach unten ziehen aktualisiert, weiter ziehen blendet die Suche ein.
- Haptisches Feedback bei Wischen, Abhaken, Auswählen und Menü (soweit Gerät und App es zulassen).

## 1.24.0
- KI-Assistent wieder da, jetzt mit Google Gemini (kostenloser Schlüssel von aistudio.google.com/apikey, Option `gemini_api_key`). Gleiche Funktionen: Notizen und Checkliste vorschlagen, Tag-Symbole zuordnen.
- Aufgabe gedrückt halten wählt sie aus und startet die Mehrfachauswahl, weitere Aufgaben tippst du einfach an.

## 1.23.0
- Homescreen-Widget und KI-Assistent entfernt (inklusive der Optionen `anthropic_api_key` und `ai_model`). Tag-Symbole werden weiter automatisch per Stichwort zugeordnet.
- Filter-Blatt: auf dem Handy nach unten ziehen schließt es, ohne etwas zu ändern.
- Startseite zeigt zuerst deine Aufgaben („Ich bin“ in den Einstellungen). Oben wechselst du auf Melanie, eine andere Person oder Alle; die Wahl bleibt gespeichert.

## 1.22.0
- Neue Statussymbole: „In Arbeit“ ist ein halb gefüllter Kreis, „Offen“ ein leerer Ring, „Erledigt“ ein Haken. Auch die kleinen Statuspunkte (Zeitstrahl, Statusmarken) folgen dem
- Homescreen-Widget für iPhone (mit der kostenlosen App Scriptable): zeigt deine Aufgaben überfällig, heute, diese und nächste Woche. Einrichtung unter Einstellungen → Home Assistant → Homescreen-Widget (Skript kopieren). Nur Anzeige, nutzt den direkten Zugang auf Port 8099 im Heimnetz

## 1.21.0
- Erinnerungen mit Knöpfen: Die tägliche Mitteilung auf dem iPhone zeigt beim langen Drücken bis zu vier Knöpfe „Erledigt: …“ (Prio 1 zuerst). Ein Druck erledigt die Aufgabe, trägt es im Verlauf ein und aktualisiert die Mitteilung (verschwindet, wenn nichts mehr fällig ist). Ein Antippen öffnet den Planner. Wiederkehrende und blockierte Aufgaben haben keinen Knopf
- Neu: dauerhafte Verbindung des Add-ons zu Home Assistant, um die Knopfdrücke zu empfangen (verbindet sich bei Störungen von selbst neu)
- Neuer Test `tools/test_ha.py` mit nachgebautem Home Assistant

## 1.20.0
- Filter überarbeitet: Statt der langen Chip-Leiste gibt es einen Knopf „Filter“ mit Zähler. Er öffnet ein Blatt mit Projekt, Priorität, Tag und Verantwortlich (mehrere gleichzeitig wählbar, Aufgabenzahl live, „Zurücksetzen“). Aktive Filter stehen als kleine Chips unter der Leiste und lassen sich mit × entfernen. Neu: Filter „Ohne Projekt“ und „Ohne Prio“
- Projekt steht jetzt als farbige Kopfzeile über dem Titel (Board und Liste) und nicht mehr neben den Tags

## 1.19.0
- Sicherheit: Schreibzugriffe auf den Server (Aufgaben ändern, löschen, importieren, KI, Erinnerungen) funktionieren nur noch aus dem Planner selbst. Fremde Webseiten im Browser können über das Heimnetz keine Aufgaben mehr verändern oder löschen
- Sicherheit: KI-Anfragen sind auf 40 pro Stunde begrenzt, damit keine unbeabsichtigten Kosten entstehen
- Exporte und Weitergabe vollständig: Priorität und Projekt stehen jetzt in PDF, Excel (neue Spalten Projekt und Priorität am Ende) und Kalenderdatei (Priorität, Projekt als Kategorie). Das JSON-Backup enthielt sie schon
- Neuer Home-Assistant-Sensor `sensor.planner_prio1` (offene Aufgaben mit Prio 1). In der Erinnerung stehen Aufgaben mit hoher Priorität zuerst

## 1.18.2
- Karten und Liste: Projektmarken ohne überlappenden Rahmen, einheitlich mit Farbpunkt; der Prio-Randstreifen ist jetzt ein kurzer, abgerundeter Strich statt Kantenlinie
- Mehrfachauswahl („Auswählen“): zusätzlich Priorität setzen und Tag hinzufügen für alle angehakten Aufgaben

## 1.18.1
- Priorität mit Farbcodierung: Prio 1 dunkles Ziegelrot (kritisch), Prio 2 Ocker, Prio 3 Salbeigrün (nicht kritisch). Farbige Marke, Randstreifen an Karten und Listenzeilen, farbige Filter-Chips

## 1.18.0
- Neu: Priorität an Aufgaben (Prio 1, Prio 2, Prio 3, oder keine). Auswahl im Aufgaben-Dialog, kleine Marke P1/P2/P3 auf Karte, in der Liste und im Zeitstrahl, Filter-Chips neben den Tags, Sortierung nach Priorität und Gruppierung „Nach Priorität“. Alte Aufgaben ohne Priorität bleiben unverändert
- Zeitstrahl: Beschriftungsspalte reicht jetzt bis zur letzten Zeile, die senkrechten Linien laufen nicht mehr über die Titel

## 1.17.1
- Zeitstrahl im Querformat (Handy): Der Kopfbereich mit Titel, Kennzahlen und Filtern ist nicht mehr fixiert, sondern scrollt mit weg; das Diagramm bekommt so den ganzen Bildschirm

## 1.17.0
- Zeitstrahl: Die Breite der Aufgabenbeschriftung links lässt sich am Griff (kleiner senkrechter Balken im Kopf) ziehen, auch mit dem Finger. Zu lange Titel werden mit „…“ gekürzt, nie umgebrochen und laufen nicht ins Diagramm. Doppeltippen auf den Griff setzt die Breite zurück; die Breite wird auf dem Gerät gemerkt

## 1.16.1
- Vollbild in der Home-Assistant-App: Der Planner nimmt den Sicherheitsabstand der Home-Leiste selbst auf und füllt die Fläche bis zum unteren Rand, wie ein Dashboard. Die Navigationsleiste sitzt dabei über der Home-Leiste. Bei neueren Home-Assistant-Versionen meldet sich der Planner zusätzlich über deren Schnittstelle für Sicherheitsabstände an

## 1.16.0
- Erinnerung ohne Tippen: In den Einstellungen des Planners wählst du unter Home Assistant → Erinnerung die Geräte aus einer Liste (alle gefundenen Benachrichtigungsdienste, z. B. dein iPhone) und die Uhrzeit aus einer Liste. Die Auswahl wird im Add-on gespeichert und hat Vorrang vor der alten Konfiguration
- Konfiguration in Home Assistant: Die Felder Benachrichtigungsdienst und Uhrzeit entfallen; das KI-Modell ist eine Auswahlliste (Haiku, Sonnet, Opus); der Port 8099 ist vorbelegt. Nur der API-Schlüssel muss getippt werden, und nur wer die KI nutzen will

## 1.15.3
- Konfigurationsseite in Home Assistant: Alle Einstellungen haben jetzt deutsche Namen und kurze Erklärungen (Benachrichtigungsdienst, Uhrzeit der Erinnerung, Sensoren, KI-Schlüssel, KI-Modell) sowie eine verständliche Beschreibung des Ports 8099

## 1.15.2
- Handy in Home Assistant: Die App füllt ihren Bereich jetzt fest bis zum unteren Rand aus (statt über die Bildschirmhöhe des Browsers). Das soll den leeren Streifen unten bei Board und Zeitstrahl beseitigen

## 1.15.1
- Liste auf dem Handy: Zeilen haben wieder Abstand und kleben nicht mehr aneinander; die Filter-Pillen liegen in einer eigenen Zeile und werden nicht mehr vom „Gruppieren“-Knopf überdeckt
- Die Auswahl „Form“ ist aus den Einstellungen entfernt; es gilt wieder durchgehend die flache Darstellung

## 1.15.0
- Technische Umbenennung: Slug, Ordner und Sensor-IDs heißen jetzt `planner` (Sensoren: `sensor.planner_offen`, `_in_arbeit`, `_ueberfaellig`, `_heute_faellig`); der Spiegel liegt unter `share/planner/`
- Für Home Assistant ist das ein neues Add-on: beim ersten Start übernimmt es Aufgaben, Tags und Dateianhänge automatisch aus dem alten Spiegel `share/haus_planer/`
- Exportdateien heißen jetzt `planner-…`

## 1.14.0
- Die App heißt jetzt „Planner“ (Titel, Startbild, Seitenleiste, App-Symbol, Exporte, Erinnerungen, Sensornamen). Slug, Datenordner und Sensor-IDs (`sensor.haus_planner_*`) bleiben unverändert, Daten und Automationen funktionieren weiter

## 1.13.1
- Handy: Die App nutzt den Bildschirm besser aus. Eingebettet in Home Assistant wurden die Sicherheitsabstände von Notch und Home-Leiste doppelt gerechnet (große Lücke oben und unten); das ist behoben
- Kompaktere Abstände auf dem Handy, Spalten im Board etwas breiter (92 %)

## 1.13.0
- Neu in den Einstellungen: „Form“ mit 11 Varianten (Flach, Schichten, Inseln, Redaktion, Bento, Zuschnitt, Kapsel, Ton, Kontrast, Mineral, Schiefer); sie ändern Karten, Spalten, Kennzahlen und Seitenleiste, unabhängig vom Farbdesign
- Drei neue Farbdesigns: Salbei, Tinte, Nacht (jeweils auch dunkel)
- Standard bleibt „Flach“, bestehende Einstellungen ändern sich nicht

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
