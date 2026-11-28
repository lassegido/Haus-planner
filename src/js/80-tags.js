/* Tags */
const TC={sky:"#6CB6E4",sun:"#FDAF54",sea:"#387CA3",brick:"#D35526",mint:"#6CC49A",rose:"#E58BAE",lilac:"#9D86DB",sand:"#C9B77A",slate:"#7C93A3",lemon:"#D9CB3F"},TCK=Object.keys(TC);
const tgs=t=>Array.isArray(t.tags)?t.tags:(t.area?[t.area]:[]);
const cur=()=>regDraft||reg;
const hashC=n=>{let h=0;for(const c of n)h=(h*31+c.charCodeAt(0))>>>0;return TCK[h%TCK.length]};
const autoC=n=>{const i=allTags().indexOf(n);return i<0?hashC(n):TCK[i%TCK.length]};
const colorKey=n=>{const c=(cur().find(x=>!x.p&&x.n===n)||{}).c;return TC[c]?c:autoC(n)};
const tcol=n=>TC[colorKey(n)];
/* Tag-Symbole: feine Linienicons, automatisch zugeordnet (Stichworte offline, KI verfeinert) */
const ICN=["bad", "kueche", "sofa", "bett", "kind", "tuer", "pflanze", "baum", "sonne", "treppe", "dach", "fenster", "flamme", "blitz", "tropfen", "werkzeug", "roller", "boden", "dokument", "muenze", "schild", "auto", "wagen", "eimer", "karton", "pfote", "herz", "koffer", "geschenk", "schloss", "wlan", "birne", "waschmaschine", "kalender", "tonne", "stuhl", "tag"];
const ICN_KW=[[/bad|dusche|wc|toilette|sanit|badezimmer/,"bad"],[/k(ü|ue)che|kochen|herd|geschirr|spül|spuel|backofen/,"kueche"],[/wohnzimmer|sofa|couch|wohnen/,"sofa"],[/schlaf|bett|matratze/,"bett"],[/kind|baby|kita|schule|spiel|nachwuchs|familie/,"kind"],[/flur|diele|t(ü|ue)r|eingang|garderobe/,"tuer"],[/baum|obst|wald|hecke|zaun/,"baum"],[/garten|beet|pflanz|rasen|blume|unkraut|gem(ü|ue)se|mähen|maehen/,"pflanze"],[/terrasse|balkon|sommer|grill|sonne|markise/,"sonne"],[/keller|treppe|stufe/,"treppe"],[/dach|schornstein|giebel|dachboden|speicher/,"dach"],[/fenster|rolll|jalousie|verglas/,"fenster"],[/heiz|ofen|kamin|w(ä|ae)rme|therme|brenner/,"flamme"],[/strom|elektr|steckdose|solar|photovoltaik|energie|sicherung|akku/,"blitz"],[/wasser|rohr|leitung|abfluss|pool|regen|tropf|dichtung/,"tropfen"],[/farbe|streich|maler|tapet|lack|renovier/,"roller"],[/boden|fliese|parkett|laminat|teppich|estrich|silikon|fuge/,"boden"],[/b(ü|ue)ro|papier|dokument|unterlagen|post\b|brief|beh(ö|oe)rde|antrag|formular|ablage/,"dokument"],[/steuer|geld|finanz|budget|rechnung|kosten|bank|sparen|kredit|miete/,"muenze"],[/versicher|recht|vertrag|garantie|gew(ä|ae)hrleistung/,"schild"],[/auto|garage|fahrzeug|reifen|carport|laden|tüv|tuev|werkstatt/,"auto"],[/einkauf|besorg|shopping|bestell|baumarkt/,"wagen"],[/putz|reinig|sauber|aufr(ä|ae)um|ordnung|fenster putzen/,"eimer"],[/umzug|karton|kiste|lager|stauraum|vorrat|keller aus/,"karton"],[/tier|hund|katze|vogel|fisch/,"pfote"],[/gesund|arzt|medizin|vorsorge|apotheke|fitness|erholung|pflege/,"herz"],[/urlaub|reise|ferien|koffer|trip|ausflug/,"koffer"],[/geburtstag|feier|fest\b|geschenk|party|weihnacht|besuch|einladung/,"geschenk"],[/sicher|schloss|alarm|einbruch|kamera|schl(ü|ue)ssel/,"schloss"],[/internet|wlan|netz|router|smart|computer|\bit\b|handy|drucker|fernseh/,"wlan"],[/licht|lampe|leucht|beleucht/,"birne"],[/wasch|w(ä|ae)sche|trockner|spülmaschine/,"waschmaschine"],[/termin|kalender|planung|frist|wartung|regelm/,"kalender"],[/m(ü|ue)ll|abfall|entsorg|sperrm|tonne|recycl/,"tonne"],[/m(ö|oe)bel|stuhl|schrank|regal|tisch|ikea|einrichtung/,"stuhl"],[/technik|ger(ä|ae)t|reparatur|werkzeug|bau|handwerk|montage|umbau|sanier|defekt|kaputt/,"werkzeug"]];
const tagIconAuto=n=>{const l=String(n).toLowerCase();for(const [r,k] of ICN_KW)if(r.test(l))return k;return "tag"};
const tagIconStored=n=>{const i=(cur().find(x=>!x.p&&x.n===n)||{}).i;return ICN.includes(i)?i:""};
const tagIcon=n=>tagIconStored(n)||tagIconAuto(n);
const tIc=n=>`<svg class="ti" aria-hidden="true"><use href="#i-${tagIcon(n)}"/></svg>`;
let iconTried=false;
async function iconSync(){
  if(iconTried||!regLoaded||!loaded)return;
  let tried={};try{tried=JSON.parse(localStorage.getItem("haus-icontry")||"{}")}catch(_){}
  const names=allTags().filter(n=>!tagIconStored(n)&&!tried[n]);if(!names.length||!aiAvail())return;
  names.forEach(n=>tried[n]=1);try{localStorage.setItem("haus-icontry",JSON.stringify(tried))}catch(_){}
  iconTried=true;
  try{const r=await aiJson("Ordne jedem Tag genau ein passendes Symbol aus der Liste zu, das den Bereich im Haushalt am besten verdeutlicht. Tags: "+JSON.stringify(names)+". Symbole: "+ICN.join(", ")+'. Antworte nur als JSON-Objekt der Form {"Tag":"symbol"}.',true);
    if(!r||typeof r!=="object")return;
    const m={};names.forEach(n=>{const k=r[n];m[n]=ICN.includes(k)?k:tagIconAuto(n)});
    saveReg(fullReg().map(x=>!x.p&&m[x.n]?{...x,i:m[x.n]}:x))}catch(e){}}
const chip=n=>`<span class="tag" style="--tc:${tcol(n)}">${tIc(n)}${esc(n)}</span>`;
function allTags(){const out=cur().filter(x=>!x.p).map(x=>x.n);[...new Set(tasks.flatMap(tgs))].filter(n=>!out.includes(n)).sort((a,b)=>a.localeCompare(b,"de")).forEach(n=>out.push(n));return out}
const nextColor=()=>{const used=new Set(allTags().map(colorKey));return TCK.find(k=>!used.has(k))||TCK[allTags().length%TCK.length]};
const mergeReg=l=>{const out=reg.map(x=>({...x}));l.forEach(x=>{if(x&&x.n&&!out.some(y=>!!y.p===!!x.p&&y.n===x.n))out.push({n:String(x.n).slice(0,30),c:TC[x.c]?x.c:hashC(String(x.n)),...(x.p?{p:1}:{})})});return out};
function allProjs(){const out=cur().filter(x=>x.p).map(x=>x.n);[...new Set(tasks.map(t=>t.proj).filter(Boolean))].filter(n=>!out.includes(n)).sort((a,b)=>a.localeCompare(b,"de")).forEach(n=>out.push(n));return out}
const pcolorKey=n=>{const c=(cur().find(x=>x.p&&x.n===n)||{}).c;if(TC[c])return c;const i=allProjs().indexOf(n);return TCK[((i<0?0:i)+3)%TCK.length]};
const pcol=n=>TC[pcolorKey(n)];
const nextPColor=()=>{const used=new Set(allProjs().map(pcolorKey));return TCK.find(k=>!used.has(k))||TCK[allProjs().length%TCK.length]};
const projChip=t=>t.proj?`<span class="tag proj" style="--tc:${pcol(t.proj)}">${esc(t.proj)}</span>`:"";
const fullReg=()=>[...allTags().map(n=>{const o={n,c:colorKey(n)},i=tagIconStored(n);if(i)o.i=i;return o}),...allProjs().map(n=>({n,c:pcolorKey(n),p:1}))];
/* 1.51: Verantwortlich ist jetzt auch Mehrfachauswahl (wie Tag, Projekt, Priorität); „__none“ = nicht zugewiesen */
let fwho=new Set();
const whoOk=t=>!fwho.size||[...fwho].some(k=>k==="__none"?!t.who:wl(t).includes(k));
const tagOk=t=>(!ftags.size||[...ftags].some(k=>k==="__none"?!tgs(t).length:tgs(t).includes(k)))&&(!fprojs.size||[...fprojs].some(k=>k==="__none"?!t.proj:t.proj===k))&&(!fprios.size||fprios.has(t.prio||0));
/* Gruppen nach einem Merkmal (by: tag, proj, prio, who). 1.54: zweite Ebene über grp2 („Dann gruppieren“), siehe groups2 */
const GSEP="\u001f";
function groups(list,by=grp){
  if(by==="none")return[{l:null,L:list}];
  const key=t=>by==="tag"?(tgs(t)[0]||""):by==="proj"?(t.proj||""):by==="prio"?(t.prio?"Prio "+t.prio:""):(t.who||"");
  const order=by==="tag"?allTags():by==="proj"?allProjs():by==="prio"?["Prio 1","Prio 2","Prio 3"]:allWho();
  const m=new Map();list.forEach(t=>{const ks=by==="who"?(wl(t).length?wl(t):[""]):[key(t)];ks.forEach(k=>{if(!m.has(k))m.set(k,[]);m.get(k).push(t)})});
  const ks=[...m.keys()].filter(Boolean).sort((a,b)=>{const i=order.indexOf(a),j=order.indexOf(b);return(i<0?999:i)-(j<0?999:j)||a.localeCompare(b,"de")});
  if(m.has(""))ks.push("");
  const pc=w=>/^melanie/i.test(w)?TC.brick:/^lasse/i.test(w)?TC.sea:TC.sky;
  return ks.map(k=>({k,l:grpLabel(k,by),c:k?(by==="tag"?tcol(k):by==="proj"?pcol(k):by==="prio"?"#14303F":pc(k)):"#9FB0B9",L:m.get(k)}))
}
const grpLabel=(k,by=grp)=>k||(by==="tag"?"Ohne Tag":by==="proj"?"Ohne Projekt":by==="prio"?"Ohne Priorität":"Nicht zugewiesen");
const twoLevel=()=>grp!=="none"&&grp2!=="none"&&grp2!==grp;
/* Zwei Ebenen: jede Gruppe bekommt Untergruppen (S) mit zusammengesetztem Schlüssel „k1␟k2“ */
function groups2(list){const G=groups(list);if(!twoLevel())return G;
  return G.map(g=>({...g,S:groups(g.L,grp2).map(h=>({...h,k:g.k+GSEP+h.k}))}))}
let migrated=false,regLoaded=false;
function migrateReg(){if(migrated||!regLoaded||!tasks.length)return;migrated=true;if(allTags().some(n=>!reg.some(x=>!x.p&&x.n===n))||allProjs().some(n=>!reg.some(x=>x.p&&x.n===n)))saveReg(fullReg())}
const fCount=()=>ftags.size+fprojs.size+fprios.size+fwho.size;
function drawTbar(){
  const names=allTags(),pn=allProjs(),box=$("tchips");
  ftags=new Set([...ftags].filter(x=>x==="__none"||names.includes(x)));fprojs=new Set([...fprojs].filter(x=>x==="__none"||pn.includes(x)));
  const ac=(a,k,l,col,pre)=>`<button class="tc on" data-a="${a}" data-v="${esc(k)}"${col?` style="--tc:${col}"`:""}>${pre||""}<span>${esc(l)}</span><em>×</em></button>`;
  const act=[...fprojs].map(k=>ac("p",k,k==="__none"?"Ohne Projekt":k,k==="__none"?"var(--faint)":pcol(k),"<i></i>")).concat([...ftags].map(k=>ac("t",k,k==="__none"?"Ohne Tag":k,k==="__none"?"var(--faint)":tcol(k),k==="__none"?"<i></i>":tIc(k))),[...fprios].sort().map(r=>ac("r",String(r),r?"Prio "+r:"Ohne Prio",r?`var(--p${r})`:"var(--faint)","<i></i>")),[...fwho].map(w=>ac("w",w,w==="__none"?"Nicht zugewiesen":w,"var(--sea)","<i></i>")));
  if(act.length>1)act.push('<button class="tclr" data-a="all">Alle entfernen</button>');
  box.innerHTML=act.join("");
  const n=fCount();$("fcnt").textContent=n||"";$("fbtn").classList.toggle("on",n>0);
  $("grp").value=grp;$("srt").value=sortm;
  if($("dlf").open)drawF();
}
function drawF(){
  const names=allTags(),pn=allProjs(),none=tasks.filter(t=>!tgs(t).length).length,noP=tasks.filter(t=>!t.proj).length,whos=allWho();
  const ch=(a,k,l,cnt,on,col,pre)=>`<button class="tc${on?" on":""}" data-fa="${a}" data-fv="${esc(k)}"${col?` style="--tc:${col}"`:""}>${pre===undefined?(col?"<i></i>":""):pre}<span>${esc(l)}</span><em>${cnt}</em></button>`;
  let h="";
  if(pn.length)h+=`<label>Projekt</label><div class="fch">`+pn.map(x=>ch("p",x,x,tasks.filter(t=>t.proj===x).length,fprojs.has(x),pcol(x))).join("")+(noP&&noP<tasks.length?ch("p","__none","Ohne Projekt",noP,fprojs.has("__none"),"var(--faint)"):"")+"</div>";
  h+=`<label>Priorität</label><div class="fch">`+[1,2,3].map(r=>ch("r",String(r),"Prio "+r,tasks.filter(t=>t.prio===r).length,fprios.has(r),`var(--p${r})`)).join("")+ch("r","0","Ohne Prio",tasks.filter(t=>!t.prio).length,fprios.has(0),"var(--faint)")+"</div>";
  if(names.length)h+=`<label>Tag</label><div class="fch">`+names.map(x=>ch("t",x,x,tasks.filter(t=>tgs(t).includes(x)).length,ftags.has(x),tcol(x),tIc(x))).join("")+(none?ch("t","__none","Ohne Tag",none,ftags.has("__none"),"var(--faint)"):"")+"</div>";
  if(whos.length)h+=`<label>Verantwortlich</label><div class="fch">`+whos.map(x=>ch("w",x,x,tasks.filter(t=>wl(t).includes(x)).length,fwho.has(x),null)).join("")+ch("w","__none","Nicht zugewiesen",tasks.filter(t=>!t.who).length,fwho.has("__none"),null)+"</div>";
  $("fbody").innerHTML=h;
  const c=filtered().length;$("f_cnt").textContent=fCount()?`${c} von ${tasks.length} Aufgaben passen`:`${tasks.length} Aufgaben, kein Filter aktiv`;$("f_reset").disabled=!fCount();
}
function fClear(){ftags.clear();fprojs.clear();fprios.clear();fwho.clear()}
function fToggle(a,v){
  if(a==="p")fprojs.has(v)?fprojs.delete(v):fprojs.add(v);
  else if(a==="t")ftags.has(v)?ftags.delete(v):ftags.add(v);
  else if(a==="r"){const k=+v;fprios.has(k)?fprios.delete(k):fprios.add(k)}
  else if(a==="w")fwho.has(v)?fwho.delete(v):fwho.add(v);
}
$("fbtn").onclick=()=>{drawF();$("dlf").showModal();$("dlf").scrollTop=0};
$("f_ok").onclick=()=>$("dlf").close();
$("f_reset").onclick=()=>{fClear();render()};
$("fbody").onclick=e=>{const b=e.target.closest("[data-fa]");if(!b)return;fToggle(b.dataset.fa,b.dataset.fv);render()};
$("tchips").onclick=e=>{const b=e.target.closest("[data-a]");if(!b)return;if(b.dataset.a==="all")fClear();else fToggle(b.dataset.a,b.dataset.v);render()};
$("grp").onchange=e=>{grp=e.target.value;try{localStorage.setItem("haus-grp",grp)}catch(_){}render()};
function setGrp2(v){grp2=v;try{localStorage.setItem("haus-grp2",v)}catch(_){}render()}
$("srt").onchange=e=>{sortm=e.target.value;gOrd=null;try{localStorage.setItem("haus-sort",sortm)}catch(_){}render()};
/* Tag-Auswahl im Aufgaben-Dialog */
function drawTags(){
  $("f_tsel").innerHTML=selTags.map((n,i)=>`<span class="tag rm${colorFor===n?" sel":""}" data-pick="${i}" style="--tc:${tcol(n)}"><span>${esc(n)}</span><b data-rm="${i}" aria-label="Entfernen">×</b></span>`).join("");
  const raw=$("f_tagin").value.trim(),q=raw.toLowerCase(),all=allTags();
  const sug=all.filter(n=>!selTags.includes(n)&&(!q||n.toLowerCase().includes(q))),exact=all.some(n=>n.toLowerCase()===q);
  $("f_tsug").innerHTML=(q&&!exact?`<button type="button" class="tnew" data-new="1">+ „${esc(raw)}“ anlegen</button>`:"")+sug.map(n=>`<button type="button" data-add="${esc(n)}" style="--tc:${tcol(n)}">${esc(n)}</button>`).join("");
  $("f_sw").innerHTML=colorFor&&selTags.includes(colorFor)?`<span class="swl">Farbe für „${esc(colorFor)}“</span>`+TCK.map(k=>`<button type="button" class="sw${colorKey(colorFor)===k?" on":""}" data-sw="${k}" style="--tc:${TC[k]}" aria-label="${k}"></button>`).join(""):"";
}
function addTag(raw){
  const name=String(raw).trim().slice(0,30);if(!name||!regDraft)return;
  const ex=allTags().find(x=>x.toLowerCase()===name.toLowerCase()),n=ex||name;
  if(!ex){regDraft.push({n,c:nextColor()});colorFor=n}
  if(!selTags.includes(n))selTags.push(n);
  $("f_tagin").value="";drawTags();
}
function setDraftColor(n,k){const i=regDraft.findIndex(x=>x.n===n);if(i>=0)regDraft[i].c=k;else regDraft.push({n,c:k});drawTags()}
$("f_tpick").onclick=e=>{
  const r=e.target.closest("[data-rm]");if(r){const n=selTags.splice(+r.dataset.rm,1)[0];if(colorFor===n)colorFor=null;drawTags();return}
  const p=e.target.closest("[data-pick]");if(p){const n=selTags[+p.dataset.pick];colorFor=colorFor===n?null:n;drawTags();return}
  $("f_tagin").focus()};
$("f_tsug").onclick=e=>{const a=e.target.closest("[data-add]");if(a){addTag(a.dataset.add);return}if(e.target.closest("[data-new]"))addTag($("f_tagin").value)};
$("f_sw").onclick=e=>{const s=e.target.closest("[data-sw]");if(s&&colorFor)setDraftColor(colorFor,s.dataset.sw)};
$("f_tagin").oninput=drawTags;
$("f_tagin").onkeydown=e=>{if(e.key==="Enter"||e.key===","){e.preventDefault();addTag($("f_tagin").value)}else if(e.key==="Backspace"&&!e.target.value&&selTags.length){selTags.pop();drawTags()}};
/* Tags verwalten */
function openMan(){palOpen=null;$("tm_new").value="";$("tm_pnew").value="";drawMan();$("dlt").showModal()}
const sw10=(sel,k)=>TCK.map(c=>`<button class="sw${sel===c?" on":""}" data-sw="${c}" style="--tc:${TC[c]}" aria-label="${c}"></button>`).join("");
function mrow(k,n,i,cnt){const col=k==="p"?pcol(n):tcol(n),ck=k==="p"?pcolorKey(n):colorKey(n);return`<div class="tm" style="--tc:${col}"><button class="dotb${k==="p"?" sq":""}" data-pal="${k}${i}" aria-label="Farbe ändern"></button><input value="${esc(n)}" data-ren="${k}${i}" maxlength="30" aria-label="Name"><small>${cnt}</small><button class="x" data-del="${k}${i}" aria-label="Löschen">✕</button></div>`+(palOpen===k+":"+n?`<div class="swatches">${sw10(ck)}</div>`:"")}
function drawMan(){
  const tn=allTags(),pn=allProjs();
  $("tm_list").innerHTML=tn.length?tn.map((n,i)=>mrow("t",n,i,tasks.filter(t=>tgs(t).includes(n)).length)).join(""):'<div class="none">Noch keine Tags.</div>';
  $("tm_plist").innerHTML=pn.length?pn.map((n,i)=>mrow("p",n,i,tasks.filter(t=>t.proj===n).length)).join(""):'<div class="none">Noch keine Projekte.</div>';
}
const manName=key=>(key[0]==="p"?allProjs():allTags())[+key.slice(1)];
async function renameItem(k,o,nw){
  nw=nw.trim().slice(0,30);if(!nw||nw===o){drawMan();return}
  const isP=k==="p",ex=(isP?allProjs():allTags()).find(x=>x!==o&&x.toLowerCase()===nw.toLowerCase()),target=ex||nw,col=isP?pcolorKey(o):colorKey(o);
  let nr=fullReg();
  if(ex)nr=nr.filter(x=>!(!!x.p===isP&&x.n===o));else nr=nr.map(x=>!!x.p===isP&&x.n===o?{...x,n:target,c:col}:x);
  let ch;
  if(isP){ch=tasks.filter(t=>t.proj===o).map(t=>({...t,proj:target}));if(fprojs.delete(o))fprojs.add(target)}
  else{ch=tasks.filter(t=>tgs(t).includes(o)).map(t=>{const a=[...new Set(tgs(t).map(x=>x===o?target:x))];return{...t,tags:a,area:a[0]||""}});if(ftags.delete(o))ftags.add(target)}
  await saveReg(nr);await saveMany(ch);palOpen=null;drawMan();
}
async function removeItem(k,n){
  const isP=k==="p",aff=tasks.filter(t=>isP?t.proj===n:tgs(t).includes(n)),c=aff.length,w=isP?"Projekt":"Tag";
  if(!await confirmSheet(c?`${w} „${n}“ löschen? Er wird bei ${c} ${c===1?"Aufgabe":"Aufgaben"} entfernt.`:`${w} „${n}“ löschen?`,"Löschen"))return;
  const ch=aff.map(t=>isP?{...t,proj:""}:(a=>({...t,tags:a,area:a[0]||""}))(tgs(t).filter(x=>x!==n)));
  if(isP)fprojs.delete(n);else ftags.delete(n);palOpen=null;
  await saveReg(fullReg().filter(x=>!(!!x.p===isP&&x.n===n)));await saveMany(ch);drawMan();
}
$("tman").onclick=openMan;
$("tm_close").onclick=()=>$("dlt").close();
const manClick=e=>{
  const p=e.target.closest("[data-pal]");if(p){const k=p.dataset.pal[0],n=manName(p.dataset.pal);palOpen=palOpen===k+":"+n?null:k+":"+n;drawMan();return}
  const sw=e.target.closest("[data-sw]");if(sw&&palOpen){const k=palOpen[0],n=palOpen.slice(2);saveReg(fullReg().map(x=>(!!x.p===(k==="p")&&x.n===n)?{...x,c:sw.dataset.sw}:x));drawMan();return}
  const d=e.target.closest("[data-del]");if(d)removeItem(d.dataset.del[0],manName(d.dataset.del))};
const manRen=e=>{const r=e.target.closest("[data-ren]");if(r)renameItem(r.dataset.ren[0],manName(r.dataset.ren),r.value)};
$("tm_list").onclick=manClick;$("tm_plist").onclick=manClick;$("tm_list").onchange=manRen;$("tm_plist").onchange=manRen;
const manAdd=k=>{const inp=$(k==="p"?"tm_pnew":"tm_new"),name=inp.value.trim().slice(0,30);if(!name)return;
  const list=k==="p"?allProjs():allTags();
  if(!list.some(x=>x.toLowerCase()===name.toLowerCase())){const nr=fullReg();nr.push(k==="p"?{n:name,c:nextPColor(),p:1}:{n:name,c:nextColor()});saveReg(nr)}
  inp.value="";drawMan()};
$("tm_add").onclick=()=>manAdd("t");$("tm_padd").onclick=()=>manAdd("p");
$("tm_new").onkeydown=e=>{if(e.key==="Enter"){e.preventDefault();manAdd("t")}};
$("tm_pnew").onkeydown=e=>{if(e.key==="Enter"){e.preventDefault();manAdd("p")}};
