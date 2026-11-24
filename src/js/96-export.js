const stamp=()=>iso(new Date()),fdl=s=>fromDn(dn(s)).toLocaleDateString("de-DE",{timeZone:"UTC"});
$("exp").onclick=()=>{$("dlx").showModal();preloadExport()};
$("x_close").onclick=()=>$("dlx").close();
$("x_json").onclick=()=>dl("planner-backup-"+stamp()+".json",new Blob([JSON.stringify({version:2,exportiert:new Date().toISOString(),tasks:RAW,tags:reg},null,2)],{type:"application/json"}));
$("x_imp").onclick=()=>$("imp").click();
$("imp").onchange=async e=>{const f=e.target.files[0];if(!f)return;try{const j=JSON.parse(await f.text()),arr=Array.isArray(j)?j:j.tasks;if(!Array.isArray(arr))throw 0;if(!await confirmSheet(arr.length+" Aufgaben einspielen? Vorhandene mit gleicher ID werden überschrieben.","Einspielen",true))return;await saveMany(arr.filter(t=>t&&t.id&&t.title&&t.start&&t.end));if(Array.isArray(j.tags)&&j.tags.length)await saveReg(mergeReg(j.tags));$("dlx").close()}catch(x){alert("Die Datei konnte nicht gelesen werden.")}e.target.value=""};
$("x_pdf").onclick=async()=>{
  if(!window.jspdf){$("note").textContent="PDF wird vorbereitet …";try{await loadJs(LIB.pdf,"jspdf")}catch(e){$("note").textContent="PDF-Bibliothek konnte nicht geladen werden.";return}$("note").textContent=""}
  const J=window.jspdf;
  const doc=new J.jsPDF({unit:"mm",format:"a4"}),L=14;let y=18;
  const c2=s=>String(s??"").replace(/[^\u0000-\u00ff]/g,"");
  const ln=(txt,sz=10,b=0,ind=0,c=[30,30,30])=>{doc.setFont("helvetica",b?"bold":"normal");doc.setFontSize(sz);doc.setTextColor(...c);for(const l of doc.splitTextToSize(c2(txt),182-ind)){if(y>282){doc.addPage();y=18}doc.text(l,L+ind,y);y+=sz*.45}};
  const grey=[90,90,90],list=tasks.slice().sort((a,b)=>dn(a.start)-dn(b.start)||dn(a.end)-dn(b.end)),n=list.length;
  ln("Planner",20,1);y+=1;
  ln(`Stand ${new Date().toLocaleDateString("de-DE")} | ${list.filter(t=>t.status==="done").length} von ${n} erledigt | ${tasks.filter(t=>t.status==="doing").length} in Arbeit | ${tasks.filter(isLate).length} überfällig | ${tasks.filter(isBlocked).length} blockiert`,10,0,0,grey);y+=4;
  list.forEach(t=>{
    ln(t.title,12,1);
    ln(`${ST[t.status]}${t.prio?" | Prio "+t.prio:""} | ${fdl(t.start)} - ${fdl(t.end)}${t.proj?" | Projekt "+t.proj:""}${tgs(t).length?" | "+tgs(t).join(", "):""}${t.who?" | "+t.who:""}`,9,0,0,grey);
    const dp=(t.deps||[]).map(i=>byId(i)?.title).filter(Boolean);if(dp.length)ln("Abhängig von: "+dp.join(", "),9,0,0,grey);
    (t.checklist||[]).forEach(c=>ln((c.d?"[x] ":"[ ] ")+c.t,9,0,4));
    if(t.notes)ln("Notiz: "+t.notes,9,0,0,grey);
    y+=3});
  if(n){
    doc.addPage("a4","l");doc.setFont("helvetica","bold");doc.setFontSize(14);doc.setTextColor(30,30,30);doc.text("Zeitstrahl",14,14);
    const T=today(),d0=Math.min(T,...list.map(t=>dn(t.start)))-1,d1=Math.max(T,...list.map(t=>dn(t.end)))+1,X0=75,sc=(297-X0-10)/(d1-d0+1),top=26,rh=Math.min(8,165/n);
    const col={todo:[108,182,228],doing:[253,175,84],done:[56,124,163]};
    doc.setFont("helvetica","normal");doc.setFontSize(7);doc.setLineWidth(.15);
    for(let k=d0;k<=d1;k++){const dt=fromDn(k);if(dt.getUTCDate()===1||k===d0){const x=X0+(k-d0)*sc;doc.setDrawColor(220,220,220);doc.line(x,top-4,x,top+n*rh);doc.setTextColor(90,90,90);doc.text(dt.toLocaleDateString("de-DE",{month:"short",year:"2-digit",timeZone:"UTC"}),x+1,top-5)}}
    const pos={};
    list.forEach((t,i)=>{const x=X0+(dn(t.start)-d0)*sc,w=Math.max((dn(t.end)-dn(t.start)+1)*sc,1.5),yy=top+i*rh;pos[t.id]={x,w,yy};doc.setTextColor(30,30,30);doc.setFontSize(7);doc.text(c2(t.title).slice(0,40),14,yy+rh/2+1);doc.setFillColor(...col[t.status]);doc.roundedRect(x,yy+1,w,rh-2,1,1,"F")});
    doc.setDrawColor(90,90,90);doc.setFillColor(90,90,90);doc.setLineWidth(.2);
    list.forEach(t=>(t.deps||[]).forEach(i=>{const a=pos[i],b=pos[t.id];if(!a)return;const x1=a.x+a.w,y1=a.yy+rh/2,x2=b.x,y2=b.yy+rh/2,mx=Math.max(x1+2,x2-2);doc.line(x1,y1,mx,y1);doc.line(mx,y1,mx,y2);doc.line(mx,y2,x2,y2);doc.triangle(x2,y2,x2-1.4,y2-.9,x2-1.4,y2+.9,"F")}));
    const tx=X0+(T-d0+.5)*sc;doc.setDrawColor(211,85,38);doc.line(tx,top-2,tx,top+n*rh);
  }
  dl("planner-"+stamp()+".pdf",doc.output("arraybuffer"));
};
/* Excel-Export (ExcelJS wird erst bei Bedarf geladen) */
const JSL={};
function loadJs(src,g){if(window[g])return Promise.resolve();return JSL[src]||(JSL[src]=new Promise((ok,no)=>{const s=document.createElement("script");s.src=src;s.onload=ok;s.onerror=()=>{delete JSL[src];s.remove();no(new Error("Bibliothek konnte nicht geladen werden"))};document.head.appendChild(s)}))}
function preloadExport(){loadJs(LIB.pdf,"jspdf").catch(()=>{});loadJs(LIB.xlsx,"ExcelJS").catch(()=>{})}
async function buildXlsx(){
  const wb=new ExcelJS.Workbook();wb.creator="Planner";wb.calcProperties={fullCalcOnLoad:true};
  const list=tasks.slice().sort((a,b)=>dn(a.start)-dn(b.start)||dn(a.end)-dn(b.end));
  const nr={};list.forEach((t,i)=>nr[t.id]=i+1);
  const R0=5,R1=304,DATA="Liste";
  const C={ink:"FF387CA3",line:"FFE6E1D2",todo:"FFDCEEF9",doing:"FFFEE7C8",done:"FFCBDEE9",bad:"FFD35526",grey:"FF587080",bTodo:"FF6CB6E4",bDoing:"FFFDAF54",bDone:"FF387CA3",today:"FFF6CDBD",we:"FFEDE9DC"};
  const edge={style:"thin",color:{argb:C.line}},box={top:edge,left:edge,bottom:edge,right:edge};
  const fill=a=>({type:"pattern",pattern:"solid",fgColor:{argb:a}});
  const cf=a=>({fill:{type:"pattern",pattern:"solid",bgColor:{argb:a}}});
  const hdr=(cell,txt)=>{cell.value=txt;cell.font={bold:true,color:{argb:"FFFFFFFF"},size:11};cell.fill=fill(C.ink);cell.alignment={vertical:"middle",wrapText:true}};
  const D=s=>{const[y,m,d]=s.split("-").map(Number);return new Date(Date.UTC(y,m-1,d))};
  const L="Liste!";

  /* ---------- Blatt 1: Liste (hier werden Aufgaben gepflegt) ---------- */
  const ws=wb.addWorksheet("Liste",{views:[{state:"frozen",xSplit:2,ySplit:4,showGridLines:false}],properties:{tabColor:{argb:C.ink}}});
  ws.columns=[{width:6},{width:34},{width:14},{width:13},{width:12},{width:12},{width:12},{width:14},{width:34},{width:30},{width:12},{width:30},{width:6,hidden:true},{width:6,hidden:true},{width:6,hidden:true},{width:16},{width:10}];
  ws.getCell("A1").value="Planner";ws.getCell("A1").font={bold:true,size:18};
  ws.getCell("H1").value="Neue Aufgabe: einfach in der nächsten freien Zeile eintragen. Board und Zeitstrahl aktualisieren sich automatisch (bis Zeile 304).";
  ws.getCell("H1").font={italic:true,color:{argb:C.grey},size:10};
  const kp=[["B","Aufgaben",`COUNTIF(B${R0}:B${R1},"?*")`,"0"],["C","Erledigt",`IFERROR(COUNTIF(G${R0}:G${R1},"Erledigt")/B3,0)`,"0%"],["D","In Arbeit",`COUNTIF(G${R0}:G${R1},"In Arbeit")`,"0"],["E","Überfällig",`SUMPRODUCT((B${R0}:B${R1}<>"")*(G${R0}:G${R1}<>"Erledigt")*ISNUMBER(F${R0}:F${R1})*(F${R0}:F${R1}<TODAY()))`,"0"],["F","Konflikte",`COUNTIF(L${R0}:L${R1},"?*")`,"0"]];
  kp.forEach(([c,l,f,nf])=>{const a=ws.getCell(c+"2"),b=ws.getCell(c+"3");a.value=l;a.font={size:9,color:{argb:C.grey}};b.value={formula:f};b.numFmt=nf;b.font={bold:true,size:18};a.border={top:edge,left:edge,right:edge};b.border={bottom:edge,left:edge,right:edge};b.alignment={horizontal:"left"}});
  ws.getRow(3).height=28;
  ["Nr","Aufgabe","Tags","Ressource","Start","Ende","Status","Abhängig von (Nr, z. B. 2,5)","Checkliste (eine Zeile je Punkt, [x] = erledigt)","Notizen","Checkl.-Stand","Hinweis","Offen","In Arbeit","Erledigt","Projekt","Priorität"].forEach((h,i)=>hdr(ws.getCell(4,i+1),h));
  ws.getRow(4).height=36;
  for(let r=R0;r<=R1;r++){
    const t=list[r-R0],row=ws.getRow(r);
    row.getCell(1).value={formula:`IF(B${r}="","",ROW()-4)`};
    if(t){
      row.getCell(2).value=t.title;row.getCell(3).value=tgs(t).join(", ")||null;row.getCell(4).value=t.who||null;
      row.getCell(5).value=D(t.start);row.getCell(6).value=D(t.end);row.getCell(7).value=ST[t.status];
      const dp=(t.deps||[]).map(i=>nr[i]).filter(Boolean).join(",");if(dp)row.getCell(8).value=dp;
      const ck=(t.checklist||[]).map(c=>(c.d?"[x] ":"[ ] ")+c.t).join("\n");if(ck)row.getCell(9).value=ck;
      if(t.notes)row.getCell(10).value=t.notes;
      if(t.proj)row.getCell(16).value=t.proj;
      if(t.prio)row.getCell(17).value="Prio "+t.prio;
    }
    row.getCell(17).dataValidation={type:"list",allowBlank:true,formulae:['"Prio 1,Prio 2,Prio 3"']};
    const dn_=`(LEN(LOWER(I${r}))-LEN(SUBSTITUTE(LOWER(I${r}),"[x]","")))/3`,op_=`(LEN(I${r})-LEN(SUBSTITUTE(I${r},"[ ]","")))/3`;
    row.getCell(11).value={formula:`IF(I${r}="","",${dn_}&"/"&(${dn_}+${op_}))`};
    row.getCell(12).value={formula:`IF(OR(B${r}="",H${r}="",E${r}=""),"",IF(SUMPRODUCT(($A$${R0}:$A$${R1}<>"")*ISNUMBER(SEARCH(","&$A$${R0}:$A$${R1}&",",","&SUBSTITUTE(H${r}," ","")&","))*ISNUMBER($F$${R0}:$F$${R1})*($F$${R0}:$F$${R1}>=E${r}))>0,"Start vor Ende des Vorgängers",""))`};
    row.getCell(13).value={formula:`IF(AND($B${r}<>"",OR($G${r}="Offen",$G${r}="")),MAX(M$4:M${r-1})+1,"")`};
    row.getCell(14).value={formula:`IF(AND($B${r}<>"",$G${r}="In Arbeit"),MAX(N$4:N${r-1})+1,"")`};
    row.getCell(15).value={formula:`IF(AND($B${r}<>"",$G${r}="Erledigt"),MAX(O$4:O${r-1})+1,"")`};
    for(const c of [1,2,3,4,5,6,7,8,9,10,11,12,16,17]){const cell=row.getCell(c);cell.border=box;cell.font={size:11,color:{argb:(c===1||c===11)?C.grey:"FF1B201C"}};cell.alignment={vertical:"top",wrapText:(c===2||c===9||c===10||c===12),horizontal:(c===1||c===11)?"center":undefined}}
    row.getCell(5).numFmt="dd.mm.yyyy";row.getCell(6).numFmt="dd.mm.yyyy";row.getCell(8).numFmt="@";
    row.getCell(7).dataValidation={type:"list",allowBlank:true,formulae:['"Offen,In Arbeit,Erledigt"']};
    row.getCell(4).dataValidation={type:"list",allowBlank:true,showErrorMessage:false,formulae:['"Melanie,Lasse"']};
  }
  ws.autoFilter=`A4:Q${R1}`;
  ws.addConditionalFormatting({ref:`G${R0}:G${R1}`,rules:[
    {type:"expression",formulae:[`$G${R0}="Erledigt"`],style:cf(C.done)},
    {type:"expression",formulae:[`$G${R0}="In Arbeit"`],style:cf(C.doing)},
    {type:"expression",formulae:[`AND($B${R0}<>"",OR($G${R0}="Offen",$G${R0}=""))`],style:cf(C.todo)}]});
  ws.addConditionalFormatting({ref:`F${R0}:F${R1}`,rules:[{type:"expression",formulae:[`AND(ISNUMBER($F${R0}),$F${R0}<TODAY(),$G${R0}<>"Erledigt")`],style:{font:{bold:true,color:{argb:C.bad}}}}]});
  ws.addConditionalFormatting({ref:`L${R0}:L${R1}`,rules:[{type:"expression",formulae:[`$L${R0}<>""`],style:{font:{bold:true,color:{argb:C.bad}}}}]});
  ws.addConditionalFormatting({ref:`B${R0}:B${R1}`,rules:[{type:"expression",formulae:[`$G${R0}="Erledigt"`],style:{font:{strike:true,color:{argb:C.grey}}}}]});

  /* ---------- Blatt 2: Board (wird aus der Liste befüllt) ---------- */
  const wb2=wb.addWorksheet("Board",{views:[{showGridLines:false}],properties:{tabColor:{argb:C.bDoing}}});
  wb2.columns=[{width:4,hidden:true},{width:38},{width:2},{width:4,hidden:true},{width:38}];
  wb2.getCell("B1").value="Board";wb2.getCell("B1").font={bold:true,size:18};
  wb2.getCell("B2").value="Wird automatisch aus der Liste befüllt. Status in der Liste ändern, um eine Karte zu verschieben.";wb2.getCell("B2").font={italic:true,color:{argb:C.grey},size:10};
  const cols=[["A","B","Offen","M",C.todo],["D","E","In Arbeit","N",C.doing],["G","H","Erledigt","O",C.done]];
  const SL=40;
  cols.forEach(([ix,cd,name,hc,colr])=>{
    hdr(wb2.getCell(cd+"4"),null);wb2.getCell(cd+"4").value={formula:`"${name} ("&MAX(${L}$${hc}$${R0}:$${hc}$${R1})&")"`};
    for(let r=5;r<5+SL;r++){
      wb2.getCell(ix+r).value={formula:`IFERROR(MATCH(ROWS(${ix}$5:${ix}${r}),${L}$${hc}$${R0}:$${hc}$${R1},0)+${R0-1},"")`};
      const I=`$${ix}${r}`,g=c=>`INDEX(${L}$${c}:$${c},${I})`;
      const dates=`IFERROR(DAY(${g("E")})&"."&MONTH(${g("E")})&". – "&DAY(${g("F")})&"."&MONTH(${g("F")})&".","")`;
      const cell=wb2.getCell(cd+r);
      cell.value={formula:`IF(${I}="","",${g("B")}&CHAR(10)&${dates}&IF(${g("D")}="","","  ·  "&${g("D")}))`};
      cell.alignment={wrapText:true,vertical:"top"};cell.font={size:10};
      wb2.getRow(r).height=44;
    }
    const rng=`${cd}5:${cd}${4+SL}`;
    wb2.addConditionalFormatting({ref:rng,rules:[
      {type:"expression",formulae:[`AND(${ix}5<>"",INDEX(${L}$F:$F,${ix}5)<TODAY(),"${name}"<>"Erledigt")`],style:{font:{bold:true,color:{argb:C.bad}}}},
      {type:"expression",formulae:[`${cd}5<>""`],style:{...cf(colr),border:box}}]});
  });
  wb2.getRow(4).height=24;

  /* ---------- Blatt 3: Zeitstrahl (Gantt) ---------- */
  const DAYS=180,FC=8;
  const wg=wb.addWorksheet("Zeitstrahl",{views:[{state:"frozen",xSplit:7,ySplit:4,showGridLines:false}],properties:{tabColor:{argb:C.bDone}}});
  [5,30,11,11,11,11,9].forEach((w,i)=>wg.getColumn(i+1).width=w);
  for(let k=0;k<DAYS;k++)wg.getColumn(FC+k).width=3.2;
  wg.getCell("A1").value="Zeitstrahl";wg.getCell("A1").font={bold:true,size:18};
  wg.getCell("B2").value="Anzeige ab (überschreibbar):";wg.getCell("B2").font={size:10,color:{argb:C.grey}};
  wg.getCell("C2").value={formula:`IF(COUNT(${L}E${R0}:E${R1})=0,TODAY()-2,MIN(${L}E${R0}:E${R1})-2)`};wg.getCell("C2").numFmt="dd.mm.yyyy";wg.getCell("C2").font={bold:true};
  wg.getCell("E2").value="Abhängigkeiten: Spalte „Abh.“ zeigt die Vorgänger-Nr.; (!) = Start liegt nicht nach dem Ende des Vorgängers.";wg.getCell("E2").font={italic:true,size:10,color:{argb:C.grey}};
  ["Nr","Aufgabe","Ressource","Start","Ende","Status","Abh."].forEach((h,i)=>hdr(wg.getCell(4,i+1),h));
  const colL=n=>wg.getColumn(n).letter,F1=colL(FC),F2=colL(FC+DAYS-1);
  for(let k=0;k<DAYS;k++){
    const cl=colL(FC+k),pv=colL(FC+k-1),h=wg.getCell(cl+"4"),m=wg.getCell(cl+"3");
    h.value={formula:k===0?"$C$2":`${pv}4+1`};h.numFmt="d";h.font={size:8,color:{argb:C.grey}};h.alignment={horizontal:"center"};h.border={bottom:edge};
    m.value={formula:k===0?`${cl}4`:`IF(DAY(${cl}4)=1,${cl}4,"")`};m.numFmt="mmm";m.font={size:8,bold:true};
  }
  for(let r=R0;r<=R1;r++){
    const row=wg.getRow(r),f=[`${L}A${r}`,`IF(${L}B${r}="","",${L}B${r})`,`IF(${L}D${r}="","",${L}D${r})`,`IF(${L}E${r}="","",${L}E${r})`,`IF(${L}E${r}="","",IF(${L}F${r}="",${L}E${r},${L}F${r}))`,`IF(${L}B${r}="","",IF(${L}G${r}="","Offen",${L}G${r}))`,`IF(${L}H${r}="","",${L}H${r}&IF(${L}L${r}="",""," (!)"))`];
    f.forEach((x,i)=>{const c=row.getCell(i+1);c.value={formula:x};c.font={size:10};c.border={bottom:edge};if(i===3||i===4)c.numFmt="dd.mm.yy"});
  }
  const rg=`${F1}${R0}:${F2}${R1}`,hd=`${F1}$4`,inb=`AND($D${R0}<>"",${hd}>=$D${R0},${hd}<=$E${R0})`;
  wg.addConditionalFormatting({ref:rg,rules:[
    {type:"expression",formulae:[`AND(${inb},$F${R0}="Erledigt")`],style:cf(C.bDone)},
    {type:"expression",formulae:[`AND(${inb},$F${R0}="In Arbeit")`],style:cf(C.bDoing)},
    {type:"expression",formulae:[inb],style:cf(C.bTodo)},
    {type:"expression",formulae:[`${hd}=TODAY()`],style:cf(C.today)},
    {type:"expression",formulae:[`WEEKDAY(${hd},2)>5`],style:cf(C.we)}]});
  wg.addConditionalFormatting({ref:`${F1}3:${F2}4`,rules:[
    {type:"expression",formulae:[`${F1}$4=TODAY()`],style:cf(C.today)},
    {type:"expression",formulae:[`WEEKDAY(${F1}$4,2)>5`],style:cf(C.we)}]});
  wg.addConditionalFormatting({ref:`G${R0}:G${R1}`,rules:[{type:"expression",formulae:[`ISNUMBER(SEARCH("(!)",$G${R0}))`],style:{font:{bold:true,color:{argb:C.bad}}}}]});
  wg.addConditionalFormatting({ref:`B${R0}:B${R1}`,rules:[{type:"expression",formulae:[`$F${R0}="Erledigt"`],style:{font:{color:{argb:C.grey},strike:true}}}]});
  return await wb.xlsx.writeBuffer();
}
$("x_xlsx").onclick=async()=>{
  try{$("note").textContent="Excel-Datei wird erstellt …";await loadJs(LIB.xlsx,"ExcelJS");
    const buf=await buildXlsx();$("note").textContent="";
    await dl("planner-"+stamp()+".xlsx",new Blob([buf],{type:"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}))
  }catch(e){$("note").textContent="Excel-Export fehlgeschlagen: "+((e&&(e.message||e.code))||e)}
};

