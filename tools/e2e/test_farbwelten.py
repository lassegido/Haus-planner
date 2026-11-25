"""Farbwelten (Kontrast in Hell und Dunkel, Polarlicht) und die Tiefe aus 1.40 (Schatten, Verläufe, Glanz)."""
import datetime
from common import DESKTOP, PHONE, Page, Server, task

T = datetime.date.today()
D = lambda n: str(T + datetime.timedelta(n))

# Löst eine Farbe (auch color-mix und var()) über ein Hilfselement in rgb() auf
COLORS = """(names)=>{const r={},el=document.createElement('i');document.body.appendChild(el);
  for(const n of names){el.style.color='var('+n+')';const s=getComputedStyle(el).color,m=s.match(/[\\d.]+/g).map(Number).slice(0,3);
    r[n]=s.startsWith('color(srgb')?m.map(v=>v*255):m}  /* color-mix liefert color(srgb 0..1) */
  el.remove();return r}"""
NAMES = ["--acc3", "--bg", "--grp", "--seg-tr", "--seg-tx", "--card", "--tx", "--mut", "--faint", "--acc", "--on-acc", "--acc2"]


def lum(c):
    f = lambda v: v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    r, g, b = [f(v / 255) for v in c]
    return .2126 * r + .7152 * g + .0722 * b


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def test_kontrast_aller_farbwelten(t, browser):
    with Server() as s:
        p = Page(browser, s.url, PHONE)
        worlds = p.js("DES.map(d=>[d[0],d[3]&&d[3].length,d[4]&&d[4].length])")
        t.check("Sieben Farbwelten: Portofino, Polarlicht und fünf neue", [w[0] for w in worlds] == ["porto", "polar", "wald", "lagune", "orchidee", "feige", "schiefer"], worlds)
        t.check("Jede Farbwelt hat alle Werte (Hell und Dunkel, Verlauf mit drei Farben)",
                all(w[1] in (None, 18) and w[2] in (None, 18) for w in worlds) and p.js("DK.length") == 18, worlds)
        t.check("Namen und Beschreibungen ohne Doppelungen", len(set(p.js("DES.map(d=>d[1])"))) == len(worlds) and len(set(p.js("DES.map(d=>d[2])"))) == len(worlds))
        # Keine Akzentfarbe, die wie ein Status aussieht: Farbton von --acc nicht rot, orange oder gelb (0–60° und ab 345°)
        hues = p.js("""DES.filter(d=>d[3]).flatMap(d=>[[d[0],d[3][11]],[d[0],d[4][11]]]).map(([k,c])=>{const n=parseInt(c.slice(1),16),r=(n>>16)/255,g=(n>>8&255)/255,b=(n&255)/255,
          mx=Math.max(r,g,b),mn=Math.min(r,g,b),d=mx-mn;let h=0;if(d){h=mx===r?((g-b)/d)%6:mx===g?(b-r)/d+2:(r-g)/d+4;h=(h*60+360)%360}return[k,Math.round(h)]})""")
        t.check("Keine rote, orange oder gelbe Akzentfarbe", all(60 < h < 345 for _, h in hues), hues)
        bad = []
        for k, *_ in worlds:
            for th in ("light", "dark"):
                p.js("([k,th])=>{prefSet('design',k);prefSet('theme',th);applyTheme()}", [k, th])
                c = p.js(COLORS, NAMES)
                need = [("Text auf Hintergrund", "--tx", "--bg", 4.5), ("Text auf Gruppen", "--tx", "--grp", 4.5),
                        ("Nebentext auf Hintergrund", "--mut", "--bg", 4.5), ("Nebentext auf Gruppen", "--mut", "--grp", 4.5),
                        ("Text im Umschalter", "--seg-tx", "--seg-tr", 4.5), ("Platzhalter", "--faint", "--grp", 3),
                        ("Akzent als Text", "--acc", "--bg", 4.5), ("Knopftext auf Akzent", "--on-acc", "--acc", 4.5),
                        ("Knopftext auf Verlaufsende", "--on-acc", "--acc2", 4.5)]
                for name, a, b, lim in need:
                    r = ratio(c[a], c[b])
                    if r < lim:
                        bad.append("%s %s %s: %.2f" % (k, th, name, r))
        t.check("Alle Farbwelten bestehen die Kontrastprüfung (WCAG, Hell und Dunkel)", not bad, bad)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_polarlicht_waehlbar(t, browser):
    with Server() as s:
        p = Page(browser, s.url, PHONE)
        p.settings("des")
        t.check("Polarlicht steht in den Einstellungen", "Polarlicht" in p.js("document.getElementById('s_body').textContent"))
        p.pg.click("#s_body [data-set='des:polar']")
        p.pg.wait_for_timeout(400)
        acc = p.js("getComputedStyle(document.documentElement).getPropertyValue('--acc').trim()")
        acc2 = p.js("getComputedStyle(document.documentElement).getPropertyValue('--acc2').trim()")
        t.check("Polarlicht setzt Indigo und Petrol", acc.upper() == "#5B4FC9" and acc2.upper() == "#23808F", (acc, acc2))
        t.check("Gespeichert", p.js("prefGet('design')") == "polar")
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_tiefe_und_verlaeufe(t, browser):
    with Server() as s:
        s.seed([task("a", "Offen", D(0), D(2), who="Lasse"), task("b", "In Arbeit", D(-1), D(3), status="doing"),
                task("c", "Erledigt", D(-3), D(-2), status="done")])
        for th in ("light", "dark"):
            p = Page(browser, s.url, {**DESKTOP, "color_scheme": th},
                     setup=lambda pg, th=th: pg.add_init_script("try{localStorage.setItem('haus-theme','%s')}catch(e){}" % th))
            cs = lambda sel, prop: p.js("([s,k])=>{const e=document.querySelector(s);return e?getComputedStyle(e)[k]:null}", [sel, prop])
            p.pg.click("[data-v=board]")
            p.pg.wait_for_timeout(400)
            t.check(th + ": Karten mit Verlauf und Schatten (auch bei festem Dunkelmodus)",
                    "gradient" in (cs(".card", "backgroundImage") or "") and cs(".card", "boxShadow") not in (None, "none"),
                    (cs(".card", "backgroundImage"), cs(".card", "boxShadow")))
            t.check(th + ": Tafel-Spalten oben in Statusfarbe getönt", "gradient" in (cs(".colm", "backgroundImage") or ""))
            t.check(th + ": Neu-Knopf mit Verlauf", "gradient" in (cs("#add", "backgroundImage") or cs(".add", "backgroundImage") or ""))
            p.pg.click("[data-v=gantt]")
            p.pg.wait_for_timeout(400)
            gl = p.js("[...document.querySelectorAll('.gbar')].map(g=>[!!g.querySelector('.ggl'),g.querySelector('.ggl')&&getComputedStyle(g.querySelector('.ggl')).pointerEvents])")
            t.check(th + ": Zeitstrahl-Balken mit Glanz, der das Ziehen nicht stört", gl and all(x == [True, "none"] for x in gl), gl)
            p.pg.click("[data-v=home]")
            p.pg.wait_for_timeout(400)
            stops = p.js("[...document.querySelectorAll('#rgG stop')].map(s=>s.getAttribute('style'))")
            t.check(th + ": Ring mit Verlauf über drei Farben", len(stops) == 3 and "--acc2" in stops[1], stops)
            t.check(th + ": keine Skriptfehler", not p.errors, p.errors)
            p.close()


def test_alte_farbwelt_wird_umgestellt(t, browser):
    with Server() as s:
        for old, new in (("salbei", "wald"), ("beere", "orchidee"), ("graphit", "schiefer")):
            p = Page(browser, s.url, PHONE, setup=lambda pg, o=old: pg.add_init_script("try{localStorage.setItem('haus-design','%s')}catch(e){}" % o))
            acc = p.js("getComputedStyle(document.documentElement).getPropertyValue('--acc').trim()").upper()
            want = p.js("k=>DES.find(d=>d[0]===k)[isDark()?4:3][11]", new).upper()
            t.check("%s wird zu %s (gespeichert und angewendet)" % (old, new), p.js("prefGet('design')") == new and acc == want, (p.js("prefGet('design')"), acc, want))
            p.settings("des")
            t.check("%s: in den Einstellungen ist %s gewählt" % (old, new),
                    p.js("k=>[...document.querySelectorAll('#s_body .opt.on')].map(b=>b.dataset.set)", new) == ["des:" + new])
            t.check("keine Skriptfehler", not p.errors, p.errors)
            p.close()
