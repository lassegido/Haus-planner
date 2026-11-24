#!/usr/bin/env python3
"""Prüft, ob eine CSS-Änderung das Aussehen verändert: berechnete Stile aller Elemente in ~100 Zuständen.

  python3 tools/build.py && python3 tools/style_diff.py save  /tmp/vorher.json.gz
  … CSS ändern …
  python3 tools/build.py && python3 tools/style_diff.py compare /tmp/vorher.json.gz

Zustände: 4 Geräte (Handy, iPad hoch/quer, Desktop) × hell/dunkel × Ansichten und Blätter, dazu auf dem Handy
alle Einstellungsseiten, Farbwelten, Schriften, Menüs, Auswahl, Suche, Willkommen, leere Seite, Echo-Ansicht.
Uhr und Daten sind fest, Animationen werden vor dem Messen beendet. Verglichen werden alle berechneten
CSS-Eigenschaften jedes Elements samt ::before/::after. „Keine Unterschiede“ heißt: pixelgleich in allen Zuständen.
"""
import gzip, json, os, sys, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "e2e"))
from common import DESKTOP, IPAD, PHONE, Page, Server, task  # noqa: E402

DAY = "2026-11-24"
DEV = {"Handy": PHONE, "iPad hoch": IPAD, "iPad quer": {**IPAD, "viewport": {"width": 1180, "height": 820}}, "Desktop": DESKTOP}

SNAP = """()=>{
  document.getAnimations().forEach(a=>{try{a.finish()}catch(e){}});
  const props=[...getComputedStyle(document.documentElement)].sort();
  const table=new Map(),rows=[];
  const sig=cs=>{const k=props.map(p=>cs.getPropertyValue(p)).join("\\u0001");if(!table.has(k))table.set(k,table.size);return table.get(k)};
  const all=[document.documentElement,...document.documentElement.querySelectorAll("*")];
  for(const el of all){
    if(el.closest("svg")&&el.tagName.toLowerCase()!=="svg")continue;
    const d=el.tagName.toLowerCase()+(el.id?"#"+el.id:"")+(typeof el.className==="string"&&el.className.trim()?"."+el.className.trim().split(/\\s+/).join("."):"");
    rows.push([d,sig(getComputedStyle(el)),sig(getComputedStyle(el,"::before")),sig(getComputedStyle(el,"::after"))]);
  }
  return {props,table:[...table.keys()].map(k=>k.split("\\u0001")),rows};
}"""


def seed(s):
    D = lambda n: str(__import__("datetime").date(2026, 11, 24) + __import__("datetime").timedelta(n))
    s.seed([task("a", "Büro fertigstellen", D(-2), D(3), who="Lasse", tags=["Haus"], proj="Schöner Wohnen", prio=1, status="doing",
                 notes="Boden zuerst", checklist=[{"t": "Boden verlegen", "d": True}, {"t": "Schreibtisch aufbauen", "d": False}],
                 log=[{"t": DAY + "T08:00", "a": "Lasse", "k": "c", "x": "Kommentar"}]),
            task("b", "Garage fertigstellen", D(1), D(8), who="Lasse, Melanie", tags=["Haus", "Garten"], proj="Schöner Wohnen", deps=["a"]),
            task("c", "Dankeskarten verschicken", D(-4), D(-1), who="Melanie", tags=["Sonstiges"], prio=2),
            task("d", "Zaun streichen", D(0), D(0), tags=["Garten"], prio=3, rec={"n": 1, "u": "w"}),
            task("e", "Rechnung bezahlen", D(-6), D(-6), who="Lasse", status="done"),
            task("f", "Richtfest", D(12), D(12), ms=True, proj="Schöner Wohnen"),
            task("g", "Alt im Archiv", D(-30), D(-29), arch=True), task("h", "Im Papierkorb", D(-3), D(-3), **{"del": True, "delAt": D(-1)})],
           tags=[{"n": "Haus", "c": "sky", "i": "house"}, {"n": "Garten", "c": "mint"}, {"n": "Sonstiges", "c": "sand"}, {"n": "Schöner Wohnen", "c": "sea", "p": 1}])


# Tut so, als wäre Home Assistant verbunden (sonst fehlen Erinnerung, Alexa usw. in den Einstellungen)
HA_ON = "haInfo=Object.assign({},haInfo,{api:true,notify:['mobile_app_iphone_von_lasse','mobile_app_ipad'],nwho:{mobile_app_iphone_von_lasse:'Lasse'},time:'08:00',alexa:true,echos:1,wsok:true});"


def C(p, sel):
    p.js("s=>document.querySelector(s).click()", sel)


def states():
    """(Name, Gerät, Aktion, Seitenzusatz, ohne Willkommen)"""
    out = []
    for dev in DEV:
        for th in ("light", "dark"):
            pre = lambda p, th=th: p.js("prefSet('theme','%s');applyTheme()" % th)
            for v in ("home", "board", "list", "gantt", "cal"):
                out.append(("%s %s %s" % (dev, th, v), dev, lambda p, v=v, pre=pre: (pre(p), C(p, "[data-v=%s]" % v))))
            out.append(("%s %s Aufgabe" % (dev, th), dev, lambda p, pre=pre: (pre(p), p.js("openDlg('a');document.querySelectorAll('#dlg details').forEach(d=>d.open=true)"))))
            out.append(("%s %s Filter" % (dev, th), dev, lambda p, pre=pre: (pre(p), C(p, "[data-v=list]"), C(p, "#fbtn"))))
            out.append(("%s %s Einstellungen" % (dev, th), dev, lambda p, pre=pre: (pre(p), p.js("openSettings()"))))
            out.append(("%s %s Menü" % (dev, th), dev, lambda p, pre=pre: (pre(p), C(p, "#more"))))
    ph = "Handy"
    for pg in ("des", "font", "theme", "me", "rem", "remt", "keys", "ki", "alexa", "show"):
        out.append(("Handy Einstellungen " + pg, ph, lambda p, pg=pg: p.js(HA_ON + "openSettings();sPage='%s';drawSettings()" % pg)))
    for d in ("salbei", "beere", "graphit"):
        for th in ("light", "dark"):
            for v in ("home", "list"):
                out.append(("Handy %s %s %s" % (d, th, v), ph, lambda p, d=d, th=th, v=v: (p.js("prefSet('design','%s');prefSet('theme','%s');applyTheme()" % (d, th)), C(p, "[data-v=%s]" % v))))
    for f in ("sys", "fraunces"):
        out.append(("Handy Schrift " + f, ph, lambda p, f=f: (p.js("prefSet('font','%s');applyFont()" % f), C(p, "[data-v=home]"))))
    out += [
        ("Handy Aktionsblatt", ph, lambda p: p.js("void taskMenu('a')")),
        ("Handy Auswahl", ph, lambda p: (C(p, "[data-v=list]"), p.js("setSel(true);sel.add('a');applySel()"))),
        ("Handy Suche", ph, lambda p: (C(p, "[data-v=list]"), C(p, "#ftog"))),
        ("Handy Export", ph, lambda p: p.js("document.getElementById('dlx').showModal()")),
        ("Handy Tags", ph, lambda p: p.js("openMan()")),
        ("Handy Archiv", ph, lambda p: p.js("openArch()")),
        ("Handy neue Aufgabe", ph, lambda p: C(p, "#add")),
        ("Handy Zeitstrahl Monate", ph, lambda p: (C(p, "[data-v=gantt]"), C(p, "[data-gm=month]"))),
        ("Handy Zeitstrahl Jahre", ph, lambda p: (C(p, "[data-v=gantt]"), C(p, "[data-gm=year]"))),
        ("Handy Start zweite Kachel", ph, lambda p: (C(p, "[data-v=home]"), p.js("document.querySelectorAll('[data-ht]')[1].click()"))),
        ("Handy Hinweis", ph, lambda p: p.js("toast('Gespeichert',()=>{},'Rückgängig',60000)")),
        ("Handy Rückfrage", ph, lambda p: p.js("void confirmSheet('Wirklich löschen?','Löschen',true)")),
        ("Desktop Auswahl Board", "Desktop", lambda p: (C(p, "[data-v=board]"), p.js("setSel(true);sel.add('a');applySel()"))),
    ]
    return out


def capture(browser, name, dev, action, url_extra="", onboarded=True, empty=False, srv=None):
    p = Page(browser, srv.url + url_extra, {**(DEV[dev] if isinstance(dev, str) else dev), "reduced_motion": "reduce"}, onboarded=onboarded, wait=False,
             setup=lambda pg: pg.clock.set_fixed_time(DAY + "T10:00:00"))
    try:
        if not url_extra:
            p.ready()
        else:
            p.pg.wait_for_timeout(1200)
        if action:
            action(p)
        p.pg.wait_for_timeout(450)
        snap = p.js(SNAP)
        return snap, p.errors
    finally:
        p.close()


def run_all(browser):
    res, errs = {}, {}
    with Server() as s:
        seed(s)
        for name, dev, action in states():
            try:
                res[name], e = capture(browser, name, dev, action, srv=s)
            except Exception as ex:
                res[name], e = None, ["Zustand nicht herstellbar: %s" % str(ex).splitlines()[0][:160]]
            if e:
                errs[name] = e
        res["Echo hell"], _ = capture(browser, "Echo", {"viewport": {"width": 960, "height": 480}, "has_touch": True}, None, "?anzeige&hell", False, srv=s)
        res["Echo dunkel Lasse"], _ = capture(browser, "Echo", {"viewport": {"width": 960, "height": 480}, "has_touch": True}, None, "?anzeige&dunkel&wer=Lasse", False, srv=s)
    with Server() as s:
        res["Handy Willkommen"], _ = capture(browser, "Willkommen", "Handy", lambda p: p.pg.wait_for_function("document.getElementById('dsh').open", timeout=5000), "", False, srv=s)
        for v in ("home", "list", "board"):
            res["Handy leer " + v], _ = capture(browser, "leer", "Handy", lambda p, v=v: (p.ready(), C(p, "[data-v=%s]" % v)), "?", True, srv=s)
    return res, errs


def expand(snap):
    t = snap["table"]
    return [(d, t[a], t[b], t[c]) for d, a, b, c in snap["rows"]]


def diff(old, new):
    out = []
    for st in old:
        if st not in new:
            out.append((st, "Zustand fehlt"))
            continue
        a, b = old[st], new[st]
        if a is None or b is None:
            out.append((st, "Zustand nicht messbar")) if a != b else None
            continue
        if a["props"] != b["props"]:
            out.append((st, "andere Eigenschaftsliste"))
            continue
        ra, rb = expand(a), expand(b)
        if [r[0] for r in ra] != [r[0] for r in rb]:
            out.append((st, "anderer Seitenaufbau (%d → %d Elemente)" % (len(ra), len(rb))))
            continue
        for x, y in zip(ra, rb):
            for k, part in ((1, ""), (2, "::before"), (3, "::after")):
                if x[k] != y[k]:
                    ch = ["%s: %s → %s" % (p, u, v) for p, u, v in zip(a["props"], x[k], y[k]) if u != v]
                    out.append((st, "%s%s  %s" % (x[0][:60], part, "; ".join(ch[:4]))))
    return out


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("save", "compare"):
        sys.exit(__doc__)
    from playwright.sync_api import sync_playwright
    t0 = time.time()
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        res, errs = run_all(b)
        b.close()
    print("%d Zustände in %.0f s" % (len(res), time.time() - t0))
    for k, v in errs.items():
        print("Skriptfehler in %s: %s" % (k, v[:2]))
    if sys.argv[1] == "save":
        with gzip.open(sys.argv[2], "wt", encoding="utf-8") as f:
            json.dump(res, f)
        print("Gespeichert:", sys.argv[2])
        return
    with gzip.open(sys.argv[2], "rt", encoding="utf-8") as f:
        old = json.load(f)
    d = diff(old, res)
    if not d:
        print("Keine Unterschiede: alle berechneten Stile in allen Zuständen gleich.")
        return
    print("%d Unterschiede:" % len(d))
    for st, msg in d[:80]:
        print("  [%s] %s" % (st, msg))
    sys.exit(1)


if __name__ == "__main__":
    main()
