"""Planen (1.46): Kalender → Planen, Zeitraum 1/2/5 Wochen, Sammelkorb, Verschieben per Ziehen oder Antippen."""
import datetime
from common import DESKTOP, IPAD, PHONE, Page, Server, task

T = datetime.date.today()
D = lambda n: str(T + datetime.timedelta(n))
MON = T - datetime.timedelta(T.weekday())
PLAN = lambda pg: pg.add_init_script("try{localStorage.setItem('haus-me','Lasse')}catch(e){}")


def zum_planen(p):
    p.js("(()=>{const b=[...document.querySelectorAll('[data-v=cal]')].find(x=>x.offsetParent);b&&b.click()})()")
    p.pg.wait_for_timeout(300)
    if not p.js("!!document.querySelector('.plan')"):
        p.pg.click("[data-calm=plan]")
        p.pg.wait_for_timeout(300)


def chips(p, sel):
    return p.js("s=>[...document.querySelectorAll(s+' .pch')].map(c=>c.dataset.id)", sel)


def test_zeitraum_und_sammelkorb(t, browser):
    with Server() as s:
        s.seed([task("a", "Kinderwagen reparieren", D(0), D(0), who="Lasse"), task("x", "Später", D(40), D(40))])
        p = Page(browser, s.url, IPAD, setup=PLAN)
        zum_planen(p)
        days = p.js("[...document.querySelectorAll('[data-pday]')].map(d=>d.dataset.pday)")
        t.check("Standard: 2 Wochen ab Montag dieser Woche", len(days) == 14 and days[0] == str(MON), days[:2])
        t.check("Kalenderwochen als Überschrift", p.js("document.querySelectorAll('.pwk').length") == 2 and
                p.js("document.querySelector('.pwk').textContent") == "KW %d" % MON.isocalendar()[1])
        p.pg.click("[data-planw='5']")
        p.pg.wait_for_timeout(200)
        t.check("5 Wochen: 35 Tage", p.js("document.querySelectorAll('[data-pday]').length") == 35)
        p.pg.click("[data-pnav='1']")
        p.pg.wait_for_timeout(200)
        t.check("Pfeil: eine Woche weiter", p.js("document.querySelector('[data-pday]').dataset.pday") == str(MON + datetime.timedelta(7)))
        p.pg.click("[data-pnav='0']")
        p.pg.wait_for_timeout(200)
        t.check("„Heute“ springt zurück", p.js("document.querySelector('[data-pday]').dataset.pday") == str(MON))
        t.check("Aufgabe steht an ihrem Tag", "a" in chips(p, "[data-pday='%s']" % D(0)))
        p.pg.click("[data-pin=box]")
        p.pg.keyboard.type("Keller entrümpeln")
        p.pg.keyboard.press("Enter")
        p.pg.wait_for_timeout(500)
        p.pg.keyboard.type("Babyfotos sortieren @Melanie")
        p.pg.keyboard.press("Enter")
        p.pg.wait_for_timeout(500)
        box = [x for x in s.tasks() if x.get("inbox")]
        t.check("Sammelkorb: schnell nacheinander eintippen, ohne Tag gespeichert", sorted(x["title"] for x in box) == ["Babyfotos sortieren", "Keller entrümpeln"]
                and any(x["who"] == "Melanie" for x in box), box)
        t.check("Eingabe bleibt aktiv für die nächste", p.js("document.activeElement.dataset.pin") == "box")
        t.check("Zähler im Sammelkorb", p.js("document.querySelector('.pbox h3 em').textContent") == "2")
        p.pg.click("[data-calm=monat]")
        p.pg.wait_for_timeout(200)
        t.check("Monat: Sammelkorb-Aufgaben stehen an keinem Tag", "Keller" not in p.js("document.querySelector('.cgrid').textContent"))
        t.check("Umschalter merkt sich die Wahl", p.js("prefGet('calm')") == "monat")
        p.pg.click("[data-v=list]")
        p.pg.wait_for_timeout(200)
        t.check("Liste: ohne Sammelkorb", "Keller" not in p.js("document.getElementById('main').textContent"))
        p.pg.click("[data-v=home]")
        p.pg.wait_for_timeout(300)
        t.check("Start: Ring zählt den Sammelkorb nicht", p.js("document.querySelector('.hero .hh').textContent") == "0 von 1 erledigt")
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_verschieben_ziehen_und_antippen(t, browser):
    with Server() as s:
        s.seed([task("i", "Hecke schneiden", D(0), D(0), inbox=True), task("m", "Gartenhaus streichen", D(0), D(2), who="Lasse"),
                task("l", "Steuer", D(-5), D(-3), who="Lasse")])
        p = Page(browser, s.url, {**DESKTOP, "viewport": {"width": 1400, "height": 1300}}, setup=PLAN)
        zum_planen(p)
        t.check("Liegen geblieben: überfällige Aufgabe", chips(p, ".pbox").count("l") == 1)
        # Ziehen mit der Maus am Griff
        def ziehen(tid, ziel):
            g = p.pg.locator("[data-pgrip='%s']" % tid).first.bounding_box()
            z = p.pg.locator(ziel).first.bounding_box()
            p.pg.mouse.move(g["x"] + g["width"] / 2, g["y"] + g["height"] / 2)
            p.pg.mouse.down()
            p.pg.mouse.move(g["x"] + 30, g["y"] + 20, steps=4)
            p.pg.mouse.move(z["x"] + z["width"] / 2, z["y"] + z["height"] - 12, steps=8)
            p.pg.mouse.up()
            p.pg.wait_for_timeout(600)
        ziehen("i", "[data-pday='%s']" % D(3))
        i = s.task("i")
        t.check("Ziehen aus dem Sammelkorb auf einen Tag", i["start"] == D(3) and "inbox" not in i, i)
        t.check("Verlauf: eingeplant", any("Aus dem Sammelkorb eingeplant" in x["x"] for x in i.get("log", [])), i.get("log"))
        ziehen("m", "[data-pday='%s']" % D(5))
        m = s.task("m")
        t.check("Mehrtägige Aufgabe behält ihre Dauer", m["start"] == D(5) and m["end"] == D(7), m)
        p.pg.click("#toast button")
        p.pg.wait_for_timeout(500)
        t.check("Rückgängig stellt den alten Zeitraum her", s.task("m")["start"] == D(0) and s.task("m")["end"] == D(2), s.task("m"))
        ziehen("l", "[data-pday='%s']" % D(1))
        t.check("Liegen gebliebenes neu eingeplant", s.task("l")["start"] == D(1) and s.task("l")["end"] == D(3), s.task("l"))
        ziehen("i", ".pbox")
        t.check("Zurück in den Sammelkorb", s.task("i").get("inbox") is True)
        # Antippen: Griff antippen, dann Ziel antippen
        p.pg.click("[data-pgrip='i']")
        p.pg.wait_for_timeout(200)
        t.check("Griff antippen: Aufgabe gewählt, Hinweis erscheint, kein Blatt", p.js("!!document.querySelector('.pch.picked')") and
                p.js("!!document.querySelector('.phint')") and not p.js("document.getElementById('dlg').open"))
        p.pg.click("[data-pday='%s'] header" % D(4))
        p.pg.wait_for_timeout(500)
        t.check("Ziel antippen verschiebt", s.task("i")["start"] == D(4) and "inbox" not in s.task("i") and not p.js("!!document.querySelector('.phint')"))
        p.pg.click("[data-pday='%s'] .pch .pct" % D(4))
        p.pg.wait_for_timeout(300)
        t.check("Antippen der Aufgabe selbst öffnet sie", p.js("document.getElementById('dlg').open") and p.js("f_title.value") == "Hecke schneiden")
        p.js("document.getElementById('dlg').close()")
        p.pg.click("[data-padd='%s']" % D(6))
        p.pg.wait_for_timeout(200)
        p.pg.keyboard.type("Arzttermin U4")
        p.pg.keyboard.press("Enter")
        p.pg.wait_for_timeout(500)
        new = [x for x in s.tasks() if x["title"] == "Arzttermin U4"]
        t.check("Plus am Tag: direkt an diesem Tag anlegen, Eingabe bleibt offen", len(new) == 1 and new[0]["start"] == D(6) and "inbox" not in new[0]
                and p.js("document.activeElement.dataset.pin") == D(6), new)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_planen_auf_dem_handy(t, browser):
    with Server() as s:
        s.seed([task("i", "Hecke schneiden", D(0), D(0), inbox=True)])
        p = Page(browser, s.url, PHONE, setup=PLAN)
        zum_planen(p)
        w = p.js("[...document.querySelectorAll('.pweek')].map(x=>getComputedStyle(x).gridTemplateColumns.split(' ').length)")
        t.check("Handy: Tage untereinander (eine Spalte)", all(x == 1 for x in w), w)
        t.check("Griff ist groß genug zum Tippen", p.js("document.querySelector('.pch').getBoundingClientRect().height") >= 44)
        p.pg.tap("[data-pgrip='i']")
        p.pg.wait_for_timeout(200)
        p.pg.tap("[data-pday='%s'] header" % D(2))
        p.pg.wait_for_timeout(500)
        t.check("Antippen, dann Tag antippen: eingeplant", s.task("i")["start"] == D(2) and "inbox" not in s.task("i"), s.task("i"))
        t.check("Keine waagerechte Verschiebung der Seite", p.js("document.documentElement.scrollWidth<=innerWidth+1"))
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()
