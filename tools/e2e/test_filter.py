"""Filter (1.51): Verantwortlich als Mehrfachauswahl, Start nur nach Person gefiltert, Kennzahlen passend zum Filter."""
import datetime
from common import DESKTOP, PHONE, Page, Server, task

T = datetime.date.today()
D = lambda n: str(T + datetime.timedelta(n))
DATEN = [task("l1", "Lasse 1", D(0), D(0), who="Lasse", tags=["Haus"]), task("l2", "Lasse 2", D(0), D(0), who="Lasse", tags=["Garten"], status="done"),
         task("m1", "Melanie 1", D(0), D(0), who="Melanie", tags=["Haus"]), task("x1", "Michel 1", D(0), D(0), who="Michel"),
         task("n1", "Niemand", D(0), D(0))]


def test_verantwortlich_mehrfach_und_kennzahlen(t, browser):
    with Server() as s:
        s.seed(DATEN, tags=[{"n": "Haus", "c": "sea"}, {"n": "Garten", "c": "mint"}])
        p = Page(browser, s.url, DESKTOP)
        p.pg.wait_for_timeout(1200)
        p.pg.click("[data-v=list]")
        p.pg.wait_for_timeout(300)
        p.pg.click("#fbtn")
        p.pg.wait_for_timeout(200)
        p.pg.click("#fbody [data-fa=w][data-fv=Lasse]")
        p.pg.click("#fbody [data-fa=w][data-fv=Melanie]")
        p.pg.wait_for_timeout(200)
        on = p.js("[...document.querySelectorAll('#fbody [data-fa=w].on')].map(b=>b.dataset.fv)")
        t.check("Verantwortlich: zwei Personen gleichzeitig wählbar", sorted(on) == ["Lasse", "Melanie"], on)
        t.check("Passend: 3 von 5", "3 von 5" in p.js("document.getElementById('f_cnt').textContent"))
        p.js("document.getElementById('dlf').close()")
        p.pg.wait_for_timeout(1000)
        kp = p.js("document.getElementById('kpis').textContent")
        t.check("Kennzahlen beziehen sich auf den Filter (1 von 3 erledigt = 33 %)", kp.startswith("33%") and "1 von 3" in kp, kp)
        p.pg.click("[data-v=gantt]")
        p.pg.wait_for_timeout(900)
        kp = p.js("document.getElementById('kpis').textContent")
        t.check("Auch im Zeitstrahl", kp.startswith("33%") and "1 von 3" in kp, kp)
        t.check("Seitenleiste „Wer“ zeigt beide gewählt", sorted(p.js("[...document.querySelectorAll('#chips [data-cw].on')].map(b=>b.dataset.cw)")) == ["Lasse", "Melanie"])
        p.pg.click("#chips [data-cw='']")
        p.pg.wait_for_timeout(300)
        t.check("„Alle“ setzt den Filter zurück", p.js("fwho.size") == 0)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_start_nur_nach_person(t, browser):
    with Server() as s:
        s.seed(DATEN, tags=[{"n": "Haus", "c": "sea"}, {"n": "Garten", "c": "mint"}])
        p = Page(browser, s.url, PHONE, setup=lambda pg: pg.add_init_script("try{localStorage.setItem('haus-me','Lasse');localStorage.setItem('haus-hwho','__all')}catch(e){}"))
        p.pg.wait_for_timeout(1200)
        p.pg.click("[data-v=home]")
        p.pg.wait_for_timeout(300)
        hh = lambda: p.js("document.querySelector('.hero .hh').textContent")
        t.check("Ohne Filter: Alle (1 von 5)", hh() == "1 von 5 erledigt", hh())
        p.js("ftags.add('Garten');render()")
        p.pg.wait_for_timeout(300)
        t.check("Tag-Filter gilt auf Start nicht", hh() == "1 von 5 erledigt", hh())
        p.js("ftags.clear();fwho.add('Lasse');fwho.add('Melanie');render()")
        p.pg.wait_for_timeout(300)
        t.check("Filter Verantwortlich gilt auf Start (Lasse + Melanie: 1 von 3)", hh() == "1 von 3 erledigt", hh())
        t.check("Oben sind beide Personen markiert", sorted(p.js("[...document.querySelectorAll('.hpick button.on')].map(b=>b.dataset.hw)")) == ["Lasse", "Melanie"])
        p.pg.click(".hpick [data-hw=Melanie]")
        p.pg.wait_for_timeout(300)
        t.check("Antippen oben schaltet den Filter um (nur noch Lasse: 1 von 2)", hh() == "1 von 2 erledigt" and sorted(p.js("[...fwho]")) == ["Lasse"], hh())
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()
