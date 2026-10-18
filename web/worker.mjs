import {loadPyodide} from './vendor/pyodide/pyodide.mjs';
let started = false;
self.onmessage = async ({data}) => {
  if (started) return;
  started = true;
  let py;
  try {
    self.postMessage({stage:'Loading the Python runtime. The first visit may take a little longer…'});
    py = await loadPyodide({indexURL:new URL('./vendor/pyodide/',import.meta.url).href});
    self.postMessage({stage:'Loading the analyzer…'});
    const [config, response] = await Promise.all([fetch('./engine.json').then(r=>{if(!r.ok)throw Error();return r.json()}),fetch('./engine.zip')]);
    if (!response.ok) throw Error('Analyzer download failed.');
    const engine = await response.arrayBuffer();
    const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256',engine))].map(x=>x.toString(16).padStart(2,'0')).join('');
    if (hash !== config.sha256) throw Error('Analyzer download integrity check failed. Reload and try again.');
    py.unpackArchive(engine,'zip');
    // Drop network APIs after runtime/application download, before reading source.
    self.fetch=()=>Promise.reject(Error('Network disabled during analysis.'));
    self.XMLHttpRequest=undefined;
    self.WebSocket=undefined;
    py.FS.writeFile('/input.zip',new Uint8Array(data.bytes));
    py.globals.set('browser_archive_name',data.name);
    py.globals.set('browser_goal',data.goal);
    self.postMessage({stage:'Inspecting files and mapping supported source connections. Nothing is uploaded…'});
    const html=await py.runPythonAsync(`
import json
from reversium.analyze import inspect_zip
from reversium.browser_report import render_browser
try:
    browser_result = inspect_zip('/input.zip')
    browser_result['archive_name'] = str(browser_archive_name)[:200]
    browser_result['user_goal'] = browser_goal if browser_goal in ('understand','handover','change') else 'understand'
    browser_html = render_browser(browser_result)
finally:
    import os
    os.remove('/input.zip')
browser_html
`);
    self.postMessage({html});
  } catch(error) {
    // Avoid including filenames, source text or Python tracebacks in UI telemetry.
    self.postMessage({error:'ZIP blocked or unreadable. It may contain unsafe paths, invalid structure, unsupported encryption/compression, or exceed archive limits. No ZIP code was executed. If runtime loading failed, check your connection or try a current desktop browser. No file was uploaded.'});
  }
};
