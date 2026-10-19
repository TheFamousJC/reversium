import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import test from 'node:test';
import assert from 'node:assert/strict';
const source=readFileSync(new URL('../reversium/cms_preview.py',import.meta.url),'utf8').split('FETCH = r"""')[1].split('"""')[0];
async function run({badHash=false,oversized=false}={}){
 const body=Buffer.from(Array.from({length:6000},(_,i)=>i%256));
 const packet={path:'/api/admin/media',method:'POST',headers_key:'a'.repeat(64),headers:{'content-type':'image/png'},body:body.toString('base64')};
 const encoded=Buffer.from(JSON.stringify(packet)).toString('base64');let calls=[],writes=[],reads=0,unlinks=0;
 const fs={statSync:()=>({size:oversized?4194305:encoded.length}),readFileSync:path=>{reads++;return path==='/tmp/cms-request.b64'?encoded:JSON.stringify(packet.headers)},writeFileSync(){},unlinkSync(){unlinks++}};
 const process={argv:['node','fetch','--file',badHash?'0'.repeat(64):crypto.createHash('sha256').update(encoded).digest('hex')],stdout:{write:(value,done)=>{writes.push(value);done()}},exit(){}};
 await vm.runInNewContext(source,{require:name=>({fs,crypto,zlib}[name]),process,Buffer,AbortSignal,console:{log:v=>writes.push(v),error(){}},fetch:async(url,options)=>{calls.push({url,options});let sent=false;return {status:201,headers:new Map([['content-type','application/json']]),body:{getReader:()=>({read:async()=>sent?{done:true}:(sent=true,{done:false,value:Buffer.from('{"ok":true}')} )})}}}});
 return {body,calls,writes,reads,unlinks};
}
test('chunked binary request verifies digest and preserves bytes at fixed guest target',async()=>{const r=await run();assert.equal(r.calls.length,1);assert.equal(r.calls[0].url,'https://127.0.0.1:18443/api/admin/media');assert.deepEqual(r.calls[0].options.body,r.body);assert.equal(r.calls[0].options.redirect,'manual');assert.equal(r.unlinks,1);assert.match(r.writes[0],/REVERSIUM_HTTP:/);});
test('tampered serial packet cannot invoke guest HTTP',async()=>{const r=await run({badHash:true});assert.equal(r.calls.length,0);assert.match(r.writes[0],/"status":502/);});
test('oversized packet file is rejected before reading its body',async()=>{const r=await run({oversized:true});assert.equal(r.calls.length,0);assert.equal(r.reads,0);});
