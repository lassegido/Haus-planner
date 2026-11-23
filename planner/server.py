import base64, datetime, hashlib, json, os, re, secrets, shutil, socket, struct, threading, time, urllib.error, urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote

# /data bleibt bei Updates und Neu-Bauen des Add-ons erhalten.
# Zusätzlich wird jede Änderung nach /share/planner gespiegelt (überlebt sogar Deinstallation).
D = os.environ.get("DATA_DIR", "/data")
SHARE = os.environ.get("SHARE_DIR", "/share/planner")
LEGACY_SHARE = os.environ.get("LEGACY_SHARE_DIR", "/share/haus_planer")  # alter Spiegel (bis 1.13)
INDEX = os.environ.get("INDEX", "/app/index.html")
VERFILE = os.environ.get("VERSION_FILE", "/app/VERSION")
PORT = int(os.environ.get("PORT", "8099"))
DATA = os.path.join(D, "tasks.json")
BK = os.path.join(D, "backups")
FILES = os.path.join(D, "files")
ICONS = os.environ.get("ICONS_DIR", os.path.join(os.path.dirname(INDEX), "icons"))
FID = re.compile(r"[a-f0-9]{12}")
SAFE = ("image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf")
LOCK = threading.Lock()
state = {"rev": 0, "tasks": {}, "tags": []}
COLORS = ("sky", "sun", "sea", "brick", "mint", "rose", "lilac", "sand", "slate", "lemon")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
ID = re.compile(r"[A-Za-z0-9_-]{1,40}")
DAILY = re.compile(r"tasks-\d{4}-\d{2}-\d{2}\.json")
MONTHLY = re.compile(r"tasks-monat-\d{4}-\d{2}\.json")
SCHEMA = 2  # Datenformat-Version; neuere Dateien werden nie abwärts beschnitten, ältere beim Lesen ergänzt
ICON = re.compile(r"[a-z]{2,20}")
OPTS = os.path.join(D, "options.json")
HASTATE = os.path.join(D, "ha_state.json")
SETTINGS = os.path.join(D, "settings.json")  # Auswahl aus der App (Erinnerung), hat Vorrang vor der Add-on-Konfiguration
SUP = os.environ.get("SUPERVISOR_URL", "http://supervisor/core/api")
SUPBASE = os.environ.get("SUPERVISOR_BASE", "http://supervisor")
WS_URL = os.environ.get("HA_WS_URL", "ws://supervisor/core/websocket")
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
    tasks = {t["id"]: t for t in j.get("tasks", [])}
    for t in tasks.values():
        t.setdefault("v", 0)  # Dateien aus älteren Versionen haben noch keine Versionsnummer
    return tasks, j.get("rev", 0), clean_tags(j.get("tags", []))


def load():
    os.makedirs(D, exist_ok=True)
    if os.path.exists(DATA):
        try:
            state["tasks"], state["rev"], state["tags"] = read_file(DATA)
            return
        except Exception as e:
            print("Datendatei defekt, wird beiseite gelegt:", e, flush=True)
            shutil.copyfile(DATA, DATA + ".defekt-" + time.strftime("%Y%m%d%H%M%S"))
    for src in (SHARE, LEGACY_SHARE):
        mirror = os.path.join(src, "tasks-latest.json")
        if not os.path.exists(mirror):
            continue
        try:
            state["tasks"], state["rev"], state["tags"] = read_file(mirror)
            print("Daten aus dem Share-Spiegel %s wiederhergestellt (%d Aufgaben)" % (src, len(state["tasks"])), flush=True)
            if src != SHARE:
                legacy_files = os.path.join(src, "files")
                if os.path.isdir(legacy_files):
                    try:
                        shutil.copytree(legacy_files, os.path.join(SHARE, "files"), dirs_exist_ok=True)
                        shutil.copytree(legacy_files, FILES, dirs_exist_ok=True)
                    except Exception as e:
                        print("Dateianhänge nicht übernommen:", e, flush=True)
            save()
            return
        except Exception as e:
            print("Share-Spiegel nicht lesbar:", e, flush=True)


def prune(folder, keep=30, keep_months=24):
    files = sorted(f for f in os.listdir(folder) if DAILY.fullmatch(f))
    for old in files[:-keep]:
        os.remove(os.path.join(folder, old))
    months = sorted(f for f in os.listdir(folder) if MONTHLY.fullmatch(f))
    for old in months[:-keep_months]:
        os.remove(os.path.join(folder, old))


def snapshot(folder):
    """Je Monat eine Sicherung (die erste Speicherung im Monat), damit auch ältere Stände erreichbar bleiben."""
    p = os.path.join(folder, "tasks-monat-%s.json" % time.strftime("%Y-%m"))
    if not os.path.exists(p):
        shutil.copyfile(DATA, p)


def save():
    os.makedirs(BK, exist_ok=True)
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"schema": SCHEMA, "rev": state["rev"], "tasks": list(state["tasks"].values()), "tags": state["tags"]}, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, DATA)
    day = "tasks-%s.json" % time.strftime("%Y-%m-%d")
    shutil.copyfile(DATA, os.path.join(BK, day))
    snapshot(BK)
    prune(BK)
    try:
        os.makedirs(SHARE, exist_ok=True)
        shutil.copyfile(DATA, os.path.join(SHARE, "tasks-latest.json"))
        shutil.copyfile(DATA, os.path.join(SHARE, day))
        snapshot(SHARE)
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
        ic = str(x.get("i", ""))
        out.append({"n": n, "c": c if c in COLORS else "", **({"p": 1} if x.get("p") else {}), **({"i": ic} if ICON.fullmatch(ic) and not x.get("p") else {})})
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


def clean_log(lst):
    out = []
    for x in lst if isinstance(lst, list) else []:
        if isinstance(x, dict) and x.get("k") in ("c", "h") and str(x.get("x", "")).strip():
            out.append({"t": str(x.get("t", ""))[:16], "a": str(x.get("a", "") or "")[:30], "k": x["k"], "x": str(x["x"])[:500]})
    return out[-120:]


def clean_files(lst):
    out = []
    for f in lst if isinstance(lst, list) else []:
        if isinstance(f, dict) and FID.fullmatch(str(f.get("id", ""))):
            try:
                size = int(f.get("s", 0))
            except (TypeError, ValueError):
                size = 0
            out.append({"id": f["id"], "n": str(f.get("n", "Datei"))[:120], "s": size, "ty": str(f.get("ty", ""))[:60]})
    return out[:30]


def file_path(tid, fid):
    for base in (FILES, os.path.join(SHARE, "files")):
        p = os.path.join(base, tid, fid)
        if os.path.isfile(p):
            return p
    return None


def drop_files(tid, fid=None):
    for base in (FILES, os.path.join(SHARE, "files")):
        p = os.path.join(base, tid) if fid is None else os.path.join(base, tid, fid)
        try:
            shutil.rmtree(p) if fid is None else os.remove(p)
        except Exception:
            pass


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
            "status": st if st in ("todo", "doing", "done") else "todo", "prio": (t.get("prio") if t.get("prio") in (1, 2, 3) else 0), "start": s, "end": e,
            "notes": str(t.get("notes", ""))[:4000], "deps": deps, "checklist": ck,
            "arch": bool(t.get("arch")), "del": bool(t.get("del")), "delAt": str(t.get("delAt", "") or "")[:10],
            "log": clean_log(t.get("log")), "files": clean_files(t.get("files")), "v": 0}


# ---- Home Assistant: Erinnerungen und Sensoren (nur im Add-on, über die Supervisor-Schnittstelle)
def options():
    try:
        with open(OPTS, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def app_settings():
    try:
        with open(SETTINGS, encoding="utf-8") as f:
            d = json.load(f)
            return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def save_app_settings(d):
    tmp = SETTINGS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    os.replace(tmp, SETTINGS)


def remind_time():
    t = app_settings().get("time")
    if isinstance(t, str) and re.fullmatch(r"([01][0-9]|2[0-3]):[0-5][0-9]", t):
        return t
    return str(options().get("reminder_time") or "08:00")


def services():
    out = []
    st = app_settings()
    raw = st["notify"] if isinstance(st.get("notify"), list) else str(options().get("notify_service") or "").split(",")
    for x in raw:
        x = str(x)
        x = x.strip()
        if x.startswith("notify."):
            x = x[7:]
        if re.fullmatch(r"[A-Za-z0-9_]+", x):
            out.append(x)
    return out


def ha_info():
    o = options()
    return {"api": bool(TOKEN), "notify": services(), "time": remind_time(),
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
    names = [t["title"] for t in sorted(late + due, key=lambda t: t.get("prio") or 9)]
    txt = ", ".join(parts) + ": " + ", ".join(names[:4]) + (" …" if len(names) > 4 else "")
    return txt


def notify(message, data=None):
    sv = services()
    if not sv:
        raise RuntimeError("Kein Benachrichtigungsdienst eingetragen")
    for s in sv:
        body = {"title": "Planner", "message": message}
        if data:
            body["data"] = data
        ha_call("POST", "/services/notify/" + s, body)


NTAG = "planner-faellig"
panel = {"url": None}


def panel_url():
    # Adresse des Planner-Bereichs in Home Assistant, damit ein Antippen der Mitteilung direkt dorthin führt
    if panel["url"] is None:
        panel["url"] = ""
        try:
            req = urllib.request.Request(SUPBASE + "/addons/self/info", headers={"Authorization": "Bearer " + TOKEN})
            with urllib.request.urlopen(req, timeout=10) as r:
                slug = (json.load(r).get("data") or {}).get("slug", "")
            if re.fullmatch(r"[A-Za-z0-9_]+", slug):
                panel["url"] = "/hassio/ingress/" + slug
        except Exception as e:
            print("Planner-Adresse nicht lesbar:", e, flush=True)
    return panel["url"]


def can_complete(t, tasks):
    # Wiederkehrende Aufgaben (legen die nächste an) und blockierte Aufgaben werden nur in der App erledigt
    if t.get("rec") and not t.get("spawned"):
        return False
    return all(tasks.get(d, {}).get("status") == "done" or d not in tasks for d in t.get("deps", []))


def reminder_data(due, late, tasks, quiet=False):
    cand = sorted(late + due, key=lambda t: (t.get("prio") or 9, t["end"]))
    acts = [{"action": "PLANNER_DONE_" + t["id"], "title": ("Erledigt: " + t["title"])[:30]} for t in cand if can_complete(t, tasks)][:4]
    d = {"tag": NTAG, "actions": acts}
    u = panel_url()
    if u:
        d["url"] = u
        d["clickAction"] = u
    if quiet:
        d["push"] = {"interruption-level": "passive"}
    return d


def complete_task(tid):
    with LOCK:
        t = state["tasks"].get(tid)
        if not t or t.get("del") or t.get("status") == "done" or not can_complete(t, state["tasks"]):
            return None
        n = dict(t)
        n["status"] = "done"
        n["log"] = (t.get("log") or []) + [{"t": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"), "a": "iPhone", "k": "h", "x": "Status: Erledigt (Mitteilung)"}]
        n["log"] = n["log"][-120:]
        n["v"] = t.get("v", 0) + 1
        state["tasks"][tid] = n
        state["rev"] += 1
        save()
        return n["title"]


def refresh_notification():
    now = datetime.datetime.now(ha["tz"]) if ha["tz"] else datetime.datetime.now()
    with LOCK:
        tasks = dict(state["tasks"])
    act, due, late, doing = stats(list(tasks.values()), now.strftime("%Y-%m-%d"))
    if due or late:
        notify(reminder_text(due, late), reminder_data(due, late, tasks, quiet=True))
    else:
        for s in services():
            ha_call("POST", "/services/notify/" + s, {"message": "clear_notification", "data": {"tag": NTAG}})


# ---- Verbindung zu Home Assistant (WebSocket), um Knopfdrücke in Mitteilungen zu empfangen
def _recv(sock, n):
    buf = b""
    while len(buf) < n:
        c = sock.recv(n - len(buf))
        if not c:
            raise ConnectionError("Verbindung beendet")
        buf += c
    return buf


def ws_send(sock, payload, op=1):
    b = payload if isinstance(payload, bytes) else payload.encode()
    mask = os.urandom(4)
    n = len(b)
    head = bytes([0x80 | op]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack(">H", n) if n < 65536 else bytes([0x80 | 127]) + struct.pack(">Q", n))
    sock.sendall(head + mask + bytes(c ^ mask[i % 4] for i, c in enumerate(b)))


def ws_recv(sock):
    # liefert eine vollständige Textnachricht; Ping wird beantwortet
    data = b""
    while True:
        b0, b1 = _recv(sock, 2)
        n = b1 & 0x7F
        if n == 126:
            n = struct.unpack(">H", _recv(sock, 2))[0]
        elif n == 127:
            n = struct.unpack(">Q", _recv(sock, 8))[0]
        if n > 4_000_000:
            raise ConnectionError("Nachricht zu groß")
        mk = _recv(sock, 4) if b1 & 0x80 else None
        pl = _recv(sock, n) if n else b""
        if mk:
            pl = bytes(c ^ mk[i % 4] for i, c in enumerate(pl))
        op = b0 & 0x0F
        if op == 8:
            raise ConnectionError("Verbindung geschlossen")
        if op == 9:
            ws_send(sock, pl, 10)
            continue
        if op == 10:
            continue
        data += pl
        if b0 & 0x80:
            return data.decode("utf-8", "replace")


def ws_open(url):
    from urllib.parse import urlparse as up
    u = up(url)
    sock = socket.create_connection((u.hostname, u.port or 80), timeout=15)
    key = base64.b64encode(os.urandom(16)).decode()
    sock.sendall(("GET %s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n"
                  % (u.path or "/", u.netloc, key)).encode())
    head = b""
    while b"\r\n\r\n" not in head:
        head += _recv(sock, 1)
    if b" 101 " not in head.split(b"\r\n")[0] + b" ":
        raise ConnectionError("WebSocket abgelehnt")
    want = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest())
    if want not in head:
        raise ConnectionError("WebSocket-Antwort ungültig")
    return sock


def handle_action(action):
    m = re.fullmatch(r"PLANNER_DONE_([A-Za-z0-9_-]{1,40})", action or "")
    if not m:
        return
    title = complete_task(m.group(1))
    print("Mitteilung: Aufgabe erledigt:", title, flush=True)
    try:
        refresh_notification()
    except Exception as e:
        print("Mitteilung nicht aktualisiert:", e, flush=True)


def ws_session():
    sock = ws_open(WS_URL)
    try:
        sock.settimeout(90)
        first = json.loads(ws_recv(sock))
        if first.get("type") != "auth_required":
            raise ConnectionError("unerwartete Antwort")
        ws_send(sock, json.dumps({"type": "auth", "access_token": TOKEN}))
        if json.loads(ws_recv(sock)).get("type") != "auth_ok":
            raise ConnectionError("Anmeldung bei Home Assistant fehlgeschlagen")
        ws_send(sock, json.dumps({"id": 1, "type": "subscribe_events", "event_type": "mobile_app_notification_action"}))
        print("Verbindung zu Home Assistant für Mitteilungs-Knöpfe steht", flush=True)
        wsok["ok"] = True
        while True:
            try:
                msg = json.loads(ws_recv(sock))
            except socket.timeout:
                ws_send(sock, b"", 9)
                continue
            if msg.get("type") == "event":
                handle_action(str(((msg.get("event") or {}).get("data") or {}).get("action", "")))
    finally:
        try:
            sock.close()
        except Exception:
            pass


wsok = {"ok": False}


def ws_loop():
    wait = 5
    while True:
        wsok["ok"] = False
        try:
            ws_session()
        except Exception as e:
            print("HA-Verbindung (Mitteilungs-Knöpfe):", e, flush=True)
        wait = 5 if wsok["ok"] else min(wait * 2, 60)
        time.sleep(wait)


def put_sensor(key, name, value, icon, titles):
    ha_call("POST", "/states/sensor.planner_" + key,
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
        for key, name, icon, lst in (("offen", "Planner offen", "mdi:clipboard-list-outline", act),
                                     ("in_arbeit", "Planner in Arbeit", "mdi:hammer-wrench", doing),
                                     ("ueberfaellig", "Planner überfällig", "mdi:alert-circle-outline", late),
                                     ("heute_faellig", "Planner heute fällig", "mdi:calendar-today", due)):
            put_sensor(key, name, len(lst), icon, [t["title"] for t in lst])
        p1 = [t for t in act if t.get("prio") == 1]
        put_sensor("prio1", "Planner Prio 1 offen", len(p1), "mdi:flag-outline", [t["title"] for t in p1])
    when = remind_time()
    if services() and now.strftime("%H:%M") >= when and ha["last"] != today:
        if due or late:
            notify(reminder_text(due, late), reminder_data(due, late, {t["id"]: t for t in tasks}))
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
        if u.path.endswith("/api/ha-notify"):
            try:
                if not TOKEN:
                    raise RuntimeError("Keine Verbindung zu Home Assistant")
                out = []
                for dom in ha_call("GET", "/services") or []:
                    if dom.get("domain") == "notify":
                        for name in sorted((dom.get("services") or {}).keys()):
                            if name not in ("notify", "send_message", "persistent_notification") and re.fullmatch(r"[A-Za-z0-9_]+", name):
                                out.append(name)
                return self.out(200, {"ok": True, "services": out})
            except Exception as e:
                return self.out(200, {"ok": False, "error": str(e)[:200], "services": []})
        if u.path.endswith("/api/tasks"):
            q = parse_qs(u.query).get("rev", [""])[0]
            with LOCK:
                if q == str(state["rev"]):
                    return self.out(200, {"rev": state["rev"], "version": version(), "ha": ha_info()})
                return self.out(200, {"rev": state["rev"], "version": version(), "tasks": list(state["tasks"].values()), "tags": state["tags"], "ha": ha_info()})
        if u.path.endswith("/manifest.webmanifest"):
            return self.out(200, {"name": "Planner", "short_name": "Planner", "start_url": "./", "scope": "./", "display": "standalone",
                                  "background_color": "#F5F3EB", "theme_color": "#2D6786", "lang": "de",
                                  "icons": [{"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                                            {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]},
                            "application/manifest+json")
        mi = re.search(r"/icons/(icon-192|icon-512|apple-touch-icon)\.png$", u.path)
        if mi:
            try:
                with open(os.path.join(ICONS, mi.group(1) + ".png"), "rb") as f:
                    b = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(b)))
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                self.wfile.write(b)
                return
            except Exception:
                return self.out(404, {"error": "nicht gefunden"})
        m = re.search(r"/api/file/([A-Za-z0-9_-]{1,40})/([a-f0-9]{12})$", u.path)
        if m:
            with LOCK:
                t = state["tasks"].get(m.group(1))
                meta = next((f for f in (t or {}).get("files", []) if f["id"] == m.group(2)), None)
            p = meta and file_path(m.group(1), m.group(2))
            if not p:
                return self.out(404, {"error": "nicht gefunden"})
            ty = meta["ty"] if meta["ty"] in SAFE else "application/octet-stream"
            with open(p, "rb") as f:
                b = f.read()
            self.send_response(200)
            self.send_header("Content-Type", ty)
            self.send_header("Content-Length", str(len(b)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "sandbox")
            self.send_header("Cache-Control", "private, max-age=3600")
            fn = re.sub(r"[^A-Za-z0-9._-]", "_", meta["n"])
            self.send_header("Content-Disposition", ("inline" if ty in SAFE else "attachment") + '; filename="%s"' % fn)
            self.end_headers()
            self.wfile.write(b)
            return
        with open(INDEX, "rb") as f:
            self.out(200, f.read(), "text/html")

    def body(self, limit=2_000_000):
        n = int(self.headers.get("Content-Length", "0"))
        if n > limit:
            raise ValueError
        return json.loads(self.rfile.read(n))

    def csrf_ok(self):
        # Fremde Webseiten können keine eigenen Header ohne Vorabfrage (CORS) senden. So werden
        # Schreibzugriffe aus einem anderen Browser-Tab (CSRF) abgewiesen.
        if self.headers.get("X-Planner") == "1":
            return True
        self.out(403, {"error": "nicht erlaubt"})
        return False

    def do_POST(self):
        if not self.csrf_ok():
            return
        pu = urlparse(self.path)
        path = pu.path
        mf = re.search(r"/api/file/([A-Za-z0-9_-]{1,40})$", path)
        if mf:
            tid = mf.group(1)
            try:
                n = int(self.headers.get("Content-Length", "0"))
                if n <= 0 or n > 20_000_000:
                    raise ValueError
                raw = self.rfile.read(n)
            except Exception:
                return self.out(400, {"error": "Datei zu groß oder leer"})
            q = parse_qs(pu.query)
            name = (q.get("name", ["Datei"])[0] or "Datei")[:120]
            ty = (q.get("type", [""])[0] or "")[:60]
            with LOCK:
                if tid not in state["tasks"]:
                    return self.out(404, {"error": "Aufgabe nicht gefunden"})
            fid = secrets.token_hex(6)
            for base in (FILES, os.path.join(SHARE, "files")):
                try:
                    os.makedirs(os.path.join(base, tid), exist_ok=True)
                    with open(os.path.join(base, tid, fid), "wb") as f:
                        f.write(raw)
                except Exception as e:
                    print("Datei speichern:", e, flush=True)
                    if base == FILES:
                        return self.out(500, {"error": "Speichern nicht möglich"})
            return self.out(200, {"file": {"id": fid, "n": name, "s": len(raw), "ty": ty}})
        try:
            data = self.body(25_000_000 if path.endswith("/api/import") else 2_000_000)
        except Exception:
            return self.out(400, {"error": "ungültige Anfrage"})
        if path.endswith("/api/ha-settings"):
            if not isinstance(data, dict):
                return self.out(400, {"error": "Ungültig"})
            st = app_settings()
            if isinstance(data.get("notify"), list):
                st["notify"] = [str(x)[:80] for x in data["notify"][:12] if re.fullmatch(r"[A-Za-z0-9_]+", str(x))]
            if isinstance(data.get("time"), str) and re.fullmatch(r"([01][0-9]|2[0-3]):[0-5][0-9]", data["time"]):
                st["time"] = data["time"]
            save_app_settings(st)
            return self.out(200, {"ok": True, "ha": ha_info()})
        if path.endswith("/api/ha-test"):
            try:
                if not TOKEN:
                    raise RuntimeError("Keine Verbindung zu Home Assistant")
                notify("Testnachricht vom Planner – die Erinnerungen funktionieren.")
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
            if path.endswith("/api/task") and self.headers.get("X-Check") == "1":
                old = state["tasks"].get(items[0]["id"])
                try:
                    sent = int(data.get("v", -1))
                except (TypeError, ValueError):
                    sent = -1
                if old is not None and sent >= 0 and sent != old.get("v", 0):
                    return self.out(409, {"error": "konflikt", "task": old})
            for t in items:
                t["v"] = state["tasks"].get(t["id"], {}).get("v", 0) + 1
                state["tasks"][t["id"]] = t
            state["rev"] += 1
            save()
            self.out(200, {"rev": state["rev"], "count": len(items), "v": items[0]["v"]})

    def do_DELETE(self):
        if not self.csrf_ok():
            return
        mf = re.search(r"/api/file/([A-Za-z0-9_-]{1,40})/([a-f0-9]{12})$", urlparse(self.path).path)
        if mf:
            drop_files(mf.group(1), mf.group(2))
            return self.out(200, {"ok": True})
        m = re.search(r"/api/task/([A-Za-z0-9_-]{1,40})$", urlparse(self.path).path)
        if not m:
            return self.out(404, {"error": "nicht gefunden"})
        i = m.group(1)
        with LOCK:
            state["tasks"].pop(i, None)
            drop_files(i)
            for t in state["tasks"].values():
                t["deps"] = [d for d in t.get("deps", []) if d != i]
            state["rev"] += 1
            save()
            self.out(200, {"rev": state["rev"]})


if __name__ == "__main__":
    load()
    if state["tasks"]:
        save()  # bestehende Daten beim Start einmal in den Share-Spiegel kopieren
    print("Planner %s läuft auf Port %d, Daten in %s" % (version(), PORT, D), flush=True)
    threading.Thread(target=ha_loop, daemon=True).start()
    if TOKEN:
        threading.Thread(target=ws_loop, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
