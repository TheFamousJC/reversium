# Reversium

An open-source, local and free-to-run archive analysis workbench. No external services, API keys, JavaScript packages or Python dependencies are required. Python 3.10+ is required.

## Run

```sh
python -m reversium
```

Choose a ZIP in the browser at http://127.0.0.1:8765. Analysis stays on your computer. Stop the server with Ctrl+C. For exportable reports:

On Windows, `./Start-Reversium.ps1` also starts the application and can use the bundled Codex Python runtime when available.

The Windows launcher now selects a free local port. Use the address it opens and check the displayed version (0.6.0); an already-running server continues serving its older code until restarted. The CLI uses 8765 by default and selects a free port if that default is busy. `--port 0` explicitly requests a free port.

```sh
python -m reversium project.zip --output reports/project
python -m unittest discover -s tests -v
```

The CLI writes standalone `report.html`, structured `report.json`, and `feature-map.svg`. It overwrites those names in the selected output directory. Browser reports offer Download JSON, Download HTML and map SVG, plus live evidence/feature filters. Exports always contain the full generated report/map view, even when the screen is filtered.

Reports open on **What this software does**, a plain-language overview with evidence links and explicit unknowns. **Architecture** holds the platform profile, supporting services and diagram; **Evidence** holds filterable findings and baseline comparison; **Coverage** holds binary inspection, inventory, readiness and limitations. Tabs support arrow/Home/End keyboard navigation. Saved HTML retains all sections; printing or disabling JavaScript exposes all sections. Analysis does not establish an exact behavioral specification of arbitrary uploaded programs.

In **Architecture**, the feature interaction map connects supported routes, handlers, helpers and data-name candidates. Select a node/line to inspect evidence or filter by feature. Solid edges are traced references; dashed data edges are inferred name matches, not proof of the same database or a business workflow. A catalogue supplies supported-operation titles and unknowns. Browser SVG export and CLI `feature-map.svg` retain the complete drawn view; JSON includes the full generated graph. The view discloses omissions beyond 120 nodes/240 edges.

`--compare previous-report.json` now compares stable feature/node/edge identities as well as files/findings. Added items are green, changed items amber; removals are listed. Baselines without a map are reported as unavailable. Structural differences do not establish behavioral changes.

Explanations use local rules only, with no AI or added dependencies. Each explanation links to matching findings and includes what remains unverified. Links clear any evidence filter and focus the referenced row. Up to 16 explanation groups appear in the overview, with an explicit omitted count; full findings stay available. Packages without supported clues get an insufficient-evidence result. Structured explanations are included in the report JSON's additive `behavior` field (schema version 3).

Python feature tracing follows module-level decorated route handlers into uniquely resolved local/imported helpers and recognizes supported SQLite reads/writes/commits, response shapes and selected literal requests/httpx host references. JavaScript/TypeScript tracing recognizes selected ES-module Express registrations, block-bodied callbacks and helpers, pg Pool/Client and mysql2 literal SQL calls, plus response field names. It uses a bounded local tokenizer, not a full parser, and requires no Node installation. CommonJS, JSX/TSX, regex-literal files, dynamic SQL/query objects, complex middleware/router prefixes, class handlers and ORM calls remain unsupported. Trace evidence and limits are recorded in `route_traces`, coverage and findings. No input is evaluated.

Tabs are visible before scripting initializes and remain near the top while scrolling; without JavaScript, their anchors navigate the visible sections. The home page links to a built-in local sample report showing the four sections. Sample source is analyzed, never executed.

## Practical use

Reversium helps with initial software due diligence, legacy-system handover and maintenance/migration discovery. Use it to locate likely features, follow supported routes to data operations, and inventory dependencies before deeper review. It provides evidence and open questions rather than a certified functional specification, runtime validation or automatic rebuild.

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
