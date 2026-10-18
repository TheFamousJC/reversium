"""Fixed guest-only service configuration. No host paths or live credentials."""
CONFIG=r"""
const fs=require('fs'),crypto=require('crypto');
const secret=crypto.randomBytes(48).toString('hex'),password=crypto.randomBytes(24).toString('hex');
function jwt(role){const b=o=>Buffer.from(JSON.stringify(o)).toString('base64url'),head=b({alg:'HS256',typ:'JWT'}),payload=b({role,iss:'reversium-disposable',iat:Math.floor(Date.now()/1000)-10,exp:Math.floor(Date.now()/1000)+7200}),text=head+'.'+payload;return text+'.'+crypto.createHmac('sha256',secret).update(text).digest('base64url');}
const anon=jwt('anon'),service=jwt('service_role'),url='https://127.0.0.1:18443';
const env={APP_URL:url,SUPABASE_URL:url,VITE_SUPABASE_URL:url,SUPABASE_SECRET_KEY:service,VITE_SUPABASE_PUBLISHABLE_KEY:anon,NODE_EXTRA_CA_CERTS:'/work/certs/cert.pem',NODE_ENV:'production',PORT:'18765',HERZL_MODE:'simulator',NARRATION_MODE:'simulator',PGRST_DB_URI:'postgresql://authenticator:'+password+'@127.0.0.1:5432/postgres',PGRST_DB_SCHEMAS:'public,storage',PGRST_DB_ANON_ROLE:'anon',PGRST_JWT_SECRET:secret,PGRST_SERVER_HOST:'127.0.0.1',PGRST_SERVER_PORT:'3001',GOTRUE_API_HOST:'127.0.0.1',GOTRUE_API_PORT:'9999',GOTRUE_API_EXTERNAL_URL:url+'/auth/v1',API_EXTERNAL_URL:url+'/auth/v1',GOTRUE_SITE_URL:url,GOTRUE_DB_DRIVER:'postgres',GOTRUE_DB_DATABASE_URL:'postgresql://supabase_auth_admin:'+password+'@127.0.0.1:5432/postgres?search_path=auth',GOTRUE_DB_NAMESPACE:'auth',GOTRUE_DB_MIGRATIONS_PATH:'/work/auth/migrations',GOTRUE_JWT_SECRET:secret,GOTRUE_JWT_AUD:'authenticated',GOTRUE_JWT_DEFAULT_GROUP_NAME:'authenticated',GOTRUE_JWT_ADMIN_ROLES:'service_role',GOTRUE_EXTERNAL_EMAIL_ENABLED:'true',GOTRUE_MAILER_AUTOCONFIRM:'true',GOTRUE_DISABLE_SIGNUP:'true',GOTRUE_RATE_LIMIT_EMAIL_SENT:'100',AUTH_JWT_SECRET:secret,PGRST_JWT_SECRET:secret,ANON_KEY:anon,SERVICE_KEY:service,PROJECT_REF:'reversium-disposable',TENANT_ID:'reversium-disposable',REGION:'local',GLOBAL_S3_BUCKET:'local',POSTGREST_URL:'http://127.0.0.1:3001',DATABASE_URL:'postgresql://supabase_storage_admin:'+password+'@127.0.0.1:5432/postgres',PGOPTIONS:'-c search_path=storage,public',STORAGE_BACKEND:'file',FILE_STORAGE_BACKEND_PATH:'/work/storage-data',FILE_SIZE_LIMIT:'8388608',ENABLE_IMAGE_TRANSFORMATION:'false',SERVER_HOST:'127.0.0.1',SERVER_PORT:'5000',SERVER_ADMIN_PORT:'5001',DB_MIGRATIONS_STRATEGY:'up',VERSION:'1.83.5',ENABLE_QUEUE_EVENTS:'false'};
fs.writeFileSync('/work/runtime.env',Object.entries(env).map(([k,v])=>`${k}='${v}'`).join('\n'),{mode:0o600});
fs.writeFileSync('/work/auth-helpers.sql',`GRANT ALL ON ALL TABLES IN SCHEMA storage TO service_role; GRANT ALL ON ALL SEQUENCES IN SCHEMA storage TO service_role; GRANT SELECT,INSERT,UPDATE,DELETE ON storage.objects TO anon,authenticated; GRANT SELECT ON storage.buckets TO anon,authenticated; CREATE OR REPLACE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql STABLE AS $$ SELECT nullif(nullif(current_setting('request.jwt.claims',true),'')::jsonb ->> 'sub','')::uuid $$; CREATE OR REPLACE FUNCTION auth.role() RETURNS text LANGUAGE sql STABLE AS $$ SELECT nullif(current_setting('request.jwt.claims',true),'')::jsonb ->> 'role' $$;`,{mode:0o600});
fs.writeFileSync('/work/bootstrap.sql',`CREATE ROLE anon NOLOGIN; CREATE ROLE authenticated NOLOGIN; CREATE ROLE service_role NOLOGIN BYPASSRLS; CREATE ROLE authenticator LOGIN NOINHERIT PASSWORD '${password}'; GRANT anon,authenticated,service_role TO authenticator;
CREATE ROLE supabase_auth_admin LOGIN NOINHERIT PASSWORD '${password}'; CREATE ROLE supabase_storage_admin LOGIN NOINHERIT PASSWORD '${password}'; GRANT anon,authenticated,service_role TO supabase_storage_admin;
CREATE SCHEMA extensions; CREATE EXTENSION pgcrypto WITH SCHEMA extensions; CREATE EXTENSION pg_trgm WITH SCHEMA extensions; CREATE EXTENSION "uuid-ossp" WITH SCHEMA extensions;
CREATE SCHEMA auth AUTHORIZATION supabase_auth_admin; CREATE SCHEMA storage AUTHORIZATION supabase_storage_admin; GRANT USAGE ON SCHEMA storage TO anon,authenticated,service_role;
GRANT CREATE ON DATABASE postgres TO supabase_auth_admin,supabase_storage_admin;
GRANT USAGE ON SCHEMA public,extensions TO anon,authenticated,service_role,supabase_auth_admin,supabase_storage_admin;
CREATE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql STABLE AS $$ SELECT nullif(current_setting('request.jwt.claims',true)::jsonb ->> 'sub','')::uuid $$;
CREATE FUNCTION auth.role() RETURNS text LANGUAGE sql STABLE AS $$ SELECT current_setting('request.jwt.claims',true)::jsonb ->> 'role' $$;
CREATE FUNCTION auth.jwt() RETURNS jsonb LANGUAGE sql STABLE AS $$ SELECT coalesce(nullif(current_setting('request.jwt.claims',true),''),'{}')::jsonb $$;
ALTER FUNCTION auth.uid() OWNER TO supabase_auth_admin; ALTER FUNCTION auth.role() OWNER TO supabase_auth_admin; ALTER FUNCTION auth.jwt() OWNER TO supabase_auth_admin;
GRANT USAGE ON SCHEMA auth TO anon,authenticated,service_role,supabase_storage_admin;
GRANT ALL ON FUNCTION auth.uid(),auth.role(),auth.jwt() TO anon,authenticated,service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO service_role;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO service_role;`,{mode:0o600});
console.log('Disposable service credentials generated inside guest; values not printed.');
"""

GATEWAY=r"""
const https=require('https'),http=require('http'),fs=require('fs');
https.createServer({key:fs.readFileSync('/work/certs/key.pem'),cert:fs.readFileSync('/work/certs/cert.pem')},(req,res)=>{
 const routes=[['/auth/v1',9999],['/rest/v1',3001],['/storage/v1',5000]],route=routes.find(([prefix])=>req.url===prefix||req.url.startsWith(prefix+'/')||req.url.startsWith(prefix+'?'));
 const port=route?route[1]:18765,path=route?(req.url.slice(route[0].length)||'/'):req.url;
 const upstream=http.request({hostname:'127.0.0.1',port,path,method:req.method,headers:{...req.headers,'x-forwarded-proto':'https'}},r=>{res.writeHead(r.statusCode,r.headers);r.pipe(res)});
 upstream.on('error',()=>{res.writeHead(502);res.end('Disposable service unavailable')});req.pipe(upstream);
}).listen(18443,'127.0.0.1',()=>console.log('Guest-only TLS gateway ready'));
"""

BOOTSTRAP=r"""set -eu
mkdir -p /work/auth /work/rest /work/storage-root /work/certs /run/postgresql
chown postgres:postgres /run/postgresql
mkdir -p /work/pg;chown postgres:postgres /work/pg
su postgres -s /bin/sh -c '/usr/libexec/postgresql17/initdb -D /work/pg --auth-local=peer --auth-host=scram-sha-256' > /tmp/postgres-init.log 2>&1
su postgres -s /bin/sh -c '/usr/libexec/postgresql17/pg_ctl -D /work/pg -l /work/pg/server.log -o "-h 127.0.0.1 -k /run/postgresql -c max_connections=60 -c shared_buffers=32MB" start' >> /tmp/postgres-init.log 2>&1
node /mnt/input/services-config.cjs
chown postgres:postgres /work/bootstrap.sql
su postgres -s /bin/sh -c '/usr/libexec/postgresql17/psql -v ON_ERROR_STOP=1 -d postgres -f /work/bootstrap.sql' > /tmp/bootstrap-sql.log 2>&1
openssl req -x509 -newkey rsa:2048 -nodes -keyout /work/certs/key.pem -out /work/certs/cert.pem -days 1 -subj /CN=127.0.0.1 -addext subjectAltName=IP:127.0.0.1 > /tmp/cert.log 2>&1
chmod 600 /work/certs/key.pem
set -a;. /work/runtime.env;set +a
(cd /work/auth && tar -xJf /mnt/input/auth.tar.xz)
(cd /work/rest && tar -xJf /mnt/input/postgrest.tar.xz)
/work/auth/auth > /tmp/auth.log 2>&1 &
echo auth-start-requested
/work/rest/postgrest > /tmp/rest.log 2>&1 &
echo rest-start-requested
for n in 6 7 9 10 11 12 13; do tar -xzf /mnt/input/storage-layer-$n.tgz -C /work/storage-root;done
mkdir -p /work/storage-data
(cd /work/storage-root/app;exec node dist/start/server.js) > /tmp/storage.log 2>&1 &
echo storage-start-requested
node /mnt/input/services-gateway.cjs > /tmp/gateway.log 2>&1 &
echo gateway-start-requested
"""

PREPARE_TEST=r"""
const fs=require('fs');let s=fs.readFileSync('scripts/test-pilot-acceptance.ts','utf8');
s=s.replace('  const publicPayload = await loadPublishedContent(admin, primarySlug, \'en\');',`  const visitorResponse=await fetch(process.env.APP_URL+'/api/public/content?organization='+primarySlug+'&language=en');
  assert.equal(visitorResponse.status,200,'Public content HTTP response');
  const publicPayload = await visitorResponse.json();`);
s=s.replace("  assert.equal(publicPayload.sites[0].imageCredit, 'Test image: Tudela Global QA');",`  assert.equal(publicPayload.sites[0].imageCredit, 'Test image: Tudela Global QA');
  const imageResponse=await fetch(process.env.APP_URL+publicPayload.sites[0].imageUrl);
  assert.equal(imageResponse.status,200,'Published image HTTP response');
  assert.deepEqual(Buffer.from(await imageResponse.arrayBuffer()),png,'Published storage image round-trip');
  fs.writeFileSync('/tmp/tour-journey.json',JSON.stringify({editor_login:true,reviewer_login:true,tour_published:true,two_ordered_stops:true,validated_media_upload:true,public_content_http:true,public_media_bytes:true,tenant_isolation:true,role_separation:true,wrong_password_rejected:true}));`);
s=s.replace('  editor = await signIn(editorUser.email);',`  const wrongLogin=await clientFor().auth.signInWithPassword({email:editorUser.email,password:'Reversium-deliberately-wrong-password'});
  assert.ok(wrongLogin.error,'Wrong password must be rejected');
  assert.equal(wrongLogin.data.session,null,'Wrong password must not create a session');
  editor = await signIn(editorUser.email);`);
s="import fs from 'node:fs';\n"+s;
if(!s.includes('visitorResponse')||!s.includes('Published storage image round-trip'))throw Error('Reviewed acceptance harness anchors not found');
fs.writeFileSync('scripts/reversium-tour-acceptance.ts',s);
"""


HEALTH=r"""
const http=require('http');
(async()=>{for(const [name,port,path] of [['auth',9999,'/health'],['rest',3001,'/'],['storage',5000,'/status']]){let good=false;for(let i=0;i<40;i++){try{const r=await fetch('http://127.0.0.1:'+port+path);if(r.ok){good=true;break}}catch{}await new Promise(r=>setTimeout(r,500));}console.log(name+':'+good);if(!good)process.exit(1);}})();
"""


MIGRATE=r"""set -eu
su postgres -s /bin/sh -c '/usr/libexec/postgresql17/psql -v ON_ERROR_STOP=1 -d postgres' < /work/auth-helpers.sql
for f in "$1"/supabase/migrations/*.sql;do
 su postgres -s /bin/sh -c '/usr/libexec/postgresql17/psql -v ON_ERROR_STOP=1 -d postgres' < "$f"
done
printf "NOTIFY pgrst, 'reload schema';\n" | su postgres -s /bin/sh -c '/usr/libexec/postgresql17/psql -v ON_ERROR_STOP=1 -d postgres'
"""
