import html
import json
from .runtime_review import SCRIPT as RUNTIME_SCRIPT
from .readiness import panel as readiness_panel, SCRIPT as READINESS_SCRIPT
from .file_review import panel as file_review_panel, SCRIPT as FILE_REVIEW_SCRIPT
from .review_tools import PANEL as COMPARE_PANEL, SCRIPT as REVIEW_SCRIPT
from .maintenance_ui import handover_panel, IMPACT_PANEL, SCRIPT as MAINTENANCE_SCRIPT
from .report_layout import layout
from .user_guide import GUIDE, SCRIPT as GUIDE_SCRIPT
from .help_ui import ABOUT, EXPORT_HELP, FAQ_GENERAL
from .owner_summary import owner_summary, NEXT_STEPS
from .presentation import STYLE as MODERN_STYLE, SCRIPT as HELP_SCRIPT
from .explain import explain_software
from .feature_map import render_svg
from .workflow_paths import workflow_paths
from .assistant_ui import PANEL as AI_PANEL, STYLE as AI_STYLE, SCRIPT as AI_SCRIPT, FAQ_AI


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
        suffix = ':' + str(evidence['line']) if 'line' in evidence else ' @ byte 0x' + format(evidence['offset'], 'x') if 'offset' in evidence else ' (file-level check)'
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
    paths = workflow_paths(graph)
    workflow_options, workflow_cards = [], []
    for number, path in enumerate(paths):
        workflow_options.append(f'<option value="{number}">{esc(path["screen"])} → {esc(path["nodes"][-1]["label"])}</option>')
        steps = []
        for step, node in enumerate(path['nodes']):
            edge = path['edges'][step - 1] if step else None
            stage = 'Screen module' if not step else 'Database operation' if node['kind'] == 'data' else 'API endpoint' if edge['label'].startswith('API target candidate ') else 'Callback / code reference'
            indices = edge['evidence_indices'] if edge else node['evidence_indices']
            links = ' · '.join(f'<a class="evidence-link" href="#finding-{i}">{location(findings[i]["evidence"])}</a>' for i in indices)
            connection = (esc(edge['label']) + ' — ' + esc(edge['confidence'])) if edge else 'Source module identified'
            steps.append(f'<li><span class="assessment">{step + 1}. {stage}</span><h4>{esc(node["label"])}</h4><p>{connection}</p><p>{links or "No location available."}</p></li>')
        workflow_cards.append(f'<section class="workflow-path" data-workflow="{number}"' + (' hidden' if number else '') + f'><h3>{esc(path["screen"])} → {esc(path["nodes"][-1]["label"])}</h3><ol class="workflow-steps">' + ''.join(steps) + '</ol></section>')
    focused = ('<h2>Follow one workflow</h2><p>Read from top to bottom: screen → callback → API → database. Each step follows an existing graph connection; use its source link to inspect the evidence.</p>'
               + ('<label for="workflow-filter">Choose a screen and data branch</label><select id="workflow-filter">' + ''.join(workflow_options) + '</select>' + ''.join(workflow_cards) if paths else '<p>No complete screen → callback → API → database candidate was found. Partial references remain in the full map; missing paths do not mean missing features.</p>')
               + '<details class="workflow-unknowns" open><summary>What remains unknown</summary><p>These are static source candidates, not a recording of a user journey. Inferred prop providers may belong to different component instances. Conditions, callback arguments, request payloads, authentication, permissions, database identity and successful responses remain unverified. A database operation can be logging or a side effect rather than the main purpose of the request.</p><p>One shortest data branch per screen is shown, within 12 connections and 3,000 search states per screen. Other branches, reads, errors and unsupported dynamic code may be missing. Imports and rendered child modules are excluded from this path search.</p></details>')
    interaction_map = (focused + '<details id="full-feature-map"><summary>Explore the full feature interaction map</summary><h2>Feature interaction map</h2><p>Solid lines: traced source references. Dashed lines: inferred connections, including API targets and prop bindings. Shared names do not prove a shared database or business workflow.</p>'
                       + '<p>' + str(graph.get('coverage', {}).get('route_candidates', 0)) + ' heuristic route candidates; ' + str(graph.get('coverage', {}).get('route_references', 0)) + ' structural route references; ' + str(graph.get('coverage', {}).get('react_modules', 0)) + ' React/JSX modules; ' + str(graph.get('coverage', {}).get('parsed_js_files', 0)) + ' JS/TS files scanned. These counts are not a completeness percentage. JSX and call references include callbacks and conditional code; they do not prove a user workflow. Router prefixes are candidates where a single literal mount is resolved.</p>'
                       + '<p>' + str(graph.get('coverage', {}).get('prop_bindings', 0)) + ' prop binding candidates; ' + str(graph.get('coverage', {}).get('api_targets', 0)) + ' API target contexts resolved. Bindings can have multiple possible providers; target counts include separate callers and are not unique endpoint counts.</p>'
                       + '<label for="map-filter">Show feature</label><select id="map-filter"><option value="">All features</option>' + feature_options + '</select> <button id="svg-export">Download map SVG</button>'
                       + '<div class="scroll map-viewport">' + map_svg + '</div><p id="map-omissions">' + str(map_omissions['omitted_nodes']) + ' nodes and ' + str(map_omissions['omitted_edges']) + ' connections omitted from this view. Select a feature to rebuild its focused map. Full graph data is in JSON.</p>'
                       + '<section id="map-details" aria-live="polite"><h3>Inspect a connection</h3><p>Select a node or line to see evidence, participating features, and unknowns.</p></section>'
                       + '</details><h2>Feature catalogue</h2>' + ('<div class="scroll"><table><tr><th>Feature</th><th>Supported code behavior</th><th>Assessment</th><th>Evidence</th></tr>' + catalogue + '</table></div>' if catalogue else '<p>No supported route traces are available. The import inventory below is not a feature map.</p>')
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
    behavior_content = ('<h2>Software findings</h2><p>' + esc(behavior['summary']) + '</p><p>' + esc(behavior['method']) + '</p>'
                        + (''.join(explanation_cards) or '<p>No behavior explanation is supported by the current findings. Missing findings do not mean the software has no features.</p>')
                        + (f'<p>{behavior["omitted_groups"]} additional explanation groups are omitted from this overview. All findings remain in Evidence.</p>' if behavior['omitted_groups'] else '')
                        + '<h2>What we still do not know</h2><ul>' + ''.join('<li>' + esc(x) + '</li>' for x in behavior['unknowns']) + '</ul>'
                        + '<h2>How to confirm the explanation</h2><ul>' + ''.join('<li>' + esc(x) + '</li>' for x in behavior['next_steps']) + '</ul>')
    owner_content = owner_summary(report)
    goal_label = {"understand": "Understand the software", "handover": "Prepare a developer handover", "change": "Plan maintenance or modernization"}.get(report.get("user_goal"), "Understand the software")
    goal_guidance = {
        'understand': 'Focus on the supported features and supporting services. Your next useful result is a short description you can confirm with the software owner.',
        'handover': 'Focus on source locations, missing setup requirements and one important workflow. Your next useful result is a developer handover with explicit checks still to perform.',
        'change': 'Focus on feature connections and shared data or services before estimating a change. Your next useful result is a shortlist of affected components and unresolved dependencies.'
    }.get(report.get('user_goal', 'understand'), 'Start with supported findings, then check their evidence and gaps.')
    alert_counts = report.get('file_review', {}).get('counts')
    alert_label = 'File alerts: ' + ' · '.join(str(alert_counts.get(k, 0)) + ' ' + k for k in ('red', 'yellow', 'green')) if alert_counts is not None else 'File alerts unavailable: re-analyze ZIP'
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Reversium report</title><style>{STYLE}{AI_STYLE}{MODERN_STYLE}</style><main>
<p class="brand">REVERSIUM 0.24.0 / LOCAL ANALYSIS</p>
<nav><a href="/">Start a new analysis</a><span>Step 3 · Review findings → Step 4 · Save &amp; next steps</span></nav>
{'<p class="sample-notice">SAMPLE ANALYSIS · Fictional demonstration data. Start a new analysis to inspect your ZIP.</p>' if report.get("example") else ''}
<p><b>Package:</b> {esc(report.get("archive_name", "Uploaded software package"))} · <b>Your goal:</b> {esc(goal_label)}</p>
<div role="tablist" aria-label="Report sections">
<a role="tab" href="#panel-behavior" id="tab-behavior" aria-controls="panel-behavior" aria-selected="false">About</a>
<a role="tab" href="#panel-software" id="tab-software" aria-controls="panel-software" aria-selected="true">Review findings</a>
<a role="tab" href="#panel-architecture" id="tab-architecture" aria-controls="panel-architecture" aria-selected="false">Architecture</a>
<button role="tab" id="tab-file-review" aria-controls="panel-file-review" aria-selected="false">File alerts</button><button role="tab" id="tab-readiness" aria-controls="panel-readiness" aria-selected="false">Setup &amp; readiness</button><button role="tab" id="tab-handover" aria-controls="panel-handover" aria-selected="false">Handover</button><button role="tab" id="tab-compare" aria-controls="panel-compare" aria-selected="false">Compare reports</button><button role="tab" id="tab-impact" aria-controls="panel-impact" aria-selected="false">Change impact</button><a role="tab" href="#panel-evidence" id="tab-evidence" aria-controls="panel-evidence" aria-selected="false">Evidence</a>
<a role="tab" href="#panel-coverage" id="tab-coverage" aria-controls="panel-coverage" aria-selected="false">Coverage</a>
<a role="tab" href="#panel-assistant" id="tab-assistant" aria-controls="panel-assistant" aria-selected="false">AI assistant · optional</a><button role="tab" id="tab-help" aria-controls="panel-help" aria-selected="false">Help</button><button role="tab" id="tab-faq" aria-controls="panel-faq" aria-selected="false">FAQ</button><button role="tab" id="tab-finish" aria-controls="panel-finish" aria-selected="false">Save &amp; next steps</button></div>
<h1>Your file review is complete.</h1><p>{esc(report['scope'])}</p>
<nav class="risk-banner"><button data-guide="tab-file-review">{esc(alert_label)}</button><span>Review signals, not a safety guarantee. ZIP contents were not executed.</span></nav><details><summary>Technical inventory numbers</summary><div class="cards">{''.join(f'<article><strong>{esc(v)}</strong><span>{esc(k.replace("_", " "))}</span></article>' for k,v in report['summary'].items() if k != 'languages')}</div><p>Counts show inspected material, not how complete or reliable the software is.</p></details>
<section role="tabpanel" id="panel-behavior" aria-labelledby="tab-behavior" tabindex="0">{ABOUT}</section>
<section role="tabpanel" id="panel-software" aria-labelledby="tab-software" tabindex="0"><h2>Review your results</h2><p>These are clues found in the files. Open “Why we say this” to see where each clue came from. A clue is not proof that a feature works.</p><p>{esc(goal_guidance)}</p>{owner_content}<h3>What should I do next?</h3><p>For a handover, send a readable report to your developer and agree on one feature to verify. You do not need to read every code reference first.</p><nav><button data-guide="tab-architecture">Explore feature connections</button><button data-guide="tab-coverage">Check gaps and limitations</button><button data-guide="tab-finish">Continue to save &amp; next steps</button></nav><details><summary>Detailed findings for a developer</summary>{behavior_content}</details></section>
<section role="tabpanel" id="panel-architecture" aria-labelledby="tab-architecture" tabindex="0">
<h2>Explore relationships</h2><p>Choose the graphical feature map or the file relationship diagram, or follow a single workflow below. These show supported source references, not verified runtime behavior.</p><nav><button data-diagram="full-feature-map">Show graphical feature map</button><button data-diagram="file-relationships">Show file relationships</button></nav>{interaction_map}{platform_section}<h2 id="file-relationships" tabindex="-1">File relationships: imports and dependencies</h2>
<p>File → local file candidate or referenced package. Labels distinguish internal, external, unresolved and ambiguous references. First 100 unique edges; full references are in the Evidence tab.</p>
<div class="scroll">{''.join(diagram) if pairs else '<p>No supported dependency references found.</p>'}</div></section>
<section role="tabpanel" id="panel-file-review" aria-labelledby="tab-file-review" tabindex="0">{file_review_panel(report)}</section><section role="tabpanel" id="panel-readiness" aria-labelledby="tab-readiness" tabindex="0">{readiness_panel(report)}</section><section role="tabpanel" id="panel-handover" aria-labelledby="tab-handover" tabindex="0">{handover_panel(report)}</section><section role="tabpanel" id="panel-compare" aria-labelledby="tab-compare" tabindex="0">{COMPARE_PANEL}</section><section role="tabpanel" id="panel-impact" aria-labelledby="tab-impact" tabindex="0">{IMPACT_PANEL}</section><section role="tabpanel" id="panel-evidence" aria-labelledby="tab-evidence" tabindex="0">
<h2>Evidence</h2><label for="evidence-filter">Filter evidence</label><input id="evidence-filter" type="search" placeholder="File, symbol, kind or resolution">
<p id="filter-count" role="status">{len(findings)} findings</p><div class="scroll"><table id="evidence-table"><thead><tr><th>Finding</th><th>Value</th><th>Location</th><th>Confidence</th><th>Resolution</th></tr></thead><tbody>{rows}</tbody></table></div>{comparison}</section>
<section role="tabpanel" id="panel-coverage" aria-labelledby="tab-coverage" tabindex="0">
<h2>What this report can explain</h2><p>Reversium identifies code and metadata clues. It cannot tell you exactly everything the program does. Missing files, runtime configuration, external services, dynamic behavior and obfuscation can hide functionality. Findings are evidence for review, not a complete behavioral specification.</p>
{binary_section}<h2>Inventory</h2><div class="scroll"><table><tr><th>File</th><th>Type</th><th>Bytes</th><th>Analysis coverage</th></tr>{files}</table></div>{readiness}
<h2>Coverage and limitations</h2><ul>{notes}</ul></section>
<section role="tabpanel" id="panel-assistant" aria-labelledby="tab-assistant" tabindex="0">{AI_PANEL}</section>
<section role="tabpanel" id="panel-help" aria-labelledby="tab-help" tabindex="0">{GUIDE}</section>
<section role="tabpanel" id="panel-faq" aria-labelledby="tab-faq" tabindex="0">{FAQ_GENERAL}{EXPORT_HELP}{FAQ_AI}</section>
<section role="tabpanel" id="panel-finish" aria-labelledby="tab-finish" tabindex="0"><h2>Step 4 · Save and decide what comes next</h2><p>Keep a record of this analysis, then choose a practical check. A saved report is not proof that the software runs.</p><h3>Save your analysis</h3><p><b>Recommended for you:</b> save the readable report and send it to the developer. Technical data is optional and mainly useful for scripts or comparing packages.</p><nav><button id="html-export">Save readable report (HTML)</button><button id="json-export">Save technical data (JSON)</button></nav>{EXPORT_HELP}{NEXT_STEPS}<nav><button data-guide="tab-coverage">Review remaining gaps</button><button data-guide="tab-assistant">Optional: ask AI about selected evidence</button><a href="/">Start another analysis</a></nav><p>AI is optional. Connecting an account is not needed to read or save this report.</p></section><p>3Sci.com · 2026</p><p>Generated locally by Reversium 0.24.0. Local analysis needs no paid services. Optional AI shares only approved requests.</p></main>
<script type="application/json" id="report-data">{payload}</script><script>{SCRIPT}{AI_SCRIPT}{HELP_SCRIPT}{GUIDE_SCRIPT}{MAINTENANCE_SCRIPT}{REVIEW_SCRIPT}{FILE_REVIEW_SCRIPT}{READINESS_SCRIPT}{RUNTIME_SCRIPT}</script></html>'''
    return layout(page)


STYLE = 'body{margin:0;background:#101823;color:#e8edf5;font:16px system-ui}main{max-width:1180px;margin:60px auto;padding:0 28px}.brand{color:#66d9c2;letter-spacing:3px;font-size:12px}h1{font-size:48px;letter-spacing:-2px}h2{margin-top:45px}p,li{color:#afbdce;line-height:1.7}.cards{display:flex;gap:14px;flex-wrap:wrap}article{padding:24px;background:#1c2838;border-radius:12px;min-width:130px}strong{display:block;font-size:30px}span{color:#afbdce}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:12px;border-bottom:1px solid #304056;overflow-wrap:anywhere}.scroll{overflow:auto}svg{width:100%;min-width:650px;background:#162130;border-radius:12px}button{background:#66d9c2;color:#101823;border:0;border-radius:8px;padding:14px 24px;font-weight:700;cursor:pointer}input{padding:20px}a{color:#66d9c2}'
STYLE += 'nav{display:flex;align-items:center;gap:12px;flex-wrap:wrap}input[type=search]{display:block;box-sizing:border-box;width:100%;max-width:600px;background:#1c2838;color:#e8edf5;border:1px solid #657890;border-radius:8px;margin-top:10px}button:disabled{opacity:.5;cursor:wait}pre{white-space:pre-wrap;overflow-wrap:anywhere}form{display:flex;flex-wrap:wrap;align-items:center;gap:12px}input[type=file]{max-width:100%;box-sizing:border-box}svg text{font:13px monospace}@media(max-width:600px){main{margin:28px auto;padding:0 16px}h1{font-size:34px}.cards article{flex:1;min-width:100px;padding:16px}nav button{padding:12px}td,th{padding:8px}}'
STYLE += 'table{min-width:760px}svg{min-width:1000px}'
STYLE += '[role=tablist]{display:flex;gap:8px;flex-wrap:wrap;margin-top:32px;padding-bottom:12px;border-bottom:1px solid #304056}[hidden]{display:none!important}[role=tab]{background:#1c2838;color:#afbdce;border:1px solid #657890}[role=tab][aria-selected=true]{background:#66d9c2;color:#101823;border-color:#66d9c2}:focus-visible{outline:3px solid #c7b6ff;outline-offset:4px}[role=tabpanel]{padding-bottom:20px}@media print{[role=tablist],nav,#evidence-filter,label[for=evidence-filter]{display:none!important}[role=tabpanel][hidden],#evidence-table tr[hidden]{display:block!important}[role=tabpanel]{break-before:page}#evidence-table tr[hidden]{display:table-row!important}.scroll{overflow:visible}table,svg{min-width:0}body{background:white;color:black}p,li,span{color:#333}}'
STYLE += '.explanation{margin:18px 0;min-width:0}.explanation h3{margin-top:0}.explanation p{margin:10px 0}.explanation b{color:#e8edf5}.assessment{font-size:14px;color:#66d9c2}tr:target{background:#304056}.evidence-link{overflow-wrap:anywhere}'
STYLE += '[role=tablist]{position:sticky;top:0;z-index:5;background:#101823;padding:14px 0;margin-top:20px}[role=tab]{display:inline-block;text-decoration:none;padding:14px 20px;border-radius:8px;font-weight:700;font-size:14px}[role=tabpanel]{scroll-margin-top:140px}'
STYLE += '.preview-tab{display:inline-block;padding:12px 18px;background:#1c2838;border:1px solid #657890;border-radius:8px;text-decoration:none}nav[aria-label="Preview report sections"]{margin:20px 0}'
STYLE += '#map-details{padding:16px;background:#1c2838;border-radius:10px;margin-top:15px}select{background:#1c2838;color:#e8edf5;padding:12px;border:1px solid #657890;border-radius:8px;max-width:100%}.map-selectable{cursor:pointer}.map-selectable:focus{outline:2px solid #c7b6ff}.map-dimmed{opacity:.13}#feature-map-svg{min-width:1100px}'

STYLE += '.workflow-steps{list-style:none;padding:0;max-width:800px}.workflow-steps li{padding:16px;margin:0 0 16px;border:1px solid #657890;border-left:4px solid #66d9c2;border-radius:8px;background:#1c2838;overflow-wrap:anywhere}.workflow-steps li+li:before{content:"↓";display:block;color:#66d9c2}.workflow-steps h4{margin:8px 0;font-size:18px}.workflow-steps p{margin:8px 0}.workflow-unknowns{max-width:800px;margin:20px 0}summary{cursor:pointer;padding:12px 0}'

SCRIPT = '''document.querySelector('#workflow-filter')?.addEventListener('change',event=>{for(const path of document.querySelectorAll('[data-workflow]'))path.hidden=path.dataset.workflow!==event.target.value});
const tabs=Array.from(document.querySelectorAll('[role=tab]'));
function activateTab(tab,focus=false){for(const item of tabs){const selected=item===tab;item.setAttribute('aria-selected',String(selected));item.tabIndex=selected?0:-1;document.getElementById(item.getAttribute('aria-controls')).hidden=!selected}if(focus)tab.focus()}
for(const tab of tabs){tab.addEventListener('click',event=>{event.preventDefault();activateTab(tab)});tab.addEventListener('keydown',event=>{let index=tabs.indexOf(tab);if(event.key==='ArrowRight')index=(index+1)%tabs.length;else if(event.key==='ArrowLeft')index=(index+tabs.length-1)%tabs.length;else if(event.key==='Home')index=0;else if(event.key==='End')index=tabs.length-1;else return;event.preventDefault();activateTab(tabs[index],true)})}
activateTab(document.querySelector('#tab-software')||tabs[0]);
for(const button of document.querySelectorAll('[data-guide]'))button.onclick=()=>{activateTab(document.getElementById(button.dataset.guide));document.getElementById(document.getElementById(button.dataset.guide).getAttribute('aria-controls')).focus()};
function revealPanel(){const tab=tabs.find(item=>'#'+item.getAttribute('aria-controls')===window.location.hash);if(tab)activateTab(tab)}
window.addEventListener('hashchange',revealPanel);revealPanel();
for(const button of document.querySelectorAll('[data-diagram]'))button.onclick=()=>{const target=document.getElementById(button.dataset.diagram);if(target.tagName==='DETAILS')target.open=true;target.scrollIntoView({block:'start'});target.focus()};
for(const nav of document.querySelectorAll('.subnav')){const buttons=[...nav.querySelectorAll('[data-subsection]')];function choose(b){for(const item of buttons){const selected=item===b;item.setAttribute('aria-pressed',String(selected));const section=document.getElementById(item.dataset.subsection);section.hidden=!selected;if(selected)section.querySelector('details')?.setAttribute('open','')}}for(const b of buttons)b.onclick=()=>choose(b);choose(buttons[0])}
const filter=document.querySelector('#evidence-filter');
filter.addEventListener('input',()=>{let count=0;for(const row of document.querySelectorAll('#evidence-table tbody tr')){row.hidden=!row.textContent.toLowerCase().includes(filter.value.toLowerCase());if(!row.hidden)count++}document.querySelector('#filter-count').textContent=count+' findings'});
function revealFinding(hash){if(!/^#finding-[0-9]+$/.test(hash))return;const row=document.getElementById(hash.slice(1));if(!row)return;activateTab(document.querySelector('#tab-evidence'));filter.value='';filter.dispatchEvent(new Event('input'));row.focus();row.scrollIntoView({block:'center'})}
for(const link of document.querySelectorAll('.evidence-link'))link.addEventListener('click',event=>{event.preventDefault();revealFinding(link.getAttribute('href'))});
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
document.querySelector('#html-export').onclick=()=>{const copy=document.documentElement.cloneNode(true);copy.querySelector('#control-help')?.remove();for(const el of copy.querySelectorAll('[aria-describedby]')){if(el.getAttribute('aria-describedby')==='control-help')el.removeAttribute('aria-describedby')}copy.querySelector('#panel-assistant')?.remove();if(copy.querySelector('#runtime-preview')){copy.querySelector('#runtime-preview').textContent='';copy.querySelector('#runtime-preview').hidden=true;}if(copy.querySelector('#runtime-apply'))copy.querySelector('#runtime-apply').hidden=true;if(copy.querySelector('#handover-preview'))copy.querySelector('#handover-preview').textContent='';if(copy.querySelector('#handover-apply'))copy.querySelector('#handover-apply').hidden=true;if(copy.querySelector('#baseline-results'))copy.querySelector('#baseline-results').textContent='';if(copy.querySelector('#baseline-save'))copy.querySelector('#baseline-save').disabled=true;for(const field of copy.querySelectorAll('.task-owner,.task-notes')){field.value='';field.removeAttribute('value');if(field.tagName==='TEXTAREA')field.textContent=''}for(const select of copy.querySelectorAll('.task-status')){for(const option of select.options)option.removeAttribute('selected');select.selectedIndex=0}copy.querySelector('#tab-assistant')?.remove();copy.querySelector('meta[name=assistant-session]')?.remove();copy.querySelector('#evidence-filter').value='';copy.querySelector('#map-filter').value='';if(copy.querySelector('#workflow-filter'))copy.querySelector('#workflow-filter').value='0';for(const path of copy.querySelectorAll('[data-workflow]'))path.hidden=path.dataset.workflow!=='0';for(const item of copy.querySelectorAll('.map-dimmed'))item.classList.remove('map-dimmed');for(const row of copy.querySelectorAll('tr'))row.removeAttribute('hidden');for(const button of copy.querySelectorAll('[data-risk-filter]'))button.setAttribute('aria-pressed',String(button.dataset.riskFilter==='all'));if(copy.querySelector('#risk-count'))copy.querySelector('#risk-count').textContent=copy.querySelectorAll('#risk-table tbody tr').length+' files shown. No signals is not a guarantee of safety.';for(const panel of copy.querySelectorAll('[role=tabpanel],.subsection'))panel.removeAttribute('hidden');for(const tab of copy.querySelectorAll('[role=tab]'))tab.removeAttribute('tabindex');copy.querySelector('#filter-count').textContent=copy.querySelectorAll('#evidence-table tbody tr').length+' findings';download('<!doctype html>'+copy.outerHTML,'text/html','reversium-report.html')};'''

STYLE += '.map-viewport{max-height:650px;border:1px solid #304056;border-radius:12px}'

STYLE += '.report-brand{display:flex;align-items:center;gap:12px;font-weight:700}.report-brand img{width:48px;height:40px;object-fit:contain;background:#12213b;border-radius:8px;padding:8px}.report-brand small{display:block;font-size:12px;font-weight:400;margin-top:5px}.subnav{margin:20px 0}.subnav button[aria-pressed=true]{outline:3px solid #8897ef}.inventory-numbers h2{font-size:16px;margin-top:24px}.inventory-numbers article{padding:12px;min-width:100px}.inventory-numbers strong{font-size:23px}main{margin-top:22px}.subsection>h2:first-child{margin-top:22px}'

STYLE += '.subsection table{table-layout:fixed}.subsection th,.subsection td{overflow-wrap:anywhere;vertical-align:top}.report-brand{margin-bottom:14px}.subsection th{white-space:normal}'

STYLE += '.handover-task{max-width:900px;min-width:0;margin:18px 0}.handover-task label{display:block;margin:12px 0}.handover-task input,.handover-task textarea{display:block;width:100%;box-sizing:border-box;max-width:100%;padding:12px}.handover-task select{min-width:230px}.handover-task p{margin:8px 0}'

STYLE += '.relationship-change{background:#fff!important;color:#17253c!important;border:1px solid #cbd5e1;border-left:5px solid #4058da;border-radius:12px;padding:22px;margin:20px 0}.relationship-change h3{color:#17253c}.relationship-change a{color:#304bb8}.relationship-change svg{background:#fff;border-radius:10px}.relationship-change p{line-height:1.6}'

STYLE += '.risk-light{display:inline-block;padding:5px 9px;border-radius:6px;font-weight:700}.risk-red{background:#fee2e2;color:#8b1616}.risk-yellow{background:#fff1b8;color:#694b00}.risk-green{background:#dcfce7;color:#14532d}.risk-banner{padding:14px 0;align-items:center}.risk-banner span{color:#40516c}#risk-table td{vertical-align:top}#risk-table a{display:block;margin-bottom:8px}'

STYLE += '#risk-table .risk-light{white-space:nowrap}#risk-table td:nth-child(2){min-width:180px}#risk-table td:nth-child(3){min-width:160px}#risk-table td:nth-child(4){min-width:300px}'

STYLE += '.handover-task,.readiness-card{background:#fff!important;color:#17253c!important;border:1px solid #cbd5e1;box-shadow:0 3px 12px #17253c08}.handover-task h3,.handover-task p,.handover-task label,.readiness-card h3,.readiness-card p,.readiness-card li{color:#17253c!important}.handover-task a{color:#304bb8!important}.handover-task input,.handover-task textarea,.handover-task select,.handover-task option{background:#fff!important;color:#17253c!important;border:1px solid #8c9bb2}#handover-preview{white-space:pre-wrap;overflow-wrap:anywhere}.readiness-card{margin:18px 0;padding:24px}'

STYLE += '#runtime-review p,#runtime-review li{overflow-wrap:anywhere}#runtime-preview{padding:18px;border:2px solid #d29b32;border-radius:12px;background:#fff9ed}#runtime-results{border-left:4px solid #4058da;padding-left:18px}'
