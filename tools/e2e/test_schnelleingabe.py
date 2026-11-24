"""Willkommen, Schnelleingabe und gleiche Erkennung im Browser (JS) und im Server (Python, für Siri/Assist/Alexa)."""
import datetime
from common import PHONE, Page, Server, task

# Jede Zeile wird im Browser und im Server zerlegt; beide müssen dasselbe ergeben.
SAETZE = [
    "Zaun streichen Sa #Garten !1 @Melanie", "Rasen mähen morgen #gart", "Dachrinne reinigen 12.12. +schöner @lasse",
    "Steuer abgeben bis Fr !2", "Filter wechseln in 3 Tagen #Haus", "Mach das so wie besprochen", "Reifen tauschen nächste Woche p3",
    "Geschenk kaufen 31.02.", "Party planen Wochenende #Feier", "Heute nichts",
    "rasen mähen am samstag tag garten priorität eins", "dachrinne reinigen am zwölften dezember projekt schöner",
    "fenster putzen in drei tagen", "heizung entlüften bis zum 5. dezember", "tag der offenen tür vorbereiten",
    "geburtstag planen am dritten januar prio zwei", "garage aufräumen kommende woche", "keller entrümpeln übermorgen",
]


def test_willkommen_und_schnelleingabe(t, browser):
    with Server() as s:
        p = Page(browser, s.url, PHONE, onboarded=False)
        try:
            p.pg.wait_for_function("document.getElementById('dsh').open", timeout=4000)
            welcome = True
        except Exception:
            welcome = False
        t.check("Beim ersten Öffnen erscheint das Willkommensblatt", welcome)
        p.pg.click("#dsh button:has-text('Lasse')")
        p.pg.wait_for_timeout(500)
        t.check("„Ich bin Lasse“ wird gemerkt", p.js("prefGet('me')") == "Lasse")
        p.pg.click("#qadd")
        p.pg.type("#qadd", "Rasen mähen Sa #Garten !2 @Melanie", delay=2)
        p.pg.wait_for_timeout(250)
        prev = p.js("[...document.querySelectorAll('#qprev > *')].map(x=>x.textContent).join(' ')")
        t.check("Vorschau zeigt erkannte Angaben", "Garten" in prev and "Melanie" in prev, prev)
        p.pg.keyboard.press("Enter")
        p.pg.wait_for_timeout(600)
        for line in ["Rechnung bezahlen heute", "Steuer abgeben bis Fr !1"]:
            p.pg.type("#qadd", line, delay=2)
            p.pg.keyboard.press("Enter")
            p.pg.wait_for_timeout(600)
        t.check("Fokus bleibt im Eingabefeld für die nächste Aufgabe", p.js("document.activeElement.id") == "qadd")
        got = {x["title"]: x for x in s.tasks()}
        r = got.get("Rasen mähen", {})
        t.check("Drei Aufgaben angelegt", set(got) == {"Rasen mähen", "Rechnung bezahlen", "Steuer abgeben"}, list(got))
        t.check("Tag, Person, Priorität und Samstag erkannt",
                r.get("tags") == ["Garten"] and r.get("who") == "Melanie" and r.get("prio") == 2
                and datetime.date.fromisoformat(r.get("start", "2000-01-01")).weekday() == 5, r)
        t.check("Ohne @Person bekommt die Aufgabe „Ich bin“", got.get("Rechnung bezahlen", {}).get("who") == "Lasse")
        t.check("Neuer Tag wird registriert", "Garten" in [x["n"] for x in s.api("api/tasks")["tags"]])
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_gleiche_erkennung_browser_und_server(t, browser):
    with Server() as s:
        s.seed([task("a1", "Alt", "2026-11-20", "2026-11-22", tags=["Haus", "Garten"], proj="Schöner Wohnen", who="Lasse, Melanie")],
               tags=[{"n": "Haus", "c": "sky"}, {"n": "Garten", "c": "mint"}, {"n": "Schöner Wohnen", "c": "sea", "p": 1}])
        p = Page(browser, s.url, PHONE)
        diff = []
        for satz in SAETZE:
            js = p.js("""s=>{const q=parseQuick(s),d=qDates(q)||[tdy(),tdy()];
              return {title:q.title.charAt(0).toUpperCase()+q.title.slice(1),tags:q.tags,proj:q.proj,who:q.who.join(", "),prio:q.prio,start:d[0],end:d[1]}}""", satz)
            r = s.api("api/quick", {"text": satz}).get("task", {})
            py = {k: r.get(k) for k in ("title", "tags", "proj", "who", "prio", "start", "end")}
            if py != js:
                diff.append((satz, js, py))
        t.check("%d Sätze: Browser und Server erkennen dasselbe" % len(SAETZE), not diff, diff)
        p.close()
