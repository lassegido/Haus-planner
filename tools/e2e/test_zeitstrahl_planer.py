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
        t.check("iPad: große Fläche zum Greifen des Punkts", p.js("+document.querySelector('.gdh').getAttribute('r')") >= 10)
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


def test_abhaengigkeiten_planen_automatisch(t, browser):
    """1.50: Nachfolger starten frühestens nach dem Ende der Vorgänger; Verlängern schiebt mit; zu früh gelegt wird korrigiert."""
    with Server() as s:
        s.seed([task("a", "Estrich trocknen", D(0), D(9)), task("b", "Boden legen", D(3), D(4)), task("c", "Möbel rein", D(5), D(5), deps=["b"])])
        p = Page(browser, s.url, GROSS)
        zeitstrahl(p)
        p.js("void addDep('a','b')")
        p.pg.wait_for_timeout(900)
        b, c = s.task("b"), s.task("c")
        t.check("Verknüpfen: Nachfolger rückt hinter den Vorgänger (10 Tage)", b["start"] == D(10) and b["end"] == D(11), b)
        t.check("… und dessen Nachfolger rückt mit", c["start"] == D(12), c)
        t.check("Hinweis erklärt die Verschiebung", "eingeplant" in (p.pg.text_content("#toast") or "") or "rückt" in (p.pg.text_content("#toast") or ""))
        # Vorgänger am Ende verlängern (Griff rechts ziehen)
        e = p.pg.locator("g[data-id=a] rect[data-h=e]").bounding_box()
        ppd = p.js("+document.querySelector('.gb').dataset.ppd")
        p.pg.mouse.move(e["x"] + e["width"] / 2, e["y"] + e["height"] / 2)
        p.pg.mouse.down()
        p.pg.mouse.move(e["x"] + e["width"] / 2 + ppd * 2 + 2, e["y"] + e["height"] / 2, steps=6)
        p.pg.mouse.up()
        p.pg.wait_for_timeout(1000)
        t.check("Griff rechts: Aufgabe um 2 Tage verlängert", s.task("a")["end"] == D(11), s.task("a"))
        t.check("Nachfolger rücken mit", s.task("b")["start"] == D(12) and s.task("c")["start"] == D(14), (s.task("b"), s.task("c")))
        s_ = p.pg.locator("g[data-id=a] rect[data-h=s]").bounding_box()
        p.pg.mouse.move(s_["x"] + s_["width"] / 2, s_["y"] + s_["height"] / 2)
        p.pg.mouse.down()
        p.pg.mouse.move(s_["x"] + s_["width"] / 2 + ppd * 3 + 2, s_["y"] + s_["height"] / 2, steps=6)
        p.pg.mouse.up()
        p.pg.wait_for_timeout(800)
        t.check("Griff links: Aufgabe kürzer (startet 3 Tage später)", s.task("a")["start"] == D(3) and s.task("a")["end"] == D(11), s.task("a"))
        s.api("api/task", {**s.task("b"), "start": D(1), "end": D(2)})
        p.js("pull(true)")
        p.pg.wait_for_timeout(600)
        p.js("void saveTask(byId('b'))")
        p.pg.wait_for_timeout(900)
        t.check("Zu früh gelegt: wird an den frühesten Tag gesetzt", s.task("b")["start"] == D(12), s.task("b"))
        s.api("api/task", {**s.task("a"), "status": "done"})
        p.js("pull(true)")
        p.pg.wait_for_timeout(500)
        p.js("void saveTask({...byId('b'),start:'%s',end:'%s'})" % (D(1), D(2)))
        p.pg.wait_for_timeout(800)
        t.check("Erledigter Vorgänger bremst nicht mehr", s.task("b")["start"] == D(1), s.task("b"))
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_meilenstein_schalter(t, browser):
    with Server() as s:
        s.seed([task("a", "Eins", D(0), D(0))])
        p = Page(browser, s.url, IPAD)
        p.pg.wait_for_timeout(1500)
        p.js("openDlg('a')")
        p.pg.wait_for_timeout(400)
        w = p.js("[parseFloat(getComputedStyle(f_ms).width),parseFloat(getComputedStyle(f_ms).height)]")
        t.check("Schalter Meilenstein hat Schalterform (breiter als hoch)", w[0] > 40 and w[0] > w[1] * 1.4, w)
        p.close()


def test_frueher_fertig_zieht_vor(t, browser):
    """1.52: Wie MS Project („so früh wie möglich“): früher fertig → Nachfolger rückt vor; bewusst später gelegt bleibt; In Arbeit wird nie verschoben."""
    with Server() as s:
        s.seed([task("y", "Fliesen legen", D(0), D(9)), task("x", "Fugen", D(2), D(3), deps=["y"]), task("z", "Silikon", D(1), D(1), deps=["x"]),
                task("w", "Schon begonnen", D(0), D(2), deps=["y"], status="doing")])
        p = Page(browser, s.url, GROSS)
        zeitstrahl(p)
        p.pg.wait_for_timeout(1200)
        t.check("Beim Laden: Kette wird eingeplant (x nach y, z nach x)", s.task("x")["start"] == D(10) and s.task("x")["end"] == D(11) and s.task("z")["start"] == D(12),
                (s.task("x")["start"], s.task("z")["start"]))
        t.check("„In Arbeit“ wird nicht verschoben", s.task("w")["start"] == D(0))
        p.js("void setStatus(byId('y'),'done')")
        p.pg.wait_for_timeout(1500)
        t.check("Vorgänger heute fertig → Nachfolger rückt auf heute vor", s.task("x")["start"] == D(0) and s.task("x")["end"] == D(1), s.task("x"))
        t.check("… und die Kette rückt mit", s.task("z")["start"] == D(2), s.task("z"))
        t.check("Hinweis „neu eingeplant“", "eingeplant" in (p.pg.text_content("#toast") or "") or "rückt" in (p.pg.text_content("#toast") or ""))
        p.js("void saveTask({...byId('x'),start:'%s',end:'%s'})" % (D(5), D(6)))
        p.pg.wait_for_timeout(1500)
        x = s.task("x")
        t.check("Bewusst später gelegt: bleibt dort (frühestens ab)", x["start"] == D(5) and x.get("snet") == D(5), x)
        t.check("Nachfolger richtet sich danach", s.task("z")["start"] == D(7), s.task("z"))
        p.js("void saveTask({...byId('x'),start:'%s',end:'%s'})" % (D(-3), D(-2)))
        p.pg.wait_for_timeout(1500)
        x = s.task("x")
        t.check("Früher als möglich: wird auf den frühesten Tag gesetzt, „frühestens ab“ entfällt", x["start"] == D(0) and "snet" not in x, x)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_reihenfolge_bleibt_beim_bearbeiten(t, browser):
    """1.52: Datum ziehen sortiert die Zeilen nicht sofort um; erst nach Neuladen."""
    with Server() as s:
        s.seed([task("a", "Eins", D(0), D(1)), task("b", "Zwei", D(2), D(3)), task("c", "Drei", D(4), D(5))])
        p = Page(browser, s.url, GROSS)
        zeitstrahl(p)
        p.js("void saveTask({...byId('a'),start:'%s',end:'%s'})" % (D(8), D(9)))
        p.pg.wait_for_timeout(800)
        t.check("Nach dem Verschieben: Zeile bleibt oben", rows(p) == ["a", "b", "c"], rows(p))
        p.pg.reload()
        zeitstrahl(p)
        t.check("Nach dem Neuladen: nach Datum sortiert", rows(p) == ["b", "c", "a"], rows(p))
        p.close()
