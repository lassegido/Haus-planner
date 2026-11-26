"""„Nicht geschafft“ (1.42): abschließen ohne Erfolg, BUSTED! nur auf der Startseite, Serie, Board sortiert nach Abschluss, Board statt Tafel."""
import datetime
from common import DESKTOP, PHONE, Page, Server, task

T = datetime.date.today()
D = lambda n: str(T + datetime.timedelta(n))
NOW = datetime.datetime.now(datetime.timezone.utc)
UTC = lambda m: (NOW - datetime.timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M")
ALS_LASSE = lambda pg: pg.add_init_script("try{localStorage.setItem('haus-me','Lasse')}catch(e){}")
HERO = "[document.querySelector('.hero .hh').textContent,document.querySelector('.hero .hsub').textContent]"


def erledigt(tid, title, tage_her, **kw):
    d = D(-tage_her)
    return task(tid, title, d, d, who="Lasse", status="done", log=[{"t": d + "T09:00", "a": "Lasse", "k": "h", "x": "Status: Offen → Erledigt"}], **kw)


def menu_waehlen(p, tid, label):
    p.js("id=>{taskMenu(id)}", tid)
    p.pg.wait_for_timeout(250)
    items = p.js("[...document.querySelectorAll('#dsh button')].map(b=>b.textContent)")
    if label in items:
        p.pg.click("#dsh button:has-text('%s')" % label)
        p.pg.wait_for_timeout(700)
    return items


def test_nicht_geschafft_auf_der_startseite(t, browser):
    with Server() as s:
        s.seed([erledigt("e1", "Gestern", 1), erledigt("e2", "Vorgestern", 2), erledigt("e3", "Vor drei Tagen", 3),
                task("m", "Müll rausbringen", D(0), D(0), who="Lasse", rec={"n": 1, "u": "d"}),
                task("h", "Blumen gießen", D(0), D(0), who="Lasse")])
        p = Page(browser, s.url, PHONE, setup=ALS_LASSE)
        p.pg.click("[data-v=home]")
        p.pg.wait_for_timeout(300)
        t.check("Vorher: Serie 3 Tage", "3 Tage" in p.js("document.querySelector('.hstreak').textContent"))
        items = menu_waehlen(p, "m", "Nicht geschafft")
        t.check("Gedrückt halten bietet „Nicht geschafft“", "Nicht geschafft" in items, items)
        bust = p.js("(document.querySelector('.bust')||{}).textContent||''")
        t.check("Startseite: groß „BUSTED!“ mit Aufgabe", "BUSTED!" in bust and "Müll rausbringen" in bust, bust)
        m = s.task("m")
        t.check("Gespeichert als abgeschlossen, nicht geschafft", m["status"] == "done" and m.get("fail") is True, m)
        t.check("Verlauf: „Status: Offen → Nicht geschafft“", m["log"][-1]["x"] == "Status: Offen → Nicht geschafft", m["log"][-1])
        nxt = [x for x in s.tasks() if x["title"] == "Müll rausbringen" and x["id"] != "m"]
        t.check("Tägliche Aufgabe: die nächste ist für morgen angelegt", len(nxt) == 1 and nxt[0]["start"] == D(1) and not nxt[0].get("fail"), nxt)
        t.check("Hinweis mit Rückgängig", "Nicht geschafft" in (p.pg.text_content("#toast") or ""))
        t.check("Kein Konfetti", not p.js("!!document.querySelector('.confetti')"))
        p.pg.wait_for_timeout(2400)
        t.check("BUSTED! verschwindet von selbst", not p.js("!!document.querySelector('.bust')"))
        h = p.js(HERO)
        t.check("Ring: zählt mit, aber nicht als erledigt (0 von 2)", h[0] == "0 von 2 erledigt" and "1 nicht geschafft" in h[1], h)
        st = p.js("document.querySelector('.hstreak').textContent")
        t.check("Serie reißt sofort", "Serie startet morgen neu" in st, st)
        t.check("Satz über dem GIF bleibt motivierend", "Eine Aufgabe für heute" in p.js("(document.querySelector('.mwhy')||{}).textContent||''") or
                p.js("!document.querySelector('.mwhy')"))
        p.js("void setStatus(byId('h'),'done')")
        p.pg.wait_for_timeout(700)
        h = p.js(HERO)
        why = p.js("(document.querySelector('.mwhy')||{}).textContent||''")
        t.check("Rest erledigt: 1 von 2, Satz nennt beides", h[0] == "1 von 2 erledigt" and (not why or "1 geschafft, 1 nicht" in why), (h, why))
        items = menu_waehlen(p, "h", "Nicht geschafft")
        t.check("Erledigte Aufgaben bieten „Nicht geschafft“ nicht an", "Nicht geschafft" not in items, items)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_busted_nur_auf_der_startseite(t, browser):
    with Server() as s:
        s.seed([task("a", "Fenster putzen", D(0), D(0), who="Lasse"), task("b", "Auto waschen", D(0), D(0), who="Lasse"),
                task("c", "Keller", D(0), D(0), who="Lasse")])
        p = Page(browser, s.url, PHONE, setup=ALS_LASSE)
        p.pg.click("[data-v=list]")
        p.pg.wait_for_timeout(300)
        menu_waehlen(p, "a", "Nicht geschafft")
        t.check("Liste: kein BUSTED!", not p.js("!!document.querySelector('.bust')"))
        t.check("Liste: Zeile mit ✕ und „nicht geschafft“", p.js("!!document.querySelector('.lrow.fail .ring.fail')") and
                "nicht geschafft" in p.js("document.querySelector('.lrow.fail .hd').textContent"))
        p.pg.click("#toast button")
        p.pg.wait_for_timeout(500)
        a = s.task("a")
        t.check("Rückgängig: wieder offen, ohne Markierung", a["status"] == "todo" and "fail" not in a, a)
        # Aufgabenblatt, von der Startseite geöffnet
        p.pg.click("[data-v=home]")
        p.pg.wait_for_timeout(300)
        p.js("openDlg('b')")
        p.pg.wait_for_timeout(300)
        t.check("Blatt: vierter Status „Nicht geschafft“", p.js("[...document.querySelectorAll('#f_stseg button')].map(b=>b.textContent)") == ["Offen", "In Arbeit", "Erledigt", "Nicht geschafft"])
        p.pg.click("#f_stseg [data-s=fail]")
        p.pg.click("#b_save")
        p.pg.wait_for_timeout(700)
        t.check("Blatt von der Startseite: BUSTED!", p.js("!!document.querySelector('.bust')"))
        t.check("Gespeichert als nicht geschafft", s.task("b")["status"] == "done" and s.task("b").get("fail") is True, s.task("b"))
        p.js("document.querySelector('.bust').click()")
        p.pg.wait_for_timeout(400)
        t.check("Antippen schließt sofort", not p.js("!!document.querySelector('.bust')"))
        p.js("openDlg('b')")
        p.pg.wait_for_timeout(300)
        t.check("Wieder geöffnet: „Nicht geschafft“ gewählt", p.js("f_status.value") == "fail")
        p.pg.click("#f_stseg [data-s=done]")
        p.pg.click("#b_save")
        p.pg.wait_for_timeout(700)
        t.check("Auf Erledigt umgestellt: Markierung weg", s.task("b")["status"] == "done" and "fail" not in s.task("b"), s.task("b"))
        p.js("prefSet('fun','0')")
        menu_waehlen(p, "c", "Nicht geschafft")
        t.check("Sprüche, GIFs und Konfetti aus: kein BUSTED!", not p.js("!!document.querySelector('.bust')") and s.task("c").get("fail") is True)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_board_zuletzt_abgeschlossen_oben(t, browser):
    with Server() as s:
        log = lambda m, z="Erledigt": [{"t": UTC(m), "a": "Lasse", "k": "h", "x": "Status: Offen → " + z}]
        s.seed([task("alt", "Vor einer Woche", D(-30), D(-29), status="done", log=log(7 * 1440)),
                task("neu", "Gerade eben", D(-40), D(-40), status="done", log=log(1)),
                task("mitte", "Vor einer Stunde", D(5), D(6), status="done", log=log(60)),
                task("nix", "Nicht geschafft vorhin", D(0), D(0), status="done", fail=True, log=log(30, "Nicht geschafft")),
                task("ohne", "Ohne Verlauf", D(-90), D(-90), status="done"),
                task("o", "Offen", D(0), D(1))])
        for dev in (PHONE, DESKTOP):
            p = Page(browser, s.url, dev)
            p.pg.click("[data-v=board]")
            p.pg.wait_for_timeout(400)
            order = p.js("[...document.querySelectorAll('.colm[data-s=done] .card')].map(c=>c.dataset.id)")
            t.check("Board, Erledigt: zuletzt abgeschlossen oben (auch nicht geschaffte)", order == ["neu", "nix", "mitte", "alt", "ohne"], order)
            t.check("Nicht geschafft ist auf der Karte benannt", "Nicht geschafft" in p.js("document.querySelector('.card.fail').textContent"))
            t.check("Überschrift heißt „Board“", p.js("document.getElementById('ttl').textContent") == "Board")
            t.check("keine Skriptfehler", not p.errors, p.errors)
            p.close()


def test_zaehlt_nicht_als_erledigt(t, browser):
    with Server() as s:
        s.api("api/task", task("z", "Z", D(0), status="todo", fail=True))
        t.check("Server: Markierung nur bei abgeschlossenen Aufgaben", "fail" not in s.task("z"))
        s.seed([task("p1", "P1", D(-2), D(-2), proj="Bad", status="done"), task("p2", "P2", D(-2), D(-2), proj="Bad", status="done", fail=True),
                task("p3", "P3", D(-2), D(-2), proj="Bad", status="done"), task("p4", "P4", D(1), D(1), proj="Bad")])
        p = Page(browser, s.url, DESKTOP)
        p.pg.click("[data-v=list]")
        p.pg.wait_for_timeout(300)
        p.pg.wait_for_timeout(900)
        kp = p.js("document.getElementById('kpis').textContent")
        t.check("Kennzahlen ohne nicht geschaffte: 2 von 4 erledigt = 50 %", kp.startswith("50%") and "2 von 4" in kp, kp)
        t.check("Tabelle zeigt „Nicht geschafft“", "Nicht geschafft" in p.js("document.querySelector('table').textContent"))
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()
