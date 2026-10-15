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

The CLI writes standalone `report.html` and structured `report.json`. It overwrites those two names in the selected output directory. Browser reports offer Download JSON and Download HTML, plus a live evidence filter. Exports always contain the full report, even when the view is filtered.

Reports have three tabs: **Architecture** (platform profile, supporting services and diagram), **Evidence** (filterable findings and baseline comparison), and **Coverage** (binary inspection, inventory, readiness and limitations). Tabs support arrow/Home/End keyboard navigation. Saved HTML retains all sections; printing or disabling JavaScript exposes all sections. Analysis does not establish an exact behavioral specification of arbitrary uploaded programs.

Compare against a previously saved JSON report:

```sh
python -m reversium project.zip --compare reports/previous/report.json --output reports/current
```

Comparison lists added/removed files and findings, and changed inspected files with hashes in both reports (including binaries). Moving a finding to a different line or byte offset alone does not count as a new finding. Comparison is currently CLI-only; reports and exports display the results.

## Current coverage

- ZIP member inventory, source language counts and hashes for inspected content.
- Python AST imports, classes, functions and main guards.
- JavaScript/TypeScript import and require heuristics, package.json dependency inventory.
- requirements.txt and go.mod dependency names (common declarations only).
- Python AST decorator route candidates (including multiline decorators) and Django/SQLAlchemy base-name model candidates.
- Heuristic non-Python route and endpoint-host candidates, with file and line references.
- Conservative Python and JavaScript/TypeScript local module links, including relative imports, index files and emitted .js to TypeScript path candidates. Ambiguous matches are retained without selecting a target.
- Internal/external/unresolved/ambiguous labels and per-file analysis coverage.
- Static binary identification and metadata: PE/ELF library references, Java class references, DEX/Mach-O header identification and APK/JAR-like container directories. Binary evidence uses byte offsets; partial/unsupported readers remain explicit.
- Evidence-backed platform/framework/runtime candidates and supporting service references from known libraries and simple Docker/Compose image declarations.
- Setup/readiness assessment with unconfirmed requirements; no automatic installation or execution.
- Embedded SVG diagram of file-to-import/package mentions, evidence table and explicit limitations.

Diagrams show import/package references and local path candidates, not call graphs. An external import label requires a matching declared package name; unknown references remain unresolved (including Python standard-library imports). Aliases, custom module paths and dynamic imports are not resolved. JavaScript is still scanned heuristically; Python is the only AST parser. Other source languages receive language inventory only. No claim of complete architecture recovery, vulnerability detection, cost estimation or binary decompilation is made in this release. Files are not extracted, built, imported or executed. Nested ZIP containers receive bounded directory-only inspection, without recursive content analysis. See [binary coverage and limits](docs/BINARY_ANALYSIS.md).

The platform profile identifies likely components and supporting services, not an exact business specification or a verified deployment. Client references can be optional or development-only. The application does not install, start or health-check submitted software; stable operation, resource sizing and required service versions remain unverified. Reversium is free to run, while the analyzed software may require paid or private external services.

Browser uploads are capped at 64 MiB. Both entry points reject archives over 10,000 entries or 256 MiB declared uncompressed size, unsafe paths, symlinks and duplicate member names. Individual content reads are capped at 4 MiB; compression ratios above 200:1 are skipped. Encrypted members are skipped. Reports can contain private paths and symbol names; review them before sharing. Run locally on trusted hardware; static parsing still consumes resources.

## Project

- GitHub: https://github.com/TheFamousJC/reversium
- [Development stages](docs/DEVELOPMENT_STAGES.md)
- [Plain-language explanation](docs/PLAIN_LANGUAGE.md)
- [Contributing](CONTRIBUTING.md)

Licensed under MIT. The built-in static binary reader has no third-party dependencies. External decompiler adapters remain planned and will have their own license notices. The core continues to work without AI or paid services.
