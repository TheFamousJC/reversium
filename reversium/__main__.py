import argparse
import json
import socket
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .analyze import inspect_zip
from .report import render, STYLE
from .source import compare_reports
from .sample import sample_archive, javascript_sample_archive
from . import __version__
from .feature_map import render_svg

HOME = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Reversium</title><style>''' + STYLE + '''</style><main><p class="brand">REVERSIUM 0.7.0 / PRIVATE BY DESIGN</p><h1>From archive to understanding.</h1><p>Inspect a ZIP on your computer. Discover source files, dependencies, route candidates and architecture evidence. No accounts, API keys or uploads to a cloud service.</p><p>Understand an unfamiliar software package, trace supported features, and prepare maintenance or migration work. Report sections: What this software does, Architecture, Evidence, and Coverage.</p><p><a href="/example">Open a local sample report</a> to see all four tabs, try the <a href="/example-js">JavaScript/TypeScript sample</a>, or analyze your ZIP below.</p><nav aria-label="Preview report sections"><a class="preview-tab" href="/example#panel-behavior">What this software does</a><a class="preview-tab" href="/example#panel-architecture">Architecture</a><a class="preview-tab" href="/example#panel-evidence">Evidence</a><a class="preview-tab" href="/example#panel-coverage">Coverage</a></nav><form><input aria-label="Choose ZIP archive" type="file" accept=".zip" required><button>Analyze archive</button></form><p id="status" role="status">Maximum ZIP size: 64 MiB. Input code is never executed.</p><p>Python AST analysis · JavaScript/TypeScript import scanning · Platform profile · Supporting services · Static binary inspection</p><script>document.querySelector('form').onsubmit=async e=>{e.preventDefault();const f=document.querySelector('input').files[0],s=document.querySelector('#status'),b=document.querySelector('button');if(f.size>67108864){s.textContent='ZIP exceeds 64 MiB.';return}b.disabled=true;s.textContent='Analyzing locally…';try{const r=await fetch('/analyze',{method:'POST',headers:{'Content-Type':'application/zip'},body:f});if(!r.ok)throw new Error(await r.text());document.open();document.write(await r.text());document.close()}catch(e){s.textContent=e.message;b.disabled=false}};</script></main></html>'''


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, kind='text/html; charset=utf-8'):
        data = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)

    def valid_host(self):
        return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

    def do_GET(self):
        if not self.valid_host():
            return self.send(403, 'Invalid host.')
        if self.path == '/example':
            return self.send(200, render(inspect_zip(sample_archive())))
        if self.path == '/example-js':
            return self.send(200, render(inspect_zip(javascript_sample_archive())))
        if self.path == '/version':
            return self.send(200, json.dumps({'version': __version__}), 'application/json')
        self.send(200, HOME) if self.path == '/' else self.send(404, 'Not found.')

    def do_POST(self):
        expected_origin = f'http://127.0.0.1:{self.server.server_port}'
        if not self.valid_host() or self.headers.get('Origin') not in (None, expected_origin):
            # Drain a bounded upload before closing. Windows can otherwise reset
            # the socket and discard the 403 response when unread data remains.
            self.connection.settimeout(2)
            try:
                remaining = min(max(int(self.headers.get('Content-Length', '0')), 0), 64 * 1024 * 1024)
                while remaining:
                    chunk = self.rfile.read(min(remaining, 65536))
                    if not chunk:
                        break
                    remaining -= len(chunk)
            except (ValueError, OSError):
                pass
            return self.send(403, 'Local requests only.')
        if self.path != '/analyze':
            return self.send(404, 'Not found.')
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 64 * 1024 * 1024:
                return self.send(413, 'ZIP must be between 1 byte and 64 MiB.')
            self.connection.settimeout(30)
            with tempfile.TemporaryFile() as stream:
                remaining = length
                while remaining:
                    chunk = self.rfile.read(min(remaining, 65536))
                    if not chunk:
                        raise ValueError('Incomplete upload.')
                    stream.write(chunk)
                    remaining -= len(chunk)
                stream.seek(0)
                result = inspect_zip(stream)
            self.send(200, render(result))
        except Exception:
            self.send(400, 'Unable to analyze ZIP. Check archive integrity, safe paths, encryption and documented size limits.', 'text/plain; charset=utf-8')


class LocalHTTPServer(ThreadingHTTPServer):
    # Windows can let multiple SO_REUSEADDR listeners bind the same port,
    # causing a newly launched browser to reach an older process.
    allow_reuse_address = False

    def server_bind(self):
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def main():
    parser = argparse.ArgumentParser(description='Reversium local archive analysis')
    parser.add_argument('archive', nargs='?', help='ZIP to inspect; omit to start browser UI')
    parser.add_argument('--output', default='reports', help='CLI report directory')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--compare', help='Prior report.json to compare with CLI analysis')
    args = parser.parse_args()
    if args.archive:
        result = inspect_zip(args.archive)
        if args.compare:
            baseline = Path(args.compare)
            if baseline.stat().st_size > 32 * 1024 * 1024:
                parser.error('Baseline report exceeds 32 MiB.')
            try:
                result['comparison'] = compare_reports(result, json.loads(baseline.read_text(encoding='utf-8')))
            except (ValueError, KeyError, TypeError) as error:
                parser.error(f'Invalid baseline report: {error}')
        output = Path(args.output)
        output.mkdir(parents=True, exist_ok=True)
        (output / 'report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        (output / 'report.html').write_text(render(result), encoding='utf-8')
        (output / 'feature-map.svg').write_text(render_svg(result['feature_map'], result.get('comparison', {}).get('feature_map'))[0], encoding='utf-8')
        print(f'Reports saved to {output.resolve()}')
        return
    try:
        server = LocalHTTPServer(('127.0.0.1', args.port), Handler)
    except OSError:
        if args.port != 8765:
            raise
        print('Default port is busy. Starting this version on a free port instead of using an older server.', flush=True)
        server = LocalHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads = True
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'Reversium {__version__}: {url} (Ctrl+C to stop)', flush=True)
    if not args.no_browser:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
