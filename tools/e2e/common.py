"""Gemeinsame Hilfen für die Browser-Tests (tools/test_browser.py).

Jeder Test bekommt einen eigenen Server mit leerem Datenordner, damit sich Tests nicht gegenseitig beeinflussen.
Externe Adressen (Schriften, CDN) werden im Test-Browser blockiert: Tests sollen ohne Internet gleich laufen.
"""
import json, os, re, shutil, socket, subprocess, sys, tempfile, threading, time, urllib.error, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PHONE = {"viewport": {"width": 390, "height": 844}, "has_touch": True, "is_mobile": True}
IPAD = {"viewport": {"width": 820, "height": 1180}, "has_touch": True, "is_mobile": True}
DESKTOP = {"viewport": {"width": 1280, "height": 800}}
SHOTS = os.environ.get("SHOT_DIR")  # optional: Ordner für Bildschirmfotos bei Fehlern


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class Server:
    """Startet planner/server.py mit eigenem Datenordner. settings: Inhalt für settings.json."""

    def __init__(self, settings=None, **env):
        self.dir = tempfile.mkdtemp(prefix="planner-test-")
        os.makedirs(self.dir + "/d")
        if settings is not None:
            with open(self.dir + "/d/settings.json", "w") as f:
                json.dump(settings, f)
        self.port = free_port()
        e = dict(os.environ, DATA_DIR=self.dir + "/d", SHARE_DIR=self.dir + "/s", LEGACY_SHARE_DIR=self.dir + "/l",
                 INDEX=ROOT + "/planner/index.html", VERSION_FILE=ROOT + "/planner/VERSION", PORT=str(self.port),
                 GEMINI_URL="http://127.0.0.1:9/v1beta/models")
        e.update({k: str(v) for k, v in env.items()})
        self.log = open(self.dir + "/server.log", "w+")
        self.proc = subprocess.Popen([sys.executable, ROOT + "/planner/server.py"], env=e, stdout=self.log, stderr=subprocess.STDOUT)
        for _ in range(100):
            try:
                self.api("api/tasks")
                return
            except Exception:
                if self.proc.poll() is not None:
                    break
                time.sleep(0.1)
        raise RuntimeError("Server startet nicht:\n" + self.output())

    @property
    def url(self):
        return "http://127.0.0.1:%d/" % self.port

    def api(self, path, body=None, method=None):
        req = urllib.request.Request(self.url + path, data=None if body is None else json.dumps(body).encode(), method=method,
                                     headers={"Content-Type": "application/json", "X-Planner": "1"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            return {"_status": e.code, **(json.loads(e.read() or b"{}") or {})}

    def seed(self, tasks, tags=None):
        if tags is not None:
            self.api("api/tags", {"tags": tags})
        self.api("api/import", {"tasks": tasks})

    def tasks(self):
        return self.api("api/tasks")["tasks"]

    def task(self, tid):
        return next(t for t in self.tasks() if t["id"] == tid)

    def output(self):
        self.log.flush()
        self.log.seek(0)
        return self.log.read()[-2000:]

    def close(self):
        self.proc.terminate()
        try:
            self.proc.wait(5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self.log.close()
        shutil.rmtree(self.dir, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


class FakeGemini:
    """Nachgebaute Gemini-Schnittstelle. answer(prompt) liefert das JSON-Objekt, das die „KI“ zurückgibt."""

    def __init__(self, answer):
        self.prompts = []
        outer = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
                prompt = body["contents"][0]["parts"][0]["text"]
                outer.prompts.append(prompt)
                out = json.dumps({"candidates": [{"content": {"parts": [{"text": json.dumps(answer(prompt))}]}}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)

        self.http = ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=self.http.serve_forever, daemon=True).start()
        self.url = "http://127.0.0.1:%d/v1beta/models" % self.http.server_address[1]

    def close(self):
        self.http.shutdown()


class Page:
    """Eine Browser-Seite mit Fehlersammlung. Wartet, bis die Aufgaben geladen sind."""

    def __init__(self, browser, url, device=PHONE, onboarded=True, headers=None, wait=True):
        opts = dict(device)
        if headers:
            opts["extra_http_headers"] = headers
        self.ctx = browser.new_context(**opts)
        self.ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1)"), lambda r: r.abort())
        self.pg = self.ctx.new_page()
        self.errors = []
        self.external = []  # Anfragen an fremde Server (im Test blockiert)
        self.pg.on("pageerror", lambda e: self.errors.append(str(e)))
        self.pg.on("request", lambda r: r.url.startswith(("http://127.0.0.1", "file:", "data:", "blob:")) or self.external.append(r.url))
        if onboarded:
            self.pg.add_init_script("try{localStorage.setItem('haus-onb','1')}catch(e){}")
        self.pg.goto(url)
        if wait:
            self.ready()

    def ready(self):
        self.pg.wait_for_function("typeof regLoaded!=='undefined'&&regLoaded", timeout=10000)
        self.pg.wait_for_timeout(300)

    def js(self, expr, arg=None):
        return self.pg.evaluate(expr, arg)

    def touch(self, selector, points):
        """Wischgeste: points = [(art, x, y), …] mit art touchstart/touchmove/touchend."""
        self.pg.evaluate(TOUCH, [selector, points])

    def box(self, selector):
        return self.pg.eval_on_selector(selector, "e=>{const r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height]}")

    def settings(self, page=None):
        self.pg.click("#more")
        self.pg.wait_for_timeout(250)
        self.pg.click("#pop .pi:has-text('Einstellungen')")
        self.pg.wait_for_timeout(350)
        if page:
            self.pg.click("#s_body [data-go=%s]" % page)
            self.pg.wait_for_timeout(300)

    def shot(self, name):
        if SHOTS:
            os.makedirs(SHOTS, exist_ok=True)
            self.pg.screenshot(path=os.path.join(SHOTS, name + ".png"))

    def close(self):
        self.ctx.close()


TOUCH = """(a)=>{const [sel,seq]=a;const el=document.querySelector(sel);
 const mk=(t,x,y)=>{const to=new Touch({identifier:1,target:el,clientX:x,clientY:y});
  el.dispatchEvent(new TouchEvent(t,{touches:t==='touchend'?[]:[to],changedTouches:[to],bubbles:true,cancelable:true}))};
 for(const [t,x,y] of seq)mk(t,x,y)}"""


def task(tid, title, start, end=None, **kw):
    t = {"id": tid, "title": title, "start": start, "end": end or start, "status": "todo"}
    t.update(kw)
    return t
