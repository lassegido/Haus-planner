#!/usr/bin/env python3
"""Erzeugt die Add-on-Version (planner/index.html + VERSION) aus der Master-Datei src/planner.html.

Aufruf im Repository-Hauptordner:  python3 tools/build.py
Die Versionsnummer kommt aus planner/config.yaml (Zeile "version").
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "planner.html")
ADDON = os.path.join(ROOT, "planner")

cfg = open(os.path.join(ADDON, "config.yaml"), encoding="utf-8").read()
ver = re.search(r'^version:\s*"?([^"\n]+)"?\s*$', cfg, re.M).group(1).strip()

s = open(SRC, encoding="utf-8").read()
a = s.index("/* Speicher: gemeinsame Datenbank, sonst lokal */")
b = s.index("/* Anzeige */")
storage = '''/* Speicher: Server im Home-Assistant-Add-on (relative Pfade wegen Ingress) */
let rev=-1;
function prefGet(k){try{return localStorage.getItem("haus-"+k)}catch(e){return null}}
function prefSet(k,v){try{localStorage.setItem("haus-"+k,v)}catch(e){}}
async function api(path,opt){const r=await fetch(path,opt);if(r.status===409){const e=new Error("409");e.conflict=await r.json().catch(()=>({}));throw e}if(!r.ok)throw new Error(r.status);return r.json()}
async function pull(force){
  try{const j=await api("api/tasks"+(force?"":"?rev="+rev));
    $("note").textContent="";
    if(j.version)$("ver").textContent="Add-on-Version "+j.version;
    haInfo=j.ha||null;
    if(j.tasks){RAW=j.tasks;reg=j.tags||[];regLoaded=true;rev=j.rev;loaded=true;render()}
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
function init(){
  pull(true);setInterval(()=>pull(),5000);
  document.addEventListener("visibilitychange",()=>{if(!document.hidden)pull()});
}

'''
s = s[:a] + storage + s[b:]
dl = '''async function dl(name,data){
  try{const blob=data instanceof Blob?data:new Blob([data],{type:"application/pdf"}),file=new File([blob],name,{type:blob.type});
    if(matchMedia("(pointer:coarse)").matches&&navigator.canShare&&navigator.canShare({files:[file]})){
      try{await navigator.share({files:[file]});$("dlx").close();return}catch(e){if(e&&e.name==="AbortError")return}}
    const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(a.href),5000);$("dlx").close()
  }catch(e){$("note").textContent="Download fehlgeschlagen: "+(e.message||e)}}
'''
s, n = re.subn(r"async function dl\(name,data\)\{.*\n", lambda m: dl, s, count=1)
if n != 1:
    sys.exit("FEHLER: dl()-Funktion in src/planner.html nicht gefunden")
if "claude.use" in s or "window.claude" in s or "lsGet(" in s:
    sys.exit("FEHLER: Claude-/Browser-spezifischer Code ist noch in der Add-on-Version")

PWA = ('<link rel="manifest" href="manifest.webmanifest"><link rel="apple-touch-icon" href="icons/apple-touch-icon.png">'
       '<link rel="icon" type="image/png" href="icons/icon-192.png"><meta name="mobile-web-app-capable" content="yes">'
       '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Planner">'
       '<meta name="apple-mobile-web-app-status-bar-style" content="default">')
if s.count("</head>") != 1:
    sys.exit("FEHLER: </head> nicht eindeutig")
s = s.replace("</head>", PWA + "</head>")
open(os.path.join(ADDON, "index.html"), "w", encoding="utf-8").write(s)
open(os.path.join(ADDON, "VERSION"), "w", encoding="utf-8").write(ver + "\n")
print("OK: planner/index.html und VERSION erzeugt, Version", ver)
