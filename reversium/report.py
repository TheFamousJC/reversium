import html
import json


def render(report):
    esc = lambda value: html.escape(str(value), quote=True)
    findings = report['findings']
    # Diagram edges represent observed mentions, not proven runtime calls.
    pairs = list(dict.fromkeys((f['evidence']['file'], f['value']) for f in findings if f['kind'] in {'import', 'dependency'}))[:100]
    height = max(90, len(pairs) * 46 + 30)
    diagram = [f'<svg viewBox="0 0 1000 {height}" role="img" aria-label="File to import and dependency mentions">']
    for index, (origin, target) in enumerate(pairs):
        y = 35 + index * 46
        diagram.append(f'<path d="M450 {y} H550" stroke="#66d9c2"/><text x="10" y="{y}" fill="#e8edf5">{esc(origin[:55])}</text><text x="560" y="{y}" fill="#66d9c2">{esc(target[:55])}</text>')
    diagram.append('</svg>')
    rows = ''.join(f'<tr><td>{esc(f["kind"])}</td><td>{esc(f["value"])}</td><td>{esc(f["evidence"]["file"])}:{f["evidence"]["line"]}</td><td>{esc(f["confidence"])}</td></tr>' for f in findings)
    files = ''.join(f'<tr><td>{esc(f["path"])}</td><td>{esc(f["language"] or f["category"])}</td><td>{f["bytes"]}</td></tr>' for f in report['files'])
    notes = ''.join(f'<li>{esc(x)}</li>' for x in report['warnings'] + report['limitations'])
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Reversium report</title><style>{STYLE}</style><main><p class="brand">REVERSIUM / LOCAL ANALYSIS</p><h1>Understand what’s inside.</h1><p>{esc(report['scope'])}</p><div class="cards">{''.join(f'<article><strong>{esc(v)}</strong><span>{esc(k.replace("_", " "))}</span></article>' for k,v in report['summary'].items() if k != 'languages')}</div><h2>Architecture: import and dependency mentions</h2><p>File → referenced module/package. External and internal references are not resolved. First 100 unique edges; full evidence is below.</p>{''.join(diagram) if pairs else '<p>No supported dependency references found.</p>'}<h2>Evidence</h2><div class="scroll"><table><tr><th>Finding</th><th>Value</th><th>Location</th><th>Confidence</th></tr>{rows}</table></div><h2>Inventory</h2><div class="scroll"><table><tr><th>File</th><th>Type</th><th>Bytes</th></tr>{files}</table></div><h2>Coverage and limitations</h2><ul>{notes}</ul><p>Generated locally by Reversium 0.1.0. No paid services or remote assets.</p></main></html>'''


STYLE = 'body{margin:0;background:#101823;color:#e8edf5;font:16px system-ui}main{max-width:1180px;margin:60px auto;padding:0 28px}.brand{color:#66d9c2;letter-spacing:3px;font-size:12px}h1{font-size:48px;letter-spacing:-2px}h2{margin-top:45px}p,li{color:#afbdce;line-height:1.7}.cards{display:flex;gap:14px;flex-wrap:wrap}article{padding:24px;background:#1c2838;border-radius:12px;min-width:130px}strong{display:block;font-size:30px}span{color:#afbdce}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:12px;border-bottom:1px solid #304056;overflow-wrap:anywhere}.scroll{overflow:auto}svg{width:100%;min-width:650px;background:#162130;border-radius:12px}button{background:#66d9c2;color:#101823;border:0;border-radius:8px;padding:14px 24px;font-weight:700;cursor:pointer}input{padding:20px}a{color:#66d9c2}'
