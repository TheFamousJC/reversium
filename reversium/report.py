import html
import json
from .explain import explain_software


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
    def location(evidence):
        suffix = ':' + str(evidence['line']) if 'line' in evidence else ' @ byte 0x' + format(evidence.get('offset', 0), 'x')
        return esc(evidence['file'] + suffix)
    rows = ''.join(f'<tr id="finding-{index}" tabindex="-1"><td>{esc(f["kind"])}</td><td>{esc(f["value"])}</td><td>{location(f["evidence"])}</td><td>{esc(f["confidence"])}</td><td>{esc(f.get("resolution", "—"))}{" → " + esc(f["target"]) if "target" in f else ""}</td></tr>' for index, f in enumerate(findings))
    files = ''.join(f'<tr><td>{esc(f["path"])}</td><td>{esc(f.get("binary", {}).get("format", f["language"] or f["category"]))}</td><td>{f["bytes"]}</td><td>{esc(f.get("analysis", "unknown"))}</td></tr>' for f in report['files'])
    notes = ''.join(f'<li>{esc(x)}</li>' for x in report['warnings'] + report['limitations'])
    payload = json.dumps(report).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    comparison = ''
    platform_section = ''
    readiness = ''
    binary_section = ''
    if 'comparison' in report:
        comparison = '<h2>Changes from baseline</h2><p>Line movement alone is ignored. Hash comparison covers content-inspected files only.</p><pre>' + esc(json.dumps(report['comparison'], indent=2)) + '</pre>'
    profile = report.get('platform', {})
    if profile:
        stack = ''.join('<li>' + esc(item['name']) + ' — candidate; ' + location(item['evidence']) + '</li>' for item in profile['stack_candidates'] + profile.get('runtime_candidates', []))
        services = ''.join('<tr><td>' + esc(item['name']) + '</td><td>' + esc(item['role']) + '</td><td>' + esc(item['status']) + '</td><td>' + location(item['evidence']) + '</td></tr>' for item in profile['supporting_services'])
        binary_rows = ''.join('<tr><td>' + esc(item['file']) + '</td><td>' + esc(item['format']) + '</td><td>' + esc(item['target']) + '</td><td>' + esc(item['architecture']) + '</td><td>' + esc(item['status']) + '</td></tr>' for item in profile['binary_targets'])
        platform_section = ('<h2>Platform profile</h2><p>' + esc(profile['purpose']) + '</p><ul>' + (stack or '<li>No supported framework evidence found.</li>') + '</ul>'
                      + '<h2>Supporting services</h2><p>References can be optional or development-only. A stable deployment is not verified.</p>'
                      + ('<div class="scroll"><table><tr><th>Service</th><th>Role</th><th>Assessment</th><th>Evidence</th></tr>' + services + '</table></div>' if services else '<p>No supported service references found; requirements remain unknown.</p>'))
        readiness = '<h2>Setup and readiness</h2><p>' + esc(profile['readiness']) + '</p><details><summary>What still needs confirmation</summary><ul>' + ''.join('<li>' + esc(x) + '</li>' for x in profile['unknowns'] + profile['next_steps']) + '</ul></details>'
        binary_section = ('<h2>Binary inspection</h2><p>Metadata and references only. Programs are never executed. Reader status describes supported inspection, not binary validity or readiness to run. Byte offsets appear in the evidence table.</p>'
                          + ('<div class="scroll"><table><tr><th>File</th><th>Format</th><th>Runtime / target</th><th>Architecture</th><th>Reader status</th></tr>' + binary_rows + '</table></div>' if binary_rows else '<p>No inspected binary candidates.</p>'))
    behavior = report.get('behavior') or explain_software(report)
    explanation_cards = []
    for explanation in behavior['explanations']:
        links = ' · '.join(f'<a class="evidence-link" href="#finding-{index}">{location(findings[index]["evidence"])}</a>' for index in explanation['evidence_indices'])
        explanation_cards.append(f'<article class="explanation"><h3>{esc(explanation["topic"])}</h3><p>{esc(explanation["explanation"])}</p><p class="assessment">{esc(explanation["assessment"])}</p><p><b>Still unknown:</b> {esc(explanation["unknown"])}</p><p><b>Evidence:</b> {links}</p></article>')
    behavior_content = ('<h2>What this software does</h2><p>' + esc(behavior['summary']) + '</p><p>' + esc(behavior['method']) + '</p>'
                        + (''.join(explanation_cards) or '<p>No behavior explanation is supported by the current findings. Missing findings do not mean the software has no features.</p>')
                        + (f'<p>{behavior["omitted_groups"]} additional explanation groups are omitted from this overview. All findings remain in Evidence.</p>' if behavior['omitted_groups'] else '')
                        + '<h2>What we still do not know</h2><ul>' + ''.join('<li>' + esc(x) + '</li>' for x in behavior['unknowns']) + '</ul>'
                        + '<h2>How to confirm the explanation</h2><ul>' + ''.join('<li>' + esc(x) + '</li>' for x in behavior['next_steps']) + '</ul>')
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Reversium report</title><style>{STYLE}</style><main>
<p class="brand">REVERSIUM / LOCAL ANALYSIS</p>
<nav><a href="/">Analyze another ZIP</a><button id="json-export">Download JSON</button><button id="html-export">Download HTML</button></nav>
<h1>Understand what’s inside.</h1><p>{esc(report['scope'])}</p>
<div class="cards">{''.join(f'<article><strong>{esc(v)}</strong><span>{esc(k.replace("_", " "))}</span></article>' for k,v in report['summary'].items() if k != 'languages')}</div>
<div role="tablist" aria-label="Report sections" hidden>
<button role="tab" id="tab-behavior" aria-controls="panel-behavior" aria-selected="true">What this software does</button>
<button role="tab" id="tab-architecture" aria-controls="panel-architecture" aria-selected="false" tabindex="-1">Architecture</button>
<button role="tab" id="tab-evidence" aria-controls="panel-evidence" aria-selected="false" tabindex="-1">Evidence</button>
<button role="tab" id="tab-coverage" aria-controls="panel-coverage" aria-selected="false" tabindex="-1">Coverage</button>
</div>
<section role="tabpanel" id="panel-behavior" aria-labelledby="tab-behavior" tabindex="0">{behavior_content}</section>
<section role="tabpanel" id="panel-architecture" aria-labelledby="tab-architecture" tabindex="0">
{platform_section}<h2>Architecture: import and dependency mentions</h2>
<p>File → local file candidate or referenced package. Labels distinguish internal, external, unresolved and ambiguous references. First 100 unique edges; full references are in the Evidence tab.</p>
<div class="scroll">{''.join(diagram) if pairs else '<p>No supported dependency references found.</p>'}</div></section>
<section role="tabpanel" id="panel-evidence" aria-labelledby="tab-evidence" tabindex="0">
<h2>Evidence</h2><label for="evidence-filter">Filter evidence</label><input id="evidence-filter" type="search" placeholder="File, symbol, kind or resolution">
<p id="filter-count" role="status">{len(findings)} findings</p><div class="scroll"><table id="evidence-table"><thead><tr><th>Finding</th><th>Value</th><th>Location</th><th>Confidence</th><th>Resolution</th></tr></thead><tbody>{rows}</tbody></table></div>{comparison}</section>
<section role="tabpanel" id="panel-coverage" aria-labelledby="tab-coverage" tabindex="0">
<h2>What this report can explain</h2><p>Reversium identifies code and metadata clues. It cannot tell you exactly everything the program does. Missing files, runtime configuration, external services, dynamic behavior and obfuscation can hide functionality. Findings are evidence for review, not a complete behavioral specification.</p>
{binary_section}<h2>Inventory</h2><div class="scroll"><table><tr><th>File</th><th>Type</th><th>Bytes</th><th>Analysis coverage</th></tr>{files}</table></div>{readiness}
<h2>Coverage and limitations</h2><ul>{notes}</ul></section>
<p>Generated locally by Reversium 0.4.0. No paid services or remote assets.</p></main>
<script type="application/json" id="report-data">{payload}</script><script>{SCRIPT}</script></html>'''


STYLE = 'body{margin:0;background:#101823;color:#e8edf5;font:16px system-ui}main{max-width:1180px;margin:60px auto;padding:0 28px}.brand{color:#66d9c2;letter-spacing:3px;font-size:12px}h1{font-size:48px;letter-spacing:-2px}h2{margin-top:45px}p,li{color:#afbdce;line-height:1.7}.cards{display:flex;gap:14px;flex-wrap:wrap}article{padding:24px;background:#1c2838;border-radius:12px;min-width:130px}strong{display:block;font-size:30px}span{color:#afbdce}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:12px;border-bottom:1px solid #304056;overflow-wrap:anywhere}.scroll{overflow:auto}svg{width:100%;min-width:650px;background:#162130;border-radius:12px}button{background:#66d9c2;color:#101823;border:0;border-radius:8px;padding:14px 24px;font-weight:700;cursor:pointer}input{padding:20px}a{color:#66d9c2}'
STYLE += 'nav{display:flex;align-items:center;gap:12px;flex-wrap:wrap}input[type=search]{display:block;box-sizing:border-box;width:100%;max-width:600px;background:#1c2838;color:#e8edf5;border:1px solid #657890;border-radius:8px;margin-top:10px}button:disabled{opacity:.5;cursor:wait}pre{white-space:pre-wrap;overflow-wrap:anywhere}form{display:flex;flex-wrap:wrap;align-items:center;gap:12px}input[type=file]{max-width:100%;box-sizing:border-box}svg text{font:13px monospace}@media(max-width:600px){main{margin:28px auto;padding:0 16px}h1{font-size:34px}.cards article{flex:1;min-width:100px;padding:16px}nav button{padding:12px}td,th{padding:8px}}'
STYLE += 'table{min-width:760px}svg{min-width:1000px}'
STYLE += '[role=tablist]{display:flex;gap:8px;flex-wrap:wrap;margin-top:32px;padding-bottom:12px;border-bottom:1px solid #304056}[hidden]{display:none!important}[role=tab]{background:#1c2838;color:#afbdce;border:1px solid #657890}[role=tab][aria-selected=true]{background:#66d9c2;color:#101823;border-color:#66d9c2}:focus-visible{outline:3px solid #c7b6ff;outline-offset:4px}[role=tabpanel]{padding-bottom:20px}@media print{[role=tablist],nav,#evidence-filter,label[for=evidence-filter]{display:none!important}[role=tabpanel][hidden],#evidence-table tr[hidden]{display:block!important}[role=tabpanel]{break-before:page}#evidence-table tr[hidden]{display:table-row!important}.scroll{overflow:visible}table,svg{min-width:0}body{background:white;color:black}p,li,span{color:#333}}'
STYLE += '.explanation{margin:18px 0;min-width:0}.explanation h3{margin-top:0}.explanation p{margin:10px 0}.explanation b{color:#e8edf5}.assessment{font-size:14px;color:#66d9c2}tr:target{background:#304056}.evidence-link{overflow-wrap:anywhere}'

SCRIPT = '''const tabs=Array.from(document.querySelectorAll('[role=tab]'));
function activateTab(tab,focus=false){for(const item of tabs){const selected=item===tab;item.setAttribute('aria-selected',String(selected));item.tabIndex=selected?0:-1;document.getElementById(item.getAttribute('aria-controls')).hidden=!selected}if(focus)tab.focus()}
document.querySelector('[role=tablist]').hidden=false;
for(const tab of tabs){tab.addEventListener('click',()=>activateTab(tab));tab.addEventListener('keydown',event=>{let index=tabs.indexOf(tab);if(event.key==='ArrowRight')index=(index+1)%tabs.length;else if(event.key==='ArrowLeft')index=(index+tabs.length-1)%tabs.length;else if(event.key==='Home')index=0;else if(event.key==='End')index=tabs.length-1;else return;event.preventDefault();activateTab(tabs[index],true)})}
activateTab(tabs[0]);
const filter=document.querySelector('#evidence-filter');
filter.addEventListener('input',()=>{let count=0;for(const row of document.querySelectorAll('#evidence-table tbody tr')){row.hidden=!row.textContent.toLowerCase().includes(filter.value.toLowerCase());if(!row.hidden)count++}document.querySelector('#filter-count').textContent=count+' findings'});
function revealFinding(hash){if(!/^#finding-[0-9]+$/.test(hash))return;const row=document.getElementById(hash.slice(1));if(!row)return;activateTab(document.querySelector('#tab-evidence'));filter.value='';filter.dispatchEvent(new Event('input'));row.focus();row.scrollIntoView({block:'center'})}
for(const link of document.querySelectorAll('.evidence-link'))link.addEventListener('click',()=>revealFinding(link.getAttribute('href')));
window.addEventListener('hashchange',()=>revealFinding(window.location.hash));revealFinding(window.location.hash);
function download(text,type,name){const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
document.querySelector('#json-export').onclick=()=>download(document.querySelector('#report-data').textContent,'application/json','reversium-report.json');
document.querySelector('#html-export').onclick=()=>{const copy=document.documentElement.cloneNode(true);copy.querySelector('#evidence-filter').value='';for(const row of copy.querySelectorAll('tr'))row.removeAttribute('hidden');for(const panel of copy.querySelectorAll('[role=tabpanel]'))panel.removeAttribute('hidden');copy.querySelector('[role=tablist]').hidden=true;copy.querySelector('#filter-count').textContent=copy.querySelectorAll('#evidence-table tbody tr').length+' findings';download('<!doctype html>'+copy.outerHTML,'text/html','reversium-report.html')};'''
