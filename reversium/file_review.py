"""Bounded triage signals, not malware detection or an execution approval."""
import html
import re
from pathlib import PurePosixPath

ACTIVE = {'.exe', '.dll', '.so', '.dylib', '.apk', '.jar', '.scr', '.com', '.msi', '.ps1', '.bat', '.cmd', '.vbs', '.sh', '.wsf', '.hta', '.docm', '.xlsm'}
TEXT = {'.py', '.js', '.jsx', '.ts', '.tsx', '.sh', '.ps1', '.bat', '.cmd', '.vbs', '.php'}
PASSIVE = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf', '.txt', '.csv'}
MAX_SCAN = 256 * 1024
PATTERNS = [
    ('download_execute', re.compile(r'\b(?:curl|wget|iwr|irm|invoke-webrequest|invoke-restmethod)\b[^\n]{0,2000}\|\s*(?:bash|sh|iex|invoke-expression|powershell)\b', re.I), 'Download piped to an interpreter; review before running.'),
    ('encoded_powershell', re.compile(r'\b(?:powershell|pwsh)(?:\.exe)?\b[^\n]{0,500}\s-(?:enc|encodedcommand)\s+[A-Za-z0-9+/=]{40,}', re.I), 'Encoded PowerShell command candidate; contents and intent unverified.'),
    ('decode_execute', re.compile(r'\b(?:exec|eval)\s*\(\s*(?:(?:base64\.)?b64decode|atob)\s*\(', re.I), 'Decoded content passed directly to execution; review the source.'),
]


def signal(item, level, code, reason, line=None):
    review = item.setdefault('file_review', {'level': 'green', 'integrity': 'not_checked', 'content_check': 'not_checked', 'signals': []})
    if code not in {s['code'] for s in review['signals']}:
        evidence = {'file': item['path']}
        if line is not None:
            evidence['line'] = line
        review['signals'].append({'level': level, 'code': code, 'reason': reason, 'evidence': evidence})
    review['level'] = max([review['level'], level], key={'green': 0, 'yellow': 1, 'red': 2}.get)


def inspect_name(item):
    item['file_review'] = {'level': 'green', 'integrity': 'not_checked', 'content_check': 'not_checked', 'signals': []}
    name = item['path'].lower()
    suffix = PurePosixPath(name).suffix
    if suffix in ACTIVE:
        signal(item, 'yellow', 'active_file', 'Executable, installer, script or macro-enabled format: capability to run code is not evidence of malware.')
    if suffix in ACTIVE | {'.js'} and re.search(r'\.(?:pdf|docx?|xlsx?|jpe?g|png|txt)\.[^.]+$', name):
        signal(item, 'red', 'disguised_name', 'Document/image-looking name with an active final extension; possible disguise.')
    if any(c in name for c in '\u202a\u202b\u202d\u202e\u202c\u2066\u2067\u2068\u2069'):
        signal(item, 'red', 'direction_control', 'Filename contains bidirectional display controls that can disguise its extension.')


def inspect_content(item, data):
    suffix = PurePosixPath(item['path']).suffix.lower()
    review = item['file_review']
    review['integrity'] = 'crc_checked'
    if suffix in PASSIVE and data.startswith((b'MZ', b'\x7fELF')):
        signal(item, 'red', 'signature_mismatch', 'Executable signature candidate in a document/image/text-named file; possible disguise, not confirmed malware.')
    if data.startswith((b'PK\x03\x04', b'PK\x05\x06')):
        signal(item, 'yellow', 'nested_container', 'Nested container contents have not received this file-risk review; outer CRC does not validate nested members.')
    if suffix not in TEXT:
        review['content_check'] = 'signature_only'
        signal(item, 'yellow', 'limited_reader', 'CRC and selected file-header signatures checked; this format has no source risk-pattern reader.')
        return
    review['content_check'] = 'bounded_patterns'
    review['pattern_bytes_checked'] = min(len(data), MAX_SCAN)
    if len(data) > MAX_SCAN:
        signal(item, 'yellow', 'pattern_limit', 'Risk-pattern scan limited to the first 256 KiB; remaining content unreviewed.')
    try:
        text = data[:MAX_SCAN].decode('utf-8-sig')
    except UnicodeDecodeError:
        signal(item, 'yellow', 'encoding_unknown', 'Risk-pattern text reader could not decode this content as UTF-8; validity remains unknown.')
        return
    for code, pattern, reason in PATTERNS:
        match = pattern.search(text)
        if match:
            signal(item, 'red', code, reason + ' Comments and examples can match; this is a review signal, not a malware verdict.', text.count('\n', 0, match.start()) + 1)


def finish_review(report):
    counts = dict.fromkeys(('green', 'yellow', 'red'), 0)
    for item in report['files']:
        review = item['file_review']
        if item['analysis'] == 'parse_failed':
            signal(item, 'yellow', 'parse_failed', 'Supported source parser failed: file may be incomplete, invalid or use unsupported syntax.')
        binary = item.get('binary', {})
        if binary.get('status') in ('partial', 'unsupported'):
            signal(item, 'yellow', 'binary_incomplete', 'Binary reader was partial or unsupported; possible damage or unsupported format, not confirmed corruption.')
        counts[review['level']] += 1
        for entry in review['signals']:
            entry['finding_index'] = len(report['findings'])
            report['findings'].append({'kind': 'file_review_signal', 'value': entry['code'] + ': ' + entry['reason'], 'confidence': 'review signal; not a malware verdict', 'evidence': entry['evidence']})
    report['file_review'] = {'version': 1, 'counts': counts, 'scope': 'Bounded static triage, not antivirus, a vulnerability audit or permission to execute. CRC detects some accidental damage, not malicious modification. No malware-signature database, digital-signature verification, reputation service or runtime behavior checks. Green means no signals from the supported checks, never guaranteed safe.'}


def panel(report):
    esc = lambda v: html.escape(str(v), quote=True)
    review = report.get('file_review')
    if not review:
        return '<h2>File alerts unavailable</h2><p>Re-analyze the original ZIP with this version to obtain file-review checks.</p>'
    rows = []
    for item in sorted(report['files'], key=lambda f: ({'red': 0, 'yellow': 1, 'green': 2}[f['file_review']['level']], f['path'])):
        r = item['file_review']
        name = ''.join('\\u%04x' % ord(c) if c in '\u202a\u202b\u202d\u202e\u202c\u2066\u2067\u2068\u2069' else c for c in item['path'])
        notes = ' '.join('<a class="evidence-link" href="#finding-' + str(s['finding_index']) + '">' + esc(s['reason']) + '</a>' for s in r['signals']) or 'No signals from supported checks. Not guaranteed safe.'
        rows.append('<tr data-integrity-problem="' + str(any(x['code'] in ('integrity_failed','parse_failed','binary_incomplete') for x in r['signals'])).lower() + '" data-file-review="' + r['level'] + '"><td><span class="risk-light risk-' + r['level'] + '">' + r['level'].upper() + '</span></td><td>' + esc(name) + '</td><td>' + esc({'crc_checked':'CRC passed','failed':'Integrity failed','not_checked':'Integrity not checked'}[r['integrity']]) + ' / ' + esc({'not_checked':'No content checks','signature_only':'File-header checks only','bounded_patterns':'Bounded text-pattern checks'}[r['content_check']]) + '</td><td>' + notes + '</td></tr>')
    counts = review['counts']
    integrity_counts = {status: sum(f['file_review']['integrity'] == status for f in report['files']) for status in ('crc_checked', 'failed', 'not_checked')}
    return ('<h2>File alerts: review before running</h2><p>Green: no signals in the supported checks. Yellow: possible corruption, active content or incomplete inspection. Red: potentially dangerous pattern or disguise requiring investigation. Red is not confirmed malware; yellow does not prove corruption.</p><p>' + esc(review['scope']) + '</p><p class="risk-summary">' + ' · '.join(level.upper() + ': ' + str(counts[level]) for level in ('red', 'yellow', 'green')) + '</p><p>ZIP member integrity: ' + str(integrity_counts['crc_checked']) + ' CRC checked; ' + str(integrity_counts['failed']) + ' failed; ' + str(integrity_counts['not_checked']) + ' unverified. CRC is not a malware check.</p><nav aria-label="File alert filters"><button data-risk-filter="all">All files</button><button data-risk-filter="red">Red alerts</button><button data-risk-filter="yellow">Yellow alerts</button><button data-risk-filter="integrity">Possible damage / invalid format</button><button data-risk-filter="green">Green checks</button></nav><p id="risk-count" role="status">All ' + str(len(rows)) + ' files shown.</p><div class="scroll"><table id="risk-table"><thead><tr><th>Signal</th><th>File</th><th>Checks</th><th>Reason / evidence</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div><h2>Can I run this in a sandbox?</h2><p>Execution is not available in this release. Browser analysis never runs uploaded software. A future local companion could prepare a disposable VM with networking, clipboard and host-write access disabled by default, no live credentials and manual approval of setup commands. A container alone is not our proposed boundary for untrusted programs.</p><p>Windows Sandbox is an option on supported Windows Pro, Enterprise and Education editions, but not Home; an existing compatible machine is required. Isolated Linux VMs are another route. Dependencies, operating-system compatibility and external services still need preparation; offline isolation may prevent the application from working. No isolation option guarantees zero risk. Do not interpret the traffic light as permission to run.</p><p><a href="https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/" target="_blank" rel="noopener noreferrer">Microsoft Windows Sandbox guidance</a> · <a href="https://docs.docker.com/engine/security/" target="_blank" rel="noopener noreferrer">Docker isolation considerations</a></p>')


SCRIPT = r"""
for(const button of document.querySelectorAll('[data-risk-filter]'))button.onclick=()=>{for(const other of document.querySelectorAll('[data-risk-filter]'))other.setAttribute('aria-pressed',String(other===button));let shown=0;for(const row of document.querySelectorAll('#risk-table tbody tr')){row.hidden=button.dataset.riskFilter==='integrity'?row.dataset.integrityProblem!=='true':button.dataset.riskFilter!=='all'&&row.dataset.fileReview!==button.dataset.riskFilter;if(!row.hidden)shown++;}document.querySelector('#risk-count').textContent=shown+' files shown. No signals is not a guarantee of safety.';};
"""
