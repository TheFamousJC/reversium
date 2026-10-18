"""Host-side download/cache preparation only. Never install project packages here.

Public dependency identifiers are requested from Alpine/npm. ZIP/source content
is not uploaded. The guest remains offline; APK signatures are checked there.
"""
import argparse
import base64
import concurrent.futures
import hashlib
import io
import json
import re
import sys
import tarfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reversium.analyze import inspect_zip


def download(url,limit):
    request=urllib.request.Request(url,headers={'User-Agent':'Reversium-offline-provisioning'})
    with urllib.request.urlopen(request,timeout=90) as response:
        if urllib.parse.urlsplit(response.url).hostname!=urllib.parse.urlsplit(url).hostname:
            raise ValueError('Cross-host download redirect requires review.')
        data=response.read(limit+1)
    if len(data)>limit:raise ValueError('Provisioning download exceeds limit.')
    return data


def compatible(values,target):
    if not values:return True
    if not isinstance(values,list) or any(not isinstance(x,str) for x in values):raise ValueError('Invalid platform metadata.')
    positive=[x for x in values if not x.startswith('!')]
    return '!'+target not in values and (not positive or target in positive)


def npm_entries(lock):
    packages=lock.get('packages',{})
    if not isinstance(packages,dict) or len(packages)>2000:raise ValueError('Unsupported lockfile size/structure.')
    excluded=[path for path,p in packages.items() if not all(compatible(p.get(k),target) for k,target in [('os','linux'),('cpu','x64'),('libc','musl')])]
    result=[]
    for path,p in packages.items():
        if not path or any(path==x or path.startswith(x+'/') for x in excluded):continue
        if not path.startswith('node_modules/') or '..' in path.split('/') or p.get('link'):raise ValueError('Unsupported lock path or link.')
        url=p.get('resolved','');u=urllib.parse.urlsplit(url)
        if u.scheme!='https' or u.hostname!='registry.npmjs.org' or u.username or u.password or u.port not in (None,443):raise ValueError('Non-registry dependency requires review.')
        sri=p.get('integrity','').split()[0] if p.get('integrity') else ''
        if not sri.startswith(('sha512-','sha256-')):raise ValueError('Missing supported dependency integrity.')
        result.append({'path':path,'url':url,'integrity':sri})
    return result


def prepare_node(lab, extra_roots=(), directory="node-packages"):
    root=lab/directory;root.mkdir(exist_ok=True)
    packages={};providers={}
    for repo in ('main','community'):
        base='https://dl-cdn.alpinelinux.org/alpine/v3.23/'+repo+'/x86_64/'
        raw=download(base+'APKINDEX.tar.gz',10*1024*1024)
        with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:
            member=t.getmember('APKINDEX')
            if member.size>32*1024*1024:raise ValueError('APK index exceeds limit.')
            text=t.extractfile(member).read().decode()
        for block in text.split('\n\n'):
            info=dict(line.split(':',1) for line in block.splitlines() if ':' in line)
            if 'P' not in info:continue
            info['base']=base;packages[info['P']]=info
            for provided in info.get('p','').split():providers.setdefault(re.split(r'[=<>~]',provided)[0],info['P'])
    needed={};pending=['nodejs','npm','openssl',*extra_roots]
    while pending:
        name=pending.pop()
        if name in needed:continue
        if len(needed)>=80:raise ValueError('Runtime dependency count exceeds bound.')
        p=packages[name];needed[name]=p
        for dependency in p.get('D','').split():
            if dependency.startswith('!'):continue
            dep=re.split(r'[=<>~]',dependency)[0]
            selected=dep if dep in packages else providers.get(dep)
            if not selected:raise ValueError('Unresolved runtime dependency.')
            if selected not in needed:pending.append(selected)
    def fetch(p):
        name=p['P']+'-'+p['V']+'.apk'
        if not re.fullmatch(r'[A-Za-z0-9_.+~-]+\.apk',name):raise ValueError('Unsupported runtime package name.')
        data=download(p['base']+name,50*1024*1024);(root/name).write_bytes(data)
        return {'name':name,'url':p['base']+name,'sha256':hashlib.sha256(data).hexdigest()}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:result=list(pool.map(fetch,needed.values()))
    (root/'manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return len(result)


def prepare_npm(lab,lock):
    root=lab/'npm-packages';root.mkdir(exist_ok=True)
    entries=npm_entries(lock);unique={e['integrity']:e for e in entries}
    def fetch(e):
        name='pkg'+str(int(hashlib.sha256(e['integrity'].encode()).hexdigest()[:16],16))+'.tgz'
        target=root/name
        data=target.read_bytes() if target.exists() else download(e['url'],128*1024*1024)
        algorithm,expected=e['integrity'].split('-',1)
        if base64.b64encode(hashlib.new(algorithm,data).digest()).decode()!=expected:raise ValueError('Public npm tarball integrity mismatch.')
        target.write_bytes(data)
        return e['integrity'],name
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:files=dict(pool.map(fetch,unique.values()))
    for e in entries:e['file']=files[e['integrity']]
    if sum((root/name).stat().st_size for name in set(files.values()))>200*1024*1024:raise ValueError('npm input bundle exceeds 200 MiB.')
    (root/'manifest.json').write_text(json.dumps(entries,indent=2),encoding='utf-8')
    return len(entries)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive');parser.add_argument('--lab',default='reports/qemu-lab')
    args=parser.parse_args()
    report=inspect_zip(args.archive)
    if report['file_review']['counts']['red']:parser.error('Review red signals before runtime provisioning.')
    with zipfile.ZipFile(args.archive) as z:
        locks=[n for n in z.namelist() if n.endswith('/package-lock.json') or n=='package-lock.json']
        if len(locks)!=1:parser.error('Pilot requires one npm lockfile.')
        lock=json.loads(z.read(locks[0]))
    lab=Path(args.lab).resolve();lab.mkdir(parents=True,exist_ok=True)
    print('Preparing public dependency caches on the host. No project scripts are executed.',flush=True)
    node=prepare_node(lab);npm=prepare_npm(lab,lock)
    print(f'Prepared {node} runtime APKs and {npm} compatible locked npm entries. Guest installation must retain APK signature checks.')


if __name__=='__main__':main()
