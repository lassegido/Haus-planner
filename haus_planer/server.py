import json, os, re, shutil, threading, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# /data bleibt bei Updates und Neu-Bauen des Add-ons erhalten.
# Zusätzlich wird jede Änderung nach /share/haus_planer gespiegelt (überlebt sogar Deinstallation).
D = os.environ.get("DATA_DIR", "/data")
SHARE = os.environ.get("SHARE_DIR", "/share/haus_planer")
INDEX = os.environ.get("INDEX", "/app/index.html")
VERFILE = os.environ.get("VERSION_FILE", "/app/VERSION")
PORT = int(os.environ.get("PORT", "8099"))
DATA = os.path.join(D, "tasks.json")
BK = os.path.join(D, "backups")
LOCK = threading.Lock()
state = {"rev": 0, "tasks": {}}
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
ID = re.compile(r"[A-Za-z0-9_-]{1,40}")
DAILY = re.compile(r"tasks-\d{4}-\d{2}-\d{2}\.json")


def version():
    try:
        with open(VERFILE, encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "?"


def read_file(path):
    with open(path, encoding="utf-8") as f:
        j = json.load(f)
    return {t["id"]: t for t in j.get("tasks", [])}, j.get("rev", 0)


def load():
    os.makedirs(D, exist_ok=True)
    if os.path.exists(DATA):
        try:
            state["tasks"], state["rev"] = read_file(DATA)
            return
        except Exception as e:
            print("Datendatei defekt, wird beiseite gelegt:", e, flush=True)
            shutil.copyfile(DATA, DATA + ".defekt-" + time.strftime("%Y%m%d%H%M%S"))
    mirror = os.path.join(SHARE, "tasks-latest.json")
    if os.path.exists(mirror):
        try:
            state["tasks"], state["rev"] = read_file(mirror)
            print("Daten aus dem Share-Spiegel wiederhergestellt (%d Aufgaben)" % len(state["tasks"]), flush=True)
            save()
        except Exception as e:
            print("Share-Spiegel nicht lesbar:", e, flush=True)


def prune(folder, keep=30):
    files = sorted(f for f in os.listdir(folder) if DAILY.fullmatch(f))
    for old in files[:-keep]:
        os.remove(os.path.join(folder, old))


def save():
    os.makedirs(BK, exist_ok=True)
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"rev": state["rev"], "tasks": list(state["tasks"].values())}, f, ensure_ascii=False)
    os.replace(tmp, DATA)
    day = "tasks-%s.json" % time.strftime("%Y-%m-%d")
    shutil.copyfile(DATA, os.path.join(BK, day))
    prune(BK)
    try:
        os.makedirs(SHARE, exist_ok=True)
        shutil.copyfile(DATA, os.path.join(SHARE, "tasks-latest.json"))
        shutil.copyfile(DATA, os.path.join(SHARE, day))
        prune(SHARE)
    except Exception as e:
        print("Share-Spiegel nicht möglich:", e, flush=True)


def clean(t):
    if not isinstance(t, dict):
        return None
    i = str(t.get("id", ""))
    s, e = str(t.get("start", "")), str(t.get("end", ""))
    if not ID.fullmatch(i) or not DATE.fullmatch(s) or not DATE.fullmatch(e):
        return None
    title = str(t.get("title", "")).strip()[:200]
    if not title:
        return None
    st = t.get("status")
    deps = [str(x) for x in t.get("deps", []) if isinstance(x, str) and ID.fullmatch(x) and x != i][:50]
    ck = [{"t": str(c.get("t", ""))[:200], "d": bool(c.get("d"))}
          for c in t.get("checklist", []) if isinstance(c, dict)][:100]
    return {"id": i, "title": title, "area": str(t.get("area", ""))[:60], "who": str(t.get("who", ""))[:60],
            "status": st if st in ("todo", "doing", "done") else "todo", "start": s, "end": e,
            "notes": str(t.get("notes", ""))[:4000], "deps": deps, "checklist": ck}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def out(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path.endswith("/api/tasks"):
            q = parse_qs(u.query).get("rev", [""])[0]
            with LOCK:
                if q == str(state["rev"]):
                    return self.out(200, {"rev": state["rev"], "version": version()})
                return self.out(200, {"rev": state["rev"], "version": version(), "tasks": list(state["tasks"].values())})
        with open(INDEX, "rb") as f:
            self.out(200, f.read(), "text/html")

    def body(self):
        n = int(self.headers.get("Content-Length", "0"))
        if n > 2_000_000:
            raise ValueError
        return json.loads(self.rfile.read(n))

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            data = self.body()
        except Exception:
            return self.out(400, {"error": "ungültige Anfrage"})
        if path.endswith("/api/task"):
            items = [clean(data)]
        elif path.endswith("/api/import"):
            items = [clean(t) for t in (data.get("tasks", []) if isinstance(data, dict) else [])]
        else:
            return self.out(404, {"error": "nicht gefunden"})
        items = [t for t in items if t]
        if not items:
            return self.out(400, {"error": "ungültige Aufgabe"})
        with LOCK:
            for t in items:
                state["tasks"][t["id"]] = t
            state["rev"] += 1
            save()
            self.out(200, {"rev": state["rev"], "count": len(items)})

    def do_DELETE(self):
        m = re.search(r"/api/task/([A-Za-z0-9_-]{1,40})$", urlparse(self.path).path)
        if not m:
            return self.out(404, {"error": "nicht gefunden"})
        i = m.group(1)
        with LOCK:
            state["tasks"].pop(i, None)
            for t in state["tasks"].values():
                t["deps"] = [d for d in t.get("deps", []) if d != i]
            state["rev"] += 1
            save()
            self.out(200, {"rev": state["rev"]})


if __name__ == "__main__":
    load()
    if state["tasks"]:
        save()  # bestehende Daten beim Start einmal in den Share-Spiegel kopieren
    print("Haus-Planer %s läuft auf Port %d, Daten in %s" % (version(), PORT, D), flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
