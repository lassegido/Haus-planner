/* Archiv, Papierkorb */
async function trash(id){const t=byId(id);if(!t)return;await saveTask({...t,del:true,delAt:iso(new Date()),arch:false});
  toast("„"+t.title+"“ liegt im Papierkorb",()=>saveTask({...byId(id),del:false,delAt:""}))}
function drawArch(){
  const A=RAW.filter(t=>t.arch&&!t.del),T=RAW.filter(t=>t.del);
  const row=(t,b)=>`<div class="ar"><div><b>${esc(t.title)}</b><small>${dr(t)}${t.del&&t.delAt?" · gelöscht am "+fd(t.delAt):""}</small></div>${b}</div>`;
  $("a_list").innerHTML=`<label>Archiv · ${A.length}</label>`+(A.length?A.map(t=>row(t,`<button class="btn ghost sm" data-un="${t.id}">Zurückholen</button>`)).join(""):'<div class="none">Nichts im Archiv.</div>')
   +`<label>Papierkorb · ${T.length}</label><p class="hint">Gelöschtes wird nach 30 Tagen endgültig entfernt.</p>`
   +(T.length?T.map(t=>row(t,`<button class="btn ghost sm" data-re="${t.id}">Zurückholen</button><button class="x" data-rm="${t.id}" aria-label="Endgültig löschen">✕</button>`)).join(""):'<div class="none">Papierkorb ist leer.</div>');
  $("a_empty").style.display=T.length?"":"none";
}
function openArch(){drawArch();$("dla").showModal()}
$("a_close").onclick=()=>$("dla").close();
$("a_list").onclick=async e=>{
  const b=e.target.closest("button");if(!b)return;const d=b.dataset;
  if(d.un){await saveTask({...byId(d.un),arch:false})}
  else if(d.re){await saveTask({...byId(d.re),del:false,delAt:""})}
  else if(d.rm){const t=byId(d.rm);if(t&&await confirmSheet("„"+t.title+"“ endgültig löschen?","Endgültig löschen"))await delTask(d.rm)}
  drawArch()};
$("a_empty").onclick=async()=>{const T=RAW.filter(t=>t.del);if(T.length&&await confirmSheet(T.length+" Aufgaben endgültig löschen?","Papierkorb leeren")){for(const t of T)await delTask(t.id);drawArch()}};

/* Einstellungen */
let sPage="main";
const CH='<svg class="chev" viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg>',CK='<svg class="ck" viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7"/></svg>';
const THN={auto:"Automatisch",light:"Hell",dark:"Dunkel"},STT={alexa:"Alexa",show:"Anzeige für Echo Show",des:"Farbwelt",font:"Schrift",ki:"KI-Assistent",fun:"Sprüche und GIFs",rem:"Erinnerung",remt:"Uhrzeit",theme:"Darstellung",me:"Ich bin",keys:"Tastaturkürzel"};
const PREV='<div class="prev" aria-label="Vorschau"><div class="pv-side"><i></i><i></i><i></i></div><div class="pv-main"><div class="pv-h">Planner</div><div class="pv-cols"><div><em class="c1"></em><span>Dachrinne reinigen</span></div><div><em class="c2"></em><span>Kinderzimmer streichen</span></div><div><em class="c3"></em><span>Steuer abheften</span></div></div><div class="pv-b"><b>Speichern</b><u>Abbrechen</u></div></div></div>';
const srow=(a,l,v,x,chev=true)=>`<button class="srow" ${a}>${x||""}<span>${l}</span>${v!=null?`<em>${v}</em>`:""}${chev?CH:""}</button>`;
const REMT=[];for(let h=5;h<=22;h++){REMT.push(String(h).padStart(2,"0")+":00");if(h<22)REMT.push(String(h).padStart(2,"0")+":30")}
const ntfName=x=>x.replace(/^mobile_app_/,"").split("_").map(w=>w==="von"?w:w==="iphone"?"iPhone":w==="ipad"?"iPad":w.charAt(0).toUpperCase()+w.slice(1)).join(" ");
async function haSave(o){try{const r=await api("api/ha-settings",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(o)});if(r.ha)haInfo=r.ha}catch(e){toast("Speichern fehlgeschlagen")}}
async function loadAvail(){try{const r=await api("api/ha-notify");haAvail=r.services||[]}catch(e){haAvail=[]}if($("dls").open&&sPage==="rem")drawSettings()}
const sopt=(a,l,on,x,st)=>`<button class="srow opt${on?" on":""}" ${a}>${x||""}<span${st?` style="${st}"`:""}>${l}</span>${on?CK:""}</button>`;
function dpHtml(l,d){const dk=isDark(),v=l?(dk?d:l):null,c=v?[v[0],v[9],v[11]]:dk?["#0E1E27","#0A171E","#6CB6E4"]:["#F5F3EB","#2D6786","#387CA3"];return `<span class="dp" style="background:${c[0]}"><i style="background:${c[1]}"></i><b style="background:${c[2]}"></b><u style="background:${c[2]}"></u></span>`}
const dsx_=k=>(DES.find(x=>x[0]===k)||DES[0])[0];
let kiMsg=null;
async function kiCheck(){let r=null;try{await aiJson('Antworte nur mit diesem JSON: {"notes":"ok","checklist":[]}')}catch(e){r=(e&&e.message)||String(e)}
  try{if(typeof pull==="function")await pull(true)}catch(_){}return r}
function drawSettings(){
  const th=prefGet("theme")||"auto",ac=prefGet("acc")||"",ds=prefGet("design")||"porto",fk=prefGet("font")||"figtree",me=prefGet("me")||"";
  $("s_back").hidden=sPage==="main";$("s_title").textContent=sPage==="main"?"Einstellungen":STT[sPage];
  const grp=x=>`<div class="sgrp">${x}</div>`,cap=t=>`<p class="scap">${t}</p>`;let h="";
  if(sPage==="main"){
    const dn=tasks.filter(t=>t.status==="done").length,A=RAW.filter(t=>t.arch&&!t.del).length,T=RAW.filter(t=>t.del).length;
    const dsx=DES.find(x=>x[0]===ds)||DES[0];
    h=`<p class="sgt sgh">Nur für dich${USER?" · "+esc(USER):""}</p>`+cap(USER?"Gilt für dich auf all deinen Geräten, die anderen behalten ihre eigene Auswahl.":"Gilt nur für dieses Gerät.")
     +grp(srow('data-go="theme"',"Darstellung",THN[th])+srow('data-go="des"',"Farbwelt",`<i class="sdot sm" style="background:var(--acc)"></i> `+dsx[1])+srow('data-go="font"',"Schrift",(FONTS.find(x=>x[0]===fk)||FONTS[0])[1])+srow('data-go="me"',"Ich bin",me||"Keine Angabe")+srow('data-go="fun"',"Sprüche und GIFs",funOn()?"An":"Aus"))
     +`<p class="sgt sgh">Für alle im Haushalt</p>`+cap("Änderungen hier gelten für alle, die den Planner nutzen.")
     +`<p class="sgt">Aufgaben</p>`+grp(srow(`data-act="arch"${dn?"":" disabled"}`,"Erledigte archivieren",dn?String(dn):"Keine",null,false)+srow('data-act="open"',"Archiv und Papierkorb",A+T?(A+T)+(A+T===1?" Eintrag":" Einträge"):"Leer"));
    const hi=haInfo;
    if(hi){const n=(hi.notify||[]).length;
      h+=`<p class="sgt">Home Assistant</p>`+grp(
        srow("",`Verbindung`,hi.api?"Aktiv":"Nicht verfügbar",null,false)
       +(hi.api?srow('data-go="rem"',`Erinnerung`,n?n+" Gerät"+(n===1?"":"e")+" · "+esc(hi.time)+" Uhr":"Aus"):srow("",`Erinnerung`,"Aus",null,false))
       +(hi.api?srow('data-go="alexa"',`Alexa`,hi.alexa?(hi.echos?hi.echos+" Echo"+(hi.echos===1?"":"s"):"An"):"Aus"):"")
       +srow('data-go="show"',`Anzeige für Echo Show`,"Link")
       +srow('data-go="ki"',`KI-Assistent`,hi.ai?"Gemini":"Aus")
       +srow("","Sensoren",hi.sensors?"Aktiv":"Aus",null,false)
       +srow(`data-act="hatest"${hi.api&&n?"":" disabled"}`,"Testnachricht senden",null,null,false))}
    if(matchMedia("(hover:hover)").matches)h+=`<p class="sgt">Hilfe</p>`+grp(srow('data-go="keys"',"Tastaturkürzel"));
  }else if(sPage==="rem"){
    const sel=new Set((haInfo&&haInfo.notify)||[]),av=haAvail;
    if(av===null)h=cap("Geräte werden geladen …");
    else{const names=[...new Set([...av,...sel])];
      const nw=(haInfo&&haInfo.nwho)||{};
      h=`<p class="sgt">Geräte</p>`+(names.length?grp(names.map(x=>sopt(`data-set="ntf:${x}"`,esc(ntfName(x)),sel.has(x))).join("")):cap("Es wurde kein Gerät gefunden. Installiere die Home-Assistant-App auf dem Handy oder iPad und melde dich an."))
       +cap("Gewählte Geräte bekommen jeden Tag eine Erinnerung an fällige und überfällige Aufgaben, mit Knöpfen zum Abhaken. Ohne Auswahl ist die Erinnerung aus.")
       +(sel.size?`<p class="sgt">Erinnert wird an Aufgaben von</p>`+grp([...sel].map(x=>srow(`data-nw="${esc(x)}"`,esc(ntfName(x)),nw[x]?esc(nw[x]):"Allen")).join(""))
         +cap("Jedes Gerät bekommt nur die Aufgaben seiner Person, dazu Aufgaben ohne Zuständigkeit. Der Planner ordnet Geräte mit Namen im Gerätenamen automatisch zu (z. B. „iPhone von Lasse“ → Lasse). Antippen zum Ändern."):"")
       +grp(srow('data-go="remt"',"Uhrzeit",esc((haInfo&&haInfo.time)||"08:00")+" Uhr")+srow(`data-act="hatest"${sel.size?"":" disabled"}`,"Testnachricht senden",null,null,false))}
  }else if(sPage==="alexa"){
    const hi=haInfo||{},on=!!hi.alexa;
    h=grp(sopt('data-set="alexa:1"',"An",on)+sopt('data-set="alexa:0"',"Aus",!on))
     +(on?cap(hi.echos?`${hi.echos} Echo-Gerät${hi.echos===1?"":"e"} gefunden. Der Planner hört auf Befehle, die mit „Planner“ beginnen.`:hi.wsok?"Noch kein Echo gefunden. Ist die Integration „Alexa Devices“ in Home Assistant eingerichtet? Neue Geräte erkennt der Planner spätestens nach 30 Minuten.":"Die Verbindung zu Home Assistant wird gerade aufgebaut …"):"")
     +`<p class="sgt">So sprichst du mit dem Planner</p>`+grp(
        srow("","„Alexa, Planner Rasen mähen am Samstag“",null,null,false)
       +srow("","„Alexa, Planner was steht heute an“",null,null,false)
       +srow("","„Alexa, Planner Woche“",null,null,false)
       +srow("","„Alexa, Planner Fenster putzen ist erledigt“",null,null,false))
     +cap("Auch möglich: „Tag Garten“, „Projekt Haus“, „Priorität eins“, „in drei Tagen“, „am zwölften Dezember“. Alexa sagt zuerst kurz, dass sie das nicht kennt, danach antwortet der Planner auf demselben Echo. Erkennt Alexa deine Stimme (Stimmprofil), wird die Aufgabe dir zugewiesen.")
     +`<p class="sgt">Einrichtung (einmalig)</p>`+cap("In Home Assistant: Einstellungen → Geräte & Dienste → Integration hinzufügen → „Alexa Devices“. Mit dem Amazon-Konto anmelden. Amazon verlangt dafür die Zwei-Faktor-Anmeldung per Authenticator-App (nicht per SMS). Danach hier „An“ wählen.");
  }else if(sPage==="show"){
    const base=location.protocol==="http:"&&location.port==="8099"?location.origin:"http://"+(location.hostname&&!/^\d+\.\d+\.\d+\.\d+$/.test(location.hostname)&&location.hostname!=="localhost"?"IP-von-Home-Assistant":location.hostname)+":8099",me=prefGet("me")||"";
    const url=base+"/?anzeige"+(me?"&wer="+encodeURIComponent(me):"")+"&dunkel";
    h=cap("Eine ruhige Übersicht für den Echo Show 5 oder ein Tablet an der Wand: Uhrzeit, heute fällige und überfällige Aufgaben, die nächsten Termine. Sie aktualisiert sich von selbst, abhaken geht per Tippen auf den Kreis.")
     +`<p class="sgt">Adresse</p><div class="sgrp kin"><input id="show_url" type="text" readonly value="${esc(url)}" aria-label="Adresse der Anzeige"></div>`
     +grp(srow('data-act="showcopy"',"<b class=\"acc\">Adresse kopieren</b>",null,null,false)+srow('data-act="showopen"',"Hier ansehen",null,null,false))
     +cap("Am Echo Show: „Alexa, öffne Silk“ (oder „Alexa, öffne Browser“), die Adresse eingeben und als Lesezeichen speichern. Den Teil „&wer=…“ weglassen für alle Personen, „&dunkel“ weglassen für hell. Funktioniert nur im Heimnetz und braucht Port 8099. Hinweis: Der Echo Show kehrt nach einer Weile zu seinem Startbildschirm zurück, das kann der Planner nicht verhindern.");
  }else if(sPage==="fun"){
    const hi=haInfo||{},on=funOn();
    h=`<p class="sgt">Nur für dich</p>`+grp(sopt('data-set="fun:1"',"An",on)+sopt('data-set="fun:0"',"Aus",!on))
     +cap("Sprüche, GIF des Tages und Konfetti auf der Startseite. Liste, Tafel, Zeitstrahl und Kalender bleiben immer sachlich.");
    if(haInfo){h+=`<p class="sgt">GIF des Tages · für alle</p>`+(GIFS[gifKind]&&GIFS[gifKind].url?`<div class="gifprev"><img src="${esc(GIFS[gifKind].url)}" alt=""><small>Gerade zu sehen: ${esc(GIFS[gifKind].name||"")} · über GIPHY</small></div>`:"")
       +`<div class="sgrp kin"><input id="gif_key" type="text" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" placeholder="${hi.giphy?"GIPHY-Schlüssel ist eingetragen":"GIPHY-Schlüssel einfügen"}" aria-label="GIPHY-Schlüssel"></div>`
       +grp(srow('data-act="gifsave"',"<b class=\"acc\">Schlüssel sichern</b>",null,null,false)+(hi.giphy?srow('data-act="gifnew"',"Heute andere GIFs",null,null,false)+srow('data-act="gifdel"',"<span class=\"bad\">Schlüssel entfernen</span>",null,null,false):""))
       +cap("Für jede Situation des Tages (alles erledigt, mehrere Tage am Stück, etwas überfällig, noch nichts erledigt, schon einiges geschafft) gibt es höchstens ein GIF am Tag, für alle dasselbe. Gezeigt werden nur bestehende Memes von GIPHY. Einen kostenlosen Schlüssel gibt es auf developers.giphy.com unter „Create an App“ → „API“. Dieser Schlüssel ist für den Browser bestimmt und wird deshalb an die App übertragen, anders als der Gemini-Schlüssel.")
       +`<p class="sgt">Eigene Suchbegriffe</p><div class="sgrp kin"><input id="gif_terms" type="text" autocomplete="off" value="${esc(((hi.gifterms)||[]).join(", "))}" placeholder="z. B. stromberg finger, dog zoomies" aria-label="Eigene GIF-Suchbegriffe"></div>`
       +grp(srow('data-act="giftermsave"',"<b class=\"acc\">Suchbegriffe sichern</b>",null,null,false))
       +cap("Mit Komma trennen. Der Planner wechselt täglich zwischen eingebauten Themen (Büro-Comedy, Zeichentrick, Gaming, Fußball, Tiere) und euren Begriffen. Mit Gemini-Schlüssel wählt die KI einmal am Tag passende bekannte Memes für jede Lage aus (eine Anfrage).")}
  }else if(sPage==="ki"){
    const hi=haInfo||{},on=!!hi.ai;
    const au=hi.aiuse||{used:0,limit:100};
    h=grp(srow("","Status",on?(au.blocked?"Ruht bis morgen":"Aktiv"):"Aus",null,false)+(on?srow("","Heute genutzt",`${au.used} von ${au.limit}`,null,false):"")+srow(`data-act="kitest"${on?"":" disabled"}`,"Verbindung testen",null,null,false))
     +`<p class="sgt">Gemini-Schlüssel</p><div class="sgrp kin"><input id="ki_key" type="text" inputmode="text" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" enterkeyhint="done" placeholder="${hi.aiapp?"Neuen Schlüssel einfügen":"AQ.… oder AIza…"}" aria-label="Gemini-Schlüssel"></div>`
     +(kiMsg?`<p class="scap kimsg${kiMsg[1]?" bad":" ok"}">${esc(kiMsg[0])}</p>`:"")
     +grp(srow('data-act="kipaste"',"Aus Zwischenablage einfügen",null,null,false)+srow('data-act="kisave"',"<b class=\"acc\">Schlüssel sichern</b>",null,null,false))
     +cap("Gilt für alle, die den Planner über diesen Home Assistant nutzen, auf jedem Gerät. Gespeichert wird er nur auf dem Home Assistant und hier nie wieder angezeigt. Alternativ in Home Assistant unter Add-on → Konfiguration → gemini_api_key. Kostenlos erstellen unter aistudio.google.com/apikey.")
     +(hi.aiapp?grp(srow('data-act="kidel"',"<span class=\"bad\">Schlüssel entfernen</span>",null,null,false)):"")
     +`<p class="sgt">Modell</p>`+grp([["gemini-flash-lite-latest","Flash-Lite","schnell, größtes Gratis-Kontingent"],["gemini-flash-latest","Flash","gründlicher, kleineres Kontingent"]].map(([k,l,d])=>sopt(`data-set="aimodel:${k}"`,`${l}<small>${d}</small>`,(hi.model||"gemini-flash-lite-latest")===k)).join(""))
     +cap("Die KI arbeitet nur auf Knopfdruck („Mit KI ausfüllen“) und einmal für neue Tag-Symbole. Der Planner begrenzt sie selbst: Flash-Lite höchstens 100, Flash höchstens 15 Anfragen am Tag, 20 pro Stunde, weit unter Googles Gratis-Grenze. Meldet Google trotzdem ein Limit, ruht sie bis morgen. Gesendet wird nur der Aufgabentext."+(hi.aicfg&&hi.aiapp?" Der hier gesicherte Schlüssel hat Vorrang vor dem aus der Add-on-Konfiguration.":""));
  }else if(sPage==="remt"){
    h=grp(REMT.map(t=>sopt(`data-set="rtime:${t}"`,t+" Uhr",t===(haInfo&&haInfo.time))).join(""));
  }else if(sPage==="theme"){
    h=PREV+grp(Object.keys(THN).map(k=>sopt(`data-set="theme:${k}"`,THN[k],k===th)).join(""))+cap("Automatisch folgt der Einstellung deines Geräts.");
  }else if(sPage==="des"){
    h=PREV+grp(DES.map(([k,n,dsc,l,d])=>sopt(`data-set="des:${k}"`,`${n}<small>${dsc}</small>`,k===(dsx_(ds)),dpHtml(l,d))).join(""))+cap("Jede Farbwelt ist für Hell und Dunkel abgestimmt und auf gute Lesbarkeit geprüft. Die Statusfarben bleiben überall gleich.");
  }else if(sPage==="font"){
    h=PREV+grp(FONTS.map(f=>sopt(`data-set="font:${f[0]}"`,`${f[1]}<small>${f[4]}</small>`,f[0]===((FONTS.find(x=>x[0]===fk)||FONTS[0])[0]),"",`font-family:${f[3].replace(/"/g,"&quot;")}`)).join(""));
  }else if(sPage==="me"){
    h=grp([["","Keine Angabe"],["Lasse","Lasse"],["Melanie","Melanie"]].map(([k,n])=>sopt(`data-set="me:${k}"`,n,k===me)).join(""))+cap("Damit weiß die App, welche Aufgaben deine sind.");
  }else if(sPage==="keys"){
    h=`<dl class="keys"><dt>N</dt><dd>Neue Aufgabe</dd><dt>/</dt><dd>Suchen</dd><dt>1 – 5</dt><dd>Start, Liste, Tafel, Zeitstrahl, Kalender</dd><dt>S</dt><dd>Mehrfachauswahl</dd><dt>A</dt><dd>Alle auswählen</dd><dt>Entf</dt><dd>Auswahl löschen</dd><dt>H</dt><dd>Zeitstrahl: zu Heute</dd><dt>Esc</dt><dd>Auswahl beenden</dd></dl>`;
  }
  $("s_body").innerHTML=h;
}
function openSettings(){sPage="main";drawSettings();$("dls").showModal();$("dls").scrollTop=0}
$("cfg").onclick=openSettings;$("s_close").onclick=()=>$("dls").close();
$("s_body").addEventListener("keydown",e=>{if(e.target.id==="ki_key"&&e.key==="Enter"){e.preventDefault();const b=document.querySelector('#s_body [data-act="kisave"]');if(b)b.click()}});
$("s_back").onclick=()=>{sPage=sPage==="remt"?"rem":"main";drawSettings();$("dls").scrollTop=0};
$("s_body").onclick=async e=>{
  const b=e.target.closest("button");if(!b||b.disabled)return;const d=b.dataset;
  if(d.nw){const sv=d.nw,cur=((haInfo&&haInfo.nwho)||{})[sv]||"";
    const v=await sheet("Erinnerung auf „"+ntfName(sv)+"“ für",[{items:[...allWho().map(w=>({t:w,v:w,cur:w===cur})),{t:"Alle Aufgaben",v:"__all",cur:!cur}]}]);
    if(v){await haSave({notify_who:{[sv]:v==="__all"?"":v}});drawSettings()}return}
  if(d.go){sPage=d.go;if(d.go==="ki")kiMsg=null;if(d.go==="rem"&&haAvail===null)loadAvail();drawSettings();$("dls").scrollTop=0;return}
  if(d.set){const i=d.set.indexOf(":"),k=d.set.slice(0,i),v=d.set.slice(i+1);
    if(k==="theme"){prefSet("theme",v);applyTheme()}else if(k==="des"){prefSet("design",v);prefSet("acc","");applyTheme()}
    else if(k==="ntf"){const cur=new Set((haInfo&&haInfo.notify)||[]);cur.has(v)?cur.delete(v):cur.add(v);await haSave({notify:[...cur]})}
    else if(k==="rtime"){await haSave({time:v});sPage="rem"}
    else if(k==="aimodel")await haSave({ai_model:v});
    else if(k==="alexa"){await haSave({alexa:v==="1"});setTimeout(async()=>{try{if(typeof pull==="function")await pull(true)}catch(_){}if(sPage==="alexa")drawSettings()},6000)}
    else if(k==="fun"){prefSet("fun",v==="1"?"":"0");render()}
    else if(k==="acc"){prefSet("acc",v);applyTheme()}else if(k==="font"){prefSet("font",v);applyFont()}else if(k==="me")prefSet("me",v);
    drawSettings();return}
  if(d.act==="arch"){const L=tasks.filter(t=>t.status==="done");if(!L.length)return;await saveMany(L.map(t=>({...t,arch:true})));$("dls").close();toast(L.length+" erledigte archiviert",()=>saveMany(L))}
  else if(d.act==="open"){$("dls").close();openArch()}
  else if(d.act==="gifsave"||d.act==="gifdel"){const k=d.act==="gifdel"?"":$("gif_key").value.trim();if(d.act==="gifsave"&&!k){toast("Erst den Schlüssel einfügen");return}
    try{await haSave({giphy_key:k});toast(k?"GIPHY-Schlüssel gesichert":"GIPHY-Schlüssel entfernt");if(k){GIFS={};gifAsked=false;render()}}catch(e){toast("Speichern fehlgeschlagen")}drawSettings()}
  else if(d.act==="giftermsave"){await haSave({gif_terms:$("gif_terms").value.split(",").map(x=>x.trim()).filter(Boolean)});toast("Suchbegriffe gesichert");drawSettings()}
  else if(d.act==="gifnew"){try{await api("api/gif",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({reset:true})});GIFS={};gifAsked=false;try{localStorage.removeItem("haus-gifseen")}catch(_){}$("dls").close();render()}catch(_){toast("Kein neues GIF gefunden")}}
  else if(d.act==="showcopy"){const u=$("show_url").value;try{await navigator.clipboard.writeText(u);toast("Adresse kopiert")}catch(_){$("show_url").focus();$("show_url").select();toast("Adresse markiert, bitte kopieren")}}
  else if(d.act==="showopen"){window.open(location.pathname+"?anzeige"+(prefGet("me")?"&wer="+encodeURIComponent(prefGet("me")):""),"_blank")}
  else if(d.act==="kipaste"){try{const t=await navigator.clipboard.readText();$("ki_key").value=t.replace(/\s+/g,"");toast(t.trim()?"Eingefügt, jetzt sichern":"Zwischenablage ist leer")}catch(e){$("ki_key").focus();toast("Bitte lange ins Feld tippen und „Einsetzen“ wählen")}}
  else if(d.act==="kisave"){const k=$("ki_key").value.replace(/\s+/g,"").replace(/^["'„“]+|["'„“”]+$/g,"");
    if(!k){kiMsg=["Erst den Schlüssel ins Feld einfügen.",1];drawSettings();return}
    if(!/^[A-Za-z0-9._-]{20,200}$/.test(k)){kiMsg=[`Das sieht nicht nach einem vollständigen Gemini-Schlüssel aus (${k.length} Zeichen). Er beginnt mit „AIza“ oder „AQ.“ und enthält keine Leerzeichen.`,1];drawSettings();return}
    kiMsg=["Schlüssel wird gesichert und geprüft …",0];drawSettings();
    try{const r=await fetch("api/ha-settings",{method:"POST",headers:{"Content-Type":"application/json","X-Planner":"1"},body:JSON.stringify({ai_key:k})}),j=await r.json().catch(()=>({}));
      if(!r.ok){kiMsg=[j.error||"Speichern fehlgeschlagen ("+r.status+").",1];drawSettings();return}
      if(j.ha)haInfo=j.ha;const err=await kiCheck();
      kiMsg=err?["Gesichert, aber die Prüfung ist fehlgeschlagen: "+err,1]:["Gesichert. Die KI antwortet, alles ist bereit.",0]}
    catch(e){kiMsg=["Der Planner-Server ist nicht erreichbar.",1]}
    drawSettings()}
  else if(d.act==="kidel"){if(!await confirmSheet("Gemini-Schlüssel entfernen?","Entfernen"))return;await haSave({ai_key:""});kiMsg=["Schlüssel entfernt.",0];drawSettings()}
  else if(d.act==="kitest"){kiMsg=["Teste …",0];drawSettings();const err=await kiCheck();kiMsg=err?["Prüfung fehlgeschlagen: "+err,1]:["Die KI antwortet, alles ist bereit.",0];drawSettings()}
  else if(d.act==="hatest"){try{const r=await api("api/ha-test",{method:"POST",headers:{"Content-Type":"application/json"},body:"{}"});$("dls").close();toast(r.ok?"Testnachricht gesendet":"Fehlgeschlagen: "+r.error)}catch(e){toast("Server nicht erreichbar")}}
};

