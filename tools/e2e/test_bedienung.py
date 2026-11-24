"""Grundbedienung: Ansichten, Wischen, Gedrückt halten, Blätter schließen, Suche."""
import datetime
from common import DESKTOP, IPAD, PHONE, Page, Server, task

TODAY = datetime.date.today()
D = lambda n: str(TODAY + datetime.timedelta(n))


def test_ansichten_auf_allen_geraeten(t, browser):
    with Server() as s:
        s.seed([task("a", "Alpha", D(0), D(3), who="Lasse", tags=["Haus"]), task("b", "Beta", D(-2), D(-1), who="Melanie", status="doing"),
                task("c", "Gamma", D(5), D(9), deps=["a"], checklist=[{"t": "Eins", "d": True}, {"t": "Zwei", "d": False}])],
               tags=[{"n": "Haus", "c": "sky"}])
        for dev, name in [(PHONE, "Handy"), (IPAD, "iPad"), (DESKTOP, "Desktop")]:
            p = Page(browser, s.url, dev)
            for v in ["home", "board", "list", "gantt", "cal"]:
                p.pg.click("[data-v=%s]" % v)
                p.pg.wait_for_timeout(250)
                p.shot("ansicht-%s-%s" % (name, v))
            wide = p.js("document.documentElement.scrollWidth-innerWidth")
            t.check("%s: alle Ansichten ohne Skriptfehler" % name, not p.errors, p.errors)
            t.check("%s: kein seitliches Verrutschen der Seite" % name, wide <= 1, wide)
            p.close()


def test_wischen_und_gedrueckt_halten(t, browser):
    with Server() as s:
        s.seed([task("t%d" % i, n, D(0), D(4), who="Lasse") for i, n in enumerate(["Alpha", "Beta", "Gamma"])])
        p = Page(browser, s.url, PHONE)
        p.pg.click("[data-v=list]")
        p.pg.wait_for_timeout(400)
        x, y, w, h = p.box("#main .lrow")
        x, y = x + 60, y + 20
        p.touch("#main .lrow", [("touchstart", x, y), ("touchmove", x + 20, y + 1), ("touchmove", x + 80, y + 2), ("touchmove", x + 150, y + 2), ("touchend", x + 150, y + 2)])
        p.pg.wait_for_timeout(700)
        st = {x["title"]: x["status"] for x in s.tasks()}
        t.check("Wischen nach rechts erledigt die Aufgabe", list(st.values()).count("done") == 1, st)

        x, y, w, h = p.box("#main .lrow")
        x, y = x + 300, y + 20
        p.touch("#main .lrow", [("touchstart", x, y), ("touchmove", x - 20, y), ("touchmove", x - 100, y), ("touchmove", x - 160, y), ("touchend", x - 160, y)])
        p.pg.wait_for_timeout(700)
        t.check("Wischen nach links legt in den Papierkorb", sum(1 for x in s.tasks() if x.get("del")) == 1)

        menu = p.js("""async()=>{const el=document.querySelector('#main [data-id]');const b=el.getBoundingClientRect();
          const o={bubbles:true,clientX:b.x+20,clientY:b.y+10,pointerType:'touch',pointerId:5,isPrimary:true};
          el.dispatchEvent(new PointerEvent('pointerdown',o));await new Promise(r=>setTimeout(r,650));
          el.dispatchEvent(new PointerEvent('pointerup',o));el.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));
          return [...document.querySelectorAll('#dsh[open] button:not(.cancel)')].map(b=>b.textContent.trim())}""")
        t.check("Gedrückt halten öffnet kurzes Menü (höchstens 3 Einträge)", 1 <= len(menu) <= 3 and any("Auswählen" in m for m in menu), menu)
        p.pg.click("#dsh button:has-text('Auswählen')")
        p.pg.wait_for_timeout(400)
        t.check("„Auswählen“ startet die Mehrfachauswahl", p.js("document.body.classList.contains('selmode')&&document.querySelectorAll('#main .sel').length===1"))
        p.js("setSel(false)")
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_blatt_schliessen_und_suche(t, browser):
    with Server() as s:
        s.seed([task("a", "Alpha", D(0), D(2))])
        p = Page(browser, s.url, PHONE)
        p.pg.click("[data-v=list]")
        p.pg.wait_for_timeout(300)
        swipe = [("touchstart", 200, 300), ("touchmove", 200, 320), ("touchmove", 200, 420), ("touchmove", 200, 520), ("touchend", 200, 520)]
        p.js("document.querySelector('#main .lrow').click()")
        p.pg.wait_for_timeout(400)
        t.check("Antippen öffnet das Aufgabenblatt", p.js("document.getElementById('dlg').open"))
        p.touch("#dlg", swipe)
        p.pg.wait_for_timeout(500)
        t.check("Nach unten wischen schließt das unveränderte Blatt", not p.js("document.getElementById('dlg').open"))

        p.js("document.querySelector('#main .lrow').click()")
        p.pg.wait_for_timeout(400)
        p.pg.fill("#f_title", "Geändert")
        p.touch("#dlg", swipe)
        p.pg.wait_for_timeout(500)
        t.check("Bei Änderungen fragt das Blatt nach (Verwerfen)", p.js("document.getElementById('dlg').open&&document.getElementById('dsh').open"))
        p.pg.click("#dsh button:has-text('Verwerfen')")
        p.pg.wait_for_timeout(400)
        t.check("Verwerfen schließt ohne zu speichern", not p.js("document.getElementById('dlg').open") and s.task("a")["title"] == "Alpha")

        p.touch("#main", [("touchstart", 200, 200), ("touchmove", 200, 230), ("touchmove", 200, 300), ("touchmove", 200, 400), ("touchend", 200, 400)])
        p.pg.wait_for_timeout(600)
        t.check("Weit nach unten ziehen öffnet die Suche", p.js("document.getElementById('filters').classList.contains('open')"))
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_filterblatt_wischen_wendet_nichts_an(t, browser):
    with Server() as s:
        s.seed([task("a", "Alpha", D(0), who="Lasse"), task("b", "Beta", D(0), who="Melanie")])
        p = Page(browser, s.url, PHONE)
        p.pg.click("[data-v=list]")
        p.pg.wait_for_timeout(300)
        p.pg.click("#fbtn")
        p.pg.wait_for_timeout(400)
        t.check("Filterknopf öffnet das Filterblatt", p.js("document.getElementById('dlf').open"))
        x, y, w, h = p.box("#dlf [data-fa=w]")
        x, y = x + w / 2, y + h / 2
        p.touch("#dlf [data-fa=w]", [("touchstart", x, y), ("touchmove", x, y + 30), ("touchmove", x, y + 150), ("touchmove", x, y + 260), ("touchend", x, y + 260)])
        p.pg.wait_for_timeout(500)
        t.check("Wischen auf einem Filter schließt das Blatt, ohne zu filtern", not p.js("document.getElementById('dlf').open") and p.js("fCount()") == 0)
        p.close()
