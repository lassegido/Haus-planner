#!/usr/bin/env python3
"""Setzt die Oberfläche aus src/ zusammen: Claude-Version (artifact/planner.html) und Add-on (planner/index.html).

Aufruf im Repository-Hauptordner:
  python3 tools/build.py           erzeugt artifact/planner.html, planner/index.html und planner/VERSION
  python3 tools/build.py --check   prüft nur, ob die erzeugten Dateien aktuell sind (für den Prüflauf)
Die Versionsnummer kommt aus planner/config.yaml (Zeile "version").

Quellen (nur hier ändern):
  src/seite.html   HTML-Gerüst mit den Platzhaltern für CSS und JavaScript
  src/style.css    alle Stile
  src/js/*.js      JavaScript, in Dateinamen-Reihenfolge aneinandergehängt (ein gemeinsames Skript, keine Module).
                   NAME.claude.js gilt nur für die Claude-Version, NAME.addon.js nur für das Add-on.

Prüfungen bei jedem Lauf:
1. Vertrag: Zu jeder .claude.js gibt es eine .addon.js. Was die Claude-Variante auf oberster Ebene definiert, muss
   auch die Add-on-Variante definieren (außer ARTIFACT_ONLY). Jede Funktion, die eine Add-on-Variante aufruft, muss
   es in der fertigen Seite geben.
2. Syntaxprüfung beider Seiten mit node --check (wenn Node installiert ist).
3. Fremdcode: Liegen Bibliotheken und Schriften geprüft in planner/vendor/ (Prüfsummen aus MANIFEST.txt),
   lädt das Add-on sie lokal statt aus dem Internet (Zeile „const LIB=“ wird ersetzt).
"""
import glob, hashlib, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
ADDON = os.path.join(ROOT, "planner")
ARTIFACT = os.path.join(ROOT, "artifact", "planner.html")
VENDOR = os.path.join(ADDON, "vendor")
CSS_PH, JS_PH = "/* @@CSS: src/style.css @@ */\n", "/* @@JS: src/js/*.js @@ */\n"
LIB_LINE = re.compile(r"^const LIB=\{.*\};$", re.M)
LIB_LOCAL = 'const LIB={pdf:"vendor/jspdf.umd.min.js?v=%(v)s",xlsx:"vendor/exceljs.min.js?v=%(v)s",font:()=>"vendor/fonts.css?v=%(v)s"};'
VENDOR_NEEDED = ("jspdf.umd.min.js", "exceljs.min.js", "fonts.css")
# Namen, die nur die Claude-Version braucht (lokaler Browser-Speicher, Claude-Datenbank)
ARTIFACT_ONLY = {"lsGet", "lsSet", "lsGetReg", "lsSetReg", "metaCol"}
# Eingebaute Browser-Funktionen und Schlüsselwörter, die in Add-on-Varianten aufgerufen werden dürfen
BUILTIN = set("""if for while switch catch return function typeof await async new fetch setInterval setTimeout clearTimeout
JSON Object Array String Number Boolean Error Blob File URL Promise Math Date matchMedia encodeURIComponent""".split())
PWA = ('<link rel="manifest" href="manifest.webmanifest"><link rel="apple-touch-icon" href="icons/apple-touch-icon.png">'
       '<link rel="icon" type="image/png" href="icons/icon-192.png"><meta name="mobile-web-app-capable" content="yes">'
       '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Planner">'
       '<meta name="apple-mobile-web-app-status-bar-style" content="default">')

# Skriptfehler und nicht ladbare Dateien an den Server melden (landen im Add-on-Protokoll). Höchstens 8 je Seitenaufruf.
ERRLOG = ('<script>(function(){var n=0,seen={};function send(m,w){try{m=String(m||"").slice(0,400);w=String(w||"");if(n>=8||seen[m+w])return;seen[m+w]=1;n++;'
          'var v=(document.body&&document.body.dataset.view)||"";fetch("api/log",{method:"POST",keepalive:true,headers:{"Content-Type":"application/json","X-Planner":"1"},'
          'body:JSON.stringify({msg:m,where:w,ver:"%s",view:v,ua:navigator.userAgent.slice(0,120)})}).catch(function(){})}catch(_){}}'
          'addEventListener("error",function(e){var t=e.target;if(t&&t!==window){if(t.tagName==="SCRIPT"||t.tagName==="LINK")send("Datei nicht geladen: "+String(t.src||t.href).split("/").pop().split("?")[0],"");return}'
          'send(e.message,String(e.filename||"").split("/").pop()+":"+e.lineno+":"+e.colno)},true);'
          'addEventListener("unhandledrejection",function(e){var r=e.reason||{};send("Unbehandelt: "+(r.message||r),String(r.stack||"").split("\\n")[1]||"")})})();</script>')


def fail(msg):
    sys.exit("FEHLER: " + msg)


def top_level_names(code):
    """Namen, die auf oberster Ebene (Zeilenanfang ohne Einrückung) definiert werden."""
    return set(m.group(1) or m.group(2) for m in
               re.finditer(r"^(?:async\s+)?function\s+([A-Za-z_$][\w$]*)|^(?:let|const|var)\s+([A-Za-z_$][\w$]*)", code, re.M))


def defined_anywhere(name, html):
    n = re.escape(name)
    return re.search(r"function\s+%s\s*\(|(?:let|const|var)\s+(?:[\w$]+\s*=[^;\n]*?,\s*)*%s\s*=" % (n, n), html) is not None


def check_contract(html):
    parts = sorted(glob.glob(os.path.join(SRC, "js", "*.js")))
    names = {os.path.basename(p) for p in parts}
    for p in parts:
        base = os.path.basename(p)
        if not base.endswith(".claude.js"):
            continue
        twin = base.replace(".claude.js", ".addon.js")
        if twin not in names:
            fail("src/js/%s hat kein Gegenstück %s für das Add-on" % (base, twin))
        claude, addon = read(p), read(os.path.join(SRC, "js", twin))
        missing = sorted(top_level_names(claude) - top_level_names(addon) - ARTIFACT_ONLY)
        if missing:
            fail("src/js/%s definiert %s, src/js/%s aber nicht.\n"
                 "  → im Add-on ergänzen oder, wenn nur für Claude nötig, in ARTIFACT_ONLY (tools/build.py) eintragen." % (base, ", ".join(missing), twin))
    for p in parts:
        if p.endswith(".addon.js"):
            calls = set(re.findall(r"(?<![\w$.])([A-Za-z_$][\w$]*)\s*\(", read(p))) - BUILTIN
            unknown = sorted(c for c in calls if c != "$" and not defined_anywhere(c, html))
            if unknown:
                fail("src/js/%s ruft Funktionen auf, die es in der Seite nicht gibt: %s" % (os.path.basename(p), ", ".join(unknown)))
    orphans = sorted(n for n in names if n.endswith(".addon.js") and n.replace(".addon.js", ".claude.js") not in names)
    if orphans:
        fail("Add-on-Varianten ohne Claude-Gegenstück: %s" % ", ".join(orphans))


def check_syntax(html, label):
    node = shutil.which("node")
    if not node:
        print("Hinweis: node fehlt, Syntaxprüfung von %s übersprungen" % label)
        return
    with tempfile.TemporaryDirectory() as d:
        for i, m in enumerate(re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)):
            f = os.path.join(d, "s%d.js" % i)
            open(f, "w", encoding="utf-8").write(m.group(1))
            r = subprocess.run([node, "--check", f], capture_output=True, text=True)
            if r.returncode:
                off = html.count("\n", 0, m.start(1))
                where = re.search(r":(\d+)", r.stderr)
                line = " ab Zeile %d" % (int(where.group(1)) + off) if where else ""
                err = [l for l in r.stderr.splitlines() if "Error" in l][:1]
                fail("JavaScript-Syntaxfehler in %s%s: %s" % (label, line, err[0] if err else r.stderr.strip()[-400:]))


def vendor_ok():
    """True, wenn planner/vendor/ vollständig ist und jede Datei zur Prüfsumme in MANIFEST.txt passt."""
    man = os.path.join(VENDOR, "MANIFEST.txt")
    if not os.path.exists(man):
        return False
    listed = set()
    for line in open(man, encoding="utf-8"):
        if not line.strip():
            continue
        digest, _size, name = line.split()[:3]
        listed.add(name)
        try:
            data = open(os.path.join(VENDOR, name), "rb").read()
        except OSError:
            fail("planner/vendor/%s fehlt (steht in MANIFEST.txt)" % name)
        if hashlib.sha256(data).hexdigest() != digest:
            fail("planner/vendor/%s passt nicht zur Prüfsumme in MANIFEST.txt (verändert?). Neu holen: GitHub → Actions → Fremdcode holen" % name)
    missing = [n for n in VENDOR_NEEDED if n not in listed]
    if missing:
        fail("planner/vendor/MANIFEST.txt nennt %s nicht" % ", ".join(missing))
    return True


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def assemble(variant):
    """Seite für "claude" oder "addon" aus src/ zusammensetzen."""
    tpl = read(os.path.join(SRC, "seite.html"))
    if tpl.count(CSS_PH) != 1 or tpl.count(JS_PH) != 1:
        fail("Platzhalter für CSS oder JavaScript in src/seite.html fehlen oder sind doppelt")
    other = "claude" if variant == "addon" else "addon"
    parts = [p for p in sorted(glob.glob(os.path.join(SRC, "js", "*.js"))) if not p.endswith(".%s.js" % other)]
    js = "".join(read(p) for p in parts)
    if not all(read(p).endswith("\n") for p in parts):
        fail("Jede Datei in src/js/ muss mit einem Zeilenumbruch enden")
    return tpl.replace(CSS_PH, read(os.path.join(SRC, "style.css"))).replace(JS_PH, js), parts


def build():
    cfg = read(os.path.join(ADDON, "config.yaml"))
    ver = re.search(r'^version:\s*"?([^"\n]+)"?\s*$', cfg, re.M).group(1).strip()
    claude, _ = assemble("claude")
    s, _ = assemble("addon")
    if "claude.use" in s or "window.claude" in s or "lsGet(" in s:
        fail("Claude-spezifischer Code ist in der Add-on-Version (gehört in eine .claude.js-Datei mit .addon.js-Gegenstück)")
    if s.count("</head>") != 1:
        fail("</head> nicht eindeutig")
    s = s.replace("</head>", PWA + ERRLOG % ver + "</head>")
    if vendor_ok():
        s, n = LIB_LINE.subn(lambda m: LIB_LOCAL % {"v": ver}, s)
        if n != 1:
            fail("Zeile „const LIB={…};“ in src/js/ nicht genau einmal gefunden")
        ext = sorted(set(re.findall(r"https://(?:cdnjs\.cloudflare\.com|fonts\.googleapis\.com|fonts\.gstatic\.com)[^\"' )]*", s)))
        if ext:
            fail("Add-on-Version lädt noch aus dem Internet: %s" % ", ".join(ext))
    else:
        print("Hinweis: planner/vendor/ fehlt, Add-on lädt Bibliotheken und Schriften aus dem Internet")
    check_contract(s)
    check_syntax(claude, "artifact/planner.html")
    check_syntax(s, "planner/index.html")
    return {ARTIFACT: claude, os.path.join(ADDON, "index.html"): s, os.path.join(ADDON, "VERSION"): ver + "\n"}, ver


def main():
    out, ver = build()
    rel = lambda p: os.path.relpath(p, ROOT)
    if "--check" in sys.argv:
        old = [p for p, c in out.items() if not os.path.exists(p) or read(p) != c]
        if old:
            fail("Veraltet: %s. Bitte python3 tools/build.py ausführen und mit einchecken." % ", ".join(rel(p) for p in old))
        print("OK: %s passen zu src/ und config.yaml (Version %s)" % (", ".join(rel(p) for p in out), ver))
        return
    os.makedirs(os.path.dirname(ARTIFACT), exist_ok=True)
    for p, c in out.items():
        with open(p, "w", encoding="utf-8") as f:
            f.write(c)
    print("OK: %s erzeugt, Version %s" % (", ".join(rel(p) for p in out), ver))


if __name__ == "__main__":
    main()
