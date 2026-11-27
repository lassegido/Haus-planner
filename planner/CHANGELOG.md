# Änderungen

## 1.51.0
- **Filter „Verantwortlich“ mit Mehrfachauswahl**, wie bei Tag, Projekt und Priorität: z. B. Lasse und Melanie gleichzeitig. Gilt auch für „Wer“ in der Seitenleiste; „Alle“ setzt zurück.
- **Startseite:** Von den Filtern gilt hier nur „Verantwortlich“. Tag, Projekt, Priorität und Suche wirken auf Start nicht. Ist der Personenfilter aktiv, zeigen die Knöpfe oben (Meine · Melanie · Alle) genau diese Auswahl und schalten sie um.
- **Kennzahlen passen immer zum Filter:** % erledigt, in Arbeit, überfällig und blockiert in Liste, Board, Zeitstrahl und Kalender zählen nur die gefilterten Aufgaben. Auf dem Handy steht in der Zeile darunter „(gefiltert)“.

## 1.50.0
- **Abhängigkeiten planen automatisch:** Eine Aufgabe startet frühestens am Tag nach dem Ende aller offenen Vorgänger. Beim Verknüpfen, beim Verlängern oder Verschieben eines Vorgängers rücken die Nachfolger (und deren Nachfolger) mit, die Dauer bleibt gleich. Wer eine Aufgabe zu früh legt, wird an den frühesten möglichen Tag gesetzt; ein Hinweis sagt, was verschoben wurde. Erledigte Vorgänger bremsen nicht mehr.
- **Zeitstrahl: kürzer oder länger ziehen:** Jeder Balken hat links und rechts einen sichtbaren Griff. Links ziehen ändert den Start, rechts das Ende. Mit dem Finger geht das sofort, ohne vorher gedrückt zu halten. Der Punkt zum Verknüpfen sitzt jetzt etwas außerhalb des Balkens, damit er sich nicht mit dem rechten Griff ins Gehege kommt.
- **Korrektur:** Der Schalter „Meilenstein“ im Aufgabenblatt war nur ein kleiner Kreis und ist wieder ein richtiger Schalter.

## 1.49.0
- **Zeitstrahl: in eine andere Gruppe ziehen.** Ist der Zeitstrahl gruppiert (⋯ → Gruppieren: Projekt, Tag, Person, Priorität), übernimmt eine Aufgabe die Gruppe, in die man sie zieht:
  - Projekt wird gesetzt bzw. entfernt („Ohne Projekt“).
  - Bei Tag wird der bisherige Gruppen-Tag ersetzt, die übrigen Tags bleiben.
  - Bei Person wird die bisherige Person getauscht.
  - Bei Priorität wird die neue Priorität gesetzt.
  - Die Ziel-Gruppe leuchtet beim Ziehen auf, „Rückgängig“ stellt alles wieder her.
- **So geht's:** links an den zwei Strichen ziehen, oder den Balken selbst nach oben/unten ziehen. Beim Balken lässt sich gleichzeitig das Datum nach links/rechts ändern.

## 1.48.0
- **Zeitstrahl: Verknüpfungen gut sichtbar.** Pfeile in der Akzentfarbe mit runden Ecken. Pfeil antippen → „Verknüpfung lösen“.
- **Verknüpfen wie im Microsoft Planner:**
  - Am Punkt am Balkenende ziehen und auf die Aufgabe loslassen, die danach kommt. Das geht jetzt auch mit dem Finger auf dem iPad; der Punkt ist dort immer sichtbar und hat eine große Greiffläche.
  - Alternativ: Balken gedrückt halten → „Verknüpfen mit …“ → Ziel-Aufgabe antippen.
  - Kreise (A nach B nach A) werden verhindert.
- **Reihenfolge ändern:** Links an den zwei Strichen ziehen und nach oben oder unten schieben (eine Linie zeigt, wo die Aufgabe landet). Oder gedrückt halten → „↑ Nach oben“ / „↓ Nach unten“. Danach gilt „Eigene Reihenfolge“, auch in Liste und Board (umstellbar unter ⋯ → Sortieren).
- **Gedrückt halten im Zeitstrahl** (Balken oder Zeile; am Computer Rechtsklick): Bearbeiten, Verknüpfen, **Zu Projekt hinzufügen** (bestehendes oder neues), **Notiz hinzufügen**, Reihenfolge, Nicht geschafft, Papierkorb.

## 1.47.0
- **Startseite: Ring zählt nur, was heute fällig ist** (und Überfälliges). Aufgaben, die heute laufen, aber erst später fällig sind, zählen nicht mehr. Wird eine heute fällige Aufgabe auf später verschoben, ist sie aus dem Ring raus.
- **„Heute“ ist zweigeteilt:** oben „Heute fällig“, darunter „Läuft heute, fällig später“ (etwas blasser).
- **Kein Springen beim Abhaken:** Nach dem Antippen des Kreises (Offen → In Arbeit → Erledigt) bleibt die Seite an derselben Stelle, vor allem auf der Startseite. Ursache war, dass das GIF bei jedem Neuzeichnen neu geladen wurde und Zeilen ihre Höhe erst verzögert bekommen; dabei hat iOS die Scrollposition nach oben gezogen.

## 1.46.0
- **Planen:** Im Kalender oben „Monat | Planen“ umschalten.
  - Zeitraum 1, 2 oder 5 Wochen ab Montag, mit ‹ › wochenweise vor und zurück und „Heute“. Jeder Tag zeigt, wie viele Aufgaben offen sind; ab 4 färbt sich die Zahl orange.
  - Auf iPad und Computer stehen die Tage als Wochen nebeneinander (Mo bis So), auf dem Handy untereinander.
- **Verschieben:** Am Griff (sechs Punkte) ziehen, auf Tag oder Sammelkorb loslassen. Oder den Griff antippen und dann den Ziel-Tag antippen, das geht auf dem Handy am leichtesten. Mehrtägige Aufgaben behalten ihre Dauer. Jede Verschiebung lässt sich unten rückgängig machen.
- **Sammelkorb:** Aufgaben ohne festen Tag schnell nacheinander eintippen (Enter, die Eingabe bleibt offen), später auf Tage verteilen. Sie zählen nirgends als fällig oder überfällig: nicht auf der Startseite, nicht in Liste, Board, Zeitstrahl und Monatskalender, nicht in Erinnerungen und bei Alexa.
- **Liegen geblieben:** Überfällige Aufgaben stehen beim Planen unter dem Sammelkorb und lassen sich direkt auf einen neuen Tag ziehen.
- **Plus an jedem Tag:** legt direkt an diesem Tag an. Kurzschreibweise wie in der Schnelleingabe (#Tag, @Person, !1).

## 1.45.1
- Korrektur: Ist heute nichts fällig, steht wieder „Heute ist nichts fällig. Genieß den freien Tag.“ statt „Mittag, und noch alle 0 offen …“.

## 1.45.0
- **Startseite: GIF und Satz passen sich der Tageszeit an.** Jede Lage hat ihr eigenes GIF des Tages, über den Tag gibt es also mehrere.
  - **Morgens** (bis 11 Uhr), noch nichts erledigt: „8 Aufgaben heute. Klingt viel, du schaffst das.“ Schon etwas erledigt: „Starker Start.“
  - **Mittags** (bis 17 Uhr), noch nichts erledigt: „Mittag, und noch alle 8 offen. Willst du nicht mal loslegen?“ Gut dabei: „Du bist auf einem guten Weg.“
  - **Abends**, noch (fast) alles offen, bewusst frech-ironisch: „Digga, du wirst es vermasseln … oder?“, mit GIFs wie „This is fine“. Gut dabei: „Endspurt, das ziehst du durch.“
  - **Ab 70 % erledigt**, egal wann: „Du hast es fast geschafft.“
  - Wie bisher: alles erledigt, etwas überfällig, mehrere Tage am Stück.
- Gemini schlägt einmal am Tag passende bestehende Memes für alle 12 Lagen vor (weiterhin nur eine Anfrage pro Tag). Nach dem Update wird die heutige Auswahl einmal neu geholt.

## 1.44.0
- **Startseite: „Morgen“ statt „7 Tage“.** Der Umschalter zeigt jetzt, was morgen anfängt oder fällig ist. Wiederholungen (z. B. tägliche Aufgaben) entstehen erst, wenn die heutige abgehakt ist; bis dahin stehen sie blass mit gestricheltem Kreis als Vorschau dabei („wiederholt sich, sobald heute abgehakt“). Lange laufende Aufgaben, die morgen weder anfangen noch enden, fehlen bewusst.

## 1.43.0
- **Startseite auf iPad und Computer:** Spruch und GIF stehen jetzt rechts neben Ring und Zahlen statt darunter. Das GIF wird dadurch deutlich größer, und die Tageskarte ist kompakter. Auf dem Handy bleibt alles untereinander.

## 1.42.0
- **„Nicht geschafft“:** Wenn eine Aufgabe, z. B. eine tägliche, nicht klappt, kann man sie damit abschließen. Das geht über Gedrückt halten → „Nicht geschafft“ oder im Aufgabenblatt beim Status. Danach ist sie nicht mehr offen und es kommt keine Erinnerung mehr. Wiederholt sie sich, wird die nächste wie gewohnt angelegt. „Rückgängig“ im Hinweis unten macht es wieder offen.
  - Sie zählt **nicht** als erledigt (Ring, Prozent, Abzeichen, gemeinsame Woche) und **beendet die Serie** sofort („Serie startet morgen neu“).
  - Sie wird mit ✕ statt Haken und dem Hinweis „Nicht geschafft“ angezeigt.
- **„BUSTED!“:** Wer auf der Startseite „Nicht geschafft“ wählt, bekommt einmal groß einen Stempel „BUSTED!“ mit Ausrufezeichen. Er verschwindet nach gut 2 Sekunden von selbst; Antippen schließt ihn sofort. Das passiert nur auf der Startseite und nur bei der Person, die es antippt. Mit „Sprüche, GIFs und Konfetti“ aus bleibt er weg.
- **Board:** Erledigte und nicht geschaffte Aufgaben stehen jetzt nach dem Zeitpunkt des Abschließens sortiert, das zuletzt Abgehakte ganz oben. Versehentlich Abgehaktes findet man so sofort wieder.
- **„Tafel“ heißt wieder „Board“.**
- Korrektur: Ist „Sprüche, GIFs und Konfetti“ aus, kommt auch kein Konfetti (seit 1.41).

## 1.41.0
- **Fünf neue Farbwelten im Stil von Polarlicht:** getönte Flächen, kräftige Leiste, Akzent mit Verlauf und eigener Ring-Farbe, jeweils für Hell und Dunkel.
  - **Wald:** Smaragd bis Moos
  - **Lagune:** Türkis bis Kobalt
  - **Orchidee:** Violett bis Magenta
  - **Feige:** Aubergine bis Altrosa auf warmem Sand
  - **Schiefer:** kühles Grau mit Tinte bis Petrol, für alle, die es sachlich mögen
- **Salbei, Beere und Graphit entfallen**, weil sie flach wirkten und kaum Verlauf hatten. Wer eine davon gewählt hatte, bekommt beim nächsten Öffnen automatisch den Nachfolger (Salbei → Wald, Beere → Orchidee, Graphit → Schiefer).
- Jetzt 7 Farbwelten: Portofino (Standard), Polarlicht, Wald, Lagune, Orchidee, Feige, Schiefer. Alle bestehen die Kontrastprüfung in Hell und Dunkel; keine hat eine rote, orange oder gelbe Akzentfarbe, damit nichts wie ein Status aussieht.
- **Korrektur:** Ist „Sprüche, GIFs und Konfetti“ ausgeschaltet, kommt jetzt auch kein Konfetti mehr. Der kurze Glückwunsch bleibt.

## 1.40.0
- **Statt „Warum dieses GIF?“ ein Satz, der motiviert** und den Grund nur andeutet, z. B. „Eine Sache ist liegen geblieben. Die holst du dir jetzt zurück.“, „2 geschafft, nur noch eine. Du bist richtig drin.“ oder „Alle 3 erledigt. Das hast du dir verdient.“
- **Mehr Tiefe in allen Ansichten, ohne Spielerei:** Karten, Kästen und Listen liegen mit weichem Schatten und feiner Lichtkante auf, die Seite hat einen kaum sichtbaren Farbschimmer. Verläufe nur auf Akzentflächen: Ring (jetzt über drei Farben), Hauptknöpfe, Neu-Knopf, Leiste unten bzw. Seitenleiste. Tafel-Spalten oben leicht in ihrer Statusfarbe getönt, Balken im Zeitstrahl und Fortschrittsbalken mit leichtem Glanz, Kalender-Einträge mit Lichtkante. Karten heben sich am Computer beim Darüberfahren leicht an.
- **Neue Farbwelt „Polarlicht“ zum Ausprobieren:** Indigo mit Verlauf nach Petrol, hell und dunkel. Einstellungen → Farbwelt. Jede Farbwelt hat jetzt einen zweiten Akzent für die Verläufe.
- Umschalter (Meine · Melanie · Alle, Heute · 7 Tage …) passen sich der Farbwelt an (vorher überall beige) und sind besser lesbar: nicht gewählte Einträge haben jetzt genug Kontrast (vorher 4,2 : 1, jetzt über 5 : 1).
- Wartung: 33 nicht mehr genutzte CSS-Regeln entfernt (ohne sichtbare Änderung, mit `style_diff` geprüft). Neuer Test prüft den Kontrast aller Farbwelten automatisch.

## 1.39.0
- **Tageskarte lebendiger, aber ruhig:** sanfter Farbverlauf mit langsam wandernden Lichtflecken, der Ring füllt sich beim Öffnen mit Farbverlauf, die Flamme flackert leicht, das GIF blendet weich ein. Mit „Bewegung reduzieren“ in iOS steht alles still.
- Kompakter: „4 Tage am Stück“ und „3 diese Woche +2“ als zwei kleine Marken.
- Unter dem GIF steht nichts mehr (kein Name, kein „über GIPHY“); die Begründung darüber ist kürzer.

## 1.38.0
- **„Warum dieses GIF?“** steht jetzt über dem GIF, z. B. „Eine Aufgabe ist liegen geblieben. Hol sie auf, dann wechselt das GIF.“ oder „Du hast heute schon 2 Aufgaben erledigt, 3 sind noch offen.“
- **GIF wechselt mit dem Stand:** Ist eine Lage gelöst (z. B. Überfälliges erledigt), kommt sofort ein neues, passendes GIF. Reihenfolge: alles erledigt → etwas liegen geblieben → schon etwas geschafft → Serie läuft → noch nichts.
- **Eine Botschaft pro Karte:** Die Startseite motiviert immer. Memes über Scheitern („Wasted“, „This is fine“, Game over …) werden nicht mehr gezeigt, auch nicht, wenn Gemini sie vorschlägt; ein bereits gespeichertes wird ersetzt. Bei Liegengebliebenem kommen jetzt Comeback-Memes.

## 1.37.0
- **Kein GIF mehr zum Wegklicken:** Beim Öffnen erscheint nichts mehr vor der Seite. Das Meme steht in der Tageskarte; groß kommt es nur beim Antippen oder wenn die letzte Aufgabe des Tages erledigt ist.
- **Startseite als ein Weg von oben nach unten:**
  1. **Ankommen:** eine Karte mit Begrüßung, Tagesstand, Serie, Woche und dem Meme passend zum Tag.
  2. **Handeln:** direkt darunter die Eingabe, dann ein schmaler Umschalter Heute · 7 Tage · In Arbeit · Überfällig (ersetzt die vier großen Kacheln) und die Liste.
  3. **Dranbleiben:** das nächste Abzeichen in einer Zeile.
  4. **Überblick:** Projekte, Tags, Personen und die gemeinsame Woche, zugeklappt ganz unten.
- „Als Nächstes“ entfällt, weil die erste Zeile der Liste genau das ist.

## 1.36.0
- **Startseite folgt jetzt einer klaren Reihenfolge:**
  1. **Dein Tag:** Stand mit Ring, „4 Tage am Stück“, „3 diese Woche · 2 mehr als letzte“ und darunter **Als Nächstes**: die eine Aufgabe, die jetzt dran ist, direkt zum Abhaken.
  2. **Meme zur Lage:** Das GIF ist jetzt vollständig und groß zu sehen (vorher abgeschnitten), mit einer deutschen Beschreibung darunter.
  3. **Nächstes Abzeichen:** in Worten, z. B. „Erste 10 – noch 2 Aufgaben“; antippen zeigt alle.
  4. Danach wie gewohnt Kacheln, Eingabe und Liste; „Gemeinsam diese Woche“ ganz unten.
- **Durchgehend natürliches Deutsch:** „Tafel“ statt „Board“, „Sicherung“ statt „Backup“, „Wer“ und „Beginn“ in Tabellen und Excel, Meldungen umformuliert (z. B. „Diese Woche 3 erledigt, 2 mehr als letzte Woche“, „Schlüssel wird gesichert und geprüft …“). Meme-Beschreibungen auf Deutsch, auch bei der täglichen Auswahl durch Gemini. Abzeichen heißen jetzt u. a. „Eine Woche durchgezogen“ und „Gemeinsam stark“.

## 1.35.0
- **Startseite neu sortiert:** Ganz oben steht jetzt deine persönliche Spiel-Karte: Tagesring, Serie, „x diese Woche“, Spruch mit GIF und Abzeichen. Danach folgen Kacheln, Eingabe und Liste. „Gemeinsam diese Woche“ ist ganz nach unten gewandert.
- **Echte Memes als GIF je Lage (GIPHY):** Es werden nur bestehende, bekannte Memes gezeigt, nichts erfunden. Zu jeder Lage (alles erledigt, Serie, überfällig, noch nichts, halb geschafft) gibt es höchstens ein GIF am Tag, für alle gleich. Es erscheint einmal kurz groß und bleibt dann klein mit dem Namen des Memes in der Karte. Ändert sich die Lage (z. B. letzte Aufgabe erledigt), kommt das passende GIF.
- **Auswahl durch Gemini:** Einmal am Tag schlägt Gemini zu jeder Lage bekannte Memes aus euren Themen vor (eine Anfrage, nur wenn weniger als die Hälfte des Tageslimits verbraucht ist); sonst gilt eine eingebaute Auswahl. Eigene Suchbegriffe lassen sich ergänzen. Die selbst geschriebenen Sprüche gibt es nur noch, solange kein GIPHY-Schlüssel eingetragen ist.
- Für GIFs braucht es einen kostenlosen GIPHY-Schlüssel (Einstellungen → Sprüche und GIFs).
- **Abzeichen mit Fortschritt:** Die Karte zeigt die freigeschalteten Abzeichen und das nächste mit Balken (z. B. „Erste 10 · 8/10“). Antippen klappt alle Abzeichen mit ihrem Stand auf.
- Sprüche und GIFs lassen sich je Person abschalten (Einstellungen → Nur für dich → Sprüche und GIFs).

## 1.34.0
- **Motivation auf der Startseite:**
  - **Serie:** Die Flamme zählt die Tage in Folge, an denen alles für den Tag erledigt war. Tage ohne Fälliges unterbrechen sie nicht, mehr als 7 Tage ganz ohne Erledigtes schon.
  - **Gemeinsam diese Woche:** Erledigte Aufgaben seit Montag mit dem Anteil jeder Person und dem Vergleich zur Vorwoche. Wer erledigt hat, kommt aus dem Verlauf.
  - **10 Abzeichen:** z. B. Erste 10, Eine Woche dran, Weiße Weste, Projekt geschafft, Frühstarter. Antippen erklärt das Abzeichen.
  - **Feiern:** Ist die letzte Aufgabe des Tages erledigt, gibt es Konfetti und eine kurze Vibration; neue Abzeichen werden gemeldet.
  - **Sprüche** passend zur Lage (alles erledigt, Serie, überfällig, noch nichts, halb geschafft): Popkultur, Gaming, Fußball, Tiere, Polit-Satire, locker formuliert. Mit Gemini-Schlüssel erneuert der Planner sie einmal am Tag (genau eine Anfrage und nur, wenn weniger als die Hälfte des Tageslimits verbraucht ist), sonst eingebaute Sprüche. Nur auf der Startseite; Liste, Board, Zeitstrahl und Kalender bleiben sachlich.
- **Wiederholen mit mehr Möglichkeiten:**
  - Schnellauswahl: Täglich, Werktags (Mo–Fr), Wöchentlich, Alle 2 Wochen, Monatlich, Vierteljährlich, Jährlich.
  - **Benutzerdefiniert:** alle n Tage, Wochen, Monate oder Jahre; bei Wochen bestimmte Wochentage (z. B. Di und Do); bei Monaten am selben Tag oder am n-ten Wochentag (z. B. 1. Dienstag, letzter Freitag); optional ein Enddatum.
  - Bestehende Wiederholungen bleiben unverändert.
- **Leiste unten neu sortiert:** Start, Liste, Board, Zeitstrahl, Kalender (auch die Tasten 1–5 am Mac).

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
