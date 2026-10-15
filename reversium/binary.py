"""Bounded static binary readers. Never load, disassemble or execute input code."""
import io
import re
import struct
import zipfile
from urllib.parse import urlsplit

VERSION = 'reversium-static/1'
MAX_STRINGS = 80


def identify(data):
    if data.startswith(b'MZ'):
        return 'PE candidate'
    if data.startswith(b'\x7fELF'):
        return 'ELF'
    if data.startswith(b'\xca\xfe\xba\xbe'):
        # Java version occupies these bytes; Mach-O universal binaries use nfat_arch.
        return 'Java class' if len(data) >= 8 and int.from_bytes(data[6:8], 'big') >= 45 else 'Mach-O universal'
    if data[:4] in (b'\xfe\xed\xfa\xce', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xcf\xfa\xed\xfe'):
        return 'Mach-O'
    if data.startswith(b'dex\n'):
        return 'DEX'
    if data.startswith(b'PK\x03\x04') or data.startswith(b'PK\x05\x06'):
        return 'ZIP container'
    return None


class Reader:
    def __init__(self, data):
        self.data = data

    def unpack(self, fmt, offset):
        size = struct.calcsize(fmt)
        if offset < 0 or offset + size > len(self.data):
            raise ValueError('Truncated or invalid header/table offset')
        return struct.unpack_from(fmt, self.data, offset)

    def string(self, offset, end=None):
        end = min(end if end is not None else len(self.data), len(self.data), offset + 256)
        if not 0 <= offset < end:
            raise ValueError('Invalid string offset')
        stop = self.data.find(b'\0', offset, end)
        if stop == -1:
            raise ValueError('Unterminated metadata string')
        return self.data[offset:stop].decode('ascii', errors='replace')


def inspect_binary(data, name, hint=None):
    fmt = identify(data)
    if fmt is None and not hint:
        return None
    metadata = {'format': fmt or 'Unknown binary candidate', 'analyzer': VERSION, 'status': 'complete', 'notes': []}
    findings = []
    reader = Reader(data)

    def emit(kind, value, offset, confidence='observed'):
        findings.append({'kind': kind, 'value': str(value)[:200], 'confidence': confidence,
                         'evidence': {'file': name, 'offset': offset}})

    emit('binary_format', metadata['format'], 0, 'heuristic' if fmt in (None, 'PE candidate') else 'observed')
    try:
        if fmt == 'PE candidate':
            pe, = reader.unpack('<I', 0x3c)
            if data[pe:pe + 4] != b'PE\0\0':
                raise ValueError('MZ marker without valid PE signature')
            machine, sections = reader.unpack('<HH', pe + 4)
            optional_size, = reader.unpack('<H', pe + 20)
            optional = pe + 24
            magic, = reader.unpack('<H', optional)
            if magic not in (0x10b, 0x20b):
                raise ValueError('Unsupported PE optional header')
            reader.unpack(f'{optional_size}s', optional)
            metadata.update(format='PE', bits=64 if magic == 0x20b else 32,
                            architecture={0x14c: 'x86', 0x8664: 'x86-64', 0xaa64: 'ARM64', 0x1c4: 'ARM'}.get(machine, f'machine {machine}'), target='Windows')
            emit('binary_architecture', metadata['architecture'], pe + 4)
            table = optional + optional_size
            if sections > 96:
                raise ValueError('PE section count exceeds reader limit (96)')
            mapped = []
            for index in range(sections):
                size, rva, raw_size, raw = reader.unpack('<IIII', table + index * 40 + 8)
                mapped.append((rva, raw_size, raw))

            def offset(rva):
                for start, size, raw in mapped:
                    if start <= rva < start + size and raw + rva - start < len(data):
                        return raw + rva - start
                raise ValueError('Unmapped PE RVA')

            directories = optional + (112 if magic == 0x20b else 96)
            count_offset = optional + (108 if magic == 0x20b else 92)
            if count_offset + 4 > optional + optional_size:
                raise ValueError('Truncated PE data-directory header')
            count, = reader.unpack('<I', count_offset)
            if count > 14 and directories + 15 * 8 <= optional + optional_size:
                clr, clr_size = reader.unpack('<II', directories + 14 * 8)
                if clr and clr_size:
                    metadata['managed'] = True
                    emit('runtime_candidate', '.NET CLR directory present', directories + 14 * 8)
            if count > 1 and directories + 16 <= optional + optional_size:
                imports, size = reader.unpack('<II', directories + 8)
                if imports and size:
                    start = offset(imports)
                    terminated = False
                    for index in range(min(size // 20, 256)):
                        entry = start + index * 20
                        descriptor = reader.unpack('<IIIII', entry)
                        if not any(descriptor):
                            terminated = True
                            break
                        location = offset(descriptor[3])
                        emit('binary_import', reader.string(location), location)
                    if not terminated:
                        metadata['notes'].append('PE import list truncated or missing terminator (limit 256).')
        elif fmt == 'ELF':
            if len(data) < 16 or data[4] not in (1, 2) or data[5] not in (1, 2):
                raise ValueError('Invalid ELF class or byte order')
            bits = 64 if data[4] == 2 else 32
            endian = '<' if data[5] == 1 else '>'
            reader.unpack(endian + ('16sHHIQQQIHHHHHH' if bits == 64 else '16sHHIIIIIHHHHHH'), 0)
            machine, = reader.unpack(endian + 'H', 18)
            metadata.update(bits=bits, architecture={3: 'x86', 62: 'x86-64', 40: 'ARM', 183: 'ARM64', 243: 'RISC-V'}.get(machine, f'machine {machine}'), target='ELF-compatible OS (not determined)')
            emit('binary_architecture', metadata['architecture'], 18)
            shoff, = reader.unpack(endian + ('Q' if bits == 64 else 'I'), 40 if bits == 64 else 32)
            entsize, count = reader.unpack(endian + 'HH', 58 if bits == 64 else 46)
            if count > 4096:
                raise ValueError('ELF section count exceeds reader limit (4096)')
            if count and entsize < (64 if bits == 64 else 40):
                raise ValueError('Invalid ELF section entry size')
            sections = []
            for index in range(count):
                fields = reader.unpack(endian + ('IIQQQQIIQQ' if bits == 64 else 'IIIIIIIIII'), shoff + index * entsize)
                sections.append(fields)
            for fields in sections:
                if fields[1] != 6:  # SHT_DYNAMIC
                    continue
                start, size, link = fields[4], fields[5], fields[6]
                if link >= len(sections):
                    raise ValueError('Invalid ELF string table link')
                strings = sections[link]
                if size // (16 if bits == 64 else 8) > 4096:
                    metadata['notes'].append('ELF dynamic entries capped at 4096 per section.')
                for index in range(min(size // (16 if bits == 64 else 8), 4096)):
                    location = start + index * (16 if bits == 64 else 8)
                    tag, value = reader.unpack(endian + ('qQ' if bits == 64 else 'iI'), location)
                    if tag == 0:
                        break
                    if tag == 1:
                        if value >= strings[5]:
                            raise ValueError('Invalid ELF dependency string index')
                        off = strings[4] + value
                        emit('binary_import', reader.string(off, strings[4] + strings[5]), off)
            if not count:
                metadata['notes'].append('No section table: ELF dynamic imports not inspected; program-header parsing is not implemented.')
        elif fmt == 'Java class':
            minor, major, count = reader.unpack('>HHH', 4)
            metadata.update(runtime=f'Java class major {major}', major=major, minor=minor)
            emit('runtime_candidate', metadata['runtime'], 6)
            cursor, index, pool, references = 10, 1, {}, []
            while index < count:
                tag, = reader.unpack('>B', cursor)
                cursor += 1
                if tag == 1:
                    size, = reader.unpack('>H', cursor)
                    cursor += 2
                    raw, = reader.unpack(f'{size}s', cursor)
                    pool[index] = (raw.decode('utf-8', errors='replace'), cursor)
                    cursor += size
                elif tag == 7:
                    value, = reader.unpack('>H', cursor)
                    references.append(value)
                    cursor += 2
                else:
                    size = {3: 4, 4: 4, 5: 8, 6: 8, 8: 2, 9: 4, 10: 4, 11: 4, 12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}.get(tag)
                    if size is None:
                        raise ValueError('Unsupported Java constant pool tag')
                    reader.unpack(f'{size}s', cursor)
                    cursor += size
                    if tag in (5, 6):
                        index += 1
                index += 1
            for ref in references[:256]:
                if ref not in pool:
                    raise ValueError('Invalid Java class-name reference')
                value, location = pool[ref]
                emit('binary_class_reference', value, location)
            if len(references) > 256:
                metadata['notes'].append('Java class references capped at 256.')
        elif fmt == 'DEX':
            reader.unpack('112s', 0)
            if not re.fullmatch(rb'dex\n\d{3}\0', data[:8]):
                raise ValueError('Invalid DEX magic/version header')
            header_size, endian = reader.unpack('<II', 36)
            if header_size != 112 or endian != 0x12345678:
                raise ValueError('Unsupported DEX header size or endian tag')
            metadata['runtime'] = 'Android DEX'
            metadata['notes'].append('DEX header only; code and type tables are not inspected.')
            emit('runtime_candidate', 'Android DEX header', 0)
        elif fmt in ('Mach-O', 'Mach-O universal'):
            reader.unpack('28s' if fmt == 'Mach-O' else '8s', 0)
            metadata['target'] = 'Apple Mach-O target (OS not determined)'
            metadata['notes'].append('Mach-O header identification only; load commands are not inspected.')
        elif fmt == 'ZIP container':
            with zipfile.ZipFile(io.BytesIO(data)) as nested:
                members = nested.infolist()
                if len(members) > 10000:
                    raise ValueError('Nested container exceeds 10,000 entries')
                names = {m.filename for m in members}
                apk = 'AndroidManifest.xml' in names and any(n.endswith('.dex') for n in names)
                jar = 'META-INF/MANIFEST.MF' in names or any(n.endswith('.class') for n in names)
                metadata['format'] = 'APK container' if apk else 'JAR-like container' if jar else 'ZIP container'
                for member in members[:80]:
                    emit('container_member', member.filename, member.header_offset)
                metadata['notes'].append('Container directory inspected only; nested members are not decompressed or executed. Maximum 80 member findings.')
        else:
            metadata['status'] = 'unsupported'
            metadata['notes'].append('Extension suggests a binary, but no supported signature was recognized.')
    except (ValueError, struct.error, zipfile.BadZipFile, OverflowError) as error:
        metadata['status'] = 'partial'
        metadata['notes'].append(str(error))

    findings[0]['value'] = metadata['format']
    if metadata['format'] == 'PE':
        findings[0]['confidence'] = 'observed'

    # Bounded samples, not a dump of all printable content. Never treat strings as behavior.
    if fmt != 'ZIP container':
        for index, match in enumerate(re.finditer(rb'[\x20-\x7e]{8,}', data)):
            if index >= MAX_STRINGS:
                metadata['notes'].append('Printable string sample capped at 80 entries.')
                break
            text = match.group()[:160].decode('ascii')
            if re.search(r'(?i)(password|secret|token|api[_-]?key|authorization)\s*[:=]', text):
                text = '[credential-like string omitted]'
            elif '://' in text:
                hosts = []
                for url in re.findall(r'https?://[^\s<>"\']+', text):
                    try:
                        host = urlsplit(url).hostname
                        if host:
                            hosts.append(host)
                    except ValueError:
                        pass
                text = 'URL host candidates: ' + ', '.join(hosts) if hosts else '[URL-like string omitted]'
            emit('binary_string_candidate', text, match.start(), 'heuristic')
    return metadata, findings
