"""Aufgabenblatt: Suche bei Abhängigkeiten."""
from common import PHONE, Page, Server, task

VIS = "[...document.querySelectorAll('#f_deps label')].filter(l=>!l.hidden).map(l=>l.querySelector('b').textContent)"


def test_abhaengigkeiten_suchen(t, browser):
    with Server() as s:
        s.seed([task("a", "Büro fertigstellen", "2026-11-24", "2026-11-30", proj="Schöner Wohnen", tags=["Haus"], who="Lasse"),
                task("b", "Garage fertigstellen", "2026-11-24", "2026-11-30", proj="Schöner Wohnen", tags=["Haus"], who="Lasse"),
                task("c", "Dankeskarten verschicken", "2026-11-24", "2026-11-30", proj="Organisation", tags=["Sonstiges"], who="Melanie"),
                task("d", "Zaun streichen", "2026-11-24", "2026-11-30", tags=["Garten"], who="Melanie"),
                task("e", "Wall abtragen", "2026-11-24", "2026-11-30", tags=["Garten"], who="Lasse", deps=["a"])])
        p = Page(browser, s.url, PHONE)
        p.js("openDlg('a')")
        p.pg.wait_for_timeout(400)
        p.js("document.getElementById('d_pl').open=true")
        t.check("Alle anderen Aufgaben werden angeboten", len(p.js(VIS)) == 4, p.js(VIS))
        t.check("Kreis-Abhängigkeit ist gesperrt (Wall hängt schon von Büro ab)", p.js("document.querySelector('#f_deps input[value=e]').disabled"))
        p.pg.fill("#f_depq", "schöner")
        t.check("Suche nach Projekt findet nur passende", p.js(VIS) == ["Garage fertigstellen"] and p.pg.text_content("#f_depc") == "1 von 4")
        p.pg.check("#f_deps input[value=b]")
        p.pg.fill("#f_depq", "garten mel")
        t.check("Mehrere Suchwörter (Tag + Person); Gewähltes bleibt sichtbar",
                p.js(VIS) == ["Garage fertigstellen", "Zaun streichen"] and "1 gewählt" in p.pg.text_content("#f_depc"), p.js(VIS))
        p.pg.fill("#f_depq", "xyz")
        t.check("Kein Treffer: Gewähltes bleibt, Zähler stimmt", p.js(VIS) == ["Garage fertigstellen"], p.pg.text_content("#f_depc"))
        t.check("Tippen in der Suche zählt nicht als Änderung der Aufgabe", p.js("dlgState()!==dlgSnap"))
        p.pg.click("#b_save")
        p.pg.wait_for_timeout(600)
        t.check("Gespeichert: nur die angehakte Abhängigkeit", s.task("a").get("deps") == ["b"], s.task("a").get("deps"))
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()
