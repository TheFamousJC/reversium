import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import vm from 'node:vm';
import test from 'node:test';
import assert from 'node:assert/strict';
const source=readFileSync(new URL('../reversium/handover_pack.py',import.meta.url),'utf8').split('FUNCTIONS=r"""')[1].split('"""')[0];
const checks=readFileSync(new URL('../reversium/review_tools.py',import.meta.url),'utf8').split('FUNCTIONS = r"""')[1].split('"""')[0];
const api=vm.runInNewContext(checks+source+';({packZip,packEntries,packCRC32})',{TextEncoder,Uint8Array,Uint32Array,DataView});
const report={archive_name:'your-package.zip',archive_sha256:'a'.repeat(64),findings:[],files:[],limitations:['Permissions remain unverified.'],warnings:[],handover:{tasks:[{id:'run',title:'Run one feature',check:'Use disposable data.',evidence_indices:[]}]},feature_map:{nodes:[],edges:[],features:[]}};
const tasks=['workflow','runtime','configuration','services','run'].map(id=>({id,status:'Blocked',owner:'Private owner',notes:'PRIVATE_NOTE'}));
const args=()=>({report,html:'<html>Reviewed report</html>',svg:'<svg/>',tasks,version:'test',exportedAt:'2026-10-20T00:00:00Z',view:'All features; bounded view'});

test('default pack excludes annotations and runtime, and records explicit limits',()=>{
 const entries=api.packEntries(args()),names=Array.from(entries,e=>e.name);
 assert.equal(names.length,9);assert.ok(!names.includes('your-package.zip'));assert.ok(!names.includes('runtime-test-record.json'));
 assert.ok(!JSON.stringify(entries).includes('PRIVATE_NOTE'));assert.ok(!JSON.stringify(entries).includes('Private owner'));
 assert.match(entries.find(e=>e.name==='remaining-questions.txt').text,/Permissions remain unverified/);
 const checklist=JSON.parse(entries.find(e=>e.name==='handover-checklist.json').text);assert.equal(checklist.archive_sha256,report.archive_sha256);assert.ok(checklist.tasks.every(t=>t.status==='Not checked'&&t.notes===''));
 const manifest=JSON.parse(entries.find(e=>e.name==='PACK-MANIFEST.json').text);assert.equal(manifest.files.length,8);assert.equal(manifest.checklist_annotations,false);
});

test('annotations and runtime are included only through explicit builder options',()=>{
 const entries=api.packEntries({...args(),includeNotes:true,runtime:{scope:'reviewer evidence'}});
 assert.match(entries.find(e=>e.name==='handover-checklist.json').text,/PRIVATE_NOTE/);assert.ok(entries.some(e=>e.name==='runtime-test-record.json'));
});

test('generated ZIP and manifest pass an independent Python ZIP/CRC reader',()=>{
 const entries=api.packEntries(args());entries[0].text+='\nUnicode: résumé 😀';
 // Build a fresh manifest for the edited fixture so byte-count checks remain independent.
 const manifest=JSON.parse(entries.at(-1).text);manifest.files[0].bytes=new TextEncoder().encode(entries[0].text).length;manifest.files[0].crc32=api.packCRC32(new TextEncoder().encode(entries[0].text)).toString(16).padStart(8,'0');entries.at(-1).text=JSON.stringify(manifest);
 const zipped=api.packZip(entries);
 const python=process.env.REVERSIUM_TEST_PYTHON||(process.platform==='win32'?'python':'python3');
 const result=execFileSync(python,['-c',"import sys,io,zipfile,json,zlib; z=zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read())); assert z.testzip() is None; m=json.loads(z.read('PACK-MANIFEST.json')); assert len(z.namelist())==9; assert all(len(z.read(f['name']))==f['bytes'] and format(zlib.crc32(z.read(f['name'])),'08x')==f['crc32'] for f in m['files']); print('valid')"],{input:Buffer.from(zipped),encoding:'utf8'});
 assert.equal(result.trim(),'valid');
});

test('unsafe names, duplicate entries, invalid annotations and oversized packs fail closed',()=>{
 for(const entries of [[{name:'../escape',text:'x'}],[{name:'a',text:'x'},{name:'a',text:'x'}]])assert.throws(()=>api.packZip(entries));
 assert.throws(()=>api.packZip([{name:'a',text:'x'.repeat(100)}],100));
 assert.throws(()=>api.packEntries({...args(),includeNotes:true,tasks:tasks.map(t=>({...t,status:'invented'}))}));
});

test('receiver brief carries located setup evidence, names only and explicit missing prerequisites',()=>{
 const detailed={...report,platform:{stack_candidates:[{name:'React',confidence:'candidate',evidence:{file:'package.json',line:3}}],supporting_services:[{name:'Database',role:'Client reference only',evidence:{file:'db.ts',line:2}}]},files:[{path:'package.json',analysis:'manifest'},{path:'schema.sql',analysis:'sql_reference_scan'}],findings:[{kind:'project_script_name',value:'start',evidence:{file:'package.json',line:4}}],handover:{...report.handover,clues:[{kind:'project_script_name',name:'start',evidence_indices:[0]}]}};
 const entries=api.packEntries({...args(),report:detailed});
 const brief=entries.find(e=>e.name==='DEVELOPER-FIRST-HOUR.txt').text;
 assert.match(brief,/React - candidate; package.json:3/);assert.match(brief,/start; \[0\] package.json:4/);
 assert.match(brief,/Not identified by this analysis/);assert.match(brief,/schema.sql/);
 assert.match(brief,/Request the original source ZIP separately/);assert.match(brief,/re-analysis is unnecessary/);
 assert.match(brief,/not autosaved/);assert.match(brief,/not a verified installation guide/);assert.ok(!brief.includes('PRIVATE_NOTE'));
 const annotated=api.packEntries({...args(),includeNotes:true}).find(e=>e.name==='DEVELOPER-FIRST-HOUR.txt').text;
 assert.match(annotated,/PRIVATE_NOTE/);assert.match(annotated,/Blocked/);
});

test('receiver brief discloses bounds and escapes misleading filename line breaks',()=>{
 const files=Array.from({length:42},(_,i)=>({path:`file${i}.sql`}));files[0].path='bad\nCLAIM\u202e.sql';
 const brief=api.packEntries({...args(),report:{...report,files}}).find(e=>e.name==='DEVELOPER-FIRST-HOUR.txt').text;
 assert.match(brief,/2 further entries omitted/);assert.ok(!brief.includes('bad\nCLAIM'));
 assert.ok(brief.includes('bad\\u000aCLAIM\\u202e.sql'));
});

test('saved reports with removed AI panels skip account initialization without errors or requests',()=>{
 const document={querySelector:()=>null};
 for(const name of ['browser_ai','online_ai_ui']){
  const body=readFileSync(new URL(`../reversium/${name}.py`,import.meta.url),'utf8').split('SCRIPT = r"""')[1].split('"""')[0];
  assert.doesNotThrow(()=>vm.runInNewContext(body,{document}));
 }
});
