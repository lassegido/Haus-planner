/* 1.25: iOS-Verhalten */
const hapEl=(()=>{const l=document.createElement("label");l.setAttribute("aria-hidden","true");l.style.cssText="position:fixed;left:-99px;top:-99px;opacity:0;pointer-events:none";const i=document.createElement("input");i.type="checkbox";i.setAttribute("switch","");l.appendChild(i);document.body.appendChild(l);return l})();
function hap(ms){try{if(navigator.vibrate&&navigator.vibrate(ms||10))return}catch(_){}try{hapEl.click()}catch(_){}}
/* Aktionsblatt (statt Bestätigungsdialog) */
function sheet(title,groups){
  return new Promise(res=>{
    const d=$("dsh");let done=false;const fin=v=>{if(done)return;done=true;d.close();res(v)};
    d.innerHTML=(title?"":"")+groups.map((g,gi)=>`<div class="shg${g.row?" row2":""}">${gi===0&&title?`<div class="sht">${esc(title)}</div>`:""}${g.items.map((it,ii)=>`<button type="button" data-g="${gi}" data-i="${ii}" class="${it.bad?"bad ":""}${it.cur?"cur":""}"${it.dis?" disabled":""}>${esc(it.t)}</button>`).join("")}</div>`).join("")+`<button type="button" class="cancel" data-c="1">Abbrechen</button>`;
    d.onclick=e=>{const b=e.target.closest("button");if(b){hap(6);if(b.dataset.c)return fin(null);return fin(groups[+b.dataset.g].items[+b.dataset.i].v)}if(e.target===d)fin(null)};
    d.oncancel=()=>{done=true;res(null)};
    d.showModal()})}
async function confirmSheet(msg,label,primary){return(await sheet(msg,[{items:[{t:label,v:true,bad:!primary}]}]))===true}
/* Kontextmenü zu einer Aufgabe */
async function taskMenu(id){
  const t=byId(id);if(!t)return;const gv=view==="gantt";
  const v=await sheet(t.title,[
    {items:[{t:"Bearbeiten",v:"edit"},gv?{t:"Verknüpfen mit …",v:"link"}:{t:"Auswählen",v:"sel"},...(t.status!=="done"?[{t:"Nicht geschafft",v:"fail"}]:[])]},
    /* 1.48: im Zeitstrahl direkt Projekt, Notiz und Reihenfolge */
    ...(gv?[{items:[{t:t.proj?"Projekt: "+t.proj:"Zu Projekt hinzufügen …",v:"proj"},{t:"Notiz hinzufügen …",v:"note"}]},{row:1,items:[{t:"↑ Nach oben",v:"up"},{t:"↓ Nach unten",v:"down"}]}]:[]),
    {items:[{t:"In den Papierkorb",v:"del",bad:true}]}]);
  if(!v)return;
  if(v==="link")return linkStart(id);
  if(v==="up"||v==="down")return moveRow(id,v==="up"?-1:1);
  if(v==="proj")return projMenu(id);
  if(v==="note"){const n=await askText("Notiz zu „"+t.title+"“","Was ist wichtig?","",true);if(n&&n.trim()){const c=byId(id),u={...c,notes:(c.notes?c.notes.replace(/\s+$/,"")+"\n":"")+n.trim()};u.log=diffLog(c,u);await saveTask(u);toast("Notiz gespeichert")}return}
  if(v==="sel"){setSel(true);sel.add(id);applySel()}
  else if(v==="edit")openDlg(id);
  else if(v==="fail")failTask(id);
  else if(v==="del")trash(id)}
/* Wischen auf Zeilen: rechts erledigt, links in den Papierkorb */
(()=>{
  const strip=document.createElement("div");strip.id="swp";document.body.appendChild(strip);
  let row=null,x0=0,y0=0,dx=0,mode=0,rect=null,crossed=false;
  const sel_="#main tr.row,#main .hrow";
  document.addEventListener("touchstart",e=>{
    row=null;mode=0;if(selMode||e.touches.length!==1||document.querySelector("dialog[open]"))return;
    const el=e.target.closest(sel_);if(!el||e.target.closest("button,a,input,select"))return;
    const t=e.touches[0];if(t.clientX<22)return;
    row=el;x0=t.clientX;y0=t.clientY;dx=0;crossed=false;rect=el.getBoundingClientRect();lpStop()},{passive:true});
  document.addEventListener("touchmove",e=>{
    if(!row)return;const t=e.touches[0],mx=t.clientX-x0,my=t.clientY-y0;
    if(mode===0){if(Math.abs(my)>10&&Math.abs(my)>Math.abs(mx)){row=null;return}if(Math.abs(mx)>12&&Math.abs(mx)>Math.abs(my)*1.4){mode=1;lpStop();row.style.transition="none"}else return}
    dx=Math.max(-190,Math.min(190,mx));
    const over=Math.abs(dx)>90;if(over&&!crossed){hap(10)}crossed=over;
    row.style.transform="translateX("+dx+"px)";
    const r=rect;strip.className=dx>0?"r":"l";
    strip.style.cssText="display:flex;top:"+r.top+"px;height:"+r.height+"px;"+(dx>0?"left:"+r.left+"px;width:"+dx+"px":"left:"+(r.right+dx)+"px;width:"+(-dx)+"px");
    const tk=byId(row.dataset.id);strip.textContent=Math.abs(dx)<40?"":dx>0?(tk&&tk.status==="done"?"Öffnen":"Erledigt"):"Löschen"},{passive:true});
  const end=()=>{
    if(!row)return;const el=row,id=el.dataset.id;row=null;if(mode!==1)return;mode=0;
    strip.style.display="none";const go=Math.abs(dx)>90,dir=dx>0?1:-1;
    el.style.transition="transform .2s ease-out,opacity .2s";
    if(!go){el.style.transform="";setTimeout(()=>{el.style.transition=""},220);return}
    el.style.transform="translateX("+dir*110+"%)";el.style.opacity="0";
    setTimeout(async()=>{el.style.transition="";el.style.transform="";el.style.opacity="";
      const t=byId(id);if(!t)return;
      if(dir>0){const prev=t.status,pf=isFail(t),next=prev==="done"?"todo":"done";hap(8);lastMoved=id;const sp=await setStatus(t,next);
        toast("„"+t.title+"“: "+ST[next],async()=>{const c=byId(id);if(c){await saveTask({...c,status:prev,fail:pf,spawned:sp?"":c.spawned});if(sp)delTask(sp.id)}})}
      else trash(id)},210)};
  document.addEventListener("touchend",end);document.addEventListener("touchcancel",()=>{if(row){row.style.transform="";row.style.transition="";strip.style.display="none"}row=null;mode=0});
  document.addEventListener("click",e=>{if(Date.now()-lastSwipe<400&&e.target.closest(sel_)){e.preventDefault();e.stopPropagation()}},true);
  let lastSwipe=0;document.addEventListener("touchend",()=>{if(mode===1)lastSwipe=Date.now()},true);
})();
/* Nach unten ziehen: aktualisieren, weiter ziehen: Suche */
(()=>{
  const el=document.createElement("div");el.id="ptr";document.body.appendChild(el);
  let y0=null,x0=0,dy=0,stage=0,busy=false;
  const scrolled=n=>{for(;n&&n!==document.body;n=n.parentElement)if(n.scrollTop>0)return true;return false};
  const canSearch=()=>{const b=$("ftog");return !!b&&b.offsetParent!==null};
  document.addEventListener("touchstart",e=>{
    y0=null;if(busy||selMode||e.touches.length!==1||document.querySelector("dialog[open]")||window.scrollY>0||scrolled(e.target))return;
    if(e.target.closest("input,select,textarea,.gwrap,svg"))return;
    y0=e.touches[0].clientY;x0=e.touches[0].clientX;dy=0;stage=0},{passive:true});
  document.addEventListener("touchmove",e=>{
    if(y0===null)return;const t=e.touches[0],m=t.clientY-y0;
    if(m<=0){if(dy===0){y0=null}return}
    if(Math.abs(t.clientX-x0)>m){y0=null;return}
    if(window.scrollY>0){y0=null;return}
    dy=Math.min(m,220);const k=dy*0.5;
    el.style.opacity=Math.min(1,dy/60);el.style.transform="translate(-50%,"+(-64+Math.min(k+10,90))+"px)";
    const st=dy>150&&canSearch()?2:dy>70?1:0;if(st!==stage){stage=st;if(st)hap(8)}
    el.textContent=st===2?"Loslassen zum Suchen":st===1?"Loslassen zum Aktualisieren":"Ziehen zum Aktualisieren"},{passive:true});
  const done=()=>{el.style.transition="transform .22s,opacity .22s";el.style.transform="translate(-50%,-4rem)";el.style.opacity="0";setTimeout(()=>{el.style.transition=""},240)};
  document.addEventListener("touchend",async()=>{
    if(y0===null)return;y0=null;const st=stage;stage=0;if(dy===0)return;dy=0;
    if(st===2){done();const f=$("filters");if(!f.classList.contains("open"))$("ftog").click();else $("q").focus();return}
    if(st===1){busy=true;el.textContent="Aktualisiere …";el.style.transition="transform .2s";el.style.transform="translate(-50%,.6rem)";
      try{if(typeof pull==="function")await pull(true);else render()}catch(_){}
      setTimeout(()=>{busy=false;done()},500);return}
    done()});
  document.addEventListener("touchcancel",()=>{y0=null;dy=0;done()});
})();
/* Dialoge und Blätter: nach unten ziehen schließt (Aufgaben-Dialog fragt bei Änderungen nach) */
let dlgSnap="";
const dlgState=()=>{try{return JSON.stringify([...document.querySelectorAll("#dlg input:not(#f_depq):not(#ai_hint),#dlg select,#dlg textarea")].map(e=>e.type==="checkbox"||e.type==="radio"?e.checked:e.value))+JSON.stringify(cklist)+JSON.stringify(selTags)}catch(_){return""}};
function swipeClose(id,guard){
  const d=$(id);let y0=null,dy=0,t0=0,drag=false;
  const sheetOn=()=>matchMedia("(max-width:699px)").matches;
  const scr=n=>{for(;n&&n!==d;n=n.parentElement)if(n.scrollTop>0)return true;return false};
  d.addEventListener("touchstart",e=>{if(!sheetOn()||e.touches.length!==1||e.target.closest(".gwrap,input,textarea,select")){y0=null;return}y0=e.touches[0].clientY;dy=0;drag=false;t0=Date.now();d.style.transition="none";if(scr(e.target))y0=null},{passive:true});
  d.addEventListener("touchmove",e=>{if(y0===null)return;const m=e.touches[0].clientY-y0;
    if(!drag){if(m>6&&d.scrollTop<=0)drag=true;else return}
    dy=Math.max(0,m);e.preventDefault();d.style.transform="translateY("+dy+"px)"},{passive:false});
  d.addEventListener("touchend",()=>{if(y0===null)return;y0=null;if(!drag)return;drag=false;
    const fast=dy/Math.max(1,Date.now()-t0)>0.6;d.style.transition="transform .2s ease-out";
    if(dy>110||(fast&&dy>40)){
      if(guard&&guard()===false){d.style.transform="";setTimeout(()=>{d.style.transition=""},210);return}
      d.style.transform="translateY(100%)";setTimeout(()=>{d.close();d.style.transform="";d.style.transition=""},190)}
    else{d.style.transform="";setTimeout(()=>{d.style.transition=""},210)}});
  d.addEventListener("touchcancel",()=>{y0=null;drag=false;d.style.transform="";d.style.transition=""})}
["dlf","dls","dla","dlt","dlx"].forEach(id=>swipeClose(id));
swipeClose("dlg",()=>{if(dlgState()===dlgSnap)return true;
  confirmSheet("Änderungen verwerfen?","Verwerfen").then(ok=>{if(ok)$("dlg").close()});return false});
/* Menü am ⋯-Knopf (wie ein iOS-Menü), mit Untermenüs */
const MIC={sel:'<path d="M8.5 12.2l2.5 2.5 4.5-5"/><circle cx="12" cy="12" r="8.5"/>',tag:'<path d="M20 13.2 13.2 20a2 2 0 0 1-2.8 0L3.5 13.1V4.5a1 1 0 0 1 1-1h8.6L20 10.4a2 2 0 0 1 0 2.8z"/><circle cx="8.2" cy="8.2" r="1.3"/>',exp:'<path d="M12 4v11M7.5 10.5 12 15l4.5-4.5M5 19.5h14"/>',cfg:'<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',arch:'<rect x="3.5" y="4.5" width="17" height="4" rx="1"/><path d="M5 8.5V18a1.5 1.5 0 0 0 1.5 1.5h11A1.5 1.5 0 0 0 19 18V8.5M10 12.5h4"/>'};
const svgI=k=>`<svg class="pic" viewBox="0 0 24 24">${MIC[k]}</svg>`;
function popMenu(anchor,items){
  const p=$("pop"),x=$("popx");
  const close=()=>{p.classList.remove("on");x.hidden=true;document.removeEventListener("keydown",esc_);setTimeout(()=>{if(!p.classList.contains("on"))p.hidden=true},160)};
  const esc_=e=>{if(e.key==="Escape"){e.preventDefault();close()}};
  const place=()=>{const r=anchor.getBoundingClientRect(),w=p.offsetWidth,h=p.offsetHeight;p.style.left=Math.max(8,Math.min(r.right-w,innerWidth-w-8))+"px";p.style.top=Math.max(8,Math.min(r.bottom+8,innerHeight-h-8))+"px"};
  const draw=(list,back)=>{
    p.innerHTML=(back?`<button class="pi pback" data-k="back" type="button"><svg class="pic l" viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6"/></svg><span>${esc(back)}</span></button>`:"")+list.map((it,i)=>it.sep?'<div class="psep"></div>':`<button class="pi${it.bad?" bad":""}" data-k="${i}" type="button" role="menuitem"${it.dis?" disabled":""}>${it.chk!==undefined?`<i class="pck">${it.chk?CK:""}</i>`:""}<span>${esc(it.t)}</span>${it.val?`<em>${esc(it.val)}</em>`:""}${it.sub?CH:it.ic?svgI(it.ic):""}</button>`).join("");
    p.onclick=e=>{const b=e.target.closest(".pi");if(!b||b.disabled)return;hap(6);if(b.dataset.k==="back"){draw(items);place();return}const it=list[+b.dataset.k];if(it.sub){draw(it.sub,it.t);place();return}close();if(it.fn)setTimeout(it.fn,10)}};
  draw(items);p.hidden=false;x.hidden=false;place();requestAnimationFrame(()=>p.classList.add("on"));
  x.onclick=close;document.addEventListener("keydown",esc_)}
const GRPL={none:"Keine",tag:"Tag",proj:"Projekt",who:"Person",prio:"Priorität"};
$("more").onclick=()=>{
  const v=view,items=[];
  if(v!=="home")items.push({t:"Auswählen",ic:"sel",fn:()=>setSel(true)});
  if(v==="board"||v==="list"||v==="gantt")items.push({t:"Sortieren",val:sortm==="prio"?"Priorität":sortm==="ord"?"Eigene":"Datum",sub:[["date","Datum"],["prio","Priorität"],["ord","Eigene Reihenfolge"]].map(([k,l])=>({t:l,chk:sortm===k,fn:()=>{$("srt").value=k;$("srt").dispatchEvent(new Event("change"))}}))});
  if(v==="list"||v==="gantt")items.push({t:"Gruppieren",val:GRPL[grp],sub:Object.entries(GRPL).map(([k,l])=>({t:l,chk:grp===k,fn:()=>{$("grp").value=k;$("grp").dispatchEvent(new Event("change"))}}))});
  /* 1.54: zweite Ebene, z. B. erst Projekt, dann Person */
  if((v==="list"||v==="gantt")&&grp!=="none")items.push({t:"Dann gruppieren",val:twoLevel()?GRPL[grp2]:"Keine",sub:Object.entries(GRPL).filter(([k])=>k!==grp).map(([k,l])=>({t:l,chk:(twoLevel()?grp2:"none")===k,fn:()=>setGrp2(k)}))});
  if(items.length)items.push({sep:true});
  items.push({t:"Tags und Projekte",ic:"tag",fn:openMan},{t:"Archiv und Papierkorb",ic:"arch",fn:openArch},{t:"Export und Sicherung",ic:"exp",fn:()=>{$("dlx").showModal();$("dlx").scrollTop=0;preloadExport()}},{t:"Einstellungen",ic:"cfg",fn:openSettings});
  hap(8);popMenu($("more"),items)};
matchMedia("(max-width:699px)").addEventListener("change",()=>{renderedView=null;render()});
$("add").onclick=()=>openDlg();
async function onboard(){if(KIOSK||prefGet("onb")||prefGet("me")||document.querySelector("dialog[open]"))return;prefSet("onb","1");
  const v=await sheet("Willkommen im Planner! Wer nutzt dieses Gerät?",[{items:[{t:"Lasse",v:"Lasse"},{t:"Melanie",v:"Melanie"}]}]);
  if(v){prefSet("me",v);prefSet("hwho","");render()}
  toast("Tipp: Auf der Startseite oben einfach tippen, z. B. „Rasen mähen Sa #Garten“",null,null,8000)}
setTimeout(onboard,1600);
/* 1.48: Text abfragen (Notiz, neues Projekt) im selben Blatt wie die Menüs */
function askText(title,ph,val,multi){return new Promise(res=>{const d=$("dsh");let done=false;const fin=v=>{if(done)return;done=true;d.close();res(v)};
  d.innerHTML=`<div class="shg ask"><div class="sht">${esc(title)}</div>${multi?`<textarea id="ask_t" rows="4" placeholder="${esc(ph)}"></textarea>`:`<input id="ask_t" placeholder="${esc(ph)}" autocomplete="off" enterkeyhint="done">`}<button type="button" data-ok="1" class="cur">Speichern</button></div><button type="button" class="cancel" data-c="1">Abbrechen</button>`;
  const inp=$("ask_t");inp.value=val||"";
  d.onclick=e=>{const b=e.target.closest("button");if(b){if(b.dataset.c)return fin(null);if(b.dataset.ok)return fin(inp.value)}if(e.target===d)fin(null)};
  d.oncancel=()=>{done=true;res(null)};inp.onkeydown=e=>{if(e.key==="Enter"&&!multi){e.preventDefault();fin(inp.value)}};
  d.showModal();setTimeout(()=>inp.focus(),50)})}
async function projMenu(id){const t=byId(id);if(!t)return;const P=allProjs();
  const v=await sheet("Projekt für „"+t.title+"“",[{items:[...P.map(p=>({t:p,v:"p:"+p,cur:t.proj===p})),{t:"Neues Projekt …",v:"new"}]},...(t.proj?[{items:[{t:"Aus dem Projekt nehmen",v:"none",bad:true}]}]:[])]);
  if(!v)return;let p=v==="none"?"":v==="new"?await askText("Neues Projekt","z. B. Elternzeit",""):v.slice(2);if(p===null)return;p=String(p).trim().slice(0,30);if(v==="new"&&!p)return;
  const c=byId(id),u={...c,proj:p};if(p)await regEnsure([],p);u.log=diffLog(c,u);await saveTask(u);toast(p?"„"+c.title+"“ → Projekt „"+p+"“":"Aus dem Projekt genommen",()=>saveTask({...byId(id),proj:c.proj}))}
