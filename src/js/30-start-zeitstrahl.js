/* Startseite, Hilfen, Bewegung */
let lastMoved=null,tt,enterT;
const greet=()=>{const h=new Date().getHours();return h<5?"Gute Nacht":h<11?"Guten Morgen":h<17?"Guten Tag":"Guten Abend"};
const reduced=()=>matchMedia("(prefers-reduced-motion:reduce)").matches;
/* 1.33: Ist ein Blatt offen, macht es den Rest der Seite unbedienbar (auch den Hinweis). Darum hängt der Hinweis dann im obersten Blatt
   und wandert beim Schließen zurück; als Popover liegt er trotzdem über allem. */
function toastHost(el){let ds=[...document.querySelectorAll("dialog[open]")];try{ds=ds.filter(d=>d.matches(":modal"))}catch(_){}
  const h=ds.length?ds[ds.length-1]:document.body;if(el.parentNode!==h){try{el.hidePopover()}catch(_){}h.appendChild(el)}}
document.addEventListener("close",e=>{const el=$("toast");if(e.target.tagName!=="DIALOG"||!e.target.contains(el))return;
  try{el.hidePopover()}catch(_){}document.body.appendChild(el);if(el.classList.contains("on"))try{el.showPopover()}catch(_){}},true);
function toast(msg,undo,label,ms){const el=$("toast");el.innerHTML="<span></span>"+(undo?"<button>"+(label||"Rückgängig")+"</button>":"");el.firstChild.textContent=msg;if(undo)el.querySelector("button").onclick=()=>{undo();el.classList.remove("on")};toastHost(el);if(el.showPopover){if(!el.hasAttribute("popover"))el.setAttribute("popover","manual");try{el.hidePopover()}catch(_){}try{el.showPopover()}catch(_){}}el.classList.add("on");clearTimeout(tt);tt=setTimeout(()=>el.classList.remove("on"),ms||4500)}
async function advance(id){
  const t=byId(id);if(!t)return;const prev=t.status,pf=isFail(t),next=NEXT[prev];hap(8);lastMoved=id;
  const sp=await setStatus(t,next);
  toast("„"+t.title+"“: "+ST[next]+(sp?" · nächste am "+fd(sp.start):""),async()=>{const c=byId(id);if(c){lastMoved=id;await saveTask({...c,status:prev,fail:pf,spawned:sp?"":c.spawned});if(sp)delTask(sp.id)}})}
/* 1.42: Nicht geschafft (z. B. tägliche Aufgabe heute nicht machbar). Auf der Startseite gibt es dafür einmal groß „BUSTED!“. */
async function failTask(id){
  const t=byId(id);if(!t||t.status==="done")return;const prev=t.status,onHome=view==="home";hap(20);lastMoved=id;
  const sp=await setStatus(t,"fail");if(onHome)busted(t);
  toast("„"+t.title+"“: Nicht geschafft"+(sp?" · nächste am "+fd(sp.start):""),async()=>{const c=byId(id);if(c){lastMoved=id;await saveTask({...c,status:prev,fail:false,spawned:sp?"":c.spawned});if(sp)delTask(sp.id)}})}
/* Wiederholung, Meilenstein */
const RECI='<svg class="mi" viewBox="0 0 24 24" aria-label="Wiederholt sich"><path d="M4 12a8 8 0 0 1 14-5.3L20 9M20 4v5h-5M20 12a8 8 0 0 1-14 5.3L4 15M4 20v-5h5"/></svg>';
const MSI='<svg class="mi" viewBox="0 0 24 24" aria-label="Meilenstein"><path d="M12 3l9 9-9 9-9-9z"/></svg>';
const dr=t=>t.ms?fd(t.start):`${fd(t.start)}–${fd(t.end)}`;
const newId=()=>"t"+Date.now().toString(36)+Math.random().toString(36).slice(2,5);
/* 1.34: Wiederholung. rec={n, u:"d"|"w"|"m"|"y", wd:[0..6] nur bei w (0 = Sonntag), mw:"nth" nur bei m (z. B. 2. Dienstag, 5 = letzter),
   until:"JJJJ-MM-TT" (letzter möglicher Beginn)}. Alte Einträge {n,u} gelten unverändert. */
const WDLONG=["Sonntag","Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag"];
const wdOf=d=>fromDn(dn(d)).getUTCDay(),mo=k=>(k+6)%7;
function nthOf(d){const dt=fromDn(dn(d)),day=dt.getUTCDate(),last=new Date(Date.UTC(dt.getUTCFullYear(),dt.getUTCMonth()+1,0)).getUTCDate();return day+7>last?5:Math.ceil(day/7)}
function addInterval(d,r){
  const dt=fromDn(dn(d));
  if(r.u==="d")dt.setUTCDate(dt.getUTCDate()+r.n);
  else if(r.u==="w"){const wd=(r.wd||[]).slice().sort((a,b)=>mo(a)-mo(b)),cur=mo(dt.getUTCDay());
    if(!wd.length)dt.setUTCDate(dt.getUTCDate()+7*r.n);
    else{const later=wd.find(x=>mo(x)>cur);dt.setUTCDate(dt.getUTCDate()+(later!==undefined?mo(later)-cur:7*r.n-cur+mo(wd[0])))}}
  else if(r.u==="m"&&r.mw==="nth"){const k=nthOf(d),w=dt.getUTCDay();dt.setUTCDate(1);dt.setUTCMonth(dt.getUTCMonth()+r.n);
    const y=dt.getUTCFullYear(),m=dt.getUTCMonth(),last=new Date(Date.UTC(y,m+1,0)).getUTCDate();let day=(w-dt.getUTCDay()+7)%7+1+7*(k-1);
    if(k===5||day>last){day=(w-dt.getUTCDay()+7)%7+1;while(day+7<=last)day+=7}dt.setUTCDate(day)}
  else{const m=r.u==="y"?r.n*12:r.n,day=dt.getUTCDate();dt.setUTCDate(1);dt.setUTCMonth(dt.getUTCMonth()+m);dt.setUTCDate(Math.min(day,new Date(Date.UTC(dt.getUTCFullYear(),dt.getUTCMonth()+1,0)).getUTCDate()))}
  return iso(dt)}
function nextOcc(t){
  const len=dn(t.end)-dn(t.start);let s=t.start,e=t.end,g=0;
  do{s=addInterval(s,t.rec);e=iso(fromDn(dn(s)+len))}while(dn(e)<today()&&++g<500);
  if(t.rec.until&&dn(s)>dn(t.rec.until))return null;
  return{...t,id:newId(),status:"todo",start:s,end:e,checklist:(t.checklist||[]).map(c=>({...c,d:false})),deps:[],spawned:""}}
/* Wiederholung in Worten, z. B. „Alle 2 Wochen am Di und Do“ */
function recText(r,start){if(!r)return"";const n=r.n||1,list=a=>a.length>1?a.slice(0,-1).join(", ")+" und "+a[a.length-1]:a[0]||"";let t;
  if(r.u==="d")t=n===1?"Täglich":`Alle ${n} Tage`;
  else if(r.u==="w"){const wd=(r.wd||[]).slice().sort((a,b)=>mo(a)-mo(b));
    t=n===1&&wd.join()==="1,2,3,4,5"?"Werktags":(n===1?"Wöchentlich":`Alle ${n} Wochen`)+(wd.length?" am "+list(wd.map(x=>WDL[x])):"")}
  else if(r.u==="m"){t=n===1?"Monatlich":n===3?"Vierteljährlich":`Alle ${n} Monate`;
    if(start&&r.mw==="nth"){const k=nthOf(start);t+=` am ${k===5?"letzten":k+"."} ${WDLONG[wdOf(start)]}`}}
  else t=n===1?"Jährlich":`Alle ${n} Jahre`;
  return t+(r.until?" bis "+fd(r.until):"")}
async function setStatus(t,next){
  const fail=next==="fail",st=fail?"done":next,u={...t,status:st};if(fail)u.fail=true;else delete u.fail;u.log=diffLog(t,u);let sp=null;
  if(st==="done"&&t.rec&&!t.spawned){sp=nextOcc(t);if(sp)u.spawned=sp.id}
  await saveTask(u);if(sp)await saveTask(sp);if(next==="done"&&t.status!=="done")cheer();return sp}
/* Zeitstrahl: Balken ziehen */
/* 1.48: Verknüpfen (A → B: B startet nach A), auch per Menü „Verknüpfen mit …“ und dann Ziel antippen */
let linkFrom=null;
async function addDep(fromId,toId){const f=byId(fromId),to=byId(toId);if(!f||!to||f.id===to.id)return false;
  if((to.deps||[]).includes(f.id)){toast("Ist schon verknüpft");return false}
  if(dependsOn(f.id,to.id)){toast("Das wäre ein Kreis: „"+f.title+"“ hängt schon von „"+to.title+"“ ab.");return false}
  await saveTask({...to,deps:[...(to.deps||[]),f.id]});hap(10);
  toast("„"+to.title+"“ startet nach „"+f.title+"“",()=>saveTask({...byId(to.id),deps:(byId(to.id).deps||[]).filter(x=>x!==f.id)}));return true}
async function dropDep(fromId,toId){const f=byId(fromId),to=byId(toId);if(!f||!to)return;
  if(!await confirmSheet("„"+f.title+"“ → „"+to.title+"“","Verknüpfung lösen"))return;
  await saveTask({...to,deps:(to.deps||[]).filter(x=>x!==f.id)});toast("Verknüpfung gelöst",()=>saveTask({...byId(to.id),deps:[...(byId(to.id).deps||[]),f.id]}))}
function linkStart(id){linkFrom=id;render();toast("Jetzt die Aufgabe antippen, die danach kommt",()=>{linkFrom=null;render()},"Abbrechen",8000)}
/* Reihenfolge (1.48): Schlüssel ord, sonst Startdatum; verschoben wird nur die eine Aufgabe (Mitte zwischen den Nachbarn) */
const ordKey=t=>typeof t.ord==="number"?t.ord:dn(t.start)*100;
/* 1.49: Ziel-Gruppe übernehmen (Projekt, Tag, Person, Priorität), wenn man eine Aufgabe im Zeitstrahl in eine andere Gruppe zieht */
function regroupFields(t,from,to){if(grp==="none"||from===to||from===undefined||to===undefined)return{};
  if(grp==="proj")return{proj:to};
  if(grp==="prio")return{prio:to?+to.replace(/\D/g,"")||0:0};
  if(grp==="tag"){const L=tgs(t).filter(x=>x!==from&&x!==to),tags=to?[to,...L]:L;return{tags,area:tags[0]||""}}
  const L=wl(t).filter(x=>x!==from);if(to&&!L.includes(to))L.push(to);return{who:L.join(", ")}}
const grpName=k=>k||(grp==="tag"?"Ohne Tag":grp==="proj"?"Ohne Projekt":grp==="prio"?"Ohne Priorität":"Nicht zugewiesen");
function ordBetween(beforeId,afterId,t){const a=beforeId&&byId(beforeId),b=afterId&&byId(afterId),ka=a?ordKey(a):null,kb=b?ordKey(b):null;
  return Math.round((ka!==null&&kb!==null?(ka+kb)/2:ka!==null?ka+50:kb!==null?kb-50:ordKey(t))*1000)/1000}
function ordOn(){if(sortm!=="ord"){sortm="ord";try{localStorage.setItem("haus-sort","ord")}catch(_){}if($("srt"))$("srt").value="ord"}}
/* Eine Aufgabe neu einordnen: Reihenfolge (zwischen Nachbarn), Gruppe und optional Zeitraum in einem Schritt, mit Rückgängig */
async function dropRow(id,{before,after,from,to,order=true,dates=null}={}){const t=byId(id);if(!t)return;const u={...t,...regroupFields(t,from,to),...(dates||{})};
  if(order){ordOn();u.ord=ordBetween(before,after,t)}u.log=diffLog(t,u);await saveTask(u);hap(8);
  const moved=grp!=="none"&&from!==to&&from!==undefined&&to!==undefined;
  toast(moved?"„"+t.title+"“ → "+grpName(to):order?"Reihenfolge geändert":"„"+t.title+"“ verschoben",async()=>{const c=byId(id);if(!c)return;const r={...c,proj:t.proj,tags:t.tags,area:t.area,who:t.who,prio:t.prio,start:t.start,end:t.end};if(typeof t.ord==="number")r.ord=t.ord;else delete r.ord;await saveTask(r)})}
async function reorder(id,beforeId,afterId){return dropRow(id,{before:beforeId,after:afterId})}
function neighbours(id){const rows=[...document.querySelectorAll(".gl .gr[data-id]")],i=rows.findIndex(r=>r.dataset.id===id);if(i<0)return null;
  const grpOf=r=>{let p=r.previousElementSibling;while(p&&!p.classList.contains("gh2"))p=p.previousElementSibling;return p};
  const same=rows.filter(r=>grpOf(r)===grpOf(rows[i])),j=same.indexOf(rows[i]);return{same,j}}
async function moveRow(id,dir){const n=neighbours(id);if(!n)return;const {same,j}=n,k=j+dir;if(k<0||k>=same.length)return;
  const ids=same.map(r=>r.dataset.id);ids.splice(j,1);ids.splice(k,0,id);await reorder(id,ids[k-1],ids[k+1])}
const dependsOn=(a,b,seen=new Set())=>{if(seen.has(a))return false;seen.add(a);const t=byId(a);return!!t&&(t.deps||[]).some(d=>d===b||dependsOn(d,b,seen))};
function ganttDrag(){
  const svg=document.querySelector(".gb");if(!svg)return;const ppd=+svg.dataset.ppd||38;
  let st=null,lp=null,suppress=false;
  const tip=$("dtip");
  const showTip=(x,y,txt)=>{tip.textContent=txt;tip.style.left=x+"px";tip.style.top=(y-34)+"px";tip.classList.add("on")};
  const range=(t,k,d)=>{let s=dn(t.start),e=dn(t.end);if(k==="m"){s+=d;e+=d}else if(k==="s")s=Math.min(s+d,e);else e=Math.max(e+d,s);return[s,e]};
  const fmt=(s,e,ms)=>ms?fd(iso(fromDn(s))):fd(iso(fromDn(s)))+" – "+fd(iso(fromDn(e)));
  const begin=(e,g,t,k,lp)=>{
    const r=g.querySelector("rect:not(.gh1)");
    st={t,k,g,lp:!!lp,x0:e.clientX,y0:e.clientY,moved:false,x:r?+r.getAttribute("x"):0,w:r?+r.getAttribute("width"):0,r,id:e.pointerId};
    g.classList.add("drag");if(k==="dep"){st.line=document.createElementNS("http://www.w3.org/2000/svg","path");st.line.setAttribute("class","gtmp");svg.appendChild(st.line)}
    document.addEventListener("touchmove",blockScroll,{passive:false});
  };
  const blockScroll=e=>{if(st)e.preventDefault()};
  const move=e=>{
    if(!st)return;const dx=e.clientX-st.x0,dy=e.clientY-st.y0;
    if(!st.moved&&Math.hypot(dx,dy)<4)return;st.moved=true;
    if(st.k==="dep"){const b=svg.getBoundingClientRect(),c=st.g.querySelector(".gdep"),x1=+c.getAttribute("cx"),y1=+c.getAttribute("cy");
      st.line.setAttribute("d",`M${x1} ${y1}L${e.clientX-b.left} ${e.clientY-b.top}`);
      const over=document.elementFromPoint(e.clientX,e.clientY),tg=over&&over.closest&&over.closest("g[data-id]");
      svg.querySelectorAll(".gbar.tgt").forEach(x=>x.classList.remove("tgt"));if(tg&&tg!==st.g)tg.classList.add("tgt");
      return}
    const d=Math.round(dx/ppd),[s2,e2]=range(st.t,st.k,d),px=d*ppd;
    if(st.k==="m"){const vy=Math.abs(dy)>14?dy:0;st.vy=vy;st.g.setAttribute("transform",`translate(${px} ${vy})`);if(vy){const r=rowDrop(e.clientY,st.t.id),gl=document.querySelector(".gl");st.drop=r;if(gl){let ln=gl.querySelector(".grline");if(!ln){ln=document.createElement("div");ln.className="grline";gl.appendChild(ln)}ln.style.top=(r.y-gl.getBoundingClientRect().top)+"px"}}else{st.drop=null;const ln=document.querySelector(".gl .grline");ln&&ln.remove()}}
    else if(st.r){if(st.k==="s"){st.r.setAttribute("x",st.x+Math.min(px,st.w-8));st.r.setAttribute("width",Math.max(8,st.w-px))}else st.r.setAttribute("width",Math.max(8,st.w+px))}
    st.d=d;showTip(e.clientX,e.clientY,fmt(s2,e2,st.t.ms));
  };
  const end=async e=>{
    document.removeEventListener("pointermove",move);document.removeEventListener("pointerup",end);document.removeEventListener("pointercancel",end);document.removeEventListener("touchmove",blockScroll);
    clearTimeout(lp);tip.classList.remove("on");const s=st;st=null;if(!s)return;
    s.g.classList.remove("drag");svg.querySelectorAll(".gbar.tgt").forEach(x=>x.classList.remove("tgt"));if(s.line)s.line.remove();
    if(!s.moved){if(s.lp&&s.k!=="dep"){suppress=true;setTimeout(()=>{suppress=false},60);taskMenu(s.t.id)}return}suppress=true;setTimeout(()=>{suppress=false},60);
    if(s.k==="dep"){const over=document.elementFromPoint(e.clientX,e.clientY),tg=over&&over.closest&&over.closest("g[data-id]"),to=tg&&byId(tg.dataset.id);
      if(to)await addDep(s.t.id,to.id);return}
    {const ln=document.querySelector(".gl .grline");ln&&ln.remove()}
    /* 1.49: Balken auch nach oben/unten ziehen: Reihenfolge und Gruppe (Projekt, Tag, Person, Priorität) übernehmen, Datum gleich mit */
    if(s.k==="m"&&s.vy&&s.drop){const d0=s.d||0,[a2,b2]=range(s.t,"m",d0);await dropRow(s.t.id,{before:s.drop.before,after:s.drop.after,from:grp==="none"?undefined:s.g.dataset.gk,to:s.drop.gk,dates:d0?{start:iso(fromDn(a2)),end:iso(fromDn(b2))}:null});return}
    const d=s.d||0;if(!d){render();return}
    const[s2,e2]=range(s.t,s.k,d),old={start:s.t.start,end:s.t.end};
    {const n2={...s.t,start:iso(fromDn(s2)),end:iso(fromDn(e2))};n2.log=diffLog(s.t,n2);await saveTask(n2)}
    toast("„"+s.t.title+"“: "+fmt(s2,e2,s.t.ms),()=>saveTask({...byId(s.t.id),...old}));
  };
  svg.addEventListener("click",e=>{if(suppress){e.stopPropagation();e.preventDefault();return}
    if(linkFrom){const g=e.target.closest("g[data-id]");e.stopPropagation();e.preventDefault();const f=linkFrom;linkFrom=null;if(g&&g.dataset.id!==f)addDep(f,g.dataset.id);else render();return}
    const dl=e.target.closest("[data-dep]");if(dl){e.stopPropagation();e.preventDefault();const[a,b]=dl.dataset.dep.split(">");dropDep(a,b)}},true);
  svg.addEventListener("contextmenu",e=>{const g=e.target.closest("g[data-id]");if(!g)return;e.preventDefault();taskMenu(g.dataset.id)});
  svg.addEventListener("pointerdown",e=>{
    if(e.button>0)return;const g=e.target.closest("g[data-id]");if(!g)return;const t=byId(g.dataset.id);if(!t)return;
    const h=e.target.closest("[data-h]"),k=h?h.dataset.h:"m";
    if(linkFrom)return;
    document.addEventListener("pointermove",move);document.addEventListener("pointerup",end);document.addEventListener("pointercancel",end);
    /* Punkt am Balkenende: auch mit dem Finger sofort ziehen (1.48) */
    if(e.pointerType==="touch"&&k==="dep"){begin(e,g,t,k);e.preventDefault();return}
    if(e.pointerType==="touch"){
      const x0=e.clientX,y0=e.clientY;
      const cancel=ev=>{if(Math.hypot(ev.clientX-x0,ev.clientY-y0)>8){clearTimeout(lp);document.removeEventListener("pointermove",cancel);if(!st){document.removeEventListener("pointermove",move);document.removeEventListener("pointerup",end)}}};
      document.addEventListener("pointermove",cancel);
      lp=setTimeout(()=>{document.removeEventListener("pointermove",cancel);begin(e,g,t,k,true);navigator.vibrate&&navigator.vibrate(12)},380);
    }else{begin(e,g,t,k);e.preventDefault()}
  });
}
/* 1.48: Zeilen links am Griff nach oben/unten ziehen. Linie zeigt, wo die Aufgabe landet. */
let grd=null;
/* Einfügestelle unter dem Finger: zwischen zwei Zeilen; die Gruppe ist die Überschrift darüber */
function rowDrop(y,skipId){const all=[...document.querySelectorAll(".gl .gr")];let k=all.length;
  for(let i=0;i<all.length;i++){const r=all[i].getBoundingClientRect();if(y<r.top+r.height/2){k=i;break}}
  if(k===0&&all[0]&&all[0].classList.contains("gh2"))k=1;
  let gk,h=null;for(let i=k-1;i>=0;i--)if(all[i].classList.contains("gh2")){h=all[i];gk=all[i].dataset.gk;break}
  const inG=r=>{let p=r.previousElementSibling;while(p&&!p.classList.contains("gh2"))p=p.previousElementSibling;return p===h};
  const prev=all.slice(0,k).reverse().find(r=>r.dataset.id&&r.dataset.id!==skipId&&inG(r)),next=all.slice(k).find(r=>(r.classList.contains("gh2"))||(r.dataset.id&&r.dataset.id!==skipId));
  const nx=next&&next.dataset.id&&inG(next)?next:null,ref=all[k]||all[all.length-1],rr=ref?ref.getBoundingClientRect():{top:0,bottom:0};
  return{gk:grp==="none"?undefined:gk,before:prev&&prev.dataset.id,after:nx&&nx.dataset.id,y:k<all.length?rr.top:rr.bottom}}
document.addEventListener("pointerdown",e=>{const g=e.target.closest&&e.target.closest("[data-ggrip]");if(!g||e.button>0)return;e.preventDefault();e.stopPropagation();
  const row=g.closest(".gr");grd={id:g.dataset.ggrip,from:grp==="none"?undefined:row.dataset.gk,row,y0:e.clientY,moved:false,line:null,drop:null};try{g.setPointerCapture(e.pointerId)}catch(_){}});
document.addEventListener("pointermove",e=>{if(!grd)return;if(!grd.moved&&Math.abs(e.clientY-grd.y0)<5)return;
  if(!grd.moved){grd.moved=true;grd.line=document.createElement("div");grd.line.className="grline";document.querySelector(".gl").appendChild(grd.line);grd.row.classList.add("dragging");hap(6)}
  grd.drop=rowDrop(e.clientY,grd.id);const gl=document.querySelector(".gl").getBoundingClientRect();grd.line.style.top=(grd.drop.y-gl.top)+"px";
  document.querySelectorAll(".gl .gh2.gtgt").forEach(x=>x.classList.remove("gtgt"));
  if(grd.drop.gk!==grd.from&&grd.drop.gk!==undefined){const h=[...document.querySelectorAll(".gl .gh2")].find(x=>x.dataset.gk===grd.drop.gk);h&&h.classList.add("gtgt")}});
function grEnd(){const d=grd;grd=null;if(!d)return;d.line&&d.line.remove();d.row.classList.remove("dragging");document.querySelectorAll(".gl .gh2.gtgt").forEach(x=>x.classList.remove("gtgt"));
  if(!d.moved||!d.drop)return;const r=d.drop,p=[...document.querySelectorAll(".gl .gr[data-id]")].filter(x=>x.dataset.gk===d.row.dataset.gk),i=p.indexOf(d.row);
  if(r.gk===d.from&&(r.before||null)===((p[i-1]||{}).dataset||{}).id&&(r.after||null)===((p[i+1]||{}).dataset||{}).id)return;
  if(r.gk===d.from&&!r.before&&i===0&&(r.after||null)===(((p[1]||{}).dataset||{}).id||null))return;
  dropRow(d.id,{before:r.before,after:r.after,from:d.from,to:r.gk})}
document.addEventListener("pointerup",grEnd);document.addEventListener("pointercancel",()=>{if(grd){grd.line&&grd.line.remove();grd.row.classList.remove("dragging");grd=null}});
document.addEventListener("click",e=>{if(e.target.closest&&e.target.closest("[data-ggrip]")){e.stopPropagation();e.preventDefault()}},true);
/* Verknüpfen per Antippen auch über die Zeilen links */
document.addEventListener("click",e=>{if(!linkFrom||view!=="gantt")return;const r=e.target.closest&&e.target.closest(".gl .gr[data-id]");if(!r)return;e.stopPropagation();e.preventDefault();
  const f=linkFrom;linkFrom=null;if(r.dataset.id!==f)addDep(f,r.dataset.id);else render()},true);
