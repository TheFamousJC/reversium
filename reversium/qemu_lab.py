"""Experimental offline guest supervisor. No guest networking or host folders.

Windows native backend only. Explicit CLI actions; never imported by browser UI.
"""
import hashlib
import io
import json
import os
import queue
import re
import secrets
import socket
import subprocess
import sys
import threading
import time
import base64
import zipfile
from pathlib import Path

ASSETS = {
    'qemu-w64-setup-20260811.exe': ('https://qemu.weilnetz.de/w64/', 'sha512', '5bcf9eed634e8575a37b74f445af41a2fe4106da512d0c30c368301d4c105037fdfab40a5287367a28a957624cddebbc8c07e16c88ab6634f554cdf3d16bf543'),
    'alpine-virt-3.23.6-x86_64.iso': ('https://dl-cdn.alpinelinux.org/alpine/v3.23/releases/x86_64/', 'sha256', '121e79056f95f95ab0479bbec9f12421a9910420d7475125b60bcaf7cb0c12f7'),
}
MAX_LOG = 2 * 1024 * 1024


def digest(path, algorithm='sha256'):
    with Path(path).open('rb') as stream:
        result=hashlib.new(algorithm)
        while chunk:=stream.read(1024*1024):result.update(chunk)
        return result.hexdigest()


def verify_lab(lab):
    lab = Path(lab).resolve()
    if os.name != 'nt':
        raise ValueError('This experimental backend currently supports native Windows only.')
    if ',' in str(lab) or '\n' in str(lab):
        raise ValueError('Lab paths containing commas/newlines are unsupported by the drive profile.')
    for name, (_, algorithm, expected) in ASSETS.items():
        if digest(lab / 'downloads' / name, algorithm) != expected:
            raise ValueError('Pinned asset checksum mismatch: ' + name)
    manifest = json.loads((lab / 'runtime-hashes.json').read_text(encoding='utf-8'))
    for name, expected in manifest.items():
        p = (lab / name).resolve()
        if not p.is_relative_to(lab) or digest(p) != expected:
            raise ValueError('Extracted runtime checksum mismatch.')
    for required in ['qemu/qemu-system-x86_64.exe', 'alpine/boot/vmlinuz-virt', 'alpine/boot/initramfs-virt']:
        if required not in manifest:
            raise ValueError('Incomplete runtime manifest.')
    return lab


def argv(lab, media=None, accelerator="tcg"):
    if accelerator not in ("tcg", "whpx"):raise ValueError("Unsupported explicit accelerator.")
    lab = Path(lab).resolve()
    args = [str(lab/'qemu/qemu-system-x86_64.exe'), '-L', str(lab/'qemu/share'),
            '-nodefaults', '-no-user-config', '-machine', 'q35', '-accel', accelerator,
            '-m', '1024', '-smp', '2', '-display', 'none', '-monitor', 'none',
            '-serial', 'stdio', '-nic', 'none', '-no-reboot',
            '-kernel', str(lab/'alpine/boot/vmlinuz-virt'), '-initrd', str(lab/'alpine/boot/initramfs-virt'),
            '-append', 'console=ttyS0 modules=loop,squashfs,sd-mod,usb-storage quiet',
            '-drive', 'file='+str(lab/'downloads/alpine-virt-3.23.6-x86_64.iso')+',format=raw,media=cdrom,readonly=on']
    if media:
        media = Path(media).resolve()
        if not media.is_relative_to(lab) or ',' in str(media):
            raise ValueError('Input media must be inside the lab and have no comma in its path.')
        args += ['-drive', 'file='+str(media)+',format=raw,media=cdrom,readonly=on']
    return args


class WindowsJob:
    """Close-on-parent-exit job; never leave a detached emulator running."""
    def __init__(self, process):
        import ctypes
        from ctypes import wintypes as w
        class Basic(ctypes.Structure):
            _fields_ = [('process_time', ctypes.c_int64), ('job_time', ctypes.c_int64), ('flags', w.DWORD),
                        ('min_working', ctypes.c_size_t), ('max_working', ctypes.c_size_t), ('active', w.DWORD),
                        ('affinity', ctypes.c_size_t), ('priority', w.DWORD), ('scheduling', w.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]
        class Extended(ctypes.Structure):
            _fields_ = [('basic', Basic), ('io', IO), ('process_memory', ctypes.c_size_t), ('job_memory', ctypes.c_size_t), ('peak_process', ctypes.c_size_t), ('peak_job', ctypes.c_size_t)]
        self.dll = ctypes.WinDLL('kernel32', use_last_error=True)
        self.dll.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
        self.dll.CreateJobObjectW.restype = w.HANDLE
        self.dll.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
        self.dll.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        self.dll.CloseHandle.argtypes = [w.HANDLE]
        self.handle = self.dll.CreateJobObjectW(None, None)
        limits = Extended()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.handle or not self.dll.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)) or not self.dll.AssignProcessToJobObject(self.handle, w.HANDLE(process._handle)):
            if self.handle:
                self.dll.CloseHandle(self.handle)
            raise OSError('Cannot attach kill-on-close job; refusing an unsupervised guest.')

    def close(self):
        if self.handle:
            self.dll.CloseHandle(self.handle)
            self.handle = None


class Guest:
    def __init__(self, lab, media=None, seconds=180, accelerator="tcg"):
        if not 1 <= seconds <= 600:
            raise ValueError('Guest timeout must be 1–600 seconds.')
        self.lab, self.buffer, self.q = Path(lab), bytearray(), queue.Queue(maxsize=1024)
        self.nonce, self.expired = secrets.token_hex(16), False
        self.process = subprocess.Popen(argv(lab, media, accelerator), cwd=Path(lab)/'qemu', stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            self.job = WindowsJob(self.process)
        except Exception:
            self.process.kill(); self.process.wait(timeout=5)
            raise
        def read():
            while chunk := self.process.stdout.read1(4096):
                try: self.q.put_nowait(chunk)
                except queue.Full:
                    self.stop(); break
        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()
        def deadline():
            self.expired = True
            self.stop()
        self.timer = threading.Timer(seconds, deadline)
        self.timer.daemon = True
        self.timer.start()

    def stop(self):
        if self.process.poll() is None:
            self.process.kill()

    def wait(self, pattern, seconds=60, start=0):
        deadline = time.monotonic()+seconds
        while time.monotonic() < deadline:
            match = re.search(pattern, bytes(self.buffer[start:]))
            if match:
                return match
            if self.process.poll() is not None and self.q.empty():
                raise RuntimeError('Guest exited before the expected result; see private serial log.')
            try: self.buffer.extend(self.q.get(timeout=.2))
            except queue.Empty: continue
            if len(self.buffer) > MAX_LOG:
                self.stop()
                raise RuntimeError('Guest serial log limit reached.')
        self.stop()
        raise TimeoutError('Guest operation timed out.')

    def send(self, text):
        # Pace the emulated UART: fast pipe writes can overrun the guest serial FIFO.
        encoded=text.encode('utf-8')
        for offset in range(0,len(encoded),8):
            self.process.stdin.write(encoded[offset:offset+8])
            self.process.stdin.flush()
            time.sleep(.02)

    def login(self):
        self.wait(rb'login:', seconds=100)
        self.send('root\n')
        self.wait(rb'localhost:~#', seconds=40)
        self.send('\x1b[1;1R')
        self.command('export TERM=dumb; stty -echo; ip link set lo up')

    def command(self, command, seconds=40):
        start = len(self.buffer)
        marker = self.nonce+':'+secrets.token_hex(4)
        self.send(command+"; rc=$?; printf '\\n"+marker+":%s\\n' \"$rc\"\n")
        match = self.wait(rb'\r*\n'+marker.encode()+rb':(\d+)\r*\n', seconds, start)
        return int(match.group(1)), bytes(self.buffer[start:]).decode('utf-8', errors='replace')

    def close(self, log=None):
        self.timer.cancel()
        self.stop()
        self.process.wait(timeout=10)
        self.reader.join(timeout=2)
        while not self.q.empty() and len(self.buffer) < MAX_LOG:
            self.buffer.extend(self.q.get_nowait())
        self.job.close()
        if log:
            Path(log).write_bytes(bytes(self.buffer[:MAX_LOG]))
        for pipe in (self.process.stdin,self.process.stdout):
            pipe.close()


def input_iso(lab, output, files):
    sys.path.insert(0, str(Path(lab)/'python'))
    import pycdlib  # optional local lab dependency; not needed by analysis
    image = pycdlib.PyCdlib()
    image.new(interchange_level=3, rock_ridge='1.09', vol_ident='REVERSIUM_INPUT')
    streams=[]
    try:
        for i, (name,data) in enumerate(files.items()):
            stream=io.BytesIO(data);streams.append(stream)
            image.add_fp(stream,len(data),iso_path='/F'+str(i)+'.BIN;1',rr_name=name)
        image.write(str(output))
    finally:
        image.close()
        for stream in streams:stream.close()


def mount_input(guest):
    return guest.command('mkdir -p /mnt/input; for d in /dev/sr*; do mount -o ro "$d" /mnt/input 2>/dev/null || continue; test -f /mnt/input/reversium-input && break; umount /mnt/input; done; test -f /mnt/input/reversium-input')[0] == 0


def self_test(lab, accelerator="tcg"):
    lab = verify_lab(lab)
    run = lab/'runs'/('self-test-'+secrets.token_hex(6)); run.mkdir(parents=True)
    media = run/'input.iso'
    input_iso(lab,media,{'reversium-input':b'benign probe only\n','probe.txt':b'read-only input\n'})
    before = digest(media)
    canary=run/'host-canary.txt';canary.write_text(secrets.token_hex(20))
    canary_hash=digest(canary)
    listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen(1);listener.settimeout(.2)
    port=listener.getsockname()[1]
    result={'stage':'blank guest isolation checks','accelerator':accelerator,'passed':False,'checks':{},'limits':{'guest_ram_mib':1024,'guest_cpus':2,'serial_log_bytes':MAX_LOG,'no_network':True,'no_host_shares':True},'scope':'Selected configuration/behavior tests, not proof against emulator vulnerabilities or a guarantee of safety.'}
    guest=None
    try:
        guest=Guest(lab,media,seconds=180,accelerator=accelerator);guest.login()
        checks=result['checks']
        checks['expected_alpine']=guest.command('test "$(cat /etc/alpine-release)" = 3.23.6')[0]==0
        checks['loopback_only']=guest.command('test "$(ls /sys/class/net)" = lo')[0]==0
        checks['no_routes']=guest.command('test -z "$(ip route)"')[0]==0
        checks['host_http_unreachable']=guest.command('if wget -q -T 2 -O /dev/null http://10.0.2.2:'+str(port)+'/; then false; else true; fi')[0]==0
        checks['no_host_filesystems']=guest.command("! grep -Eq ' (9p|virtiofs|cifs|vboxsf|fuse.sshfs) ' /proc/mounts")[0]==0
        checks['probe_media_mounted']=mount_input(guest)
        checks['probe_readable']=guest.command('test "$(cat /mnt/input/probe.txt)" = "read-only input"')[0]==0
        checks['input_write_rejected']=guest.command('if echo changed > /mnt/input/probe.txt; then false; else true; fi')[0]==0
        checks['no_windows_mount']=guest.command('test ! -d /mnt/c && test ! -d /mnt/host; mkdir -p /mnt/host; echo guest-only > /mnt/host/host-canary.txt; echo disposable > /tmp/reversium-marker')[0]==0
        guest.close(run/'first-guest-private.log');guest=None
        checks['input_media_unchanged']=digest(media)==before
        checks['host_canary_unchanged']=digest(canary)==canary_hash
        try: listener.accept();checks['no_host_connection']=False
        except socket.timeout:checks['no_host_connection']=True
        guest=Guest(lab,seconds=150,accelerator=accelerator);guest.login()
        checks['fresh_guest_no_marker']=guest.command('test ! -e /tmp/reversium-marker && test ! -e /mnt/host/host-canary.txt')[0]==0
        guest.close(run/'fresh-guest-private.log');guest=None
        guest=Guest(lab,seconds=1,accelerator=accelerator)
        guest.process.wait(timeout=15)
        checks['hard_timeout_stops_process']=guest.expired and guest.process.poll() is not None
        guest.close(run/'timeout-private.log');guest=None
        result['passed']=all(checks.values())
    except Exception as error:
        result['error']=type(error).__name__+': '+str(error)
    finally:
        if guest:guest.close(run/'failed-guest-private.log')
        listener.close()
        result['asset_digests']={name:digest(lab/'downloads'/name,algorithm) for name,(_,algorithm,_) in ASSETS.items()}
        (run/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        (lab/'latest-self-test.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


def sanitize_delivery(archive):
    """Copy reviewed members into another ZIP in memory, never onto the host."""
    from .analyze import inspect_zip
    report=inspect_zip(archive)
    if report['file_review']['counts']['red']:
        raise ValueError('Red file-review signals require review before this experimental run.')
    if any(f['file_review']['integrity']!='crc_checked' for f in report['files']):
        raise ValueError('All members must pass bounded CRC inspection before guest input is prepared.')
    output=io.BytesIO();omitted=[]
    with zipfile.ZipFile(archive) as source, zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as target:
        for member in source.infolist():
            parts=member.filename.replace('\\','/').split('/')
            name=parts[-1].lower()
            if any(p in ('.git','node_modules') for p in parts) or name.startswith('.env') or name in ('.npmrc','.netrc') or name.endswith(('.pem','.key','.p12','.pfx')):
                omitted.append(member.filename);continue
            if member.is_dir():continue
            if member.flag_bits&1 or member.file_size>4*1024*1024:
                raise ValueError('Experimental guest copy requires readable members within 4 MiB.')
            target.writestr(member.filename,source.read(member))
    return output.getvalue(),report['archive_sha256'],omitted


def bundle_files(lab, archive):
    """Validate offline cache identity before copying bytes onto read-only media."""
    lab=Path(lab)
    delivery,source_hash,omitted=sanitize_delivery(archive)
    if len(delivery)>32*1024*1024:raise ValueError('Experimental delivery exceeds 32 MiB.')
    files={'reversium-input':b'Experimental offline application input\n','project.zip':delivery}
    with zipfile.ZipFile(io.BytesIO(delivery)) as z:
        manifests=[n for n in z.namelist() if n.endswith('/package.json') or n=='package.json']
        if len(manifests)!=1:raise ValueError('Pilot requires exactly one root Node project.')
        root=manifests[0][:-len('package.json')]
        package=json.loads(z.read(manifests[0]))
        lock=json.loads(z.read(root+'package-lock.json'))
    expected_build='vite build --configLoader runner && tsc server.ts --outDir dist --module NodeNext --moduleResolution NodeNext --target ES2022 --esModuleInterop --skipLibCheck'
    if package.get('scripts',{}).get('build')!=expected_build or package.get('scripts',{}).get('start')!='node dist/server.js':
        raise ValueError('This pilot supports only the reviewed Tudela build/start profile; arbitrary script execution is not exposed.')
    npm_manifest=json.loads((lab/'npm-packages/manifest.json').read_text(encoding='utf-8'))
    if not 1<=len(npm_manifest)<=1500:raise ValueError('Offline npm cache count invalid.')
    for entry in npm_manifest:
        path=entry['path'];name=entry['file'];sri=entry['integrity']
        if path not in lock['packages'] or lock['packages'][path].get('integrity')!=sri or not path.startswith('node_modules/') or '..' in path.split('/') or not re.fullmatch(r'pkg\d+\.tgz',name):
            raise ValueError('Offline cache does not match the delivery lockfile.')
        algorithm,expected=sri.split('-',1)
        if algorithm not in ('sha512','sha256'):raise ValueError('Unsupported integrity algorithm.')
        data=(lab/'npm-packages'/name).read_bytes()
        if len(data)>128*1024*1024 or base64.b64encode(hashlib.new(algorithm,data).digest()).decode()!=expected:
            raise ValueError('Offline npm tarball integrity mismatch.')
        files[name]=data
    files['npm-manifest.json']=json.dumps(npm_manifest).encode()
    apks=json.loads((lab/'node-packages/manifest.json').read_text(encoding='utf-8'))
    if not 1<=len(apks)<=80:raise ValueError('Offline APK count invalid.')
    for entry in apks:
        name=entry['name']
        if not re.fullmatch(r'[A-Za-z0-9_.+~-]+\.apk',name):raise ValueError('Invalid APK cache filename.')
        data=(lab/'node-packages'/name).read_bytes()
        if hashlib.sha256(data).hexdigest()!=entry['sha256']:raise ValueError('Offline APK cache changed.')
        files[name]=data
    if sum(map(len,files.values()))>256*1024*1024:raise ValueError('Read-only input media exceeds 256 MiB.')
    # All tar extraction and source execution takes place inside the disposable guest.
    install=r"""const fs=require('fs'),cp=require('child_process');
const manifest=JSON.parse(fs.readFileSync('/mnt/input/npm-manifest.json','utf8'));
for(const e of manifest){if(!e.path.startsWith('node_modules/')||e.path.split('/').includes('..')||!/^pkg\d+\.tgz$/.test(e.file))throw Error('Invalid guest install path');fs.mkdirSync(e.path,{recursive:true});const r=cp.spawnSync('tar',['-xzf','/mnt/input/'+e.file,'-C',e.path,'--strip-components=1'],{stdio:'ignore'});if(r.status!==0)throw Error('Guest tar extraction failed');}
console.log('Offline locked libraries unpacked; lifecycle install scripts were not run.');"""
    files['install-libraries.cjs']=install.encode()
    return files,{'source_archive_sha256':source_hash,'sanitized_archive_sha256':hashlib.sha256(delivery).hexdigest(),'omitted_sensitive_or_generated_members':omitted,'project_root':root,'npm_entries':len(npm_manifest),'apk_entries':len(apks)}


def probe_tudela(lab,archive, accelerator="tcg"):
    """A fixed, reviewed build/start experiment; always retest isolation first."""
    lab=verify_lab(lab)
    print('Running fresh blank-guest isolation tests before loading application input…',flush=True)
    isolation=self_test(lab,accelerator=accelerator)
    if isolation.get('passed') is not True:raise RuntimeError('Isolation self-test failed; no application guest was started.')
    files,metadata=bundle_files(lab,archive)
    run=lab/'runs'/('tudela-'+secrets.token_hex(6));run.mkdir(parents=True)
    media=run/'application-input.iso';input_iso(lab,media,files);before=digest(media)
    result={'stage':'experimental offline Tudela build/start','accelerator':accelerator,'isolation_passed':True,'checks':{},'delivery':metadata,
            'scope':'Fixed build/start profile, synthetic configuration, no NIC or host shares. Not a complete platform acceptance, security audit or production deployment.'}
    guest=None
    try:
        print('Booting separate application guest; networking remains absent…',flush=True)
        guest=Guest(lab,media,seconds=600,accelerator=accelerator);guest.login()
        checks=result['checks']
        checks['loopback_only']=guest.command('test "$(ls /sys/class/net)" = lo && test -z "$(ip route)"')[0]==0
        checks['input_mounted']=mount_input(guest)
        if not all(checks.values()):raise RuntimeError('Application guest preflight failed.')
        print('Installing signed Alpine runtime packages offline…',flush=True)
        rc,_=guest.command('apk add --force-non-repository --no-network --repositories-file /dev/null /mnt/input/*.apk',seconds=120)
        checks['signed_runtime_installed']=rc==0
        if rc:raise RuntimeError('Offline signed runtime installation failed; no application code ran.')
        rc,versions=guest.command('node --version; npm --version')
        checks['node_available']=rc==0
        result['runtime_versions']=re.findall(r'(?<![A-Za-z0-9])(v?\d+\.\d+\.\d+)(?=\r?\n)',versions)
        root=metadata['project_root']
        if not re.fullmatch(r'[A-Za-z0-9_./-]*',root):raise ValueError('Project root unsupported by reviewed guest profile.')
        rc,_=guest.command('mkdir -p /work; cd /work && unzip -q /mnt/input/project.zip && cd '+(root or '.')+' && node /mnt/input/install-libraries.cjs',seconds=180)
        checks['libraries_unpacked_without_hooks']=rc==0
        if rc:raise RuntimeError('Offline library unpack failed.')
        print('Building Tudela inside the offline guest…',flush=True)
        env='NODE_OPTIONS=--max-old-space-size=384 VITE_SUPABASE_URL=https://reversium-sandbox.invalid VITE_SUPABASE_PUBLISHABLE_KEY=synthetic-publishable-no-live-key'
        rc,_=guest.command('cd /work/'+(root or '.')+' && '+env+' node node_modules/vite/bin/vite.js build --configLoader runner > /tmp/build.log 2>&1',seconds=240)
        checks['frontend_build']=rc==0
        if rc:
            guest.command('tail -n 30 /tmp/build.log')
            raise RuntimeError('Frontend build failed; private guest log records the blocker.')
        rc,_=guest.command('cd /work/'+(root or '.')+' && NODE_OPTIONS=--max-old-space-size=384 node node_modules/typescript/bin/tsc server.ts --outDir dist --module NodeNext --moduleResolution NodeNext --target ES2022 --esModuleInterop --skipLibCheck > /tmp/typescript.log 2>&1',seconds=180)
        checks['backend_compile']=rc==0
        if rc:
            guest.command('tail -n 30 /tmp/typescript.log')
            raise RuntimeError('Backend compilation failed; private guest log records the blocker.')
        print('Starting compiled server with synthetic offline service configuration…',flush=True)
        rc,_=guest.command('cd /work/'+(root or '.')+' && NODE_ENV=production PORT=18765 APP_URL=https://reversium-app.invalid SUPABASE_URL=https://reversium-sandbox.invalid VITE_SUPABASE_URL=https://reversium-sandbox.invalid SUPABASE_SECRET_KEY=synthetic-server-secret-no-live-key VITE_SUPABASE_PUBLISHABLE_KEY=synthetic-publishable-no-live-key HERZL_MODE=simulator node dist/server.js > /tmp/server.log 2>&1 & echo guest-server-launch-requested')
        # Poll from within the guest; no host forwarding or preview exposure.
        rc,_=guest.command('for n in 1 2 3 4 5 6 7 8 9 10; do wget -q -T 2 -O /tmp/home.html http://127.0.0.1:18765/ && break; sleep 1; done; test -s /tmp/home.html',seconds=60)
        checks['guest_local_home_responded']=rc==0
        guest.command('tail -n 20 /tmp/server.log')
        if not checks['guest_local_home_responded']:raise RuntimeError('Guest-local home page did not respond; see private server log.')
        checks['still_no_external_route']=guest.command('test "$(ls /sys/class/net)" = lo && test -z "$(ip route)"')[0]==0
        result['remaining_gaps']=['No real Supabase/database/auth/storage services provisioned.','Synthetic keys are not live credentials.','No published-tour or authenticated workflow acceptance test.','No host browser preview or host port forwarding.']
    except Exception as error:
        result['blocker']=type(error).__name__+': '+str(error)
    finally:
        if guest:guest.close(run/'application-private.log')
        result['input_media_unchanged']=digest(media)==before
        result['guest_process_stopped']=guest is None or guest.process.poll() is not None
        result['passed']=not result.get('blocker') and all(result['checks'].values()) and result['input_media_unchanged'] and result['guest_process_stopped']
        if not result['passed'] and not result.get('blocker'):result['blocker']='Application or teardown checks did not all pass.'
        (run/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        (lab/'latest-tudela-probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
