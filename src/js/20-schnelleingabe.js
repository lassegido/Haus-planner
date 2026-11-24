/* Anzeige */
/* Schnelleingabe: „Zaun streichen Sa #Garten +Haus !1 @Melanie“ */
const QWD=[["So","sonntag"],["Mo","montag"],["Di","dienstag"],["Mi","mittwoch"],["Do","donnerstag"],["Fr","freitag"],["Sa","samstag"]];
const QMON=["januar","februar","märz","april","mai","juni","juli","august","september","oktober","november","dezember"];
const QNUM={ein:1,eine:1,einen:1,einem:1,eins:1,zwei:2,drei:3,vier:4,"fünf":5,sechs:6,sieben:7,acht:8,neun:9,zehn:10,elf:11,"zwölf":12,vierzehn:14};
const QORD=(()=>{const st=["erst","zweit","dritt","viert","fünft","sechst","siebt","acht","neunt","zehnt","elft","zwölft","dreizehnt","vierzehnt","fünfzehnt","sechzehnt","siebzehnt","achtzehnt","neunzehnt","zwanzigst",...["ein","zwei","drei","vier","fünf","sechs","sieben","acht","neun"].map(p=>p+"undzwanzigst"),"dreißigst","einunddreißigst"],o={};
  st.forEach((x,n)=>["e","en","er","es","em"].forEach(e=>o[x+e]=n+1));o.siebente=o.siebenten=7;return o})();
const qn=s=>String(s||"").toLowerCase().replace(/[.,;:!?]+$/,"");
const qName=(x,list)=>{x=x.replace(/_/g," ").replace(/[.,;:!?]+$/,"").trim();const l=x.toLowerCase();return list.find(n=>n.toLowerCase()===l)||(list.filter(n=>n.toLowerCase().startsWith(l)).length===1?list.find(n=>n.toLowerCase().startsWith(l)):x.charAt(0).toUpperCase()+x.slice(1))};
const qKnown=(x,list)=>{const l=qn(x);if(l.length<3)return null;const e=list.find(n=>n.toLowerCase()===l);if(e)return e;const p=list.filter(n=>n.toLowerCase().startsWith(l));return p.length===1?p[0]:null};
const qNum=x=>{x=qn(x);return /^\d{1,3}$/.test(x)?+x:(QNUM[x]??null)};
function qDay(d,mo,y,T,explicit){const t=Date.UTC(y,mo-1,d)/864e5,x=fromDn(t);if(x.getUTCMonth()!==mo-1||x.getUTCDate()!==d)return null;
  if(!explicit&&t<T){const t2=Date.UTC(y+1,mo-1,d)/864e5,x2=fromDn(t2);if(x2.getUTCMonth()===mo-1&&x2.getUTCDate()===d)return t2}return t}
function qDateAt(W,i){
  const w=qn(W[i]),raw=String(W[i]).replace(/[,;:!?]+$/,""),nx=qn(W[i+1]),T=today(),dow=fromDn(T).getUTCDay();
  if((w==="am"||w==="zum"||w==="ab")&&i+1<W.length){const r=qDateAt(W,i+1);return r?[r[0],r[1]+1]:null}
  if(w==="heute")return[T,1];if(w==="morgen")return[T+1,1];if(w==="übermorgen"||w==="uebermorgen")return[T+2,1];
  if(w==="wochenende")return[T+(6-dow+7)%7,1];
  if(["nächste","naechste","nächsten","kommende","kommenden"].includes(w)&&nx==="woche")return[T+((1-dow+7)%7||7),2];
  if(w==="in"&&i+2<W.length&&qNum(W[i+1])!==null){const k=qNum(W[i+1]),u=qn(W[i+2]);if(u==="tag"||u==="tagen")return[T+k,3];if(u==="woche"||u==="wochen")return[T+7*k,3]}
  const wi=QWD.findIndex(([a,b])=>w===b||raw.replace(/\.$/,"")===a);if(wi>=0)return[T+(wi-dow+7)%7,1];
  let m=/^(\d{1,2})\.(\d{1,2})\.(\d{2}|\d{4})?$/.exec(raw);
  if(m){let y=m[3]?+m[3]:fromDn(T).getUTCFullYear();if(y<100)y+=2000;const t=qDay(+m[1],+m[2],y,T,!!m[3]);return t===null?null:[t,1]}
  const d=/^\d{1,2}\.$/.test(raw)?parseInt(raw):(QORD[w]||null);
  if(d&&QMON.includes(nx)){const t=qDay(d,QMON.indexOf(nx)+1,fromDn(T).getUTCFullYear(),T,false);return t===null?null:[t,2]}
  return null}
function parseQuick(text){
  const W=String(text||"").trim().split(/\s+/).filter(Boolean),o={tags:[],who:[],proj:"",prio:0,date:null,until:false},keep=[];let m;
  for(let i=0;i<W.length;i++){const w=W[i],lo=qn(w),nx=W[i+1]||"";
    if((m=/^#(.+)$/.exec(w))){const n=qName(m[1],allTags());if(n&&!o.tags.includes(n))o.tags.push(n.slice(0,30));continue}
    if((m=/^\+(.+)$/.exec(w))){o.proj=qName(m[1],allProjs()).slice(0,30);continue}
    if((m=/^@(.+)$/.exec(w))){const n=qName(m[1],allWho());if(n&&!o.who.includes(n))o.who.push(n.slice(0,30));continue}
    if((m=/^(?:!|p)([1-3])$/i.exec(w))){o.prio=+m[1];continue}
    if(/^!{1,3}$/.test(w)){o.prio=4-w.length;continue}
    if(keep.length){
      if((lo==="priorität"||lo==="prio")&&[1,2,3].includes(qNum(nx))){o.prio=qNum(nx);i++;continue}
      if((lo==="tag"||lo==="hashtag")&&nx&&qKnown(nx,allTags())){const n=qKnown(nx,allTags());if(!o.tags.includes(n))o.tags.push(n);i++;continue}
      if(lo==="projekt"&&nx&&qKnown(nx,allProjs())){o.proj=qKnown(nx,allProjs());i++;continue}
      if(lo==="bis"&&i+1<W.length){const r=qDateAt(W,i+1);if(r){o.date=r[0];o.until=true;i+=r[1];continue}}
      const r=qDateAt(W,i);if(r){o.date=r[0];o.until=false;i+=r[1]-1;continue}}
    keep.push(w)}
  o.title=keep.join(" ").slice(0,200);o.found=!!(o.tags.length||o.who.length||o.proj||o.prio||o.date!==null);return o}
function qDates(q){const T=today();if(q.date===null)return null;return q.until?[iso(fromDn(Math.min(T,q.date))),iso(fromDn(q.date))]:[iso(fromDn(q.date)),iso(fromDn(q.date))]}
const WDL=["So","Mo","Di","Mi","Do","Fr","Sa"];
function qChips(q){if(!q.found)return"";const c=[];const d=qDates(q);
  if(d){const t=dn(d[1]),T=today();c.push(`<span class="qc qd">${q.until?"bis ":""}${t===T?"Heute":t===T+1?"Morgen":WDL[fromDn(t).getUTCDay()]+" "+fd(d[1])}</span>`)}
  q.tags.forEach(n=>c.push(`<span class="qc" style="--tc:${tcol(n)}">${tIc(n)}${esc(n)}</span>`));
  if(q.proj)c.push(`<span class="qc qp" style="--tc:${pcol(q.proj)}"><i></i>${esc(q.proj)}</span>`);
  q.who.forEach(n=>c.push(`<span class="qc">@${esc(n)}</span>`));
  if(q.prio)c.push(`<span class="pr p${q.prio}">P${q.prio}</span>`);
  return c.join("")}
async function regEnsure(tags,proj){const r=reg.map(x=>({...x}));let ch=false;
  tags.forEach(n=>{if(!r.some(x=>!x.p&&x.n===n)){r.push({n,c:nextColor()});ch=true}});
  if(proj&&!r.some(x=>x.p&&x.n===proj)){r.push({n:proj,c:nextPColor(),p:1});ch=true}
  if(ch)await saveReg(r)}
let qaddKeep=null;
async function quickAdd(text){
  const q=parseQuick(text);if(!q.title){toast("Bitte einen Titel eingeben");return false}q.title=q.title.charAt(0).toUpperCase()+q.title.slice(1);
  const d=qDates(q)||[tdy(),tdy()],hw=homeW(),who=q.who.length?q.who:(hw&&hw!=="__all"?[hw]:[]);
  const t={id:newId(),title:q.title.slice(0,200),tags:q.tags,area:q.tags[0]||"",proj:q.proj,who:who.join(", "),status:"todo",prio:q.prio,start:d[0],end:d[1],notes:"",deps:[],checklist:[],ms:false,rec:null};
  await regEnsure(q.tags,q.proj);await saveTask(t);hap(10);
  toast("„"+t.title+"“ angelegt",()=>delTask(t.id));return true}
