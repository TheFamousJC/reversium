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
from reversium.user_guide import SCRIPT as GUIDE_SCRIPT


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
    start = start.replace('No sign-in is required; AI is optional.', 'No sign-in is required. Optional AI handoff is available after analysis; no account is connected here.')
    start = start.replace('<main>', '<main id="app-content" hidden>', 1)
    splash = '<section id="splash" class="splash"><nav class="entry-help" aria-label="Welcome help"><button type="button" data-entry-panel="start-guide">Help</button><button type="button" data-entry-panel="start-faq">FAQ</button><button type="button" data-entry-panel="start-about">About</button></nav><div class="logo-panel"><img src="../assets/3sci-logo.png" alt="3Sci" width="210" height="167"></div><p class="brand">FREE · PRIVATE · NO INSTALLATION</p><h1>Reversium by 3Sci Labs</h1><p class="tagline">Understand. Prepare. Develop.</p><p>Turn unfamiliar software into evidence, feature connections and a clearer next step.</p><button id="enter-app">Start exploring →</button><p><small>Your ZIP stays on your device. No account required.</small></p></section>'
    start = start.replace('<main id="app-content" hidden>', splash + '<main id="app-content" hidden>', 1)
    start = start.replace('</style>', '.splash{max-width:850px;margin:60px auto;padding:32px;text-align:center}.logo-panel{display:inline-flex;background:#12213b;border-radius:22px;padding:26px;margin-bottom:22px}.logo-panel img{object-fit:contain}.splash h1{font-size:clamp(32px,6vw,60px)}.tagline{font-size:24px;color:#4058da}.splash #enter-app{margin-top:18px;min-width:280px;min-height:70px;font-size:22px;padding:22px 38px}.entry-help{justify-content:center;margin-bottom:28px}.entry-help button{padding:12px 22px;font-size:16px;min-width:90px}.site-brand{display:flex;align-items:center;gap:16px}.site-brand img{background:#12213b;padding:8px;border-radius:12px;width:64px;height:auto}</style>', 1)
    start = start.replace('<p class="brand">REVERSIUM', '<div class="site-brand"><img src="../assets/3sci-logo.png" alt="3Sci"><p class="brand">REVERSIUM', 1).replace('· LOCAL &amp; FREE</p>', '· LOCAL &amp; FREE</p></div>', 1)
    start = start.replace('<nav aria-label="Help">', '<nav aria-label="Help"><button type="button" data-help-panel="browser-ai">Where is AI?</button>')
    start = start.replace('<section id="start-about"', '<section id="browser-ai" hidden><h2>Where is the AI assistant?</h2><p>After analysis, open AI · choose provider to prepare selected evidence for ChatGPT or another AI. This is a manual handoff, not an embedded connection. The local application also offers the existing optional account connection. Your ChatGPT sign-in does not automatically connect to this hosted website.</p><p>Browser analysis uses local rules and needs no account or AI service. For optional AI, use the local application, connect an eligible account and review the evidence before sending it. Provider access and usage limits apply.</p><a href="../docs/user-guide.html" target="_blank" rel="noopener noreferrer">Local application instructions</a></section><section id="start-about"',1)

    start = start.replace('<title>Start · Reversium</title>', '<title>Reversium · Analyze your ZIP in your browser</title><meta name="description" content="Understand your software ZIP with local code analysis, feature maps and evidence-backed handover reports. Free to use, with no installation."><meta property="og:type" content="website"><meta property="og:title" content="Reversium by 3Sci Labs · Understand your software"><meta property="og:description" content="Understand your software ZIP with local code analysis, feature maps and evidence-backed handover reports. Free to use, with no installation."><meta name="twitter:card" content="summary"><meta name="twitter:title" content="Reversium by 3Sci Labs · Understand your software"><meta name="twitter:description" content="Understand your software ZIP with local code analysis, feature maps and evidence-backed handover reports. Free to use, with no installation."><meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="default-src \'self\'; img-src \'self\' data:; script-src \'self\' \'unsafe-inline\'; worker-src \'self\'; style-src \'unsafe-inline\'; connect-src \'self\'; frame-src \'self\' about:; object-src \'none\'; base-uri \'none\'">')
    start = start.replace('Software ZIP (maximum 64 MiB)', 'Software ZIP (maximum 32 MiB in the browser)')
    start = start.replace('No report exists yet.', 'No report exists yet. Your file stays on this device.')
    start = start.replace('a sample contact application, not your software.', 'a sample community-library project, not your software.')
    start = start.replace('href="/example-js"', 'href="../demo/report.html"')
    privacy = '''<details class="privacy"><summary>How are my files handled?</summary><p><b>Your ZIP is not uploaded.</b> The analyzer runs in a worker in your browser. The hosting provider serves the application and Python runtime, not your software. Normal hosting requests expose connection information such as your IP address; they do not include ZIP contents.</p><p>Your file and generated report are held in this page’s memory. Nothing is written to localStorage, IndexedDB or our server. Clear and start again or close the page to release the app’s references; this is not a secure-memory-erasure guarantee. Reports you download remain wherever you save them.</p><p>The browser may cache application/runtime files. No analytics, third-party assets, account sign-in or AI calls are included in this browser edition. The report frame is sandboxed and network-disabled. Do not run modified copies from sites you do not trust.</p><p>Browser limit: 32 MiB ZIP; the existing archive safety and inspection bounds still apply. Large archives can exceed your device’s memory. Cancel stops the worker. Selected code is read, never executed. Optional ChatGPT assistance remains available only in the local application.</p></details>'''
    start = start.replace('<p id="start-step"', privacy + '<p id="start-step"')
    start += '<script>' + GUIDE_SCRIPT + '</script>'
    start += '''<section id="browser-progress" hidden><h2>Analyzing on your device</h2><p id="browser-message" role="status">Preparing…</p><button id="browser-cancel">Cancel and clear</button></section><section id="browser-results" hidden><nav><button id="browser-clear">Clear and start again</button><span>Your ZIP was analyzed here, not uploaded.</span></nav><iframe id="browser-report" title="Your Reversium analysis" sandbox="allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox" style="width:100%;height:85vh;border:1px solid #dce4ef;border-radius:12px;background:white"></iframe></section><script type="module" src="app.js?v=BUILD_VERSION"></script></html>'''
    (web / 'index.html').write_text(start.replace('BUILD_VERSION', __version__), encoding='utf-8')
    print('Packaged browser analyzer', __version__, len(data), 'bytes')


if __name__ == '__main__':
    main()
