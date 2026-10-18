"""Opt-in, bounded browser relay over serial. Never adds a guest NIC or shares."""
import base64
import gzip
import io
import json
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

LIMIT = 2 * 1024 * 1024
CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; media-src 'self' blob:; object-src 'none'; frame-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"

FETCH = r"""
const fs=require('fs'),zlib=require('zlib');
(async()=>{const r=JSON.parse(Buffer.from(process.argv[2],'base64').toString());
if(!r.path.startsWith('/')||r.path.startsWith('//')||/[\r\n\\]/.test(r.path))throw Error('Invalid relative target');
if(!/^[a-f0-9]{64}$/.test(r.headers_key))throw Error('Invalid header cache key');
const headerFile='/tmp/cms-headers-'+r.headers_key+'.json';
if(r.headers)fs.writeFileSync(headerFile,JSON.stringify(r.headers),{mode:0o600});
r.headers=JSON.parse(fs.readFileSync(headerFile,'utf8'));
const response=await fetch('https://127.0.0.1:18443'+r.path,{method:r.method,headers:r.headers,body:['GET','HEAD'].includes(r.method)?undefined:Buffer.from(r.body,'base64'),redirect:'manual',signal:AbortSignal.timeout(15000)});
const reader=response.body?.getReader();let chunks=[],size=0;
if(reader)while(true){const {value,done}=await reader.read();if(done)break;size+=value.length;if(size>2097152)throw Error('Response too large');chunks.push(value)}
const headers={};for(const k of ['content-type','location','content-range','accept-ranges'])if(response.headers.has(k))headers[k]=response.headers.get(k);
process.stdout.write('REVERSIUM_HTTP:'+JSON.stringify({status:response.status,headers,body:zlib.gzipSync(Buffer.concat(chunks)).toString('base64')})+'\n',()=>process.exit(0));
})().catch(()=>{console.log('REVERSIUM_HTTP:'+JSON.stringify({status:502,headers:{'content-type':'text/plain'},body:require('zlib').gzipSync('Guest relay failed').toString('base64')}))});
"""

SEED = r"""
const crypto=require('crypto');
const {createClient}=require(process.argv[2]+'/node_modules/@supabase/supabase-js');
(async()=>{const admin=createClient(process.env.SUPABASE_URL,process.env.SUPABASE_SECRET_KEY,{auth:{persistSession:false}}),suffix=crypto.randomBytes(4).toString('hex'),password=crypto.randomBytes(18).toString('hex')+'Aa!9',org=crypto.randomUUID(),users={};
function must(r){if(r.error)throw Error(r.error.message);return r.data}
for(const role of ['editor','reviewer']){const email='cms-'+role+'-'+suffix+'@reversium.test';const {user}=must(await admin.auth.admin.createUser({email,password,email_confirm:true,user_metadata:{display_name:'Disposable CMS '+role,username:'cms-'+role+'-'+suffix,age_16_confirmed:true,preferred_language:'en'}}));must(await admin.from('profiles').update({password_reset_required:false}).eq('user_id',user.id));users[role]={email,id:user.id};}
must(await admin.from('organizations').insert({id:org,name:'Disposable Browser Test',slug:'cms-'+suffix,status:'active',created_by:users.editor.id}));
must(await admin.from('organization_memberships').insert(Object.entries(users).map(([role,user])=>({organization_id:org,user_id:user.id,role,status:'active',invited_by:users.editor.id,accepted_at:new Date().toISOString()}))));
console.log('REVERSIUM_FIXTURE:'+JSON.stringify({organization:org,slug:'cms-'+suffix,password,users}));
})().catch(e=>{console.error(e.message);process.exit(1)});
"""


def valid_target(path):
    return (isinstance(path, str) and path.startswith('/') and not path.startswith('//')
            and len(path) <= 8192 and not any(c in path for c in '\r\n\\'))


class Preview:
    """Dedicated random loopback origin; cookie gate, exact Host/Origin, no files."""
    def __init__(self):
        self.token = secrets.token_urlsafe(32)
        self.stop_token = secrets.token_urlsafe(32)
        self.lock = threading.Lock()
        self.guest = None
        self.count = 0
        self.header_cache = set()
        self.events = []
        self.done = threading.Event()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass  # Auth headers, request bodies and token URLs are never logged.

            def reply(self, status, body, kind='text/plain', headers=None):
                self.send_response(status)
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Content-Type', kind)
                self.send_header('Content-Security-Policy', CSP)
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Referrer-Policy', 'no-referrer')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Connection', 'close')
                for k, v in (headers or {}).items():
                    self.send_header(k, v)
                try:
                    self.end_headers()
                    if self.command != 'HEAD':
                        self.wfile.write(body)
                except OSError:
                    self.close_connection = True  # Client navigated away.

            def handle_request(self):
                if self.headers.get('Host') != owner.origin.removeprefix('http://'):
                    return self.reply(403, b'Invalid host')
                if self.path == '/__preview/' + owner.token and self.command == 'GET':
                    return self.reply(303, b'', headers={'Location': '/', 'Set-Cookie': 'reversium_preview='+owner.token+'; HttpOnly; SameSite=Strict; Path=/'})
                cookies = self.headers.get('Cookie', '').split('; ')
                if 'reversium_preview='+owner.token not in cookies:
                    return self.reply(403, b'Open the private preview entry URL first')
                origin = self.headers.get('Origin')
                stop_form = self.path == '/__reversium_finish' and self.command == 'POST'
                # Browser form POSTs may have Origin:null under no-referrer.
                # Only this non-guest control uses a separate CSRF token instead.
                if not stop_form and ((origin and origin != owner.origin) or (self.command not in ('GET','HEAD') and origin != owner.origin)):
                    return self.reply(403, b'Invalid origin')
                if not valid_target(self.path) or self.headers.get('Transfer-Encoding'):
                    return self.reply(400, b'Invalid request')
                try:
                    length = int(self.headers.get('Content-Length', '0'))
                    if not 0 <= length <= LIMIT:
                        return self.reply(413, b'Request too large')
                    self.connection.settimeout(20)
                    body = self.rfile.read(length)
                    if len(body) != length:
                        return self.reply(400, b'Incomplete request')
                    if stop_form:
                        content_type=self.headers.get('Content-Type','').split(';')[0]
                        values=parse_qs(body.decode('ascii',errors='strict')) if content_type=='application/x-www-form-urlencoded' else {}
                        submitted=values.get('confirm',[])
                        if len(submitted)!=1 or not secrets.compare_digest(submitted[0],owner.stop_token):
                            return self.reply(403,b'Invalid stop confirmation')
                        owner.done.set()
                        return self.reply(200, b'Preview stopping')
                    if self.path == '/__reversium' and self.command == 'GET':
                        page='<!doctype html><title>Stop disposable preview</title><h1>Disposable Tudela preview</h1><p>This stops the local listener and destroys the temporary guest state.</p><form method="post" action="/__reversium_finish"><input type="hidden" name="confirm" value="'+owner.stop_token+'"><button>Stop preview and guest</button></form>'
                        return self.reply(200,page.encode(), 'text/html; charset=utf-8')
                    if owner.guest is None:
                        return self.reply(503, b'Guest not ready')
                    result = owner.forward(self.command, self.path, self.headers, body)
                    headers = result['headers']
                    location = headers.get('location')
                    if location and (not valid_target(location) or location.startswith('/__preview/')):
                        return self.reply(502, b'External redirect blocked')
                    return self.reply(result['status'], result['body'], headers.pop('content-type', 'application/octet-stream'), headers)
                except Exception:
                    return self.reply(502, b'Bounded guest relay failed')

            do_GET = do_HEAD = do_POST = do_PATCH = do_PUT = do_DELETE = do_OPTIONS = handle_request

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.server.daemon_threads = True
        self.origin = 'http://127.0.0.1:' + str(self.server.server_port)

    def forward(self, method, path, headers, body):
        allowed = {'authorization','apikey','content-type','range','prefer','accept','accept-profile','content-profile','x-client-info','x-supabase-api-version','x-organization-id','x-file-name','x-media-rights-status','x-media-creator','x-media-attribution','x-media-rights-notes','x-media-source-url','x-media-license-name','x-media-license-url'}
        import hashlib
        selected = {k.lower():v for k,v in headers.items() if k.lower() in allowed}
        key = hashlib.sha256(json.dumps(selected,sort_keys=True).encode()).hexdigest()
        packet = {'method':method,'path':path,'headers_key':key,'body':base64.b64encode(body).decode()}
        with self.lock:
            if key not in self.header_cache:packet['headers']=selected
            encoded = base64.b64encode(json.dumps(packet).encode()).decode()
            rc, output = self.guest.command('NODE_EXTRA_CA_CERTS=/work/certs/cert.pem node /mnt/input/cms-fetch.cjs '+encoded, seconds=25)
            self.count += 1
            if not rc:self.header_cache.add(key)
        if rc:
            raise ValueError('Guest fetch failed')
        result = json.JSONDecoder().raw_decode(output.split('REVERSIUM_HTTP:',1)[1])[0]
        self.events.append({'method':method,'route':path.split('?')[0],'status':result['status']})
        self.events=self.events[-2000:]
        if hasattr(self,'run_path'):
            (self.run_path/'relay-requests-private.json').write_text(json.dumps(self.events),encoding='utf-8')
        with gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(result['body']))) as stream:
            result['body'] = stream.read(LIMIT+1)
        if len(result['body']) > LIMIT:
            raise ValueError('Response exceeds bound')
        return result

    def run(self, guest, run):
        self.guest = guest
        self.run_path = run
        (run/'preview-entry.json').write_text(json.dumps({'url':self.origin+'/__preview/'+self.token,'scope':'temporary local serial relay; no guest NIC'}),encoding='utf-8')
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        print('CMS preview ready; private entry URL saved in '+str(run/'preview-entry.json'),flush=True)
        start = time.monotonic()
        while not self.done.wait(1) and guest.process.poll() is None and time.monotonic()-start < 1200:
            pass
        self.server.shutdown()
        with self.lock:
            self.guest = None
        return {'preview_requests':self.count,'preview_stopped':True,'cms_publishing':'manual review required; no automatic success claim'}

    def close(self):
        self.done.set()
        self.server.server_close()
