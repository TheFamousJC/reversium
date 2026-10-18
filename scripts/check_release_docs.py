"""Release gate for generated Help, PDF and browser guide consistency (stdlib only)."""
import base64
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from reversium import __version__
from reversium.user_guide import GUIDE, GUIDE_VERSION, SCRIPT


def check():
    problems=[]
    if GUIDE_VERSION!=__version__:problems.append('Rebuild Help: guide version differs from application.')
    page=(ROOT/'docs/user-guide.html').read_text(encoding='utf-8')
    if GUIDE not in page or SCRIPT not in page:problems.append('Standalone Help differs from embedded Help.')
    encoded=re.search(r"const encoded='([A-Za-z0-9+/=]+)'",SCRIPT)
    if not encoded or base64.b64decode(encoded.group(1))!=(ROOT/'output/pdf/Reversium-User-Guide.pdf').read_bytes():
        problems.append('Downloadable PDF differs from the embedded guide PDF.')
    if 'id="guide-search"' not in GUIDE or 'id="guide-search-status"' not in GUIDE:
        problems.append('Search controls missing from Help.')
    meta=json.loads((ROOT/'web/engine.json').read_text())
    engine=ROOT/'web/engine.zip'
    if meta.get('version')!=__version__ or hashlib.sha256(engine.read_bytes()).hexdigest()!=meta.get('sha256'):
        problems.append('Browser analyzer metadata is stale.')
    with zipfile.ZipFile(engine) as z:
        if z.read('reversium/user_guide.py').decode('utf-8').replace('\r\n','\n')!=(ROOT/'reversium/user_guide.py').read_text(encoding='utf-8'):
            problems.append('Browser analyzer contains a stale guide.')
    # Product copy only: dependency licence notices and vendor assets are preserved.
    targets=[ROOT/'README.md',ROOT/'CONTRIBUTING.md',ROOT/'index.html',ROOT/'demo/report.html',ROOT/'web/index.html',ROOT/'web/README.md']
    targets+=list((ROOT/'docs').glob('*'))+list((ROOT/'reversium').glob('*.py'))
    forbidden=re.compile(r'open[ -]source|github\.(?:com|io)',re.I)
    for target in targets:
        if target.is_file() and target.suffix in ('.md','.txt','.html','.py') and forbidden.search(target.read_text(encoding='utf-8')):
            problems.append('Retired product wording or source-hosting link: '+target.relative_to(ROOT).as_posix())
    return problems


if __name__=='__main__':
    problems=check()
    if problems:
        print('\n'.join(problems));raise SystemExit(1)
    print('Release documentation matches Reversium '+__version__+'; embedded/PDF/browser guides agree.')
