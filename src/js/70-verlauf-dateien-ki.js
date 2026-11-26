/* Verlauf, Kommentare */
const lg=(o,n)=>({...n,log:diffLog(o,n)});
const CMI='<svg class="mi" viewBox="0 0 24 24" aria-label="Kommentare"><path d="M4 5h16v11H9l-5 4z"/></svg>';
const FLI='<svg class="mi" viewBox="0 0 24 24" aria-label="Anhänge"><path d="M20 11.5l-7.8 7.8a5 5 0 0 1-7-7L13 4.5a3.4 3.4 0 0 1 4.8 4.8l-7.9 7.9a1.8 1.8 0 0 1-2.5-2.5l7.2-7.2"/></svg>';
function extra(t){const c=(t.log||[]).filter(x=>x.k==="c").length,f=(t.files||[]).length;return(c?`<span class="ex">${CMI}${c}</span>`:"")+(f?`<span class="ex">${FLI}${f}</span>`:"")}
function diffLog(o,n){
  const L=(o.log||[]).slice(),me=prefGet("me")||"",now=new Date().toISOString().slice(0,16),add=x=>L.push({t:now,a:me,k:"h",x});
  if(o.status!==n.status||isFail(o)!==isFail(n))add("Status: "+stName(o)+" → "+stName(n));
  if(o.start!==n.start||o.end!==n.end)add("Zeitraum: "+dr(o)+" → "+dr(n));
  if((o.who||"")!==(n.who||""))add("Verantwortlich: "+(n.who||"niemand"));
  if((o.proj||"")!==(n.proj||""))add("Projekt: "+(n.proj||"keins"));
  if((o.prio||0)!==(n.prio||0))add("Priorität: "+(n.prio?"Prio "+n.prio:"keine"));
  if(o.title!==n.title)add("Titel geändert");
  return L.slice(-120)}
const fts=t=>{const d=new Date(t+"Z");return isNaN(d)?"":d.toLocaleString("de-DE",{day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit"})};
function drawLog(){
  $("f_logsec").style.display=editing?"":"none";if(!editing)return;
  const L=(editing.log||[]).slice().reverse().slice(0,40);
  $("lg_list").innerHTML=L.length?L.map(x=>x.k==="c"?`<div class="c"><small>${esc(x.a||"Kommentar")} · ${fts(x.t)}</small>${esc(x.x)}</div>`:`<div class="h">${fts(x.t)}${x.a?" · "+esc(x.a):""} · ${esc(x.x)}</div>`).join(""):'<div class="none">Noch nichts passiert.</div>'}
async function addComment(){
  const x=$("lg_in").value.trim();if(!x||!editing)return;
  const L=[...(editing.log||[]),{t:new Date().toISOString().slice(0,16),a:prefGet("me")||"",k:"c",x:x.slice(0,500)}].slice(-120);
  editing={...editing,log:L};$("lg_in").value="";drawLog();await saveTask({...byId(editing.id),log:L})}
$("lg_add").onclick=addComment;
$("lg_in").onkeydown=e=>{if(e.key==="Enter"){e.preventDefault();addComment()}};

/* Fotos und Dateien (nur im Add-on, dort liegen sie auf dem Server) */
const fsz=n=>n>1048576?(n/1048576).toFixed(1).replace(".",",")+" MB":Math.max(1,Math.round(n/1024))+" KB";
function drawFiles(){
  const can=typeof api==="function";$("f_filesec").style.display=can?"":"none";if(!can)return;
  $("fl_btn").style.display=editing?"":"none";
  if(!editing){$("f_files").innerHTML='<div class="none" style="grid-column:1/-1">Erst speichern, dann Fotos und Dateien anhängen.</div>';return}
  const u=f=>`api/file/${editing.id}/${f.id}`,F=editing.files||[];
  $("f_files").innerHTML=F.map(f=>/^image\//.test(f.ty)
    ?`<div class="fl img"><a href="${u(f)}" target="_blank" rel="noopener"><img loading="lazy" src="${u(f)}" alt="${esc(f.n)}"></a><button class="x" data-fd="${f.id}" aria-label="Entfernen">✕</button></div>`
    :`<div class="fl doc"><a href="${u(f)}" target="_blank" rel="noopener"><b>${esc(f.n)}</b><small>${fsz(f.s)}</small></a><button class="x" data-fd="${f.id}" aria-label="Entfernen">✕</button></div>`).join("")}
async function shrink(f){
  if(!/^image\/(jpeg|png|webp)$/.test(f.type)||f.size<400000)return f;
  try{const bm=await createImageBitmap(f),k=Math.min(1,1600/Math.max(bm.width,bm.height)),c=document.createElement("canvas");c.width=Math.round(bm.width*k);c.height=Math.round(bm.height*k);
    c.getContext("2d").drawImage(bm,0,0,c.width,c.height);const b=await new Promise(r=>c.toBlob(r,"image/jpeg",.82));return b&&b.size<f.size?b:f}catch(e){return f}}
$("fl_btn").onclick=()=>$("fl_in").click();
$("fl_in").onchange=async()=>{
  const fs=[...$("fl_in").files];$("fl_in").value="";if(!editing)return;
  for(const f of fs){
    if(f.size>20e6){toast("„"+f.name+"“ ist größer als 20 MB");continue}
    try{const b=await shrink(f),ty=b.type||f.type||"application/octet-stream",nm=b===f?f.name:f.name.replace(/\.\w+$/,"")+".jpg";
      const r=await api("api/file/"+editing.id+"?name="+encodeURIComponent(nm)+"&type="+encodeURIComponent(ty),{method:"POST",body:b});
      const files=[...(editing.files||[]),r.file];editing={...editing,files};await saveTask({...byId(editing.id),files});drawFiles()}
    catch(e){toast("Hochladen fehlgeschlagen: "+f.name)}}};
$("f_files").onclick=async e=>{
  const b=e.target.closest("[data-fd]");if(!b||!editing)return;const fid=b.dataset.fd;
  try{await api("api/file/"+editing.id+"/"+fid,{method:"DELETE"})}catch(x){}
  const files=(editing.files||[]).filter(f=>f.id!==fid);editing={...editing,files};drawFiles();await saveTask({...byId(editing.id),files})};

/* Kalender */
let calM=null,calSel=null;
const DLONG=["Sonntag","Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag"];
function cal(list){
  const T=iso(new Date());if(!calM)calM=T.slice(0,7);if(!calSel)calSel=T;
  const[y,m]=calM.split("-").map(Number),first=Date.UTC(y,m-1,1)/864e5,dow=(fromDn(first).getUTCDay()+6)%7,start=first-dow,
    nd=new Date(Date.UTC(y,m,0)).getUTCDate(),weeks=Math.ceil((dow+nd)/7);
  let cells="";
  for(let i=0;i<weeks*7;i++){
    const d=start+i,ds=iso(fromDn(d)),dt=fromDn(d),L=list.filter(t=>dn(t.start)<=d&&dn(t.end)>=d);
    cells+=`<div class="cd${dt.getUTCMonth()!==m-1?" out":""}${ds===T?" today":""}${ds===calSel?" sel":""}" data-day="${ds}"><span class="n">${dt.getUTCDate()}</span>`
      +`<div class="pills">${L.slice(0,3).map(t=>`<button class="pill ${t.status}${isFail(t)?" fail":""}${t.ms?" ms":""}${isLate(t)?" late":""}" data-id="${t.id}">${esc(t.title)}</button>`).join("")}</div>`
      +`<div class="cdots">${L.slice(0,4).map(t=>`<i class="${t.status}"></i>`).join("")}</div>${L.length>3?`<em>+${L.length-3}</em>`:""}</div>`}
  const sd=dn(calSel),sl=list.filter(t=>dn(t.start)<=sd&&dn(t.end)>=sd),sdt=fromDn(sd);
  return`<div class="calbar"><button class="cnav" data-cm="-1" aria-label="Voriger Monat">‹</button><h2>${MONL[m-1]} ${y}</h2><button class="cnav" data-cm="1" aria-label="Nächster Monat">›</button><button class="cnav t" data-cm="0">Heute</button></div>`
   +`<div class="cgrid">${["Mo","Di","Mi","Do","Fr","Sa","So"].map(x=>`<div class="cwd">${x}</div>`).join("")}${cells}</div>`
   +`<div class="agenda"><h3><span>${DLONG[sdt.getUTCDay()]}, ${sdt.getUTCDate()}. ${MONL[sdt.getUTCMonth()]}</span><button class="btn ghost sm" data-newday="${calSel}">Aufgabe anlegen</button></h3>${sl.length?sl.map((t,i)=>card(t,t.status,i)).join(""):'<div class="none">Nichts geplant.</div>'}</div>`}
$("main").addEventListener("click",e=>{
  const cm=e.target.closest("[data-cm]");
  if(cm){const v=+cm.dataset.cm,T=iso(new Date());if(!v){calM=T.slice(0,7);calSel=T}else{const[y,m]=calM.split("-").map(Number),d=new Date(Date.UTC(y,m-1+v,1));calM=iso(d).slice(0,7);calSel=calM+"-01"}render();return}
  const nd=e.target.closest("[data-newday]");if(nd){openDlg();$("f_start").value=nd.dataset.newday;$("f_end").value=nd.dataset.newday;drawRange();return}
  const dy=e.target.closest("[data-day]");if(dy&&!e.target.closest("[data-id]")){calSel=dy.dataset.day;render()}});
function ics(){
  const esc2=x=>String(x||"").replace(/\\/g,"\\\\").replace(/;/g,"\;").replace(/,/g,"\\,").replace(/\r?\n/g,"\\n"),c=d=>d.replace(/-/g,""),stp=new Date().toISOString().replace(/[-:]/g,"").slice(0,15)+"Z";
  const ev=tasks.filter(t=>t.status!=="done").map(t=>["BEGIN:VEVENT","UID:"+t.id+"@planner","DTSTAMP:"+stp,"DTSTART;VALUE=DATE:"+c(t.start),"DTEND;VALUE=DATE:"+c(iso(fromDn(dn(t.end)+1))),"SUMMARY:"+esc2(t.title),...(t.notes?["DESCRIPTION:"+esc2(t.notes)]:[]),...(t.prio?["PRIORITY:"+[0,1,5,9][t.prio]]:[]),...((t.who||t.proj)?["CATEGORIES:"+[t.who,t.proj].filter(Boolean).map(esc2).join(",")]:[]),"END:VEVENT"].join("\r\n"));
  return["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Planner//DE","CALSCALE:GREGORIAN","X-WR-CALNAME:Planner",...ev,"END:VCALENDAR"].join("\r\n")+"\r\n"}
$("x_ics").onclick=()=>dl("planner-"+stamp()+".ics",new Blob([ics()],{type:"text/calendar"}));
/* KI-Assistent */
function aiPrompt(){
  const t=$("f_title").value.trim(),notes=$("f_notes").value.trim(),have=cklist.map(c=>c.t).filter(Boolean),tags=selTags.join(", "),pv=$("f_proj").value,proj=pv&&pv!=="__new"?pv:"";
  return"Du hilfst einem Paar beim Planen von Aufgaben rund ums Haus. Schreibe auf Deutsch, knapp und praktisch.\nAufgabe: "+t+"\n"+(tags?"Tags: "+tags+"\n":"")+(proj?"Projekt: "+proj+"\n":"")+(notes?"Vorhandene Notizen (nicht wiederholen): "+notes+"\n":"")+(have.length?"Vorhandene Checklistenpunkte (nicht wiederholen): "+have.join("; ")+"\n":"")
   +'Antworte ausschließlich mit einem JSON-Objekt, ohne Erklärung und ohne Code-Block: {"notes":"1 bis 3 kurze Sätze: was ist zu tun, worauf achten","checklist":["3 bis 8 kurze Schritte im Imperativ"]}'}
let aiRes=null,aiHints=[];
async function aiRun(refine){
  if(!$("f_title").value.trim()){toast("Bitte zuerst einen Titel eingeben");$("f_title").focus();return}
  const hint=refine?$("ai_hint").value.trim():"";if(refine&&!hint){$("ai_hint").focus();toast("Schreib kurz, was anders sein soll");return}
  if(!refine)aiHints=[];else aiHints.push(hint.slice(0,300));
  let prompt=aiPrompt();
  if(refine&&aiRes)prompt=prompt.replace("Antworte ausschließlich","Bisheriger Vorschlag: "+JSON.stringify({notes:aiRes.notes,checklist:aiRes.items})+"\nHinweise des Nutzers dazu (unbedingt beachten, betreffende Schritte weglassen oder ändern): "+aiHints.join(" | ")+"\nErstelle einen angepassten Vorschlag. Antworte ausschließlich");
  const b=refine?$("ai_re"):$("ai_btn"),old=b.textContent;b.disabled=true;b.textContent=refine?"Passe an …":"KI denkt nach …";
  try{const r=await aiJson(prompt),notes=String(r&&r.notes||"").trim().slice(0,1000),items=(Array.isArray(r&&r.checklist)?r.checklist:[]).map(x=>String(x).trim().slice(0,120)).filter(Boolean).slice(0,10);
    if(!notes&&!items.length)throw new Error("Keine brauchbare Antwort");aiRes={notes,items};if(refine)$("ai_hint").value="";drawAi()}
  catch(e){toast("KI nicht erreichbar: "+((e&&(e.message||e.code))||"unbekannt"))}
  b.disabled=false;b.textContent=old}
function drawAi(){
  const box=$("ai_box");if(!aiRes){box.style.display="none";return}box.style.display="";
  $("ai_notes").textContent=aiRes.notes;
  $("ai_items").innerHTML=aiRes.items.map((x,i)=>`<label class="aii"><input type="checkbox" data-ai="${i}" checked><span>${esc(x)}</span></label>`).join("")}
$("ai_btn").onclick=()=>aiRun(false);
$("ai_re").onclick=()=>aiRun(true);
$("ai_hint").addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();aiRun(true)}});
$("ai_no").onclick=()=>{aiRes=null;aiHints=[];$("ai_hint").value="";drawAi()};
$("ai_ok").onclick=()=>{
  if(!aiRes)return;const on=[...document.querySelectorAll("#ai_items input:checked")].map(i=>aiRes.items[+i.dataset.ai]);
  if(aiRes.notes){const n=$("f_notes");n.value=(n.value.trim()?n.value.trim()+"\n\n":"")+aiRes.notes}
  on.forEach(x=>cklist.push({t:x,d:false}));drawCk();aiRes=null;drawAi()};
