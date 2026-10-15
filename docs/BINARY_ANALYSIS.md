# Static binary inspection

Reversium v0.3.0 uses its own dependency-free reader, `reversium-static/1`. It does not invoke executable files, loaders, package managers, debuggers or external decompilers. Input bytes remain in memory; archive files are not extracted. No paid software, model or API is required.

## Coverage

| Format | Supported inspection | Not implemented |
| --- | --- | --- |
| PE | MZ/PE signatures, 32/64-bit header, machine, CLR-directory presence, ordinary imported DLL names | Function imports, delay imports, CLR assembly reconstruction, disassembly |
| ELF | 32/64-bit and byte order, machine, DT_NEEDED names via section-linked dynamic/string tables | Program-header-only imports, symbol resolution, disassembly, definitive OS detection |
| Java class | Magic/version, constant pool class-name references | Methods, original source, complete class validation; modified UTF-8 decoding uses replacement for unsupported sequences |
| DEX | Signature/version/header shape | Types, methods, code, decompilation |
| Mach-O | Magic/header identification, including universal-file candidate | CPU/load commands, imports, code |
| APK/JAR-like ZIP | Signature and central-directory markers/member names | Nested extraction, Android manifest parsing, nested class/DEX analysis |
| Unknown extension candidate | Explicit unsupported result and bounded strings | Format reconstruction |

Files without executable extensions can be detected by signature. Extension-only candidates remain candidates. Reader status `complete` means that the supported inspection completed; it does not mean that the complete binary is valid or can run. `partial` preserves findings from malformed or unsupported structures. `unsupported` means no supported format signature was found for an extension candidate.

## Limits and evidence

- Existing 4 MiB member-content and 200:1 compression limits apply. Larger binaries are inventoried without content inspection or signature detection. Other inventory/upload limits remain unchanged.
- At most 96 PE sections and 256 import descriptors are inspected. ELF is limited to 4,096 sections and 4,096 dynamic entries per section. Java output is capped at 256 class references.
- Nested ZIP directories are limited to 10,000 entries and 80 output members; no nested content is decompressed.
- Printable ASCII samples are capped at 80 entries and 160 characters each. They are labeled heuristic. UTF-16 strings are not extracted. Recognized credential assignments are omitted, and URL-like samples retain host candidates only. This is not a comprehensive secret scrubber; inspect reports before sharing.
- Evidence uses zero-based byte offsets within the member file. Nested-container offsets refer to local ZIP headers in that container, not the outer ZIP. Source findings retain one-based lines.
- Imported DLL/library names and class references describe file metadata, not guaranteed runtime behavior. Packed/encrypted/obfuscated programs can hide useful information.
- SHA-256 hashes cover inspected member content. Comparisons accept report schemas 1–3. `changed_files` includes binary and text hashes; `changed_source_files` remains a source-only compatibility field.

## Reproduce verification

```sh
python -m unittest discover -s tests -v
python tests/make_binary_fixture.py
python -m reversium reports/binary-fixture.zip --output reports/binary
```

The generated fixture contains synthetic metadata only, plus a tiny source/config example. It is not a working software platform. With the v0.5.0 route tracer, analysis reports 8 files, 5 binary candidates and 29 findings (including the source handler/response evidence). Filtering evidence to `binary_import` shows KERNEL32.dll and libc.so.6. Fixture artifacts are ignored by Git.

## Format references

Readers were implemented with reference to [Microsoft PE/COFF documentation](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format), the [ELF ABI](https://gabi.xinuos.com/elf.pdf), and the [Java class-file specification](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-4.html). They implement the subset above, not complete validators.

## Next increment

Optional ILSpy, JADX and Ghidra integrations remain planned. They require local installations, version/availability checks, bounded subprocess output and runtime, license notices, and isolated handling of their output. Reversium does not currently download, bundle or invoke them. Automatic installation/execution of submitted software remains a separate future VM workflow.
