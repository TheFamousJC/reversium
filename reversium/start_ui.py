"""A short guided entry flow before analysis controls become available."""
from . import __version__
from .help_ui import ABOUT, FAQ_GENERAL
from .assistant_ui import FAQ_AI


def render_start(style, help_script):
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Start · Reversium</title><style>{style}</style><main>
<p class="brand">REVERSIUM {__version__} · LOCAL &amp; FREE</p>
<nav aria-label="Help"><button type="button" data-help-panel="start-about">About</button><button type="button" data-help-panel="start-faq">FAQ</button></nav>
<section id="start-about" hidden>{ABOUT}</section><section id="start-faq" hidden>{FAQ_GENERAL}{FAQ_AI}</section>
<p id="start-step" class="assessment">Step 1 of 4 · Start</p>
<section id="start-screen"><h1>Start with a clear question.</h1><p>Understand a software ZIP before you take it over, change it or plan its future. Reversium checks the files locally and shows evidence, connections and gaps.</p>
<form id="goal-form"><fieldset><legend>What would you like to achieve?</legend>
<label class="goal-choice"><input type="radio" name="goal" value="understand" checked> <b>Understand the software</b><br>Find its likely features, building blocks and supporting services.</label>
<label class="goal-choice"><input type="radio" name="goal" value="handover"> <b>Prepare a developer handover</b><br>Find the code and questions another developer needs to investigate.</label>
<label class="goal-choice"><input type="radio" name="goal" value="change"> <b>Plan maintenance or modernization</b><br>Explore feature connections and areas that need further checks.</label>
</fieldset><button id="start-continue">Continue to ZIP</button></form>
<details><summary>Just exploring? Try a clearly labelled sample</summary><p><a href="/example-js">View sample analysis</a> — a small fictional contact application, not your software.</p></details>
<p>No sign-in is required. Uploaded code is never run. AI is an optional later step.</p></section>
<section id="upload-screen" hidden><h1>Choose your software ZIP.</h1><p id="chosen-goal"></p><p>Choose the package you want to understand. You will review its findings next, then decide what to save or investigate. Nothing is sent to an AI provider during analysis.</p>
<form id="upload-form"><label for="zip-input">Software ZIP (maximum 64 MiB)</label><input id="zip-input" aria-label="Choose ZIP archive" type="file" accept=".zip" required><button id="analyze-zip">Analyze ZIP locally</button></form>
<p id="status" role="status">Choose a ZIP to begin. No report exists yet.</p><button type="button" id="start-back">Back to Start</button></section>
<footer><p>Open Source · 3Sci.com · 2026</p></footer></main><script>
(()=>{{let goal='understand';const names={{understand:'Understand the software',handover:'Prepare a developer handover',change:'Plan maintenance or modernization'}};
const start=document.querySelector('#start-screen'),upload=document.querySelector('#upload-screen');
function step(two){{start.hidden=two;upload.hidden=!two;document.querySelector('#start-step').textContent=two?'Step 2 of 4 · Choose ZIP':'Step 1 of 4 · Start';document.querySelector(two?'#upload-screen h1':'#start-screen h1').setAttribute('tabindex','-1');document.querySelector(two?'#upload-screen h1':'#start-screen h1').focus()}}
document.querySelector('#goal-form').onsubmit=e=>{{e.preventDefault();goal=document.querySelector('input[name=goal]:checked').value;document.querySelector('#chosen-goal').textContent='Your goal: '+names[goal];step(true)}};
document.querySelector('#start-back').onclick=()=>step(false);
for(const button of document.querySelectorAll('[data-help-panel]'))button.onclick=()=>{{const panel=document.getElementById(button.dataset.helpPanel);panel.hidden=!panel.hidden;button.setAttribute('aria-expanded',String(!panel.hidden))}};
document.querySelector('#upload-form').onsubmit=async e=>{{e.preventDefault();const file=document.querySelector('#zip-input').files[0],status=document.querySelector('#status'),button=document.querySelector('#analyze-zip');if(!file)return;if(file.size>67108864){{status.textContent='ZIP exceeds 64 MiB. Choose a smaller archive.';return}}button.disabled=true;document.querySelector('#start-back').disabled=true;status.textContent='Analyzing locally. Your findings will appear when ready…';try{{const response=await fetch('/analyze',{{method:'POST',headers:{{'Content-Type':'application/zip','X-Reversium-Goal':goal}},body:file}});if(!response.ok)throw Error(await response.text());const page=await response.text();document.open();document.write(page);document.close()}}catch(error){{status.textContent=error.message;button.disabled=false;document.querySelector('#start-back').disabled=false}}}};
}})();{help_script}</script></html>'''
