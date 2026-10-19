"""Download pinned trusted assets into an ignored local lab; no installer/VM run.

Requires existing 7-Zip on Windows. Optional ISO authoring dependency is installed
only in LAB/python. Downloaded files and VM logs must never be committed.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reversium.qemu_lab import ASSETS, digest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab',default='reports/qemu-lab')
    parser.add_argument('--seven-zip',default=shutil.which('7z') or 'C:/Program Files/7-Zip/7z.exe')
    args=parser.parse_args()
    lab=Path(args.lab).resolve();(lab/'downloads').mkdir(parents=True,exist_ok=True)
    seven=Path(args.seven_zip)
    if not seven.is_file():parser.error('Install 7-Zip from its official source, or specify --seven-zip.')
    sources=[]
    for name,(base,algorithm,expected) in ASSETS.items():
        target=lab/'downloads'/name
        if not target.exists():
            partial=target.with_suffix(target.suffix+'.part');size=0
            with urllib.request.urlopen(base+name,timeout=90) as response,partial.open('wb') as output:
                while chunk:=response.read(1024*1024):
                    size+=len(chunk)
                    if size>300*1024*1024:raise ValueError('Download exceeds 300 MiB bound.')
                    output.write(chunk)
            partial.replace(target)
        if digest(target,algorithm)!=expected:raise ValueError('Pinned checksum mismatch: '+name)
        sources.append({'url':base+name,'algorithm':algorithm,'digest':expected,'verification':'Publisher-provided checksum over HTTPS, not independent signature verification.'})
    subprocess.run([str(seven),'x',str(lab/'downloads/qemu-w64-setup-20260811.exe'),'-o'+str(lab/'qemu'),'qemu-system-x86_64.exe','*.dll',r'share\*','-r','-y','-bso0','-bsp0'],check=True,timeout=300)
    subprocess.run([str(seven),'x',str(lab/'downloads/alpine-virt-3.23.6-x86_64.iso'),'-o'+str(lab/'alpine'),r'boot\vmlinuz-virt',r'boot\initramfs-virt','-y','-bso0','-bsp0'],check=True,timeout=60)
    subprocess.run([sys.executable,'-m','pip','install','--disable-pip-version-check','--no-deps','--target',str(lab/'python'),'pycdlib==1.14.0'],check=True,timeout=120)
    files=list((lab/'qemu').rglob('*'))+list((lab/'alpine').rglob('*'))
    manifest={p.relative_to(lab).as_posix():digest(p) for p in files if p.is_file()}
    (lab/'runtime-hashes.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    (lab/'asset-sources.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
    print('Assets prepared. No VM was launched. Run the explicit sandbox self-test next.')


if __name__=='__main__':main()
