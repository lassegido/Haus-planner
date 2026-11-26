# Prüfliste für echte Geräte

Die automatischen Tests (`tools/check.py`) laufen in Chromium mit nachgebautem Home Assistant, Gemini und Alexa. Was dort nicht prüfbar ist, steht hier. Nach größeren Updates einmal durchgehen; Fehler mit Bildschirmfoto und den Zeilen „Browser-Fehler“ aus dem Add-on-Protokoll melden.

Zuletzt vollständig geprüft: _noch nie_ (Version: –)

## 1. Start und Aussehen (iPhone, HA-App)
- [ ] Unter ⋯ → Export und Backup steht unten die neue Version.
- [ ] Schrift sieht aus wie vorher (Figtree; bei Wahl „Fraunces und Figtree“ Serifen-Überschriften).
- [ ] App startet spürbar nicht langsamer als vorher.
- [ ] Hell und Dunkel: Texte gut lesbar, keine weißen Flächen im Dunkelmodus.

## 2. Gesten (iPhone)
- [ ] Karte oder Zeile gedrückt halten: Menü mit höchstens vier Einträgen (bei offenen Aufgaben auch „Nicht geschafft“), **kein** markierter Text, keine Lupe.
- [ ] Liste: nach rechts wischen = erledigt, nach links = Papierkorb.
- [ ] Liste ganz oben nach unten ziehen: aktualisiert; weiter ziehen: Suche öffnet sich.
- [ ] Blätter (Aufgabe, Filter, Einstellungen) nach unten wischen: schließt; bei Änderungen kommt die Rückfrage.
- [ ] Filter-Blatt: nach unten wischen setzt keinen Filter.
- [ ] Checkliste: Punkt am Griff (sechs Punkte) gedrückt halten und verschieben.

## 3. Aufgabenblatt
- [ ] „Wiederholen und Abhängigkeiten“ öffnen, im Suchfeld z. B. „garten“ tippen: nur passende Aufgaben, Zähler „x von y“.
- [ ] Haken setzen, Suche ändern: gewählte Aufgabe bleibt sichtbar. Speichern: Abhängigkeit ist gespeichert.
- [ ] Beim Tippen ins Suchfeld zoomt das iPhone nicht hinein.

- [ ] Neue Aufgabe, Titel anfangen („Ras…“): frühere Aufgaben erscheinen; Antippen füllt alles aus, „Rückgängig“ unten lässt sich antippen.
- [ ] Startseite: „Rasen…“ tippen, Vorschlag antippen: Blatt öffnet sich ausgefüllt, Tastatur bleibt zu.

- [ ] Wiederholen → Benutzerdefiniert: Wochentage antippen (Di, Do), „Alle 2“ eingeben, Enddatum wählen; Hinweis darunter stimmt. Beim Erledigen entsteht die nächste am richtigen Tag.
- [ ] Startseite: Serie mit Flamme, „Gemeinsam diese Woche“ mit beiden Namen, Abzeichen antippen. Letzte Aufgabe des Tages abhaken: Konfetti und Vibration.
- [ ] Leiste unten: Start, Liste, Board, Zeitstrahl, Kalender.
- [ ] GIPHY-Schlüssel eintragen: GIF erscheint kurz groß, danach klein in der Karte; auf dem zweiten iPhone dasselbe GIF. Antippen zeigt es wieder.
- [ ] Startseite: Beim Öffnen nichts zum Wegklicken. Tageskarte mit Meme, darunter Eingabe, Umschalter und Liste ohne Scrollen erreichbar. Letzte Aufgabe abhaken: Meme groß und Konfetti.
- [ ] Über dem GIF steht ein kurzer Satz (z. B. „2 geschafft, nur noch eine. Du bist richtig drin.“), keine Frage „Warum dieses GIF?“.
- [ ] Hell und Dunkel: Karten, Liste und Board wirken leicht plastisch (Schatten, Lichtkante), nichts sieht verwaschen oder grell aus; Ring-Verlauf gut sichtbar.
- [ ] Einstellungen → Farbwelt: alle 7 durchtippen (Portofino, Polarlicht, Wald, Lagune, Orchidee, Feige, Schiefer), jeweils Hell und Dunkel gut lesbar.
- [ ] Wer vorher Salbei, Beere oder Graphit hatte: nach dem Update Wald, Orchidee bzw. Schiefer, auch auf dem zweiten Gerät.
- [ ] „Sprüche, GIFs und Konfetti“ aus, letzte Aufgabe abhaken: kein Konfetti, nur der kurze Hinweis.
- [ ] Zeitstrahl: Balken ziehen und an den Enden verlängern funktioniert wie vorher (Glanz liegt nur darüber).
- [ ] Startseite: Aufgabe gedrückt halten → „Nicht geschafft“: großes „BUSTED!“, verschwindet von selbst, Vibration; Ring zählt sie nicht als erledigt, Serie „startet morgen neu“. Tägliche Aufgabe: die von morgen ist da.
- [ ] Dasselbe in der Liste oder im Board: kein „BUSTED!“. Auf dem anderen iPhone auch nicht.
- [ ] Board: zuletzt Abgehaktes steht in „Erledigt“ ganz oben; nicht Geschafftes mit ✕.
- [ ] iPad hochkant und quer: GIF rechts neben dem Ring, gut groß; iPhone: GIF darunter.
- [ ] Startseite → „Morgen“: morgige Aufgaben, tägliche als blasse Vorschau; nach dem Abhaken der heutigen steht die echte da, nicht doppelt.
- [ ] Am Tag nach dem Update: Spruch auf der Startseite kommt von Gemini (neu formuliert), KI-Verbrauch in den Einstellungen nur +1.

## 4. Export (iPhone)
- [ ] PDF: Teilen-Menü erscheint, PDF lässt sich in Dateien sichern oder per Mail senden.
- [ ] Excel: ebenso; Datei öffnet sich in Numbers oder Excel.
- [ ] Backup (JSON): ebenso.

## 5. Benutzer, Startseite und Erinnerungen
- [ ] Startseite mit „Meine“: Ring zeigt „Heute: x von y erledigt“ nur mit euren heutigen und überfälligen Aufgaben; nach dem Abhaken steigt die Zahl.
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
