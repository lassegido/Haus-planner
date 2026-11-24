#!/usr/bin/env python3
"""Erzeugt die Add-on-Version (planner/index.html + VERSION) aus der Master-Datei src/planner.html.

Aufruf im Repository-Hauptordner:
  python3 tools/build.py           erzeugt planner/index.html und planner/VERSION
  python3 tools/build.py --check   prüft nur, ob die erzeugten Dateien aktuell sind (für den Prüflauf)
Die Versionsnummer kommt aus planner/config.yaml (Zeile "version").

Was passiert:
1. Der Speicher-Block zwischen den Markierungen „Speicher: gemeinsame Datenbank“ und „Anzeige“ wird durch
   die Server-Version unten (STORAGE) ersetzt. dl() wird durch eine Version mit Teilen-Menü ersetzt.
2. Vertragsprüfung: Alles, was der Claude-Block oben auf oberster Ebene definiert, muss auch die Server-Version
   definieren (außer ARTIFACT_ONLY). Jede Funktion, die die Server-Version aufruft, muss es in der Datei geben.
   So fällt sofort auf, wenn im Master ein neuer Name in den Speicher-Block gerät, den der Build verlieren würde.
3. Syntaxprüfung beider Dateien mit node --check (wenn Node installiert ist).
4. Fremdcode: Liegen Bibliotheken und Schriften geprüft in planner/vendor/ (Prüfsummen aus MANIFEST.txt),
   lädt die Add-on-Version sie lokal statt aus dem Internet (Zeile „const LIB=“ wird ersetzt).
"""
import hashlib, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "planner.html")
ADDON = os.path.join(ROOT, "planner")
VENDOR = os.path.join(ADDON, "vendor")
LIB_LINE = re.compile(r"^const LIB=\{.*\};$", re.M)
LIB_LOCAL = 'const LIB={pdf:"vendor/jspdf.umd.min.js?v=%(v)s",xlsx:"vendor/exceljs.min.js?v=%(v)s",font:()=>"vendor/fonts.css?v=%(v)s"};'
VENDOR_NEEDED = ("jspdf.umd.min.js", "exceljs.min.js", "fonts.css")
START, END = "/* Speicher: gemeinsame Datenbank, sonst lokal */", "/* Anzeige */"
# Namen, die nur die Claude-Version braucht (lokaler Browser-Speicher, Claude-Datenbank)
ARTIFACT_ONLY = {"lsGet", "lsSet", "lsGetReg", "lsSetReg", "metaCol"}
# Eingebaute Browser-Funktionen und Schlüsselwörter, die im Speicher-Block aufgerufen werden dürfen
BUILTIN = set("""if for while switch catch return function typeof await async new fetch setInterval setTimeout clearTimeout
JSON Object Array String Number Boolean Error Blob File URL Promise Math Date matchMedia encodeURIComponent""".split())
STORAGE = '''/* Speicher: Server im Home-Assistant-Add-on (relative Pfade wegen Ingress) */
let rev=-1;
function prefGet(k){try{return localStorage.getItem("haus-"+k)}catch(e){return null}}
function prefSet(k,v){try{localStorage.setItem("haus-"+k,v)}catch(e){}if(typeof prefSync==="function")prefSync(k,v)}
let USER=null;
async function api(path,opt){opt=opt||{};if(opt.method&&opt.method!=="GET")opt={...opt,headers:{...(opt.headers||{}),"X-Planner":"1"}};const r=await fetch(path,opt);if(r.status===409){const e=new Error("409");e.conflict=await r.json().catch(()=>({}));throw e}if(!r.ok)throw new Error(r.status);return r.json()}
async function pull(force){
  try{const j=await api("api/tasks"+(force?"":"?rev="+rev));
    $("note").textContent="";
    if(j.version)$("ver").textContent="Add-on-Version "+j.version;
    haInfo=j.ha||null;
    if(j.tasks){const sg=a=>JSON.stringify(a.map(t=>{const {v,...r}=t;return r})),same=loaded&&sg(RAW)===sg(j.tasks)&&JSON.stringify(reg)===JSON.stringify(j.tags||[]);
      RAW=j.tasks;reg=j.tags||[];regLoaded=true;rev=j.rev;loaded=true;if(!same)render()}
  }catch(e){$("note").textContent="Keine Verbindung zum Server – Änderungen werden evtl. nicht gespeichert."}
}
async function saveTask(t,o){
  const i=RAW.findIndex(x=>x.id===t.id);i>=0?RAW[i]=t:RAW.push(t);render();
  try{await api("api/task",{method:"POST",headers:{"Content-Type":"application/json",...(o&&o.check?{"X-Check":"1"}:{})},body:JSON.stringify(t)})}
  catch(e){
    if(e.conflict&&e.conflict.task){const s=e.conflict.task,j=RAW.findIndex(x=>x.id===s.id);if(j>=0)RAW[j]=s;render();
      toast("„"+s.title+"“ wurde zwischenzeitlich geändert. Deine Änderung ist nicht gespeichert.",()=>saveTask({...t,v:s.v}),"Trotzdem speichern",10000);return}
    $("note").textContent="Speichern fehlgeschlagen."}
  pull(true);
}
async function delTask(id){
  RAW=RAW.filter(t=>t.id!==id).map(t=>({...t,deps:(t.deps||[]).filter(x=>x!==id)}));render();
  try{await api("api/task/"+id,{method:"DELETE"})}catch(e){$("note").textContent="Löschen fehlgeschlagen."}
  pull(true);
}
async function saveReg(l){
  reg=l;render();
  try{await api("api/tags",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({tags:l})})}
  catch(e){$("note").textContent="Tags speichern fehlgeschlagen."}
  pull(true);
}
async function saveMany(list){
  list.forEach(t=>{const i=RAW.findIndex(x=>x.id===t.id);i>=0?RAW[i]=t:RAW.push(t)});render();
  try{await api("api/import",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({tasks:list})})}
  catch(e){$("note").textContent="Speichern fehlgeschlagen."}
  pull(true);
}
const aiAvail=()=>!!(haInfo&&haInfo.ai);
async function aiJson(prompt,raw){const r=await api("api/ai",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt,raw:!!raw})});if(!r.ok)throw new Error(r.error||"KI-Fehler");return r.data}
const PK=["theme","design","font","me","sort","glw","hwho","htile"];
function prefSync(k,v){if(!USER||!PK.includes(k))return;fetch("api/me",{method:"POST",headers:{"Content-Type":"application/json","X-Planner":"1"},body:JSON.stringify({[k]:v||""})}).catch(()=>{})}
async function initUser(){
  try{const r=await fetch("api/me",{cache:"no-store"}),j=await r.json();if(!j.user)return;USER=j.user;const sp=j.prefs||{};
    if(Object.keys(sp).length){PK.forEach(k=>{try{if(sp[k])localStorage.setItem("haus-"+k,sp[k]);else localStorage.removeItem("haus-"+k)}catch(_){}})}
    else{const up={};PK.forEach(k=>{const v=prefGet(k);if(v)up[k]=v});if(Object.keys(up).length)fetch("api/me",{method:"POST",headers:{"Content-Type":"application/json","X-Planner":"1"},body:JSON.stringify(up)}).catch(()=>{})}
    if(!prefGet("me")){const first=USER.split(/\\s+/)[0].toLowerCase(),m=["Lasse","Melanie",...allWho()].find(n=>n.toLowerCase()===first);if(m){prefSet("me",m);prefSet("onb","1")}}
    applyTheme();applyFont();render()}catch(_){}}
function init(){
  initUser();
  pull(true);setInterval(()=>pull(),5000);
  document.addEventListener("visibilitychange",()=>{if(!document.hidden)pull()});
}

'''
DL = '''async function dl(name,data){
  try{const blob=data instanceof Blob?data:new Blob([data],{type:"application/pdf"}),file=new File([blob],name,{type:blob.type});
    if(matchMedia("(pointer:coarse)").matches&&navigator.canShare&&navigator.canShare({files:[file]})){
      try{await navigator.share({files:[file]});$("dlx").close();return}catch(e){if(e&&e.name==="AbortError")return}}
    const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(a.href),5000);$("dlx").close()
  }catch(e){$("note").textContent="Download fehlgeschlagen: "+(e.message||e)}}
'''
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


def check_contract(src_block, html):
    missing = sorted(top_level_names(src_block) - top_level_names(STORAGE) - ARTIFACT_ONLY)
    if missing:
        fail("Diese Namen stehen in src/planner.html im Speicher-Block, fehlen aber in der Add-on-Version: %s\n"
             "  → in tools/build.py (STORAGE) ergänzen oder, wenn nur für Claude nötig, in ARTIFACT_ONLY eintragen." % ", ".join(missing))
    calls = set(re.findall(r"(?<![\w$.])([A-Za-z_$][\w$]*)\s*\(", STORAGE)) - BUILTIN
    unknown = sorted(c for c in calls if c != "$" and not defined_anywhere(c, html))
    if unknown:
        fail("Die Add-on-Version ruft Funktionen auf, die es in der Datei nicht gibt: %s" % ", ".join(unknown))


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


def build():
    cfg = open(os.path.join(ADDON, "config.yaml"), encoding="utf-8").read()
    ver = re.search(r'^version:\s*"?([^"\n]+)"?\s*$', cfg, re.M).group(1).strip()
    src = open(SRC, encoding="utf-8").read()
    if src.count(START) != 1 or src.count(END) != 1 or src.index(START) > src.index(END):
        fail("Markierungen für den Speicher-Block in src/planner.html fehlen oder sind doppelt")
    a, b = src.index(START), src.index(END)
    s = src[:a] + STORAGE + src[b:]
    s, n = re.subn(r"async function dl\(name,data\)\{.*\n", lambda m: DL, s, count=1)
    if n != 1:
        fail("dl()-Funktion in src/planner.html nicht gefunden")
    if "claude.use" in s or "window.claude" in s or "lsGet(" in s:
        fail("Claude-/Browser-spezifischer Code ist noch in der Add-on-Version")
    if s.count("</head>") != 1:
        fail("</head> nicht eindeutig")
    s = s.replace("</head>", PWA + ERRLOG % ver + "</head>")
    if vendor_ok():
        s, n = LIB_LINE.subn(lambda m: LIB_LOCAL % {"v": ver}, s)
        if n != 1:
            fail("Zeile „const LIB={…};“ in src/planner.html nicht genau einmal gefunden")
        ext = sorted(set(re.findall(r"https://(?:cdnjs\.cloudflare\.com|fonts\.googleapis\.com|fonts\.gstatic\.com)[^\"' )]*", s)))
        if ext:
            fail("Add-on-Version lädt noch aus dem Internet: %s" % ", ".join(ext))
    else:
        print("Hinweis: planner/vendor/ fehlt, Add-on lädt Bibliotheken und Schriften aus dem Internet")
    check_contract(src[a:b], s)
    check_syntax(src, "src/planner.html")
    check_syntax(s, "planner/index.html")
    return s, ver + "\n"


def main():
    html, ver = build()
    out = {os.path.join(ADDON, "index.html"): html, os.path.join(ADDON, "VERSION"): ver}
    if "--check" in sys.argv:
        old = [p for p, c in out.items() if not os.path.exists(p) or open(p, encoding="utf-8").read() != c]
        if old:
            fail("Veraltet: %s. Bitte python3 tools/build.py ausführen und mit einchecken." % ", ".join(os.path.relpath(p, ROOT) for p in old))
        print("OK: planner/index.html und VERSION passen zu src/planner.html und config.yaml (Version %s)" % ver.strip())
        return
    for p, c in out.items():
        open(p, "w", encoding="utf-8").write(c)
    print("OK: planner/index.html und VERSION erzeugt, Version", ver.strip())


if __name__ == "__main__":
    main()
