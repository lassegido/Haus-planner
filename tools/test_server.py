#!/usr/bin/env python3
"""Schnelltest des Servers: Prio bleibt erhalten, Schreibzugriff nur mit Header. Aufruf: python3 tools/test_server.py"""
import json, os, subprocess, sys, tempfile, time, urllib.request, urllib.error

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = tempfile.mkdtemp()
env = dict(os.environ, DATA_DIR=d + "/d", SHARE_DIR=d + "/s", LEGACY_SHARE_DIR=d + "/l", INDEX=root + "/planner/index.html",
           VERSION_FILE=root + "/planner/VERSION", PORT="8096", GEMINI_URL="http://127.0.0.1:9/v1beta/models", TRUST_USER_HEADERS="1")
os.makedirs(d + "/d")
svlog = open(d + "/server.log", "w")
sv = subprocess.Popen([sys.executable, root + "/planner/server.py"], env=env, stdout=svlog, stderr=subprocess.STDOUT)
time.sleep(1.5)


def call(path, data=None, method=None, hdr=True, host=None):
    h = {"Content-Type": "application/json"}
    if hdr:
        h["X-Planner"] = "1"
    if host:
        h["Host"] = host
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
    # 1.42: „Nicht geschafft“ = erledigt + fail, nur bei abgeschlossenen Aufgaben
    call("api/task", {**t, "status": "done", "fail": True})
    check("Nicht geschafft bleibt erhalten", call("api/tasks")[1]["tasks"][0].get("fail") is True)
    call("api/task", {**t, "status": "todo", "fail": True})
    check("Offene Aufgabe verliert die Markierung", "fail" not in call("api/tasks")[1]["tasks"][0])
    call("api/task", {**t, "inbox": True})
    check("Sammelkorb bleibt erhalten (1.46)", call("api/tasks")[1]["tasks"][0].get("inbox") is True)
    call("api/task", {**t, "status": "done", "inbox": True})
    check("Erledigte Aufgabe liegt nicht im Sammelkorb", "inbox" not in call("api/tasks")[1]["tasks"][0])
    call("api/task", {**t, "status": "done", "fail": "ja"})
    check("Nur echtes true zählt als nicht geschafft", "fail" not in call("api/tasks")[1]["tasks"][0])
    call("api/task", t)
    # Sicherheit: fremder Hostname (DNS-Rebinding) wird abgewiesen, Heimnetz-Namen und IPs nicht
    check("Fremder Hostname wird abgewiesen (403)", call("api/tasks", host="evil.example.com")[0] == 403)
    check("Schreiben über fremden Hostnamen abgewiesen", call("api/task", t, host="evil.example.com:8099")[0] == 403)
    check("homeassistant.local erlaubt", call("api/tasks", host="homeassistant.local:8099")[0] == 200)
    check("IP-Adresse erlaubt", call("api/tasks", host="192.168.178.20:8099")[0] == 200)
    check("Name ohne Punkt erlaubt", call("api/tasks", host="homeassistant:8099")[0] == 200)
    r = urllib.request.urlopen("http://127.0.0.1:8096/api/tasks")
    check("Header nosniff gesetzt", r.headers.get("X-Content-Type-Options") == "nosniff")
    # Datenprüfung
    check("Unmögliches Datum wird abgewiesen", call("api/task", {**t, "id": "t2", "start": "2026-13-45"})[0] == 400)
    check("Falscher Typ bei Abhängigkeiten stürzt nicht ab", call("api/task", {**t, "id": "t3", "deps": 5, "checklist": "x"})[0] == 200)
    call("api/task", {**t, "id": "t4", "start": "2026-03-10", "end": "2026-03-01"})
    t4 = [x for x in call("api/tasks")[1]["tasks"] if x["id"] == "t4"][0]
    check("Ende vor Start wird korrigiert", t4["end"] == "2026-03-10")
    check("Mehrere Personen werden nicht abgeschnitten", call("api/task", {**t, "id": "t5", "who": "Lasse, Melanie, Oma Gisela, Opa Heinz, Handwerker Müller"})[0] == 200 and [x for x in call("api/tasks")[1]["tasks"] if x["id"] == "t5"][0]["who"].endswith("Müller"))
    # KI-Schlüssel aus der App: wird gespeichert, aber nie ausgeliefert
    check("Ungültiger KI-Schlüssel abgewiesen", call("api/ha-settings", {"ai_key": "abc"})[0] == 400)
    key = "AIzaTestSchluessel_1234567890abcdef"
    c, j = call("api/ha-settings", {"ai_key": key, "ai_model": "gemini-flash-latest"})
    check("KI-Schlüssel gespeichert", c == 200 and j["ha"]["ai"] and j["ha"]["aiapp"] and j["ha"]["model"] == "gemini-flash-latest")
    raw = urllib.request.urlopen("http://127.0.0.1:8096/api/tasks").read().decode()
    check("KI-Schlüssel wird nie ausgeliefert", key not in raw and key not in json.dumps(j))
    check("Neues Schlüsselformat mit Punkt (AQ.…) wird angenommen", call("api/ha-settings", {"ai_key": "AQ.Ab8Testschluessel_neuesFormat-1234567890"})[0] == 200)
    c, j = call("api/quick", {"text": "Rasen mähen morgen #Garten !2 @Melanie"})
    check("Schnelleingabe per Sprache legt Aufgabe an", c == 200 and j["task"]["title"] == "Rasen mähen" and j["task"]["tags"] == ["Garten"] and j["task"]["prio"] == 2 and j["task"]["who"] == "Melanie" and "morgen" in j["speech"])
    sp = json.loads(urllib.request.urlopen("http://127.0.0.1:8096/api/speech?when=woche&who=Melanie").read())["speech"]
    check("Vorlesen der Woche für eine Person", "Rasen mähen" in sp and "Aufgabe" in sp)
    c, j = call("api/voice", {"text": "Rasen mähen ist erledigt"})
    check("Siri: Abhaken per Sprache", c == 200 and j["speech"].endswith("ist erledigt."))
    c, j = call("api/voice", {"text": "heute"})
    check("Siri: „heute“ wird vorgelesen", c == 200 and j["speech"].startswith("Heute"))
    check("Schnelleingabe ohne Header abgewiesen", call("api/quick", {"text": "x"}, hdr=False)[0] == 403)
    check("Leere Schnelleingabe abgewiesen", call("api/quick", {"text": "  "})[0] == 400)
    # KI-Grenzen: Tageslimit und Stundenlimit greifen, Zähler ist sichtbar
    call("api/ha-settings", {"ai_key": key, "ai_model": "gemini-flash-lite-latest"})
    import datetime as _dt
    json.dump({"day": _dt.date.today().isoformat(), "n": 100, "blocked": False}, open(d + "/d/ai_usage.json", "w"))
    j = call("api/ai", {"prompt": "x"})[1]
    check("KI-Tageslimit greift", j["ok"] is False and "Tageslimit" in j["error"])
    check("KI-Verbrauch wird angezeigt", call("api/tasks")[1]["ha"]["aiuse"] == {"used": 100, "limit": 100, "blocked": False})
    json.dump({"day": _dt.date.today().isoformat(), "n": 0, "blocked": False}, open(d + "/d/ai_usage.json", "w"))
    errs = [call("api/ai", {"prompt": "x"})[1].get("error", "") for _ in range(21)]
    check("KI-Stundenlimit greift nach 20 Anfragen", "Stunde" in errs[-1] and not any("Stunde" in e for e in errs[:20]))
    # Persönliche Einstellungen je Home-Assistant-Benutzer
    def me_call(uid, name, data=None):
        h = {"Content-Type": "application/json", "X-Planner": "1", "X-Remote-User-Id": uid, "X-Remote-User-Display-Name": name}
        r = urllib.request.Request("http://127.0.0.1:8096/api/me", data=None if data is None else json.dumps(data).encode(), headers=h)
        return json.load(urllib.request.urlopen(r))
    me_call("lasse0001", "Lasse", {"design": "porto", "theme": "dark"})
    me_call("melanie01", "Melanie", {"design": "beere"})
    check("Design je Benutzer getrennt", me_call("lasse0001", "Lasse")["prefs"] == {"design": "porto", "theme": "dark"} and me_call("melanie01", "Melanie")["prefs"] == {"design": "beere"})
    check("Unbekannte Einstellung wird ignoriert", "ai_key" not in me_call("melanie01", "Melanie", {"ai_key": "x"}) and "ai_key" not in me_call("melanie01", "Melanie")["prefs"])
    check("Ohne Anmeldung kein Benutzer", call("api/me")[1].get("user") is None)
    c, j = call("api/ha-settings", {"notify": ["mobile_app_iphone_von_lasse", "mobile_app_ipad"], "notify_who": {"mobile_app_ipad": "Melanie"}})
    check("Gerät wird Person zugeordnet (automatisch und von Hand)", j["ha"]["nwho"] == {"mobile_app_iphone_von_lasse": "Lasse", "mobile_app_ipad": "Melanie"})
    check("KI-Schlüssel entfernbar", call("api/ha-settings", {"ai_key": ""})[1]["ha"]["ai"] is False)
    # Lokale Bibliotheken und Schriften (planner/vendor)
    def raw(path, method="GET", data=None, hdr=None):
        r = urllib.request.Request("http://127.0.0.1:8096/" + path, data=data, method=method, headers=hdr or {})
        try:
            with urllib.request.urlopen(r) as x:
                return x.status, x.headers, x.read()
        except urllib.error.HTTPError as e:
            return e.code, e.headers, e.read()
    if os.path.isdir(root + "/planner/vendor"):
        c, h, b = raw("vendor/jspdf.umd.min.js?v=1")
        check("Bibliothek wird lokal ausgeliefert (JavaScript, nosniff)", c == 200 and h["Content-Type"].startswith("text/javascript") and h["X-Content-Type-Options"] == "nosniff" and b.startswith(b"/**"))
        c, h, b = raw("vendor/fonts.css")
        check("Schriften-CSS wird ausgeliefert", c == 200 and h["Content-Type"].startswith("text/css") and b"@font-face" in b)
        check("Nur erlaubte Dateien aus vendor/ (keine anderen Endungen, kein ../)", b"cdnjs" not in raw("vendor/MANIFEST.txt")[2]
              and b"ThreadingHTTPServer" not in raw("vendor/..%2F..%2Fserver.py")[2] and b"ThreadingHTTPServer" not in raw("vendor/../server.py")[2]
              and raw("vendor/nichtda.js")[0] == 404)
    # Fehler aus dem Browser landen im Protokoll, begrenzt und ohne Zeilenumbrüche
    check("Fehlerprotokoll ohne Header abgewiesen", call("api/log", {"msg": "x"}, hdr=False)[0] == 403)
    check("Fehlerprotokoll nimmt Meldung an", call("api/log", {"msg": "TypeError: x is null\nGEFÄLSCHTE ZEILE", "where": "index.html:12:3", "ver": "1.32.0", "view": "list"})[0] == 200)
    codes = [call("api/log", {"msg": "Flut %d" % i})[0] for i in range(40)]
    check("Fehlerprotokoll begrenzt (höchstens 30 pro Stunde)", codes.count(200) == 29 and codes[-1] == 429)
    check("Unbekannte Schnittstelle: 404", call("api/gibtsnicht", {"x": 1})[0] == 404)
    check("Zu große Anfrage wird abgewiesen", call("api/me", {"x": "y" * 30000})[0] == 400)
    open(d + "/d/settings.json", "w").write("{kaputt")
    c, j = call("api/tasks")
    check("Defekte Einstellungsdatei: Planner läuft weiter", c == 200 and j["ha"]["ai"] is False)
    time.sleep(0.3)
    svlog.flush()
    logtxt = open(d + "/server.log", encoding="utf-8").read()
    check("Browser-Fehler steht im Protokoll (eine Zeile, mit Ort und Version)", "Browser-Fehler: TypeError: x is null GEFÄLSCHTE ZEILE | index.html:12:3 | Ansicht list | Version 1.32.0" in logtxt
          and "\nGEFÄLSCHTE" not in logtxt)
    check("Defekte Datei wird im Protokoll gemeldet (einmal)", logtxt.count("Einstellungen aus der App nicht lesbar") == 1)
finally:
    sv.kill()
sys.exit(0 if ok else 1)
