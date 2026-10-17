"""Package the current analyzer, not user data, for the public browser edition."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reversium import __version__
from reversium.report import STYLE
from reversium.presentation import STYLE as MODERN
from reversium.start_ui import render_start
from reversium.browser_report import browser_copy


def main():
    web = ROOT / 'web'
    web.mkdir(exist_ok=True)
    with zipfile.ZipFile(web / 'engine.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for file in sorted((ROOT / 'reversium').glob('*.py')):
            if file.name != '__main__.py':
                z.write(file, 'reversium/' + file.name)
    data = (web / 'engine.zip').read_bytes()
    (web / 'engine.json').write_text(json.dumps({'version': __version__, 'sha256': hashlib.sha256(data).hexdigest()}))
    start = browser_copy(render_start(STYLE + MODERN, ''))
    # Preserve the guided content but replace its server upload script entirely.
    start = start[:start.index('<script>')]
    start = start.replace('<title>Start · Reversium</title>', '<title>Reversium · Analyze your ZIP in your browser</title><meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="default-src \'self\'; script-src \'self\' \'unsafe-inline\'; worker-src \'self\'; style-src \'unsafe-inline\'; connect-src \'self\'; frame-src \'self\' about:; object-src \'none\'; base-uri \'none\'">')
    start = start.replace('Software ZIP (maximum 64 MiB)', 'Software ZIP (maximum 32 MiB in the browser)')
    start = start.replace('No report exists yet.', 'No report exists yet. Your file stays on this device.')
    start = start.replace('a small fictional contact application, not your software.', 'a fictional community library, not your software.')
    start = start.replace('href="/example-js"', 'href="../demo/report.html"')
    privacy = '''<details class="privacy"><summary>How are my files handled?</summary><p><b>Your ZIP is not uploaded.</b> The analyzer runs in a worker in your browser. GitHub Pages serves the application and Python runtime, not your software. Normal hosting requests expose connection information such as your IP address; they do not include ZIP contents.</p><p>Your file and generated report are held in this page’s memory. Nothing is written to localStorage, IndexedDB or our server. Clear and start again or close the page to release the app’s references; this is not a secure-memory-erasure guarantee. Reports you download remain wherever you save them.</p><p>The browser may cache application/runtime files. No analytics, third-party assets, account sign-in or AI calls are included in this browser edition. The report frame is sandboxed and network-disabled. Do not run modified copies from sites you do not trust.</p><p>Browser limit: 32 MiB ZIP; the existing archive safety and inspection bounds still apply. Large archives can exceed your device’s memory. Cancel stops the worker. Selected code is read, never executed. Optional ChatGPT assistance remains available only in the local application.</p></details>'''
    start = start.replace('<p id="start-step"', privacy + '<p id="start-step"')
    start += '''<section id="browser-progress" hidden><h2>Analyzing on your device</h2><p id="browser-message" role="status">Preparing…</p><button id="browser-cancel">Cancel and clear</button></section><section id="browser-results" hidden><nav><button id="browser-clear">Clear and start again</button><span>Your ZIP was analyzed here, not uploaded.</span></nav><iframe id="browser-report" title="Your Reversium analysis" sandbox="allow-scripts allow-downloads" style="width:100%;height:85vh;border:1px solid #dce4ef;border-radius:12px;background:white"></iframe></section><script type="module" src="app.js"></script></html>'''
    (web / 'index.html').write_text(start, encoding='utf-8')
    print('Packaged browser analyzer', __version__, len(data), 'bytes')


if __name__ == '__main__':
    main()
