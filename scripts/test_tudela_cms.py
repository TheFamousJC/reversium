"""Explicit local CMS preview: no NIC, live services or public listener."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reversium.cms_preview import Preview
from reversium.qemu_lab import probe_tudela

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('zip')
    parser.add_argument('--lab',default='reports/qemu-lab')
    parser.add_argument('--accelerator',choices=('tcg','whpx'),default='tcg')
    args=parser.parse_args()
    preview=Preview()
    try:
        result=probe_tudela(args.lab,args.zip,accelerator=args.accelerator,tour=True,preview=preview)
        print(json.dumps(result,indent=2))
        if result.get('blocker'):sys.exit(1)
    finally:
        preview.close()
