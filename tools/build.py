#!/usr/bin/env python3
"""Erzeugt die Add-on-Version (haus_planer/index.html + VERSION) aus der Master-Datei src/haus-planner.html.

Aufruf im Repository-Hauptordner:  python3 tools/build.py
Die Versionsnummer kommt aus haus_planer/config.yaml (Zeile "version").
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "haus-planner.html")
ADDON = os.path.join(ROOT, "haus_planer")

cfg = open(os.path.join(ADDON, "config.yaml"), encoding="utf-8").read()
ver = re.search(r'^version:\s*"?([^"\n]+)"?\s*$', cfg, re.M).group(1).strip()

s = open(SRC, encoding="utf-8").read()
a = s.index("/* Speicher: gemeinsame Datenbank, sonst lokal */")
b = s.index("/* Anzeige */")
storage = '''/* Speicher: Server im Home-Assistant-Add-on (relative Pfade wegen Ingress) */
let rev=-1;
async function api(path,opt){const r=await fetch(path,opt);if(!r.ok)throw new Error(r.status);return r.json()}
async function pull(force){
  try{const j=await api("api/tasks"+(force?"":"?rev="+rev));
    $("note").textContent="";
    if(j.version)$("ver").textContent="Add-on-Version "+j.version;
    if(j.tasks){tasks=j.tasks;rev=j.rev;loaded=true;render()}
  }catch(e){$("note").textContent="Keine Verbindung zum Server – Änderungen werden evtl. nicht gespeichert."}
}
async function saveTask(t){
  const i=tasks.findIndex(x=>x.id===t.id);i>=0?tasks[i]=t:tasks.push(t);render();
  try{await api("api/task",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(t)})}
  catch(e){$("note").textContent="Speichern fehlgeschlagen."}
  pull(true);
}
async function delTask(id){
  tasks=tasks.filter(t=>t.id!==id).map(t=>({...t,deps:(t.deps||[]).filter(x=>x!==id)}));render();
  try{await api("api/task/"+id,{method:"DELETE"})}catch(e){$("note").textContent="Löschen fehlgeschlagen."}
  pull(true);
}
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
    sys.exit("FEHLER: dl()-Funktion in src/haus-planner.html nicht gefunden")
if "claude.use" in s or "localStorage" in s:
    sys.exit("FEHLER: Claude-/Browser-spezifischer Code ist noch in der Add-on-Version")

open(os.path.join(ADDON, "index.html"), "w", encoding="utf-8").write(s)
open(os.path.join(ADDON, "VERSION"), "w", encoding="utf-8").write(ver + "\n")
print("OK: haus_planer/index.html und VERSION erzeugt, Version", ver)
