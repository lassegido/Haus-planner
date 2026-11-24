#!/usr/bin/env python3
"""Alle Prüfungen in einem Lauf. Aufruf: python3 tools/check.py [--ohne-browser]

Reihenfolge: erzeugte Dateien aktuell? → Versionsnummer und Änderungsprotokoll passen? → Server-Tests →
Home-Assistant-/Alexa-Tests → Browser-Tests. Läuft genauso im GitHub-Prüflauf (.github/workflows/check.yml).
"""
import os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def version_and_changelog():
    cfg = open(os.path.join(ROOT, "planner", "config.yaml"), encoding="utf-8").read()
    ver = re.search(r'^version:\s*"?([^"\n]+)"?\s*$', cfg, re.M).group(1).strip()
    log = open(os.path.join(ROOT, "planner", "CHANGELOG.md"), encoding="utf-8").read()
    top = re.search(r"^## (\S+)", log, re.M)
    if not top or top.group(1) != ver:
        print("Version %s in config.yaml, oberster Eintrag im CHANGELOG: %s" % (ver, top.group(1) if top else "keiner"))
        return False
    print("Version %s, CHANGELOG-Eintrag vorhanden" % ver)
    return True


def run(args):
    return subprocess.run([PY] + args, cwd=ROOT).returncode == 0


def main():
    steps = [("Erzeugte Dateien aktuell und Vertrag eingehalten", lambda: run(["tools/build.py", "--check"])),
             ("Versionsnummer und Änderungsprotokoll", version_and_changelog),
             ("Python-Syntax Server", lambda: run(["-m", "py_compile", "planner/server.py"])),
             ("Server-Tests", lambda: run(["tools/test_server.py"])),
             ("Home Assistant, Erinnerungen, Alexa", lambda: run(["tools/test_ha.py"]))]
    if "--ohne-browser" not in sys.argv:
        steps.append(("Browser-Tests (Handy, iPad, Desktop)", lambda: run(["tools/test_browser.py"])))
    results = []
    for name, fn in steps:
        print("\n=== " + name)
        t0 = time.time()
        ok = fn()
        results.append((name, ok, time.time() - t0))
    print("\n=== Ergebnis")
    for name, ok, dt in results:
        print("%s  %-45s %5.0f s" % ("OK  " if ok else "FEHL", name, dt))
    sys.exit(0 if all(ok for _, ok, _ in results) else 1)


if __name__ == "__main__":
    main()
