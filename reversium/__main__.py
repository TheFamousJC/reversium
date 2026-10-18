import argparse
import json
import socket
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .sandbox import capabilities, prepare as prepare_sandbox
from .analyze import inspect_zip
from .report import render, STYLE
from .presentation import STYLE as MODERN_STYLE, SCRIPT as HELP_SCRIPT
from .source import compare_reports
from .sample import sample_archive, javascript_sample_archive
from . import __version__
from .feature_map import render_svg
from .assistant import Assistant
from .help_ui import ABOUT, EXPORT_HELP, FAQ_GENERAL
from .assistant_ui import PANEL as AI_PANEL, STYLE as AI_STYLE, SCRIPT as AI_SCRIPT, FAQ_AI
from urllib.parse import urlsplit, parse_qs, unquote
import secrets
import html
import re
from urllib.error import HTTPError

from .start_ui import render_start

HOME = render_start(STYLE + AI_STYLE + MODERN_STYLE, HELP_SCRIPT)


class Handler(BaseHTTPRequestHandler):
    # Successful responses have explicit Content-Length and can reuse the socket.
    # Avoid closing immediately after a large send: Windows clients can otherwise
    # observe a reset while still consuming the response body.
    protocol_version = 'HTTP/1.1'

    def log_message(self, format, *args):
        # OAuth callback query contains a code; never include request URLs in logs.
        if not self.path.startswith('/auth/callback'):
            super().log_message(format, *args)

    def send(self, code, body, kind='text/html; charset=utf-8'):
        if kind.startswith('text/html'):
            body = body.replace('<!--assistant-session-->', '<meta name="assistant-session" content="' + self.server.assistant_session + '">')
        data = body.encode('utf-8') if isinstance(body,str) else body
        self.send_response(code)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(data)))
        if code >= 400:
            # Rejected/invalid requests may retain unread input. Never reuse them.
            self.close_connection = True
        if self.close_connection:
            self.send_header('Connection', 'close')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)
        self.wfile.flush()

    def valid_host(self):
        return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

    def do_GET(self):
        documents={'/docs/user-guide.html':('docs/user-guide.html','text/html; charset=utf-8'),'/docs/market-position.html':('docs/market-position.html','text/html; charset=utf-8'),'/output/pdf/Reversium-User-Guide.pdf':('output/pdf/Reversium-User-Guide.pdf','application/pdf')}
        if self.path in documents:
            path,kind=documents[self.path]
            source=Path(__file__).resolve().parents[1]/path
            return self.send(200,source.read_text(encoding='utf-8') if kind.startswith('text/') else source.read_bytes(),kind)
        if not self.valid_host():
            return self.send(403, 'Invalid host.')
        if urlsplit(self.path).path == '/auth/callback':
            try:
                self.server.assistant.callback(parse_qs(urlsplit(self.path).query))
                message = 'Connected. Return to your Reversium tab and choose Check connection. No report evidence was shared.'
            except Exception:
                message = 'Connection could not be completed. Check account eligibility, optional dependencies and consent, then start again. Local analysis still works.'
            return self.send(200, '<!doctype html><meta charset="utf-8"><title>Reversium connection</title><p>' + html.escape(message) + '</p>')
        if self.path == '/example':
            result = inspect_zip(sample_archive())
            result['example'] = True
            return self.send(200, render(result))
        if self.path == '/example-js':
            result = inspect_zip(javascript_sample_archive())
            result['example'] = True
            return self.send(200, render(result))
        if self.path == '/sandbox/status':
            return self.send(200, json.dumps(capabilities()), 'application/json')
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
        if self.path.startswith('/assistant/'):
            if self.headers.get('Origin') != expected_origin or self.headers.get('X-Reversium-Session') != self.server.assistant_session:
                self.connection.settimeout(2)
                try:
                    self.rfile.read(min(max(int(self.headers.get('Content-Length', '0')), 0), 100000))
                except (ValueError, OSError):
                    pass
                return self.send(403, 'Assistant requests require this local browser session.')
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 100000:
                    raise ValueError('Assistant request exceeds 100 KB.')
                self.connection.settimeout(90)
                body = json.loads(self.rfile.read(length))
                assistant = self.server.assistant
                if self.path == '/assistant/status':
                    result = assistant.status()
                elif self.path == '/assistant/connect':
                    result = {'url': assistant.begin(expected_origin)}
                elif self.path == '/assistant/disconnect':
                    assistant.disconnect()
                    result = assistant.status()
                elif self.path == '/assistant/ask':
                    result = assistant.ask(body)
                else:
                    return self.send(404, 'Not found.')
                return self.send(200, json.dumps(result), 'application/json')
            except HTTPError as error:
                # Provider diagnostics must never echo tokens, evidence or raw bodies.
                details = []
                try:
                    provider = json.loads(error.read(65536)).get('error', {})
                    if isinstance(provider, dict):
                        for key in ('code', 'type', 'param'):
                            value = provider.get(key)
                            if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', value):
                                details.append(key + '=' + value)
                except (ValueError, OSError, AttributeError):
                    pass
                message = 'OpenAI returned HTTP ' + str(error.code)
                if details:
                    message += ' (' + ', '.join(details) + ')'
                message += '. Request failed; no automatic retry or API billing fallback.'
                return self.send(502, json.dumps({'error': message}), 'application/json')
            except ValueError as error:
                return self.send(400, json.dumps({'error': str(error)}), 'application/json')
            except Exception:
                return self.send(502, json.dumps({'error': 'Account service unavailable or response invalid. Check sign-in, connectivity and plan limits. No automatic retry or API billing fallback.'}), 'application/json')
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
                goal = self.headers.get('X-Reversium-Goal', 'understand')
                result['user_goal'] = goal if goal in ('understand', 'handover', 'change') else 'understand'
                name = unquote(self.headers.get('X-Reversium-Archive-Name', 'Uploaded software package'))
                result['archive_name'] = ''.join(c for c in name if c.isprintable())[:200]
            self.send(200, render(result))
        except Exception:
            self.send(400, 'ZIP blocked or unreadable. Check archive integrity, safe paths, encryption/compression and documented size limits. No ZIP code was executed.', 'text/plain; charset=utf-8')


class LocalHTTPServer(ThreadingHTTPServer):
    # Windows can let multiple SO_REUSEADDR listeners bind the same port,
    # causing a newly launched browser to reach an older process.
    allow_reuse_address = False

    def __init__(self, *args, **kwargs):
        self.assistant = Assistant()
        self.assistant_session = secrets.token_urlsafe(32)
        super().__init__(*args, **kwargs)

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
    parser.add_argument('--sandbox-check', action='store_true', help='Read local backend availability; no execution')
    parser.add_argument('--sandbox-plan', metavar='NEW_DIRECTORY', help='Write offline preparation profiles; never boot or run ZIPs')
    parser.add_argument('--sandbox-lab', default='reports/qemu-lab', help='Private QEMU lab directory (not uploaded or published)')
    parser.add_argument('--sandbox-accelerator', choices=['tcg','whpx'], default='tcg', help='Explicit local CPU backend; WHPX requires already enabled Windows hypervisor support')
    parser.add_argument('--sandbox-self-test', action='store_true', help='Explicitly boot benign offline guests and test isolation/teardown')
    parser.add_argument('--sandbox-tudela', metavar='ZIP', help='Experimental fixed Tudela build/start profile; retests isolation first')
    args = parser.parse_args()
    actions=sum(bool(x) for x in (args.sandbox_check,args.sandbox_plan,args.sandbox_self_test,args.sandbox_tudela))
    if actions>1 or (actions and args.archive):
        parser.error('Choose exactly one sandbox action, separately from archive analysis.')
    if args.sandbox_self_test or args.sandbox_tudela:
        from .qemu_lab import self_test, probe_tudela
        try:
            result=probe_tudela(args.sandbox_lab,args.sandbox_tudela,accelerator=args.sandbox_accelerator) if args.sandbox_tudela else self_test(args.sandbox_lab,accelerator=args.sandbox_accelerator)
        except (OSError,ValueError,ImportError,RuntimeError) as error:
            parser.error('Sandbox stopped: '+str(error))
        print(json.dumps(result,indent=2))
        if result.get('passed') is False or result.get('blocker'):
            parser.exit(1)
        return
    if args.sandbox_check or args.sandbox_plan:
        if args.archive or (args.sandbox_check and args.sandbox_plan):
            parser.error('Sandbox preparation/check is separate from ZIP analysis; choose one action.')
        try:
            status = prepare_sandbox(args.sandbox_plan) if args.sandbox_plan else capabilities()
        except OSError as error:
            parser.error('Cannot write sandbox plan: ' + str(error))
        print(json.dumps(status, indent=2))
        return
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
