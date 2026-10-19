"""Build a harmless mixed archive for CLI/browser verification."""
import sys
import zipfile
from pathlib import Path
from binary_fixtures import pe_fixture, elf_fixture, java_fixture, container_fixture


def main():
    output = Path(sys.argv[1] if len(sys.argv) > 1 else 'reports/binary-fixture.zip')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w') as archive:
        archive.writestr('windows/renamed.data', pe_fixture())
        archive.writestr('linux/service', elf_fixture())
        archive.writestr('java/Example.class', java_fixture())
        archive.writestr('android/sample.apk', container_fixture(True))
        archive.writestr('broken.exe', b'MZ')
        archive.writestr('requirements.txt', 'FastAPI\npsycopg>=3\nredis>=5\n')
        archive.writestr('app.py', 'from fastapi import FastAPI\napp = FastAPI()\n@app.get("/health")\ndef health(): return {"ok": True}\n')
        archive.writestr('compose.yaml', 'services:\n  database:\n    image: postgres:16\n  cache:\n    image: redis:7\n')
    print(output.resolve())


if __name__ == '__main__':
    main()
