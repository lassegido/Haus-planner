#!/usr/bin/env python3
"""Browser-Tests der Oberfläche (Playwright, Chromium). Aufruf: python3 tools/test_browser.py [Teil des Testnamens]

Die Tests liegen in tools/e2e/test_*.py. Jede Funktion test_…(t, browser) prüft einen Bereich mit t.check(…).
Voraussetzung: pip install playwright && python3 -m playwright install chromium
Bildschirmfotos zum Nachsehen: SHOT_DIR=/tmp/shots python3 tools/test_browser.py
"""
import importlib.util, os, sys, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "e2e"))


class Checks:
    def __init__(self):
        self.failed = []
        self.count = 0
        self.prefix = ""

    def check(self, name, cond, detail=""):
        self.count += 1
        print(("OK   " if cond else "FEHL ") + self.prefix + name + ("" if cond or not detail else "  → %s" % (detail,)))
        if not cond:
            self.failed.append(self.prefix + name)
        return cond


def main():
    from playwright.sync_api import sync_playwright
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    files = sorted(f for f in os.listdir(os.path.join(HERE, "e2e")) if f.startswith("test_") and f.endswith(".py"))
    t = Checks()
    t0 = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for f in files:
            spec = importlib.util.spec_from_file_location(f[:-3], os.path.join(HERE, "e2e", f))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for name in [n for n in dir(mod) if n.startswith("test_") and callable(getattr(mod, n))]:
                if only and only not in f and only not in name:
                    continue
                t.prefix = ""
                print("\n# %s · %s" % (f[5:-3], name[5:].replace("_", " ")))
                try:
                    getattr(mod, name)(t, browser)
                except Exception:
                    t.count += 1
                    t.failed.append("%s: Abbruch" % name)
                    print("FEHL Abbruch mit Ausnahme:\n" + traceback.format_exc(limit=4))
        browser.close()
    print("\n%d Prüfungen in %.0f s, %d fehlgeschlagen" % (t.count, time.time() - t0, len(t.failed)))
    for n in t.failed:
        print("  – " + n)
    sys.exit(1 if t.failed or not t.count else 0)


if __name__ == "__main__":
    main()
