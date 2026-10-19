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


def asset_hash(path):
    data=path.read_bytes()
    if path.suffix in ('.json','.html','.svg'):data=data.replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest()


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
    catalog=ROOT/'docs/product-catalog.json'
    manifest=json.loads((ROOT/'docs/product-docs-manifest.json').read_text(encoding='utf-8'))
    product=json.loads(catalog.read_text(encoding='utf-8'))
    if manifest.get('version')!=__version__ or manifest.get('catalog_sha256')!=asset_hash(catalog):
        problems.append('Feature/journey catalog is stale: rebuild Help after reviewing the catalog.')
    required={'output/pdf/Reversium-Feature-List.pdf','output/pdf/Reversium-User-Journeys.pdf','docs/user-journeys.html'}
    required.update('docs/journeys/'+j['id']+'.svg' for j in product['journeys'])
    if len(product['journeys'])!=7 or set(manifest.get('artifacts',{}))!=required:
        problems.append('Feature/journey artifact inventory must include seven diagrams and both PDFs.')
    for name in required:
        asset=ROOT/name
        if not asset.is_file() or asset_hash(asset)!=manifest.get('artifacts',{}).get(name):
            problems.append('Stale or missing product documentation: '+name)
    for button,name in [('feature-pdf','Reversium-Feature-List.pdf'),('journeys-pdf','Reversium-User-Journeys.pdf')]:
        match=re.search(r"querySelector\('#"+button+r"'\).*?const encoded='([A-Za-z0-9+/=]+)'",SCRIPT)
        if not match or base64.b64decode(match.group(1))!=(ROOT/'output/pdf'/name).read_bytes():
            problems.append('Help download differs from generated documentation: '+name)
        if name not in (ROOT/'web/app.js').read_text(encoding='utf-8'):
            problems.append('Browser download broker is missing '+name)
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
    general=[ROOT/'README.md',ROOT/'CONTRIBUTING.md',ROOT/'web/index.html',ROOT/'demo/report.html']+list((ROOT/'docs').rglob('*'))
    for target in general:
        if target.is_file() and target.suffix in ('.md','.txt','.html','.json','.svg'):
            content=target.read_text(encoding='utf-8')
            # Stable internal import/profile IDs in executable code are not documentation.
            if target.suffix=='.html':content=re.sub(r'<script\b[^>]*>.*?</script>', '',content,flags=re.I|re.S)
            if re.search(r'tudela',content,re.I):
                problems.append('Project-specific name remains in general documentation: '+target.relative_to(ROOT).as_posix())
    if re.search(r'tudela',GUIDE,re.I):problems.append('Project-specific name remains in embedded Help.')
    return problems


if __name__=='__main__':
    problems=check()
    if problems:
        print('\n'.join(problems));raise SystemExit(1)
    print('Release documentation matches Reversium '+__version__+'; embedded/PDF/browser guides agree.')
