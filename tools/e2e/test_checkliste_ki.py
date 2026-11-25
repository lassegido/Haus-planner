"""Checkliste umsortieren, KI-Vorschlag mit eigenem Hinweis, KI-Schlüssel in den Einstellungen (mit nachgebautem Gemini)."""
from common import PHONE, FakeGemini, Page, Server


def antwort(prompt):
    if "Hinweise des Nutzers" in prompt:
        return {"notes": "Wände sind fertig, nur Boden und Möbel.", "checklist": ["Boden verlegen", "Schreibtisch aufbauen"]}
    return {"notes": "Erst Wände, dann Boden.", "checklist": ["Wände verputzen", "Wände streichen", "Boden verlegen"]}


def test_checkliste_ziehen_und_ki_anpassen(t, browser):
    g = FakeGemini(antwort)
    with Server(settings={"ai_key": "AQ.TestSchluessel_1234567890abcdef"}, GEMINI_URL=g.url) as s:
        p = Page(browser, s.url, PHONE)
        pg = p.pg
        pg.click("#add")
        pg.wait_for_timeout(400)
        pg.fill("#f_title", "Büro fertigstellen")
        p.js("document.getElementById('d_ck').open=true")
        for x in ["Eins", "Zwei", "Drei"]:
            pg.click("#ck_add")
            pg.keyboard.type(x)
        pg.wait_for_timeout(200)
        grips = pg.query_selector_all("#f_ck .grip")
        bb = grips[2].bounding_box()
        top = pg.query_selector_all("#f_ck .ck")[0].bounding_box()
        cx, cy = bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2
        pg.mouse.move(cx, cy)
        pg.mouse.down()
        for k in range(1, 13):
            pg.mouse.move(cx, cy - (bb["y"] - top["y"] + 10) * k / 12)
            pg.wait_for_timeout(25)
        pg.mouse.up()
        pg.wait_for_timeout(200)
        order = p.js("cklist.map(c=>c.t)")
        t.check("Checkliste: „Drei“ am Griff nach oben gezogen", order == ["Drei", "Eins", "Zwei"], order)

        pg.click("#ai_btn")
        pg.wait_for_function("aiRes&&aiRes.items&&aiRes.items.length", timeout=5000)
        first = p.js("aiRes.items")
        t.check("KI-Vorschlag kommt an", "Wände verputzen" in first, first)
        pg.fill("#ai_hint", "Wände sind schon verputzt und gestrichen")
        pg.click("#ai_re")
        pg.wait_for_function("aiRes.items.includes('Schreibtisch aufbauen')", timeout=5000)
        t.check("Eigener Hinweis und alter Vorschlag gehen an die KI", "Wände sind schon verputzt" in g.prompts[-1] and "Wände verputzen" in g.prompts[-1])
        t.check("Hinweisfeld wird danach geleert", pg.input_value("#ai_hint") == "")
        pg.click("#ai_ok")
        pg.wait_for_timeout(200)
        pg.click("#b_save")
        pg.wait_for_timeout(700)
        saved = [c["t"] for c in s.tasks()[0]["checklist"]]
        t.check("Gespeichert: eigene Reihenfolge plus übernommene Vorschläge", saved[:3] == ["Drei", "Eins", "Zwei"] and "Boden verlegen" in saved, saved)
        use = s.api("api/tasks")["ha"]["aiuse"]
        extra = sum(1 for x in g.prompts if "BESTEHENDES" in x)  # tägliche Meme-Auswahl der Startseite (höchstens 1)
        t.check("Jede KI-Anfrage wird für das Tageslimit gezählt (2 + %d Meme-Auswahl)" % extra, extra <= 1 and use.get("used") == 2 + extra and not use.get("blocked"), use)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()
    g.close()


def test_ki_schluessel_speichern(t, browser):
    g = FakeGemini(lambda prompt: {"notes": "ok", "checklist": []})
    with Server(GEMINI_URL=g.url) as s:
        p = Page(browser, s.url, PHONE)
        p.settings("ki")
        p.pg.fill("#ki_key", "AIzaKurz")
        p.pg.click("#s_body [data-act=kisave]")
        p.pg.wait_for_timeout(400)
        msg = p.pg.text_content(".kimsg") or ""
        t.check("Zu kurzer Schlüssel wird mit Hinweis abgelehnt", "nicht nach einem vollständigen" in msg, msg)
        p.pg.fill("#ki_key", "AQ.Beispiel_1234567890abcdefGHIJK")
        p.pg.click("#s_body [data-act=kisave]")
        p.pg.wait_for_timeout(1500)
        msg = p.pg.text_content(".kimsg") or ""
        t.check("Schlüssel mit Punkt wird gespeichert und getestet", "gesichert" in msg.lower() and "bereit" in msg.lower(), msg)
        html = p.js("document.documentElement.outerHTML")
        t.check("Schlüssel steht danach nicht mehr in der Seite", "Beispiel_1234567890" not in html)
        t.check("Server liefert den Schlüssel nie aus", "Beispiel_1234567890" not in str(s.api("api/tasks")))
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()
    g.close()
