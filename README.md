# Reversium

An open-source, local and free-to-run archive analysis workbench. No external services, API keys, JavaScript packages or Python dependencies are required. Python 3.10+ is required.

## Run

```sh
python -m reversium
```

Choose a ZIP in the browser at http://127.0.0.1:8765. Analysis stays on your computer. Stop the server with Ctrl+C. For exportable reports:

On Windows, `./Start-Reversium.ps1` also starts the application and can use the bundled Codex Python runtime when available.

```sh
python -m reversium project.zip --output reports/project
python -m unittest discover -s tests -v
```

The CLI writes standalone `report.html` and structured `report.json`. It overwrites those two names in the selected output directory. The browser displays a report; use browser Save/Print to retain it, or the CLI for JSON export.

## Current coverage

- ZIP member inventory, source language counts, source hashes, binary candidates.
- Python AST imports, classes, functions and main guards.
- JavaScript/TypeScript import and require heuristics, package.json dependency inventory.
- Heuristic route and endpoint-host candidates, with file and line references.
- Embedded SVG diagram of file-to-import/package mentions, evidence table and explicit limitations.

Diagrams show mentions, not resolved call graphs. Other supported extensions receive language inventory only. No claim of complete architecture recovery, vulnerability detection, cost estimation or binary decompilation is made in this release. Files are not extracted, built, imported or executed. Nested archives are inventoried without recursion.

Browser uploads are capped at 64 MiB. Both entry points reject archives over 10,000 entries or 256 MiB declared uncompressed size, unsafe paths, symlinks and duplicate member names. Individual content reads are capped at 4 MiB; compression ratios above 200:1 are skipped. Encrypted members are skipped. Reports can contain private paths and symbol names; review them before sharing. Run locally on trusted hardware; static parsing still consumes resources.

## Project

- GitHub: https://github.com/TheFamousJC/reversium
- [Development stages](docs/DEVELOPMENT_STAGES.md)
- [Plain-language explanation](docs/PLAIN_LANGUAGE.md)
- [Contributing](CONTRIBUTING.md)

Licensed under MIT. Binary analyzers will be optional adapters with their own license notices. The core will continue to work without AI or paid services.
