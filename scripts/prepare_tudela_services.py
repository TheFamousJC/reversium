"""Cache official pinned services; no guest or application code runs on this host."""
import argparse,hashlib,json,sys,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reversium.service_inputs import PINNED
from scripts.prepare_tudela_offline import prepare_node

STORAGE_MANIFEST='sha256:1c3a04916ee78fdadb833e942ea8274caf081f88f5ed4fe022cd0f636cf82b6f'
RELEASES={'auth.tar.xz':'https://github.com/supabase/auth/releases/download/v2.197.0/auth-v2.197.0-amd64.tar.xz','postgrest.tar.xz':'https://github.com/PostgREST/postgrest/releases/download/v16.4/postgrest-v16.4-linux-static-x86-64.tar.xz'}


def cache(root,name,url,headers=None):
    target=root/name
    if target.exists():
        if target.stat().st_size>160*1024*1024:raise ValueError('Cached service asset exceeds bound.')
        if hashlib.sha256(target.read_bytes()).hexdigest()!=PINNED[name]:raise ValueError('Cached service checksum mismatch: '+name)
        return
    partial=target.with_suffix('.partial')
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers or {'User-Agent':'Reversium-offline-provisioning'}),timeout=90) as response,partial.open('wb') as output:
        size=0;digest=hashlib.sha256()
        while chunk:=response.read(1024*1024):
            size+=len(chunk)
            if size>160*1024*1024:raise ValueError('Service artifact exceeds bound.')
            digest.update(chunk);output.write(chunk)
    if digest.hexdigest()!=PINNED[name]:raise ValueError('Publisher/image artifact checksum mismatch: '+name)
    partial.replace(target)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--lab',default='reports/qemu-lab');args=parser.parse_args()
    lab=Path(args.lab).resolve();root=lab/'services';root.mkdir(parents=True,exist_ok=True)
    for name,url in RELEASES.items():cache(root,name,url)
    repo='supabase/storage-api';base='https://registry-1.docker.io/v2/'+repo+'/'
    with urllib.request.urlopen('https://auth.docker.io/token?service=registry.docker.io&scope=repository:'+repo+':pull',timeout=30) as response:token=json.load(response)['token']
    headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json'}
    with urllib.request.urlopen(urllib.request.Request(base+'manifests/'+STORAGE_MANIFEST,headers=headers),timeout=30) as response:raw=response.read(1024*1024+1)
    if len(raw)>1024*1024 or 'sha256:'+hashlib.sha256(raw).hexdigest()!=STORAGE_MANIFEST:raise ValueError('Storage image manifest mismatch.')
    manifest=json.loads(raw)
    if len(manifest['layers'])!=14:raise ValueError('Unexpected service image layer count.')
    for i,layer in enumerate(manifest['layers']):
        name='storage-layer-'+str(i)+'.tgz'
        if layer['digest']!='sha256:'+PINNED[name]:raise ValueError('Unexpected storage image layer.')
        if i in (6,7,9,10,11,12,13):cache(root,name,base+'blobs/'+layer['digest'],headers)
    count=prepare_node(lab,('postgresql17','postgresql17-contrib','xz'),directory='service-apks')
    (root/'sources.json').write_text(json.dumps({'releases':RELEASES,'storage_image_digest':STORAGE_MANIFEST,'artifact_sha256':PINNED,'runtime_apks':count,'trust':'Publisher/image digests over HTTPS and guest APK signature trust; not independent signature attestation.'},indent=2),encoding='utf-8')
    print('Services cached. No host installation, VM launch or source upload. Continue with the explicit tour sandbox action.')


if __name__=='__main__':main()
