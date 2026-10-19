"""Dependency-free on-device handover ZIP. Never includes the input archive."""
PANEL='''<section id="pack-panel"><h3>One-download handover pack</h3><p>Keep the readable report, technical JSON, current map SVG, full bounded map JSON, checklist and remaining questions together in one ZIP. Includes START-HERE.txt, a developer first-hour brief with setup evidence and missing prerequisites, and a file manifest. Generated on this device; the original code package and AI requests/conversations are excluded. Reports can contain private filenames, endpoints and code-derived details: inspect the pack before sharing.</p><label><input type="checkbox" id="pack-notes"> Include my checklist annotations (owners, statuses and notes)</label><label><input type="checkbox" id="pack-runtime"> Include the attached, reviewed runtime test record, if present</label><p>Both options start unchecked. The checklist is otherwise a blank review template. Pending imports and comparison previews are excluded. The map SVG is the current drawn view; its bounds/filter are recorded. The JSON retains the full generated, bounded graph.</p><button type="button" id="pack-export">Download handover pack (ZIP)</button><p id="pack-status" role="status">Ready to generate locally. Maximum combined pack content: 64 MiB.</p></section>'''

FUNCTIONS=r"""
const packCRCTable=Uint32Array.from({length:256},(_,value)=>{for(let i=0;i<8;i++)value=(value>>>1)^((value&1)?0xedb88320:0);return value>>>0;});
function packCRC32(bytes){let crc=0xffffffff;for(const value of bytes)crc=(crc>>>8)^packCRCTable[(crc^value)&255];return (crc^0xffffffff)>>>0;}
function packZip(entries,limit=67108864){
 if(!Array.isArray(entries)||!entries.length||entries.length>16)throw Error('Invalid pack entry count.');
 const encoder=new TextEncoder(),seen=new Set();let size=22;
 const files=entries.map(({name,text})=>{if(typeof name!=='string'||!/^[A-Za-z0-9][A-Za-z0-9._-]{0,100}$/.test(name)||name.includes('..')||seen.has(name)||typeof text!=='string')throw Error('Invalid pack file.');if(text.length>limit)throw Error('Pack exceeds 64 MiB. Use the individual exports or a smaller analysis.');seen.add(name);const filename=encoder.encode(name),bytes=encoder.encode(text);size+=76+filename.length*2+bytes.length;if(size>limit)throw Error('Pack exceeds 64 MiB. Use the individual exports or a smaller analysis.');return {filename,bytes,crc:packCRC32(bytes)};});
 const output=new Uint8Array(size),view=new DataView(output.buffer);let at=0;const offsets=[];
 const u16=(p,v)=>view.setUint16(p,v,true),u32=(p,v)=>view.setUint32(p,v,true);
 for(const f of files){offsets.push(at);u32(at,0x04034b50);u16(at+4,20);u16(at+6,0x800);u16(at+12,33);u32(at+14,f.crc);u32(at+18,f.bytes.length);u32(at+22,f.bytes.length);u16(at+26,f.filename.length);output.set(f.filename,at+30);output.set(f.bytes,at+30+f.filename.length);at+=30+f.filename.length+f.bytes.length;}
 const directory=at;
 files.forEach((f,i)=>{u32(at,0x02014b50);u16(at+4,20);u16(at+6,20);u16(at+8,0x800);u16(at+14,33);u32(at+16,f.crc);u32(at+20,f.bytes.length);u32(at+24,f.bytes.length);u16(at+28,f.filename.length);u32(at+42,offsets[i]);output.set(f.filename,at+46);at+=46+f.filename.length;});
 u32(at,0x06054b50);u16(at+8,files.length);u16(at+10,files.length);u32(at+12,at-directory);u32(at+16,directory);return output;
}
function packChecklist(report,tasks,includeNotes){
 const selected=tasks.map(t=>({id:t.id,status:includeNotes?t.status:'Not checked',owner:includeNotes?t.owner:'',notes:includeNotes?t.notes:''}));
 const exact=/^[a-f0-9]{64}$/.test(report.archive_sha256||'');
 const result={format:'reversium-handover',version:exact?2:1,archive_name:report.archive_name||'',scope:'Reviewer annotations, not automated runtime verification.',tasks:selected};
 if(exact)result.archive_sha256=report.archive_sha256;validateChecklist(result,report);return result;
}
function packQuestions(report,checklist){
 const questions=[...(report.limitations||[]),...(report.warnings||[]),...(report.feature_map?.features||[]).flatMap(f=>f.unknowns||[])];
 const unique=[...new Set(questions.filter(x=>typeof x==='string'))];
 return 'Reversium - remaining questions and checks\nStatic clues and reviewer annotations are separate from tested behavior.\n\n'+(report.handover?.tasks||[]).map(t=>t.title+'\n'+t.check+'\nFinding IDs: '+(t.evidence_indices||[]).join(', ')).join('\n\n')+'\n\nCoverage, warnings and map unknowns ('+unique.length+')\n'+unique.map(x=>'- '+x).join('\n')+'\n\nChecklist annotations included: '+checklist.tasks.some(t=>t.owner||t.notes||t.status!=='Not checked')+'\n';
}
function packText(value){return String(value??'').replace(/[\x00-\x1f\x7f-\x9f\u202a-\u202e\u2066-\u2069]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));}
function packLocation(e){return e?.file?packText(e.file)+(Number.isInteger(e.line)?':'+e.line:Number.isInteger(e.offset)?' @ byte '+e.offset:' (file-level reference)'):'Location unavailable';}
function packDeveloperBrief(report,checklist,includeNotes){
 const findings=report.findings||[],lines=['DEVELOPER FIRST HOUR','Static inspection, not a verified installation guide. No input code was executed.',
 'Package: '+packText(report.archive_name||'Unnamed'),'Original ZIP SHA-256: '+(report.archive_sha256||'Unavailable; confirm delivery independently.'),'',
 '1. CONFIRM THE DELIVERY AND REQUEST WHAT IS MISSING',
 'This pack contains analysis, not the source code. Request the original source ZIP separately through your agreed channel. Compare its SHA-256 with the value above before using these findings. A matching hash identifies bytes, not safety or authorship.',
 'Ask the sender for: the agreed user workflow and expected result; supported runtime versions; reviewed install/build/start/test instructions; migrations and disposable seed data; local database/login/storage setup and permissions; a known-good test result and a maintenance contact. Obtain any authorized configuration values through a separate secure channel. Do not put credentials in this pack.',
 '', '2. OPEN THE RECEIVED REPORT',
 'Open report.html in a browser; it works without the original ZIP or a Reversium installation. Handover contains setup clues and five review tasks. Architecture contains the workflow map; Evidence contains finding IDs and locations. Help is embedded. PDF download availability depends on your browser. Paths below are relative to the original ZIP, not files supplied in this pack.',
 'Restore handover-checklist.json in Handover > Restore saved checklist. Read the fingerprint/annotation preview, then press Replace checklist with reviewed saved notes. You can do this inside this saved report; re-analysis is unnecessary. All five annotations are replaced. Save the checklist or opt into annotations in a new pack before closing; changes are not autosaved.',
 '', '3. REVIEW THESE STATIC CLUES BEFORE SETUP'];
 function section(title,items,format,limit=40){lines.push('',title+' ('+items.length+')');if(!items.length)lines.push('Not identified by this analysis. Ask the sender; absence is not proof it is unnecessary.');for(const item of items.slice(0,limit))lines.push('- '+format(item));if(items.length>limit)lines.push((items.length-limit)+' further entries omitted here; inspect report.json and Coverage.');}
 function refs(indices){const valid=(indices||[]).filter(i=>Number.isInteger(i)&&findings[i]);return valid.length?valid.slice(0,3).map(i=>'['+i+'] '+packLocation(findings[i].evidence)).join('; ')+(valid.length>3?' ('+(valid.length-3)+' further references in report.json)':''):'No finding location supplied';}
 function unique(items){const seen=new Set();return items.filter(x=>{if(seen.has(x.name))return false;seen.add(x.name);return true;});}
 section('Stack candidates (one example location per name)',unique(report.platform?.stack_candidates||[]),x=>packText(x.name)+' - '+packText(x.confidence||'candidate')+'; '+packLocation(x.evidence));
 section('Referenced services (requirements remain unconfirmed)',unique(report.platform?.supporting_services||[]),x=>packText(x.name)+' - '+packText(x.role||x.status||'Reference only')+'; '+packLocation(x.evidence));
 const clues=report.handover?.clues||[];
 for(const [kind,title] of [['runtime_constraint_candidate','Declared runtime constraints'],['project_script_name','Declared script names (commands deliberately not retained)'],['environment','Configuration names (values deliberately not retained)']])section(title,clues.filter(c=>c.kind===kind),c=>packText(c.name)+'; '+refs(c.evidence_indices),80);
 if(report.handover?.omitted_clues)lines.push('Analyzer omitted '+report.handover.omitted_clues+' additional setup clues; coverage is incomplete.');
 section('Possible UI/server starting files (filename candidates, not verified entry points)',(report.files||[]).filter(f=>/(^|\/)(?:server|main|app|index|vite\.config|next\.config)\.[cm]?[jt]sx?$/i.test(f.path)),f=>packText(f.path)+' - '+packText(f.analysis||'Inventory only'),12);
 const interesting=(report.files||[]).filter(f=>/(^|\/)(?:readme[^/]*|package\.json|[^/]*lock[^/]*|pyproject\.toml|requirements[^/]*|pom\.xml|[^/]*\.csproj|dockerfile[^/]*|compose[^/]*|\.env\.(?:example|sample|template))$|\.(?:sql|prisma)$/i.test(f.path));
 section('Files to inspect in the original code package (filename candidates, not verified entry points)',interesting,f=>packText(f.path)+' - '+packText(f.analysis||'Inventory only'));
 section('Recorded entry-point clues',findings.map((f,i)=>({...f,index:i})).filter(f=>f.kind==='entry_point'),f=>packText(f.value)+'; ['+f.index+'] '+packLocation(f.evidence));
 lines.push('', '4. VERIFY ONE WORKFLOW IN A DISPOSABLE ENVIRONMENT',
 'Review the source and scripts before installation. Confirm service configuration, migrations and permissions with the sender. Choose one workflow from Architecture and follow its links to Evidence. Only after a reviewed local setup, record the expected result, actual result, date and blockers. This pack does not install or run the software. An attached runtime record is unsigned reviewer evidence and may contain untested outcomes.',
 '', '5. RETURN A CLEAR HANDOVER DECISION',
 'Update all five Handover tasks with an owner, status and a verification reference. Read remaining-questions.txt and Coverage before accepting the delivery. Send back the saved checklist and blockers. Keep the original source ZIP separate; report.json can be used for a future delivery comparison.',
 '', 'REVIEWER ANNOTATIONS');
 if(includeNotes)for(const t of checklist.tasks)lines.push(packText(t.id)+' / '+packText(t.status)+' / Owner: '+packText(t.owner||'Unassigned')+'\nNotes: '+packText(t.notes||'None supplied'));
 else lines.push('Excluded by the sender. The included checklist is a blank template; do not infer that tasks passed.');
 return lines.join('\n')+'\n';
}
function packEntries({report,html,svg,tasks,includeNotes=false,runtime=null,version,exportedAt,view}){
 const checklist=packChecklist(report,tasks,includeNotes);
 const entries=[{name:'DEVELOPER-FIRST-HOUR.txt',text:packDeveloperBrief(report,checklist,includeNotes)},{name:'report.html',text:html},{name:'report.json',text:JSON.stringify(report,null,2)},{name:'feature-map.svg',text:svg},{name:'feature-map.json',text:JSON.stringify(report.feature_map||{nodes:[],edges:[],features:[]},null,2)},{name:'handover-checklist.json',text:JSON.stringify(checklist,null,2)},{name:'remaining-questions.txt',text:packQuestions(report,checklist)}];
 if(runtime)entries.push({name:'runtime-test-record.json',text:JSON.stringify(runtime,null,2)});
 entries.unshift({name:'START-HERE.txt',text:'Reversium handover pack / Build '+version+'\nPackage: '+(report.archive_name||'Unnamed')+'\nOriginal ZIP SHA-256: '+(report.archive_sha256||'Unavailable - confirm delivery identity independently')+'\nExported: '+exportedAt+'\n\nReceiving developer: read DEVELOPER-FIRST-HOUR.txt, then open report.html in a browser. The report works offline without installing Reversium. In Handover, choose Restore saved checklist, select handover-checklist.json, review its exact-ZIP fingerprint preview, then press Replace checklist with reviewed saved notes. This works in the saved report without re-analyzing the source ZIP. Notes are not restored automatically and are not autosaved. Use report.json for a future comparison. Read remaining-questions.txt before accepting the handover. Request the original source ZIP and reviewed setup instructions separately: this pack alone cannot run the project.\n\nChecklist annotations included: '+includeNotes+'\nAttached runtime record included: '+Boolean(runtime)+' (unsigned reviewer evidence, not certification).\nMap SVG view: '+view+'\nThe SVG is a bounded current view; feature-map.json contains the full bounded generated graph.\n\nExcluded: original ZIP/source files, AI requests/conversations, pending imports and comparison previews. Code-derived details can still be private. Review every file before sharing. No file is uploaded.\n\nManifest CRC32 values detect accidental corruption, not malicious tampering or authorship. This pack is not an application backup or proof that the software works.\n'});
 const encoder=new TextEncoder();entries.push({name:'PACK-MANIFEST.json',text:JSON.stringify({format:'reversium-handover-pack',version:1,tool_version:version,exported_at:exportedAt,archive_sha256:report.archive_sha256||null,checklist_annotations:includeNotes,runtime_record:Boolean(runtime),map_view:view,integrity:'ZIP/manifest CRC32 is not authentication. The manifest excludes itself.',files:entries.map(e=>{const b=encoder.encode(e.text);return {name:e.name,bytes:b.length,crc32:packCRC32(b).toString(16).padStart(8,'0')};})},null,2)});
 return entries;
}
"""

SCRIPT=FUNCTIONS+r"""
document.querySelector('#pack-export').onclick=()=>{
 const status=document.querySelector('#pack-status'),button=document.querySelector('#pack-export');button.disabled=true;
 try{
 const includeNotes=document.querySelector('#pack-notes').checked,includeRuntime=document.querySelector('#pack-runtime').checked;
 const tasks=[...document.querySelectorAll('.handover-task')].map(el=>({id:el.dataset.task,status:el.querySelector('.task-status').value,owner:el.querySelector('.task-owner').value,notes:el.querySelector('.task-notes').value}));
 const saved=JSON.parse(document.querySelector('#runtime-record-data').textContent);const runtime=includeRuntime&&saved?validateRuntimeRecord(saved,reportData):null;
 const copy=document.querySelector('#feature-map-svg').cloneNode(true);for(const item of copy.querySelectorAll('.map-dimmed'))item.classList.remove('map-dimmed');
 const view='Selected feature: '+(document.querySelector('#map-filter').value||'All features')+'. '+document.querySelector('#map-omissions').textContent;
 const version=document.querySelector('#pack-panel').dataset.version;
 const entries=packEntries({report:reportData,html:readableReportHTML(Boolean(runtime)),svg:copy.outerHTML,tasks,includeNotes,runtime,version,exportedAt:new Date().toISOString(),view});
 const bytes=packZip(entries);if(parent!==window&&location.href==='about:srcdoc')parent.postMessage({type:'reversium-pack-download',bytes:bytes.buffer},'*',[bytes.buffer]);else{const url=URL.createObjectURL(new Blob([bytes],{type:'application/zip'})),a=document.createElement('a');a.href=url;a.download='reversium-handover-pack.zip';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);}
 status.textContent='Handover pack generated locally: '+entries.length+' files. Checklist annotations '+(includeNotes?'included':'excluded')+'; attached runtime record '+(runtime?'included':'excluded')+'. Review the files before sharing.';
 }catch(error){status.textContent='Pack not generated: '+error.message;}finally{button.disabled=false;}
};
"""
