import html
import json
from .explain import explain_software
from .feature_map import render_svg


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
    def target_label(finding):
        target = finding.get('target')
        if isinstance(target, dict):
            return target['file'] + ' :: ' + target['function']
        return target
    rows = ''.join(f'<tr id="finding-{index}" tabindex="-1"><td>{esc(f["kind"])}</td><td>{esc(f["value"])}</td><td>{location(f["evidence"])}</td><td>{esc(f["confidence"])}</td><td>{esc(f.get("resolution", "traced call" if f["kind"] == "handler_call" else "—"))}{" → " + esc(target_label(f)) if "target" in f else ""}</td></tr>' for index, f in enumerate(findings))
    files = ''.join(f'<tr><td>{esc(f["path"])}</td><td>{esc(f.get("binary", {}).get("format", f["language"] or f["category"]))}</td><td>{f["bytes"]}</td><td>{esc(f.get("analysis", "unknown"))}</td></tr>' for f in report['files'])
    notes = ''.join(f'<li>{esc(x)}</li>' for x in report['warnings'] + report['limitations'])
    payload = json.dumps(report).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    graph = report.get('feature_map', {'nodes': [], 'edges': [], 'features': [], 'unknowns': []})
    map_comparison = report.get('comparison', {}).get('feature_map', {})
    map_svg, map_omissions = render_svg(graph, map_comparison)
    feature_options = ''.join(f'<option value="{feature["id"]}">{esc(feature["name"])} — {esc(feature["file"])}</option>' for feature in graph['features'])
    catalogue = ''.join(f'<tr><td><b>{esc(feature.get("title", feature["name"]))}</b><br>{esc(feature["name"])}</td><td>{esc(feature["description"])}</td><td>{esc(feature["confidence"])}</td><td>' + ' · '.join(f'<a class="evidence-link" href="#finding-{index}">{location(findings[index]["evidence"])}</a>' for index in feature['evidence_indices']) + '</td></tr>' for feature in graph['features'])
    interaction_map = ('<h2>Feature interaction map</h2><p>Solid lines: traced source references. Dashed lines: inferred data-name connections. Shared names do not prove a shared database or business workflow.</p>'
                       + '<p>' + str(graph.get('coverage', {}).get('route_candidates', 0)) + ' heuristic route candidates; ' + str(graph.get('coverage', {}).get('route_references', 0)) + ' structural route references; ' + str(graph.get('coverage', {}).get('react_modules', 0)) + ' React/JSX modules; ' + str(graph.get('coverage', {}).get('parsed_js_files', 0)) + ' JS/TS files scanned. These counts are not a completeness percentage. JSX and call references include callbacks and conditional code; they do not prove a user workflow. Router prefixes are candidates where a single literal mount is resolved.</p>'
                       + '<label for="map-filter">Show feature</label><select id="map-filter"><option value="">All features</option>' + feature_options + '</select> <button id="svg-export">Download map SVG</button>'
                       + '<div class="scroll map-viewport">' + map_svg + '</div><p id="map-omissions">' + str(map_omissions['omitted_nodes']) + ' nodes and ' + str(map_omissions['omitted_edges']) + ' connections omitted from this view. Select a feature to rebuild its focused map. Full graph data is in JSON.</p>'
                       + '<section id="map-details" aria-live="polite"><h3>Inspect a connection</h3><p>Select a node or line to see evidence, participating features, and unknowns.</p></section>'
                       + '<h2>Feature catalogue</h2>' + ('<div class="scroll"><table><tr><th>Feature</th><th>Supported code behavior</th><th>Assessment</th><th>Evidence</th></tr>' + catalogue + '</table></div>' if catalogue else '<p>No supported route traces are available. The import inventory below is not a feature map.</p>')
                       + '<ul>' + ''.join('<li>' + esc(item) + '</li>' for item in graph['unknowns']) + '</ul>')
    if map_comparison:
        if map_comparison.get('status') == 'compared':
            removed = ', '.join(item.get('name', item.get('label', item['id'])) for item in map_comparison.get('removed_features_details', [])) or 'None'
            interaction_map += f'<h3>Map changes from baseline</h3><p>Green borders: added nodes. Amber borders: changed nodes/features. {len(map_comparison["added_features"])} features added; {len(map_comparison["changed_features"])} changed. Removed features: {esc(removed)}.</p>'
            interaction_map += '<p>Removed connections: ' + str(len(map_comparison.get('removed_connections', []))) + '</p><ul>' + ''.join('<li>' + esc(item['source'] + ' → ' + item['target'] + ' (' + item['label'] + ')') + '</li>' for item in map_comparison.get('removed_connections', [])[:20]) + '</ul>'
        else:
            interaction_map += '<p>Map comparison unavailable: baseline has no feature map.</p>'
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
<p class="brand">REVERSIUM 0.7.0 / LOCAL ANALYSIS</p>
<nav><a href="/">Analyze another ZIP</a><button id="json-export">Download JSON</button><button id="html-export">Download HTML</button></nav>
<div role="tablist" aria-label="Report sections">
<a role="tab" href="#panel-behavior" id="tab-behavior" aria-controls="panel-behavior" aria-selected="true">What this software does</a>
<a role="tab" href="#panel-architecture" id="tab-architecture" aria-controls="panel-architecture" aria-selected="false">Architecture</a>
<a role="tab" href="#panel-evidence" id="tab-evidence" aria-controls="panel-evidence" aria-selected="false">Evidence</a>
<a role="tab" href="#panel-coverage" id="tab-coverage" aria-controls="panel-coverage" aria-selected="false">Coverage</a>
</div>
<h1>Understand what’s inside.</h1><p>{esc(report['scope'])}</p>
<div class="cards">{''.join(f'<article><strong>{esc(v)}</strong><span>{esc(k.replace("_", " "))}</span></article>' for k,v in report['summary'].items() if k != 'languages')}</div>
<section role="tabpanel" id="panel-behavior" aria-labelledby="tab-behavior" tabindex="0">{behavior_content}</section>
<section role="tabpanel" id="panel-architecture" aria-labelledby="tab-architecture" tabindex="0">
{interaction_map}{platform_section}<h2>Architecture: import and dependency mentions</h2>
<p>File → local file candidate or referenced package. Labels distinguish internal, external, unresolved and ambiguous references. First 100 unique edges; full references are in the Evidence tab.</p>
<div class="scroll">{''.join(diagram) if pairs else '<p>No supported dependency references found.</p>'}</div></section>
<section role="tabpanel" id="panel-evidence" aria-labelledby="tab-evidence" tabindex="0">
<h2>Evidence</h2><label for="evidence-filter">Filter evidence</label><input id="evidence-filter" type="search" placeholder="File, symbol, kind or resolution">
<p id="filter-count" role="status">{len(findings)} findings</p><div class="scroll"><table id="evidence-table"><thead><tr><th>Finding</th><th>Value</th><th>Location</th><th>Confidence</th><th>Resolution</th></tr></thead><tbody>{rows}</tbody></table></div>{comparison}</section>
<section role="tabpanel" id="panel-coverage" aria-labelledby="tab-coverage" tabindex="0">
<h2>What this report can explain</h2><p>Reversium identifies code and metadata clues. It cannot tell you exactly everything the program does. Missing files, runtime configuration, external services, dynamic behavior and obfuscation can hide functionality. Findings are evidence for review, not a complete behavioral specification.</p>
{binary_section}<h2>Inventory</h2><div class="scroll"><table><tr><th>File</th><th>Type</th><th>Bytes</th><th>Analysis coverage</th></tr>{files}</table></div>{readiness}
<h2>Coverage and limitations</h2><ul>{notes}</ul></section>
<p>Generated locally by Reversium 0.7.0. No paid services or remote assets.</p></main>
<script type="application/json" id="report-data">{payload}</script><script>{SCRIPT}</script></html>'''


STYLE = 'body{margin:0;background:#101823;color:#e8edf5;font:16px system-ui}main{max-width:1180px;margin:60px auto;padding:0 28px}.brand{color:#66d9c2;letter-spacing:3px;font-size:12px}h1{font-size:48px;letter-spacing:-2px}h2{margin-top:45px}p,li{color:#afbdce;line-height:1.7}.cards{display:flex;gap:14px;flex-wrap:wrap}article{padding:24px;background:#1c2838;border-radius:12px;min-width:130px}strong{display:block;font-size:30px}span{color:#afbdce}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:12px;border-bottom:1px solid #304056;overflow-wrap:anywhere}.scroll{overflow:auto}svg{width:100%;min-width:650px;background:#162130;border-radius:12px}button{background:#66d9c2;color:#101823;border:0;border-radius:8px;padding:14px 24px;font-weight:700;cursor:pointer}input{padding:20px}a{color:#66d9c2}'
STYLE += 'nav{display:flex;align-items:center;gap:12px;flex-wrap:wrap}input[type=search]{display:block;box-sizing:border-box;width:100%;max-width:600px;background:#1c2838;color:#e8edf5;border:1px solid #657890;border-radius:8px;margin-top:10px}button:disabled{opacity:.5;cursor:wait}pre{white-space:pre-wrap;overflow-wrap:anywhere}form{display:flex;flex-wrap:wrap;align-items:center;gap:12px}input[type=file]{max-width:100%;box-sizing:border-box}svg text{font:13px monospace}@media(max-width:600px){main{margin:28px auto;padding:0 16px}h1{font-size:34px}.cards article{flex:1;min-width:100px;padding:16px}nav button{padding:12px}td,th{padding:8px}}'
STYLE += 'table{min-width:760px}svg{min-width:1000px}'
STYLE += '[role=tablist]{display:flex;gap:8px;flex-wrap:wrap;margin-top:32px;padding-bottom:12px;border-bottom:1px solid #304056}[hidden]{display:none!important}[role=tab]{background:#1c2838;color:#afbdce;border:1px solid #657890}[role=tab][aria-selected=true]{background:#66d9c2;color:#101823;border-color:#66d9c2}:focus-visible{outline:3px solid #c7b6ff;outline-offset:4px}[role=tabpanel]{padding-bottom:20px}@media print{[role=tablist],nav,#evidence-filter,label[for=evidence-filter]{display:none!important}[role=tabpanel][hidden],#evidence-table tr[hidden]{display:block!important}[role=tabpanel]{break-before:page}#evidence-table tr[hidden]{display:table-row!important}.scroll{overflow:visible}table,svg{min-width:0}body{background:white;color:black}p,li,span{color:#333}}'
STYLE += '.explanation{margin:18px 0;min-width:0}.explanation h3{margin-top:0}.explanation p{margin:10px 0}.explanation b{color:#e8edf5}.assessment{font-size:14px;color:#66d9c2}tr:target{background:#304056}.evidence-link{overflow-wrap:anywhere}'
STYLE += '[role=tablist]{position:sticky;top:0;z-index:5;background:#101823;padding:14px 0;margin-top:20px}[role=tab]{display:inline-block;text-decoration:none;padding:14px 20px;border-radius:8px;font-weight:700;font-size:14px}[role=tabpanel]{scroll-margin-top:140px}'
STYLE += '.preview-tab{display:inline-block;padding:12px 18px;background:#1c2838;border:1px solid #657890;border-radius:8px;text-decoration:none}nav[aria-label="Preview report sections"]{margin:20px 0}'
STYLE += '#map-details{padding:16px;background:#1c2838;border-radius:10px;margin-top:15px}select{background:#1c2838;color:#e8edf5;padding:12px;border:1px solid #657890;border-radius:8px;max-width:100%}.map-selectable{cursor:pointer}.map-selectable:focus{outline:2px solid #c7b6ff}.map-dimmed{opacity:.13}#feature-map-svg{min-width:1100px}'

SCRIPT = '''const tabs=Array.from(document.querySelectorAll('[role=tab]'));
function activateTab(tab,focus=false){for(const item of tabs){const selected=item===tab;item.setAttribute('aria-selected',String(selected));item.tabIndex=selected?0:-1;document.getElementById(item.getAttribute('aria-controls')).hidden=!selected}if(focus)tab.focus()}
for(const tab of tabs){tab.addEventListener('click',event=>{event.preventDefault();activateTab(tab)});tab.addEventListener('keydown',event=>{let index=tabs.indexOf(tab);if(event.key==='ArrowRight')index=(index+1)%tabs.length;else if(event.key==='ArrowLeft')index=(index+tabs.length-1)%tabs.length;else if(event.key==='Home')index=0;else if(event.key==='End')index=tabs.length-1;else return;event.preventDefault();activateTab(tabs[index],true)})}
activateTab(tabs[0]);
function revealPanel(){const tab=tabs.find(item=>'#'+item.getAttribute('aria-controls')===window.location.hash);if(tab)activateTab(tab)}
window.addEventListener('hashchange',revealPanel);revealPanel();
const filter=document.querySelector('#evidence-filter');
filter.addEventListener('input',()=>{let count=0;for(const row of document.querySelectorAll('#evidence-table tbody tr')){row.hidden=!row.textContent.toLowerCase().includes(filter.value.toLowerCase());if(!row.hidden)count++}document.querySelector('#filter-count').textContent=count+' findings'});
function revealFinding(hash){if(!/^#finding-[0-9]+$/.test(hash))return;const row=document.getElementById(hash.slice(1));if(!row)return;activateTab(document.querySelector('#tab-evidence'));filter.value='';filter.dispatchEvent(new Event('input'));row.focus();row.scrollIntoView({block:'center'})}
for(const link of document.querySelectorAll('.evidence-link'))link.addEventListener('click',()=>revealFinding(link.getAttribute('href')));
window.addEventListener('hashchange',()=>revealFinding(window.location.hash));revealFinding(window.location.hash);
const reportData=JSON.parse(document.querySelector('#report-data').textContent),graph=reportData.feature_map||{nodes:[],edges:[],features:[]};
const mapColumns={feature:0,module:1,handler:1,helper:2,data:3,external:3,rpc:3,storage:3,auth:3};
function drawMap(feature=''){
 const svg=document.querySelector('#feature-map-svg'),all=graph.nodes.filter(n=>!feature||n.features.includes(feature));
 const rootIds=new Set(graph.features.filter(f=>!feature||f.id===feature).map(f=>f.node_id));
 all.sort((a,b)=>(rootIds.has(b.id)-rootIds.has(a.id))||mapColumns[a.kind]-mapColumns[b.kind]||a.label.localeCompare(b.label)||a.id.localeCompare(b.id));
 const chosen=all.slice(0,120),positions=new Map(),counts=[0,0,0,0];
 for(const n of chosen){const c=rootIds.has(n.id)?0:mapColumns[n.kind];positions.set(n.id,[25+c*310,65+counts[c]++*115]);}
 const height=Math.max(220,Math.max(...counts)*115+90);svg.setAttribute('viewBox','0 0 1260 '+height);svg.replaceChildren();
 function el(tag,attrs,text,parent=svg){const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));if(text!==undefined)e.textContent=text;parent.append(e);return e;}
 el('rect',{width:'100%',height:'100%',fill:'#101823'});
 ['Features / UI modules','Handlers / modules','Helpers','Data / services'].forEach((label,c)=>el('text',{x:25+c*310,y:28,fill:'#afbdce','font-size':15},label));
 let drawn=0;const eligible=graph.edges.filter(e=>(!feature||e.features.includes(feature))&&positions.has(e.source)&&positions.has(e.target));
 const comparison=reportData.comparison?.feature_map||{};
 for(const edge of eligible.slice(0,240)){drawn++;const [sx,sy]=positions.get(edge.source),[tx,ty]=positions.get(edge.target),x1=sx+255,y1=sy+32,y2=ty+32;
 const g=el('g',{'class':'map-selectable','data-map-kind':'edge','data-map-id':edge.id,role:'button',tabindex:0,'aria-label':'Inspect connection: '+edge.label+' '+edge.id});
 el('title',{},edge.label+' ('+edge.confidence+')',g);
 const color=(comparison.added_edges||[]).includes(edge.id)?'#8fed75':(comparison.changed_edges||[]).includes(edge.id)?'#f8c86b':'#9cafc8';
 el('path',{d:`M${x1} ${y1} C${x1+45} ${y1},${tx-45} ${y2},${tx} ${y2}`,fill:'none',stroke:color,'stroke-width':2,'stroke-dasharray':edge.confidence==='inferred'?'7 5':''},undefined,g);
 el('text',{x:(x1+tx)/2,y:(y1+y2)/2-8,fill:'#b6c9de','font-size':11,'text-anchor':'middle'},edge.label,g);
 }
 for(const n of chosen){const [x,y]=positions.get(n.id),g=el('g',{'class':'map-selectable','data-map-kind':'node','data-map-id':n.id,role:'button',tabindex:0,'aria-label':'Inspect '+n.kind+': '+n.label});
 const color=(comparison.added_nodes||[]).includes(n.id)?'#8fed75':(comparison.changed_nodes||[]).includes(n.id)?'#f8c86b':'#66d9c2';
 el('title',{},n.label,g);el('rect',{x,y,width:255,height:72,rx:10,fill:'#1c2838',stroke:color,'stroke-width':2},undefined,g);
 el('text',{x:x+12,y:y+27,fill:'#e8edf5','font-size':14},n.label.slice(0,30),g);el('text',{x:x+12,y:y+52,fill:'#afbdce','font-size':12},n.kind+' · '+n.features.length+' feature(s)',g);}
 const edgesForFeature=graph.edges.filter(e=>!feature||e.features.includes(feature));
 document.querySelector('#map-omissions').textContent=(all.length-chosen.length)+' nodes and '+(edgesForFeature.length-drawn)+' connections omitted from this view. Select a feature to rebuild its focused map. Full graph data is in JSON.';
 document.querySelector('#map-details').replaceChildren();
}
document.querySelector('#map-filter').addEventListener('change',event=>drawMap(event.target.value));
function inspectMap(element){const collection=element.getAttribute('data-map-kind')==='node'?graph.nodes:graph.edges;const item=collection.find(item=>item.id===element.getAttribute('data-map-id'));if(!item)return;const box=document.querySelector('#map-details');box.replaceChildren();const title=document.createElement('h3');title.textContent=item.label;box.append(title);if(item.source){const path=document.createElement('p');path.textContent=(graph.nodes.find(n=>n.id===item.source)?.label||item.source)+' → '+(graph.nodes.find(n=>n.id===item.target)?.label||item.target);box.append(path);}const assessment=document.createElement('p');assessment.textContent=(item.confidence||item.kind)+' · Static evidence, not runtime verification.';box.append(assessment);for(const text of item.unknowns||[]){const p=document.createElement('p');p.textContent=text;box.append(p)}for(const feature of graph.features.filter(feature=>item.features.includes(feature.id))){const p=document.createElement('p');p.textContent='Feature: '+feature.name;box.append(p);for(const unknown of feature.unknowns){const p=document.createElement('p');p.textContent='Unknown: '+unknown;box.append(p)}}for(const index of item.evidence_indices){const f=reportData.findings[index],a=document.createElement('a');a.href='#finding-'+index;a.textContent=f.evidence.file+':'+f.evidence.line+' ('+f.kind+')';a.onclick=()=>revealFinding(a.hash);box.append(a,document.createTextNode(' · '))}}
const mapSvg=document.querySelector('#feature-map-svg');
mapSvg.addEventListener('click',event=>{const item=event.target.closest('.map-selectable');if(item)inspectMap(item)});
mapSvg.addEventListener('keydown',event=>{const item=event.target.closest('.map-selectable');if(item&&(event.key==='Enter'||event.key===' ')){event.preventDefault();inspectMap(item)}});
drawMap();
function download(text,type,name){const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
document.querySelector('#svg-export').onclick=()=>{const copy=document.querySelector('#feature-map-svg').cloneNode(true);for(const item of copy.querySelectorAll('.map-dimmed'))item.classList.remove('map-dimmed');download(copy.outerHTML,'image/svg+xml','reversium-feature-map.svg')};
document.querySelector('#json-export').onclick=()=>download(document.querySelector('#report-data').textContent,'application/json','reversium-report.json');
document.querySelector('#html-export').onclick=()=>{const copy=document.documentElement.cloneNode(true);copy.querySelector('#evidence-filter').value='';copy.querySelector('#map-filter').value='';for(const item of copy.querySelectorAll('.map-dimmed'))item.classList.remove('map-dimmed');for(const row of copy.querySelectorAll('tr'))row.removeAttribute('hidden');for(const panel of copy.querySelectorAll('[role=tabpanel]'))panel.removeAttribute('hidden');for(const tab of copy.querySelectorAll('[role=tab]'))tab.removeAttribute('tabindex');copy.querySelector('#filter-count').textContent=copy.querySelectorAll('#evidence-table tbody tr').length+' findings';download('<!doctype html>'+copy.outerHTML,'text/html','reversium-report.html')};'''

STYLE += '.map-viewport{max-height:650px;border:1px solid #304056;border-radius:12px}'
