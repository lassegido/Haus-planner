/* Darstellung: Hell/Dunkel, Akzentfarbe */
const hostTheme=document.documentElement.dataset.theme||"";
const pg=prefGet;
const DK=["--bg","--surf","--card","--tx","--mut","--faint","--line","--line2","--wk","--side","--side-mut","--acc","--on-acc","--acc-soft","--tagc","--focus","--acc2","--acc3"];
/* Farbwelten (ab 1.40.1 im Stil „Polarlicht“): getönte Flächen, kräftige Seitenleiste, Akzent mit Verlauf (--acc → --acc2, Ring endet in --acc3).
   Kuratiert und auf Kontrast geprüft (tools/e2e/test_farbwelten.py). Je Farbwelt genau eine Akzentfarbe für Bedienelemente;
   keine rote, orange oder gelbe Akzentfarbe, damit nichts wie ein Status aussieht. Statusfarben bleiben überall gleich. */
const DES=[
 ["porto","Portofino","Creme, Meerblau, Sonnenorange",null,null],
 ["polar","Polarlicht","Indigo bis Petrol, wie Nordlicht",["#F1F2F8","#FFFFFF","#FFFFFF","#1B1E3A","#5A5F80","#868AA6","#E3E4F0","#D0D2E4","#E8E9F4","#23264A","#B9BCD9","#5B4FC9","#FFFFFF","#ECEAFB","#4A3FB0","#5B4FC9","#23808F","#6CB6E4"],
  ["#10122A","#171A36","#1C2040","#EEF0FA","#A3A7C9","#6F7396","#272B4F","#343963","#141733","#0B0C1F","#A9ADD6","#A99CFF","#15122E","#2A2856","#C9C0FF","#A99CFF","#6FD5E3","#6CB6E4"]],
 ["wald","Wald","Smaragd bis Moos, natürlich",["#F2F8F5","#FFFFFF","#FFFFFF","#1A3326","#557766","#7D968A","#E3EDE8","#D0DFD7","#EAF2EE","#234333","#C1D7CC","#1E7A4E","#FFFFFF","#EEFCF5","#196440","#1E7A4E","#4F7A12","#B5D65A"],
  ["#0E2017","#162A20","#1B3226","#EEF7F2","#A8C8B8","#749585","#284336","#365947","#12241B","#09130E","#B4D0C2","#6CD39E","#0F291C","#2B4A3B","#AEE7CA","#6CD39E","#B9DC6E","#E3F09A"]],
 ["lagune","Lagune","Türkis bis Kobalt, frisch wie Wasser",["#F2F7F8","#FFFFFF","#FFFFFF","#192E34","#547178","#7D9297","#E3EBEE","#CFDCE0","#E9F0F2","#223D44","#C1D3D7","#0B6E7B","#FFFFFF","#EEFAFC","#095A65","#0B6E7B","#2F55C4","#7FD6E6"],
  ["#0E1C20","#15262B","#1A2E32","#EDF5F7","#A6C2C9","#738F96","#273E44","#35525A","#112125","#081214","#B3CBD0","#5ED0DD","#0F2429","#2A464C","#A6E5EC","#5ED0DD","#93AEFF","#B8F0E8"]],
 ["orchidee","Orchidee","Violett bis Magenta, kräftig",["#F5F2F8","#FFFFFF","#FFFFFF","#261A33","#665577","#8A7D96","#E8E3ED","#D7D0DF","#EEEAF2","#332343","#CCC1D7","#6A3FC6","#FFFFFF","#F4EEFC","#5734A2","#6A3FC6","#A42E7C","#F2A2D2"],
  ["#170E20","#20162A","#261B32","#F2EEF7","#B8A8C8","#857495","#362843","#473659","#1B1224","#0E0913","#C2B4D0","#B89DFF","#1B0F29","#3A2B4A","#D8C9FF","#B89DFF","#F08DC6","#FFC9E6"]],
 ["feige","Feige","Aubergine bis Altrosa, warm wie Sand",["#F7F3F1","#FFFFFF","#FFFFFF","#31241B","#756457","#94887F","#EDE7E4","#DED6D1","#F1EDEA","#413125","#D5CAC3","#7A3A76","#FFFFFF","#FCEEFB","#643061","#7A3A76","#A3446F","#F0B8CF"],
  ["#1E160F","#291E17","#30251C","#F6F2EE","#C6B5AA","#938276","#41342A","#564539","#231913","#130D09","#CEC0B6","#D9A2E0","#290F27","#482D46","#EACCEE","#D9A2E0","#EE97BE","#FFD3E4"]],
 ["schiefer","Schiefer","Kühles Grau, Tinte bis Petrol, sachlich",["#F4F5F6","#FFFFFF","#FFFFFF","#22252B","#60656C","#85898E","#E6E8EA","#D5D7DA","#ECEDEF","#2D3239","#C8CBD0","#34557F","#FFFFFF","#EEF4FC","#2B4668","#34557F","#22737A","#8CC4D6"],
  ["#14161A","#1C1F24","#22262A","#F1F2F4","#B2B7BD","#7F848B","#31353B","#41464E","#171A1E","#0C0E10","#BDC1C7","#93B5E6","#0F1A29","#353A40","#C4D6F1","#93B5E6","#7FD0D4","#C6E6F0"]]];
/* Frühere Farbwelten (bis 1.40.0) → Nachfolger; gespeicherte Wahl wird beim nächsten Öffnen umgestellt */
const DES_OLD={salbei:"wald",beere:"orchidee",graphit:"schiefer"};
function isDark(){const th=pg("theme")||"auto";return th==="dark"||(th==="auto"&&(hostTheme?hostTheme==="dark":matchMedia("(prefers-color-scheme:dark)").matches))}
function applyTheme(){
  const th=pg("theme")||"auto",ac=pg("acc")||"",r=document.documentElement;let ds=pg("design")||"porto";
  if(DES_OLD[ds]){ds=DES_OLD[ds];prefSet("design",ds)}
  if(th==="auto"){hostTheme?r.dataset.theme=hostTheme:r.removeAttribute("data-theme")}else r.dataset.theme=th;
  const dark=isDark();
  DK.forEach(k=>r.style.removeProperty(k));
  const d=DES.find(x=>x[0]===ds);if(d&&d[3])d[dark?4:3].forEach((v,i)=>r.style.setProperty(DK[i],v));
}
applyTheme();
matchMedia("(prefers-color-scheme:dark)").addEventListener("change",applyTheme);

/* Fremdcode-Adressen. Das Add-on bekommt lokale Dateien aus planner/vendor/ (tools/build.py ersetzt diese Zeile). */
const LIB={pdf:"https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js",xlsx:"https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.4.0/exceljs.min.js",font:f=>"https://fonts.googleapis.com/css2?family="+f+"&display=swap"};
const SYSF='-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
const FONTS=[["figtree","Figtree","Figtree:wght@400;500;600;700;800",'"Figtree",'+SYSF,"Freundlich und klar (Standard)"],
 ["sys","Systemschrift","",SYSF,"Sachlich wie iOS (auf dem iPhone San Francisco), lädt sofort"],
 ["fraunces","Fraunces und Figtree","Fraunces:opsz,wght@9..144,600;9..144,700&family=Figtree:wght@400;500;600;700;800",'"Figtree",'+SYSF,"Elegante Überschriften mit Serifen",'"Fraunces",Georgia,"Times New Roman",serif']];
function applyFont(){
  const k=pg("font")||"figtree",f=FONTS.find(x=>x[0]===k)||FONTS[0],r=document.documentElement;
  const fh=f[2]&&LIB.font(f[2]);if(fh&&![...document.querySelectorAll("link[data-gf]")].some(l=>l.getAttribute("href")===fh)){const l=document.createElement("link");l.dataset.gf=f[0];l.rel="stylesheet";l.href=fh;document.head.appendChild(l)}
  r.style.setProperty("--fb",f[3]);r.style.setProperty("--disp",f[5]||f[3])}
applyFont();

