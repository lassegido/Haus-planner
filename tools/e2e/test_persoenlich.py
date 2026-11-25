"""Persönliche Einstellungen je Home-Assistant-Benutzer und Text-Markieren beim Gedrückthalten."""
from common import PHONE, Page, Server, task

USERS = {"Lasse": {"X-Remote-User-Id": "lasse0001", "X-Remote-User-Display-Name": "Lasse"},
         "Melanie": {"X-Remote-User-Id": "melanie01", "X-Remote-User-Display-Name": "Melanie"}}
ACC = "getComputedStyle(document.documentElement).getPropertyValue('--acc').trim()"


def test_design_je_benutzer(t, browser):
    # TRUST_USER_HEADERS: Im Test kommen die Benutzer-Kopfzeilen nicht von der Ingress-Adresse, darum ausdrücklich vertrauen.
    with Server(TRUST_USER_HEADERS=1) as s:
        p = Page(browser, s.url, PHONE, onboarded=False, headers=USERS["Lasse"])
        p.pg.wait_for_function("USER!==null", timeout=5000)
        t.check("Lasse wird erkannt, „Ich bin“ automatisch gesetzt", p.js("[USER,prefGet('me')]") == ["Lasse", "Lasse"])
        t.check("Kein Willkommensblatt, wenn der Benutzer bekannt ist", not p.js("document.getElementById('dsh').open"))
        default = p.js(ACC)
        p.settings("des")
        p.pg.click("#s_body [data-set='des:wald']")
        p.pg.wait_for_timeout(500)
        lasse = p.js(ACC)
        t.check("Lasse wählt Wald", lasse != default, (default, lasse))
        p.close()

        p = Page(browser, s.url, PHONE, onboarded=False, headers=USERS["Melanie"])
        p.pg.wait_for_function("USER!==null", timeout=5000)
        p.pg.wait_for_timeout(300)
        t.check("Melanie behält ihr eigenes Design", p.js(ACC) == default and p.js("prefGet('me')") == "Melanie")
        p.close()

        p = Page(browser, s.url, PHONE, onboarded=False, headers=USERS["Lasse"])
        p.pg.wait_for_function("USER!==null", timeout=5000)
        p.pg.wait_for_timeout(300)
        t.check("Lasse bekommt Wald auch auf einem neuen Gerät", p.js(ACC) == lasse)
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()


def test_einstellungen_getrennt_sichtbar(t, browser):
    with Server() as s:
        p = Page(browser, s.url, PHONE)
        p.settings()
        heads = p.js("[...document.querySelectorAll('#s_body h3,#s_body .sgh,#s_body .grph')].map(h=>h.textContent.trim())")
        txt = p.js("document.getElementById('s_body').textContent")
        t.check("Einstellungen zeigen „Nur für dich“ und „Für alle im Haushalt“", "Nur für dich" in txt and "Für alle im Haushalt" in txt, heads)
        p.close()


def test_gedrueckt_halten_markiert_keinen_text(t, browser):
    with Server() as s:
        s.seed([task("a1", "Dankeskarten verschicken", "2026-11-23", "2026-11-25")])
        p = Page(browser, s.url, PHONE)
        p.pg.click("[data-v=board]")
        p.pg.wait_for_timeout(400)
        us = "e=>getComputedStyle(e).webkitUserSelect||getComputedStyle(e).userSelect"
        t.check("Karte: Text nicht markierbar", p.pg.eval_on_selector("#main [data-id]", us) == "none")
        p.js("void taskMenu('a1')")
        p.pg.wait_for_timeout(300)
        t.check("Menütitel: nicht markierbar", p.pg.eval_on_selector("#dsh .sht", us) == "none")
        prevented = p.js("(()=>{const t=document.querySelector('#dsh .sht');const ev=new Event('selectstart',{bubbles:true,cancelable:true});t.firstChild.dispatchEvent(ev);return ev.defaultPrevented})()")
        t.check("Markieren im Menü wird unterbunden", prevented)
        p.pg.click("#dsh .cancel")
        p.pg.wait_for_timeout(300)
        p.js("openDlg('a1')")
        p.pg.wait_for_timeout(400)
        t.check("Eingabefelder bleiben markierbar (Kopieren/Einsetzen)", p.pg.eval_on_selector("#f_title", us) != "none")
        t.check("keine Skriptfehler", not p.errors, p.errors)
        p.close()
