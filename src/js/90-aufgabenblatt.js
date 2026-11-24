/* Ressource: Auswahl oder Freitext */
/* Verantwortlich: Mehrfachauswahl */
let selWho=[];
function drawWho(){
  const names=[...new Set([...allWho(),...selWho])];
  $("f_whoseg").innerHTML=names.map(n=>`<button type="button" class="wch ${avc(n)}${selWho.includes(n)?" on":""}" data-w="${esc(n)}" aria-pressed="${selWho.includes(n)}"><i class="av ${avc(n)}">${esc(n[0].toUpperCase())}</i>${esc(n)}</button>`).join("")+'<button type="button" class="wch wadd" data-w="__add"><svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>Person</button>';
}
function addWho(){const v=$("f_who").value.replace(/,/g," ").trim().slice(0,30);$("f_who").value="";$("f_who").style.display="none";if(v&&!selWho.some(x=>x.toLowerCase()===v.toLowerCase())){const ex=allWho().find(x=>x.toLowerCase()===v.toLowerCase());selWho.push(ex||v)}drawWho()}
$("f_whoseg").onclick=e=>{const b=e.target.closest("[data-w]");if(!b)return;const v=b.dataset.w;
  if(v==="__add"){$("f_who").style.display="";$("f_who").focus();return}
  selWho=selWho.includes(v)?selWho.filter(x=>x!==v):[...selWho,v];drawWho()};
$("f_who").onkeydown=e=>{if(e.key==="Enter"){e.preventDefault();e.stopPropagation();addWho()}};
$("f_who").onblur=()=>{if($("f_who").value.trim())addWho()};
$("f_stseg").onclick=e=>{const b=e.target.closest("[data-s]");if(!b)return;$("f_status").value=b.dataset.s;syncSeg()};
const PRN={0:"",1:"Prio 1: zuerst erledigen, dringend oder wichtig",2:"Prio 2: normal, als Nächstes",3:"Prio 3: wenn Zeit ist"};
$("f_prseg").onclick=e=>{const b=e.target.closest("[data-p]");if(!b)return;$("f_prio").value=b.dataset.p;syncPr()};
function syncPr(){const v=$("f_prio").value;document.querySelectorAll("#f_prseg button").forEach(b=>b.classList.toggle("on",b.dataset.p===v));$("f_prh").textContent=PRN[v]||""}
function syncSeg(){document.querySelectorAll("#f_stseg button").forEach(b=>b.classList.toggle("on",b.dataset.s===$("f_status").value))}
/* Zeitraum: Kalender mit einem Zug für Start und Ende */
const MONS=["Jan.","Feb.","März","Apr.","Mai","Juni","Juli","Aug.","Sept.","Okt.","Nov.","Dez."];
let rpM=new Date(),rpStep=0;
const tdy=()=>{const d=new Date();return iso(new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate())))};
const fdd=k=>{const d=fromDn(dn(k));return d.getUTCDate()+". "+MONS[d.getUTCMonth()]+(d.getUTCFullYear()!==new Date().getFullYear()?" "+d.getUTCFullYear():"")};
function drawRange(){
  const s0=$("f_start").value,e0=$("f_end").value||s0,one=s0===e0,n=dn(e0)-dn(s0)+1;
  $("f_rtxt").textContent=s0?(one?fdd(s0):fdd(s0)+" – "+fdd(e0)):"Zeitraum wählen";
  $("f_rlen").textContent=s0?($("f_ms").checked?"Meilenstein":n+(n===1?" Tag":" Tage")):"";
}
function rpOpen(on){const p=$("f_rp");p.hidden=!on;$("f_range").setAttribute("aria-expanded",on);
  if(on){rpM=fromDn(dn($("f_start").value||tdy()));rpM=new Date(Date.UTC(rpM.getUTCFullYear(),rpM.getUTCMonth(),1));rpStep=0;drawRp();p.scrollIntoView({block:"nearest",behavior:"smooth"})}}
function drawRp(){
  const s0=$("f_start").value,e0=$("f_end").value||s0,y=rpM.getUTCFullYear(),m=rpM.getUTCMonth(),off=(new Date(Date.UTC(y,m,1)).getUTCDay()+6)%7,days=new Date(Date.UTC(y,m+1,0)).getUTCDate(),today=tdy();
  let h=`<div class="rph"><button type="button" data-rp="-1" aria-label="Vorheriger Monat"><svg viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6"/></svg></button><b>${MONL[m]} ${y}</b><button type="button" data-rp="1" aria-label="Nächster Monat"><svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg></button></div><div class="rpw">${["Mo","Di","Mi","Do","Fr","Sa","So"].map(x=>`<span>${x}</span>`).join("")}</div><div class="rpg">`+"<span></span>".repeat(off);
  for(let d=1;d<=days;d++){const k=iso(new Date(Date.UTC(y,m,d)));h+=`<button type="button" data-d="${k}" class="${k===today?"rtd ":""}${k>=s0&&k<=e0?"rin ":""}${k===s0?"rst ":""}${k===e0?"ren":""}">${d}</button>`}
  h+=`</div><div class="rpq"><button type="button" data-q="today">Heute</button><button type="button" data-q="week">Diese Woche</button><button type="button" data-q="next">Nächste Woche</button></div><div class="rpn">${rpStep?"Jetzt das Ende antippen":"Start antippen, dann Ende"}</div>`;
  $("f_rp").innerHTML=h;
}
function setRange(a,b){$("f_start").value=a;$("f_end").value=b;if(a===b&&!$("f_ms").checked){}drawRange()}
$("f_range").onclick=()=>rpOpen($("f_rp").hidden);
$("f_rp").onclick=e=>{
  const nav=e.target.closest("[data-rp]");if(nav){rpM=new Date(Date.UTC(rpM.getUTCFullYear(),rpM.getUTCMonth()+ +nav.dataset.rp,1));drawRp();return}
  const q=e.target.closest("[data-q]");if(q){const t0=dn(tdy()),mo=t0-((fromDn(t0).getUTCDay()+6)%7),a=q.dataset.q==="today"?t0:q.dataset.q==="week"?mo:mo+7;
    setRange(iso(fromDn(a)),iso(fromDn(q.dataset.q==="today"?a:a+6)));if($("f_ms").checked)setRange($("f_start").value,$("f_start").value);rpOpen(false);return}
  const d=e.target.closest("[data-d]");if(!d)return;const k=d.dataset.d;
  if($("f_ms").checked){setRange(k,k);rpOpen(false);return}
  if(!rpStep){setRange(k,k);rpStep=1;drawRp()}
  else{const s0=$("f_start").value;k<s0?setRange(k,s0):setRange(s0,k);rpStep=0;rpOpen(false)}};
$("f_rp").onmouseover=e=>{if(!rpStep)return;const d=e.target.closest("[data-d]");if(!d)return;const s0=$("f_start").value,k=d.dataset.d;
  document.querySelectorAll("#f_rp [data-d]").forEach(b=>{const x=b.dataset.d;b.classList.toggle("rin",x>=(k<s0?k:s0)&&x<=(k<s0?s0:k))})};
/* Gruppen im Dialog: Zusammenfassung rechts, automatisch geöffnet wenn gefüllt */
function sumDlg(){
  const set=(id,t)=>{const e=document.querySelector("#"+id+" summary em");if(e)e.textContent=t||""};
  const ck=cklist.filter(x=>x.t.trim()),dd=ck.filter(x=>x.d).length;set("d_ck",ck.length?dd+"/"+ck.length:"");
  const nd=document.querySelectorAll("#f_deps input:checked").length,r=$("f_rec").value;set("d_pl",[r?"wiederholt":"",nd?nd+" Abhängigkeit"+(nd>1?"en":""):""].filter(Boolean).join(" · "));
  set("f_filesec",(editing&&(editing.files||[]).length)?String(editing.files.length):"");
  set("f_logsec",(editing&&(editing.log||[]).length)?String(editing.log.length):"");
}
$("dlg").addEventListener("input",sumDlg);$("dlg").addEventListener("click",()=>setTimeout(sumDlg,0));
/* Checkliste */
let cklist=[];
function drawCk(){const box=$("f_ck");box.innerHTML=cklist.map((c,i)=>`<div class="ck" data-ck="${i}">${cklist.length>1?`<button class="grip" type="button" aria-label="Ziehen zum Verschieben" tabindex="-1"><svg viewBox="0 0 24 24"><circle cx="9" cy="7" r="1.5"/><circle cx="15" cy="7" r="1.5"/><circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/><circle cx="9" cy="17" r="1.5"/><circle cx="15" cy="17" r="1.5"/></svg></button>`:""}<input type="checkbox" data-i="${i}" ${c.d?"checked":""}><input class="ct" data-i="${i}" value="${esc(c.t)}" placeholder="Punkt"><button class="x" type="button" data-r="${i}">✕</button></div>`).join("");
  box.querySelectorAll("input[type=checkbox]").forEach(b=>b.onchange=()=>{cklist[b.dataset.i].d=b.checked});
  box.querySelectorAll(".ct").forEach(b=>{b.oninput=()=>{cklist[b.dataset.i].t=b.value};b.onkeydown=e=>{if(e.key==="Enter"){e.preventDefault();cklist.splice(+b.dataset.i+1,0,{t:"",d:false});drawCk();box.querySelectorAll(".ct")[+b.dataset.i+1].focus()}}});
  box.querySelectorAll("[data-r]").forEach(b=>b.onclick=()=>{cklist.splice(+b.dataset.r,1);drawCk()});
  box.querySelectorAll(".grip").forEach(g=>g.onpointerdown=ckDrag)}
/* Checkliste umsortieren: Griff gedrückt halten und ziehen */
function ckDrag(e){
  if(e.button>0)return;e.preventDefault();
  const g=e.currentTarget,row=g.closest(".ck"),box=$("f_ck");let y0=e.clientY,moved=false;
  g.setPointerCapture(e.pointerId);row.classList.add("drag");hap(10);
  const mv=ev=>{let dy=ev.clientY-y0;
    const prev=row.previousElementSibling,next=row.nextElementSibling;
    if(prev&&dy<-prev.offsetHeight/2){box.insertBefore(row,prev);y0-=prev.offsetHeight+parseFloat(getComputedStyle(prev).marginBottom);dy=ev.clientY-y0;moved=true;hap(5)}
    else if(next&&dy>next.offsetHeight/2){box.insertBefore(next,row);y0+=next.offsetHeight+parseFloat(getComputedStyle(next).marginBottom);dy=ev.clientY-y0;moved=true;hap(5)}
    row.style.transform=`translateY(${dy}px)`};
  const up=()=>{g.removeEventListener("pointermove",mv);g.removeEventListener("pointerup",up);g.removeEventListener("pointercancel",up);
    row.classList.remove("drag");row.style.transform="";
    if(moved){const order=[...box.querySelectorAll(".ck")].map(r=>+r.dataset.ck);cklist=order.map(i=>cklist[i]);drawCk()}};
  g.addEventListener("pointermove",mv);g.addEventListener("pointerup",up);g.addEventListener("pointercancel",up)}
$("ck_add").onclick=()=>{cklist.push({t:"",d:false});drawCk();const a=$("f_ck").querySelectorAll(".ct");a[a.length-1].focus()};

/* Dialog */
const blankTask=()=>({title:"",tags:ftags.size===1&&!ftags.has("__none")?[...ftags]:[],who:"",proj:fprojs.size===1&&!fprojs.has("__none")?[...fprojs][0]:"",status:"todo",start:tdy(),end:iso(fromDn(dn(tdy())+6)),deps:[],notes:""});
/* Öffnet das Aufgabenblatt: id = bearbeiten, sonst neu; tpl = neue Aufgabe mit diesen Werten (Vorschlag aus der Schnelleingabe) */
function openDlg(id,tpl){
  editing=id?byId(id):null;const t=editing||tpl||blankTask();
  $("dt").textContent=editing?"Aufgabe bearbeiten":"Neue Aufgabe";
  fillDlg(t);
  $("b_del").style.display=editing?"":"none";
  $("dlg").showModal();dlgSnap=dlgState();$("dlg").scrollTop=0;if(!editing&&!tpl)setTimeout(()=>$("f_title").focus(),50);
}
function fillDlg(t){
  $("f_title").value=t.title;$("f_qp").innerHTML="";$("f_sug").innerHTML="";selTags=[...tgs(t)];regDraft=reg.map(x=>({...x}));colorFor=null;$("f_tagin").value="";drawTags();selWho=wl(t);$("f_who").value="";$("f_who").style.display="none";drawWho();$("f_status").value=t.status;syncSeg();$("f_prio").value=t.prio||0;syncPr();
  $("f_start").value=t.start;$("f_end").value=t.end;initExtra(t);rpOpen(false);drawRange();$("f_notes").value=t.notes||"";
  const others=tasks.filter(x=>!editing||x.id!==editing.id);
  drawDeps(others,t.deps||[]);
  cklist=(t.checklist||[]).map(x=>({...x}));drawCk();drawLog();drawFiles();aiRes=null;drawAi();$("ai_row").style.display=aiAvail()?"":"none";
}
/* 1.33: Vorschläge aus früheren Aufgaben (wie Apple Kalender). Treffer: Titel beginnt mit dem Getippten, ab 3 Zeichen auch ein Wort darin.
   Gleiche Titel nur einmal (die jüngste Aufgabe). Auswahl übernimmt alle Einstellungen außer Datum, Abhängigkeiten, Verlauf und Dateien. */
const SUGI='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 12a8.5 8.5 0 1 0 2.6-6.1L3.5 8.5M3.5 3.5v5h5M12 7.5V12l3 2"/></svg>';
function sugFind(text){
  const q=parseQuick(text),base=String(q.found&&q.title?q.title:text).trim().toLowerCase();if(base.length<2)return[];
  const best=new Map();
  for(const t of RAW){if(t.del||!t.title)continue;const k=t.title.trim().toLowerCase();
    const r=k.startsWith(base)?0:base.length>=3&&k.split(/[\s\-\/]+/).some(w=>w.startsWith(base))?1:-1;if(r<0)continue;
    const o=best.get(k);if(!o||dn(t.start)>dn(o.t.start))best.set(k,{t,r})}
  return[...best.values()].sort((a,b)=>a.r-b.r||dn(b.t.start)-dn(a.t.start)).slice(0,4).map(x=>x.t)}
function sugMeta(t){const d=dn(t.end)-dn(t.start)+1,ck=(t.checklist||[]).length;
  return[t.proj,...tgs(t),t.who,t.ms?"Meilenstein":d>1?d+" Tage":"",ck?ck+(ck===1?" Punkt":" Punkte"):"",t.rec?"wiederholt sich":"","zuletzt "+fd(t.start)].filter(Boolean).join(" · ")}
const sugHtml=L=>L.map(t=>`<button type="button" class="vsg" data-sid="${t.id}">${SUGI}<span><b>${esc(t.title)}</b><small>${esc(sugMeta(t))}</small></span></button>`).join("");
/* Neue Aufgabe aus einer alten: Getipptes (Datum, #Tag, @Person, +Projekt, !Prio) hat Vorrang, Dauer bleibt gleich */
function fromTemplate(src,text,fb){
  const q=text?parseQuick(text):null,qd=q&&qDates(q),len=Math.max(0,dn(src.end)-dn(src.start)),start=qd?qd[0]:fb||tdy();
  const end=src.ms?start:qd&&qd[0]!==qd[1]?qd[1]:iso(fromDn(dn(start)+len));
  return{title:src.title,tags:[...new Set([...tgs(src),...(q?q.tags:[])])],proj:(q&&q.proj)||src.proj||"",who:q&&q.who.length?q.who.join(", "):src.who||"",
    prio:(q&&q.prio)||src.prio||0,status:"todo",ms:!!src.ms,rec:src.rec?{...src.rec}:null,start,end,notes:src.notes||"",deps:[],checklist:(src.checklist||[]).map(c=>({...c,d:false}))}}
function sugApply(id){
  const src=byId(id);if(!src||editing)return;const prev={title:$("f_title").value,start:$("f_start").value,end:$("f_end").value};
  fillDlg(fromTemplate(src,prev.title,prev.start));$("f_title").blur();hap(8);
  toast("„"+src.title+"“ übernommen",()=>{fillDlg({...blankTask(),...prev});$("f_title").focus()},"Rückgängig",6000)}
function sugOpen(id){
  const src=byId(id),qa=$("qadd");if(!src)return;const text=qa?qa.value:"";
  if(qa){qa.value="";qa.blur()}$("qprev").innerHTML="";$("qsug").innerHTML="";hap(8);openDlg(null,fromTemplate(src,text))}
$("f_title").addEventListener("input",()=>{$("f_sug").innerHTML=editing?"":sugHtml(sugFind($("f_title").value))});
$("f_sug").addEventListener("click",e=>{const b=e.target.closest("[data-sid]");if(b)sugApply(b.dataset.sid)});
const sugDown=(e,box)=>{if(e.key==="ArrowDown"){const b=box&&box.querySelector("button");if(b){e.preventDefault();b.focus()}}};
$("f_title").addEventListener("keydown",e=>sugDown(e,$("f_sug")));
/* Tippen außerhalb von Titel und Vorschlägen blendet die Vorschläge aus (wie beim Verlassen des Feldes) */
document.addEventListener("pointerdown",e=>{const t=e.target;if(!t.closest)return;
  if(!t.closest("#f_title,#f_sug"))$("f_sug").innerHTML="";
  const qs=$("qsug");if(qs&&!t.closest(".qadd"))qs.innerHTML=""},{passive:true});
/* Abhängigkeiten: gewählte oben, dann offene nach Fälligkeit, erledigte zuletzt; Suche über Titel, Projekt, Tags, Person */
function drawDeps(others,chosen){
  const me=editing&&editing.id,rank=x=>chosen.includes(x.id)?0:x.status==="done"?2:1;
  const L=[...others].sort((a,b)=>rank(a)-rank(b)||dn(a.end)-dn(b.end));
  $("f_depq").value="";
  $("f_deps").innerHTML=L.length?L.map(x=>{const cyc=me&&(x.deps||[]).includes(me),meta=[x.proj,...tgs(x),x.who,x.status==="done"?"erledigt":"bis "+fd(x.end)].filter(Boolean);
    const q=[x.title,x.proj,...tgs(x),x.who].filter(Boolean).join(" ").toLowerCase();
    return`<label data-q="${esc(q)}"${cyc?' class="cyc"':""}><input type="checkbox" value="${x.id}" ${chosen.includes(x.id)?"checked":""}${cyc?" disabled":""}><span class="dl"><b>${esc(x.title)}</b><small>${cyc?"hängt von dieser Aufgabe ab":meta.map(esc).join(" · ")}</small></span></label>`}).join(""):'<span class="dnone">Noch keine anderen Aufgaben.</span>';
  filterDeps()}
function filterDeps(){
  const w=$("f_depq").value.toLowerCase().trim().split(/\s+/).filter(Boolean),all=[...document.querySelectorAll("#f_deps label")];let shown=0,sel=0;
  all.forEach(l=>{const c=l.querySelector("input").checked,ok=c||w.every(x=>l.dataset.q.includes(x));l.hidden=!ok;if(ok)shown++;if(c)sel++});
  $("f_depc").textContent=!all.length?"":w.length?(shown-sel>0||sel?`${shown} von ${all.length}`+(sel?` · ${sel} gewählt`:""):"Nichts gefunden"):(sel?`${sel} gewählt`:"")}
$("f_depq").addEventListener("input",filterDeps);
$("f_deps").addEventListener("change",filterDeps);
function syncMs(){if($("f_ms").checked)$("f_end").value=$("f_start").value;drawRange()}
function initExtra(t){
  const pn=allProjs();$("f_proj").innerHTML='<option value="">Kein Projekt</option>'+pn.map(n=>`<option>${esc(n)}</option>`).join("")+'<option value="__new">Neues Projekt …</option>';
  $("f_proj").value=t.proj||"";tintProj();$("f_projnew").value="";$("f_projnew").style.display="none";
  $("f_rec").value=t.rec?t.rec.n+t.rec.u:"";$("f_rechint").style.display=t.rec?"":"none";
  $("f_ms").checked=!!t.ms;syncMs()}
$("f_ms").onchange=syncMs;
$("f_rec").onchange=()=>{$("f_rechint").style.display=$("f_rec").value?"":"none"};
function tintProj(){const v=$("f_proj").value;$("f_proj").style.setProperty("--tc",v&&v!=="__new"?pcol(v):"var(--line2)")}
$("f_proj").onchange=()=>{tintProj();const n=$("f_proj").value==="__new";$("f_projnew").style.display=n?"":"none";if(n)$("f_projnew").focus()};
$("f_title").addEventListener("input",()=>{$("f_qp").innerHTML=qChips(parseQuick($("f_title").value))});
$("b_save").onclick=async()=>{
  const q=parseQuick($("f_title").value),prev=editing?{...editing}:null;
  const title=(q.found&&q.title?q.title:$("f_title").value.trim());if(!title){$("f_title").focus();return}
  if($("f_tagin").value.trim())addTag($("f_tagin").value);if($("f_who").value.trim())addWho();
  let s=$("f_start").value,e=$("f_end").value;if(!s)s=iso(new Date());const ms=$("f_ms").checked;if(!e||dn(e)<dn(s)||ms)e=s;
  let proj=$("f_proj").value;if(proj==="__new")proj=$("f_projnew").value.trim().slice(0,30);
  {const ex=allProjs().find(x=>x.toLowerCase()===proj.toLowerCase());if(ex)proj=ex}
  if(q.found){q.tags.forEach(n=>{if(!selTags.includes(n))selTags.push(n)});q.who.forEach(n=>{if(!selWho.includes(n))selWho.push(n)});if(q.proj)proj=q.proj;const qd=qDates(q);if(qd&&!ms){s=qd[0];e=qd[1]}else if(qd){s=e=qd[1]}}
  const rm=/^(\d+)([dwmy])$/.exec($("f_rec").value),rec=rm?{n:+rm[1],u:rm[2]}:null;
  const t={...(editing||{}),id:editing?editing.id:newId(),title,tags:selTags.slice(),area:selTags[0]||"",proj,rec,ms,who:selWho.join(", "),
    status:$("f_status").value,prio:q.prio||+$("f_prio").value||0,start:s,end:e,notes:$("f_notes").value,checklist:cklist.filter(x=>x.t.trim()),deps:[...document.querySelectorAll("#f_deps input:checked")].map(i=>i.value)};
  $("dlg").close();
  let sp=null;if(t.status==="done"&&t.rec&&!t.spawned){sp=nextOcc(t);t.spawned=sp.id}
  {const r=regDraft;if(r){if(proj&&!r.some(x=>x.p&&x.n===proj))r.push({n:proj,c:nextPColor(),p:1});selTags.forEach(n=>{if(!r.some(x=>!x.p&&x.n===n))r.push({n,c:colorKey(n)})});if(JSON.stringify(r)!==JSON.stringify(reg))saveReg(r)}}
  if(editing)t.log=diffLog(editing,t);
  await saveTask(t,{check:true});if(sp)await saveTask(sp);
  if(prev)toast("Änderungen gespeichert",async()=>{const c=byId(prev.id);await saveTask({...prev,v:c?c.v:prev.v})});
  else toast("„"+t.title+"“ angelegt",()=>delTask(t.id));
};
$("b_cancel").onclick=()=>$("dlg").close();
$("dlg").addEventListener("close",()=>{regDraft=null;colorFor=null});
$("b_del").onclick=()=>{const t=editing;$("dlg").close();trash(t.id)};
