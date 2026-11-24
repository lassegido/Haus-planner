#!/usr/bin/env python3
"""Test der Mitteilungs-Knöpfe und der Alexa-Sprachbefehle mit einem nachgebauten Home Assistant. Aufruf: python3 tools/test_ha.py"""
import base64, hashlib, importlib.util, json, os, socket, struct, subprocess, sys, tempfile, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("srv", root + "/planner/server.py")
srv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(srv)

posts = []


class Mock(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def reply(self, obj):
        b = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        self.reply({"data": {"slug": "abc123_planner"}} if "addons" in self.path else {"time_zone": "Europe/Berlin"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n) or b"{}")
        posts.append((self.path, body))
        if self.path.endswith("/template"):
            tpl = body.get("template", "")
            out = '["event.echo_kueche"]' if "integration_entities" in tpl else "notify.echo_kueche_speak" if "device_entities" in tpl else ""
            b = out.encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return
        self.reply({})


def frame(text):
    b = text.encode()
    return bytes([0x81, len(b)]) + b if len(b) < 126 else bytes([0x81, 126]) + struct.pack(">H", len(b)) + b


def ws_mock(listener, done):
    c, _ = listener.accept()
    head = b""
    while b"\r\n\r\n" not in head:
        head += c.recv(1)
    key = [l for l in head.decode().split("\r\n") if l.lower().startswith("sec-websocket-key")][0].split(":")[1].strip()
    acc = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
    c.sendall(("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: %s\r\n\r\n" % acc).encode())
    c.sendall(frame(json.dumps({"type": "auth_required"})))
    auth = json.loads(srv.ws_recv(c))
    assert auth["access_token"] == "tok"
    c.sendall(frame(json.dumps({"type": "auth_ok"})))
    sub = json.loads(srv.ws_recv(c))
    assert sub["event_type"] == "mobile_app_notification_action"
    time.sleep(8)  # erst die tägliche Erinnerung abwarten
    c.sendall(frame(json.dumps({"type": "event", "event": {"data": {"action": "PLANNER_DONE_t1"}}})))
    c.sendall(frame(json.dumps({"type": "event", "event": {"data": {"action": "PLANNER_DONE_../etc"}}})))
    sub2 = json.loads(srv.ws_recv(c))
    assert sub2["type"] == "subscribe_trigger" and sub2["trigger"]["entity_id"] == ["event.echo_kueche"], sub2

    def voice(n, text, person=""):
        st = {"entity_id": "event.echo_kueche", "state": "2026-11-24T06:%02d:00+00:00" % n,
              "attributes": {"voice_command": text, "person_first_name": person}}
        c.sendall(frame(json.dumps({"id": 2, "type": "event", "event": {"variables": {"trigger": {"entity_id": "event.echo_kueche", "to_state": st}}}})))
        time.sleep(1.2)
    voice(1, "planner rasen mähen morgen tag garten", "Lasse")
    voice(2, "planner was steht heute an")
    voice(3, "wie wird das wetter")
    voice(4, "planner fenster putzen ist erledigt")
    voice(4, "planner doppelt gesendet")  # gleicher Zeitstempel: wird ignoriert
    time.sleep(2)
    done.set()


d = tempfile.mkdtemp()
os.makedirs(d + "/d")
today = time.strftime("%Y-%m-%d")
json.dump({"schema": 2, "rev": 1, "tags": [{"n": "Garten", "c": "mint"}], "tasks": [
    {"id": "t1", "title": "Rauchmelder tauschen", "start": "2020-01-01", "end": "2020-01-02", "status": "todo", "prio": 1, "v": 0},
    {"id": "t2", "title": "Wiederkehrend", "start": "2020-01-01", "end": "2020-01-02", "status": "todo", "rec": {"every": 1, "unit": "w"}, "v": 0},
    {"id": "t3", "title": "Fenster putzen", "start": today, "end": today, "status": "todo", "v": 0},
    {"id": "t4", "title": "Lasses Aufgabe", "start": "2020-01-01", "end": "2020-01-02", "status": "todo", "who": "Lasse", "v": 0},
    {"id": "t5", "title": "Melanies Aufgabe", "start": "2020-01-01", "end": "2020-01-02", "status": "todo", "who": "Melanie", "v": 0}]}, open(d + "/d/tasks.json", "w"))
json.dump({"notify": ["mobile_app_test", "mobile_app_iphone_von_lasse", "mobile_app_iphone_von_melanie"], "time": "00:00", "alexa": True}, open(d + "/d/settings.json", "w"))
http = HTTPServer(("127.0.0.1", 8095), Mock)
threading.Thread(target=http.serve_forever, daemon=True).start()
lst = socket.socket()
lst.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lst.bind(("127.0.0.1", 8094))
lst.listen(1)
done = threading.Event()
threading.Thread(target=ws_mock, args=(lst, done), daemon=True).start()
env = dict(os.environ, DATA_DIR=d + "/d", SHARE_DIR=d + "/s", LEGACY_SHARE_DIR=d + "/l", INDEX=root + "/planner/index.html",
           VERSION_FILE=root + "/planner/VERSION", PORT="8093", SUPERVISOR_URL="http://127.0.0.1:8095/core", SUPERVISOR_BASE="http://127.0.0.1:8095",
           HA_WS_URL="ws://127.0.0.1:8094/ws", SUPERVISOR_TOKEN="tok")
sv = subprocess.Popen([sys.executable, root + "/planner/server.py"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
ok = True


def check(name, cond):
    global ok
    print(("OK   " if cond else "FEHL ") + name)
    ok = ok and cond


try:
    done.wait(30)
    time.sleep(1)
    rem = [b for p, b in posts if "/services/notify/mobile_app_test" in p and b.get("message") != "clear_notification" and "data" in b]
    first = rem[0]["data"] if rem else {}
    acts = [a["action"] for a in first.get("actions", [])]
    check("Erinnerung hat Knopf für t1", "PLANNER_DONE_t1" in acts)
    check("Wiederkehrende Aufgabe hat keinen Knopf", "PLANNER_DONE_t2" not in acts)
    check("Antippen öffnet den Planner", first.get("url") == "/hassio/ingress/abc123_planner")
    t = {x["id"]: x for x in json.load(open(d + "/d/tasks.json"))["tasks"]}
    check("Knopfdruck erledigt die Aufgabe", t["t1"]["status"] == "done" and t["t1"]["v"] == 1 and t["t1"]["log"])
    check("Anderes bleibt unverändert", t["t2"]["status"] == "todo")
    left = [b for p, b in posts if "/services/notify/mobile_app_test" in p][-1]
    check("Mitteilung wird danach aktualisiert", "PLANNER_DONE_t1" not in json.dumps(left))
    said = [b.get("message") for p, b in posts if p.endswith("/services/notify/send_message") and b.get("entity_id") == "notify.echo_kueche_speak"]
    t = {x["id"]: x for x in json.load(open(d + "/d/tasks.json"))["tasks"]}
    new = [x for x in t.values() if x["title"] == "Rasen mähen"]
    def first_for(sv):
        r = [b for p, b in posts if p.endswith("/services/notify/" + sv) and "data" in b and b.get("message") != "clear_notification"]
        return json.dumps(r[0], ensure_ascii=False) if r else ""
    la, me = first_for("mobile_app_iphone_von_lasse"), first_for("mobile_app_iphone_von_melanie")
    check("Erinnerung je Person: Lasse bekommt seine Aufgabe, nicht Melanies", "PLANNER_DONE_t4" in la and "PLANNER_DONE_t5" not in la)
    check("Erinnerung je Person: Melanie bekommt ihre Aufgabe, nicht Lasses", "PLANNER_DONE_t5" in me and "PLANNER_DONE_t4" not in me)
    check("Erinnerung je Person: Aufgaben ohne Zuständigkeit bekommen beide", "PLANNER_DONE_t1" in la and "PLANNER_DONE_t1" in me)
    check("Alexa: Aufgabe per Sprache angelegt (Tag, Datum, Person per Stimmerkennung)", len(new) == 1 and new[0]["tags"] == ["Garten"] and new[0]["who"] == "Lasse" and new[0]["start"] > today)
    check("Alexa: Bestätigung auf demselben Echo gesprochen", len(said) >= 1 and "Rasen mähen" in said[0] and "morgen" in said[0])
    check("Alexa: „was steht heute an“ wird vorgelesen", len(said) >= 2 and said[1].startswith("Heute") and "Fenster putzen" in said[1])
    check("Alexa: fremde Befehle werden ignoriert", len(said) == 3)
    check("Alexa: Abhaken per Sprache", t["t3"]["status"] == "done" and said[-1].endswith("ist erledigt."))
    check("Alexa: doppelte Ereignisse werden nur einmal verarbeitet", not any(x["title"].lower().startswith("doppelt") for x in t.values()))
finally:
    sv.kill()
    print(sv.stdout.read().decode()[-600:])
sys.exit(0 if ok else 1)
