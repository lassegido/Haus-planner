"""Echo-Show-Ansicht (?anzeige) und die Claude-Version (src/planner.html ohne Server, lokaler Speicher)."""
import datetime
from common import ROOT, Page, Server, task

T = datetime.date.today()
D = lambda n: str(T + datetime.timedelta(n))


def test_echo_show_anzeige(t, browser):
    with Server() as s:
        s.seed([task("k0", "Rechnung bezahlen", D(-1), who="Lasse"), task("k1", "Steuer abgeben", D(-2), D(3), who="Lasse", status="doing"),
                task("k2", "Rasen mähen", D(0), who="Lasse, Melanie"), task("k3", "Dachrinne reinigen", D(4), who="Lasse"),
                task("k4", "Fenster putzen", D(2), who="Melanie"), task("k5", "Alt und erledigt", D(-3), who="Lasse", status="done")])
        for q, name in [("?anzeige&wer=Lasse&dunkel", "dunkel"), ("?anzeige&hell", "hell")]:
            p = Page(browser, s.url + q, {"viewport": {"width": 960, "height": 480}, "has_touch": True}, onboarded=False)
            txt = p.js("document.body.innerText")
            p.shot("anzeige-" + name)
            t.check("Anzeige %s: kein Blatt, keine Fehler" % name, not p.js("!!document.querySelector('dialog[open]')") and not p.errors, p.errors)
            t.check("Anzeige %s: überfällige und heutige Aufgaben sichtbar, erledigte nicht" % name,
                    "Rechnung bezahlen" in txt and "Rasen mähen" in txt and "Alt und erledigt" not in txt)
            if "wer=Lasse" in q:
                t.check("Anzeige nur für Lasse: Melanies Aufgabe fehlt", "Fenster putzen" not in txt)
            wide = p.js("document.documentElement.scrollWidth-innerWidth")
            t.check("Anzeige %s: passt auf den Echo Show 5 (kein seitliches Scrollen)" % name, wide <= 1, wide)
            p.close()


def test_claude_version_ohne_server(t, browser):
    p = Page(browser, "file://" + ROOT + "/src/planner.html", {"viewport": {"width": 390, "height": 844}})
    for v in ["home", "board", "list", "gantt", "cal"]:
        p.pg.click("[data-v=%s]" % v)
        p.pg.wait_for_timeout(200)
    p.settings("des")
    p.pg.click("#s_body [data-set='des:salbei']")
    p.pg.wait_for_timeout(200)
    t.check("Claude-Version: Farbwelt wechselt", p.js("getComputedStyle(document.documentElement).getPropertyValue('--acc').trim()") != "")
    p.js("document.getElementById('dls').close()")
    p.pg.click("[data-v=home]")
    p.pg.fill("#qadd", "Test Aufgabe morgen #Haus")
    p.pg.keyboard.press("Enter")
    p.pg.wait_for_timeout(400)
    got = p.js("RAW.map(t=>[t.title,t.tags,t.start])")
    t.check("Claude-Version: Schnelleingabe speichert lokal", got and got[0][0] == "Test Aufgabe" and got[0][1] == ["Haus"] and got[0][2] == D(1), got)
    t.check("Claude-Version: keine Skriptfehler", not p.errors, p.errors)
    p.close()
