import html
import json


def render(report):
    esc = lambda value: html.escape(str(value), quote=True)
    findings = report['findings']
    # Diagram edges represent observed mentions, not proven runtime calls.
    pairs = list(dict.fromkeys((f['evidence']['file'], f.get('target', f['value']) + ' [' + f.get('resolution', 'unresolved') + ']') for f in findings if f['kind'] in {'import', 'dependency'}))[:100]
    height = max(90, len(pairs) * 46 + 30)
    diagram = [f'<svg viewBox="0 0 1000 {height}" role="img" aria-label="File to import and dependency mentions">']
    for index, (origin, target) in enumerate(pairs):
        y = 35 + index * 46
        diagram.append(f'<path d="M450 {y} H550" stroke="#66d9c2"/><text x="10" y="{y}" fill="#e8edf5">{esc(origin[:55])}</text><text x="560" y="{y}" fill="#66d9c2">{esc(target[:55])}</text>')
    diagram.append('</svg>')
    rows = ''.join(f'<tr><td>{esc(f["kind"])}</td><td>{esc(f["value"])}</td><td>{esc(f["evidence"]["file"])}:{f["evidence"]["line"]}</td><td>{esc(f["confidence"])}</td><td>{esc(f.get("resolution", "—"))}{" → " + esc(f["target"]) if "target" in f else ""}</td></tr>' for f in findings)
    files = ''.join(f'<tr><td>{esc(f["path"])}</td><td>{esc(f["language"] or f["category"])}</td><td>{f["bytes"]}</td><td>{esc(f.get("analysis", "unknown"))}</td></tr>' for f in report['files'])
    notes = ''.join(f'<li>{esc(x)}</li>' for x in report['warnings'] + report['limitations'])
    payload = json.dumps(report).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    comparison = ''
    if 'comparison' in report:
        comparison = '<h2>Changes from baseline</h2><p>Line movement alone is ignored. Hash comparison covers readable files only.</p><pre>' + esc(json.dumps(report['comparison'], indent=2)) + '</pre>'
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Reversium report</title><style>{STYLE}</style><main><p class="brand">REVERSIUM / LOCAL ANALYSIS</p><nav><a href="/">Analyze another ZIP</a><button id="json-export">Download JSON</button><button id="html-export">Download HTML</button></nav><h1>Understand what’s inside.</h1><p>{esc(report['scope'])}</p><div class="cards">{''.join(f'<article><strong>{esc(v)}</strong><span>{esc(k.replace("_", " "))}</span></article>' for k,v in report['summary'].items() if k != 'languages')}</div>{comparison}<h2>Architecture: import and dependency mentions</h2><p>File → local file candidate or referenced package. Labels distinguish internal, external, unresolved and ambiguous references. First 100 unique edges; full evidence is below.</p><div class="scroll">{''.join(diagram) if pairs else '<p>No supported dependency references found.</p>'}</div><h2>Evidence</h2><label for="evidence-filter">Filter evidence</label><input id="evidence-filter" type="search" placeholder="File, symbol, kind or resolution"><p id="filter-count" role="status">{len(findings)} findings</p><div class="scroll"><table id="evidence-table"><thead><tr><th>Finding</th><th>Value</th><th>Location</th><th>Confidence</th><th>Resolution</th></tr></thead><tbody>{rows}</tbody></table></div><h2>Inventory</h2><div class="scroll"><table><tr><th>File</th><th>Type</th><th>Bytes</th><th>Analysis coverage</th></tr>{files}</table></div><h2>Coverage and limitations</h2><ul>{notes}</ul><p>Generated locally by Reversium 0.2.0. No paid services or remote assets.</p></main><script type="application/json" id="report-data">{payload}</script><script>{SCRIPT}</script></html>'''


STYLE = 'body{margin:0;background:#101823;color:#e8edf5;font:16px system-ui}main{max-width:1180px;margin:60px auto;padding:0 28px}.brand{color:#66d9c2;letter-spacing:3px;font-size:12px}h1{font-size:48px;letter-spacing:-2px}h2{margin-top:45px}p,li{color:#afbdce;line-height:1.7}.cards{display:flex;gap:14px;flex-wrap:wrap}article{padding:24px;background:#1c2838;border-radius:12px;min-width:130px}strong{display:block;font-size:30px}span{color:#afbdce}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:12px;border-bottom:1px solid #304056;overflow-wrap:anywhere}.scroll{overflow:auto}svg{width:100%;min-width:650px;background:#162130;border-radius:12px}button{background:#66d9c2;color:#101823;border:0;border-radius:8px;padding:14px 24px;font-weight:700;cursor:pointer}input{padding:20px}a{color:#66d9c2}'
STYLE += 'nav{display:flex;align-items:center;gap:12px;flex-wrap:wrap}input[type=search]{display:block;box-sizing:border-box;width:100%;max-width:600px;background:#1c2838;color:#e8edf5;border:1px solid #657890;border-radius:8px;margin-top:10px}button:disabled{opacity:.5;cursor:wait}pre{white-space:pre-wrap;overflow-wrap:anywhere}form{display:flex;flex-wrap:wrap;align-items:center;gap:12px}input[type=file]{max-width:100%;box-sizing:border-box}svg text{font:13px monospace}@media(max-width:600px){main{margin:28px auto;padding:0 16px}h1{font-size:34px}.cards article{flex:1;min-width:100px;padding:16px}nav button{padding:12px}td,th{padding:8px}}'
STYLE += 'table{min-width:760px}svg{min-width:1000px}'

SCRIPT = '''const filter=document.querySelector('#evidence-filter');
filter.addEventListener('input',()=>{let count=0;for(const row of document.querySelectorAll('#evidence-table tbody tr')){row.hidden=!row.textContent.toLowerCase().includes(filter.value.toLowerCase());if(!row.hidden)count++}document.querySelector('#filter-count').textContent=count+' findings'});
function download(text,type,name){const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
document.querySelector('#json-export').onclick=()=>download(document.querySelector('#report-data').textContent,'application/json','reversium-report.json');
document.querySelector('#html-export').onclick=()=>{const copy=document.documentElement.cloneNode(true);copy.querySelector('#evidence-filter').value='';for(const row of copy.querySelectorAll('tr'))row.removeAttribute('hidden');copy.querySelector('#filter-count').textContent=copy.querySelectorAll('#evidence-table tbody tr').length+' findings';download('<!doctype html>'+copy.outerHTML,'text/html','reversium-report.html')};'''
