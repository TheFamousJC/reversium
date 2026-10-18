"""Inventory-backed setup questions, never an automatic execution plan."""
import html
from pathlib import PurePosixPath


def build_readiness(report):
    files = report['files']
    groups = [
        ('Runtime declarations', lambda p: p.name in {'package.json','pyproject.toml','requirements.txt','pom.xml','global.json','.nvmrc','.python-version'}, 'Confirm exact runtime versions and OS compatibility.'),
        ('Reproducible dependencies', lambda p: p.name in {'package-lock.json','pnpm-lock.yaml','yarn.lock','uv.lock','poetry.lock','Pipfile.lock','Cargo.lock','go.sum'}, 'Review lockfile, installation hooks and offline dependency availability; do not install automatically.'),
        ('Configuration templates', lambda p: p.name in {'.env.example','.env.sample','.env.template'}, 'Obtain synthetic values securely. A template does not establish that all required names are present.'),
        ('Database migrations and seed data', lambda p: p.suffix == '.sql' or any(x in p.parts for x in ('migrations','seeds')), 'Review schema, migration order, permissions and disposable seed data. Files may be unused.'),
        ('Build, start and test clues', lambda p: p.name == 'package.json' or 'test' in p.name.lower() or p.name in {'Makefile','pytest.ini'}, 'Confirm documented commands, successful build, startup and health checks in isolation.'),
        ('Deployment and container clues', lambda p: p.name.startswith('Dockerfile') or p.name in {'compose.yaml','compose.yml','docker-compose.yml','docker-compose.yaml'}, 'Review images, ports and volumes. A container definition is not an untrusted-code sandbox.'),
        ('Backup and recovery clues', lambda p: any(x in p.name.lower() for x in ('backup','restore','recovery')), 'Test backup and restore using disposable services; filenames do not establish a working recovery process.'),
        ('Monitoring and operations clues', lambda p: any(x in p.name.lower() for x in ('monitor','health','load-test','runbook')), 'Confirm health checks, logs, alerting and load expectations. Operational success remains unverified.'),
    ]
    return {'scope':'Static setup clues, not a readiness score. Found means matching inventory names only; missing means no matching names in this ZIP, not proof of an absent capability.',
            'checks':[{'title':title,'files':[f['path'] for f in files if match(PurePosixPath(f['path']))], 'next_step':step} for title,match,step in groups]}


def panel(report):
    esc=lambda s:html.escape(str(s),quote=True)
    data=report.get('readiness_plan') or build_readiness(report)
    cards=[]
    for check in data['checks']:
        paths=check['files']
        cards.append('<article class="readiness-card"><h3>'+esc(check['title'])+'</h3><p><b>'+('Clues found: '+str(len(paths)) if paths else 'No filename clues found')+'</b> · Not runtime verified</p><p>'+esc(check['next_step'])+'</p><details><summary>Inventory evidence ('+str(len(paths))+')</summary><ul>'+''.join('<li>'+esc(p)+' — inventory name only</li>' for p in paths[:30])+'</ul>'+('<p>'+str(len(paths)-30)+' further names in report JSON.</p>' if len(paths)>30 else '')+'</details></article>')
    return '<h2>Setup &amp; readiness: a practical review plan</h2><p>'+esc(data['scope'])+'</p><button id="readiness-save">Save setup review plan</button>'+''.join(cards)+'<p><a href="https://thefamousjc.github.io/reversium/docs/market-position.html" target="_blank" rel="noopener noreferrer">Market comparison and missing features</a> — next candidates include local scanner-result import, offline dependency advisories and standard SBOM support. These are planned, not currently implemented.</p><h2>Zero-cost sandbox preparation</h2><p>General-purpose ZIP execution is not available in the browser. The local CLI can check backend availability and create offline starter profiles: <code>python -m reversium --sandbox-plan reports/sandbox-draft</code>. This prepares files only; it does not boot a VM or run software.</p><p>Experimental Windows QEMU pilot: prepare verified assets with <code>python scripts/bootstrap_qemu_lab.py</code>, prepare public offline dependencies with <code>python scripts/prepare_tudela_offline.py PROJECT.zip</code>, then use <code>python -m reversium --sandbox-self-test</code>. The explicit <code>--sandbox-tudela PROJECT.zip</code> action retests isolation before a separate, fixed build/start experiment. It is not a general ZIP runner. Private source-bearing media and logs stay in the ignored lab folder. See Help before use.</p><button id="sandbox-status">Check local sandbox prerequisites</button><p id="sandbox-status-result" role="status">Available only in the local Reversium server; the online edition cannot inspect your host. Windows Sandbox requires a supported edition; QEMU with a trusted Linux guest is a free alternative to investigate. The CLI pilot downloads a pinned guest and retests isolation before application input.</p>'


SCRIPT=r"""
document.querySelector('#readiness-save').onclick=()=>{const report=JSON.parse(document.querySelector('#report-data').textContent),plan=report.readiness_plan;if(!plan)return;download('Reversium setup review\n'+plan.scope+'\n\n'+plan.checks.map(c=>c.title+'\n'+c.next_step+'\nInventory only: '+(c.files.join('\n')||'No filename clues found')).join('\n\n'),'text/plain','reversium-readiness.txt');};
const sandboxButton=document.querySelector('#sandbox-status');if(parent!==window||location.hostname!=='127.0.0.1'){sandboxButton.disabled=true;}else sandboxButton.onclick=async()=>{const status=document.querySelector('#sandbox-status-result');try{const r=await fetch('/sandbox/status');if(!r.ok)throw Error();const d=await r.json();status.textContent=d.summary+' This button did not start a VM. A stored check result does not validate this delivery.';}catch{status.textContent='Local prerequisite check unavailable. Use python -m reversium --sandbox-check in the local installation.';}};
"""
