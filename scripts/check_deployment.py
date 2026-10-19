"""Read-only public-release smoke check. Sends no user ZIP, notes or credentials."""
import argparse
import hashlib
import json
import sys
import threading
import time
import urllib.request
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from reversium import __version__

PUBLIC=('index.html','web/index.html','web/app.js','web/engine.json','web/engine.zip','docs/user-guide.html','output/pdf/Reversium-User-Guide.pdf','output/pdf/Reversium-Feature-List.pdf','output/pdf/Reversium-User-Journeys.pdf')


def verify(base,fetch=None):
    parsed=urlsplit(base)
    if parsed.username or parsed.password or parsed.query or parsed.fragment or (parsed.scheme!='https' and not(parsed.scheme=='http' and parsed.hostname in ('127.0.0.1','localhost','::1'))):
        raise ValueError('Use an HTTPS public base URL or an HTTP loopback preview, without credentials, query or fragment.')
    def read(path):
        if fetch:return fetch(path)
        request=urllib.request.Request(base.rstrip('/')+'/'+path,headers={'User-Agent':'Reversium-release-check','Cache-Control':'no-cache'})
        with urllib.request.urlopen(request,timeout=15) as response:
            if urlsplit(response.url).netloc!=parsed.netloc:raise ValueError('Cross-host release redirect refused.')
            data=response.read(8*1024*1024+1)
            if len(data)>8*1024*1024:raise ValueError('Release asset exceeds check limit: '+path)
            return data
    assets={name:read(name) for name in PUBLIC}
    # Exact committed build bytes prevent a mixed or stale release passing.
    for name,body in assets.items():
        expected=(ROOT/name).read_bytes()
        if name.endswith(('.html','.js','.json')):body=body.replace(b'\r\n',b'\n');expected=expected.replace(b'\r\n',b'\n')
        if body!=expected:raise ValueError('Stale or different public asset: '+name)
    meta=json.loads(assets['web/engine.json'])
    if meta.get('version')!=__version__ or hashlib.sha256(assets['web/engine.zip']).hexdigest()!=meta.get('sha256'):
        raise ValueError('Analyzer version or integrity mismatch.')
    return {'version':__version__,'assets_checked':len(assets),'result':'pass','scope':'Public files match this checkout. Browser interaction is a separate test.'}


@contextmanager
def local_preview():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path=urlsplit(self.path).path.lstrip('/')
            if path not in PUBLIC:self.send_error(404);return
            body=(ROOT/path).read_bytes();self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    try:yield 'http://127.0.0.1:'+str(server.server_port)
    finally:server.shutdown();server.server_close();worker.join()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--base-url');group.add_argument('--local',action='store_true')
    parser.add_argument('--attempts',type=int,default=1);parser.add_argument('--retry-delay',type=int,default=10)
    args=parser.parse_args()
    if not 1<=args.attempts<=6 or not 0<=args.retry_delay<=30:parser.error('Attempts 1-6; retry delay 0-30 seconds.')
    if args.local:
        with local_preview() as base:print(json.dumps(verify(base)))
        return
    for attempt in range(args.attempts):
        try:print(json.dumps(verify(args.base_url)));return
        except Exception as error:
            print('Release not verified: '+str(error),file=sys.stderr)
            if attempt+1==args.attempts:raise SystemExit(1)
            time.sleep(args.retry_delay)


if __name__=='__main__':main()
