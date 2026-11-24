import base64, datetime, hashlib, ipaddress, json, os, re, secrets, shutil, socket, struct, threading, time, traceback, urllib.error, urllib.request
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
VENDOR = os.environ.get("VENDOR_DIR", os.path.join(os.path.dirname(INDEX), "vendor"))  # Bibliotheken und Schriften (tools/vendor.py)
STATIC_TYPES = {"png": "image/png", "js": "text/javascript; charset=utf-8", "css": "text/css; charset=utf-8", "woff2": "font/woff2"}
FID = re.compile(r"[a-f0-9]{12}")
SAFE = ("image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf")
LOCK = threading.RLock()  # wiedereintrittsfähig: ha_info() fragt Personen ab, auch wenn ein Handler die Sperre hält
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


def as_list(x):
    return x if isinstance(x, list) else []


def real_date(x):
    # Format JJJJ-MM-TT und ein echtes Kalenderdatum (kein 2026-13-45)
    if not DATE.fullmatch(x):
        return False
    try:
        datetime.date.fromisoformat(x)
        return True
    except ValueError:
        return False


def clean(t):
    if not isinstance(t, dict):
        return None
    i = str(t.get("id", ""))
    s, e = str(t.get("start", "")), str(t.get("end", ""))
    if not ID.fullmatch(i) or not real_date(s) or not real_date(e):
        return None
    if e < s:
        e = s
    title = str(t.get("title", "")).strip()[:200]
    if not title:
        return None
    st = t.get("status")
    deps = [str(x) for x in as_list(t.get("deps")) if isinstance(x, str) and ID.fullmatch(x) and x != i][:50]
    ck = [{"t": str(c.get("t", ""))[:200], "d": bool(c.get("d"))}
          for c in as_list(t.get("checklist")) if isinstance(c, dict)][:100]
    tags = t.get("tags")
    if not isinstance(tags, list):
        tags = [t.get("area")] if t.get("area") else []
    tags = [n for n in dict.fromkeys(str(x).strip()[:30] for x in tags if isinstance(x, str)) if n][:20]
    return {"id": i, "title": title, "area": (tags[0] if tags else str(t.get("area", ""))[:60]), "tags": tags, "proj": str(t.get("proj", "") or "")[:30], "ms": bool(t.get("ms")), "rec": clean_rec(t.get("rec")), "spawned": str(t.get("spawned", "") or "")[:40], "who": str(t.get("who", "") or "")[:200],
            "status": st if st in ("todo", "doing", "done") else "todo", "prio": (t.get("prio") if t.get("prio") in (1, 2, 3) else 0), "start": s, "end": e,
            "notes": str(t.get("notes", ""))[:4000], "deps": deps, "checklist": ck,
            "arch": bool(t.get("arch")), "del": bool(t.get("del")), "delAt": str(t.get("delAt", "") or "")[:10],
            "log": clean_log(t.get("log")), "files": clean_files(t.get("files")), "v": 0}


# ---- Home Assistant: Erinnerungen und Sensoren (nur im Add-on, über die Supervisor-Schnittstelle)
LOGGED = set()


def log_once(key, msg):
    """Meldung nur einmal je Serverlauf ins Add-on-Protokoll (verhindert Flut bei Fehlern, die bei jeder Abfrage auftreten)."""
    if key not in LOGGED:
        LOGGED.add(key)
        print(msg, flush=True)


def read_json(path, what):
    """JSON-Objekt lesen. Fehlt die Datei: {}. Ist sie defekt: {} und eine Meldung im Protokoll statt still zu schweigen."""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except FileNotFoundError:
        return {}
    except Exception as e:
        log_once("read:" + path, "%s nicht lesbar (%s): %s" % (what, os.path.basename(path), e))
        return {}


def options():
    return read_json(OPTS, "Add-on-Konfiguration")


def app_settings():
    return read_json(SETTINGS, "Einstellungen aus der App")


def save_app_settings(d):
    tmp = SETTINGS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    try:
        os.chmod(tmp, 0o600)  # enthält ggf. den KI-Schlüssel
    except OSError:
        pass  # Dateisystem ohne Rechteverwaltung: Datei liegt trotzdem nur im Add-on-Ordner
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


def notify_who():
    """Welche Person zu welchem Gerät gehört. Ohne Angabe: aus dem Gerätenamen erraten (z. B. iphone_von_lasse → Lasse)."""
    st = app_settings()
    m = st.get("notify_who") if isinstance(st.get("notify_who"), dict) else {}
    with LOCK:
        people = known_people(list(state["tasks"].values()))
    out = {}
    for sv in services():
        v = m.get(sv)
        if v is None:
            v = next((p for p in people if p.lower() in sv.lower()), "")
        out[sv] = str(v)[:30]
    return out


def ha_info():
    o = options()
    return {"api": bool(TOKEN), "notify": services(), "nwho": notify_who(), "time": remind_time(),
            "sensors": bool(o.get("sensors", True)),
            "ai": bool(ai_key()), "model": ai_model(), "aiapp": bool(app_settings().get("ai_key")),
            "aicfg": bool(str(o.get("gemini_api_key") or "").strip()), "aiuse": ai_usage_info(),
            "alexa": bool(app_settings().get("alexa")), "echos": ALEXA["n"], "wsok": wsok["ok"]}


AI_MODELS = ("gemini-flash-lite-latest", "gemini-flash-latest")
AI_KEY = re.compile(r"[A-Za-z0-9._\-]{20,200}")  # altes Format AIza…, neues Format AQ.…


def ai_key():
    k = str(app_settings().get("ai_key") or "").strip()
    return k or str(options().get("gemini_api_key") or "").strip()


def ai_model():
    m = app_settings().get("ai_model")
    if m in AI_MODELS:
        return m
    m = str(options().get("ai_model") or "")
    return m if m in AI_MODELS else AI_MODELS[0]


GEMINI = os.environ.get("GEMINI_URL", "https://generativelanguage.googleapis.com/v1beta/models")
AI_SYSTEM = "Du bist ein sachkundiger Helfer für Heim- und Gartenprojekte. Antworte immer auf Deutsch und genau im verlangten JSON-Format."
AI_CALLS = []


AI_DAY = {"gemini-flash-lite-latest": 100, "gemini-flash-latest": 15}  # deutlich unter Googles Gratis-Kontingent
AI_USAGE = os.path.join(D, "ai_usage.json")
AI_LOCK = threading.Lock()


def ai_today():
    now = datetime.datetime.now(ha["tz"]) if ha["tz"] else datetime.datetime.now()
    return now.strftime("%Y-%m-%d")


def ai_usage():
    try:
        with open(AI_USAGE, encoding="utf-8") as f:
            u = json.load(f)
    except Exception:
        u = {}
    if u.get("day") != ai_today():
        u = {"day": ai_today(), "n": 0, "blocked": False}
    return u


def ai_usage_info():
    u = ai_usage()
    return {"used": u.get("n", 0), "limit": AI_DAY.get(ai_model(), 15), "blocked": bool(u.get("blocked"))}


def ai_limit():
    # Schutz vor Kosten und gesperrtem Gratis-Kontingent: max. 20 pro Stunde und ein Tageslimit je Modell.
    # Meldet Google „Limit erreicht“ (429), ruht die KI bis zum nächsten Tag.
    with AI_LOCK:
        now = time.time()
        AI_CALLS[:] = [x for x in AI_CALLS if now - x < 3600]
        u = ai_usage()
        if u.get("blocked"):
            raise RuntimeError("Google meldet das Tageslimit. Die KI ruht bis morgen.")
        if u["n"] >= AI_DAY.get(ai_model(), 15):
            raise RuntimeError("Tageslimit des Planners erreicht (%d Anfragen). Morgen geht es weiter." % u["n"])
        if len(AI_CALLS) >= 20:
            raise RuntimeError("Zu viele KI-Anfragen in einer Stunde, bitte später erneut versuchen")
        AI_CALLS.append(now)
        u["n"] += 1
        ai_usage_save(u)


def ai_usage_save(u):
    try:
        tmp = AI_USAGE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(u, f)
        os.replace(tmp, AI_USAGE)
    except Exception as e:
        print("KI-Zähler nicht gespeichert:", e, flush=True)


def ai_call(prompt, raw=False):
    ai_limit()
    key = ai_key()
    if not key:
        raise RuntimeError("Kein Gemini-Schlüssel eingetragen")
    model = ai_model()
    body = {"system_instruction": {"parts": [{"text": AI_SYSTEM}]},
            "contents": [{"role": "user", "parts": [{"text": prompt[:4000]}]}],
            "generationConfig": {"maxOutputTokens": 2000, "responseMimeType": "application/json"}}
    req = urllib.request.Request("%s/%s:generateContent" % (GEMINI, model), method="POST", data=json.dumps(body).encode(),
                                 headers={"x-goog-api-key": key, "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            j = json.load(r)
    except urllib.error.HTTPError as e:
        try:
            msg = json.load(e).get("error", {}).get("message", "")
        except Exception:
            msg = ""
        if e.code == 429:
            with AI_LOCK:
                u = ai_usage()
                u["blocked"] = True
                ai_usage_save(u)
            raise RuntimeError("Google meldet das Limit. Die KI ruht bis morgen.")
        if e.code in (400, 401, 403) and "key" in msg.lower():
            raise RuntimeError("Der Gemini-Schlüssel wird nicht akzeptiert")
        raise RuntimeError("Gemini %s %s" % (e.code, msg[:120]))
    text = ""
    for c in (j.get("candidates") or [])[:1]:
        text = "".join(x.get("text", "") for x in (c.get("content") or {}).get("parts", []) if isinstance(x, dict))
    a, z = text.find("{"), text.rfind("}")
    if a < 0 or z < a:
        raise RuntimeError("Unerwartete Antwort")
    d = json.loads(text[a:z + 1])
    if raw:  # freie Zuordnungen (z. B. Tag -> Symbol), nur kurze Texte
        return {str(k)[:60]: str(v)[:40] for k, v in list(d.items())[:100]}
    items = [str(x).strip()[:120] for x in d.get("checklist", []) if str(x).strip()] if isinstance(d.get("checklist"), list) else []
    return {"notes": str(d.get("notes", "")).strip()[:1000], "checklist": items[:10]}


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
            cfg = ha_call("GET", "/config") or {}
            name = cfg.get("time_zone")
            for k in ("internal_url", "external_url"):
                hn = urlparse(str(cfg.get(k) or "")).hostname
                if hn:
                    TRUSTED_HOSTS.add(hn.lower())
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


def notify(message, data=None, only=None):
    sv = [only] if only else services()
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


def complete_task(tid, actor="iPhone"):
    with LOCK:
        t = state["tasks"].get(tid)
        if not t or t.get("del") or t.get("status") == "done" or not can_complete(t, state["tasks"]):
            return None
        n = dict(t)
        n["status"] = "done"
        n["log"] = (t.get("log") or []) + [{"t": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"), "a": actor, "k": "h", "x": "Status: Erledigt (Mitteilung)"}]
        n["log"] = n["log"][-120:]
        n["v"] = t.get("v", 0) + 1
        state["tasks"][tid] = n
        state["rev"] += 1
        save()
        return n["title"]


def _for_person(lst, who):
    # Erinnerung je Person: eigene Aufgaben und solche ohne Zuständigkeit
    return [t for t in lst if not who or not str(t.get("who", "")).strip() or _mine(t, who)]


def remind_all(quiet=False, clear=False):
    now = datetime.datetime.now(ha["tz"]) if ha["tz"] else datetime.datetime.now()
    with LOCK:
        tasks = dict(state["tasks"])
    act, due, late, doing = stats(list(tasks.values()), now.strftime("%Y-%m-%d"))
    for sv, who in notify_who().items():
        d, l = _for_person(due, who), _for_person(late, who)
        if d or l:
            notify(reminder_text(d, l), reminder_data(d, l, tasks, quiet=quiet), only=sv)
        elif clear:
            ha_call("POST", "/services/notify/" + sv, {"message": "clear_notification", "data": {"tag": NTAG}})


def refresh_notification():
    remind_all(quiet=True, clear=True)


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


# ---- Vorlesen und Abhaken per Stimme (Siri, Alexa)
def _today():
    now = datetime.datetime.now(ha["tz"]) if ha["tz"] else datetime.datetime.now()
    return now.date()


def _mine(t, who):
    return not who or who.lower() in [p.strip().lower() for p in str(t.get("who", "")).split(",")]


def _names(lst):
    n = ["„%s“" % t["title"] for t in lst[:5]]
    more = len(lst) - 5
    if more > 0:
        n.append("%d weitere" % more)
    return n[0] if len(n) == 1 else ", ".join(n[:-1]) + " und " + n[-1]


def speech_summary(when="heute", who=""):
    today = _today()
    ti = today.isoformat()
    with LOCK:
        act = [t for t in state["tasks"].values() if not t.get("del") and not t.get("arch") and t["status"] != "done" and _mine(t, who)]
    late = sorted([t for t in act if t["end"] < ti], key=lambda t: t["end"])
    if when == "woche":
        lim = (today + datetime.timedelta(7)).isoformat()
        lst = late + sorted([t for t in act if t["end"] >= ti and t["start"] <= lim], key=lambda t: t["end"])
        head = "In den nächsten sieben Tagen"
    else:
        lst = late + sorted([t for t in act if t["end"] >= ti and t["start"] <= ti], key=lambda t: t["end"])
        head = "Heute"
    who_txt = " für %s" % who if who else ""
    if not lst:
        return "%s steht%s nichts an." % (head, who_txt)
    s = "%s %s%s %d %s an: %s." % (head, "steht" if len(lst) == 1 else "stehen", who_txt, len(lst), "Aufgabe" if len(lst) == 1 else "Aufgaben", _names(lst))
    if late:
        s += " %s davon %s überfällig." % ("Eine" if len(late) == 1 else str(len(late)), "ist" if len(late) == 1 else "sind")
    return s


def _norm(x):
    return re.sub(r"[^a-zäöüß0-9 ]", "", str(x).lower()).strip()


def done_by_voice(text, actor="Sprache"):
    import difflib
    q = _norm(text)
    if not q:
        return "Welche Aufgabe soll ich abhaken?"
    with LOCK:
        cand = [t for t in state["tasks"].values() if not t.get("del") and not t.get("arch") and t["status"] != "done"]
    best, score = None, 0.0
    for t in cand:
        ti = _norm(t["title"])
        sc = 1.0 if ti == q else 0.9 if (q in ti or ti in q) else difflib.SequenceMatcher(None, q, ti).ratio()
        if sc > score:
            best, score = t, sc
    if not best or score < 0.6:
        return "Ich habe keine passende offene Aufgabe gefunden."
    if not complete_task(best["id"], actor):
        return "„%s“ kann ich per Sprache nicht abhaken, sie wiederholt sich oder wartet auf eine andere Aufgabe." % best["title"]
    return "„%s“ ist erledigt." % best["title"]


ALEXA_PREFIX = re.compile(r"^(?:alexa[, ]+)?(?:planner|planer|plana|planna|plan a|neue aufgabe|aufgabe)\b[ ,:]*(.*)$")


def alexa_command(text, person=""):
    """Wertet einen Echo-Sprachbefehl aus. Gibt die Antwort zurück oder None, wenn er nicht dem Planner gilt."""
    orig = str(text or "").strip()
    m = ALEXA_PREFIX.match(orig.lower())
    if not m:
        return None
    return voice_rest(orig[m.start(1):], person, "Alexa")


def voice_rest(rest, person="", actor="Sprache"):
    rest = str(rest or "").strip(" .?!")
    low = rest.lower()
    with LOCK:
        people = known_people(list(state["tasks"].values()))
    who = next((p for p in people if person and p.lower() == person.strip().lower()), "")
    rest, full = low, rest
    if rest in ("", "heute", "was steht heute an", "was steht an", "was ist heute dran", "was ist heute zu tun", "was habe ich heute"):
        return speech_summary("heute", who)
    if re.fullmatch(r"(?:diese |die )?woche|was steht diese woche an", rest):
        return speech_summary("woche", who)
    m2 = re.fullmatch(r"(?:erledigt|fertig|abhaken|hake ab|hak ab)\s+(.+)", rest) or re.fullmatch(r"(.+?)\s+(?:ist\s+)?(?:erledigt|fertig)", rest)
    if m2:
        return done_by_voice(m2.group(1), actor)
    t, speech = quick_task(full, who)
    with LOCK:
        t["v"] = 1
        state["tasks"][t["id"]] = t
        state["rev"] += 1
        save()
    return speech


def ha_template(tpl):
    req = urllib.request.Request(SUP + "/template", method="POST", data=json.dumps({"template": tpl}).encode(),
                                 headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode("utf-8", "replace")


ALEXA = {"seen": {}, "speak": {}, "n": 0, "sock": None}


def alexa_entities():
    try:
        return [e for e in json.loads(ha_template("{{ integration_entities('alexa_devices') | select('match', 'event\\\\.') | list | to_json }}")) if isinstance(e, str)]
    except Exception as e:
        print("Alexa-Geräte nicht lesbar:", e, flush=True)
        return []


def alexa_speak(entity, text):
    try:
        sp = ALEXA["speak"].get(entity)
        if sp is None:
            sp = ha_template("{{ device_entities(device_id('%s')) | select('match', 'notify\\\\..*_speak$') | first | default('') }}" % entity).strip()
            ALEXA["speak"][entity] = sp
        if sp:
            ha_call("POST", "/services/notify/send_message", {"entity_id": sp, "message": text[:600]})
    except Exception as e:
        print("Alexa-Antwort fehlgeschlagen:", e, flush=True)


def alexa_event(entity, st):
    if not isinstance(st, dict):
        return
    stamp = st.get("state")
    if not stamp or ALEXA["seen"].get(entity) == stamp:
        return
    first = entity not in ALEXA["seen"]
    ALEXA["seen"][entity] = stamp
    if first and st.get("_initial"):
        return
    a = st.get("attributes") or {}
    try:
        answer = alexa_command(a.get("voice_command", ""), a.get("person_first_name") or "")
    except Exception as e:
        answer = "Das habe ich nicht verstanden."
        print("Alexa-Befehl:", e, flush=True)
    if answer:
        alexa_speak(entity, answer)



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
        ents = alexa_entities() if app_settings().get("alexa") else []
        ALEXA["n"] = len(ents)
        if ents:
            ws_send(sock, json.dumps({"id": 2, "type": "subscribe_trigger", "trigger": {"platform": "state", "entity_id": ents}}))
            print("Alexa-Sprachbefehle aktiv für %d Echo-Geräte" % len(ents), flush=True)
        ALEXA["sock"] = sock
        wsok["ok"] = True
        started = time.time()
        while True:
            try:
                msg = json.loads(ws_recv(sock))
            except socket.timeout:
                if time.time() - started > 1800:
                    raise ConnectionError("Neuaufbau, um neue Geräte zu erkennen")
                ws_send(sock, b"", 9)
                continue
            if msg.get("type") != "event":
                continue
            if msg.get("id") == 2:
                tr = ((msg.get("event") or {}).get("variables") or {}).get("trigger") or {}
                ent, st = tr.get("entity_id"), tr.get("to_state")
                if ent:
                    threading.Thread(target=alexa_event, args=(ent, st), daemon=True).start()
                continue
            handle_action(str(((msg.get("event") or {}).get("data") or {}).get("action", "")))
    finally:
        ALEXA["sock"] = None
        try:
            sock.close()
        except Exception:
            pass


def ws_restart():
    s_ = ALEXA.get("sock")
    if s_:
        try:
            s_.close()
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
        remind_all()
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



# ---- Schnelleingabe (gleiche Regeln wie im Browser, siehe parseQuick in src/js/20-schnelleingabe.js)
# Getippt: „Zaun streichen Sa #Garten +Haus !1 @Melanie“ · gesprochen: „Zaun streichen am Samstag Tag Garten Priorität eins“
QWD = (("mo", "montag"), ("di", "dienstag"), ("mi", "mittwoch"), ("do", "donnerstag"), ("fr", "freitag"), ("sa", "samstag"), ("so", "sonntag"))
WDS = ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So")
MON = ("januar", "februar", "märz", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "dezember")
NUMW = {"ein": 1, "eine": 1, "einen": 1, "einem": 1, "eins": 1, "zwei": 2, "drei": 3, "vier": 4, "fünf": 5, "sechs": 6, "sieben": 7,
        "acht": 8, "neun": 9, "zehn": 10, "elf": 11, "zwölf": 12, "vierzehn": 14}
_ORD = ["erst", "zweit", "dritt", "viert", "fünft", "sechst", "siebt", "acht", "neunt", "zehnt", "elft", "zwölft", "dreizehnt", "vierzehnt",
        "fünfzehnt", "sechzehnt", "siebzehnt", "achtzehnt", "neunzehnt", "zwanzigst"]
_ORD += [p + "undzwanzigst" for p in ("ein", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun")] + ["dreißigst", "einunddreißigst"]
ORDW = {stem + end: n + 1 for n, stem in enumerate(_ORD) for end in ("e", "en", "er", "es", "em")}
ORDW["siebente"] = ORDW["siebenten"] = 7


def _qn(x):
    return re.sub(r"[.,;:!?]+$", "", str(x or "")).lower()


def _qname(x, names):
    x = re.sub(r"[.,;:!?]+$", "", x.replace("_", " ")).strip()
    lo = x.lower()
    for n in names:
        if n.lower() == lo:
            return n
    pre = [n for n in names if n.lower().startswith(lo)]
    if len(pre) == 1:
        return pre[0]
    return x[:1].upper() + x[1:]


def _qknown(x, names):
    # gesprochenes „Tag Garten“ / „Projekt Haus“: nur bekannte Namen (mind. 3 Buchstaben), sonst gehört das Wort zum Titel
    lo = _qn(x)
    if len(lo) < 3:
        return None
    for n in names:
        if n.lower() == lo:
            return n
    pre = [n for n in names if n.lower().startswith(lo)]
    return pre[0] if len(pre) == 1 else None


def _qnum(x):
    x = _qn(x)
    return int(x) if re.fullmatch(r"\d{1,3}", x) else NUMW.get(x)


def _qday(d, mo, y, today, explicit):
    try:
        r = datetime.date(y, mo, d)
    except ValueError:
        return None
    if not explicit and r < today:
        try:
            r = datetime.date(y + 1, mo, d)
        except ValueError:
            pass
    return r


def _qdate_at(w, i, today):
    td = datetime.timedelta
    x, raw = _qn(w[i]), re.sub(r"[,;:!?]+$", "", w[i])
    nx = _qn(w[i + 1]) if i + 1 < len(w) else ""
    if x in ("am", "zum", "ab") and i + 1 < len(w):
        r = _qdate_at(w, i + 1, today)
        return (r[0], r[1] + 1) if r else None
    if x == "heute":
        return today, 1
    if x == "morgen":
        return today + td(1), 1
    if x in ("übermorgen", "uebermorgen"):
        return today + td(2), 1
    if x == "wochenende":
        return today + td((5 - today.weekday()) % 7), 1
    if x in ("nächste", "naechste", "nächsten", "kommende", "kommenden") and nx == "woche":
        return today + td(7 - today.weekday()), 2
    if x == "in" and i + 2 < len(w) and _qnum(w[i + 1]) is not None:
        k, u = _qnum(w[i + 1]), _qn(w[i + 2])
        if u in ("tag", "tagen"):
            return today + td(k), 3
        if u in ("woche", "wochen"):
            return today + td(7 * k), 3
    for idx, (a, b) in enumerate(QWD):
        if x == b or raw.rstrip(".") == a.capitalize():
            return today + td((idx - today.weekday()) % 7), 1
    m = re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{2}|\d{4})?", raw)
    if m:
        y = int(m.group(3)) if m.group(3) else today.year
        r = _qday(int(m.group(1)), int(m.group(2)), y + 2000 if y < 100 else y, today, bool(m.group(3)))
        return (r, 1) if r else None
    d = int(raw[:-1]) if re.fullmatch(r"\d{1,2}\.", raw) else ORDW.get(x)
    if d and nx in MON:
        r = _qday(d, MON.index(nx) + 1, today.year, today, False)
        return (r, 2) if r else None
    return None


def parse_quick(text, today, tags, projs, people):
    w = str(text or "").split()
    o = {"tags": [], "who": [], "proj": "", "prio": 0, "date": None, "until": False}
    keep = []
    i = 0
    while i < len(w):
        x = w[i]
        lo = _qn(x)
        nx = w[i + 1] if i + 1 < len(w) else ""
        m = re.fullmatch(r"(?:!|[pP])([1-3])", x)
        if x.startswith("#") and len(x) > 1:
            n = _qname(x[1:], tags)
            if n and n not in o["tags"]:
                o["tags"].append(n[:30])
        elif x.startswith("+") and len(x) > 1:
            o["proj"] = _qname(x[1:], projs)[:30]
        elif x.startswith("@") and len(x) > 1:
            n = _qname(x[1:], people)
            if n and n not in o["who"]:
                o["who"].append(n[:30])
        elif m:
            o["prio"] = int(m.group(1))
        elif re.fullmatch(r"!{1,3}", x):
            o["prio"] = 4 - len(x)
        elif keep and lo in ("priorität", "prio") and _qnum(nx) in (1, 2, 3):
            o["prio"] = _qnum(nx)
            i += 2
            continue
        elif keep and lo in ("tag", "hashtag") and nx and _qknown(nx, tags):
            n = _qknown(nx, tags)
            if n not in o["tags"]:
                o["tags"].append(n)
            i += 2
            continue
        elif keep and lo == "projekt" and nx and _qknown(nx, projs):
            o["proj"] = _qknown(nx, projs)
            i += 2
            continue
        else:
            r = None
            if keep:
                if lo == "bis" and i + 1 < len(w):
                    r = _qdate_at(w, i + 1, today)
                    if r:
                        o["date"], o["until"] = r[0], True
                        i += r[1] + 1
                        continue
                r = _qdate_at(w, i, today)
            if r:
                o["date"], o["until"] = r[0], False
                i += r[1]
                continue
            keep.append(x)
        i += 1
    o["title"] = " ".join(keep)[:200]
    return o


def known_people(tl):
    return list(dict.fromkeys(["Lasse", "Melanie"] + sorted({p.strip() for t in tl for p in str(t.get("who", "")).split(",") if p.strip()})))


def quick_task(text, who_default=""):
    now = datetime.datetime.now(ha["tz"]) if ha["tz"] else datetime.datetime.now()
    today = now.date()
    with LOCK:
        tl = list(state["tasks"].values())
        tags = [x["n"] for x in state["tags"] if not x.get("p")] + sorted({n for t in tl for n in t.get("tags", [])})
        projs = [x["n"] for x in state["tags"] if x.get("p")] + sorted({t.get("proj") for t in tl if t.get("proj")})
    tags, projs = list(dict.fromkeys(tags)), list(dict.fromkeys(projs))
    people = known_people(tl)
    q = parse_quick(text, today, tags, projs, list(dict.fromkeys(people)))
    if not q["title"]:
        raise ValueError("Kein Titel erkannt")
    q["title"] = q["title"][:1].upper() + q["title"][1:]  # Sprachdiktat liefert oft alles klein
    d = q["date"]
    if d is None:
        s = e = today
    elif q["until"]:
        s, e = min(today, d), d
    else:
        s = e = d
    who = q["who"] or ([who_default] if who_default else [])
    t = clean({"id": "q" + secrets.token_hex(5), "title": q["title"], "tags": q["tags"], "proj": q["proj"], "who": ", ".join(who),
               "status": "todo", "prio": q["prio"], "start": s.isoformat(), "end": e.isoformat()})
    when = "heute" if e == today else "morgen" if e == today + datetime.timedelta(1) else "%s, %s" % (WDS[e.weekday()], e.strftime("%d.%m."))
    speech = "„%s“ ist %s %s eingetragen." % (t["title"], "bis" if q["until"] else "für", when)
    return t, speech

BROWSER_LOG = []  # Zeitpunkte der letzten Browser-Fehlermeldungen (Begrenzung)
LOG_LOCK = threading.Lock()
PREFS = os.path.join(D, "prefs.json")  # persönliche Einstellungen je Home-Assistant-Benutzer
PREFS_LOCK = threading.Lock()
PREF_KEYS = ("theme", "design", "font", "me", "sort", "glw", "hwho", "htile")


def prefs_all():
    return read_json(PREFS, "Persönliche Einstellungen")


def prefs_save(d):
    tmp = PREFS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    os.replace(tmp, PREFS)


INGRESS_IP = "172.30.32.2"  # Home-Assistant-Ingress (Supervisor)
LOCAL_SUFFIX = (".local", ".lan", ".home", ".home.arpa", ".internal", ".localdomain", ".fritz.box", ".box", ".intranet", ".localhost")
TRUSTED_HOSTS = set()  # Adressen aus der Home-Assistant-Konfiguration (interne/externe URL)


def host_ok(client_ip, host_header):
    # Schutz gegen DNS-Rebinding: Eine fremde Webseite, deren Name plötzlich auf das Heimnetz zeigt,
    # schickt ihren eigenen Namen im Host-Header. Erlaubt sind Ingress, IP-Adressen und Namen aus dem Heimnetz.
    if client_ip == INGRESS_IP:
        return True
    h = (host_header or "").strip().lower()
    if h.startswith("["):
        h = h[1:h.find("]")] if "]" in h else ""
    elif h.count(":") == 1:
        h = h.rsplit(":", 1)[0]
    if not h:
        return False
    try:
        ipaddress.ip_address(h)
        return True
    except ValueError:
        pass
    return h == "localhost" or "." not in h or h.endswith(LOCAL_SUFFIX) or h in TRUSTED_HOSTS


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def ha_user(self):
        # Angemeldeter Home-Assistant-Benutzer. Nur über Ingress vertrauenswürdig (Port 8099 könnte die Kopfzeilen fälschen).
        if self.client_address[0] != INGRESS_IP and not os.environ.get("TRUST_USER_HEADERS"):
            return None
        uid = (self.headers.get("X-Remote-User-Id") or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{4,64}", uid):
            return None
        name = (self.headers.get("X-Remote-User-Display-Name") or self.headers.get("X-Remote-User-Name") or "").strip()[:40]
        return {"id": uid, "name": name}

    def guard(self):
        if host_ok(self.client_address[0], self.headers.get("Host")):
            return True
        self.out(403, {"error": "Zugriff über diese Adresse ist nicht erlaubt"})
        return False

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def out(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if not self.guard():
            return
        try:
            self.get(urlparse(self.path))
        except Exception:
            self.fail("GET", urlparse(self.path).path)

    def get(self, u):
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
        if u.path.endswith("/api/me"):
            usr = self.ha_user()
            if not usr:
                return self.out(200, {"user": None})
            with PREFS_LOCK:
                pr = prefs_all().get(usr["id"]) or {}
            return self.out(200, {"user": usr["name"], "prefs": pr})
        if u.path.endswith("/api/speech"):
            qs = parse_qs(u.query)
            when = "woche" if (qs.get("when") or [""])[0] == "woche" else "heute"
            return self.out(200, {"speech": speech_summary(when, (qs.get("who") or [""])[0][:30])})
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
            return self.static(os.path.join(ICONS, mi.group(1) + ".png"))
        mv = re.search(r"/vendor/([a-z0-9][a-z0-9.-]{0,60}\.(?:js|css|woff2))$", u.path)
        if mv and ".." not in mv.group(1):
            return self.static(os.path.join(VENDOR, mv.group(1)), 604800)
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
            self.send_header("Content-Security-Policy", "sandbox")
            self.send_header("Cache-Control", "private, max-age=3600")
            fn = re.sub(r"[^A-Za-z0-9._-]", "_", meta["n"])
            self.send_header("Content-Disposition", ("inline" if ty in SAFE else "attachment") + '; filename="%s"' % fn)
            self.end_headers()
            self.wfile.write(b)
            return
        with open(INDEX, "rb") as f:
            self.out(200, f.read(), "text/html")

    def static(self, path, max_age=86400):
        """Feste Datei aus dem Add-on ausliefern (Symbole, Bibliotheken, Schriften)."""
        try:
            with open(path, "rb") as f:
                b = f.read()
        except OSError:
            return self.out(404, {"error": "nicht gefunden"})
        self.send_response(200)
        self.send_header("Content-Type", STATIC_TYPES.get(path.rsplit(".", 1)[-1], "application/octet-stream"))
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "public, max-age=%d" % max_age)
        self.end_headers()
        self.wfile.write(b)

    def body(self, limit=2_000_000):
        n = int(self.headers.get("Content-Length", "0"))
        if n < 0 or n > limit:
            raise ValueError
        return json.loads(self.rfile.read(n))

    def csrf_ok(self):
        # Fremde Webseiten können keine eigenen Header ohne Vorabfrage (CORS) senden. So werden
        # Schreibzugriffe aus einem anderen Browser-Tab (CSRF) abgewiesen.
        if self.headers.get("X-Planner") == "1":
            return True
        self.out(403, {"error": "nicht erlaubt"})
        return False

    # POST-Routen: Pfadende → (Methode, größte erlaubte Anfrage in Bytes). Reihenfolge egal, Pfade enden eindeutig.
    POST_ROUTES = {"/api/ai": ("post_ai", 200_000), "/api/me": ("post_me", 20_000), "/api/voice": ("post_voice", 20_000),
                   "/api/quick": ("post_quick", 20_000), "/api/ha-settings": ("post_ha_settings", 50_000),
                   "/api/ha-test": ("post_ha_test", 1_000), "/api/tags": ("post_tags", 200_000), "/api/task": ("post_task", 2_000_000),
                   "/api/import": ("post_import", 25_000_000), "/api/log": ("post_log", 8_000)}

    def do_POST(self):
        if not self.guard() or not self.csrf_ok():
            return
        pu = urlparse(self.path)
        try:
            mf = re.search(r"/api/file/([A-Za-z0-9_-]{1,40})$", pu.path)
            if mf:
                return self.post_file(mf.group(1), parse_qs(pu.query))
            route = next((r for suffix, r in self.POST_ROUTES.items() if pu.path.endswith(suffix)), None)
            if not route:
                return self.out(404, {"error": "nicht gefunden"})
            try:
                data = self.body(route[1])
            except Exception:
                return self.out(400, {"error": "ungültige Anfrage"})
            return getattr(self, route[0])(data)
        except Exception:
            self.fail("POST", pu.path)

    def fail(self, method, path):
        """Unerwarteter Fehler: mit Kontext ins Add-on-Protokoll, Browser bekommt 500 statt abgebrochener Verbindung."""
        print("Fehler bei %s %s:\n%s" % (method, path, traceback.format_exc(limit=6)), flush=True)
        try:
            self.out(500, {"error": "Interner Fehler, Details im Add-on-Protokoll"})
        except Exception:
            pass  # Verbindung schon zu

    def post_file(self, tid, q):
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n <= 0 or n > 20_000_000:
                raise ValueError
            raw = self.rfile.read(n)
        except Exception:
            return self.out(400, {"error": "Datei zu groß oder leer"})
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

    def post_ai(self, data):
        try:
            p = data.get("prompt") if isinstance(data, dict) else None
            if not isinstance(p, str) or not p.strip():
                raise RuntimeError("Leere Anfrage")
            return self.out(200, {"ok": True, "data": ai_call(p, bool(data.get("raw")))})
        except Exception as e:
            return self.out(200, {"ok": False, "error": str(e)[:200]})

    def post_me(self, data):
        usr = self.ha_user()
        if not usr:
            return self.out(200, {"ok": False})
        if not isinstance(data, dict):
            return self.out(400, {"error": "Ungültig"})
        with PREFS_LOCK:
            allp = prefs_all()
            mine = allp.get(usr["id"]) if isinstance(allp.get(usr["id"]), dict) else {}
            for k, v in data.items():
                if k in PREF_KEYS and (v is None or isinstance(v, str)):
                    if v is None or v == "":
                        mine.pop(k, None)
                    else:
                        mine[k] = v[:60]
            allp[usr["id"]] = mine
            prefs_save(allp)
        return self.out(200, {"ok": True})

    def post_voice(self, data):
        # Wie /api/quick, versteht zusätzlich „heute“, „Woche“ und „erledigt …“ (für Siri-Kurzbefehle)
        try:
            txt = data.get("text") if isinstance(data, dict) else None
            if not isinstance(txt, str) or not txt.strip():
                raise ValueError("Leerer Text")
            return self.out(200, {"ok": True, "speech": voice_rest(txt[:300], str(data.get("who") or "")[:30], "Siri")})
        except Exception as e:
            return self.out(400, {"ok": False, "error": str(e)[:200], "speech": "Das habe ich nicht verstanden."})

    def post_quick(self, data):
        # Für Siri-Kurzbefehle und Home-Assistant-Sprachsteuerung: {"text": "Zaun streichen Sa #Garten", "who": "Lasse"}
        try:
            txt = data.get("text") if isinstance(data, dict) else None
            if not isinstance(txt, str) or not txt.strip():
                raise ValueError("Leerer Text")
            t, speech = quick_task(txt[:300], str(data.get("who") or "")[:30])
        except Exception as e:
            return self.out(400, {"ok": False, "error": str(e)[:200], "speech": "Das habe ich nicht verstanden."})
        with LOCK:
            t["v"] = 1
            state["tasks"][t["id"]] = t
            state["rev"] += 1
            save()
        return self.out(200, {"ok": True, "task": t, "speech": speech})

    def post_ha_settings(self, data):
        if not isinstance(data, dict):
            return self.out(400, {"error": "Ungültig"})
        st = app_settings()
        if isinstance(data.get("notify"), list):
            st["notify"] = [str(x)[:80] for x in data["notify"][:12] if re.fullmatch(r"[A-Za-z0-9_]+", str(x))]
        if isinstance(data.get("time"), str) and re.fullmatch(r"([01][0-9]|2[0-3]):[0-5][0-9]", data["time"]):
            st["time"] = data["time"]
        if isinstance(data.get("ai_key"), str):
            k = re.sub(r"\s+", "", data["ai_key"]).strip("\"'„“”")
            if not k:
                st.pop("ai_key", None)
            elif AI_KEY.fullmatch(k):
                st["ai_key"] = k
            else:
                return self.out(400, {"error": "Das sieht nicht wie ein Gemini-Schlüssel aus"})
        if data.get("ai_model") in AI_MODELS:
            st["ai_model"] = data["ai_model"]
        if isinstance(data.get("notify_who"), dict):
            m = st.get("notify_who") if isinstance(st.get("notify_who"), dict) else {}
            for k, v in list(data["notify_who"].items())[:20]:
                if re.fullmatch(r"[A-Za-z0-9_]+", str(k)) and isinstance(v, str):
                    m[str(k)] = v.strip()[:30]
            st["notify_who"] = m
        alexa_changed = isinstance(data.get("alexa"), bool) and data["alexa"] != bool(st.get("alexa"))
        if isinstance(data.get("alexa"), bool):
            st["alexa"] = data["alexa"]
        save_app_settings(st)
        if alexa_changed:
            ws_restart()
        return self.out(200, {"ok": True, "ha": ha_info()})

    def post_ha_test(self, data):
        try:
            if not TOKEN:
                raise RuntimeError("Keine Verbindung zu Home Assistant")
            notify("Testnachricht vom Planner – die Erinnerungen funktionieren.")
            return self.out(200, {"ok": True})
        except Exception as e:
            return self.out(200, {"ok": False, "error": str(e)[:200]})

    def post_tags(self, data):
        with LOCK:
            state["tags"] = clean_tags(data.get("tags", []) if isinstance(data, dict) else [])
            state["rev"] += 1
            save()
            return self.out(200, {"rev": state["rev"], "count": len(state["tags"])})

    def post_task(self, data):
        return self.store([clean(data)], data, check=self.headers.get("X-Check") == "1")

    def post_import(self, data):
        return self.store([clean(t) for t in (data.get("tasks", []) if isinstance(data, dict) else [])], data)

    def store(self, items, data, check=False):
        items = [t for t in items if t]
        if not items:
            return self.out(400, {"error": "ungültige Aufgabe"})
        with LOCK:
            if check:
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
            return self.out(200, {"rev": state["rev"], "count": len(items), "v": items[0]["v"]})

    def post_log(self, data):
        # Skriptfehler aus dem Browser ins Add-on-Protokoll (Home Assistant → Add-on → Protokoll). Höchstens 30 pro Stunde.
        now = time.time()
        with LOG_LOCK:
            BROWSER_LOG[:] = [x for x in BROWSER_LOG if now - x < 3600]
            if len(BROWSER_LOG) >= 30:
                return self.out(429, {"ok": False})
            BROWSER_LOG.append(now)
        d = data if isinstance(data, dict) else {}
        one = lambda k, n: re.sub(r"[\x00-\x1f\x7f]+", " ", str(d.get(k) or ""))[:n].strip()
        usr = self.ha_user()
        print("Browser-Fehler: %s | %s | Ansicht %s | Version %s | %s%s" % (one("msg", 400), one("where", 160), one("view", 20), one("ver", 20),
              one("ua", 120), " | " + usr["name"] if usr else ""), flush=True)
        return self.out(200, {"ok": True})

    def do_DELETE(self):
        if not self.guard() or not self.csrf_ok():
            return
        try:
            self.delete()
        except Exception:
            self.fail("DELETE", urlparse(self.path).path)

    def delete(self):
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
