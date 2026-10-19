import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';
import assert from 'node:assert/strict';

const report=readFileSync(new URL('../reversium/report.py',import.meta.url),'utf8');
const source=report.slice(report.indexOf('function revealFinding(hash)'),report.indexOf("window.addEventListener('hashchange',()=>revealFinding"));
const inspectSource=report.slice(report.indexOf('function inspectMap(element)'),report.indexOf('const mapSvg='));

function setup(){
 const listeners=new Map(),calls=[];
 const row={focus:()=>calls.push('focus'),scrollIntoView:()=>calls.push('scroll')};
 const filter={value:'old search',dispatchEvent:()=>calls.push('filter')};
 const document={addEventListener:(event,fn)=>listeners.set(event,fn),querySelector:()=> 'evidence tab',getElementById:id=>id==='finding-7'?row:null};
 vm.runInNewContext(source,{document,filter,Event,activateTab:tab=>calls.push(tab)});
 return {listeners,calls,filter};
}

test('evidence link created after initialization reveals its row without navigating the frame',()=>{
 const state=setup(); // No evidence link exists when the script registers.
 let prevented=false;
 const dynamicLink={getAttribute:name=>name==='href'?'#finding-7':null};
 state.listeners.get('click')({target:{closest:selector=>{assert.equal(selector,'a.evidence-link');return dynamicLink}},preventDefault:()=>{prevented=true}});
 assert.equal(prevented,true);
 assert.deepEqual(state.calls,['evidence tab','filter','focus','scroll']);
 assert.equal(state.filter.value,'');
});

test('unrelated controls, external links and malformed targets are not intercepted',()=>{
 for(const href of [null,'https://example.com/','#finding-bad']){
  const state=setup();let prevented=false;
  state.listeners.get('click')({target:{closest:()=>href===null?null:{getAttribute:()=>href}},preventDefault:()=>{prevented=true}});
  assert.equal(prevented,false);assert.deepEqual(state.calls,[]);
 }
});

test('a missing internal finding does not navigate outside the report',()=>{
 const state=setup();let prevented=false;
 state.listeners.get('click')({target:{closest:()=>({getAttribute:()=> '#finding-999'})},preventDefault:()=>{prevented=true}});
 assert.equal(prevented,true);assert.deepEqual(state.calls,[]);
});

test('actual map-detail renderer creates links handled by the shared navigation listener',()=>{
 const listeners=new Map(),children=[],calls=[];
 const box={replaceChildren:()=>{children.length=0},append:(...nodes)=>children.push(...nodes)};
 const row={focus:()=>calls.push('focus'),scrollIntoView:()=>calls.push('scroll')};
 const document={addEventListener:(event,fn)=>listeners.set(event,fn),querySelector:selector=>selector==='#map-details'?box:'evidence tab',getElementById:id=>id==='finding-7'?row:null,createTextNode:text=>text,createElement:tag=>({tag,getAttribute(name){return this[name]}})};
 const findings=Array.from({length:8},()=>({evidence:{file:'example.ts',line:4},kind:'source_reference'}));
 const element={getAttribute:name=>name==='data-map-kind'?'node':'save'};
 vm.runInNewContext(source+inspectSource+';inspectMap(element)',{document,element,filter:{value:'',dispatchEvent(){}},Event,activateTab:()=>calls.push('evidence'),graph:{nodes:[{id:'save',label:'Save',kind:'helper',features:[],evidence_indices:[7]}],edges:[],features:[]},reportData:{findings}});
 const link=children.find(n=>n?.tag==='a');assert.equal(link.className,'evidence-link');
 let prevented=false;
 listeners.get('click')({target:{closest:()=>link.className==='evidence-link'?link:null},preventDefault:()=>{prevented=true}});
 assert.equal(prevented,true);assert.deepEqual(calls,['evidence','focus','scroll']);
});
