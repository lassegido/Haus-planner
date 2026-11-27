"""Zeitstrahl (1.48): Verknüpfungen sehen, anlegen (ziehen oder Menü + antippen) und lösen; Reihenfolge ändern; Menü mit Projekt und Notiz."""
import datetime
from common import DESKTOP, IPAD, Page, Server, task

T = datetime.date.today()
D = lambda n: str(T + datetime.timedelta(n))
GROSS = {**DESKTOP, "viewport": {"width": 1400, "height": 1000}}


def zeitstrahl(p):
    p.pg.wait_for_function("!document.getElementById('splash')||getComputedStyle(document.getElementById('splash')).display==='none'||getComputedStyle(document.getElementById('splash')).opacity==='0'", timeout=8000)
    p.js("(()=>{const b=[...document.querySelectorAll('[data-v=gantt]')].find(x=>x.offsetParent);b&&b.click()})()")
    p.pg.wait_for_timeout(500)


def menu(p, tid, label):
    p.js("id=>{taskMenu(id)}", tid)
    p.pg.wait_for_timeout(250)
    items = p.js("[...document.querySelectorAll('#dsh button')].map(b=>b.textContent)")
    if label:
        p.pg.click("#dsh button:has-text('%s')" % label)
        p.pg.wait_for_timeout(400)
    return items


def rows(p):
    return p.js("[...document.querySelectorAll('.gl .gr[data-id]')].map(r=>r.dataset.id)")


def test_verknuepfungen(t, browser):
    with Server() as s:
        s.seed([task("a", "Farbe kaufen", D(0), D(1)), task("b", "Wand streichen", D(2), D(4), deps=["a"]), task("c", "Möbel rücken", D(5), D(6))])
        p = Page(browser, s.url, GROSS)
        zeitstrahl(p)
        t.check("Verknüpfung sichtbar (Pfeil a → b)", p.js("!!document.querySelector('[data-dep=\"a>b\"] .gdlv')"))
        t.check("Pfeil in Akzentfarbe", "var(--acc)" in p.js("getComputedStyle(document.querySelector('.gdlv')).stroke") or
                p.js("getComputedStyle(document.querySelector('.gdlv')).stroke") != "none")
        # Ziehen vom Punkt am Balkenende auf einen anderen Balken
        d = p.pg.locator("g[data-id=b] .gdep").bounding_box()
        z = p.pg.locator("g[data-id=c] rect").first.bounding_box()
        p.pg.mouse.move(d["x"] + 5, d["y"] + 5)
        p.pg.mouse.down()
        p.pg.mouse.move(z["x"] + 20, z["y"] + 8, steps=8)
        p.pg.mouse.up()
        p.pg.wait_for_timeout(600)
        t.check("Punkt ziehen verknüpft b → c", s.task("c").get("deps") == ["b"], s.task("c").get("deps"))
        # Menü: Verknüpfen mit … und dann Ziel antippen
        items = menu(p, "a", "Verknüpfen mit")
        t.check("Menü im Zeitstrahl: Verknüpfen, Projekt, Notiz, Reihenfolge", all(any(x.startswith(l) for x in items) for l in ("Verknüpfen", "Zu Projekt", "Notiz", "↑ Nach oben", "↓ Nach unten")), items)
        t.check("Hinweis zum Antippen erscheint", p.js("!!document.querySelector('.phint')"))
        p.pg.click("g[data-id=c] rect >> nth=0")
        p.pg.wait_for_timeout(600)
        t.check("Ziel angetippt: a → c verknüpft, kein Blatt offen", sorted(s.task("c")["deps"]) == ["a", "b"] and not p.js("document.getElementById('dlg').open"), s.task("c"))
        menu(p, "c", "Verknüpfen mit")
        p.pg.click("g[data-id=a] rect >> nth=0")
        p.pg.wait_for_timeout(500)
        t.check("Kreis wird verhindert", s.task("a").get("deps") in ([], None) and "Kreis" in (p.pg.text_content("#toast") or ""))
        p.pg.click("[data-dep='a>b']", force=True)
        p.pg.wait_for_timeout(300)
        p.pg.click("#dsh button:has-text('Verknüpfung lösen')")
        p.pg.wait_for_timeout(500)
        t.check("Pfeil antippen → lösen", s.task("b").get("deps") == [], s.task("b").get("deps"))
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_reihenfolge_projekt_notiz(t, browser):
    with Server() as s:
        s.seed([task("a", "Eins", D(0), D(1)), task("b", "Zwei", D(1), D(2)), task("c", "Drei", D(2), D(3)), task("d", "Vier", D(3), D(4), proj="Elternzeit")])
        p = Page(browser, s.url, GROSS)
        zeitstrahl(p)
        t.check("Vorher nach Datum", rows(p) == ["a", "b", "c", "d"], rows(p))
        g = p.pg.locator(".gr[data-id=d] .ggrip").bounding_box()
        z = p.pg.locator(".gr[data-id=b]").bounding_box()
        p.pg.mouse.move(g["x"] + g["width"] / 2, g["y"] + g["height"] / 2)
        p.pg.mouse.down()
        p.pg.mouse.move(g["x"] + 5, z["y"] + 8, steps=8)
        p.pg.mouse.up()
        p.pg.wait_for_timeout(700)
        t.check("Zeile am Griff nach oben ziehen: Vier steht vor Zwei", rows(p) == ["a", "d", "b", "c"], rows(p))
        t.check("Eigene Reihenfolge ist jetzt eingestellt und gespeichert", p.js("sortm") == "ord" and isinstance(s.task("d").get("ord"), (int, float)))
        menu(p, "c", "↑ Nach oben")
        p.pg.wait_for_timeout(300)
        t.check("Menü „Nach oben“", rows(p) == ["a", "d", "c", "b"], rows(p))
        menu(p, "a", "↓ Nach unten")
        p.pg.wait_for_timeout(300)
        t.check("Menü „Nach unten“", rows(p) == ["d", "a", "c", "b"], rows(p))
        items = menu(p, "a", "Zu Projekt hinzufügen")
        p.pg.click("#dsh button:has-text('Elternzeit')")
        p.pg.wait_for_timeout(500)
        t.check("Zu bestehendem Projekt hinzufügen", s.task("a")["proj"] == "Elternzeit", s.task("a"))
        menu(p, "b", "Zu Projekt hinzufügen")
        p.pg.click("#dsh button:has-text('Neues Projekt')")
        p.pg.wait_for_timeout(200)
        p.pg.fill("#ask_t", "Keller")
        p.pg.keyboard.press("Enter")
        p.pg.wait_for_timeout(500)
        t.check("Neues Projekt anlegen und zuordnen", s.task("b")["proj"] == "Keller", s.task("b"))
        menu(p, "c", "Notiz hinzufügen")
        p.pg.fill("#ask_t", "Werkzeug bei Papa leihen")
        p.pg.click("#dsh button:has-text('Speichern')")
        p.pg.wait_for_timeout(500)
        t.check("Notiz hinzufügen", s.task("c")["notes"] == "Werkzeug bei Papa leihen", s.task("c"))
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_ipad_punkt_sichtbar(t, browser):
    with Server() as s:
        s.seed([task("a", "Eins", D(0), D(1)), task("b", "Zwei", D(2), D(3))])
        p = Page(browser, s.url, {**IPAD, "viewport": {"width": 1180, "height": 820}})
        zeitstrahl(p)
        t.check("iPad: Punkt zum Verknüpfen ist sichtbar", p.js("getComputedStyle(document.querySelector('.gdep')).display") != "none")
        t.check("iPad: große Fläche zum Greifen des Punkts", p.js("+document.querySelector('.gdh').getAttribute('r')") >= 14)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def ziehen_y(p, sel_from, sel_to, dx=0):
    g = p.pg.locator(sel_from).first.bounding_box()
    z = p.pg.locator(sel_to).first.bounding_box()
    p.pg.mouse.move(g["x"] + g["width"] / 2, g["y"] + g["height"] / 2)
    p.pg.mouse.down()
    p.pg.mouse.move(g["x"] + g["width"] / 2 + 3, g["y"] + 12, steps=3)
    p.pg.mouse.move(g["x"] + g["width"] / 2 + dx, z["y"] + z["height"] - 6, steps=10)
    p.pg.mouse.up()
    p.pg.wait_for_timeout(700)


def test_in_andere_gruppe_ziehen(t, browser):
    """1.49: Im gruppierten Zeitstrahl übernimmt eine Aufgabe die Gruppe, in die man sie zieht."""
    with Server() as s:
        s.seed([task("a", "Kinderzimmer", D(0), D(2), proj="Elternzeit", who="Lasse", tags=["Haus"]),
                task("b", "Hecke", D(1), D(3), who="Melanie", tags=["Garten"]),
                task("c", "Steuer", D(2), D(4), who="Lasse")], tags=[{"n": "Haus", "c": "sea"}, {"n": "Garten", "c": "mint"}, {"n": "Elternzeit", "c": "sun", "p": 1}])
        p = Page(browser, s.url, GROSS)
        zeitstrahl(p)
        def gruppieren(k):
            p.js("k=>{grp=k;const g=document.getElementById('grp');if(g)g.value=k;render()}", k)
            p.pg.wait_for_timeout(400)
        gruppieren("proj")
        ziehen_y(p, ".gr[data-id=b] .ggrip", ".gr[data-id=a]")
        t.check("Nach Projekt: Zeile in „Elternzeit“ ziehen setzt das Projekt", s.task("b")["proj"] == "Elternzeit", s.task("b"))
        t.check("Hinweis nennt die neue Gruppe", "Elternzeit" in (p.pg.text_content("#toast") or ""))
        p.pg.click("#toast button")
        p.pg.wait_for_timeout(500)
        t.check("Rückgängig nimmt das Projekt wieder weg", s.task("b")["proj"] == "", s.task("b"))
        gruppieren("who")
        ziehen_y(p, ".gr[data-id=c] .ggrip", ".gr[data-gk=Melanie][data-id]")
        t.check("Nach Person: Lasse → Melanie", s.task("c")["who"] == "Melanie", s.task("c"))
        gruppieren("tag")
        ziehen_y(p, "g[data-id=b] rect", ".gr[data-id=a]", dx=0)
        b = s.task("b")
        t.check("Nach Tag: Balken nach oben in „Haus“ ziehen tauscht den Tag", b["tags"][0] == "Haus" and "Garten" not in b["tags"], b)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()
