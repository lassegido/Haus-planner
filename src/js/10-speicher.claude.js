/* Speicher: gemeinsame Datenbank, sonst lokal */
function lsGet(){try{return JSON.parse(localStorage.getItem("haus-tasks")||"[]")}catch(e){return[]}}
function lsSet(){try{localStorage.setItem("haus-tasks",JSON.stringify(RAW))}catch(e){}}
function prefGet(k){try{return localStorage.getItem("haus-"+k)}catch(e){return null}}
function prefSet(k,v){try{localStorage.setItem("haus-"+k,v)}catch(e){}if(typeof prefSync==="function")prefSync(k,v)}
let USER=null;
function lsGetReg(){try{return JSON.parse(localStorage.getItem("haus-tags")||"[]")}catch(e){return[]}}
function lsSetReg(){try{localStorage.setItem("haus-tags",JSON.stringify(reg))}catch(e){}}
let metaCol=null;
async function init(){
  let db=null;
  try{db=await window.claude.use("db")}catch(e){}
  if(db){
    col=db.collection("tasks");metaCol=db.collection("meta");
    metaCol.onSnapshot(s=>{const d=s.docs.find(x=>x.id==="tags"),l=d&&d.data().list;reg=Array.isArray(l)?l:[];regLoaded=true;render()},()=>{regLoaded=true});
    const timer=setTimeout(()=>{if(!loaded)$("note").textContent="Laden dauert länger als gewöhnlich …"},10000);
    col.onSnapshot(s=>{loaded=true;clearTimeout(timer);$("note").textContent="";RAW=s.docs.map(d=>({id:d.id,...d.data()}));render()},
      e=>{$("note").textContent="Gemeinsamer Speicher nicht erreichbar ("+e.code+")."});
  }else{
    $("note").textContent="Hinweis: Nur lokaler Speicher auf diesem Gerät – Teilen mit Partnerin funktioniert so nicht.";
    RAW=lsGet();reg=lsGetReg();regLoaded=true;render();
  }
}
async function saveTask(t,o){
  const {id,...data}=t;depLater(t,o);
  if(col){try{await col.doc(id).set(data)}catch(e){$("note").textContent="Speichern fehlgeschlagen: "+(e.message||e.code)}}
  else{const i=RAW.findIndex(x=>x.id===id);i>=0?RAW[i]=t:RAW.push(t);lsSet();render()}
}
async function delTask(id){
  if(col){try{await col.doc(id).delete();for(const t of RAW)if((t.deps||[]).includes(id))await saveTask({...t,deps:t.deps.filter(x=>x!==id)})}catch(e){}}
  else{RAW=RAW.filter(t=>t.id!==id).map(t=>({...t,deps:(t.deps||[]).filter(x=>x!==id)}));lsSet();render()}
}

async function saveReg(l){
  reg=l;
  if(metaCol){try{await metaCol.doc("tags").set({list:l})}catch(e){$("note").textContent="Tags speichern fehlgeschlagen: "+(e.message||e.code)}}
  else{lsSetReg();render()}
}
async function saveMany(list){for(const t of list)await saveTask(t)}
const aiAvail=()=>true;
async function aiJson(prompt,raw){const sm=await window.claude.use("sample");if(!sm)throw new Error("Die KI ist hier nicht verfügbar");return sm.json(prompt)}

