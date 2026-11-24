/* Export */
async function dl(name,data){try{const d=await window.claude.use("downloads");if(!d){$("note").textContent="Download ist hier nicht verfügbar.";return}await d.save({filename:name,data});$("dlx").close()}catch(e){if(!e||e.code!=="declined")$("note").textContent="Download fehlgeschlagen: "+((e&&(e.message||e.code))||"unbekannt")}}
