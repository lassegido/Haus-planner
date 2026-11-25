/* Export */
async function dl(name,data){try{const d=await window.claude.use("downloads");if(!d){$("note").textContent="Herunterladen ist hier nicht möglich.";return}await d.save({filename:name,data});$("dlx").close()}catch(e){if(!e||e.code!=="declined")$("note").textContent="Herunterladen fehlgeschlagen: "+((e&&(e.message||e.code))||"unbekannt")}}
