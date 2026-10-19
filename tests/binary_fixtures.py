"""Synthetic metadata-only fixtures. They contain no executable program logic."""
import io
import struct
import zipfile


def pe_fixture():
    data = bytearray(1024)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 0x3c, 0x80)
    data[0x80:0x84] = b'PE\0\0'
    struct.pack_into('<HH', data, 0x84, 0x8664, 1)
    struct.pack_into('<H', data, 0x94, 240)
    optional = 0x98
    struct.pack_into('<H', data, optional, 0x20b)
    struct.pack_into('<I', data, optional + 108, 16)
    struct.pack_into('<II', data, optional + 112 + 8, 0x1000, 40)
    struct.pack_into('<II', data, optional + 112 + 14 * 8, 0x1100, 72)
    section = optional + 240
    struct.pack_into('<IIII', data, section + 8, 512, 0x1000, 512, 512)
    struct.pack_into('<IIIII', data, 512, 0, 0, 0, 0x1050, 0)
    data[592:605] = b'KERNEL32.dll\0'
    data[700:734] = b'https://user:pass@example.test/path'
    return bytes(data)


def elf_fixture():
    data = bytearray(512)
    ident = b'\x7fELF\x02\x01\x01' + b'\0' * 9
    struct.pack_into('<16sHHIQQQIHHHHHH', data, 0, ident, 3, 62, 1, 0, 0, 64, 0, 64, 0, 0, 64, 3, 0)
    struct.pack_into('<IIQQQQIIQQ', data, 128, 0, 6, 0, 0, 256, 32, 2, 0, 8, 16)
    struct.pack_into('<IIQQQQIIQQ', data, 192, 0, 3, 0, 0, 320, 32, 0, 0, 1, 0)
    struct.pack_into('<qQqQ', data, 256, 1, 1, 0, 0)
    data[320:331] = b'\0libc.so.6\0'
    return bytes(data)


def java_fixture():
    name = b'java/lang/Object'
    return b'\xca\xfe\xba\xbe' + struct.pack('>HHH', 0, 61, 3) + b'\x01' + struct.pack('>H', len(name)) + name + b'\x07\x00\x01'


def container_fixture(apk=False):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        if apk:
            archive.writestr('AndroidManifest.xml', b'fixture')
            archive.writestr('classes.dex', b'not executed')
        else:
            archive.writestr('META-INF/MANIFEST.MF', b'Manifest-Version: 1.0')
            archive.writestr('Example.class', java_fixture())
    return buffer.getvalue()
