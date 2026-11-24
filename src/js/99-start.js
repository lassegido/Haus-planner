$("ftog").onclick=()=>{const f=$("filters");f.classList.toggle("open");if(f.classList.contains("open"))$("q").focus()};
$("main").addEventListener("click",e=>{const t=e.target.closest("[data-ht]");if(!t)return;hap(6);prefSet("htile",t.dataset.ht);render()});
$("main").addEventListener("input",e=>{if(e.target.id==="qadd"){const v=e.target.value;$("qprev").innerHTML=v.trim()?qChips(parseQuick(v)):"";$("qsug").innerHTML=v.trim()?sugHtml(sugFind(v)):""}});
$("main").addEventListener("click",e=>{const b=e.target.closest&&e.target.closest("#qsug [data-sid]");if(b)sugOpen(b.dataset.sid)});
$("main").addEventListener("keydown",async e=>{if(e.target.id!=="qadd")return;if(e.key==="ArrowDown")return sugDown(e,$("qsug"));if(e.key!=="Enter")return;e.preventDefault();const v=e.target.value;if(!v.trim())return;
  qaddKeep=true;e.target.value="";$("qprev").innerHTML="";$("qsug").innerHTML="";if(!await quickAdd(v)){e.target.value=v}});
$("main").addEventListener("click",e=>{const b=e.target.closest("[data-hw]");if(!b)return;prefSet("hwho",b.dataset.hw);render()});
$("q").oninput=render;$("fw").onchange=render;
$("chips").onclick=e=>{const b=e.target.closest("button");if(!b)return;if("cw" in b.dataset)$("fw").value=b.dataset.cw;render()};
$("tabs").onclick=e=>{const bt=e.target.closest("button"),v=bt&&bt.dataset.v;if(!v)return;view=v;[...$("tabs").children].forEach(b=>b.classList.toggle("on",b.dataset.v===v));render()};
(function(){const s=$("splash");let seen=false;try{seen=sessionStorage.getItem("hp-start")}catch(e){}
  if(seen||reduced()){s.remove();return}
  try{sessionStorage.setItem("hp-start","1")}catch(e){}
  
  const close=()=>{s.classList.add("out");setTimeout(()=>s.remove(),700)};setTimeout(close,1100);s.onclick=close})();
init();
