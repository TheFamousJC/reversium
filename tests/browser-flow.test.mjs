import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';
import assert from 'node:assert/strict';
const app=readFileSync(new URL('../web/app.js',import.meta.url),'utf8');
const submit=app.slice(app.indexOf("$('#upload-form').onsubmit="),app.indexOf("window.addEventListener('pagehide'"));
const stop=app.slice(app.indexOf('function stop()'),app.indexOf('function clear()'));
function setup(){
 const elements=new Map(),workers=[],timers=[];
 const get=id=>{if(!elements.has(id))elements.set(id,{hidden:false,textContent:'',srcdoc:'',scrollIntoView(){}});return elements.get(id)};
 const file={size:20,name:'sample.zip',arrayBuffer:async()=>new ArrayBuffer(20)};get('#zip-input').files=[file];
 class Worker{constructor(){this.messages=[];workers.push(this)}terminate(){this.terminated=true}postMessage(message){this.messages.push(message)}}
 const context=vm.createContext({$,Worker,setTimeout:fn=>(timers.push(fn),timers.length),clearTimeout(){},document:{querySelector:get},upload:get('#upload-screen'),progress:get('#browser-progress'),results:get('#browser-results'),frame:get('#browser-report'),goal:'understand',worker:null,timer:null});
 function $(id){return get(id)}
 vm.runInContext(stop+submit,context);
 return {get,workers,timers,context,start:()=>get('#upload-form').onsubmit({preventDefault(){}}),cancel:()=>vm.runInContext('stop()',context)};
}
test('a canceled worker cannot overwrite a newer report or terminate its worker',async()=>{
 const s=setup();await s.start();const first=s.workers[0];s.cancel();await s.start();const second=s.workers[1];
 first.onmessage({data:{html:'old report'}});first.onerror();s.timers[0]();
 assert.notEqual(second.terminated,true);assert.equal(s.get('#browser-report').srcdoc,'');
 second.onmessage({data:{html:'current report'}});assert.equal(s.get('#browser-report').srcdoc,'current report');assert.equal(second.terminated,true);
});
test('a delayed file read after cancellation cannot feed the next worker',async()=>{
 const s=setup();let resolve;
 s.get('#zip-input').files=[{size:20,name:'old.zip',arrayBuffer:()=>new Promise(r=>{resolve=r})}];const pending=s.start();s.cancel();
 s.get('#zip-input').files=[{size:20,name:'new.zip',arrayBuffer:async()=>new ArrayBuffer(20)}];await s.start();resolve(new ArrayBuffer(20));await pending;
 assert.equal(s.workers[0].messages.length,0);assert.equal(s.workers[1].messages.length,1);assert.equal(s.workers[1].messages[0].name,'new.zip');
});
test('empty or oversized input cannot start a worker',async()=>{
 for(const size of [0,33554433]){const s=setup();s.get('#zip-input').files=[{size}];await s.start();assert.equal(s.workers.length,0)}
});
