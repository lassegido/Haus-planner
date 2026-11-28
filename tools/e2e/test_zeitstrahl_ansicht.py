"""Zeitstrahl-Ansicht (1.54): Wochen, Zoom, zwei Gruppierungsebenen, Personen-Kürzel, Erledigte mit Haken, Antippen öffnet,
neue Statusfarben, einklappbare Seitenleiste."""
import datetime
from common import DESKTOP, IPAD, PHONE, Page, Server, task
from test_zeitstrahl_planer import zeitstrahl

T = datetime.date.today()
D = lambda n: str(T + datetime.timedelta(n))
GROSS = {**DESKTOP, "viewport": {"width": 1400, "height": 1000}}
IPAD_QUER = {**IPAD, "viewport": {"width": 1180, "height": 820}}


def seed(s):
    s.seed([task("a", "Babyalbum", D(0), D(4), proj="Baby", who="Melanie"),
            task("b", "Kinderzimmer streichen", D(1), D(6), proj="Haus", who="Lasse"),
            task("c", "Dankeskarten verschicken", D(-3), D(-1), proj="Baby", who="Lasse", status="done"),
            task("d", "Wickeltisch", D(2), D(3), proj="Baby", who="Lasse"),
            task("e", "Steuer", D(-2), D(-2), status="done", fail=True)])


def test_wochen_und_zoom(t, browser):
    with Server() as s:
        seed(s)
        p = Page(browser, s.url, GROSS)
        zeitstrahl(p)
        t.check("Vier Stufen: Tage, Wochen, Monate, Jahre", p.js("[...document.querySelectorAll('[data-gm]')].map(b=>b.textContent)") == ["Tage", "Wochen", "Monate", "Jahre"])
        p.pg.click("[data-gm=week]")
        p.pg.wait_for_timeout(300)
        kw = "KW %d" % T.isocalendar()[1]
        t.check("Wochen: aktuelle Kalenderwoche markiert", p.js("document.querySelector('.gh .tdn').textContent") == kw, p.js("document.querySelector('.gh .tdn').textContent"))
        t.check("Wochen: Spalte = 7 Tage", abs(p.js("+document.querySelector('.gb').dataset.ppd") - 12) < 0.01)
        t.check("Wahl bleibt gespeichert", p.js("prefGet('gmode')") == "week")
        p.pg.click("[data-gm=day]")
        p.pg.wait_for_timeout(300)
        w0 = p.js("document.querySelector('.gb').width.baseVal.value")
        p.pg.fill("#gzoom", "200")
        p.pg.dispatch_event("#gzoom", "change")
        p.pg.wait_for_timeout(400)
        t.check("Zoom 200 %: Tagesspalte doppelt so breit", p.js("+document.querySelector('.gb').dataset.ppd") == 76)
        t.check("Zoom gespeichert", p.js("prefGet('gzoom')") == "2")
        p.pg.fill("#gzoom", "50")
        p.pg.wait_for_timeout(400)
        lab = p.js("[...document.querySelectorAll('.gh text:not(.l1)')].map(x=>x.textContent)")
        t.check("Eng: Wochentage nur als Buchstabe", "M" in lab and "Mo" not in lab, lab[:14])
        t.check("Eng: Spalten schmaler, Zeitraum gleich lang", p.js("+document.querySelector('.gb').dataset.ppd") == 19 and w0 > 0)
        p.pg.click("[data-gm=month]")
        p.pg.wait_for_timeout(300)
        lab = p.js("[...document.querySelectorAll('.gh text:not(.l1)')].map(x=>x.textContent)")
        t.check("Monate eng: Anfangsbuchstabe", all(len(x) == 1 for x in lab), lab)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_zwei_ebenen_und_personen(t, browser):
    with Server() as s:
        seed(s)
        p = Page(browser, s.url, GROSS)
        zeitstrahl(p)
        p.js("(()=>{$('grp').value='proj';$('grp').dispatchEvent(new Event('change'));setGrp2('who')})()")
        p.pg.wait_for_timeout(400)
        heads = p.js("[...document.querySelectorAll('.gl .gh2')].map(h=>h.dataset.lv+':'+h.querySelector('span').textContent)")
        t.check("Erst Projekt, dann Person", heads[0] == "1:Baby" and sorted(heads[1:3]) == ["2:Lasse", "2:Melanie"] and "1:Haus" in heads, heads)
        t.check("Gruppierung gespeichert", p.js("[localStorage.getItem('haus-grp'),localStorage.getItem('haus-grp2')]") == ["proj", "who"])
        t.check("Menü bietet „Dann gruppieren“", "Dann gruppieren" in p.js("(()=>{$('more').click();return [...document.querySelectorAll('.pop button, #pop button, [role=menu] button')].map(b=>b.textContent).join('|')})()"))
        p.pg.keyboard.press("Escape")
        av = p.js("[...document.querySelectorAll('.gb .gav')].map(g=>g.closest('[data-id]').dataset.id+g.classList[1])")
        t.check("Balken tragen das Kürzel in Personenfarbe", "aam" in av and "bal" in av, av)
        t.check("Zeilen links mit Kürzel", p.js("!!document.querySelector('.gl .gr[data-id=a] .av.am')"))
        # Ziehen über beide Ebenen: Wickeltisch (Baby/Lasse) nach Haus/Lasse → Projekt wechselt, Person bleibt
        p.js("void dropRow('d',{after:'b',from:'Baby\\u001fLasse',to:'Haus\\u001fLasse'})")
        p.pg.wait_for_timeout(500)
        d = s.task("d")
        t.check("Andere obere Gruppe: Projekt übernommen, Person bleibt", d["proj"] == "Haus" and d["who"] == "Lasse", d)
        t.check("Hinweis nennt nur, was sich ändert", p.js("document.getElementById('toast').textContent").startswith("„Wickeltisch“ → Haus"), p.js("document.getElementById('toast').textContent"))
        p.js("void dropRow('d',{from:'Haus\\u001fLasse',to:'Baby\\u001fMelanie'})")
        p.pg.wait_for_timeout(500)
        d = s.task("d")
        t.check("Beide Ebenen: Projekt und Person übernommen", d["proj"] == "Baby" and d["who"] == "Melanie", d)
        p.pg.click("[data-v=list]")
        p.pg.wait_for_timeout(300)
        t.check("Liste: zwei Ebenen", p.js("document.querySelectorAll('tr.grp2').length") >= 2)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_erledigt_farben_antippen(t, browser):
    with Server() as s:
        seed(s)
        p = Page(browser, s.url, IPAD)
        zeitstrahl(p)
        c = p.js("document.querySelector('.gbar[data-id=c] .bo').textContent")
        t.check("Erledigt: Haken vor dem Namen", c.startswith("✓ "), c)
        t.check("Nicht geschafft: Kreuz", p.js("document.querySelector('.gbar[data-id=e] .bo').textContent").startswith("✕ "))
        t.check("Erledigt: kein Verknüpfungspunkt, keine Griffe", not p.js("!!document.querySelector('.gbar[data-id=c] .gdep, .gbar[data-id=c] .gh1')"))
        t.check("Offen: Verknüpfungspunkt ausgefüllt", p.js("getComputedStyle(document.querySelector('.gbar[data-id=a] .gdep')).fill") != "none")
        col = p.js("['--todo','--doing','--done','--fail'].map(v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim().toUpperCase())")
        t.check("Statusfarben: Offen grau-blau, In Arbeit blau, Erledigt grün, Nicht geschafft rot", col == ["#7890A3", "#3B82C4", "#3E9F68", "#C2362B"], col)
        p.pg.tap(".gbar[data-id=a] rect")
        p.pg.wait_for_timeout(500)
        t.check("Antippen öffnet die Aufgabe", p.js("document.getElementById('dlg').open") and p.js("f_title.value") == "Babyalbum")
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_seitenleiste_einklappen(t, browser):
    with Server() as s:
        seed(s)
        p = Page(browser, s.url, IPAD_QUER)
        w = lambda: p.js("document.querySelector('.side').getBoundingClientRect().width")
        t.check("iPad quer: volle Seitenleiste", w() > 200, w())
        p.pg.click("#sidetog")
        p.pg.wait_for_timeout(400)
        t.check("Eingeklappt: schmale Symbolleiste", w() < 100, w())
        t.check("Ansichten bleiben erreichbar", p.js("[...document.querySelectorAll('.tabs button')].filter(b=>b.offsetParent).length") >= 4)
        zeitstrahl(p)
        t.check("Zeitstrahl in eingeklappter Leiste erreicht", p.js("view") == "gantt")
        p.pg.reload()
        p.pg.wait_for_timeout(800)
        t.check("Bleibt nach Neuladen eingeklappt", w() < 100 and p.js("document.documentElement.classList.contains('mini')"))
        p.pg.click("#sidetog")
        p.pg.wait_for_timeout(400)
        t.check("Wieder ausklappen", w() > 200)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()
        p = Page(browser, s.url, PHONE)
        t.check("Handy: kein Einklapp-Knopf", not p.js("document.getElementById('sidetog').offsetParent"))
        p.close()
