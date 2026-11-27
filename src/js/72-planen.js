/* 1.46: Planen (im Kalender umschaltbar „Monat | Planen“).
   Zeitraum 1, 2 oder 5 Wochen ab Montag, links/oben der Sammelkorb (Aufgaben ohne festen Tag) und „Liegen geblieben“.
   Verschieben: am Griff ziehen (Maus, Finger, Stift) oder Griff antippen und dann den Ziel-Tag antippen.
   Eine Aufgabe steht an ihrem Starttag; beim Verschieben bleibt die Dauer gleich. */
let calMode=null,planFrom=null,planPick=null,planKeep=null,planDay=null;
const PLAN_W=[1,2,5],WDS=["Mo","Di","Mi","Do","Fr","Sa","So"];
const planWeeks=()=>{const w=+(prefGet("planw")||2);return PLAN_W.includes(w)?w:2};
const calModeNow=()=>calMode||(prefGet("calm")==="plan"?"plan":"monat");
const monOf=d=>d-(fromDn(d).getUTCDay()+6)%7;
const pLabel=d=>WDS[(fromDn(d).getUTCDay()+6)%7]+" "+fd(iso(fromDn(d)));
const inboxL=()=>RAW.filter(t=>t.inbox&&!t.del&&!t.arch&&t.status!=="done");
function calSwitch(){const m=calModeNow();return`<div class="calmode hpick" role="tablist" aria-label="Ansicht">${[["monat","Monat"],["plan","Planen"]].map(([k,n])=>`<button type="button" role="tab" data-calm="${k}" class="${m===k?"on":""}" aria-selected="${m===k}">${n}</button>`).join("")}</div>`}
function pChip(t,i){const meta=[t.who,...tgs(t).slice(0,1)].filter(Boolean),dur=dn(t.end)-dn(t.start);
  return`<div class="pch${t.status==="done"?" done":""}${isFail(t)?" fail":""}${planPick===t.id?" picked":""}${t.prio?" p"+t.prio:""}" data-id="${t.id}" style="--i:${Math.min(i,8)}">`
   +`<span class="pgrip" data-pgrip="${t.id}" role="button" tabindex="0" aria-label="„${esc(t.title)}“ verschieben"><svg viewBox="0 0 24 24"><circle cx="9" cy="6" r="1.6"/><circle cx="15" cy="6" r="1.6"/><circle cx="9" cy="12" r="1.6"/><circle cx="15" cy="12" r="1.6"/><circle cx="9" cy="18" r="1.6"/><circle cx="15" cy="18" r="1.6"/></svg></span>`
   +`<span class="pct"><b>${esc(t.title)}</b>${meta.length||dur>0||t.rec?`<small>${[...meta.map(esc),dur>0?(dur+1)+" Tage":"",t.rec?"↻":""].filter(Boolean).join(" · ")}</small>`:""}</span></div>`}
const pSort=(a,b)=>(a.status==="done")-(b.status==="done")||(a.prio||9)-(b.prio||9)||a.title.localeCompare(b.title,"de");
function plan(list){
  const T=today(),W=planWeeks();if(planFrom===null)planFrom=monOf(T);const from=planFrom,to=from+W*7-1;
  const box=inboxL().filter(t=>list.some(x=>x.id===t.id)||!fActive()).sort(pSort),late=list.filter(t=>!t.inbox&&isLate(t)).sort((a,b)=>dn(a.end)-dn(b.end));
  /* Tag der Aufgabe: ihr Start; läuft sie schon vorher und ist noch offen, steht sie am ersten sichtbaren Tag */
  const at=new Map();for(const t of list){if(t.inbox||isLate(t))continue;const s=dn(t.start),e=dn(t.end);
    const d=s>=from?s:(t.status!=="done"&&e>=from?Math.max(from,T):null);if(d!==null&&d<=to){if(!at.has(d))at.set(d,[]);at.get(d).push(t)}}
  const last=fromDn(to),first=fromDn(from);
  const lbl=`${first.getUTCDate()}. ${MONL[first.getUTCMonth()]} – ${last.getUTCDate()}. ${MONL[last.getUTCMonth()]}`;
  let weeks="";for(let w=0;w<W;w++){let days="";for(let i=0;i<7;i++){const d=from+w*7+i,L=(at.get(d)||[]).sort(pSort),open=L.filter(t=>t.status!=="done").length,k=iso(fromDn(d));
      days+=`<section class="pday${i>4?" we":""}${d===T?" today":""}${d<T?" past":""}" data-pday="${k}" aria-label="${pLabel(d)}, ${open} offen"><header><b>${WDS[i]}</b><span>${fromDn(d).getUTCDate()}.${fromDn(d).getUTCMonth()+1}.</span>${open?`<em class="pload l${Math.min(open,5)}">${open}</em>`:""}</header>`
        +`<div class="pchips">${L.map(pChip).join("")}</div>`
        +(planDay===k?`<input class="pin" data-pin="${k}" placeholder="Aufgabe für ${pLabel(d)}" enterkeyhint="done" autocomplete="off">`:`<button type="button" class="padd" data-padd="${k}" aria-label="Aufgabe am ${pLabel(d)} anlegen">+</button>`)+`</section>`}
    weeks+=`<div class="pweek"><h3 class="pwk">KW ${kw(from+w*7)}</h3>${days}</div>`}
  return calSwitch()+`<div class="calbar pbar"><button class="cnav" data-pnav="-1" aria-label="Eine Woche zurück">‹</button><h2>${lbl}</h2><button class="cnav" data-pnav="1" aria-label="Eine Woche vor">›</button><button class="cnav t" data-pnav="0">Heute</button>`
   +`<div class="hpick pw">${PLAN_W.map(n=>`<button type="button" data-planw="${n}" class="${n===W?"on":""}">${n} ${n===1?"Woche":"Wochen"}</button>`).join("")}</div></div>`
   +(planPick?`<div class="phint" role="status">Ziel antippen: einen Tag oder den Sammelkorb. <button type="button" class="btn ghost sm" data-pcancel>Abbrechen</button></div>`:"")
   +`<div class="plan${planPick?" picking":""}"><aside class="pbox" data-pbox="1" aria-label="Sammelkorb"><h3>Sammelkorb <em>${box.length}</em></h3>`
   +`<input class="pin" data-pin="box" placeholder="Neue Aufgabe ohne Tag, Enter" enterkeyhint="done" autocomplete="off">`
   +`<div class="pchips">${box.length?box.map(pChip).join(""):`<p class="pnone">Hier sammeln, was noch keinen Tag hat. Dann auf einen Tag ziehen.</p>`}</div>`
   +(late.length?`<h3 class="plate">Liegen geblieben <em>${late.length}</em></h3><div class="pchips">${late.map(pChip).join("")}</div>`:"")
   +`</aside><div class="pgrid">${weeks}</div></div>`}
/* Kalenderwoche nach ISO: zählt nach dem Donnerstag der Woche */
function kw(d){const th=monOf(d)+3,y=fromDn(th).getUTCFullYear();return 1+Math.floor((th-Date.UTC(y,0,1)/864e5)/7)}
const fActive=()=>!!($("fw")&&$("fw").value)||!!($("q")&&$("q").value.trim());

async function planMove(id,target){
  const t=byId(id);if(!t)return;let u;
  if(target==="box"){if(t.inbox)return;u={...t,inbox:true}}
  else{const d=dn(target),dur=Math.max(0,dn(t.end)-dn(t.start));if(!t.inbox&&dn(t.start)===d&&!isLate(t))return;u={...t,start:target,end:iso(fromDn(d+dur))};delete u.inbox}
  u.log=diffLog(t,u);lastMoved=id;await saveTask(u);hap(8);
  toast(`„${t.title}“ → ${target==="box"?"Sammelkorb":pLabel(dn(target))}`,async()=>{const c=byId(id);if(!c)return;const r={...c,start:t.start,end:t.end};if(t.inbox)r.inbox=true;else delete r.inbox;await saveTask(r)})}
async function planAdd(text,k){
  const q=parseQuick(text);if(!q.title)return false;q.title=q.title.charAt(0).toUpperCase()+q.title.slice(1);
  const qd=qDates(q),day=k==="box"?tdy():k,d=qd||[day,day],hw=homeW(),who=q.who.length?q.who:(hw&&hw!=="__all"?[hw]:[]);
  const t={id:newId(),title:q.title.slice(0,200),tags:q.tags,area:q.tags[0]||"",proj:q.proj,who:who.join(", "),status:"todo",prio:q.prio,start:d[0],end:d[1],notes:"",deps:[],checklist:[],ms:false,rec:null};
  if(k==="box"&&!qd)t.inbox=true;
  planKeep={k};await regEnsure(q.tags,q.proj);await saveTask(t);hap(10);return true}

/* Ziehen am Griff: Zeiger festhalten, Geist folgt, Ziel unter dem Finger wird markiert, am Rand scrollt die Seite mit */
let pdr=null;
document.addEventListener("pointerdown",e=>{const g=e.target.closest&&e.target.closest("[data-pgrip]");if(!g||e.button>0)return;e.preventDefault();
  pdr={id:g.dataset.pgrip,x:e.clientX,y:e.clientY,moved:false,src:g.closest(".pch"),ghost:null,over:null,raf:0,vy:0};try{g.setPointerCapture(e.pointerId)}catch(_){}});
document.addEventListener("pointermove",e=>{if(!pdr)return;const dx=e.clientX-pdr.x,dy=e.clientY-pdr.y;
  if(!pdr.moved){if(Math.hypot(dx,dy)<6)return;pdr.moved=true;const r=pdr.src.getBoundingClientRect(),gh=pdr.src.cloneNode(true);gh.className+=" pghost";
    gh.style.width=r.width+"px";gh.style.left=r.left+"px";gh.style.top=r.top+"px";document.body.appendChild(gh);pdr.ghost=gh;pdr.src.classList.add("dragging");document.body.classList.add("pdragging");hap(6)}
  pdr.ghost.style.transform=`translate(${dx}px,${dy}px) rotate(-1.5deg)`;
  const el=document.elementFromPoint(e.clientX,e.clientY),tg=el&&el.closest&&el.closest("[data-pday],[data-pbox]");
  if(tg!==pdr.over){pdr.over&&pdr.over.classList.remove("pover");pdr.over=tg;tg&&tg.classList.add("pover")}
  const m=$("main"),mr=m.getBoundingClientRect(),edge=56;pdr.vy=e.clientY<mr.top+edge?-(mr.top+edge-e.clientY)/3:e.clientY>mr.bottom-edge?(e.clientY-(mr.bottom-edge))/3:0;
  if(pdr.vy&&!pdr.raf){const step=()=>{if(!pdr||!pdr.vy){if(pdr)pdr.raf=0;return}m.scrollTop+=pdr.vy;pdr.raf=requestAnimationFrame(step)};pdr.raf=requestAnimationFrame(step)}});
function pdEnd(drop){const d=pdr;if(!d)return;pdr=null;if(d.raf)cancelAnimationFrame(d.raf);d.ghost&&d.ghost.remove();d.src&&d.src.classList.remove("dragging");document.body.classList.remove("pdragging");d.over&&d.over.classList.remove("pover");
  if(!drop)return;
  if(!d.moved){planPick=planPick===d.id?null:d.id;hap(6);render();return}
  if(d.over){planPick=null;planMove(d.id,d.over.dataset.pday||"box")}}
document.addEventListener("pointerup",()=>pdEnd(true));
document.addEventListener("pointercancel",()=>pdEnd(false));
/* Antippen des Griffs öffnet nicht die Aufgabe */
document.addEventListener("click",e=>{if(e.target.closest&&e.target.closest("[data-pgrip]")){e.stopPropagation();e.preventDefault()}},true);
document.addEventListener("keydown",e=>{const g=e.target.closest&&e.target.closest("[data-pgrip]");if(g&&(e.key==="Enter"||e.key===" ")){e.preventDefault();planPick=planPick===g.dataset.pgrip?null:g.dataset.pgrip;render()}
  if(e.key==="Escape"&&planPick){planPick=null;render()}});
/* Gewählte Aufgabe: Ziel antippen. Läuft vor den Klicks auf Karten (Erfassungsphase), damit kein Blatt aufgeht */
$("main").addEventListener("click",e=>{if(!planPick||e.target.closest("[data-pgrip],[data-pcancel],input"))return;const tg=e.target.closest("[data-pday],[data-pbox]");if(!tg)return;
  e.stopPropagation();e.preventDefault();const id=planPick;planPick=null;planMove(id,tg.dataset.pday||"box")},true);
$("main").addEventListener("click",e=>{
  const cm=e.target.closest("[data-calm]");if(cm){calMode=cm.dataset.calm;prefSet("calm",calMode);planPick=null;render();return}
  const pn=e.target.closest("[data-pnav]");if(pn){const v=+pn.dataset.pnav;planFrom=v?planFrom+7*v:monOf(today());render();return}
  const pw=e.target.closest("[data-planw]");if(pw){prefSet("planw",pw.dataset.planw);render();return}
  if(e.target.closest("[data-pcancel]")){planPick=null;render();return}
  const pa=e.target.closest("[data-padd]");if(pa){planDay=pa.dataset.padd;planKeep={k:planDay};render();return}});
$("main").addEventListener("keydown",async e=>{const i=e.target.closest&&e.target.closest("[data-pin]");if(!i)return;
  if(e.key==="Escape"){planKeep=null;planDay=null;i.blur();render();return}
  if(e.key!=="Enter")return;e.preventDefault();const v=i.value;if(!v.trim()){if(i.dataset.pin!=="box"){planDay=null;render()}return}i.value="";if(!await planAdd(v,i.dataset.pin))i.value=v});
$("main").addEventListener("focusout",e=>{const i=e.target.closest&&e.target.closest("[data-pin]");if(i&&i.dataset.pin!=="box"&&!i.value.trim())setTimeout(()=>{if(planDay===i.dataset.pin&&!(document.activeElement&&document.activeElement.closest&&document.activeElement.closest("[data-pin]"))){planDay=null;render()}},150)});
