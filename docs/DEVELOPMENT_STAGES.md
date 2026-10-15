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

Initial verification: all 8 tests passed on 2026-10-15 with the bundled Python runtime. The local HTTP integration test required execution outside the sandbox because loopback connections were restricted. CI configuration covers Python 3.10/3.13 on Windows/Linux; those CI runs have not yet been observed. Browser verification was completed during Stage 2 below.

Initial limits: only Python receives AST analysis; heuristic scans can match comments; diagrams did not resolve modules. Stage 2 adds local path resolution and browser exports. Runtime call graphs remain out of scope.

## Stage 2 — Deeper source understanding (first increment delivered, v0.2.0)

Implemented:
- Conservative Python and JavaScript/TypeScript local module resolution; internal/external/unresolved/ambiguous labels. Ambiguous candidates remain explicit, and missing modules are not presumed external.
- Separate source adapter module; Python AST decorator routes (including multiline), relative `from . import module` references and Django/SQLAlchemy base-name model candidates. Comments are no longer reported as Python routes.
- Dependency-name extraction for common requirements.txt and go.mod declarations, alongside package.json. Other known manifests remain identification-only.
- Per-file analysis coverage and normalized ZIP paths with duplicate detection.
- Live evidence filter and full JSON/standalone HTML browser downloads. Horizontal diagram/table scrolling and responsive controls keep narrow views readable.
- CLI baseline comparison (`--compare previous/report.json`), including added/removed files and findings, plus changed files when both reports have content hashes. Findings moving lines alone do not count as additions/removals.
- Maintained mixed-language synthetic fixture in `tests/fixtures/webapp` and regression coverage.
- Bounded draining of rejected upload bodies so Windows clients receive the intended 403 instead of a connection reset.

Verification on 2026-10-15:
- All 16 tests passed on the bundled Python runtime, including the loopback HTTP integration test outside the sandbox socket restriction.
- CLI HTML/JSON generation and unchanged-baseline comparison completed; no changes were reported for the same fixture.
- Browser: uploaded the 7-file fixture, observed 17 findings, checked dependency labels and local targets, filtered `internal` down to 3 findings, and downloaded both JSON and HTML. JSON parsed as schema version 2 with all 17 findings. Saved HTML retained all findings despite the filtered view.
- Visually inspected desktop home/report and 390×844 report layout. Fixed cramped table wrapping, then verified the generated final HTML with horizontal scrolling. Screenshot saved locally under ignored `reports/browser-evidence.jpg`.
- An older local server occupied port 8765; verification used 8766 for upload and 8767 for the final generated report. Browser fixture/export calls were unusually slow in the automation environment, but completed.

Remaining Stage 2 work: additional language parsers, broader framework/manifest coverage, browser baseline selection, improved alias/re-export handling, and richer graph layouts. Python remains the sole AST parser; JavaScript/TypeScript remains heuristic. Cross-language calls and actual runtime behavior are not inferred. Binary analysis remains Stage 3.

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

- 2026-10-15: Delivered v0.2.0 source-resolution/reporting increment, verified browser workflow and responsive layout, and expanded tests from 8 to 16. No paid service or new runtime dependency added.
- 2026-10-15: Created initial workbench and living documents. Configured project identity for TheFamousJC/reversium. Remote reachability and publishing depend on available network access.
