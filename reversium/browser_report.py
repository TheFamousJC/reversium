"""Adapt a local analysis report for an isolated, network-disabled browser frame."""

import re

from .report import render
from .browser_ai import PANEL as BROWSER_AI, SCRIPT as BROWSER_AI_SCRIPT


from .assistant_ui import FAQ_AI

from .assistant_ui import PANEL as AI_PANEL, SCRIPT as AI_SCRIPT





def render_browser(report):

    page = browser_copy(render(report))

    page = page.replace('<section role="tabpanel" id="panel-assistant" aria-labelledby="tab-assistant" tabindex="0">' + AI_PANEL + '</section>', '<section role="tabpanel" id="panel-assistant" aria-labelledby="tab-assistant" tabindex="0">' + BROWSER_AI + '</section>')

    page = page.replace('AI assistant · optional', 'AI · choose provider')

    page = re.sub(r'<button data-guide="tab-assistant">.*?</button>', '', page)

    page = page.replace(AI_SCRIPT, '').replace('<!--assistant-session-->', '')

    page = re.sub(r'<a href="/">.*?</a>', '<button class="browser-reset">Clear and start again</button>', page)

    page = re.sub(r"function download\(text,type,name\)\{.*?\}\n", "function download(text,type,name){if(parent!==window){parent.postMessage({type:'reversium-download',text,mime:type,name},'*');return}const u=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)}\n", page, count=1)
    policy = "default-src 'none'; script-src 'unsafe-inline' blob:; style-src 'unsafe-inline'; img-src data: blob:; connect-src 'none'; form-action 'none'; base-uri 'none'"

    page = page.replace('<meta charset="utf-8">', '<meta charset="utf-8"><meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="' + policy + '">', 1)

    page = page.replace('</main>', '<p>Analyzed on your device. This report has no network access. Files are not uploaded. Optional cloud AI is not connected in this browser edition.</p></main>')

    reset = "document.querySelectorAll('.browser-reset').forEach(b=>b.onclick=()=>parent.postMessage({type:'reversium-clear'},'*'));"

    return page.replace('</html>', '<script>' + reset + BROWSER_AI_SCRIPT + '</script></html>')





def browser_copy(page):

    page = page.replace(FAQ_AI, '<p>This browser edition has no AI connection. All analysis uses local rules.</p>')

    page = re.sub(r'<p><b>Ask for an explanation.</b>.*?</p>', '<p><b>Keep analysis private.</b> This browser edition reads files on your device, with no AI connection or sign-in. Internet access is needed to load the application first.</p>', page)

    page = page.replace('Local analysis is free and open source; optional cloud AI follows your provider’s eligibility and usage limits.', 'Analysis is free and open source. This browser edition has no cloud AI connection.')

    page = page.replace('AI is optional. Connecting an account is not needed to read or save this report.', 'No account or AI connection is used in this browser edition.')

    page = page.replace('Optional AI shares only approved requests.', 'No files are uploaded and no AI requests are sent.')

    return page

