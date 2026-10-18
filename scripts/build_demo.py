"""Build public demo from fictional source only; never read local user archives."""
import io
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reversium.analyze import inspect_zip
from reversium.report import render
from reversium.assistant_ui import PANEL as AI_PANEL, SCRIPT as AI_SCRIPT
from reversium.presentation import STYLE
from reversium.branding import HEADER

SOURCE = {
    'package.json': json.dumps({'name': 'fictional-community-library', 'dependencies': {'react': '*', 'express': '*', '@supabase/supabase-js': '*'}}),
    'src/AddBook.tsx': '''export function AddBook({ onSave }) {
  function handleSubmit() { onSave(); }
  return <button onClick={handleSubmit}>Add sample book</button>;
}
''',
    'src/App.tsx': '''import { AddBook } from './AddBook';
export function App() {
  async function saveBook() {
    await fetch('/api/books', { method: 'POST', body: JSON.stringify({ title: 'Fictional book' }) });
  }
  return <AddBook onSave={saveBook} />;
}
''',
    'server.ts': '''import express from 'express';
import { createClient } from '@supabase/supabase-js';
const app = express();
const db = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);
app.post('/api/books', async (req, res) => {
  await db.from('books').insert({ title: req.body.title });
  res.json({ created: true });
});
''',
    'schema.sql': 'CREATE TABLE books (id integer primary key, title text);',
}


def main():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        for name, source in SOURCE.items():
            archive.writestr(name, source)
    buffer.seek(0)
    report = inspect_zip(buffer)
    report.update(example=True, archive_name='Fictional community library sample', user_goal='handover')
    page = render(report)
    page = page.replace('<section role="tabpanel" id="panel-assistant" aria-labelledby="tab-assistant" tabindex="0">' + AI_PANEL + '</section>', '')
    page = re.sub(r'<a role="tab"[^>]*id="tab-assistant"[^>]*>.*?</a>', '', page)
    page = re.sub(r'<button data-guide="tab-assistant">.*?</button>', '', page)
    page = page.replace(AI_SCRIPT, '')
    page = page.replace('<!--assistant-session-->', '').replace('href="/"', 'href="../"')
    page = page.replace('Start a new analysis', 'Back to demo start').replace('Start another analysis', 'Back to demo start')
    page = page.replace('Your file review is complete.', 'Explore a real analysis of fictional code.')
    page = page.replace('SAMPLE ANALYSIS · Fictional demonstration data. Start a new analysis to inspect your ZIP.', 'PUBLIC DEMO · Fictional community library. No upload, account connection or live AI in this hosted demo. Analyze your own ZIP in the browser from the home page.')
    page = page.replace('<title>Reversium report</title>', '<title>Interactive sample · Reversium demo</title>')
    page = page.replace('AI is optional. Connecting an account is not needed to read or save this report.', 'This hosted demo has no AI connection or upload service. The optional AI assistant is available in the local application.')
    output = ROOT / 'demo'
    output.mkdir(exist_ok=True)
    (output / 'report.html').write_text(page, encoding='utf-8')
    (ROOT / '.nojekyll').write_text('')
    landing = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta name="description" content="Try Reversium’s free interactive software handover demo. Explore fictional code findings, feature connections and evidence without installing anything."><title>Try Reversium · Free interactive demo</title><style>'''+STYLE+'''
main{max-width:1040px}.demo-hero{padding:42px 0 24px}.demo-hero h1{max-width:800px;font-size:clamp(38px,6vw,68px)}.demo-hero p{max-width:730px;font-size:18px}.cta{min-width:260px;text-align:center;font-size:22px;display:inline-block;background:#4058da;color:white;text-decoration:none;padding:24px 36px;border-radius:12px;font-weight:700}.preview{padding:25px;background:white;border:1px solid #dce4ef;border-radius:18px;margin:30px 0}.path{display:flex;gap:12px;flex-wrap:wrap;align-items:center}.path span{padding:12px;border-radius:10px;background:#edf1ff;color:#354dc4}footer{margin-top:45px}nav{display:flex;justify-content:space-between}.report-brand{display:flex;gap:12px;align-items:center}.report-brand img{width:44px;height:36px;object-fit:contain;background:#12213b;padding:8px;border-radius:8px}.entry-help{display:flex;gap:8px;flex-wrap:wrap}.help-button{display:inline-block;padding:12px 20px;border-radius:9px;background:#4058da;color:white;text-decoration:none;font-weight:700}nav{gap:16px;align-items:center;flex-wrap:wrap}.report-brand small{display:block;font-size:12px}</style><main>
<nav>'''+HEADER+'''<div class="entry-help"><a class="help-button" href="web/?help=guide">Help</a><a class="help-button" href="web/?help=faq">FAQ</a><a class="help-button" href="web/?help=about">About</a></div><a href="https://github.com/TheFamousJC/reversium">Open-source project ↗</a></nav>
<section class="demo-hero"><p class="brand">FREE · YOUR OWN ZIP · NO INSTALLATION</p><div style="display:inline-flex;background:#12213b;padding:24px;border-radius:20px"><img src="assets/3sci-logo.png" alt="3Sci" width="210" height="167" style="object-fit:contain"></div><h1>Reversium by 3Sci Labs</h1><p>Understand. Prepare. Develop.</p><p>See how Reversium turns a software package into findings, feature connections and questions a developer can investigate.</p><a class="cta" href="web/">Enter Reversium →</a> <a href="demo/report.html">Explore sample data</a><p><small>No sign-up. Your files stay on your device. Or explore the clearly labelled fictional sample.</small></p></section>
<section class="preview"><h2>Follow one simple feature</h2><p>Our fictional community library has an “Add book” action. Explore the supported source path and inspect what each connection can—and cannot—establish.</p><div class="path"><span>Screen</span> → <span>Save callback</span> → <span>POST /api/books</span> → <span>Books table</span></div><p>These are static code references, not proof of a working application.</p></section>
<p><a href="docs/market-position.html">Where Reversium fits: comparison and roadmap →</a></p><h2>Three things to try</h2><ol><li><a href="demo/report.html#panel-software">Read the owner-friendly overview.</a> Open “Why we say this” to inspect a source finding.</li><li><a href="demo/report.html#panel-architecture">Explore the feature map.</a> Follow the sample screen towards its API and database references.</li><li><a href="demo/report.html#panel-finish">Save a sample report.</a> Compare the readable HTML report with structured JSON findings and review the next-step checklist.</li></ol>
<section class="preview"><h2>Want to inspect your own ZIP?</h2><p>The browser version runs the analyzer on your device. Select your own ZIP, explore findings and diagrams, and save reports. No installation, file upload or AI account is needed. The browser limit is 32 MiB; larger packages can use the local application.</p><p><a href="https://github.com/TheFamousJC/reversium#run">Get the local version and setup instructions →</a></p></section>
<footer><p>Open Source · <a href="https://3Sci.com">3Sci.com</a> · 2026</p><p>No analytics or remote assets are added by this demo. GitHub Pages serves the site; your browser makes normal hosting requests.</p></footer></main></html>'''
    (ROOT / 'index.html').write_text(landing, encoding='utf-8')
    print('Built public sample demo from', len(SOURCE), 'fictional files;', len(report['findings']), 'findings.')


if __name__ == '__main__':
    main()
