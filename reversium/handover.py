"""Names-only setup clues and evidence-linked handover actions; never run commands."""
import json
import re
from pathlib import PurePosixPath
TEMPLATES={'.env.example','.env.sample','.env.template'}


def setup_details(source,name,finding):
    template=PurePosixPath(name).name in TEMPLATES
    for line,text in enumerate(source.splitlines(),1):
        patterns=[r"\bprocess\.env\.([A-Za-z_][A-Za-z0-9_]*)",r"\bimport\.meta\.env\.([A-Za-z_][A-Za-z0-9_]*)",r"\bos\.(?:getenv|environ\.get)\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]",r"\b(?:process\.env|os\.environ)\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*\]"]
        names={match.group(1) for pattern in patterns for match in re.finditer(pattern,text)}
        for value in sorted(names):finding('environment_name_candidate',value,name,line,'heuristic')
        if template:
            match=re.match(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=',text)
            if match:finding('environment_template_name',match[1],name,line,'observed')
    if PurePosixPath(name).name=='package.json':
        try:data=json.loads(source)
        except (ValueError,RecursionError):return
        if not isinstance(data,dict):return
        scripts=data.get('scripts',{})
        if isinstance(scripts,dict):
            start=source.find('"scripts"')
            for key in list(scripts)[:80]:
                if not isinstance(key,str) or not re.fullmatch(r'[A-Za-z0-9_:.\-]{1,80}',key):continue
                match=re.search(re.escape(json.dumps(key))+r'\s*:',source[max(0,start):])
                line=source[:max(0,start)+(match.start() if match else 0)].count('\n')+1
                finding('project_script_name',key,name,line,'observed')
        engines=data.get('engines',{})
        if isinstance(engines,dict):
            for key,value in engines.items():
                if key in {'node','npm','yarn','pnpm'} and isinstance(value,str) and re.fullmatch(r'[0-9vxX.*^~<>=| \-]{1,80}',value):finding('runtime_constraint_candidate',key+': '+value,name,1,'manifest declaration')


def build_handover(report):
    grouped={}
    for i,f in enumerate(report['findings']):
        if f['kind'] in {'environment_name_candidate','environment_template_name','project_script_name','runtime_constraint_candidate'}:
            key=('environment' if f['kind'].startswith('environment_') else f['kind'],f['value'])
            grouped.setdefault(key,[]).append(i)
    clues=[{'kind':kind,'name':name,'evidence_indices':indices} for (kind,name),indices in sorted(grouped.items())]
    templates={f['value'] for f in report['findings'] if f['kind']=='environment_template_name'}
    for item in clues:
        if item['kind']=='environment':item['template_name_found']=item['name'] in templates
    service_locations=[x['evidence'] for x in report.get('platform',{}).get('supporting_services',[])]
    service_indices=[i for i,f in enumerate(report['findings']) if f['evidence'] in service_locations][:20]
    tasks=[{'id':'workflow','title':'Agree on one user workflow and expected result','check':'Verify it in a separate environment using disposable data.','evidence_indices':[]},
           {'id':'runtime','title':'Confirm runtimes and dependency installation','check':'Review version constraints and lockfiles; do not execute unreviewed scripts.','evidence_indices':[i for item in clues if item['kind']=='runtime_constraint_candidate' for i in item['evidence_indices']][:20]},
           {'id':'configuration','title':'Confirm configuration names and obtain values securely','check':'Names are clues, not proof they are required. Never put passwords or keys in this checklist.','evidence_indices':[i for item in clues if item['kind']=='environment' for i in item['evidence_indices']][:20]},
           {'id':'services','title':'Confirm supporting services, permissions and sample data','check':'Check database migrations, authentication, storage and optional integrations with the developer.','evidence_indices':service_indices},
           {'id':'run','title':'Review build/start/test instructions and record an isolated result','check':'Script names do not establish safe commands or successful setup. Record failures and unresolved questions.','evidence_indices':[i for item in clues if item['kind']=='project_script_name' for i in item['evidence_indices']][:20]}]
    return {'clues':clues[:240],'omitted_clues':max(0,len(clues)-240),'tasks':tasks,'scope':'Names and declared constraints only. Values and script commands are not retained by this reader. No setup or runtime validation performed.'}
