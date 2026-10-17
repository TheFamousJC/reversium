const $=s=>document.querySelector(s);$('#enter-app').onclick=()=>{document.querySelector('#splash').hidden=true;document.querySelector('#app-content').hidden=false;document.querySelector('#start-screen h1').setAttribute('tabindex','-1');document.querySelector('#start-screen h1').focus()};
const start=$('#start-screen'),upload=$('#upload-screen'),progress=$('#browser-progress'),results=$('#browser-results'),frame=$('#browser-report');
let goal='understand',worker=null,timer=null;
const names={understand:'Understand the software',handover:'Prepare a developer handover',change:'Plan maintenance or modernization'};
function step(two){start.hidden=two;upload.hidden=!two;$('#start-step').textContent=two?'Step 2 of 4 · Choose ZIP':'Step 1 of 4 · Start';$('#chosen-goal').textContent='Your goal: '+names[goal]}
function stop(){if(worker)worker.terminate();worker=null;clearTimeout(timer)}
function clear(){document.querySelector('#app-content').hidden=false;stop();frame.srcdoc='';$('#zip-input').value='';$('#analyze-zip').disabled=true;$('#status').textContent='Choose a ZIP to begin. Your file stays on this device.';progress.hidden=true;results.hidden=true;$('#start-step').hidden=false;step(false)}
$('#goal-form').onsubmit=e=>{e.preventDefault();goal=document.querySelector('input[name=goal]:checked').value;step(true)};
$('#start-back').onclick=()=>step(false);
for(const button of document.querySelectorAll('[data-help-panel]'))button.onclick=()=>{const panel=document.getElementById(button.dataset.helpPanel);panel.hidden=!panel.hidden;button.setAttribute('aria-expanded',String(!panel.hidden))};
$('#zip-input').onchange=()=>{const f=$('#zip-input').files[0],ok=!!f&&f.size>0&&f.size<=33554432;$('#analyze-zip').disabled=!ok;$('#status').textContent=!f?'Choose a ZIP to begin.':!ok?'Choose a non-empty ZIP smaller than 32 MiB.':'Selected: '+f.name+' ('+(f.size/1048576).toFixed(1)+' MiB). This file will be read on your device, not uploaded.'};
$('#browser-cancel').onclick=clear;$('#browser-clear').onclick=clear;
window.addEventListener('message',event=>{
 if(event.source!==frame.contentWindow)return;
 if(event.data?.type==='reversium-clear')clear();
 const d=event.data,formats={'reversium-ai-request.txt':'text/plain','reversium-report.json':'application/json','reversium-report.html':'text/html','reversium-feature-map.svg':'image/svg+xml'};
 if(d?.type==='reversium-download'&&formats[d.name]===d.mime&&typeof d.text==='string'&&d.text.length<100000000){const url=URL.createObjectURL(new Blob([d.text],{type:d.mime}));const a=document.createElement('a');a.href=url;a.download=d.name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
});
$('#upload-form').onsubmit=async event=>{
 event.preventDefault();const file=$('#zip-input').files[0];if(!file||file.size>33554432||file.size===0||worker)return;
 upload.hidden=true;progress.hidden=false;$('#browser-message').textContent='Preparing the local analysis…';
 worker=new Worker('./worker.mjs',{type:'module'});
 timer=setTimeout(()=>{stop();$('#browser-message').textContent='Analysis stopped after five minutes. Try a smaller archive or a more capable device. Nothing was uploaded.'},300000);
 worker.onerror=()=>{stop();$('#browser-message').textContent='Browser runtime could not start. Check your connection and browser support, then cancel and retry. Nothing was uploaded.'};
 worker.onmessage=({data})=>{if(data.stage)$('#browser-message').textContent=data.stage;if(data.error){stop();$('#browser-message').textContent=data.error}if(data.html){stop();document.querySelector('#app-content').hidden=true;progress.hidden=true;results.hidden=false;$('#start-step').hidden=true;frame.srcdoc=data.html;results.scrollIntoView({block:'start'})}};
 try{const bytes=await file.arrayBuffer();if(worker)worker.postMessage({bytes,name:file.name,goal},[bytes])}catch(error){stop();$('#browser-message').textContent='The selected file could not be read. Cancel and choose it again.'}
};
window.addEventListener('pagehide',stop);
