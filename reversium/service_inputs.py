"""Pinned official service artifacts for the offline reviewed tour profile."""
import hashlib,json,re
from pathlib import Path
from .service_guest import CONFIG,GATEWAY,BOOTSTRAP,PREPARE_TEST,HEALTH,MIGRATE

PINNED = {'auth.tar.xz': 'b5c2991d1df760c9b099c1c2395a94bd1c2f83ed58901934921997179dc9f7ea', 'postgrest.tar.xz': 'b47ecc82fce1dcebbbc4183d839e52f07f7630c9d7ad0f54db753d1939299354', 'storage-layer-0.tgz': 'd0c1d894c237d8192cbcd37e435031ad4eddec173299568a5a05869c2e40dfa3', 'storage-layer-1.tgz': '849b6d766a29b3c0e0ac4165f1f677f3ca80e3de0a7f544fb00c1d188d5d4b5b', 'storage-layer-2.tgz': '9d567708845ceb476af9b0c529afe405bb180fcfe2ae5a8f1ca1fbd38fcf4505', 'storage-layer-3.tgz': 'a2bb6eaf080b473d286c6da1d3900fce543f45e7eea1712fe51e92c3138dfeca', 'storage-layer-4.tgz': 'd940c5903eae00b95eaeb14e19a2da6292f745393273734117e45c8ca7a1154f', 'storage-layer-5.tgz': '064054c04827bf86f303b5d5f0767f91d26327aa06c473878a9a13d031330018', 'storage-layer-6.tgz': '699607ef168662ee941769ab03a6aadd57bf8c6692d03bd4d1ae7eb452866ed1', 'storage-layer-7.tgz': 'a9a0da367407cce64c949df85d310c457ba10b8bc898e963d1f21fbf25db648f', 'storage-layer-8.tgz': '055610b10f4baf1edf9b991e00d63bcf354d29e25b44d2aa68065e1a5d100eb4', 'storage-layer-9.tgz': 'f5fa54e1ffd033ad9006db91cc124d98e0ee34e36c6b048be88f81624b2eb0c9', 'storage-layer-10.tgz': '4f39a67cdd5aa61dd99fa3a7445fcb0d34ce19aa9a80f8733777c09c408bf687', 'storage-layer-11.tgz': 'b9b42a4e63845823a6d357b3eba7bf0ab790d7ffdc169de7ac71018da04f6f71', 'storage-layer-12.tgz': '45ae59205791b7b67807368492029512d0e39ef89d09b3afca48ebfa3e808e44', 'storage-layer-13.tgz': '2c6b814eda40f421f048a0ea7ac64de30ac71557292caf0471c5d6577a943852'}

def add_services(lab,files):
    lab=Path(lab)
    for name,expected in PINNED.items():
        if name.startswith('storage-layer-') and int(name.split('-')[2].split('.')[0]) not in (6,7,9,10,11,12,13):continue
        p=lab/'services'/name
        if p.stat().st_size>160*1024*1024:raise ValueError('Service asset exceeds bound.')
        data=p.read_bytes()
        if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Pinned service artifact checksum mismatch.')
        files[name]=data
    apks=json.loads((lab/'service-apks/manifest.json').read_text(encoding='utf-8'))
    if not 1<=len(apks)<=80:raise ValueError('Service APK count invalid.')
    if not any(re.fullmatch(r'postgresql17-17\.11-r\d+\.apk',e.get('name','')) for e in apks):raise ValueError('Reviewed service profile requires PostgreSQL 17.11.')
    for name in list(files):
        if name.endswith('.apk'):del files[name]
    for item in apks:
        name=item['name']
        if not re.fullmatch(r'[A-Za-z0-9_.+~-]+\.apk',name):raise ValueError('Invalid service APK name.')
        p=lab/'service-apks'/name
        if p.stat().st_size>64*1024*1024:raise ValueError('Service APK too large.')
        data=p.read_bytes()
        if hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('Service APK cache changed.')
        files[name]=data
    for name,content in {'services-config.cjs':CONFIG,'services-gateway.cjs':GATEWAY,'services-bootstrap.sh':BOOTSTRAP,'prepare-tour-test.cjs':PREPARE_TEST,'services-health.cjs':HEALTH,'services-migrate.sh':MIGRATE}.items():files[name]=content.encode()
    if sum(map(len,files.values()))>512*1024*1024:raise ValueError('Tour input exceeds 512 MiB.')
    return files
