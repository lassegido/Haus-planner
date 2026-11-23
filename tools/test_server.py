#!/usr/bin/env python3
"""Schnelltest des Servers: Prio bleibt erhalten, Schreibzugriff nur mit Header. Aufruf: python3 tools/test_server.py"""
import json, os, subprocess, sys, tempfile, time, urllib.request, urllib.error

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = tempfile.mkdtemp()
env = dict(os.environ, DATA_DIR=d + "/d", SHARE_DIR=d + "/s", LEGACY_SHARE_DIR=d + "/l", INDEX=root + "/planner/index.html",
           VERSION_FILE=root + "/planner/VERSION", PORT="8096")
os.makedirs(d + "/d")
sv = subprocess.Popen([sys.executable, root + "/planner/server.py"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)


def call(path, data=None, method=None, hdr=True):
    h = {"Content-Type": "application/json"}
    if hdr:
        h["X-Planner"] = "1"
    r = urllib.request.Request("http://127.0.0.1:8096/" + path, data=None if data is None else json.dumps(data).encode(), headers=h, method=method)
    try:
        with urllib.request.urlopen(r) as x:
            return x.status, json.load(x)
    except urllib.error.HTTPError as e:
        return e.code, {}


ok = True
def check(name, cond):
    global ok
    print(("OK   " if cond else "FEHL ") + name)
    ok = ok and cond

try:
    t = {"id": "t1", "title": "Test", "start": "2026-01-01", "end": "2026-01-02", "prio": 1, "proj": "P", "tags": ["a"]}
    check("Schreiben ohne Header wird abgelehnt (403)", call("api/task", t, hdr=False)[0] == 403)
    check("Löschen ohne Header wird abgelehnt (403)", call("api/task/t1", method="DELETE", hdr=False)[0] == 403)
    check("Schreiben mit Header", call("api/task", t)[0] == 200)
    got = call("api/tasks")[1]["tasks"][0]
    check("Priorität bleibt erhalten", got["prio"] == 1 and got["proj"] == "P")
    t["prio"] = 7
    call("api/task", t)
    check("Ungültige Priorität wird zu 0", call("api/tasks")[1]["tasks"][0]["prio"] == 0)
    del t["prio"]
    call("api/task", t)
    check("Alte Aufgabe ohne Priorität lesbar", call("api/tasks")[1]["tasks"][0]["prio"] == 0)
finally:
    sv.kill()
sys.exit(0 if ok else 1)
