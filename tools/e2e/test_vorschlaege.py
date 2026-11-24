"""Vorschläge aus früheren Aufgaben (Titel) und der Ring auf der Startseite (nur heute, gewählte Person)."""
import datetime
from common import PHONE, Page, Server, task

T = datetime.date.today()
D = lambda n: str(T + datetime.timedelta(n))
NOW_UTC = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M")
ALS_LASSE = lambda pg: pg.add_init_script("try{localStorage.setItem('haus-me','Lasse')}catch(e){}")
SUG = "[...document.querySelectorAll('%s .vsg b')].map(b=>b.textContent)"
VORLAGEN = [
    task("r1", "Rasen mähen", D(-40), D(-39), tags=["Garten"], who="Lasse", prio=1, notes="alt"),
    task("r2", "Rasen mähen", D(-10), D(-9), tags=["Garten"], who="Lasse", prio=2, notes="Kanten nicht vergessen", status="done",
         rec={"n": 1, "u": "w"}, checklist=[{"t": "Benzin prüfen", "d": True}, {"t": "Schnittgut entsorgen", "d": True}], deps=["f1"],
         log=[{"t": "2026-01-01T10:00", "a": "Lasse", "k": "c", "x": "alter Kommentar"}]),
    task("r3", "Rasenmäher warten", D(-100), D(-100)),
    task("r4", "Rasen düngen", D(-5), D(-5), **{"del": True, "delAt": D(-1)}),
    task("r5", "Rasenkanten schneiden", D(-200), D(-200), arch=True),
    task("f1", "Fenster putzen", D(-3), D(-3)),
]


def test_vorschlaege_im_aufgabenblatt(t, browser):
    with Server() as s:
        s.seed(VORLAGEN, tags=[{"n": "Garten", "c": "mint"}])
        p = Page(browser, s.url, PHONE)
        pg = p.pg
        pg.click("#add")
        pg.wait_for_timeout(300)
        pg.type("#f_title", "ras", delay=15)
        got = p.js(SUG % "#f_sug")
        t.check("Vorschläge beim Tippen: gleicher Anfang, gleiche Titel nur einmal, Papierkorb nicht",
                sorted(got) == ["Rasen mähen", "Rasenkanten schneiden", "Rasenmäher warten"] and got[0] == "Rasen mähen", got)
        meta = p.js("document.querySelector('#f_sug .vsg small').textContent")
        t.check("Vorschlag zeigt die jüngste Aufgabe mit diesem Titel", "2 Punkte" in meta and "wiederholt" in meta, meta)
        pg.fill("#f_title", "putz")
        p.js("document.getElementById('f_title').dispatchEvent(new Event('input'))")
        t.check("Treffer auch bei einem Wort im Titel", p.js(SUG % "#f_sug") == ["Fenster putzen"])
        pg.fill("#f_title", "")
        pg.type("#f_title", "Rasen m", delay=15)
        pg.click("#f_sug .vsg")
        pg.wait_for_timeout(300)
        st = p.js("""({title:f_title.value,tags:selTags,who:selWho,prio:f_prio.value,rec:f_rec.value,start:f_start.value,end:f_end.value,
                     notes:f_notes.value,ck:cklist.map(c=>[c.t,c.d]),sug:f_sug.innerHTML,deps:[...document.querySelectorAll('#f_deps input:checked')].length})""")
        t.check("Auswahl übernimmt Titel, Tag, Person, Priorität, Wiederholung, Notizen",
                st["title"] == "Rasen mähen" and st["tags"] == ["Garten"] and st["who"] == ["Lasse"] and st["prio"] == "2"
                and st["rec"] == "1w" and st["notes"] == "Kanten nicht vergessen", st)
        t.check("Checkliste übernommen, alle Punkte wieder offen", st["ck"] == [["Benzin prüfen", False], ["Schnittgut entsorgen", False]], st["ck"])
        t.check("Datum: ab heute mit gleicher Dauer (2 Tage)", st["start"] == D(0) and st["end"] == D(1), (st["start"], st["end"]))
        t.check("Abhängigkeiten werden nicht übernommen, Vorschläge verschwinden", st["deps"] == 0 and st["sug"] == "")
        t.check("Hinweis mit Rückgängig erscheint", "übernommen" in (pg.text_content("#toast") or ""))
        pg.click("#toast button")
        pg.wait_for_timeout(200)
        t.check("Rückgängig stellt das leere Blatt mit dem Getippten wieder her", p.js("[f_title.value,selTags.length,cklist.length]") == ["Rasen m", 0, 0])
        p.js("document.getElementById('f_title').dispatchEvent(new Event('input'))")
        pg.click("#f_sug .vsg")
        pg.click("#b_save")
        pg.wait_for_timeout(700)
        new = [x for x in s.tasks() if x["title"] == "Rasen mähen" and x["id"] not in ("r1", "r2")]
        n = new[0] if new else {}
        t.check("Gespeichert als neue, offene Aufgabe ohne alten Verlauf", len(new) == 1 and n.get("status") == "todo" and not n.get("log")
                and n.get("deps") in (None, []) and n.get("rec") == {"n": 1, "u": "w"}, n)
        t.check("Alte Aufgabe bleibt unverändert", s.task("r2")["status"] == "done" and s.task("r2")["checklist"][0]["d"] is True)
        p.js("openDlg('f1')")
        pg.wait_for_timeout(300)
        pg.type("#f_title", " ras", delay=15)
        t.check("Beim Bearbeiten keine Vorschläge", p.js("document.getElementById('f_sug').innerHTML") == "")
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_vorschlaege_in_der_schnelleingabe(t, browser):
    with Server() as s:
        s.seed(VORLAGEN, tags=[{"n": "Garten", "c": "mint"}])
        p = Page(browser, s.url, PHONE, setup=ALS_LASSE)
        pg = p.pg
        pg.click("[data-v=home]")
        pg.click("#qadd")
        pg.type("#qadd", "Rasen mähen Sa @Melanie", delay=10)
        got = p.js(SUG % "#qsug")
        t.check("Schnelleingabe zeigt Vorschläge (Datum und @Person stören nicht)", got == ["Rasen mähen"], got)
        pg.click("#qsug .vsg")
        pg.wait_for_timeout(400)
        st = p.js("({open:dlg.open,title:f_title.value,who:selWho,tags:selTags,start:f_start.value,end:f_end.value,qa:(document.getElementById('qadd')||{}).value,focus:document.activeElement.id})")
        sa = datetime.date.fromisoformat(st["start"]) if st.get("start") else None
        t.check("Antippen öffnet das Blatt mit allen Einstellungen", st["open"] and st["title"] == "Rasen mähen" and st["tags"] == ["Garten"], st)
        t.check("Getipptes hat Vorrang: @Melanie und Samstag", st["who"] == ["Melanie"] and sa and sa.weekday() == 5 and st["end"] == str(sa + datetime.timedelta(1)), st)
        t.check("Schnelleingabe geleert, Tastatur bleibt zu", st["qa"] == "" and st["focus"] != "f_title", st)
        pg.click("#b_save")
        pg.wait_for_timeout(600)
        t.check("Gespeichert", sum(1 for x in s.tasks() if x["title"] == "Rasen mähen" and x.get("who") == "Melanie") == 1)
        pg.click("#qadd")
        pg.type("#qadd", "Fens", delay=10)
        t.check("Vorschläge erscheinen wieder", p.js(SUG % "#qsug") == ["Fenster putzen"])
        pg.click(".hlist h3")
        pg.wait_for_timeout(200)
        t.check("Tippen daneben blendet die Vorschläge aus", p.js("document.getElementById('qsug').innerHTML") == "")
        pg.click("#qadd")
        pg.keyboard.press("End")
        pg.keyboard.type("ter putzen")
        pg.keyboard.press("Enter")
        pg.wait_for_timeout(600)
        t.check("Enter legt wie bisher direkt an (ohne Vorlage)", sum(1 for x in s.tasks() if x["title"] == "Fenster putzen") == 2)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_ring_zeigt_heute(t, browser):
    with Server() as s:
        s.seed([task("l1", "Überfällig", D(-3), D(-2), who="Lasse"),
                task("l2", "Heute fällig", D(0), D(0), who="Lasse"),
                task("l3", "Heute erledigt", D(-5), D(5), who="Lasse", status="done",
                     log=[{"t": NOW_UTC, "a": "Lasse", "k": "h", "x": "Status: In Arbeit → Erledigt"}]),
                task("l4", "Letzte Woche erledigt", D(-8), D(-7), who="Lasse", status="done",
                     log=[{"t": D(-7) + "T09:00", "a": "Lasse", "k": "h", "x": "Status: Offen → Erledigt"}]),
                task("l5", "Erledigt und wieder geöffnet", D(-1), D(3), who="Lasse", status="todo",
                     log=[{"t": NOW_UTC, "a": "Lasse", "k": "h", "x": "Status: Erledigt → Offen"}]),
                task("l6", "Nächste Woche", D(7), D(8), who="Lasse"),
                task("m1", "Melanie heute", D(0), D(0), who="Melanie")])
        p = Page(browser, s.url, PHONE, setup=ALS_LASSE)
        p.pg.click("[data-v=home]")
        p.pg.wait_for_timeout(300)
        hh = lambda: p.js("[document.querySelector('.hero .hh').textContent,document.querySelector('.hero .hsub').textContent,document.querySelector('.hero .hn').textContent]")
        h = hh()
        t.check("Meine, heute: überfällig + heute anstehend + heute erledigt (1 von 4)", h[0] == "Heute: 1 von 4 erledigt" and h[2] == "25%", h)
        t.check("Unterzeile: noch offen, davon überfällig", h[1] == "Noch 3 offen, davon 1 überfällig.", h)
        p.js("void setStatus(byId('l2'),'done')")
        p.pg.wait_for_timeout(700)
        t.check("Abhaken zählt sofort als heute erledigt (2 von 4)", hh()[0] == "Heute: 2 von 4 erledigt", hh())
        p.pg.click(".hpick [data-hw=__all]")
        p.pg.wait_for_timeout(300)
        t.check("„Alle“: auch Melanies heutige Aufgabe (2 von 5)", hh()[0] == "Heute: 2 von 5 erledigt", hh())
        p.pg.click(".hpick [data-hw=Melanie]")
        p.pg.wait_for_timeout(300)
        p.js("void setStatus(byId('m1'),'done')")
        p.pg.wait_for_timeout(700)
        t.check("Alles erledigt: 100 % und passender Text", hh() == ["Heute: 1 von 1 erledigt", "Alles für heute erledigt.", "100%"], hh())
        s.api("api/task", {**s.task("m1"), "start": D(9), "end": D(9), "status": "todo", "log": []})
        p.js("pull(true)")
        p.pg.wait_for_timeout(700)
        t.check("Nichts für heute: Strich statt 0 %", hh() == ["Heute: 0 von 0 erledigt", "Für heute ist nichts geplant.", "–"], hh())
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()
