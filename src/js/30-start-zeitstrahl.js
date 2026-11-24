/* Startseite, Hilfen, Bewegung */
let lastMoved=null,tt,enterT;
const greet=()=>{const h=new Date().getHours();return h<5?"Gute Nacht":h<11?"Guten Morgen":h<17?"Guten Tag":"Guten Abend"};
const reduced=()=>matchMedia("(prefers-reduced-motion:reduce)").matches;
function toast(msg,undo,label,ms){const el=$("toast");el.innerHTML="<span></span>"+(undo?"<button>"+(label||"Rückgängig")+"</button>":"");el.firstChild.textContent=msg;if(undo)el.querySelector("button").onclick=()=>{undo();el.classList.remove("on")};if(el.showPopover){if(!el.hasAttribute("popover"))el.setAttribute("popover","manual");try{el.hidePopover()}catch(_){}try{el.showPopover()}catch(_){}}el.classList.add("on");clearTimeout(tt);tt=setTimeout(()=>el.classList.remove("on"),ms||4500)}
async function advance(id){
  const t=byId(id);if(!t)return;const prev=t.status,next=NEXT[prev];hap(8);lastMoved=id;
  const sp=await setStatus(t,next);
  toast("„"+t.title+"“: "+ST[next]+(sp?" · nächste am "+fd(sp.start):""),async()=>{const c=byId(id);if(c){lastMoved=id;await saveTask({...c,status:prev,spawned:sp?"":c.spawned});if(sp)delTask(sp.id)}})}
/* Wiederholung, Meilenstein */
const RECI='<svg class="mi" viewBox="0 0 24 24" aria-label="Wiederholt sich"><path d="M4 12a8 8 0 0 1 14-5.3L20 9M20 4v5h-5M20 12a8 8 0 0 1-14 5.3L4 15M4 20v-5h5"/></svg>';
const MSI='<svg class="mi" viewBox="0 0 24 24" aria-label="Meilenstein"><path d="M12 3l9 9-9 9-9-9z"/></svg>';
const dr=t=>t.ms?fd(t.start):`${fd(t.start)}–${fd(t.end)}`;
const newId=()=>"t"+Date.now().toString(36)+Math.random().toString(36).slice(2,5);
function addInterval(d,r){
  const dt=fromDn(dn(d));
  if(r.u==="d")dt.setUTCDate(dt.getUTCDate()+r.n);
  else if(r.u==="w")dt.setUTCDate(dt.getUTCDate()+7*r.n);
  else{const m=r.u==="y"?r.n*12:r.n,day=dt.getUTCDate();dt.setUTCDate(1);dt.setUTCMonth(dt.getUTCMonth()+m);dt.setUTCDate(Math.min(day,new Date(Date.UTC(dt.getUTCFullYear(),dt.getUTCMonth()+1,0)).getUTCDate()))}
  return iso(dt)}
function nextOcc(t){
  const len=dn(t.end)-dn(t.start);let s=t.start,e=t.end,g=0;
  do{s=addInterval(s,t.rec);e=iso(fromDn(dn(s)+len))}while(dn(e)<today()&&++g<500);
  return{...t,id:newId(),status:"todo",start:s,end:e,checklist:(t.checklist||[]).map(c=>({...c,d:false})),deps:[],spawned:""}}
async function setStatus(t,next){
  const u={...t,status:next};u.log=diffLog(t,u);let sp=null;
  if(next==="done"&&t.rec&&!t.spawned){sp=nextOcc(t);u.spawned=sp.id}
  await saveTask(u);if(sp)await saveTask(sp);return sp}
/* Zeitstrahl: Balken ziehen */
const dependsOn=(a,b,seen=new Set())=>{if(seen.has(a))return false;seen.add(a);const t=byId(a);return!!t&&(t.deps||[]).some(d=>d===b||dependsOn(d,b,seen))};
function ganttDrag(){
  const svg=document.querySelector(".gb");if(!svg)return;const ppd=+svg.dataset.ppd||38;
  let st=null,lp=null,suppress=false;
  const tip=$("dtip");
  const showTip=(x,y,txt)=>{tip.textContent=txt;tip.style.left=x+"px";tip.style.top=(y-34)+"px";tip.classList.add("on")};
  const range=(t,k,d)=>{let s=dn(t.start),e=dn(t.end);if(k==="m"){s+=d;e+=d}else if(k==="s")s=Math.min(s+d,e);else e=Math.max(e+d,s);return[s,e]};
  const fmt=(s,e,ms)=>ms?fd(iso(fromDn(s))):fd(iso(fromDn(s)))+" – "+fd(iso(fromDn(e)));
  const begin=(e,g,t,k)=>{
    const r=g.querySelector("rect:not(.gh1)");
    st={t,k,g,x0:e.clientX,y0:e.clientY,moved:false,x:r?+r.getAttribute("x"):0,w:r?+r.getAttribute("width"):0,r,id:e.pointerId};
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
    if(st.k==="m")st.g.setAttribute("transform",`translate(${px} 0)`);
    else if(st.r){if(st.k==="s"){st.r.setAttribute("x",st.x+Math.min(px,st.w-8));st.r.setAttribute("width",Math.max(8,st.w-px))}else st.r.setAttribute("width",Math.max(8,st.w+px))}
    st.d=d;showTip(e.clientX,e.clientY,fmt(s2,e2,st.t.ms));
  };
  const end=async e=>{
    document.removeEventListener("pointermove",move);document.removeEventListener("pointerup",end);document.removeEventListener("pointercancel",end);document.removeEventListener("touchmove",blockScroll);
    clearTimeout(lp);tip.classList.remove("on");const s=st;st=null;if(!s)return;
    s.g.classList.remove("drag");svg.querySelectorAll(".gbar.tgt").forEach(x=>x.classList.remove("tgt"));if(s.line)s.line.remove();
    if(!s.moved)return;suppress=true;setTimeout(()=>{suppress=false},60);
    if(s.k==="dep"){const over=document.elementFromPoint(e.clientX,e.clientY),tg=over&&over.closest&&over.closest("g[data-id]"),to=tg&&byId(tg.dataset.id);
      if(!to||to.id===s.t.id||(to.deps||[]).includes(s.t.id))return;
      if(dependsOn(s.t.id,to.id)){toast("Das wäre ein Kreis: „"+s.t.title+"“ hängt schon von „"+to.title+"“ ab.");return}
      await saveTask({...to,deps:[...(to.deps||[]),s.t.id]});toast("„"+to.title+"“ startet nach „"+s.t.title+"“",()=>saveTask({...byId(to.id),deps:(byId(to.id).deps||[]).filter(x=>x!==s.t.id)}));return}
    const d=s.d||0;if(!d){render();return}
    const[s2,e2]=range(s.t,s.k,d),old={start:s.t.start,end:s.t.end};
    {const n2={...s.t,start:iso(fromDn(s2)),end:iso(fromDn(e2))};n2.log=diffLog(s.t,n2);await saveTask(n2)}
    toast("„"+s.t.title+"“: "+fmt(s2,e2,s.t.ms),()=>saveTask({...byId(s.t.id),...old}));
  };
  svg.addEventListener("click",e=>{if(suppress){e.stopPropagation();e.preventDefault()}},true);
  svg.addEventListener("pointerdown",e=>{
    if(e.button>0)return;const g=e.target.closest("g[data-id]");if(!g)return;const t=byId(g.dataset.id);if(!t)return;
    const h=e.target.closest("[data-h]"),k=h?h.dataset.h:"m";
    if(e.pointerType==="touch"&&k==="dep")return;
    document.addEventListener("pointermove",move);document.addEventListener("pointerup",end);document.addEventListener("pointercancel",end);
    if(e.pointerType==="touch"){
      const x0=e.clientX,y0=e.clientY;
      const cancel=ev=>{if(Math.hypot(ev.clientX-x0,ev.clientY-y0)>8){clearTimeout(lp);document.removeEventListener("pointermove",cancel);if(!st){document.removeEventListener("pointermove",move);document.removeEventListener("pointerup",end)}}};
      document.addEventListener("pointermove",cancel);
      lp=setTimeout(()=>{document.removeEventListener("pointermove",cancel);begin(e,g,t,k);navigator.vibrate&&navigator.vibrate(12)},380);
    }else{begin(e,g,t,k);e.preventDefault()}
  });
}
