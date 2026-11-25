/* 1.34: Motivation auf der Startseite: Serie, gemeinsame Woche, Abzeichen und Feiern.
   Alles wird aus Status und Verlauf der Aufgaben berechnet, nichts zusätzlich gespeichert
   (Ausnahme: welche Abzeichen dieses Gerät schon gemeldet hat, im Browser unter haus-badges). */
const doneOn=t=>{if(t.status!=="done")return Infinity;const d=doneDay(t);return isNaN(d)?dn(t.end):d};
const motScope=()=>{const hw=homeW();return RAW.filter(t=>!t.del&&(hw==="__all"||wl(t).includes(hw)))};
const todayOpenOf=L=>{const T=today();return L.filter(t=>t.status!=="done"&&!t.arch&&dn(t.start)<=T&&(dn(t.end)>=T||isLate(t)))};
/* Tage, an denen etwas Fälliges offen blieb (Tagesring nicht voll) */
function badDays(L,T){const bad=new Set();for(const t of L){const due=dn(t.end),dd=doneOn(t);for(let x=Math.max(due,T-400);x<Math.min(dd,T+1);x++)bad.add(x)}return bad}
/* Serie: Tage in Folge mit vollem Tagesring und mindestens einer erledigten Aufgabe. Tage ohne alles unterbrechen nicht.
   Heute zählt erst, wenn der Ring voll ist; bis dahin läuft die Serie von gestern weiter. */
function motStats(L){
  const T=today(),bad=badDays(L,T),doneL=L.filter(t=>t.status==="done"),act=new Map();doneL.forEach(t=>{const d=doneOn(t);act.set(d,(act.get(d)||0)+1)});
  /* Mehr als 7 Tage ganz ohne Erledigtes beenden die Serie ebenfalls */
  let n=0,todayIn=false,gap=0;for(let x=T;x>T-400;x--){if(bad.has(x)){if(x===T)continue;break}if(act.has(x)){n++;gap=0;if(x===T)todayIn=true}else if(x<T&&++gap>7)break}
  let run=0,maxS=0;gap=0;for(let x=T-400;x<=T;x++){if(bad.has(x)&&x<T)run=0;else if(act.has(x)){run++;gap=0;maxS=Math.max(maxS,run)}else if(++gap>7)run=0}
  let cleanWeek=false;const mon=T-mo(fromDn(T).getUTCDay());for(let m=mon-7;m>mon-400&&!cleanWeek;m-=7){let ok=true,c=0;for(let x=m;x<m+7;x++){if(bad.has(x))ok=false;c+=act.get(x)||0}if(ok&&c>=3)cleanWeek=true}
  const projDone=allProjs().some(p=>{const P=L.filter(t=>t.proj===p);return P.length>=3&&P.every(t=>t.status==="done")});
  return{streak:n,todayIn,maxStreak:maxS,done:doneL.length,cleanWeek,projDone,early:doneL.filter(t=>doneOn(t)<dn(t.end)).length,
    team:doneL.filter(t=>wl(t).length>1).length,bigCk:doneL.some(t=>(t.checklist||[]).length>=10&&t.checklist.every(c=>c.d))}}
const BADGES=[
  ["d10","Erste 10","10 Aufgaben erledigt",s=>s.done>=10],["d50","Fünfzig","50 Aufgaben erledigt",s=>s.done>=50],["d100","Hundert","100 Aufgaben erledigt",s=>s.done>=100],
  ["s7","Eine Woche dran","7 Tage in Folge alles für den Tag erledigt",s=>s.maxStreak>=7],["s30","Ausdauer","30 Tage in Folge alles für den Tag erledigt",s=>s.maxStreak>=30],
  ["clean","Weiße Weste","Eine ganze Woche (Mo–So) ohne Überfälliges, mindestens 3 Aufgaben erledigt",s=>s.cleanWeek],
  ["proj","Projekt geschafft","Alle Aufgaben eines Projekts erledigt (mindestens 3)",s=>s.projDone],
  ["early","Frühstarter","10 Aufgaben vor dem Fälligkeitstag erledigt",s=>s.early>=10],
  ["team","Teamwork","5 Aufgaben mit mehreren Personen erledigt",s=>s.team>=5],
  ["ck","Abgehakt","Eine Checkliste mit mindestens 10 Punkten komplett erledigt",s=>s.bigCk]];
const MEDAL='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3.5l2.2 5M16 3.5l-2.2 5"/><circle cx="12" cy="14.5" r="5.5"/><path d="M12 12v5"/></svg>';
const FLAME='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21c-3.6 0-6-2.5-6-5.8 0-3.3 2.3-5 3.4-7.6.4 1.6 1.3 2.6 2.3 3.1-.2-2.9.9-5.6 3.3-7.2-.1 3 1.1 4.6 2.2 6.2.9 1.3 1.8 2.6 1.8 4.9C19 18.6 15.9 21 12 21z"/></svg>';
/* Wer hat erledigt: Name aus dem Verlauf (auch „iPhone von Lasse“), sonst die einzige zuständige Person, sonst „Gemeinsam“ */
function doneBy(t){const names=allWho(),L=t.log||[];
  for(let i=L.length-1;i>=0;i--){const x=L[i];if(x.k==="h"&&DONE_RX.test(x.x||"")){const a=String(x.a||"").toLowerCase(),n=names.find(w=>a.includes(w.toLowerCase()));if(n)return n;break}}
  const w=wl(t);return w.length===1?w[0]:"Gemeinsam"}
const motCol=w=>/^melanie/i.test(w)?"var(--brick)":/^lasse/i.test(w)?"var(--sea)":w==="Gemeinsam"?"var(--mut)":"var(--sky)";
function streakHtml(s,rn){
  if(s.streak)return`<div class="hstreak${s.todayIn?" lit":""}">${FLAME}<span><b>${s.streak} ${s.streak===1?"Tag":"Tage"}</b> in Folge${s.todayIn?"":" · heute weitermachen"}</span></div>`;
  return rn?`<div class="hstreak">${FLAME}<span>Erledige heute alles und starte eine Serie</span></div>`:""}
function motPanel(L,i){
  const T=today(),mon=T-mo(fromDn(T).getUTCDay()),all=RAW.filter(t=>!t.del&&t.status==="done");
  const wk=all.filter(t=>{const d=doneOn(t);return d>=mon&&d<=T}),prev=all.filter(t=>{const d=doneOn(t);return d>=mon-7&&d<=T-7}).length;
  const by=new Map();wk.forEach(t=>{const w=doneBy(t);by.set(w,(by.get(w)||0)+1)});const parts=[...by].sort((a,b)=>(a[0]==="Gemeinsam")-(b[0]==="Gemeinsam")||b[1]-a[1]);
  const bar=wk.length?`<div class="wbar">${parts.map(([w,c])=>`<i style="flex:${c};background:${motCol(w)}" title="${esc(w)}: ${c}"></i>`).join("")}</div>`:`<div class="wbar"></div>`;
  const leg=parts.map(([w,c])=>`<span><i style="background:${motCol(w)}"></i>${esc(w)} ${c}</span>`).join("");
  const diff=wk.length-prev,wd=WDLONG[fromDn(T).getUTCDay()];
  const cmp=T===mon?`Vorwoche gesamt: ${all.filter(t=>{const d=doneOn(t);return d>=mon-7&&d<mon}).length}`:`Vorwoche bis ${wd}: ${prev}`+(diff>0?` · ${diff} mehr`:diff<0?` · ${-diff} weniger`:" · gleich viel");
  const s=motStats(L),got=BADGES.filter(b=>b[3](s)).length;
  try{if(localStorage.getItem(badgeKey())===null)localStorage.setItem(badgeKey(),JSON.stringify(BADGES.filter(b=>b[3](s)).map(b=>b[0])))}catch(_){}
  const bdg=BADGES.map(([id,t,dsc,f])=>{const on=f(s);return`<button type="button" class="bdg${on?" on":""}" data-bdg="${id}" aria-label="${esc(t)}${on?"":" (noch offen)"}">${MEDAL}<span>${esc(t)}</span></button>`}).join("");
  return`<section class="pnl mot" style="--i:${i}"><h3><span>Gemeinsam diese Woche</span><em>${wk.length} erledigt</em></h3>${bar}<div class="wleg">${leg||"<span>Noch nichts erledigt – los geht’s.</span>"}</div><p class="wcmp">${cmp}</p>
    <h3 class="bh"><span>Abzeichen</span><em>${got} von ${BADGES.length}</em></h3><div class="bdgs">${bdg}</div></section>`}
/* Abzeichen antippen: Beschreibung */
document.addEventListener("click",e=>{const b=e.target.closest&&e.target.closest("[data-bdg]");if(!b)return;const x=BADGES.find(y=>y[0]===b.dataset.bdg);
  if(x)toast((b.classList.contains("on")?"🏅 ":"Noch offen: ")+x[1]+" – "+x[2])});
/* Feiern: nach dem Abhaken. Letzte Aufgabe des Tages → Konfetti; neues Abzeichen → Hinweis */
function confetti(){if(matchMedia("(prefers-reduced-motion:reduce)").matches)return;const box=document.createElement("div");box.className="confetti";box.setAttribute("aria-hidden","true");
  const C=["var(--acc)","var(--sky)","var(--sun)","var(--sea)","var(--brick)"];
  box.innerHTML=Array.from({length:48},(_,k)=>`<i style="left:${Math.random()*100}%;background:${C[k%5]};--d:${(Math.random()*.5).toFixed(2)}s;--r:${Math.round(Math.random()*720-360)}deg;--x:${Math.round(Math.random()*120-60)}px"></i>`).join("");
  document.body.appendChild(box);setTimeout(()=>box.remove(),2600)}
function badgeKey(){return"haus-badges-"+(prefGet("me")||"alle")}
function newBadges(){const s=motStats(motScope()),got=BADGES.filter(b=>b[3](s)).map(b=>b[0]);let seen=null;try{seen=JSON.parse(localStorage.getItem(badgeKey())||"null")}catch(_){}
  try{localStorage.setItem(badgeKey(),JSON.stringify(got))}catch(_){}
  return seen?BADGES.filter(b=>got.includes(b[0])&&!seen.includes(b[0])):[]}
function cheer(){
  const L=motScope(),T=today(),doneToday=L.some(t=>t.status==="done"&&doneOn(t)===T),fresh=newBadges();
  const all=!todayOpenOf(L).length&&doneToday,nb=fresh.length?"Neues Abzeichen: "+fresh.map(b=>b[1]).join(", "):"";
  if(all||nb){confetti();hap(30);toast(all?"Alles für heute erledigt – stark! 🎉"+(nb?" "+nb:""):"🏅 "+nb,null,null,5000)}}
/* 1.34: Sprüche auf der Startseite (nur dort). Eingebaut; im Add-on erneuert Gemini sie höchstens einmal am Tag (api/sprueche).
   Platzhalter: {n} Serie, {late} überfällig, {open} offen. */
const MEME_BASE={
  done:["Mission bestanden. Respekt + 🏆","Woo-hoo! Alles erledigt. Homer gönnt sich jetzt einen Donut.","Das hätte nicht mal Bernd Stromberg kleinreden können.",
    "Michael Scott würde jetzt eine Dundie-Verleihung veranstalten.","Abpfiff, Sieg, Feierabend. Ab in die Kabine.","Giggity! Liste leer.","Wanted-Level 0. Ihr seid sauber.","Such wow, very erledigt 🐕","Good-Boy-Energy: alles erledigt, Leckerli verdient 🦴","No cap, ihr habt heute gegessen.","Sheesh. Liste leer, Couch voll.","Wir schaffen das. – Und zwar heute schon 💅","Raute machen, zurücklehnen. Läuft."],
  streak:["{n} Tage in Folge. Das ist keine Glückssträhne mehr, das ist Führungsqualität.","Respekt + {n}. Los Santos hat Angst vor euch.",
    "{n} Tage am Stück – mehr Serie als Die Simpsons Staffeln haben … fast.","{n} Siege in Folge. Die Fans singen schon.","{n} Tage durchgezogen. Dwight wäre eifersüchtig.","Slay. {n} Tage am Stück.","Sheesh, {n} Tage in Folge! Der Hund ist stolz 🐶","{n} Tage durchgezogen – Capybara-Level an Gelassenheit."],
  late:["D'oh! {late} überfällig. Kurz durchatmen, dann weg damit.","Mission fehlgeschlagen? Nur ein Checkpoint. Neustart.","{late} Aufgaben warten. Stromberg sagt: „Das Büro ist kein Ponyhof.“",
    "Wanted-Level steigt: {late} überfällig. Zeit, die Fahndung zu beenden.","Rückstand zur Halbzeit? Zweite Hälfte, Comeback.","Peter Griffin würde sich jetzt hinsetzen. Ihr nicht.","This is fine 🐶🔥 – {late} überfällig.","Lowkey überfällig: {late}. Highkey Zeit loszulegen.","Die Katze hat eure Liste vom Tisch geschubst. Aufheben, {late} erledigen 🐈","Neuland? Nein, nur {late} überfällige Aufgaben."],
  start:["Neuer Tag, neue Mission. Wanted-Level: 0.","Anpfiff! Die erste Aufgabe ist der Ball.","Kaffee? Check. Erste Aufgabe? Gleich. Michael Scott glaubt an euch.",
    "Ay caramba, heute ist noch alles offen. Fangt klein an.","Erst die Pflicht, dann die Couch. So steht’s im Handbuch.","Digga, die Liste wartet. Erster Move zählt.","Der Hund guckt euch an. Er erwartet Großes 🐕","Main-Character-Energy aktivieren: erste Aufgabe.","Wir schaffen das. Erste Aufgabe, los."],
  good:["Halbzeitführung. Jetzt bloß nicht nachlassen.","Noch {open} offen – das macht ihr mit links.","Läuft bei euch. Fast so gut wie Ernie beim Kaffeeholen.",
    "Mission läuft. Noch {open} Ziele auf der Karte.","Excellent. – Mr. Burns wäre zufrieden. Noch {open}.","Ihr cookt gerade. Noch {open}.","Lass mal so weitermachen, noch {open} – ezpz.","Wauzi-Wackel-Modus: noch {open} 🐕","Tremendous progress. The best. Noch {open}."]};
let MEMES=null;
(function loadMemes(){if(typeof api!=="function")return;api("api/sprueche").then(j=>{if(j&&j.lines){MEMES=j.lines;if(typeof regLoaded!=="undefined"&&regLoaded&&view==="home")render()}}).catch(()=>{})})();
function memeHtml(kind,v){const L=(MEMES&&MEMES[kind]&&MEMES[kind].length?MEMES[kind]:MEME_BASE[kind])||[];if(!L.length)return"";
  const s=L[(today()+kind.length*7)%L.length].replace(/\{(\w+)\}/g,(m,k)=>v[k]!==undefined?v[k]:m);return`<p class="meme">${esc(s)}</p>`}
