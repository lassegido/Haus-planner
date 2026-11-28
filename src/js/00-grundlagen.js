const wl=t=>String(t.who||"").split(",").map(x=>x.trim()).filter(Boolean);
const allWho=()=>[...new Set(["Melanie","Lasse",...tasks.flatMap(wl)])];
const ST={todo:"Offen",doing:"In Arbeit",done:"Erledigt"},NEXT={todo:"doing",doing:"done",done:"todo"};
/* 1.42: „Nicht geschafft“ ist kein eigener Status, sondern Erledigt + fail:true. Damit gilt die Aufgabe überall als abgeschlossen
   (nicht mehr offen, keine Erinnerung, Wiederholung legt die nächste an), zählt aber nicht als geschafft. */
const isFail=t=>!!t&&t.status==="done"&&!!t.fail,isOk=t=>t.status==="done"&&!t.fail,stName=t=>isFail(t)?"Nicht geschafft":ST[t.status];
let RAW=[],tasks=[],selMode=false,sel=new Set(),haInfo=null,haAvail=null,purged=false,reg=[],ftags=new Set(),fprojs=new Set(),grp=(()=>{try{return localStorage.getItem("haus-grp")||"none"}catch(e){return"none"}})(),grp2=(()=>{try{return localStorage.getItem("haus-grp2")||"none"}catch(e){return"none"}})(),fprios=new Set(),sortm=(()=>{try{return localStorage.getItem("haus-sort")||"date"}catch(e){return"date"}})(),selTags=[],regDraft=null,colorFor=null,palOpen=null,view="home",col=null,editing=null,loaded=false;
const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const iso=d=>d.toISOString().slice(0,10);
const dn=s=>{const[y,m,d]=s.split("-").map(Number);return Date.UTC(y,m-1,d)/864e5};
const fromDn=n=>new Date(n*864e5);
const today=()=>{const d=new Date();return Date.UTC(d.getFullYear(),d.getMonth(),d.getDate())/864e5};
const FDC=new Map();const fd=s=>{if(!s)return"";let v=FDC.get(s);if(v===undefined){v=fromDn(dn(s)).toLocaleDateString("de-DE",{day:"2-digit",month:"2-digit",timeZone:"UTC"});if(FDC.size>2000)FDC.clear();FDC.set(s,v)}return v};
const byId=id=>RAW.find(t=>t.id===id);
const isLate=t=>t.status!=="done"&&dn(t.end)<today();
const isBlocked=t=>t.status!=="done"&&(t.deps||[]).some(i=>{const p=byId(i);return p&&!p.del&&p.status!=="done"});

