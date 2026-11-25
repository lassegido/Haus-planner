/* Darstellung: Hell/Dunkel, Akzentfarbe */
const hostTheme=document.documentElement.dataset.theme||"";
const pg=prefGet;
const DK=["--bg","--surf","--card","--tx","--mut","--faint","--line","--line2","--wk","--side","--side-mut","--acc","--on-acc","--acc-soft","--tagc","--focus","--acc2"];
/* Farbwelten: kuratiert und auf Kontrast geprüft (Text ≥ 4,5 : 1, Bedienelemente ≥ 3 : 1, Hell und Dunkel).
   Je Farbwelt genau eine Akzentfarbe; Statusfarben (Offen, In Arbeit, Erledigt, Überfällig) bleiben überall gleich. */
const DES=[
 ["porto","Portofino","Creme, Meerblau, Sonnenorange",null,null],
 ["salbei","Salbei","Ruhiges Grün, natürlich",["#ECEFE4","#FFFFFF","#FFFFFF","#1E2D26","#5C6F65","#7F8A83","#E1E6D8","#CFD7C6","#E4E8DA","#22403A","#AFC7BC","#3C755F","#FFFFFF","#E1EDE6","#2F5F4C","#3C755F","#4A7340"],
  ["#101A16","#17241F","#1C2B25","#EAF0EB","#9DB3A8","#62756B","#26382F","#324A3F","#14201B","#0B1411","#8FB5A2","#7CC4A2","#0E1A15","#223C31","#A6D9C0","#7CC4A2","#A3CC7C"]],
 ["beere","Beere","Sanftes Pastell-Violett",["#F4EFF4","#FFFCFE","#FFFCFE","#2B1F33","#6C5A78","#92879A","#E8DEEC","#D7C8DE","#ECE3EF","#5B3A6B","#D4BEE0","#7A4A92","#FFFFFF","#EEE3F3","#603878","#7A4A92","#9A3F74"],
  ["#1A1220","#221829","#2A1E32","#F4EFF4","#AE9BBA","#75677D","#3A2A44","#4A3857","#1E1526","#120B17","#B79BC8","#C79BE0","#22112B","#3A2548","#DDBFF0","#C79BE0","#E59AC2"]],
 ["graphit","Graphit","Neutrales Grau, sachlich",["#F0F1F2","#FFFFFF","#FFFFFF","#1B2126","#5C666E","#868C91","#E0E3E5","#CDD2D6","#E7E9EB","#2A3238","#B6C0C8","#3E5C74","#FFFFFF","#E2E9EE","#34505F","#3E5C74","#4B5A80"],
  ["#121518","#1A1E22","#20252A","#EEF0F2","#9AA5AD","#677076","#2A3036","#38414A","#161A1E","#0C0E10","#9AA9B4","#8FB4D0","#101820","#26333E","#B5D0E3","#8FB4D0","#A3A9DD"]],
 /* 1.40: zum Ausprobieren. Indigo bis Petrol als Verlauf; Violett ist klar von allen Statusfarben unterscheidbar */
 ["polar","Polarlicht","Indigo und Petrol, mit Verlauf",["#F1F2F8","#FFFFFF","#FFFFFF","#1B1E3A","#5A5F80","#868AA6","#E3E4F0","#D0D2E4","#E8E9F4","#23264A","#B9BCD9","#5B4FC9","#FFFFFF","#ECEAFB","#4A3FB0","#5B4FC9","#23808F"],
  ["#10122A","#171A36","#1C2040","#EEF0FA","#A3A7C9","#6F7396","#272B4F","#343963","#141733","#0B0C1F","#A9ADD6","#A99CFF","#15122E","#2A2856","#C9C0FF","#A99CFF","#6FD5E3"]]];
function isDark(){const th=pg("theme")||"auto";return th==="dark"||(th==="auto"&&(hostTheme?hostTheme==="dark":matchMedia("(prefers-color-scheme:dark)").matches))}
function applyTheme(){
  const th=pg("theme")||"auto",ac=pg("acc")||"",ds=pg("design")||"porto",r=document.documentElement;
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

