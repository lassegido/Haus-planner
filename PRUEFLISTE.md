# Prüfliste für echte Geräte

Die automatischen Tests (`tools/check.py`) laufen in Chromium mit nachgebautem Home Assistant, Gemini und Alexa. Was dort nicht prüfbar ist, steht hier. Nach größeren Updates einmal durchgehen; Fehler mit Bildschirmfoto und den Zeilen „Browser-Fehler“ aus dem Add-on-Protokoll melden.

Zuletzt vollständig geprüft: _noch nie_ (Version: –)

## 1. Start und Aussehen (iPhone, HA-App)
- [ ] Unter ⋯ → Export und Backup steht unten die neue Version.
- [ ] Schrift sieht aus wie vorher (Figtree; bei Wahl „Fraunces und Figtree“ Serifen-Überschriften).
- [ ] App startet spürbar nicht langsamer als vorher.
- [ ] Hell und Dunkel: Texte gut lesbar, keine weißen Flächen im Dunkelmodus.

## 2. Gesten (iPhone)
- [ ] Karte oder Zeile gedrückt halten: Menü mit höchstens drei Einträgen, **kein** markierter Text, keine Lupe.
- [ ] Liste: nach rechts wischen = erledigt, nach links = Papierkorb.
- [ ] Liste ganz oben nach unten ziehen: aktualisiert; weiter ziehen: Suche öffnet sich.
- [ ] Blätter (Aufgabe, Filter, Einstellungen) nach unten wischen: schließt; bei Änderungen kommt die Rückfrage.
- [ ] Filter-Blatt: nach unten wischen setzt keinen Filter.
- [ ] Checkliste: Punkt am Griff (sechs Punkte) gedrückt halten und verschieben.

## 3. Aufgabenblatt
- [ ] „Wiederholen und Abhängigkeiten“ öffnen, im Suchfeld z. B. „garten“ tippen: nur passende Aufgaben, Zähler „x von y“.
- [ ] Haken setzen, Suche ändern: gewählte Aufgabe bleibt sichtbar. Speichern: Abhängigkeit ist gespeichert.
- [ ] Beim Tippen ins Suchfeld zoomt das iPhone nicht hinein.

## 4. Export (iPhone)
- [ ] PDF: Teilen-Menü erscheint, PDF lässt sich in Dateien sichern oder per Mail senden.
- [ ] Excel: ebenso; Datei öffnet sich in Numbers oder Excel.
- [ ] Backup (JSON): ebenso.

## 5. Benutzer und Erinnerungen
- [ ] Melanie öffnet den Planner auf ihrem iPhone: „Ich bin“ = Melanie, eigene Farbwelt. Lasses Farbwelt bleibt unverändert.
- [ ] Tägliche Erinnerung: Lasse bekommt nur seine Aufgaben und solche ohne Zuständigkeit, Melanie ebenso.
- [ ] Knopf „Erledigt: …“ in der Mitteilung hakt die Aufgabe ab.

## 6. KI (mit echtem Gemini-Schlüssel)
- [ ] Aufgabenblatt → KI-Vorschlag kommt in wenigen Sekunden.
- [ ] Eigenen Hinweis eingeben („Wände sind schon fertig“) → Neu vorschlagen berücksichtigt ihn.
- [ ] Einstellungen → KI zeigt den Tagesverbrauch.

## 7. Alexa und Echo Show
- [ ] „Alexa, Planner Rasen mähen morgen Tag Garten“ legt die Aufgabe an, der Echo bestätigt.
- [ ] „Alexa, Planner was steht heute an“ liest vor.
- [ ] „Alexa, Planner Rasen mähen ist erledigt“ hakt ab.
- [ ] Echo Show 5: Link aus Einstellungen → Anzeige für Echo Show zeigt die Übersicht ohne Scrollen.

## 8. Protokoll
- [ ] Add-on-Protokoll nach einem Tag Nutzung: keine oder nur vereinzelte Zeilen „Browser-Fehler“.
