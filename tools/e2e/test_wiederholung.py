"""Wiederholungen: Schnellauswahl, benutzerdefiniert (Wochentage, Abstand, n-ter Wochentag, Ende) und Reihenfolge der Leiste unten."""
import datetime
from common import DESKTOP, PHONE, Page, Server, task

# Feste Termine in der Zukunft (nextOcc überspringt Vergangenes)
TUE = datetime.date(2027, 3, 2)  # Dienstag
assert TUE.weekday() == 1
d = lambda n: str(TUE + datetime.timedelta(n))


def test_berechnung(t, browser):
    with Server() as s:
        p = Page(browser, s.url, PHONE)
        nx = lambda start, r: p.js("([s,r])=>addInterval(s,r)", [start, r])
        t.check("Di/Do: von Dienstag zum Donnerstag", nx(d(0), {"n": 1, "u": "w", "wd": [2, 4]}) == d(2))
        t.check("Di/Do: von Donnerstag zum nächsten Dienstag", nx(d(2), {"n": 1, "u": "w", "wd": [2, 4]}) == d(7))
        t.check("Alle 2 Wochen Di/Do: Donnerstag → Dienstag in 2 Wochen", nx(d(2), {"n": 2, "u": "w", "wd": [2, 4]}) == d(14))
        t.check("Sonntag zählt als Wochenende (Mo → So derselben Woche)", nx(d(-1), {"n": 1, "u": "w", "wd": [0]}) == d(5))
        t.check("Ohne Wochentage: wie bisher 7 Tage", nx(d(0), {"n": 1, "u": "w"}) == d(7))
        t.check("Monatlich am 1. Dienstag: 2.3. → 6.4.2027", nx("2027-03-02", {"n": 1, "u": "m", "mw": "nth"}) == "2027-04-06")
        t.check("Monatlich am letzten Dienstag: 30.3. → 27.4.2027", nx("2027-03-30", {"n": 1, "u": "m", "mw": "nth"}) == "2027-04-27")
        t.check("Monatlich am 31.: Januar → 28. Februar", nx("2027-01-31", {"n": 1, "u": "m"}) == "2027-02-28")
        rt = lambda r, st: p.js("([r,s])=>recText(r,s)", [r, st])
        t.check("Text: „Alle 2 Wochen am Di und Do“", rt({"n": 2, "u": "w", "wd": [4, 2]}, d(0)) == "Alle 2 Wochen am Di und Do")
        t.check("Text: „Werktags“", rt({"n": 1, "u": "w", "wd": [1, 2, 3, 4, 5]}, d(0)) == "Werktags")
        t.check("Text: „Monatlich am letzten Dienstag bis …“", rt({"n": 1, "u": "m", "mw": "nth", "until": "2027-12-31"}, "2027-03-30") == "Monatlich am letzten Dienstag bis 31.12.")
        last = p.js("t=>nextOcc(t)", {"id": "x", "title": "x", "start": d(0), "end": d(0), "rec": {"n": 1, "u": "w", "until": d(3)}})
        t.check("Nach dem Enddatum wird keine neue Aufgabe angelegt", last is None)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_benutzerdefiniert_im_blatt(t, browser):
    with Server() as s:
        s.seed([task("a", "Müll rausbringen", d(0), d(0))])
        p = Page(browser, s.url, PHONE)
        pg = p.pg
        p.js("openDlg('a');document.getElementById('d_pl').open=true")
        pg.select_option("#f_rec", "c")
        pg.wait_for_timeout(100)
        on = lambda: p.js("[...document.querySelectorAll('#f_rwd button.on')].map(b=>b.textContent)")
        t.check("Benutzerdefiniert: wöchentlich, Wochentag des Beginns vorgewählt", not p.js("f_rcus.hidden") and on() == ["Di"], on())
        pg.click("#f_rwd [data-d='4']")
        pg.fill("#f_rn", "2")
        hint = pg.text_content("#f_rechint")
        t.check("Hinweis: „Alle 2 Wochen am Di und Do“", hint.startswith("Alle 2 Wochen am Di und Do."), hint)
        pg.click("#f_rwd [data-d='2']")
        pg.click("#f_rwd [data-d='4']")
        t.check("Der letzte Wochentag lässt sich nicht abwählen", on() == ["Do"], on())
        pg.click("#f_rwd [data-d='2']")
        pg.click("#b_save")
        pg.wait_for_timeout(600)
        t.check("Gespeichert: {n:2, u:w, wd:[Di, Do]}", s.task("a").get("rec") == {"n": 2, "u": "w", "wd": [2, 4]}, s.task("a").get("rec"))
        p.js("openDlg('a')")
        pg.wait_for_timeout(200)
        t.check("Wieder geöffnet: Benutzerdefiniert mit Di und Do", p.js("f_rec.value") == "c" and on() == ["Di", "Do"])
        pg.click("#f_ru [data-u=m]")
        t.check("Monatlich: Auswahl „Am 2.“ / „Am 1. Dienstag“", p.js("[...document.querySelectorAll('#f_rmo button')].map(b=>b.textContent)") == ["Am 2.", "Am 1. Dienstag"])
        pg.click("#f_rmo [data-m=nth]")
        pg.fill("#f_runtil", "2027-12-31")
        p.js("f_runtil.dispatchEvent(new Event('change'))")
        t.check("Hinweis: Abstand bleibt, „Alle 2 Monate am 1. Dienstag bis 31.12.“", pg.text_content("#f_rechint").startswith("Alle 2 Monate am 1. Dienstag bis 31.12. Beim"), pg.text_content("#f_rechint"))
        pg.select_option("#f_rec", "wk")
        pg.wait_for_timeout(100)
        t.check("Schnellauswahl Werktags blendet die eigene Einstellung aus", p.js("f_rcus.hidden") and pg.text_content("#f_rechint").startswith("Werktags."))
        pg.click("#b_save")
        pg.wait_for_timeout(600)
        t.check("Gespeichert: Werktags", s.task("a").get("rec") == {"n": 1, "u": "w", "wd": [1, 2, 3, 4, 5]}, s.task("a").get("rec"))
        p.js("openDlg('a')")
        pg.wait_for_timeout(200)
        t.check("Wieder geöffnet als Werktags", p.js("f_rec.value") == "wk")
        p.js("document.getElementById('dlg').close()")
        p.js("void setStatus(byId('a'),'done')")
        pg.wait_for_timeout(800)
        nxt = [x for x in s.tasks() if x["title"] == "Müll rausbringen" and x["id"] != "a"]
        t.check("Erledigen legt die nächste am Mittwoch an", len(nxt) == 1 and nxt[0]["start"] == d(1), nxt)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_server_prueft_wiederholung(t, browser):
    with Server() as s:
        s.api("api/task", task("z", "Z", d(0), rec={"n": 1, "u": "w", "wd": [4, 2, 2, 9, "x", True], "mw": "nth", "until": "2027-02-30"}))
        t.check("Server: ungültige Wochentage/Felder verworfen, Reihenfolge Mo–So", s.task("z")["rec"] == {"n": 1, "u": "w", "wd": [2, 4]}, s.task("z")["rec"])
        s.api("api/task", task("y", "Y", d(0), rec={"n": 1, "u": "m", "mw": "nth", "until": "2027-12-31", "wd": [1]}))
        t.check("Server: Monatlich n-ter Wochentag mit Ende bleibt erhalten", s.task("y")["rec"] == {"n": 1, "u": "m", "mw": "nth", "until": "2027-12-31"}, s.task("y")["rec"])
        s.api("api/task", task("o", "Alt", d(0), rec={"n": 2, "u": "w"}))
        t.check("Alte Wiederholungen unverändert", s.task("o")["rec"] == {"n": 2, "u": "w"})


def test_reihenfolge_leiste(t, browser):
    with Server() as s:
        for dev in (PHONE, DESKTOP):
            p = Page(browser, s.url, dev)
            order = p.js("[...document.querySelectorAll('[data-v]')].filter(b=>b.closest('nav,#tabs,aside')).map(b=>b.dataset.v)")
            first = []
            for v in order:
                if v not in first:
                    first.append(v)
            t.check("Leiste: Start, Liste, Board, Zeitstrahl, Kalender", first == ["home", "list", "board", "gantt", "cal"], order)
            p.close()
