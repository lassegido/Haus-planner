/* Mehrfachauswahl */
function applySel(){
  document.body.classList.toggle("selmode",selMode);
  document.querySelectorAll("#main [data-id]").forEach(e=>e.classList.toggle("sel",sel.has(e.dataset.id)));
  const b=$("selbar");b.classList.toggle("on",selMode);b.classList.toggle("has",sel.size>0);$("selbtn").classList.toggle("on",selMode);
  $("selcnt").textContent=isPhone()?(sel.size?String(sel.size):"0"):(sel.size?sel.size+" ausgewählt":"Aufgaben antippen");$("selcnt").title=sel.size+" ausgewählt";
  if(selMode){
    const whos=allWho();
    $("selwho").innerHTML='<option value="">Verantwortlich …</option><option value="__none">Niemand</option>'+whos.map(w=>`<option>${esc(w)}</option>`).join("");
    $("selprio").innerHTML='<option value="">Priorität …</option><option value="0">Keine Priorität</option><option value="1">Prio 1</option><option value="2">Prio 2</option><option value="3">Prio 3</option>';
    $("seltag").innerHTML='<option value="">Tag hinzufügen …</option>'+allTags().map(n=>`<option>${esc(n)}</option>`).join("");
    $("selproj").innerHTML='<option value="">Projekt …</option><option value="__none">Ohne Projekt</option>'+allProjs().map(p=>`<option>${esc(p)}</option>`).join("");
  }
}
function setSel(on){selMode=on;if(!on)sel.clear();applySel()}
$("selbtn").onclick=()=>setSel(!selMode);
/* Gedrückt halten öffnet ein Menü (Auswählen, Status, Duplizieren, Löschen) */
let lpT=0,lpX=0,lpY=0,lpSwallow=false;
const lpStop=()=>{clearTimeout(lpT);lpT=0};
$("main").addEventListener("pointerdown",e=>{
  if(selMode||e.button>0||e.target.closest("button,a,input,select,textarea,svg"))return;
  const el=e.target.closest("#main [data-id]");if(!el)return;
  lpX=e.clientX;lpY=e.clientY;lpStop();
  lpT=setTimeout(()=>{lpT=0;lpSwallow=true;noSel();hap(14);taskMenu(el.dataset.id)},450)});
$("main").addEventListener("pointermove",e=>{if(lpT&&Math.hypot(e.clientX-lpX,e.clientY-lpY)>8)lpStop()});
["pointerup","pointercancel","scroll","dragstart"].forEach(t=>$("main").addEventListener(t,()=>{lpStop();if(lpSwallow){noSel();setTimeout(noSel,60);setTimeout(()=>{lpSwallow=false},350)}},true));
/* Kein Text-Markieren auf Karten, Zeilen und Menüs (iOS markiert sonst beim langen Drücken den Titel) */
function noSel(){try{const s=getSelection();if(s&&s.rangeCount&&!(document.activeElement&&/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)))s.removeAllRanges()}catch(_){}}
const NOSEL="#main [data-id],#dsh,#pop,.tile,.hb,.krow,.tabs,#selbar";
document.addEventListener("selectstart",e=>{const el=e.target&&e.target.nodeType===3?e.target.parentElement:e.target;if(el&&el.closest&&el.closest(NOSEL)&&!el.closest("input,textarea"))e.preventDefault()});
$("main").addEventListener("contextmenu",e=>{if(e.target.closest("#main [data-id]")&&matchMedia("(pointer:coarse)").matches)e.preventDefault()});
$("main").addEventListener("click",e=>{
  if(lpSwallow){lpSwallow=false;e.preventDefault();e.stopPropagation();return}
  if(!selMode)return;const el=e.target.closest("#main [data-id]");if(!el)return;
  e.preventDefault();e.stopPropagation();const id=el.dataset.id;sel.has(id)?sel.delete(id):sel.add(id);hap(6);applySel()},true);
const selList=()=>[...sel].map(byId).filter(Boolean);
$("selbar").onclick=async e=>{
  const b=e.target.closest("button");if(!b)return;
  if(b.dataset.ba==="x"){setSel(false);return}
  const L=selList(),n=L.length;if(!n){toast("Erst Aufgaben antippen");return}
  const T=n===1?"1 Aufgabe":n+" Aufgaben",fire=(id,v)=>{$(id).value=v;$(id).dispatchEvent(new Event("change"))};
  const pick=(title,opts)=>sheet(title,[{items:opts.map(([v,t])=>({t,v}))}]);
  const k=b.dataset.sa;
  if(k==="status"){const v=await sheet(T,[{row:true,items:Object.entries(ST).map(([v,t])=>({t,v}))}]);if(!v)return;
    for(const t of L)if(t.status!==v)await setStatus(t,v);toast(T+": "+ST[v]);sel.clear();applySel()}
  else if(k==="who"){const v=await pick(T+" zuweisen",[...allWho().map(w=>[w,w]),["__none","Niemand"]]);if(v)fire("selwho",v)}
  else if(k==="more"){
    const v=await sheet(T,[{items:[{t:"Priorität",v:"prio"},{t:"Tag hinzufügen",v:"tag",dis:!allTags().length},{t:"Projekt",v:"proj"},{t:"Alle auswählen",v:"all"}]},{items:[{t:"Archivieren",v:"arch"},{t:"In den Papierkorb",v:"del",bad:true}]}]);
    if(v==="prio"){const p=await pick("Priorität",[["1","Prio 1"],["2","Prio 2"],["3","Prio 3"],["0","Keine Priorität"]]);if(p!=null)fire("selprio",p)}
    else if(v==="tag"){const p=await pick("Tag hinzufügen",allTags().map(x=>[x,x]));if(p)fire("seltag",p)}
    else if(v==="proj"){const p=await pick("Projekt",[...allProjs().map(x=>[x,x]),["__none","Ohne Projekt"]]);if(p)fire("selproj",p)}
    else if(v==="all"){filtered().forEach(t=>sel.add(t.id));applySel()}
    else if(v==="arch"){await saveMany(L.map(t=>({...t,arch:true})));toast(T+" archiviert",()=>saveMany(L));sel.clear();applySel()}
    else if(v==="del"){const d=iso(new Date());await saveMany(L.map(t=>({...t,del:true,delAt:d,arch:false})));toast(T+" im Papierkorb",()=>saveMany(L));sel.clear();applySel()}}
};
$("selwho").onchange=async()=>{const v=$("selwho").value,L=selList();if(!v||!L.length)return;
  await saveMany(L.map(t=>lg(t,{...t,who:v==="__none"?"":v})));toast(L.length+" Aufgaben: "+(v==="__none"?"niemand verantwortlich":v));sel.clear();applySel()};
$("selprio").onchange=async()=>{const v=$("selprio").value,L=selList();if(v===""||!L.length)return;
  await saveMany(L.map(t=>lg(t,{...t,prio:+v})));toast(L.length+" Aufgaben: "+(+v?"Prio "+v:"keine Priorität"));sel.clear();applySel()};
$("seltag").onchange=async()=>{const v=$("seltag").value,L=selList();if(!v||!L.length)return;
  await saveMany(L.map(t=>{const a=[...new Set([...tgs(t),v])];return lg(t,{...t,tags:a,area:a[0]||""})}));toast(L.length+" Aufgaben: Tag „"+v+"“ hinzugefügt");sel.clear();applySel()};
$("selproj").onchange=async()=>{const v=$("selproj").value,L=selList();if(!v||!L.length)return;
  await saveMany(L.map(t=>lg(t,{...t,proj:v==="__none"?"":v})));toast(L.length+" Aufgaben: "+(v==="__none"?"ohne Projekt":v));sel.clear();applySel()};

/* Tastatur */
document.addEventListener("keydown",e=>{
  if(e.metaKey||e.ctrlKey||e.altKey)return;
  const el=e.target,typing=el&&(/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)||el.isContentEditable),dlg=document.querySelector("dialog[open]");
  if(e.key==="Escape"&&selMode&&!dlg){setSel(false);return}
  if(typing||dlg)return;
  const tab=v=>{const b=document.querySelector('#tabs [data-v="'+v+'"]');b&&b.click()};
  switch(e.key){
    case"n":e.preventDefault();openDlg();break;
    case"/":e.preventDefault();$("q").focus();break;
    case"1":tab("home");break;case"2":tab("board");break;case"3":tab("list");break;case"4":tab("gantt");break;case"5":tab("cal");break;
    case"s":setSel(!selMode);break;
    case"a":if(selMode){filtered().forEach(t=>sel.add(t.id));applySel()}break;
    case"Delete":case"Backspace":if(selMode&&sel.size){e.preventDefault();$("selbar").querySelector('[data-ba="del"]').click()}break;
    case"h":if(view==="gantt")gToday(true);break;
    case"?":case",":openSettings();break;
  }});
