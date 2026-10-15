# Reversium development stages

Living document. Update completed work, verification and remaining limitations with each stage. Last updated: 2026-10-15.

## Stage 1 — Local source archive workbench

Implemented:
- Dependency-free Python CLI and loopback-only browser interface.
- Bounded ZIP inspection without extraction or execution.
- Language/file inventory and extension-based binary candidates.
- Python AST analysis, JavaScript/TypeScript import heuristics and package.json dependencies.
- Route/host candidates with evidence locations and explicit confidence labels.
- Standalone HTML/JSON reports and SVG dependency-mention diagram.
- MIT license, contribution guidance and regression tests.

Verification: run `python -m unittest discover -s tests -v`. Tests cover source evidence, HTML escaping, archive path/symlink/duplicate protections, content limits and local HTTP behavior.

Initial verification: all 8 tests passed on 2026-10-15 with the bundled Python runtime. The local HTTP integration test required execution outside the sandbox because loopback connections were restricted. CI configuration covers Python 3.10/3.13 on Windows/Linux; those CI runs have not yet been observed. Browser layout has not yet been visually verified.

Known limits: only Python receives AST analysis; routes/import heuristics can match comments; diagrams do not resolve modules or runtime calls. Browser export uses Save/Print; structured export uses the CLI. Not an enterprise architecture analyzer.

## Stage 2 — Deeper source understanding (planned)

- Resolve local module links and distinguish internal/external dependencies.
- Add parser adapters for selected languages and framework-specific routes/models.
- Improve manifest coverage and explicit unknown/unsupported reporting.
- Add report filtering, comparisons and browser JSON/HTML download.
- Validate with maintained fixture projects and coverage expectations.

## Stage 3 — Binary inspection (planned)

- Detect binary formats by signatures, not extensions alone.
- Add imports, metadata and strings with offsets as evidence.
- Optional ILSpy, JADX/Java and Ghidra headless adapters.
- Bound analyzer runtime/output and show tool versions and failure status.
- Keep original artifacts unchanged and report decompilation uncertainty.

Exit criterion: supported binary fixtures yield reproducible evidence without executing their programs. Tool installation and redistribution notices must be documented.

## Stage 4 — Requirements and planning (planned)

- Evidence-linked functional specification drafts and unresolved questions.
- Optional local model adapter; deterministic reports remain available without AI.
- Editable modernization options and work breakdown estimates.
- Versioned infrastructure price assumptions and low/base/high cost scenarios.

## Stage 5 — Optional runtime investigation (future)

Separate disposable-VM workflow with explicit user control, network capture and behavior evidence. Never execute submitted programs in the main application process. This stage is outside the initial static-analysis release.

## Change log

- 2026-10-15: Created initial workbench and living documents. Configured project identity for TheFamousJC/reversium. Remote reachability and publishing depend on available network access.
