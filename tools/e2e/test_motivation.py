"""Motivation auf der Startseite: Serie, gemeinsame Woche, Abzeichen und Feiern."""
import datetime
from common import PHONE, Page, Server, task

T = datetime.date.today()
D = lambda n: str(T + datetime.timedelta(n))
UM = lambda h: (lambda pg: pg.add_init_script("window.PLANNER_HOUR=%d" % h))
ALS_LASSE = lambda pg: pg.add_init_script("try{localStorage.setItem('haus-me','Lasse')}catch(e){}")


def erledigt(tid, title, due, done, who="Lasse", actor="Lasse"):
    return task(tid, title, D(due), D(due), who=who, status="done",
                log=[{"t": D(done) + "T10:00", "a": actor, "k": "h", "x": "Status: Offen → Erledigt"}])


def daten():
    L = [erledigt("a1", "Gestern", -1, -1), erledigt("a2", "Vorgestern", -2, -2), erledigt("a4", "Vor vier Tagen", -4, -4),
         erledigt("a5", "Zu spät", -6, -5),  # an Tag -6 blieb etwas offen → Serie endet dort
         erledigt("a7", "Früh", -7, -9), erledigt("m1", "Melanies", -1, -1, who="Melanie", actor="iPhone von Melanie"),
         erledigt("g1", "Gemeinsam", -2, -2, who="Lasse, Melanie", actor="Alexa"),
         erledigt("a8", "Alt 1", -20, -20), erledigt("a9", "Alt 2", -21, -21),
         task("h1", "Heute fällig", D(0), D(0), who="Lasse")]
    return L


def test_serie_woche_abzeichen_feiern(t, browser):
    with Server() as s:
        s.seed(daten())
        p = Page(browser, s.url, PHONE, setup=ALS_LASSE)
        p.pg.click("[data-v=home]")
        p.pg.wait_for_timeout(300)
        st = p.js("document.querySelector('.hstreak').textContent")
        t.check("Serie: 4 Tage (leerer Tag unterbricht nicht, verspäteter Tag beendet)", st == "4 Tage am Stück", st)
        order = p.js("[...document.querySelector('.home').children].map(e=>e.className.split(' ')[0])")
        t.check("Reihenfolge: Tageskarte, Eingabe, Umschalter, Liste, Abzeichen, Überblick (zugeklappt)",
                [x for x in order if x != "hpick"] == ["hero", "qadd", "hseg", "pnl", "pnl", "pnl"] and p.js("!document.querySelector('.ovw').open"), order)
        p.js("document.querySelector('.ovw').open=true")
        t.check("Persönliche Woche in der Karte", "diese Woche" in p.js("document.querySelector('.hero .hwk').textContent"))
        mon = T - datetime.timedelta(T.weekday())
        wk = [x for x in daten() if x["status"] == "done" and mon <= datetime.date.fromisoformat(x["log"][0]["t"][:10]) <= T]
        h = p.js("document.querySelector('.mot h3 em').textContent")
        t.check("Gemeinsame Woche zählt alle Erledigten seit Montag (%d)" % len(wk), h == "%d erledigt" % len(wk), h)
        leg = p.js("document.querySelector('.mot .wleg').textContent")
        if any(x["id"] == "m1" for x in wk):
            t.check("Anteil nach Verlauf: „iPhone von Melanie“ zählt für Melanie", "Melanie 1" in leg, leg)
        t.check("Vergleich zur Vorwoche angezeigt", "Letzte Woche" in p.js("document.querySelector('.mot .wcmp').textContent"))
        badges = p.js("[...document.querySelectorAll('.bdg.on span')].map(x=>x.textContent)")
        t.check("Noch kein Abzeichen bei 8 eigenen Erledigten", badges == [], badges)
        nx = p.js("document.querySelector('.bnext').textContent")
        t.check("Nächstes Abzeichen in Worten (Erste 10: noch 2 Aufgaben)", "Erste 10" in nx and "noch 2 Aufgaben" in nx, nx)
        p.pg.click(".bdx summary")
        p.pg.click(".bdg[data-bdg=d10]")
        t.check("Abzeichen antippen erklärt es", "Noch offen: Erste 10" in (p.pg.text_content("#toast") or ""))
        s.api("api/import", {"tasks": [erledigt("a10", "Neun", -30, -30)]})
        p.js("pull(true)")
        p.pg.wait_for_timeout(500)
        p.js("void setStatus(byId('h1'),'done')")
        p.pg.wait_for_timeout(600)
        msg = p.pg.text_content("#toast") or ""
        t.check("Letzte Aufgabe des Tages: Konfetti und Glückwunsch", p.js("!!document.querySelector('.confetti')") and "Alles für heute erledigt" in msg, msg)
        t.check("Gleichzeitig neues Abzeichen gemeldet (10 erledigt)", "Neues Abzeichen: Erste 10" in msg, msg)
        p.pg.wait_for_timeout(300)
        st = p.js("document.querySelector('.hstreak').textContent")
        t.check("Serie jetzt 5 Tage, Flamme leuchtet", st == "5 Tage am Stück" and p.js("document.querySelector('.hstreak').classList.contains('lit')"), st)
        t.check("Abzeichen „Erste 10“ freigeschaltet", "Erste 10" in p.js("[...document.querySelectorAll('.bdg.on span')].map(x=>x.textContent)"))
        p.pg.reload()
        p.ready()
        p.js("void setStatus(byId('a1'),'todo')")
        p.pg.wait_for_timeout(300)
        p.js("void setStatus(byId('a1'),'done')")
        p.pg.wait_for_timeout(400)
        t.check("Schon gemeldete Abzeichen kommen nicht noch einmal", "Neues Abzeichen" not in (p.pg.text_content("#toast") or ""))
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_ohne_geschichte_kein_alarm(t, browser):
    with Server() as s:
        s.seed([erledigt("x%d" % i, "Alt %d" % i, -40 - i, -40 - i) for i in range(12)] + [task("h", "Heute", D(0), D(0), who="Lasse")])
        p = Page(browser, s.url, PHONE, setup=ALS_LASSE)
        p.pg.click("[data-v=home]")
        p.pg.wait_for_timeout(300)
        t.check("Ohne Serie: Einladung statt 0", "Serie startet heute" in p.js("document.querySelector('.hstreak').textContent"))
        t.check("Bestehende Abzeichen beim ersten Öffnen nicht als neu gemeldet", p.js("JSON.parse(localStorage.getItem('haus-badges-Lasse'))").count("d10") == 1)
        p.js("void setStatus(byId('h'),'doing')")
        p.pg.wait_for_timeout(400)
        t.check("„In Arbeit“ löst nichts aus", not p.js("!!document.querySelector('.confetti')"))
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_meme_auswahl_einmal_am_tag(t, browser):
    from common import FakeGemini
    import json, time
    kinds = ["done", "streak", "late", "start", "good", "frueh", "frueh_gut", "mittag", "mittag_gut", "abend", "abend_gut", "fast"]
    g = FakeGemini(lambda prompt: {k: [{"q": "gemini %s %d" % (k, i), "n": "Meme %s %d" % (k, i)} for i in range(4)] for k in kinds})
    with Server(settings={"ai_key": "AQ.TestSchluessel_1234567890abcdef", "giphy_key": "TestGiphyKey1234567890abcd"}, GEMINI_URL=g.url) as s:
        s.seed([task("h", "Heute", D(0), D(0), who="Lasse")])
        first = s.api("api/sprueche")
        time.sleep(1)
        second = s.api("api/sprueche")
        s.api("api/sprueche")
        time.sleep(0.5)
        t.check("Meme-Auswahl: eine Gemini-Anfrage im Hintergrund, danach aus dem Speicher", first["gifs"] is None and second["gifs"] and len(g.prompts) == 1, (first, len(g.prompts)))
        t.check("Anfrage verlangt bestehende Memes aus den gewünschten Bereichen", "BESTEHENDES" in g.prompts[0] and all(x in g.prompts[0] for x in ("Stromberg", "Simpsons", "GTA", "Tier", "Polit")))
        t.check("Zählt fürs Tageslimit (1 Anfrage)", s.api("api/tasks")["ha"]["aiuse"]["used"] == 1)
        calls = []
        p = Page(browser, s.url, PHONE, setup=lambda pg: (ALS_LASSE(pg), UM(9)(pg), giphy_mock(pg, calls)))
        p.pg.wait_for_timeout(800)
        t.check("GIPHY-Suche mit dem von Gemini gewählten Meme der Lage „frueh“ (morgens, noch nichts)", len(calls) == 1 and "q=gemini%20frueh" in calls[0], calls)
        t.check("Karte zeigt GIF mit Meme-Namen", (p.js("(document.querySelector('.hero .gifbox img')||{}).alt") or "").startswith("Meme frueh"))
        t.check("Anfrage nennt alle Lagen nach Tageszeit, abends ironisch erlaubt", all(k in g.prompts[0] for k in ("frueh_gut", "mittag_gut", "abend_gut", "fast")) and "IRONISCH" in g.prompts[0])
        p.js("document.querySelectorAll('.gifpop').forEach(x=>x.remove())")
        p.js("void setStatus(byId('h'),'done')")
        p.pg.wait_for_timeout(900)
        t.check("Lage wechselt (alles erledigt): neues passendes GIF, groß eingeblendet", len(calls) == 2 and "q=gemini%20done" in calls[1] and p.js("!!document.querySelector('.gifpop')"), calls)
        t.check("Server merkt sich je Lage ein GIF", sorted(s.api("api/gif").get("by", {})) == ["done", "frueh"])
        p.pg.click("[data-v=list]")
        t.check("Andere Ansichten bleiben ohne Memes", not p.js("!!document.querySelector('#main .meme,#main .gifbox')"))
        p.close()
    with Server(settings={"ai_key": "AQ.TestSchluessel_1234567890abcdef"}, GEMINI_URL=g.url) as s:
        json.dump({"day": time.strftime("%Y-%m-%d"), "n": 60, "blocked": False}, open(s.dir + "/d/ai_usage.json", "w"))
        s.api("api/sprueche")
        time.sleep(0.5)
        t.check("Ist mehr als die Hälfte des Tageslimits verbraucht, wird nicht nachgefragt", len(g.prompts) == 1)
        p = Page(browser, s.url, PHONE, setup=ALS_LASSE)
        t.check("Ohne GIPHY-Schlüssel: kurzer Spruch statt GIF", p.js("!!document.querySelector('.hero .meme')") and not p.js("!!document.querySelector('.hero .gifbox')"))
        p.close()
    g.close()


GIFS = {"data": [{"title": "Testhund", "url": "https://giphy.com/gifs/test", "images": {"fixed_height": {"webp": "https://media.giphy.com/media/test/200.webp"}}}]}


def giphy_mock(pg, calls):
    import json, os
    icon = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "planner", "icons", "icon-192.png"), "rb").read()
    def api(route):
        calls.append(route.request.url)
        route.fulfill(status=200, content_type="application/json", body=json.dumps(GIFS))
    pg.route("https://api.giphy.com/**", api)
    pg.route("https://media.giphy.com/**", lambda r: r.fulfill(status=200, content_type="image/png", body=icon))


def test_gif_des_tages(t, browser):
    with Server(settings={"giphy_key": "TestGiphyKey1234567890abcd"}) as s:
        s.seed([task("h", "Heute", D(0), D(0), who="Lasse")])
        calls = []
        p = Page(browser, s.url, PHONE, setup=lambda pg: (ALS_LASSE(pg), giphy_mock(pg, calls)))
        p.pg.wait_for_timeout(600)  # Start ist die erste Ansicht
        t.check("Erstes Öffnen: eine GIPHY-Suche, GIF in der Karte, nichts zum Wegklicken", len(calls) == 1 and not p.js("!!document.querySelector('.gifpop')") and p.js("!!document.querySelector('.hero .gifbox img')"), calls)
        t.check("Suche mit Schlüssel und Jugendschutz pg-13", "api_key=TestGiphyKey" in calls[0] and "rating=pg-13" in calls[0])
        p.pg.click(".hero .gifbox")
        p.pg.wait_for_timeout(300)
        t.check("Antippen zeigt das GIF groß", p.js("!!document.querySelector('.gifpop img')"))
        p.pg.click(".gifpop")
        p.pg.wait_for_timeout(400)
        t.check("Antippen schließt, GIF bleibt in der Karte", not p.js("!!document.querySelector('.gifpop')") and p.js("!!document.querySelector('.hero .gifbox img')"))
        p.close()
        calls2 = []
        p = Page(browser, s.url, PHONE, setup=lambda pg: (ALS_LASSE(pg), giphy_mock(pg, calls2)))
        p.pg.wait_for_timeout(600)
        t.check("Zweites Gerät: keine neue Suche, gleiches GIF", calls2 == [] and p.js("!!document.querySelector('.hero .gifbox img')"), calls2)
        p.js("prefSet('fun','0');render()")
        t.check("Abschaltbar je Person: dann weder Spruch noch GIF", not p.js("!!document.querySelector('.hero .meme,.hero .gifbox')"))
        t.check("Fremde GIF-Adressen lehnt der Server ab", s.api("api/gif", {"kind": "done", "url": "https://evil.example/x.gif"}).get("_status") == 400)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_gif_wechselt_mit_der_lage_und_erklaert_sich(t, browser):
    with Server(settings={"giphy_key": "TestGiphyKey1234567890abcd"}) as s:
        s.seed([task("o", "Überfällig", D(-2), D(-1), who="Lasse"), task("h1", "Heute 1", D(0), D(0), who="Lasse"), task("h2", "Heute 2", D(0), D(0), who="Lasse")])
        calls = []
        p = Page(browser, s.url, PHONE, setup=lambda pg: (ALS_LASSE(pg), UM(13)(pg), giphy_mock(pg, calls)))
        p.pg.wait_for_timeout(600)
        why = lambda: p.js("(document.querySelector('.hero .mwhy')||{}).textContent||''")
        t.check("Satz über dem GIF deutet den Grund an: überfällig", why() == "Eine Sache ist liegen geblieben. Die holst du dir jetzt zurück.", why())
        t.check("Keine Frage „Warum dieses GIF?“ mehr", "Warum" not in p.js("document.querySelector('.hero').textContent"))
        p.js("void setStatus(byId('o'),'done')")
        p.pg.wait_for_timeout(800)
        t.check("Überfälliges gelöst: neue Lage, neue Suche, neue Begründung", len(calls) == 2 and calls[0] != calls[1] and why() == "1 geschafft, noch 2. Du bist auf einem guten Weg.", (calls, why()))
        p.js("void setStatus(byId('h1'),'done')")
        p.pg.wait_for_timeout(600)
        t.check("Gleiche Lage: kein neues GIF", len(calls) == 2 and why() == "2 geschafft, nur noch eine. Du bist auf einem guten Weg.", why())
        p.js("void setStatus(byId('h2'),'done')")
        p.pg.wait_for_timeout(900)
        t.check("Alles erledigt: drittes GIF, groß eingeblendet", len(calls) == 3 and why() == "Alle 3 erledigt. Das hast du dir verdient." and p.js("!!document.querySelector('.gifpop')"), (calls, why()))
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_keine_negativen_memes(t, browser):
    import json, time
    with Server(settings={"giphy_key": "TestGiphyKey1234567890abcd"}) as s:
        s.seed([task("o", "Überfällig", D(-2), D(-1), who="Lasse"), task("h1", "Heute 1", D(0), D(0), who="Lasse")])
        json.dump({"day": time.strftime("%Y-%m-%d"), "by": {"late": {"kind": "late", "url": "https://media.giphy.com/media/alt/200.webp", "term": "gta wasted", "name": "GTA: Hinüber"}}},
                  open(s.dir + "/d/gif.json", "w"))
        calls = []
        p = Page(browser, s.url, PHONE, setup=lambda pg: (ALS_LASSE(pg), giphy_mock(pg, calls)))
        p.pg.wait_for_timeout(800)
        t.check("Gespeichertes „Wasted“-GIF wird ersetzt", len(calls) == 1 and "wasted" not in calls[0].lower() and s.api("api/gif")["by"]["late"]["term"] != "gta wasted", calls)
        t.check("Karte zeigt nie das negative GIF", "Hinüber" not in p.js("document.querySelector('.hero').textContent"))
        bad = p.js("Object.entries(GIF_BASE).filter(([k])=>k!=='abend').flatMap(([k,v])=>v).filter(x=>GIF_BAD.test(x[0]+' '+x[1])).length")
        t.check("Eingebaute Auswahl enthält keine Scheitern-Memes (außer der ironischen Abend-Lage)", bad == 0, bad)
        t.check("Abends, wenn noch alles offen ist, ist Ironie erlaubt („This is fine“)", p.js("!gifBad('abend','this is fine')&&gifBad('mittag','this is fine')"))
        p.close()


def test_ohne_spass_kein_konfetti(t, browser):
    with Server() as s:
        s.seed([task("h1", "Heute 1", D(0), D(0), who="Lasse")])
        p = Page(browser, s.url, PHONE, setup=lambda pg: (ALS_LASSE(pg), pg.add_init_script("try{localStorage.setItem('haus-fun','0')}catch(e){}")))
        p.pg.click("[data-v=home]")
        p.pg.wait_for_timeout(300)
        p.js("void setStatus(byId('h1'),'done')")
        p.pg.wait_for_timeout(600)
        msg = p.pg.text_content("#toast") or ""
        t.check("Sprüche, GIFs und Konfetti aus: kein Konfetti, kein GIF", not p.js("!!document.querySelector('.confetti,.gifpop')"))
        t.check("Der kurze Glückwunsch kommt trotzdem", "Alles für heute erledigt" in msg, msg)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_tageskarte_breit_gif_rechts(t, browser):
    """1.43: Auf iPad und Computer steht das GIF rechts neben Ring und Zahlen, auf dem Handy darunter."""
    from common import IPAD, DESKTOP
    with Server(settings={"giphy_key": "TestGiphyKey1234567890abcd"}) as s:
        s.seed(daten())
        for name, dev, nebeneinander in (("iPad", IPAD, True), ("iPad quer", {**IPAD, "viewport": {"width": 1180, "height": 820}}, True),
                                         ("Computer", DESKTOP, True), ("Handy", PHONE, False)):
            calls = []
            p = Page(browser, s.url, dev, setup=lambda pg: (ALS_LASSE(pg), giphy_mock(pg, calls)))
            p.pg.click("[data-v=home]")
            p.pg.wait_for_timeout(600)
            r = p.js("""(()=>{const b=s=>document.querySelector(s).getBoundingClientRect();const g=b('.hero .hring'),m=b('.hero .hmeme'),h=b('.hero');
              return {side:m.left>g.right&&m.top<g.bottom,below:m.top>=g.bottom-1,inside:m.right<=h.right+1,w:Math.round(m.width)}})()""")
            ok = (r["side"] and r["inside"]) if nebeneinander else r["below"]
            t.check(name + (": GIF rechts neben dem Ring" if nebeneinander else ": GIF unter dem Ring"), ok, r)
            t.check(name + ": keine Skriptfehler", not p.errors, p.errors)
            p.close()


def test_lage_nach_tageszeit(t, browser):
    """1.45: Satz und GIF-Lage hängen von Tageszeit und Fortschritt ab; abends ironisch, sonst anspornend."""
    with Server() as s:
        s.seed([task("h%d" % i, "Heute %d" % i, D(0), D(0), who="Lasse") for i in range(8)])
        def lage(h, erledigt):
            p = Page(browser, s.url, PHONE, setup=lambda pg: (ALS_LASSE(pg), UM(h)(pg)))
            for i in range(8):
                p.js("([id,st])=>{const t=byId(id);if(t)t.status=st}", ["h%d" % i, "done" if i < erledigt else "todo"])
            p.js("for(const t of tasks)if(t.status==='done')t.log=[{t:new Date().toISOString().slice(0,16),a:'Lasse',k:'h',x:'Status: Offen → Erledigt'}];render()")
            p.pg.wait_for_timeout(200)
            r = (p.js("gifKind"), p.js("(document.querySelector('.hero .mwhy')||{}).textContent||''"), p.errors)
            p.close()
            return r
        for h, n, kind, text in ((8, 0, "frueh", "8 Aufgaben heute. Klingt viel, du schaffst das."),
                                 (9, 2, "frueh_gut", "2 schon weg, und es ist noch nicht mal Mittag. Starker Start."),
                                 (13, 0, "mittag", "Mittag, und noch alle 8 offen. Willst du nicht mal loslegen?"),
                                 (14, 3, "mittag_gut", "3 geschafft, noch 5. Du bist auf einem guten Weg."),
                                 (19, 0, "abend", "Abend, und noch alle 8 offen. Digga, du wirst es vermasseln … oder?"),
                                 (20, 1, "abend", "Erst 1 von 8, und es ist Abend. Digga, das wird knapp."),
                                 (19, 4, "abend_gut", "4 geschafft, noch 4. Endspurt, das ziehst du durch."),
                                 (15, 6, "fast", "Nur noch 2. Du hast es fast geschafft.")):
            k, w, err = lage(h, n)
            t.check("%d Uhr, %d von 8: %s" % (h, n, kind), k == kind and w == text and not err, (k, w, err))


def test_nichts_faellig_ist_freier_tag(t, browser):
    """1.45.1: Ist heute nichts fällig, gibt es zu keiner Uhrzeit „noch alle 0 offen“."""
    with Server() as s:
        s.seed([task("m", "Morgen", D(1), D(1), who="Lasse")])
        for h in (8, 13, 20):
            p = Page(browser, s.url, PHONE, setup=lambda pg, h=h: (ALS_LASSE(pg), UM(h)(pg)))
            p.pg.wait_for_timeout(300)
            w = p.js("(document.querySelector('.hero .mwhy')||{}).textContent||''")
            t.check("%d Uhr, nichts fällig: freier Tag" % h, p.js("gifKind") == "done" and w == "Heute ist nichts fällig. Genieß den freien Tag." and "0" not in w, w)
            p.close()
