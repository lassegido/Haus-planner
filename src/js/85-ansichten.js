function enter(){const m=$("main");m.classList.add("enter");clearTimeout(enterT);enterT=setTimeout(()=>m.classList.remove("enter"),1300);animateNums()}
function animateNums(){if(reduced())return;document.querySelectorAll("[data-n]").forEach(el=>{const n=+el.dataset.n;if(!n)return;const t0=performance.now(),step=t=>{const k=Math.min(1,(t-t0)/800),e=1-Math.pow(1-k,3);el.textContent=Math.round(n*e);if(k<1)requestAnimationFrame(step)};requestAnimationFrame(step)})}
function rel(t){const d=dn(t.end)-today();return d<0?`${-d} ${-d===1?"Tag":"Tage"} überfällig`:d===0?"heute":d===1?"morgen":d<=14?`in ${d} Tagen`:fd(t.end)}
function hrow(t,i){if(t.pre)return`<div class="hrow pre" data-id="${t.id}" style="--i:${Math.min(i,8)}"><span class="ring pre" aria-hidden="true"></span><div class="hm"><div class="ht">${esc(t.title)}</div><div class="hs">${["wiederholt sich, sobald heute abgehakt",t.who].filter(Boolean).map(esc).join(" · ")}</div></div><span class="hd">morgen</span></div>`;
  return`<div class="hrow" data-id="${t.id}" style="--i:${Math.min(i,8)}"><button class="ring ${t.status}" data-adv="${t.id}" aria-label="Status: ${ST[t.status]}. Weiterschalten"></button><div class="hm"><div class="ht">${esc(t.title)}</div><div class="hs">${[t.proj,...tgs(t),t.who].filter(Boolean).map(esc).join(" · ")||"&nbsp;"}</div></div><span class="hd ${isLate(t)?"late":""}">${rel(t)}</span></div>`}
/* 1.33: Tag, an dem eine Aufgabe erledigt wurde (aus dem Verlauf, Ortszeit); NaN, wenn unbekannt */
const DONE_RX=/^Status: (?:[^→]*→ )?Erledigt(?: \(|$)/;
/* Abgeschlossen = erledigt oder nicht geschafft (1.42) */
const CLOSE_RX=/^Status: (?:[^→]*→ )?(?:Erledigt|Nicht geschafft)(?: \(|$)/;
/* Zeitpunkt des Abschließens (UTC aus dem Verlauf), sonst das Ende; für „zuletzt abgeschlossen zuerst“ im Board */
function closedAt(t){const L=t.log||[];for(let i=L.length-1;i>=0;i--){const x=L[i];if(x.k==="h"&&CLOSE_RX.test(x.x||""))return String(x.t)}return String(t.end||"")}
function doneDay(t){const L=t.log||[];for(let i=L.length-1;i>=0;i--){const x=L[i];if(x.k==="h"&&CLOSE_RX.test(x.x||"")){const d=new Date(String(x.t)+"Z");return isNaN(d)?NaN:Date.UTC(d.getFullYear(),d.getMonth(),d.getDate())/864e5}}return NaN}
function homeBody(tasks,allT){
  const T=today(),n=tasks.filter(t=>!isFail(t)).length,d=tasks.filter(isOk).length;
  const doing=tasks.filter(t=>t.status==="doing").length,over=tasks.filter(isLate).sort((a,b)=>dn(a.end)-dn(b.end)),blk=tasks.filter(isBlocked).length;
  /* 1.44: Morgen = beginnt oder ist fällig morgen (lange Aufgaben, die morgen weder anfangen noch enden, nicht).
     Wiederholungen von heute gibt es morgen erst, wenn die heutige abgehakt ist; sie stehen deshalb als Vorschau dabei. */
  const M=T+1,tmrL=tasks.filter(t=>t.status!=="done"&&!isLate(t)&&dn(t.start)<=M&&dn(t.end)>=M&&(dn(t.start)===M||dn(t.end)===M)),
    tmrIds=new Set(tmrL.map(t=>t.title+"|"+(t.who||""))),
    tmrPre=tasks.filter(t=>t.status!=="done"&&t.rec&&!t.spawned&&dn(t.end)<M).map(t=>{const n=nextOcc(t);return n&&dn(n.start)<=M&&dn(n.end)>=M&&!tmrIds.has(t.title+"|"+(t.who||""))?{...t,start:n.start,end:n.end,pre:1}:null}).filter(Boolean),
    week=[...tmrL,...tmrPre].sort((a,b)=>dn(a.end)-dn(b.end)||(a.pre||0)-(b.pre||0)||a.title.localeCompare(b.title,"de"));
  const nx=tasks.filter(t=>t.status!=="done"&&dn(t.end)>=T).sort((a,b)=>dn(a.end)-dn(b.end))[0],C=326.7,open=n-d;
  const areas=allTags().filter(a=>tasks.some(t=>tgs(t).includes(a)));
  const bars=areas.map(a=>{const L=tasks.filter(t=>tgs(t).includes(a)&&!isFail(t)),x=L.filter(isOk).length;return`<div class="prg" style="--tc:${tcol(a)}"><span class="pn">${tIc(a)}${esc(a)}</span><div class="pb"><i style="width:${L.length?Math.round(x/L.length*100):0}%"></i></div><em>${x}/${L.length}</em></div>`}).join("");
  const names=allWho(),cnt=w=>allT.filter(t=>t.status!=="done"&&wl(t).includes(w)).length,mx=Math.max(1,...names.map(cnt));
  const who=names.map(w=>`<div class="prg"><span>${esc(w)}</span><div class="pb ${avc(w)}"><i style="width:${Math.round(cnt(w)/mx*100)}%"></i></div><em>${cnt(w)}</em></div>`).join("");
  const pjs=allProjs().filter(n=>tasks.some(t=>t.proj===n)),pbars=pjs.map(n=>{const L=tasks.filter(t=>t.proj===n&&!isFail(t)),x=L.filter(isOk).length;return`<div class="prg" style="--tc:${pcol(n)}"><span>${esc(n)}</span><div class="pb"><i style="width:${Math.round(x/L.length*100)}%"></i></div><em>${x}/${L.length}</em></div>`}).join("");
  let k=1;const P=(cls,h,c,body)=>`<section class="pnl ${cls}" style="--i:${k++}"><h3><span>${h}</span><em>${c}</em></h3>${body}</section>`;
  const byEnd=(a,b)=>dn(a.end)-dn(b.end)||dn(a.start)-dn(b.start),opn=tasks.filter(t=>t.status!=="done");
  /* 1.47: Für den Ring und „Heute“ zählt nur, was heute fällig ist (oder überfällig). Was heute läuft, aber später fällig ist,
     steht in der Liste darunter getrennt und zählt nicht. Wer eine fällige Aufgabe heute verschiebt, nimmt sie aus dem Ring. */
  const nowL=opn.filter(t=>!isLate(t)&&dn(t.start)<=T&&dn(t.end)>=T).sort(byEnd),dueL=nowL.filter(t=>dn(t.end)===T),runL=nowL.filter(t=>dn(t.end)>T),todayL=[...over,...dueL];
  const doingL=opn.filter(t=>t.status==="doing").sort(byEnd);
  /* Ring: nur heute (überfällig, heute anstehend, heute erledigt) der oben gewählten Person */
  const closedT=tasks.filter(t=>{if(t.status!=="done")return false;const dd=doneDay(t);return isNaN(dd)?dn(t.start)<=T&&dn(t.end)>=T:dd===T});
  const doneT=closedT.filter(t=>!t.fail),nf=closedT.length-doneT.length;
  const rd=doneT.length,rn=todayL.length+rd+nf,rpct=rn?Math.round(rd/rn*100):0,off=(C*(1-rpct/100)).toFixed(1);
  const ms=motStats(motScope());
  const NF=nf?` ${nf} nicht geschafft.`:"";
  const sub=!rn?"Für heute ist nichts geplant.":!todayL.length?(nf?NF.trim():"Alles für heute erledigt."):`Noch ${todayL.length} offen`+(over.length?`, davon ${over.length} überfällig.`:".")+NF;
  const TL={heute:["Heute",todayL,"var(--acc)",'<rect x="4" y="5.5" width="16" height="14.5" rx="2.5"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/><circle cx="12" cy="15" r="1.6" fill="currentColor" stroke="none"/>',"Für heute ist nichts geplant."],
    morgen:["Morgen",week,"#6F8796",'<rect x="4" y="5.5" width="16" height="14.5" rx="2.5"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4M10 13.5l2.5 2.5-2.5 2.5"/>',"Für morgen ist nichts geplant."],
    doing:["In Arbeit",doingL,"var(--sun)",'<circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 1 0 16z" fill="currentColor" stroke="none"/>',"Gerade ist nichts in Arbeit."],
    late:["Überfällig",over,"var(--brick)",'<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5v5.5M12 16.3v.2"/>',"Nichts überfällig."]};
  let ht="heute";try{ht=localStorage.getItem("haus-htile")||"heute"}catch(_){}if(!TL[ht])ht="heute";
  const tiles=`<div class="tiles">`+Object.entries(TL).map(([k,[l,L,c,ic]])=>`<button type="button" class="tile${k===ht?" on":""}" data-ht="${k}" style="--tc:${c}"><span class="ti2"><svg viewBox="0 0 24 24">${ic}</svg></span><b>${L.length}</b><span class="tl">${l}</span></button>`).join("")+`</div>`;
  const qa=`<section class="qadd"><div class="qbox"><svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg><input id="qadd" placeholder="Neue Aufgabe, z. B. Rasen mähen Sa" enterkeyhint="done" autocomplete="off" autocorrect="on" aria-label="Schnelleingabe"></div><div class="qprev" id="qprev"></div><div class="vsug qsug" id="qsug" role="list" aria-label="Frühere Aufgaben"></div><p class="qhint">Erkannt werden: heute · morgen · Sa · 12.12. · in 3 Tagen · bis Fr · #Tag · +Projekt · @Person · !1</p></section>`;
  const cur=TL[ht],LL=cur[1];
  const runH=ht==="heute"&&runL.length?`<h4 class="hsub2"><span>Läuft heute, fällig später</span><em>${runL.length}</em></h4>`+runL.slice(0,40).map((t,i)=>hrow(t,i+LL.length)).join(""):"";
  const list=`<section class="pnl hlist" style="--i:${k++}" aria-label="${cur[0]}">${LL.length?(runH?`<h4 class="hsub2 first"><span>Heute fällig</span><em>${LL.length}</em></h4>`:"")+LL.slice(0,40).map(hrow).join(""):`<div class="none">${runH?"Heute ist nichts fällig.":cur[4]}</div>`}${runH}</section>`;
  /* Lage für das Meme, in dieser Reihenfolge: alles erledigt → etwas überfällig → schon etwas geschafft → Serie läuft → noch nichts.
     Ist eine Lage gelöst (z. B. Überfälliges erledigt), greift die nächste und damit ein anderes GIF. */
  /* 1.45: Tageszeit zählt mit. Morgens (bis 11 Uhr) anspornen, mittags (bis 17 Uhr) anstupsen oder bestätigen, abends frech-ironisch
     oder Endspurt; ab 70 % „fast geschafft“. Jede Lage hat ihr eigenes GIF des Tages. */
  const ph=dayPhase(),offen=todayL.length;
  /* Nichts fällig = freier Tag (Lage „done“), egal zu welcher Uhrzeit */
  const kind=!rn?"done":!offen?(nf?(rd?"good":"start"):"done"):over.length?"late":rd&&rpct>=70?"fast":
    ph==="frueh"?(rd?"frueh_gut":ms.streak>=3?"streak":"frueh"):ph==="mittag"?(rd?"mittag_gut":"mittag"):(rpct>=30?"abend_gut":"abend");
  const A=n=>n===1?"Aufgabe":"Aufgaben",nOpen=todayL.length;
  /* Ein Satz, der motiviert und den Grund für das GIF mitliefert, ohne ihn zu erklären */
  const why={done:rn?(rn===1?"Erledigt. Genau so sieht ein guter Tag aus.":`Alle ${rn} erledigt. Das hast du dir verdient.`):"Heute ist nichts fällig. Genieß den freien Tag.",
    late:over.length===1?"Eine Sache ist liegen geblieben. Die holst du dir jetzt zurück.":`${over.length} Sachen sind liegen geblieben. Zeit für dein Comeback.`,
    good:nOpen?`${rd} geschafft, ${nOpen===1?"nur noch eine":"noch "+nOpen}. Du bist richtig drin.`:`${rd} geschafft, ${nf} nicht. Morgen holst du dir die volle Runde.`,
    streak:`${ms.streak} Tage am Stück. Heute ${nOpen===1?"noch eine":"noch "+nOpen}, dann hält die Serie.`,
    frueh:nOpen===1?"Eine Aufgabe heute. Kurz erledigen, dann ist der Tag gewonnen.":`${nOpen} Aufgaben heute. Klingt viel, du schaffst das.`,
    frueh_gut:`${rd} schon weg, und es ist noch nicht mal Mittag. Starker Start.`,
    mittag:nOpen===1?"Mittag, und die eine Aufgabe wartet noch. Wie wär’s?":`Mittag, und noch alle ${nOpen} offen. Willst du nicht mal loslegen?`,
    mittag_gut:`${rd} geschafft, ${nOpen===1?"nur noch eine":"noch "+nOpen}. Du bist auf einem guten Weg.`,
    abend:rd?`Erst ${rd} von ${rn}, und es ist Abend. Digga, das wird knapp.`:`Abend, und noch alle ${nOpen} offen. Digga, du wirst es vermasseln … oder?`,
    abend_gut:`${rd} geschafft, ${nOpen===1?"nur noch eine":"noch "+nOpen}. Endspurt, das ziehst du durch.`,
    fast:`Nur noch ${nOpen===1?"eine":nOpen}. Du hast es fast geschafft.`,
    start:!nOpen&&nf?"Heute hat’s nicht geklappt. Morgen holst du dir die volle Runde.":nOpen===1?"Eine Aufgabe für heute. Kurz erledigen, dann ist der Tag gewonnen.":`${nOpen} Aufgaben für heute. Fang mit der ersten an, der Rest läuft.`}[kind];
  /* Startseite (1.37), ein Weg von oben nach unten:
     1. Ankommen: Begrüßung, Tagesstand, Serie, Meme zur Lage (eine Karte)
     2. Handeln: Eingabe, dann die Liste mit Umschalter Heute / Morgen / In Arbeit / Überfällig
     3. Dranbleiben: nächstes Abzeichen in einer Zeile
     4. Überblick: Projekte, Tags, Personen, Gemeinsam (zugeklappt) */
  const ring=`<div class="hring"><svg viewBox="0 0 120 120" aria-hidden="true"><defs><linearGradient id="rgG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" style="stop-color:var(--acc)"/><stop offset=".55" style="stop-color:var(--acc2)"/><stop offset="1" style="stop-color:var(--acc3)"/></linearGradient></defs><circle class="rt" cx="60" cy="60" r="52"/><circle class="rg" cx="60" cy="60" r="52" stroke-dasharray="${C}" stroke-dashoffset="${off}" style="--off:${off}" transform="rotate(-90 60 60)"/></svg><div class="hn">${rn?`<span data-n="${rpct}">${rpct}</span><i>%</i>`:"<span>–</span>"}</div></div>`;
  const me=prefGet("me")||"",hw=homeW(),who1=hw==="__all"?"":hw===me?"":hw;
  const hero=`<section class="hero game" style="--i:0">${ring}<div class="hbody"><small class="eyebrow">${who1?"Tag von "+esc(who1):greet()+(me?", "+esc(me):"")}</small><div class="hh">${rn?`${rd} von ${rn} erledigt`:"Heute ist nichts fällig"}</div><div class="hsub">${sub}</div><div class="hmeta">${streakHtml(ms)}${weekHtml(ms)}</div></div>${funHtml(kind,{n:ms.streak,late:over.length,open:todayL.length,why})}</section>`;
  const seg=`<div class="hseg" role="tablist">`+Object.entries(TL).map(([k,[l,L]])=>`<button type="button" role="tab" class="${k===ht?"on":""}${k==="late"&&L.length?" hot":""}" data-ht="${k}" aria-selected="${k===ht}">${l}<b>${L.length}</b></button>`).join("")+`</div>`;
  const ovw=`<details class="pnl ovw" style="--i:${k++}"${ovwOpen?" open":""}><summary><span>Überblick</span><em>Projekte, Tags, Personen, gemeinsame Woche</em></summary>`
    +(pjs.length?P("","Projekte",pjs.length,pbars):"")+P("","Tags",areas.length,bars||'<div class="none">Noch keine Tags.</div>')+P("","Offen je Person",open,who)+motPanel(k++)+`</details>`;
  return`<div class="home">${hero}${qa}${seg}${list}${badgeCard(ms)}${ovw}</div>`}
let ovwOpen=false;
document.addEventListener("toggle",e=>{if(e.target.classList&&e.target.classList.contains("ovw"))ovwOpen=e.target.open},true);

const homeW=()=>{let v=null;try{v=localStorage.getItem("haus-hwho")}catch(_){}const me=prefGet("me")||"";return v||me||"__all"};
function home(){
  const hw=homeW(),me=prefGet("me")||"",who=allWho(),opts=[...(me?[me]:[]),...who.filter(w=>w!==me)];
  const sc=hw==="__all"?tasks:tasks.filter(t=>wl(t).includes(hw));
  const pick=`<div class="hpick" role="group" aria-label="Aufgaben von">`+opts.map(w=>`<button type="button" data-hw="${esc(w)}" class="${w===hw?"on":""}">${w===me?"Meine":esc(w)}</button>`).join("")+`<button type="button" data-hw="__all" class="${hw==="__all"?"on":""}">Alle</button></div>`;
  return homeBody(sc,tasks).replace('<div class="home">','<div class="home">'+pick)}
function filtered(){
  const q=$("q").value.toLowerCase(),w=$("fw").value;
  return tasks.filter(t=>tagOk(t)&&(!w||(w==="__none"?!t.who:wl(t).includes(w)))&&(!q||(t.title+" "+tgs(t).join(" ")+" "+(t.who||"")).toLowerCase().includes(q)))
    .sort((x,y)=>(sortm==="prio"?((x.prio||9)-(y.prio||9)):0)||dn(x.start)-dn(y.start)||dn(x.end)-dn(y.end));
}
let renderedView=null;
const snap=()=>({v:renderedView,y:scrollY,m:$("main").scrollTop,b:(document.querySelector(".board")||{}).scrollLeft,g:(document.querySelector(".gwrap")||{}).scrollLeft,gy:(document.querySelector(".gwrap")||{}).scrollTop});
function glResize(){
  const g=document.querySelector(".gwrap"),h=g&&g.querySelector(".glg"),gl=g&&g.querySelector(".gl");if(!h)return;
  const lim=w=>Math.round(Math.max(52,Math.min(w,g.clientWidth*.7)));
  const set=w=>{if(w==null){g.style.removeProperty("--glw")}else g.style.setProperty("--glw",lim(w)+"px")};
  const saved=parseFloat(prefGet("glw"));if(saved>0)set(saved);
  let st=null;
  h.onpointerdown=e=>{e.preventDefault();e.stopPropagation();st={x:e.clientX,w:gl.offsetWidth};h.setPointerCapture(e.pointerId);h.classList.add("on");document.body.classList.add("glres")};
  h.onpointermove=e=>{if(!st)return;set(st.w+e.clientX-st.x)};
  const end=()=>{if(!st)return;st=null;h.classList.remove("on");document.body.classList.remove("glres");prefSet("glw",String(gl.offsetWidth))};
  h.onpointerup=end;h.onpointercancel=end;
  h.ondblclick=()=>{set(null);prefSet("glw","")};
  h.onclick=e=>e.stopPropagation();
}
function gToday(smooth){const g=document.querySelector(".gwrap"),sv=g&&g.querySelector(".gb");if(!sv)return;const l=g.querySelector(".gl").offsetWidth;g.scrollTo({left:Math.max(0,(+sv.dataset.tx||0)-(g.clientWidth-l)*.3),behavior:smooth?"smooth":"auto"})}
function stickyLabels(){const g=document.querySelector(".gwrap");if(!g)return;const x0=g.scrollLeft;g.querySelectorAll(".l1").forEach(t=>{const a=+t.dataset.a,b=+t.dataset.b,w=t.getComputedTextLength?t.getComputedTextLength():60;t.setAttribute("x",Math.max(a+10,Math.min(x0+10,b-w-10)))})}
/* 1.47: Nach dem Neuzeichnen an derselben Stelle bleiben. Zeilen mit content-visibility und Bilder bekommen ihre Höhe erst
   nach und nach; bis dahin klemmt der Browser die Scrollposition. Deshalb mehrmals nachziehen, solange niemand selbst scrollt. */
let userScrollAt=0;["wheel","touchstart","keydown"].forEach(ev=>addEventListener(ev,()=>{userScrollAt=Date.now()},{passive:true}));
function keepScroll(m,y){const t0=Date.now(),fix=()=>{if(userScrollAt>t0||Math.abs(m.scrollTop-y)<1)return;m.scrollTop=y};
  requestAnimationFrame(()=>{fix();requestAnimationFrame(fix)});[60,160,400].forEach(ms=>setTimeout(fix,ms))}
function after(o){
  const entering=o.v!==view;renderedView=view;if(entering)enter();setTimeout(()=>{lastMoved=null},500);
  if(view==="board"){$("main").insertAdjacentHTML("beforeend",'<div class="dots"><i class="on"></i><i></i><i></i></div>');
    const b=document.querySelector(".board"),dots=[...document.querySelectorAll(".dots i")];
    if(b){const mark=()=>{const w=b.firstElementChild.offsetWidth+12,i=Math.max(0,Math.min(2,Math.round(b.scrollLeft/w)));dots.forEach((d,k)=>d.classList.toggle("on",k===i))};b.onscroll=mark;if(o.v==="board"&&o.b)b.scrollLeft=o.b;mark()}}
  const g=document.querySelector(".gwrap");
  if(o.v===view){const m=$("main");m.scrollTop=o.m;scrollTo(0,o.y);keepScroll(m,o.m);if(g&&o.g!=null){g.scrollLeft=o.g;g.scrollTop=o.gy||0}}
  else if(g)gToday(false);
  if(g){g.onscroll=stickyLabels;stickyLabels();ganttDrag();glResize()}
}
const KQ=new URLSearchParams(location.search),KIOSK=KQ.has("anzeige");
if(KIOSK){document.documentElement.classList.add("kiosk");if(KQ.has("dunkel"))try{localStorage.setItem("haus-theme","dark")}catch(_){}else if(KQ.has("hell"))try{localStorage.setItem("haus-theme","light")}catch(_){}applyTheme();
  try{localStorage.setItem("haus-onb","1")}catch(_){}setInterval(()=>{const c=$("kclock");if(c)c.textContent=new Date().toLocaleTimeString("de-DE",{hour:"2-digit",minute:"2-digit"})},15000)}
function kiosk(){
  const T=today(),who=KQ.get("wer")||"",mine=t=>!who||wl(t).includes(who),opn=tasks.filter(t=>t.status!=="done"&&mine(t)),be=(a,b)=>dn(a.end)-dn(b.end);
  const late=opn.filter(isLate).sort(be),now=opn.filter(t=>!isLate(t)&&dn(t.start)<=T).sort(be),next=opn.filter(t=>dn(t.start)>T&&dn(t.start)<=T+7).sort((a,b)=>dn(a.start)-dn(b.start));
  const L=[...late,...now],row=t=>`<div class="krow"><button class="ring ${t.status}" data-adv="${t.id}" aria-label="Status weiterschalten"></button><div class="km"><b>${esc(t.title)}</b><span>${[t.proj,...tgs(t),who?"":t.who].filter(Boolean).map(esc).join(" · ")}</span></div><em class="${isLate(t)?"late":""}">${rel(t)}</em></div>`;
  const nx=next.slice(0,Math.max(0,6-L.length));
  return`<div class="kio"><section class="kl"><div class="kclock" id="kclock">${new Date().toLocaleTimeString("de-DE",{hour:"2-digit",minute:"2-digit"})}</div><div class="kdate">${new Date().toLocaleDateString("de-DE",{weekday:"long",day:"numeric",month:"long"})}</div>
    <div class="kst"><div><b>${L.length}</b><span>heute</span></div><div class="${late.length?"hot":""}"><b>${late.length}</b><span>überfällig</span></div><div><b>${next.length}</b><span>7 Tage</span></div></div>${who?`<div class="kwho">${esc(who)}</div>`:""}</section>
    <section class="kr">${L.length?`<h3>Heute</h3>${L.slice(0,6).map(row).join("")}`:`<div class="kfree"><b>Für heute ist nichts geplant.</b><span>Genieß den Tag.</span></div>`}${nx.length?`<h3>Als Nächstes</h3>${nx.map(row).join("")}`:""}${L.length>6?`<p class="kmore">und ${L.length-6} weitere</p>`:""}</section></div>`}
function render(){
  tasks=RAW.filter(t=>!t.arch&&!t.del&&!t.inbox).map(t=>t.status==="backlog"?{...t,status:"todo"}:t);
  if(KIOSK){$("main").innerHTML=kiosk();document.querySelectorAll("[data-adv]").forEach(b=>b.onclick=e=>{e.stopPropagation();advance(b.dataset.adv)});return}
  if(!purged&&RAW.length){purged=true;const lim=iso(new Date(Date.now()-30*864e5));RAW.filter(t=>t.del&&t.delAt&&t.delAt<lim).forEach(t=>delTask(t.id))}
  for(const id of [...sel])if(!tasks.some(t=>t.id===id))sel.delete(id);
  const n=tasks.length,d=tasks.filter(isOk).length,nv=n-tasks.filter(isFail).length,pct=nv?Math.round(d/nv*100):0;
  const doing=tasks.filter(t=>t.status==="doing").length,late=tasks.filter(isLate).length,blk=tasks.filter(isBlocked).length,op=nv-d-doing;
  if(view!=="home"&&isPhone())$("sub").innerHTML=n?`${n} ${n===1?"Aufgabe":"Aufgaben"} · ${pct} % erledigt`+(late?` · <b class="hot">${late} überfällig</b>`:""):"Noch keine Aufgaben";
  else $("sub").textContent=new Date().toLocaleDateString("de-DE",{weekday:"long",day:"numeric",month:"long"});
  $("kpis").innerHTML=view==="home"?"":`<div class="kp"><div class="kn"><b><span data-n="${pct}">${pct}</span><i>%</i></b><span>erledigt · ${d} von ${nv}</span></div><div class="kn"><b data-n="${doing}">${doing}</b><span>in Arbeit</span></div><div class="kn ${late?"hot":""}"><b data-n="${late}">${late}</b><span>überfällig</span></div><div class="kn"><b data-n="${blk}">${blk}</b><span>blockiert</span></div></div>${n?`<div class="stripe" title="Erledigt · In Arbeit · Offen"><i class="s-x" style="flex:${d}"></i><i class="s-d" style="flex:${doing}"></i><i class="s-o" style="flex:${op}"></i></div>`:""}`;
  document.body.dataset.view=view;$("ttl").textContent=view==="home"?"Start":{board:"Board",list:"Liste",gantt:"Zeitstrahl",cal:"Kalender"}[view];
    const whos=allWho(),curw=$("fw").value;
  $("fw").innerHTML='<option value="">Alle Personen</option>'+whos.map(a=>`<option ${a===curw?"selected":""}>${esc(a)}</option>`).join("")+`<option value="__none" ${curw==="__none"?"selected":""}>Nicht zugewiesen</option>`;
  const fw2=$("fw").value,ch=(attr,val,label,c,on)=>`<button data-${attr}="${esc(val)}" class="${on?"on":""}"><span>${attr==="cw"&&val&&val!=="__none"?`<i class="wd ${avc(val)}"></i>`:""}${esc(label)}</span><em>${c}</em></button>`;
  $("chips").innerHTML=`<div class="cg"><h4>Wer</h4>${ch("cw","","Alle",n,!fw2)}${whos.map(w=>ch("cw",w,w,tasks.filter(t=>wl(t).includes(w)).length,w===fw2)).join("")}${ch("cw","__none","Nicht zugewiesen",tasks.filter(t=>!t.who).length,fw2==="__none")}</div>`;
  drawTbar();migrateReg();if(!iconTried)setTimeout(iconSync,1200);
  $("main").classList.toggle("g",view==="gantt"&&n>0);
  const old=snap(),list=filtered();
  const planOn=view==="cal"; /* Kalender (auch Planen mit Sammelkorb) zeigt immer sein Raster */
  if(!n&&view!=="home"&&!planOn){$("main").innerHTML='<div class="empty">Noch keine Aufgaben.<br><br><button class="btn" onclick="openDlg()">Erste Aufgabe anlegen</button></div>';return}
  if(view!=="home"&&!list.length&&!planOn){$("main").innerHTML='<div class="empty">Keine Aufgaben mit diesen Filtern.<br><br><button class="btn ghost" id="fclr">Filter zurücksetzen</button></div>';$("fclr").onclick=()=>{fClear();$("q").value="";render()};applySel();return}
  const qa0=$("qadd"),qv0=qa0?qa0.value:"",qf0=!!qa0&&document.activeElement===qa0,gif0=document.querySelector(".hero .gifbox img");
  {const pi=document.activeElement&&document.activeElement.dataset&&document.activeElement.dataset.pin;if(pi)planKeep={k:pi,v:document.activeElement.value}}
  $("main").innerHTML=view==="home"?home():view==="board"?board(list):view==="list"?table(list):view==="cal"?cal(list):gantt(list);
  /* 1.47: Das GIF nicht neu laden (sonst ist die Karte kurz niedriger und iOS springt nach oben) */
  {const g1=document.querySelector(".hero .gifbox img");if(gif0&&g1&&gif0.getAttribute("src")===g1.getAttribute("src"))g1.replaceWith(gif0)}
  bind();after(old);applySel();
  if(planKeep){const pi=document.querySelector(`[data-pin="${planKeep.k}"]`);if(pi){pi.value=planKeep.v||"";pi.focus({preventScroll:true})}planKeep=null}
  const qa1=$("qadd");if(qa1){qa1.value=qv0;if(qv0)$("qprev").innerHTML=qChips(parseQuick(qv0));if(qv0&&qf0)$("qsug").innerHTML=sugHtml(sugFind(qv0));if(qf0||qaddKeep){qa1.focus({preventScroll:true});qaddKeep=null}}
}
const avc=w=>/^melanie/i.test(w)?"am":/^lasse/i.test(w)?"al":"ao";
const pjh=t=>t.proj?`<div class="pjh" style="--tc:${pcol(t.proj)}"><i></i>${esc(t.proj)}</div>`:"";
const pb=t=>t.prio?`<span class="pr p${t.prio}" title="Prio ${t.prio}">P${t.prio}</span>`:"";
const cl=t=>{const a=t.checklist||[];return a.length?`<span class="ckc">${a.filter(x=>x.d).length}/${a.length}</span>`:""};
function card(t,s,i=0){
  const a=t.checklist||[],k=a.filter(x=>x.d).length,late=isLate(t),fl=isFail(t)?" fail":"";
  const tg=pb(t)+tgs(t).map(chip).join("")+(isBlocked(t)?'<span class="blk">blockiert</span>':"");
  return`<div class="card ${s}${fl}${t.id===lastMoved?" pop":""}"${t.prio?` data-pr="${t.prio}"`:""} draggable="true" data-id="${t.id}" style="--i:${Math.min(i,8)}">${pjh(t)}<div class="ch"><button class="ring ${s}${fl}" data-adv="${t.id}" aria-label="Status: ${stName(t)}. Weiterschalten"></button><div class="t">${esc(t.title)}</div>${wl(t).length?`<span class="avs" title="${esc(wl(t).join(", "))}">${wl(t).slice(0,3).map(n=>`<i class="av ${avc(n)}">${esc(n[0].toUpperCase())}</i>`).join("")}${wl(t).length>3?`<i class="av ao">+${wl(t).length-3}</i>`:""}</span>`:""}</div>${tg?`<div class="tg">${tg}</div>`:""}${a.length?`<div class="cb"><i style="width:${Math.round(k/a.length*100)}%"></i></div>`:""}<div class="cm"><span class="${late?"late":""}">${fl?'<b class="nfail">Nicht geschafft</b> · ':""}${dr(t)}</span><span class="ic">${t.ms?MSI:""}${t.rec?RECI:""}${extra(t)}${cl(t)}</span></div></div>`}
let showDone=false;const DONE_MAX=20;
function board(list){
  return`<div class="board">`+Object.keys(ST).map(s=>{let L=list.filter(t=>t.status===s);const all=L.length;
    /* Abgeschlossene: zuletzt abgehakte (oder nicht geschaffte) oben, damit man Versehen schnell findet */
    if(s==="done"){const ca=new Map(L.map(t=>[t,closedAt(t)]));L=L.slice().sort((x,y)=>ca.get(y)<ca.get(x)?-1:ca.get(y)>ca.get(x)?1:0)}
    const cut=s==="done"&&!showDone&&all>DONE_MAX;if(cut)L=L.slice(0,DONE_MAX);
    return`<div class="colm" data-s="${s}"><h3><i class="dt ${s}"></i><span>${ST[s]}</span><em>${all}</em></h3>`+(L.length?L.map((t,i)=>card(t,s,i)).join(""):'<div class="none">Keine Aufgaben</div>')+(cut?`<button class="btn ghost sm more" onclick="showDone=true;render()">Alle ${all} anzeigen</button>`:"")+`</div>`}).join("")+`</div>`;
}
const isPhone=()=>matchMedia("(max-width:699px)").matches;
function lrow(t,i){const dn_=t.status==="done",fl=isFail(t);return`<div class="hrow lrow${fl?" fail":""}" data-id="${t.id}"${t.prio?` data-pr="${t.prio}"`:""} style="--i:${Math.min(i,8)}"><button class="ring ${t.status}${fl?" fail":""}" data-adv="${t.id}" aria-label="Status: ${stName(t)}. Weiterschalten"></button><div class="hm"><div class="ht">${pb(t)}<span>${esc(t.title)}</span>${t.ms?MSI:""}${t.rec?RECI:""}</div><div class="hs">${[t.proj,...tgs(t),t.who].filter(Boolean).map(esc).join(" · ")||"&nbsp;"}${isBlocked(t)?' · <span class="blk">blockiert</span>':""}</div></div><span class="hd${isLate(t)?" late":""}">${fl?"nicht geschafft":dn_?fd(t.end):rel(t)}</span></div>`}
function table(list){
  if(isPhone())return`<div class="ilist">`+groups(list).map(g=>(g.l!=null?`<h3 class="igh"><i class="dt" style="background:${g.c}"></i><span>${esc(g.l)}</span><em>${g.L.length}</em></h3>`:"")+`<div class="igrp">${g.L.map(lrow).join("")}</div>`).join("")+`</div>`;
  const row=t=>`<tr class="row" data-id="${t.id}"${t.prio?` data-pr="${t.prio}"`:""}><td>${pjh(t)}${pb(t)}${esc(t.title)} ${isBlocked(t)?'<span class="blk">blockiert</span>':""}<span class="ic">${t.ms?MSI:""}${t.rec?RECI:""}${extra(t)}</span></td><td>${tgs(t).map(chip).join("")}</td><td>${esc(t.who)}</td><td>${fd(t.start)}</td><td class="${isLate(t)?"late":""}">${fd(t.end)}</td><td><span class="st ${t.status}${isFail(t)?" fail":""}">${stName(t)}</span></td></tr>`;
  return`<div class="wrap"><table><tr><th>Aufgabe</th><th>Tags</th><th>Wer</th><th>Beginn</th><th>Ende</th><th>Status</th></tr>`+
  groups(list).map(g=>(g.l!=null?`<tr class="grp"><td colspan="6"><i class="dt" style="background:${g.c}"></i>${esc(g.l)}<em>${g.L.length}</em></td></tr>`:"")+g.L.map(row).join("")).join("")+`</table></div>`;
}
let gmode="day";
const MON=["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"],MONL=["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"],WD=["So","Mo","Di","Mi","Do","Fr","Sa"];
function gantt(list){
  if(!list.length)return'<div class="empty">Keine Treffer.</div>';
  const T=today(),ROW=42,GH=30,mode=gmode,G=groups(list),items=[];let BH=0;
  G.forEach(g=>{if(g.l!=null){items.push({g,y:BH});BH+=GH}g.L.forEach(t=>{items.push({t,y:BH});BH+=ROW})});
  const mn=Math.min(T,...list.map(t=>dn(t.start))),mx=Math.max(T,...list.map(t=>dn(t.end)));
  const dp=d=>{const x=fromDn(d);return[x.getUTCFullYear(),x.getUTCMonth(),x.getUTCDate(),x.getUTCDay()]};
  const dim=(y,m)=>new Date(Date.UTC(y,m+1,0)).getUTCDate();
  const tx=(x,y,c,t)=>`<text class="${c}" x="${x}" y="${y}" text-anchor="middle">${t}</text>`;
  let X,W,HEAD,PPD,hd="",gd="",tdx;
  if(mode==="day"){
    const U=38,d0=mn-3,d1=Math.max(mx+14,d0+30);HEAD=68;PPD=U;W=(d1-d0+1)*U;X=d=>(d-d0)*U;tdx=X(T)+U/2;
    let seg=null;const segs=[];
    for(let d=d0;d<=d1;d++){
      const[y,m,dd,w]=dp(d),x=X(d),we=w===0||w===6;
      if(!seg||seg.y!==y||seg.m!==m){seg={y,m,x,w:0};segs.push(seg)}seg.w+=U;
      if(we)gd+=`<rect class="wk" x="${x}" y="0" width="${U}" height="${BH}"/>`;
      gd+=`<line class="${dd===1?"gs2":"gs1"}" x1="${x}" x2="${x}" y1="0" y2="${BH}"/>`;
      hd+=tx(x+U/2,43,we?"we":"",WD[w]);
      hd+=d===T?`<rect x="${x+U/2-14}" y="47" width="28" height="20" rx="10" fill="var(--bad)"/>`+tx(x+U/2,61,"tdn",dd):tx(x+U/2,61,we?"we":"",dd);
    }
    segs.forEach(g=>{hd+=`<line class="gs2" x1="${g.x}" x2="${g.x}" y1="0" y2="28"/><text class="l1" data-a="${g.x}" data-b="${g.x+g.w}" x="${g.x+10}" y="18">${g.w>=150?MONL[g.m]+" "+g.y:MON[g.m]+" "+String(g.y).slice(2)}</text>`});
  }else if(mode==="month"){
    const U=64,mi=d=>{const[y,m]=dp(d);return y*12+m},m0=mi(mn)-1,m1=Math.max(mi(mx)+3,m0+11);HEAD=52;PPD=U/30.44;W=(m1-m0+1)*U;
    X=d=>{const[y,m,dd]=dp(d);return(y*12+m-m0+(dd-1)/dim(y,m))*U};tdx=X(T);
    let ys=null;const segs=[];
    for(let k=m0;k<=m1;k++){
      const y=Math.floor(k/12),m=k%12,x=(k-m0)*U;
      if(!ys||ys.y!==y){ys={y,x,w:0};segs.push(ys)}ys.w+=U;
      gd+=`<line class="${m===0?"gs2":"gs1"}" x1="${x}" x2="${x}" y1="0" y2="${BH}"/>`;
      hd+=k===mi(T)?`<rect x="${x+U/2-19}" y="30" width="38" height="21" rx="10.5" fill="var(--bad)"/>`+tx(x+U/2,45,"tdn",MON[m]):tx(x+U/2,45,"",MON[m]);
    }
    segs.forEach(g=>{hd+=`<line class="gs2" x1="${g.x}" x2="${g.x}" y1="0" y2="28"/><text class="l1" data-a="${g.x}" data-b="${g.x+g.w}" x="${g.x+10}" y="18">${g.y}</text>`});
  }else{
    const U=150,y0=dp(mn)[0],y1=Math.max(dp(mx)[0]+1,y0+4),cy=dp(T)[0];HEAD=52;PPD=U/365.25;W=(y1-y0+1)*U;
    X=d=>{const y=dp(d)[0],len=dim(y,1)===29?366:365;return(y-y0+(d-Date.UTC(y,0,1)/864e5)/len)*U};tdx=X(T);
    let ds=null;const segs=[];
    for(let y=y0;y<=y1;y++){
      const x=(y-y0)*U,dc=Math.floor(y/10)*10;
      if(!ds||ds.dc!==dc){ds={dc,x,w:0};segs.push(ds)}ds.w+=U;
      gd+=`<line class="${y%10===0?"gs2":"gs1"}" x1="${x}" x2="${x}" y1="0" y2="${BH}"/>`;
      hd+=y===cy?`<rect x="${x+U/2-27}" y="30" width="54" height="21" rx="10.5" fill="var(--bad)"/>`+tx(x+U/2,45,"tdn",y):tx(x+U/2,45,"",y);
    }
    segs.forEach(g=>{hd+=`<line class="gs2" x1="${g.x}" x2="${g.x}" y1="0" y2="28"/><text class="l1" data-a="${g.x}" data-b="${g.x+g.w}" x="${g.x+10}" y="18">${g.dc}er</text>`});
  }
  items.forEach(it=>{if(it.g)gd+=`<rect style="fill:color-mix(in srgb,${it.g.c} 16%,var(--card))" x="0" y="${it.y}" width="${W}" height="${GH}"/>`;gd+=`<line class="gs1" x1="0" x2="${W}" y1="${it.y}" y2="${it.y}"/>`});
  gd+=`<line class="gs1" x1="0" x2="${W}" y1="${BH}" y2="${BH}"/>`;
  const col={todo:"var(--todo)",doing:"var(--doing)",done:"var(--done)"},pos={};
  items.forEach(it=>{if(!it.t)return;const t=it.t,x1=X(dn(t.start)),x2=X(dn(t.end)+1);pos[t.id]=t.ms?{x:x1+(x2-x1)/2-9,w:18,y:it.y}:{x:x1,w:Math.max(x2-x1,8),y:it.y}});
  gd+=`<line x1="${tdx}" x2="${tdx}" y1="0" y2="${BH}" stroke="var(--bad)" stroke-width="1.6" stroke-dasharray="3 3"/>`;
  list.forEach(t=>(t.deps||[]).forEach(id=>{const a=pos[id],b=pos[t.id];if(!a)return;
    const x1=a.x+a.w,y1=a.y+ROW/2,x2=b.x,y2=b.y+ROW/2,mx2=Math.max(x1+8,x2-8);
    gd+=`<path d="M${x1} ${y1}H${mx2}V${y2}H${x2}" fill="none" stroke="var(--mut)" stroke-width="1.4" marker-end="url(#ar)"/>`}));
  list.forEach(t=>{const p=pos[t.id],inside=!t.ms&&p.w>=t.title.length*6.7+20,cy=p.y+ROW/2;
    const body=t.ms?`<path d="M${p.x+9} ${cy-10}l10 10l-10 10l-10-10z" fill="${col[t.status]}"/>`:`<rect x="${p.x}" y="${p.y+8}" width="${p.w}" height="${ROW-16}" rx="8" fill="${col[t.status]}"/><rect class="ggl" x="${p.x}" y="${p.y+8}" width="${p.w}" height="${ROW-16}" rx="8" fill="url(#gGl)"/>`;
    const lbl=inside?`<text class="bt ${t.status}" x="${p.x+11}" y="${cy+4.2}">${esc(t.title)}</text>`:`<text class="bo" x="${p.x+p.w+10}" y="${cy+4.2}">${esc(t.title)}</text>`;
    const hd2=t.ms?"":`<rect data-h="s" class="gh1" x="${p.x}" y="${p.y+8}" width="7" height="${ROW-16}"/><rect data-h="e" class="gh1" x="${p.x+p.w-7}" y="${p.y+8}" width="7" height="${ROW-16}"/>`;
    gd+=`<g data-id="${t.id}" class="gbar${isFail(t)?" gfail":""}"${t.status==="done"?' opacity=".72"':""}>${body}${lbl}${hd2}<circle data-h="dep" class="gdep" cx="${p.x+p.w+(t.ms?1:0)}" cy="${cy}" r="5"/></g>`});
  const rows=items.map(it=>it.g?`<div class="gr gh2" style="--tc:${it.g.c}"><i class="dt" style="background:${it.g.c}"></i><span>${esc(it.g.l)}</span><em>${it.g.L.length}</em></div>`:`<div class="gr" data-id="${it.t.id}" title="${esc(it.t.title)}"><i class="dt ${it.t.status}"></i>${pb(it.t)}<span>${esc(it.t.title)}</span></div>`).join("");
  const seg=[["day","Tage"],["month","Monate"],["year","Jahre"]].map(([k,l])=>`<button data-gm="${k}" class="${k===mode?"on":""}">${l}</button>`).join("");
  return`<div class="gctl"><div class="seg">${seg}</div><button class="btn ghost sm" data-gtoday>Heute</button></div>`+
  `<div class="gwrap"><div class="gl"><div class="glh" style="--hd:${HEAD}px"></div>${rows}<div class="glg" style="--hd:${HEAD}px" role="separator" aria-label="Breite der Beschriftung ändern" title="Ziehen zum Ändern, Doppeltippen zum Zurücksetzen"></div></div><div class="gs" style="width:${W}px"><svg class="gh" width="${W}" height="${HEAD}">${hd}</svg><svg class="gb" width="${W}" height="${BH}" data-tx="${tdx}" data-ppd="${PPD}"><defs><marker id="ar" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L8 4L0 8z" fill="var(--mut)"/></marker><linearGradient id="gGl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".34"/><stop offset=".65" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>${gd}</svg></div></div>`;
}
function bind(){
  document.querySelectorAll("[data-id]").forEach(el=>el.onclick=e=>{if(e.target.dataset.adv)return;openDlg(el.dataset.id)});
  document.querySelectorAll("[data-adv]").forEach(b=>b.onclick=e=>{e.stopPropagation();advance(b.dataset.adv)});
  document.querySelectorAll("[data-back]").forEach(b=>b.onclick=e=>{e.stopPropagation();navigator.vibrate&&navigator.vibrate(8);const t=byId(b.dataset.back);saveTask({...t,status:{doing:"todo",done:"doing"}[t.status]})});
  document.querySelectorAll("[data-gm]").forEach(b=>b.onclick=()=>{gmode=b.dataset.gm;renderedView=null;render()});
  const gt=document.querySelector("[data-gtoday]");if(gt)gt.onclick=()=>gToday(true);
  document.querySelectorAll(".card").forEach(c=>c.ondragstart=e=>e.dataTransfer.setData("text/plain",c.dataset.id));
  document.querySelectorAll(".colm").forEach(c=>{
    c.ondragover=e=>{e.preventDefault();c.classList.add("over")};c.ondragleave=()=>c.classList.remove("over");
    c.ondrop=e=>{e.preventDefault();c.classList.remove("over");const t=byId(e.dataTransfer.getData("text/plain"));if(t&&t.status!==c.dataset.s)setStatus(t,c.dataset.s)}});
}

