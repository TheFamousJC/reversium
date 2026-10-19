"""Offline browser review tools; imported data is never interpreted as markup."""
from .map_review import FUNCTIONS as MAP_FUNCTIONS, UI as MAP_UI

PANEL = '''<h2>Compare with a saved report</h2><p>Choose an earlier Reversium report JSON. Both reports stay on this device. This compares file inventory, available content hashes and finding identities, feature-map relationships, not runtime behavior. Different analyzer versions can produce different findings from identical code. Checklist notes are preserved.</p><label>Earlier report (JSON, maximum 32 MiB) <input id="baseline-import" type="file" accept=".json,application/json"></label><button id="baseline-save" disabled>Save comparison notes</button><button id="baseline-clear">Clear comparison</button><p id="baseline-status" role="status">Save a report JSON after each delivery to compare it here later.</p><div id="baseline-results"></div>'''

FUNCTIONS = r"""
function validateChecklist(saved,report){
 const ids=['workflow','runtime','configuration','services','run'],statuses=['Not checked','Needs information','Blocked','Verified by reviewer'];
 if(!saved||saved.format!=='reversium-handover'||![1,2].includes(saved.version)||!Array.isArray(saved.tasks)||saved.tasks.length!==ids.length)throw Error('Unsupported checklist format. Choose a saved handover JSON.');
 const legacy=saved.version===1;
 if(legacy){if(!report.archive_name||saved.archive_name!==report.archive_name)throw Error('Legacy checklist package name does not match.');}
 else if(!/^[a-f0-9]{64}$/.test(saved.archive_sha256||'')||saved.archive_sha256!==report.archive_sha256)throw Error('Delivery fingerprint does not match. Choose the checklist for this report, or analyze the matching original ZIP in Reversium.');
 const seen=new Set();
 for(const t of saved.tasks){if(!t||!ids.includes(t.id)||seen.has(t.id)||!statuses.includes(t.status)||typeof t.owner!=='string'||t.owner.length>100||typeof t.notes!=='string'||t.notes.length>2000)throw Error('Invalid checklist tasks. Existing notes were kept.');seen.add(t.id);}
 return {legacy,tasks:saved.tasks};
}
function compareLocal(current,previous){
 function check(r){
  if(!r||![1,2,3].includes(r.schema_version)||!Array.isArray(r.files)||r.files.length>10000||!Array.isArray(r.findings)||r.findings.length>200000)throw Error('Unsupported or oversized report structure.');
  const paths=new Set();
  for(const f of r.files){if(!f||typeof f.path!=='string'||f.path.length>4096||paths.has(f.path)|| (f.sha256!==undefined&&!/^[a-f0-9]{64}$/.test(f.sha256)))throw Error('Invalid or duplicate file entry.');paths.add(f.path);}
  for(const f of r.findings)if(!f||typeof f.kind!=='string'||typeof f.value!=='string'||typeof f.evidence?.file!=='string'||f.kind.length>300||f.value.length>10000||f.evidence.file.length>4096)throw Error('Invalid finding entry.');
 }
 check(current);check(previous);
 const old=new Map(previous.files.map(f=>[f.path,f])),now=new Map(current.files.map(f=>[f.path,f]));
 const key=f=>JSON.stringify([f.kind,f.value,f.evidence.file]),before=new Map(previous.findings.map(f=>[key(f),f])),after=new Map(current.findings.map(f=>[key(f),f]));
 return {added_files:[...now.keys()].filter(p=>!old.has(p)).sort(),removed_files:[...old.keys()].filter(p=>!now.has(p)).sort(),changed_files:[...now.keys()].filter(p=>old.has(p)&&now.get(p).sha256&&old.get(p).sha256&&now.get(p).sha256!==old.get(p).sha256).sort(),unverified_files:[...now.keys()].filter(p=>old.has(p)&&(!now.get(p).sha256||!old.get(p).sha256)).sort(),added_findings:[...after.keys()].filter(k=>!before.has(k)).map(k=>after.get(k)),removed_findings:[...before.keys()].filter(k=>!after.has(k)).map(k=>before.get(k))};
}
"""

FUNCTIONS += MAP_FUNCTIONS

SCRIPT = FUNCTIONS + MAP_UI + r"""
(()=>{
const $=s=>document.querySelector(s),report=JSON.parse($('#report-data').textContent);let pending=null,restoreSerial=0,compareSerial=0;
if(parent!==window&&location.href==='about:srcdoc'){for(const kind of ['handover','baseline'])$('#'+kind+'-import').onclick=e=>{e.preventDefault();parent.postMessage({type:'reversium-review-pick',kind},'*');};window.addEventListener('message',e=>{if(e.source!==parent||e.data?.type!=='reversium-review-file'||!['handover','baseline'].includes(e.data.kind)||!(e.data.file instanceof File))return;$('#'+e.data.kind+'-import').onchange({target:{files:[e.data.file],value:''}});});}
$('#handover-import').onchange=async e=>{const serial=++restoreSerial;pending=null;$('#handover-apply').hidden=true;$('#handover-preview').textContent='';const file=e.target.files[0];if(!file)return;
try{if(file.size>1048576)throw Error('Checklist exceeds 1 MiB.');const saved=JSON.parse(await file.text());if(serial!==restoreSerial)return;const validated=validateChecklist(saved,report);pending=validated;
$('#handover-preview').textContent=(validated.legacy?'Legacy checklist: name matches, but this format has no fingerprint. Confirm independently that it belongs to this delivery.':'Exact ZIP fingerprint matches.')+'\nRestoring replaces all five current task annotations. Review these notes first:\n'+validated.tasks.map(t=>t.id+' / '+t.status+' / '+t.owner+'\n'+t.notes).join('\n\n');$('#handover-apply').hidden=false;$('#handover-status').textContent='Preview ready. Current notes are unchanged until you press Replace.';
}catch(error){if(serial===restoreSerial)$('#handover-status').textContent='Not restored: '+error.message;}finally{e.target.value='';}};
$('#handover-apply').onclick=()=>{if(!pending)return;for(const t of pending.tasks){const el=$('.handover-task[data-task="'+t.id+'"]');el.querySelector('.task-status').value=t.status;el.querySelector('.task-owner').value=t.owner;el.querySelector('.task-notes').value=t.notes;}$('#handover-status').textContent=pending.legacy?'Legacy notes restored by your confirmation; delivery identity was not verified. Save a new checklist to bind future restores to this ZIP.':'Checklist restored for this exact ZIP. Reviewer statuses remain annotations, not automated verification.';pending=null;$('#handover-apply').hidden=true;$('#handover-preview').textContent='';};
$('#baseline-save').onclick=()=>download('Reversium structural comparison\n'+$('#baseline-status').textContent+'\n\n'+$('#baseline-results').innerText,'text/plain','reversium-comparison.txt');
$('#baseline-clear').onclick=()=>{compareSerial++;$('#baseline-save').disabled=true;$('#baseline-import').value='';$('#baseline-results').replaceChildren();$('#baseline-status').textContent='Comparison cleared. Checklist notes are unchanged.';};
$('#baseline-import').onchange=async e=>{const serial=++compareSerial,file=e.target.files[0];$('#baseline-results').replaceChildren();$('#baseline-save').disabled=true;if(!file)return;$('#baseline-status').textContent='Reading the earlier report locally…';
try{if(file.size>33554432)throw Error('Report exceeds 32 MiB.');const previous=JSON.parse(await file.text());if(serial!==compareSerial)return;const result=compareLocal(report,previous),area=$('#baseline-results');$('#baseline-save').disabled=false;
$('#baseline-status').textContent='Compared current '+(report.archive_name||'package')+' with '+(previous.archive_name||file.name)+'. Structural evidence only; analyzer changes can affect findings. Each list shows at most 200 entries. Comparison is temporary; save these results as readable notes.';
drawMapComparison(report,previous,area);
for(const [key,items] of Object.entries(result)){const h=document.createElement('h3');h.textContent=key.replaceAll('_',' ')+': '+items.length;area.append(h);const list=document.createElement('ul');for(const item of items.slice(0,200)){const li=document.createElement('li');li.textContent=typeof item==='string'?item:item.kind+': '+item.value+' — '+item.evidence.file;list.append(li);}area.append(list);if(items.length>200){const p=document.createElement('p');p.textContent=(items.length-200)+' further entries omitted from this view.';area.append(p);}}
}catch(error){if(serial===compareSerial){$('#baseline-results').replaceChildren();$('#baseline-save').disabled=true;}if(serial===compareSerial)$('#baseline-status').textContent='Comparison not loaded: '+error.message;}finally{e.target.value='';}};
})();
"""
