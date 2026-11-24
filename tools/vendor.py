#!/usr/bin/env python3
"""Lädt Fremdbibliotheken und Schriften einmalig herunter und legt sie ins Add-on (planner/vendor/).

Warum: Das Add-on soll ohne CDN und ohne Google Fonts funktionieren (schneller Start, keine Anfragen an Dritte,
läuft auch, wenn ein CDN ausfällt). Die Claude-Version lädt weiter aus dem Internet.

Aufruf (braucht Internet, läuft normalerweise im GitHub-Prüflauf „Fremdcode holen“):  python3 tools/vendor.py
Ergebnis: planner/vendor/*.js, fonts.css, *.woff2, Lizenztexte und MANIFEST.txt (SHA-256 jeder Datei).
tools/build.py prüft die Prüfsummen bei jedem Lauf. Neue Version einer Bibliothek: Adresse unten ändern, Skript laufen lassen.
"""
import hashlib, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "planner", "vendor")
# Dieselben Dateien, die die App bisher zur Laufzeit lädt
LIBS = {
    "jspdf.umd.min.js": "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js",
    "exceljs.min.js": "https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.4.0/exceljs.min.js",
}
FONTS = "https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap"
SUBSETS = ("latin", "latin-ext")  # Deutsch braucht nur latin; latin-ext für Namen mit Sonderzeichen
LICENSES = {
    "LICENSE-jspdf.txt": "https://raw.githubusercontent.com/parallax/jsPDF/v2.5.1/LICENSE",
    "LICENSE-exceljs.txt": "https://raw.githubusercontent.com/exceljs/exceljs/v4.4.0/LICENSE",
    "OFL-figtree.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/figtree/OFL.txt",
    "OFL-fraunces.txt": "https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/OFL.txt",
}
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
        if r.status != 200:
            sys.exit("FEHLER: %s → %s" % (url, r.status))
        return r.read()


def main():
    os.makedirs(OUT, exist_ok=True)
    files = {}
    for name, url in {**LIBS, **LICENSES}.items():
        files[name] = (get(url), url)
    css = get(FONTS).decode()
    out_css, names = [], {}
    for subset, body in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", css, re.S):
        if subset not in SUBSETS:
            continue
        fam = re.search(r"font-family:\s*'([^']+)'", body).group(1).lower()
        url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
        if url not in names:
            names[url] = "%s-%s-%d.woff2" % (fam, subset, sum(1 for n in names.values() if n.startswith(fam + "-" + subset)) + 1)
            files[names[url]] = (get(url), url)
        out_css.append("/* %s */\n@font-face {%s}" % (subset, body.replace(url, names[url])))
    if not out_css:
        sys.exit("FEHLER: keine Schriften in der Google-Fonts-Antwort gefunden")
    head = "/* Schriften Figtree und Fraunces (SIL Open Font License, siehe OFL-*.txt), lokal für das Add-on. Erzeugt von tools/vendor.py */\n"
    files["fonts.css"] = ((head + "\n".join(out_css) + "\n").encode(), FONTS)
    for old in os.listdir(OUT):
        os.remove(os.path.join(OUT, old))
    manifest = []
    for name in sorted(files):
        data, src = files[name]
        open(os.path.join(OUT, name), "wb").write(data)
        manifest.append("%s  %8d  %s  %s" % (hashlib.sha256(data).hexdigest(), len(data), name, src))
    open(os.path.join(OUT, "MANIFEST.txt"), "w").write("\n".join(manifest) + "\n")
    print("\n".join(manifest))


if __name__ == "__main__":
    main()
