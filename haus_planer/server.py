import datetime, json, os, re, shutil, threading, time, urllib.request
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
state = {"rev": 0, "tasks": {}, "tags": []}
COLORS = ("sky", "sun", "sea", "brick", "mint", "rose", "lilac", "sand", "slate", "lemon")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
ID = re.compile(r"[A-Za-z0-9_-]{1,40}")
DAILY = re.compile(r"tasks-\d{4}-\d{2}-\d{2}\.json")
OPTS = os.path.join(D, "options.json")
HASTATE = os.path.join(D, "ha_state.json")
SUP = os.environ.get("SUPERVISOR_URL", "http://supervisor/core/api")
TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
ha = {"tz": None, "last": ""}


def version():
    try:
        with open(VERFILE, encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "?"


def read_file(path):
    with open(path, encoding="utf-8") as f:
        j = json.load(f)
    return {t["id"]: t for t in j.get("tasks", [])}, j.get("rev", 0), clean_tags(j.get("tags", []))


def load():
    os.makedirs(D, exist_ok=True)
    if os.path.exists(DATA):
        try:
            state["tasks"], state["rev"], state["tags"] = read_file(DATA)
            return
        except Exception as e:
            print("Datendatei defekt, wird beiseite gelegt:", e, flush=True)
            shutil.copyfile(DATA, DATA + ".defekt-" + time.strftime("%Y%m%d%H%M%S"))
    mirror = os.path.join(SHARE, "tasks-latest.json")
    if os.path.exists(mirror):
        try:
            state["tasks"], state["rev"], state["tags"] = read_file(mirror)
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
        json.dump({"rev": state["rev"], "tasks": list(state["tasks"].values()), "tags": state["tags"]}, f, ensure_ascii=False)
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


def clean_tags(lst):
    out, seen = [], set()
    for x in lst if isinstance(lst, list) else []:
        if not isinstance(x, dict):
            continue
        n = str(x.get("n", "")).strip()[:30]
        key = (bool(x.get("p")), n.lower())
        if not n or key in seen:
            continue
        seen.add(key)
        c = x.get("c")
        out.append({"n": n, "c": c if c in COLORS else "", **({"p": 1} if x.get("p") else {})})
    return out[:100]


def clean_rec(r):
    if isinstance(r, dict) and r.get("u") in ("d", "w", "m", "y"):
        try:
            n = int(r.get("n", 1))
        except (TypeError, ValueError):
            return None
        if 1 <= n <= 60:
            return {"n": n, "u": r["u"]}
    return None


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
    tags = t.get("tags")
    if not isinstance(tags, list):
        tags = [t.get("area")] if t.get("area") else []
    tags = [n for n in dict.fromkeys(str(x).strip()[:30] for x in tags if isinstance(x, str)) if n][:20]
    return {"id": i, "title": title, "area": (tags[0] if tags else str(t.get("area", ""))[:60]), "tags": tags, "proj": str(t.get("proj", "") or "")[:30], "ms": bool(t.get("ms")), "rec": clean_rec(t.get("rec")), "spawned": str(t.get("spawned", "") or "")[:40], "who": str(t.get("who", ""))[:60],
            "status": st if st in ("todo", "doing", "done") else "todo", "start": s, "end": e,
            "notes": str(t.get("notes", ""))[:4000], "deps": deps, "checklist": ck,
            "arch": bool(t.get("arch")), "del": bool(t.get("del")), "delAt": str(t.get("delAt", "") or "")[:10]}


# ---- Home Assistant: Erinnerungen und Sensoren (nur im Add-on, über die Supervisor-Schnittstelle)
def options():
    try:
        with open(OPTS, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def services():
    out = []
    for x in str(options().get("notify_service") or "").split(","):
        x = x.strip()
        if x.startswith("notify."):
            x = x[7:]
        if re.fullmatch(r"[A-Za-z0-9_]+", x):
            out.append(x)
    return out


def ha_info():
    o = options()
    return {"api": bool(TOKEN), "notify": services(), "time": str(o.get("reminder_time") or "08:00"),
            "sensors": bool(o.get("sensors", True))}


def ha_call(method, path, body=None):
    req = urllib.request.Request(SUP + path, method=method, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        raw = r.read()
        return json.loads(raw) if raw else None


def init_tz():
    name = None
    if TOKEN:
        try:
            name = (ha_call("GET", "/config") or {}).get("time_zone")
        except Exception as e:
            print("HA-Zeitzone nicht lesbar:", e, flush=True)
    name = name or os.environ.get("TZ")
    if name:
        try:
            from zoneinfo import ZoneInfo
            ha["tz"] = ZoneInfo(name)
        except Exception as e:
            print("Zeitzone nicht verfügbar:", e, flush=True)
    try:
        with open(HASTATE, encoding="utf-8") as f:
            ha["last"] = json.load(f).get("last", "")
    except Exception:
        pass


def stats(tasks, today):
    act = [t for t in tasks if not t.get("del") and not t.get("arch") and t["status"] != "done"]
    due = [t for t in act if t["end"] == today]
    late = [t for t in act if t["end"] < today]
    doing = [t for t in act if t["status"] == "doing"]
    return act, due, late, doing


def reminder_text(due, late):
    parts = []
    if due:
        parts.append("%d heute fällig" % len(due))
    if late:
        parts.append("%d überfällig" % len(late))
    names = [t["title"] for t in late + due]
    txt = ", ".join(parts) + ": " + ", ".join(names[:4]) + (" …" if len(names) > 4 else "")
    return txt


def notify(message):
    sv = services()
    if not sv:
        raise RuntimeError("Kein Benachrichtigungsdienst eingetragen")
    for s in sv:
        ha_call("POST", "/services/notify/" + s, {"title": "Haus-planner", "message": message})


def put_sensor(key, name, value, icon, titles):
    ha_call("POST", "/states/sensor.haus_planner_" + key,
            {"state": str(value), "attributes": {"friendly_name": name, "unit_of_measurement": "Aufgaben", "icon": icon, "aufgaben": titles[:20]}})


def ha_tick():
    if not TOKEN:
        return
    o = options()
    now = datetime.datetime.now(ha["tz"]) if ha["tz"] else datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    with LOCK:
        tasks = list(state["tasks"].values())
    act, due, late, doing = stats(tasks, today)
    if o.get("sensors", True):
        for key, name, icon, lst in (("offen", "Haus-planner offen", "mdi:clipboard-list-outline", act),
                                     ("in_arbeit", "Haus-planner in Arbeit", "mdi:hammer-wrench", doing),
                                     ("ueberfaellig", "Haus-planner überfällig", "mdi:alert-circle-outline", late),
                                     ("heute_faellig", "Haus-planner heute fällig", "mdi:calendar-today", due)):
            put_sensor(key, name, len(lst), icon, [t["title"] for t in lst])
    when = str(o.get("reminder_time") or "08:00")
    if services() and now.strftime("%H:%M") >= when and ha["last"] != today:
        if due or late:
            notify(reminder_text(due, late))
        ha["last"] = today
        with open(HASTATE, "w", encoding="utf-8") as f:
            json.dump({"last": today}, f)


def ha_loop():
    time.sleep(5)
    init_tz()
    while True:
        try:
            ha_tick()
        except Exception as e:
            print("Home-Assistant-Abgleich:", e, flush=True)
        time.sleep(60)


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
                    return self.out(200, {"rev": state["rev"], "version": version(), "ha": ha_info()})
                return self.out(200, {"rev": state["rev"], "version": version(), "tasks": list(state["tasks"].values()), "tags": state["tags"], "ha": ha_info()})
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
        if path.endswith("/api/ha-test"):
            try:
                if not TOKEN:
                    raise RuntimeError("Keine Verbindung zu Home Assistant")
                notify("Testnachricht vom Haus-planner – die Erinnerungen funktionieren.")
                return self.out(200, {"ok": True})
            except Exception as e:
                return self.out(200, {"ok": False, "error": str(e)[:200]})
        if path.endswith("/api/tags"):
            with LOCK:
                state["tags"] = clean_tags(data.get("tags", []) if isinstance(data, dict) else [])
                state["rev"] += 1
                save()
                return self.out(200, {"rev": state["rev"], "count": len(state["tags"])})
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
    print("Haus-planner %s läuft auf Port %d, Daten in %s" % (version(), PORT, D), flush=True)
    threading.Thread(target=ha_loop, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
