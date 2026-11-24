/* Export */
async function dl(name,data){
  try{const blob=data instanceof Blob?data:new Blob([data],{type:"application/pdf"}),file=new File([blob],name,{type:blob.type});
    if(matchMedia("(pointer:coarse)").matches&&navigator.canShare&&navigator.canShare({files:[file]})){
      try{await navigator.share({files:[file]});$("dlx").close();return}catch(e){if(e&&e.name==="AbortError")return}}
    const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(a.href),5000);$("dlx").close()
  }catch(e){$("note").textContent="Download fehlgeschlagen: "+(e.message||e)}}
