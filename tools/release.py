#!/usr/bin/env python3
"""Neue Version vorbereiten. Aufruf: python3 tools/release.py 1.32.0

1. Prüft, dass die Nummer größer ist als die aktuelle und oben im CHANGELOG ein Eintrag „## 1.32.0“ steht
   (den Text schreibt man vorher selbst: was ändert sich für Lasse und Melanie?).
2. Trägt die Version in planner/config.yaml ein und erzeugt die Add-on-Version (tools/build.py).
3. Führt alle Prüfungen aus (tools/check.py). Committen, pushen und das Claude-Artifact aktualisieren
   passiert danach von Hand, siehe CLAUDE.md.
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "planner", "config.yaml")


def parse(v):
    if not re.fullmatch(r"\d+\.\d+\.\d+", v):
        sys.exit("Versionsnummer bitte als Zahl.Zahl.Zahl, z. B. 1.32.0")
    return tuple(int(x) for x in v.split("."))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    new = sys.argv[1]
    cfg = open(CFG, encoding="utf-8").read()
    old = re.search(r'^version:\s*"?([^"\n]+)"?\s*$', cfg, re.M).group(1).strip()
    if parse(new) <= parse(old):
        sys.exit("Neue Version %s muss größer sein als die aktuelle %s (sonst zeigt Home Assistant kein Update an)" % (new, old))
    log = open(os.path.join(ROOT, "planner", "CHANGELOG.md"), encoding="utf-8").read()
    top = re.search(r"^## (\S+)", log, re.M)
    if not top or top.group(1) != new:
        sys.exit("Bitte zuerst oben in planner/CHANGELOG.md einen Abschnitt „## %s“ schreiben." % new)
    open(CFG, "w", encoding="utf-8").write(re.sub(r'^version:.*$', 'version: "%s"' % new, cfg, count=1, flags=re.M))
    print("config.yaml: %s → %s" % (old, new))
    if subprocess.run([sys.executable, "tools/build.py"], cwd=ROOT).returncode:
        sys.exit(1)
    if subprocess.run([sys.executable, "tools/check.py"] + sys.argv[2:], cwd=ROOT).returncode:
        sys.exit("Prüfungen fehlgeschlagen. Version bleibt eingetragen; nach dem Beheben: python3 tools/check.py")
    print("\nBereit. Weiter: git add -A && git commit && git push, danach Claude-Artifact mit artifact/planner.html aktualisieren.")


if __name__ == "__main__":
    main()
