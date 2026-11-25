/* Speicher: Server im Home-Assistant-Add-on (relative Pfade wegen Ingress) */
let rev=-1;
function prefGet(k){try{return localStorage.getItem("haus-"+k)}catch(e){return null}}
function prefSet(k,v){try{localStorage.setItem("haus-"+k,v)}catch(e){}if(typeof prefSync==="function")prefSync(k,v)}
let USER=null;
async function api(path,opt){opt=opt||{};if(opt.method&&opt.method!=="GET")opt={...opt,headers:{...(opt.headers||{}),"X-Planner":"1"}};const r=await fetch(path,opt);if(r.status===409){const e=new Error("409");e.conflict=await r.json().catch(()=>({}));throw e}if(!r.ok)throw new Error(r.status);return r.json()}
async function pull(force){
  try{const j=await api("api/tasks"+(force?"":"?rev="+rev));
    $("note").textContent="";
    if(j.version)$("ver").textContent="Add-on-Version "+j.version;
    haInfo=j.ha||null;
    if(j.tasks){const sg=a=>JSON.stringify(a.map(t=>{const {v,...r}=t;return r})),same=loaded&&sg(RAW)===sg(j.tasks)&&JSON.stringify(reg)===JSON.stringify(j.tags||[]);
      RAW=j.tasks;reg=j.tags||[];regLoaded=true;rev=j.rev;loaded=true;if(!same)render()}
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
const PK=["theme","design","font","me","sort","glw","hwho","htile","fun"];
function prefSync(k,v){if(!USER||!PK.includes(k))return;fetch("api/me",{method:"POST",headers:{"Content-Type":"application/json","X-Planner":"1"},body:JSON.stringify({[k]:v||""})}).catch(()=>{})}
async function initUser(){
  try{const r=await fetch("api/me",{cache:"no-store"}),j=await r.json();if(!j.user)return;USER=j.user;const sp=j.prefs||{};
    if(Object.keys(sp).length){PK.forEach(k=>{try{if(sp[k])localStorage.setItem("haus-"+k,sp[k]);else localStorage.removeItem("haus-"+k)}catch(_){}})}
    else{const up={};PK.forEach(k=>{const v=prefGet(k);if(v)up[k]=v});if(Object.keys(up).length)fetch("api/me",{method:"POST",headers:{"Content-Type":"application/json","X-Planner":"1"},body:JSON.stringify(up)}).catch(()=>{})}
    if(!prefGet("me")){const first=USER.split(/\s+/)[0].toLowerCase(),m=["Lasse","Melanie",...allWho()].find(n=>n.toLowerCase()===first);if(m){prefSet("me",m);prefSet("onb","1")}}
    applyTheme();applyFont();render()}catch(_){}}
function init(){
  initUser();
  pull(true);setInterval(()=>pull(),5000);
  document.addEventListener("visibilitychange",()=>{if(!document.hidden)pull()});
}

