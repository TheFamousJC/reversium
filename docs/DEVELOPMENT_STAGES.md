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

## Stage 3 — Binary inspection (first increment delivered, v0.3.0)

Implemented:
- Local dependency-free static reader `reversium-static/1`, with explicit complete/partial/unsupported inspection status. No submitted code is executed or extracted.
- Signature recognition for PE candidates, ELF, Java class, DEX, Mach-O and ZIP containers; APK/JAR-like directory markers. Renamed and extensionless binaries can be detected within content limits.
- PE architecture/bitness, CLR-directory marker and ordinary imported DLL names; ELF architecture/bitness/endian and section-based DT_NEEDED references; Java version/class references.
- DEX/Mach-O header identification; bounded nested-container directory inspection, without nested member extraction.
- Bounded ASCII string samples, limited credential-assignment omission and URL host-only samples. Source evidence keeps line numbers; binary evidence uses byte offsets.
- Binary metadata table and byte-offset evidence in HTML/JSON reports. Hash comparisons include inspected binaries via `changed_files`.
- Evidence-linked platform profile: framework/runtime candidates, supporting database/cache/broker/integration references and simple Docker/Compose image candidates.
- Setup/readiness section lists unknowns explicitly: the tool does not install, build, start or health-check the software, or certify stability.
- Reproducible synthetic fixtures and [binary coverage/limits](BINARY_ANALYSIS.md).

Verification on 2026-10-15:
- All 30 tests pass, including PE/ELF imports, Java references, ELF 32-bit big-endian header, DEX/Mach-O identification, malformed offsets/truncation, output limits, signature detection, binary comparisons, service evidence and source URL credential omission. The loopback HTTP test ran outside sandbox socket restrictions.
- CLI mixed binary fixture generation and HTML/JSON export completed. Browser upload on local port 8768 showed 8 files, 5 binary candidates, 27 findings and the expected partial status for broken.exe. Filtering `binary_import` showed 2 findings with offsets. Downloaded JSON contains schema version 3 and full results.
- Visually checked report profile, service references and binary table. Screenshot is saved locally under ignored `reports/browser-binary.jpg`. Tests use synthetic metadata fixtures, not reconstructed production applications. Broader real-world binary coverage remains to be validated.

Remaining: external decompiler adapters (ILSpy/JADX/Ghidra), richer native imports/symbols, UTF-16 strings, program-header-only ELF imports, and deeper Mach-O/DEX/managed metadata. No optional tool is installed or invoked in this increment. Reader status describes supported field inspection, not whole-file validity. Platform purpose and service needs are candidates; business behavior and deployment stability are unverified.

Exit criterion: supported binary fixtures yield reproducible evidence without executing their programs. Tool installation and redistribution notices must be documented.

## Stage 4 — Requirements and planning (first explanation increment delivered, v0.4.0)

Implemented:
- Default “What this software does” report tab, alongside Architecture, Evidence and Coverage.
- Dependency-free local rules convert route/model/host findings, recognized framework/service references and binary-format clues into cautious plain-language explanations. No model, API key, network request or program execution is involved.
- Every explanation has matching finding indices, a statement that it is not verified by running, and a specific unknown. Names, dependencies and binary strings are not promoted into confirmed business features.
- Evidence links switch to Evidence, clear filters, focus/highlight the exact finding and preserve line/byte provenance. Finding hashes support direct navigation and reopening.
- Explicit global unknowns cover business purpose, workflow completeness, side effects, configuration, external services, uninspected code and runtime stability. An archive without supported clues receives an honest insufficient-evidence state.
- Overview capped at 16 explanation groups, with an explicit omitted count and all findings retained. The additive `behavior` JSON field includes explanations, unknowns, method and confirmation steps within schema version 3; HTML exports retain all four tabs.

Verification on 2026-10-15:
- All 36 regression tests pass, including six explanation tests covering evidence integrity, unsupported-input unknowns, inference limits, service uncertainty, escaped names/export data and output caps. The local HTTP test ran outside sandbox socket restrictions.
- Browser verified the default explanation tab, 11 explanation groups for the mixed fixture, the insufficient-evidence state for a text-only ZIP, and navigation from app.py:3 to finding-22 after a filter deliberately hid all findings.
- Standalone HTML download completed; exported content retains all four panels and the structured explanations. Screenshot saved locally under ignored `reports/browser-explanations.jpg`.

Remaining Stage 4 work:

- Evidence-linked functional specification drafts and unresolved questions.
- Optional local model adapter; deterministic reports remain available without AI.
- Editable modernization options and work breakdown estimates.
- Versioned infrastructure price assumptions and low/base/high cost scenarios.

## Stage 5 — Optional runtime investigation (future)

Separate disposable-VM workflow with explicit user control, network capture and behavior evidence. Never execute submitted programs in the main application process. This stage is outside the initial static-analysis release.

Future setup workflow: produce a reviewable run plan (OS/architecture, pinned dependencies, services, environment-variable names, migrations and startup commands), then validate in a disposable VM. Only successful installation, startup, health checks and service checks may establish that a package runs. Stability additionally needs load, restart/recovery, backup and monitoring validation. None of those steps are performed by v0.3.0.

## Change log

- 2026-10-15: Delivered v0.4.0 “What this software does” tab with local evidence-linked explanations, per-claim and global unknowns, and 36 passing tests. The summaries describe clues, not a complete or verified functional specification.
- 2026-10-15: Delivered v0.3.1 report navigation: Architecture (profile/services/diagram), Evidence (filterable findings/comparison), and Coverage (binary inspection/inventory/readiness/limits). Added accessible tab relationships, arrow/Home/End keyboard navigation, no-JavaScript fallback and print styles exposing every section. HTML exports retain every section and reset the filter. Browser checks confirmed tab isolation, keyboard switching, two matching binary-import findings and full HTML export; existing 30-test regression suite passes. The Coverage tab explicitly distinguishes evidence from an exact behavioral specification.
- 2026-10-15: Delivered v0.3.0 static binary inspection and evidence-backed platform/service candidates; 30 tests pass. Automatic setup/execution and decompiler adapters remain future work. No new runtime dependencies, network services or paid features.
- 2026-10-15: Delivered v0.2.0 source-resolution/reporting increment, verified browser workflow and responsive layout, and expanded tests from 8 to 16. No paid service or new runtime dependency added.
- 2026-10-15: Created initial workbench and living documents. Configured project identity for TheFamousJC/reversium. Remote reachability and publishing depend on available network access.
