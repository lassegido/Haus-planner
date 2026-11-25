"""Motivation auf der Startseite: Serie, gemeinsame Woche, Abzeichen und Feiern."""
import datetime
from common import PHONE, Page, Server, task

T = datetime.date.today()
D = lambda n: str(T + datetime.timedelta(n))
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
        t.check("Serie: 4 Tage (leerer Tag unterbricht nicht, verspäteter Tag beendet)", st == "4 Tage Serie", st)
        order = p.js("[...document.querySelector('.home').children].map(e=>e.className.split(' ')[0]).slice(0,4)")
        t.check("Spiel-Karte steht ganz oben, gemeinsamer Teil ganz unten", order[:2] in (["hpick", "hero"], ["hero", "tiles"]) and p.js("document.querySelector('.home').lastElementChild.classList.contains('mot')"), order)
        t.check("Persönliche Woche in der Karte", "diese Woche" in p.js("document.querySelector('.hero .hwk').textContent"))
        mon = T - datetime.timedelta(T.weekday())
        wk = [x for x in daten() if x["status"] == "done" and mon <= datetime.date.fromisoformat(x["log"][0]["t"][:10]) <= T]
        h = p.js("document.querySelector('.mot h3 em').textContent")
        t.check("Gemeinsame Woche zählt alle Erledigten seit Montag (%d)" % len(wk), h == "%d erledigt" % len(wk), h)
        leg = p.js("document.querySelector('.mot .wleg').textContent")
        if any(x["id"] == "m1" for x in wk):
            t.check("Anteil nach Verlauf: „iPhone von Melanie“ zählt für Melanie", "Melanie 1" in leg, leg)
        t.check("Vergleich zur Vorwoche angezeigt", "Vorwoche" in p.js("document.querySelector('.mot .wcmp').textContent"))
        badges = p.js("[...document.querySelectorAll('.bdg.on span')].map(x=>x.textContent)")
        t.check("Noch kein Abzeichen bei 8 eigenen Erledigten", badges == [], badges)
        nx = p.js("document.querySelector('.bnext').textContent")
        t.check("Nächstes Abzeichen mit Fortschritt (Erste 10: 8/10)", "Erste 10" in nx and "8/10" in nx, nx)
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
        t.check("Serie jetzt 5 Tage, Flamme leuchtet", st == "5 Tage Serie" and p.js("document.querySelector('.hstreak').classList.contains('lit')"), st)
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


def test_sprueche_einmal_am_tag(t, browser):
    from common import FakeGemini
    import json, time
    kinds = ["done", "streak", "late", "start", "good"]
    g = FakeGemini(lambda prompt: {k: ["Gemini-%s-%d" % (k, i) for i in range(8)] for k in kinds})
    with Server(settings={"ai_key": "AQ.TestSchluessel_1234567890abcdef"}, GEMINI_URL=g.url) as s:
        s.seed([task("h", "Heute", D(0), D(0), who="Lasse")])
        first = s.api("api/sprueche")
        time.sleep(1)
        second = s.api("api/sprueche")
        s.api("api/sprueche")
        time.sleep(0.5)
        t.check("Sprüche: eine Gemini-Anfrage im Hintergrund, danach aus dem Speicher", first["lines"] is None and second["lines"] and len(g.prompts) == 1, (first, len(g.prompts)))
        t.check("Anfrage nennt die gewünschten Themen", all(x in g.prompts[0] for x in ("Stromberg", "Simpsons", "GTA", "Tier", "Satire")))
        t.check("Zählt fürs Tageslimit (1 Anfrage)", s.api("api/tasks")["ha"]["aiuse"]["used"] == 1)
        p = Page(browser, s.url, PHONE, setup=ALS_LASSE)
        p.pg.click("[data-v=home]")
        p.pg.wait_for_timeout(500)
        m = p.js("(document.querySelector('.hero .meme')||{}).textContent||''")
        t.check("Startseite zeigt einen Gemini-Spruch passend zur Lage (heute noch nichts erledigt)", m.startswith("Gemini-start-"), m)
        p.pg.click("[data-v=list]")
        t.check("Andere Ansichten bleiben ohne Sprüche", not p.js("!!document.querySelector('.meme')"))
        p.close()
    with Server(settings={"ai_key": "AQ.TestSchluessel_1234567890abcdef"}, GEMINI_URL=g.url) as s:
        json.dump({"day": time.strftime("%Y-%m-%d"), "n": 60, "blocked": False}, open(s.dir + "/d/ai_usage.json", "w"))
        s.api("api/sprueche")
        time.sleep(0.5)
        t.check("Ist mehr als die Hälfte des Tageslimits verbraucht, wird nicht nachgefragt", len(g.prompts) == 1)
        p = Page(browser, s.url, PHONE, setup=ALS_LASSE)
        p.pg.click("[data-v=home]")
        t.check("Dann eingebaute Sprüche", p.js("!!document.querySelector('.hero .meme')") and "Gemini" not in p.js("document.querySelector('.hero .meme').textContent"))
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
        p.pg.wait_for_timeout(500)  # Start ist die erste Ansicht
        t.check("Erstes Öffnen am Tag: eine GIPHY-Suche, GIF groß eingeblendet", len(calls) == 1 and p.js("!!document.querySelector('.gifpop img')"), calls)
        t.check("Suche mit Schlüssel und Jugendschutz pg-13", "api_key=TestGiphyKey" in calls[0] and "rating=pg-13" in calls[0])
        p.pg.click(".gifpop")
        p.pg.wait_for_timeout(400)
        t.check("Antippen schließt, GIF bleibt klein in der Karte", not p.js("!!document.querySelector('.gifpop')") and p.js("!!document.querySelector('.hero .gifth img')"))
        t.check("Server merkt sich das GIF des Tages", s.api("api/gif").get("url", "").startswith("https://media.giphy.com/"))
        p.close()
        calls2 = []
        p = Page(browser, s.url, PHONE, setup=lambda pg: (ALS_LASSE(pg), giphy_mock(pg, calls2)))
        p.pg.click("[data-v=home]")
        p.pg.wait_for_timeout(800)
        t.check("Zweites Gerät: keine neue Suche, gleiches GIF", calls2 == [] and p.js("!!document.querySelector('.hero .gifth img')"), calls2)
        p.js("prefSet('fun','0');render()")
        t.check("Abschaltbar je Person: dann weder Spruch noch GIF", not p.js("!!document.querySelector('.hero .meme,.hero .gifth')"))
        t.check("Fremde GIF-Adressen lehnt der Server ab", s.api("api/gif", {"url": "https://evil.example/x.gif"}).get("_status") == 400)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()
