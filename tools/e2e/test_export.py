"""Export (PDF, Excel, Backup) und lokale Bibliotheken/Schriften im Add-on: keine Anfragen ins Internet."""
from common import DESKTOP, PHONE, Page, Server, task


def oeffne_export(p):
    p.pg.click("#more")
    p.pg.wait_for_timeout(250)
    p.pg.click("#pop .pi:has-text('Export')")
    p.pg.wait_for_timeout(300)


def test_export_pdf_excel_backup(t, browser):
    with Server() as s:
        s.seed([task("a", "Büro fertigstellen", "2026-11-24", "2026-11-30", who="Lasse", tags=["Haus"],
                     checklist=[{"t": "Boden verlegen", "d": False}]), task("b", "Zaun streichen", "2026-12-01", "2026-12-03")])
        p = Page(browser, s.url, DESKTOP)
        oeffne_export(p)
        t.check("Export-Blatt öffnet sich", p.js("document.getElementById('dlx').open"))
        for knopf, name, start in [("#x_pdf", "PDF", b"%PDF"), ("#x_xlsx", "Excel", b"PK"), ("#x_json", "Backup", b"{")]:
            if not p.js("document.getElementById('dlx').open"):
                oeffne_export(p)
            try:
                with p.pg.expect_download(timeout=15000) as dl:
                    p.pg.click(knopf)
                data = open(dl.value.path(), "rb").read()
                t.check("%s-Export erzeugt eine Datei (%s, %d KB)" % (name, dl.value.suggested_filename, len(data) // 1024), data.startswith(start) and len(data) > 500)
            except Exception as e:
                t.check("%s-Export erzeugt eine Datei" % name, False, str(e)[:200])
        t.check("Export ohne Skriptfehler", not p.errors, p.errors)
        t.check("Bibliotheken kommen aus dem Add-on, nicht aus dem Internet", not p.external, p.external)
        p.close()


def test_schriften_lokal(t, browser):
    with Server() as s:
        p = Page(browser, s.url, PHONE)
        p.js("document.fonts.ready")
        p.pg.wait_for_timeout(500)
        t.check("Schrift Figtree ist geladen (aus dem Add-on)", p.js("document.fonts.check('600 16px Figtree')") and
                p.js("[...document.fonts].some(f=>f.family.replace(/\\W/g,'')==='Figtree'&&f.status==='loaded')"))
        p.settings("font")
        p.pg.click("#s_body [data-set='font:fraunces']")
        p.pg.wait_for_timeout(600)
        t.check("Schrift Fraunces lädt bei Auswahl", p.js("document.fonts.check('700 28px Fraunces')") and
                p.js("[...document.fonts].some(f=>f.family.replace(/\\W/g,'')==='Fraunces'&&f.status==='loaded')"))
        t.check("Start ohne Anfragen ins Internet", not p.external, p.external)
        p.close()


def test_fehler_im_browser_landen_im_protokoll(t, browser):
    with Server() as s:
        p = Page(browser, s.url, PHONE)
        p.pg.click("[data-v=list]")
        p.js("setTimeout(()=>{null.kaputt},0)")
        p.js("void Promise.reject(new Error('Absichtlicher Testfehler'))")
        p.js("(()=>{const x=document.createElement('script');x.src='vendor/gibtsnicht.js';document.head.appendChild(x)})()")
        p.pg.wait_for_timeout(800)
        log = s.output()
        t.check("Skriptfehler steht im Add-on-Protokoll (mit Ansicht und Version)", "TypeError: Cannot read properties of null" in log and "Ansicht list" in log, log[-600:])
        t.check("Unbehandelter Promise-Fehler steht im Protokoll", "Unbehandelt: Absichtlicher Testfehler" in log)
        t.check("Nicht ladbare Datei steht im Protokoll", "Datei nicht geladen: gibtsnicht.js" in log)
        p.close()
