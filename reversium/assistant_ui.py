"""Self-contained optional assistant; no remote scripts or automatic sharing."""

import html
from .assistant import INSTRUCTIONS

PANEL = '''<!--assistant-session--><h2>Optional AI assistant</h2>
<p>Local analysis is free and works without an account. AI uses your own eligible ChatGPT plan and its limits. Only the request you preview and approve is sent to OpenAI. Authentication opens a separate provider screen; answers stay here.</p>
<ol><li>Connect your account.</li><li>Select evidence and ask a question.</li><li>Review exactly what will be shared, then send.</li></ol>
<details open><summary>Setup wizard · 1. Connect</summary>
<p>Install the optional sign-in dependency once: <code>python -m pip install -r requirements-ai.txt</code>. The archive analyzer itself needs no packages. Account tokens stay in server memory, never in reports or browser storage. Restarting Reversium requires sign-in again.</p>
<button id="ai-connect">Continue with ChatGPT</button> <button id="ai-status">Check connection</button> <button id="ai-disconnect">Disconnect</button>
<p id="ai-account" role="status">Not connected. No evidence has been shared.</p>
<label for="ai-model">Account model</label><select id="ai-model"><option value="">Connect to load eligible models</option></select></details>
<details open><summary>2. Choose evidence</summary>
<p>Select at most 30 findings. Only selected finding descriptions, locations and confidence are included; the ZIP and source file contents are excluded. Filenames and descriptions can still be sensitive. Review or edit the outgoing JSON below. Automatic redaction is only a best-effort aid.</p>
<label for="ai-search">Find evidence to share</label><input id="ai-search" type="search" placeholder="Search findings by file, symbol or operation">
<p id="ai-selection">0 selected</p><div id="ai-findings" class="ai-findings"></div>
<label for="ai-question">Your question</label><textarea id="ai-question" maxlength="4000" rows="3" placeholder="What does this workflow do, and what is still unknown?"></textarea>
<button id="ai-prepare">Prepare sharing preview</button></details>
<details open><summary>3. Review and ask</summary>
<label for="ai-preview">Exact user content sent to OpenAI (editable JSON)</label><textarea id="ai-preview" rows="10" spellcheck="false"></textarea>
<details><summary>Assistant instructions also sent</summary><p>{assistant_instructions}</p></details>
<label><input type="checkbox" id="ai-consent"> I reviewed this question and evidence and approve sharing this request with OpenAI.</label>
<button id="ai-send" disabled>Send approved request</button> <button id="ai-clear">Clear question and answer</button>
<p id="ai-progress" role="status">Nothing sent.</p><section id="ai-answer" aria-live="polite"></section></details>
<h3>Frequently asked questions</h3>
<details><summary>Is local analysis still free?</summary><p>Yes. Inventory, tracing, diagrams and local reports work without AI, sign-in or an internet connection. Cloud AI depends on your plan, eligibility and usage limits. Reversium does not fall back to separately billed API keys.</p></details>
<details><summary>Does connecting upload my ZIP?</summary><p>No. Sign-in shares account authorization information, not your ZIP. Each question sends only its approved preview plus assistant instructions. No automatic whole-report upload, tool execution or background evidence retrieval occurs.</p></details>
<details><summary>Can I trust the answer?</summary><p>Answers are AI interpretations, not verified runtime facts. Reversium rejects claims with missing or unselected citation IDs, but a valid citation does not prove the interpretation is correct. Open the linked finding and check the unknowns.</p></details>
<details><summary>Why can’t I connect?</summary><p>Check the optional dependency, internet connection, ChatGPT account eligibility and plan permission. Sign-in expires after ten minutes; retry if needed. This integration uses OpenAI’s documented open-source sign-in flow. Its availability may change.</p></details>
<details><summary>What is saved?</summary><p>Tokens and answers are held only for the running session. Local host and account-registration identifiers are retained under reports/assistant-host.json and reports/assistant-registration.json so the same account can reconnect. To switch accounts, disconnect and remove the registration file locally before reconnecting. Disconnect removes local account tokens; it does not revoke provider-side consent. Manage app authorization in ChatGPT settings. Saved HTML exports omit the question, preview, selection, account identity and AI answer. Export the local analysis separately.</p></details>
<details><summary>Can the assistant install or run the uploaded software?</summary><p>No. It can explain selected findings and suggest checks. It has no command, file-editing or execution tools.</p></details>'''

PANEL = PANEL.replace('{assistant_instructions}', html.escape(INSTRUCTIONS))

STYLE = '''.ai-findings{max-height:280px;overflow:auto;border:1px solid #657890;padding:12px}.ai-findings label{display:block;overflow-wrap:anywhere;margin:10px 0}textarea{display:block;box-sizing:border-box;width:100%;max-width:950px;margin:12px 0;padding:12px;background:#162130;color:#e8edf5;border:1px solid #657890;border-radius:8px}#ai-answer{white-space:pre-wrap;overflow-wrap:anywhere}#panel-assistant details{margin:16px 0}#panel-assistant label{line-height:1.7}'''

SCRIPT = r'''
(()=>{
const aiPanel=document.querySelector('#panel-assistant');
if(aiPanel){
 const $=s=>aiPanel.querySelector(s), chosen=new Set();let connected=false,busy=false;
 const findings=typeof reportData==='undefined'?[]:reportData.findings||[];
 const session=document.querySelector('meta[name=assistant-session]')?.content;
 async function api(path,body={}){if(!session||location.protocol==='file:')throw Error('Open the running local Reversium app to use AI. Saved reports keep local analysis only.');const r=await fetch('/assistant/'+path,{method:'POST',headers:{'Content-Type':'application/json','X-Reversium-Session':session},body:JSON.stringify(body)});const data=await r.json();if(!r.ok)throw Error(data.error||'Local assistant request failed.');return data}
 function gate(){$('#ai-send').disabled=busy||!connected||!$('#ai-model').value||!$('#ai-consent').checked||!$('#ai-preview').value}
 function invalidate(){ $('#ai-consent').checked=false;gate() }
 function redact(text){return text.replace(/\bsk-[A-Za-z0-9_-]{12,}\b/g,'[REDACTED KEY]').replace(/\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/g,'[REDACTED TOKEN]').replace(/(password|secret|api[_-]?key)\s*[:=]\s*[^\s,;]+/gi,'$1=[REDACTED]')}
 function showFindings(){const q=$('#ai-search').value.toLowerCase(),box=$('#ai-findings');box.replaceChildren();let shown=0;for(let i=0;i<findings.length&&shown<100;i++){const f=findings[i],t=JSON.stringify(f);if(q&&!t.toLowerCase().includes(q))continue;shown++;const label=document.createElement('label'),check=document.createElement('input');check.type='checkbox';check.checked=chosen.has(i);check.onchange=()=>{if(check.checked&&chosen.size>=30){check.checked=false;return}check.checked?chosen.add(i):chosen.delete(i);$('#ai-selection').textContent=chosen.size+' selected';invalidate()};label.append(check,document.createTextNode(' #'+i+' '+f.kind+': '+String(f.value).slice(0,240)+' — '+f.evidence.file));box.append(label)}if(!findings.length)box.textContent='Analyze a ZIP or open a sample report first. No evidence is available on the home screen.';else{const p=document.createElement('p');p.textContent='Showing up to 100 matching findings. Search to narrow the list.';box.append(p)}}
 async function status(){const s=await api('status');connected=s.connected;$('#ai-account').textContent=s.connected?'Connected: '+s.account:'Not connected. Local analysis remains available.';$('#ai-model').replaceChildren();for(const m of s.models){const o=document.createElement('option');o.value=m.id;o.textContent=m.name;$('#ai-model').append(o)}gate()}
 $('#ai-connect').onclick=async()=>{try{const r=await api('connect');const a=document.createElement('a');a.href=r.url;a.target='_blank';a.rel='noopener noreferrer';a.textContent='Open OpenAI sign-in';$('#ai-account').replaceChildren(a,document.createTextNode(' — return here and choose Check connection afterward.'));}catch(e){$('#ai-account').textContent=e.message}};
 $('#ai-status').onclick=()=>status().catch(e=>$('#ai-account').textContent=e.message);
 $('#ai-disconnect').onclick=async()=>{try{await api('disconnect');connected=false;$('#ai-account').textContent='Disconnected. Local tokens removed.';$('#ai-model').replaceChildren();gate()}catch(e){$('#ai-account').textContent=e.message}};
 $('#ai-search').oninput=showFindings;$('#ai-question').oninput=invalidate;$('#ai-model').onchange=invalidate;$('#ai-preview').oninput=invalidate;$('#ai-consent').onchange=gate;
 $('#ai-prepare').onclick=()=>{const evidence=[...chosen].sort((a,b)=>a-b).map(i=>{const f=findings[i];return{id:i,text:redact(JSON.stringify({kind:f.kind,value:f.value,confidence:f.confidence,location:f.evidence.file,line:f.evidence.line,offset:f.evidence.offset})).slice(0,4000)}});$('#ai-preview').value=JSON.stringify({question:$('#ai-question').value,evidence},null,2);invalidate();$('#ai-progress').textContent='Preview prepared locally. Nothing sent.'};
 $('#ai-clear').onclick=()=>{chosen.clear();$('#ai-question').value='';$('#ai-preview').value='';$('#ai-answer').replaceChildren();$('#ai-selection').textContent='0 selected';$('#ai-progress').textContent='Cleared locally. Previously shared content cannot be recalled.';invalidate();showFindings()};
 $('#ai-send').onclick=async()=>{busy=true;gate();$('#ai-progress').textContent='Request in progress. No automatic retries.';$('#ai-answer').replaceChildren();try{const packet=JSON.parse($('#ai-preview').value);const ids=new Set(packet.evidence.map(e=>e.id));if(packet.evidence.some(e=>!Number.isInteger(e.id)||!findings[e.id]))throw Error('Evidence IDs must refer to this report.');const answer=await api('ask',{model:$('#ai-model').value,packet,consent:true});const heading=document.createElement('h3');heading.textContent='AI interpretation — check its cited evidence';$('#ai-answer').append(heading);for(const c of answer.claims){const p=document.createElement('p');p.textContent=c.text+' ';for(const id of c.evidence_ids){if(!ids.has(id))throw Error('Unshared citation rejected.');const a=document.createElement('a');a.href='#finding-'+id;a.textContent='[Finding '+id+'] ';a.onclick=()=>revealFinding(a.getAttribute('href'));p.append(a)}$('#ai-answer').append(p)}const h=document.createElement('h3');h.textContent='Unknowns';$('#ai-answer').append(h);for(const u of answer.unknowns){const p=document.createElement('p');p.textContent=u;$('#ai-answer').append(p)}$('#ai-progress').textContent='Completed. Citations are selected evidence references, not verification of correctness.'}catch(e){$('#ai-progress').textContent=e.message}finally{busy=false;invalidate()}};
 showFindings();gate();
}
})();
'''
