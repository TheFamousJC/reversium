# Reversium development stages

Living document. Update completed work, verification and remaining limitations with each stage. Last updated: 2026-10-16.

## v0.10.0 — Optional account-based AI assistance

Delivered locally 2026-10-17. Resumed development after the Tudela handover rehearsal. Local ZIP inspection, diagrams and reports retain their dependency-free, offline operation. The pending v0.9 workflow view is included: one bounded screen/callback/API/database branch with evidence and explicit static-analysis limitations.

- Added an AI assistant report tab and home-screen setup wizard plus FAQ. Users select up to 30 findings, enter a question, edit the exact outgoing JSON and approve each request. No ZIP, automatic source upload, tool execution or paid API-key fallback.
- Implemented documented open-source ChatGPT authorization with dynamic client registration, loopback callback, PKCE, state, nonce, signed ID-token validation, granted plan scopes and account-specific model discovery. Optional `requirements-ai.txt` uses maintained PyJWT/cryptography. Tokens stay in process memory; non-token host/client/subject registration metadata stays in ignored reports/. Reconnect after expiry/restart; disconnect clears local tokens, not provider consent.
- Requests use the public Responses endpoint, store=false and stream=true. Only completed responses are accepted. Claims require selected numeric evidence IDs; invalid/missing citations, failed/incomplete/interrupted streams are rejected. Citations do not validate semantic correctness. AI answers render as plain text with local finding links.
- Assistant requests require exact Origin, Host and a per-server session capability. OAuth query codes are omitted from HTTP logs; response bodies and tokens are not logged. Remote redirects are refused. HTML exports remove the assistant panel, account identity, question, preview, answer and local session capability. JSON remains the original local analysis only.
- Wizard/FAQ disclose eligibility/plan limits, optional dependencies, external sharing, best-effort redaction, memory-only tokens, no execution, and account switching. Signing in is never required for analysis.

Validation: 107 tests passed, including consent gates, evidence bounds, citation validation, state expiry/replay rejection, real locally generated RSA signatures and terminal stream handling. Browser checked wizard, disconnected state and sample evidence selection/preview. Live ChatGPT sign-in and inference require the user's consent/account and are not yet verified; do not describe cloud operation as accepted. No private Tudela evidence was sent to OpenAI during development. Browser additionally verified the ChatGPT authorization link, disconnected send gate and editable sample evidence preview. Downloaded HTML was checked to exclude the panel, question and session capability.

Provider contract references (checked 2026-10-17): https://developers.openai.com/siwc/token-sharing-open-source/sign-in and https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference . Current implementation supports RS256 ID tokens and one retained account registration; other signature algorithms fail closed. No automatic token refresh or persisted token vault is provided. Account eligibility, provider policy and plan limits remain external dependencies.

## v0.8.0 — Selected React callbacks and computed API targets

Delivered 2026-10-16. Extends the Tudela discovery milestone while retaining local, dependency-free static analysis.

- Preserve JSX attribute identity alongside tokenized expressions. Connect explicit callback providers to destructured/aliased component props or object props, forwarded callbacks, inline callbacks, direct immutable component aliases, selected React.lazy literal imports (named/default function exports), useCallback bindings and callbacks in returned hook objects, including the useMemo-returned-object pattern. Prop edges are inferred and combine possible providers across source usages; they are not a component-instance execution trace.
- Follow the CMS chain `CmsPanel.onSaveCity` → callback returned by `useCmsContent` → `saveCmsCity`, and the chat chain `AskHerzlChat.onSendMessage` → `App.handleSendChatMessage` → `POST /api/chat`. Wider feature traversal now reaches the latter route's backend/data references. Both chains have source links; execution/permissions and branch outcomes remain unverified.
- Resolve selected fetch targets using immutable local string aliases, concatenation, bounded templates, encoded path-segment candidates and per-call-site arguments through named helper wrappers. Methods are inferred from supported RequestInit object literals/spreads with override order; omitted optional options can retain GET. Different wrapper callers keep separate path/method contexts. Literal local routes are linked only when method/path matching is unambiguous; parameterized path matching accepts encoded segment candidates. Unknown method/route results remain visibly unresolved.
- Query strings/fragments and external URL credentials are omitted from generated API node labels. No expressions, callbacks, requests or source imports are executed. Mutable/environment-dependent targets, arbitrary function results, shadowed fetch/encoder names and unknown provider expressions stay unknown. Local/parameter shadowing also prevents inherited wrapper arguments from replacing inner bindings.
- Nodes now expose sampled source evidence as well as edges. Repeated connection locations retain up to 16 provenance entries; nodes sample up to 32. The Architecture tab shows prop-binding and API-context counts, explicitly distinguishing contexts from unique endpoints.

Real ZIP results: same 266 files / 5,167,505 bytes, all 115 JS/TS files scanned, 25 structural routes and 32 React/JSX module roots. New reader identifies 172 callback prop-binding occurrences and 52 resolved API-target contexts, producing 46 unambiguous caller-to-route edges. The workspace graph has 1,183 nodes / 2,160 connections; reachable feature map has 963 nodes / 1,493 connections and 3,882 total findings. Counts are bounded source candidates, not a completeness or success percentage. Large App/CMS traversals disclose their limits; the focused chat and staff maps showed no view omissions.

Verification: 96 automated tests pass (including local HTTP tests). New coverage includes 24 workflow tests: callback forwarding/aliasing, lazy/default components, returned-hook callbacks, React useCallback shorthand, multiple providers, defaults/unknown providers, methods/spread order, separate wrapper caller contexts/provenance, query/credential omission, constant/template paths, mutation/environment/unsupported targets, global fetch/encoder and inner-binding shadowing, scalar useMemo rejection, stable IDs after line moves and the 400-request output bound. Browser verified the real-ZIP report counts, focused chat and staff maps, exact prop evidence at App.tsx:1064 and the computed staff request with caller/helper evidence at CmsStaffAccess.tsx:74 and :44. Generated reports, screenshots and the user's ZIP remain local and excluded from Git.

Limits: prop spreads/default substitution, runtime component instances, state setters, arbitrary re-exports, namespace APIs, complex expressions and general callback argument/state flow are not fully resolved. Multiple bindings remain candidates. Local API paths do not establish deployment origin, proxy behavior, authentication, runtime enablement or successful requests. SQL/database uncertainty from v0.7.0 still applies. Computed API expansion is bounded to helper depth 4, 5,000 contexts, 400 output contexts and 2,000 characters per expression. Feature traversal is depth 10 / 360 visited nodes; SVG views retain their 120-node / 240-edge cap and disclose omissions. Files are not run, installed or sent to external services; no Node, AI or paid API is required.

Next focused milestone: validate additional real workflows and improve per-workflow navigation for large maps. Resolve additional callback/state and origin-dependent URL patterns only with evidence and explicit ambiguity; runtime validation and automatic setup remain deferred.

## v0.7.0 — Tudela TypeScript, React and Supabase reference map

Delivered 2026-10-16 after the real Tudela ZIP exposed the limits of v0.6.0. This extends the focused roadmap; automatic setup/execution and paid services remain deferred.

- Added a dependency-free structural reference reader for nested TypeScript route registrations, expression/block callbacks, multiline named imports, nested helpers, JSX component/value references and React modules. Regex literals and JSX text are opaque, preventing code-looking text from becoming supported connections. JSX expressions are inspected without executing them.
- Recognize Supabase clients through named createClient imports, direct-return factories, aliases and SupabaseClient parameters. Record literal table read/insert/update/upsert/delete chains, named RPCs, Auth methods and storage operations. Parameter/local-variable shadowing prevents unrelated receivers from being treated as clients. Payloads, keys, passwords, SQL values and storage object paths are not copied into this graph.
- Add inferred links from named RPCs to dollar-quoted SQL migration function definitions and recognizable table operations. Table references require a public schema qualifier or a declared table; SQL keywords and variables do not become table nodes. Definitions across historical migrations are retained as name candidates, not an applied/current database schema.
- Literal router factory mounts provide candidate prefixes; unique literal local fetch paths can link to route references. Computed URLs/tables/RPC names stay unknown. Cross-file helper and JSX references distinguish code calls, component mentions, declarations and shared data-name candidates.
- Feature selection now rebuilds the SVG from the selected feature's graph, including nodes outside the initial overview. A scrollable viewport and omission counts keep larger maps usable. Inspection shows connection endpoints, evidence and unknowns. JSON retains the workspace reference graph and all generated feature data; SVG exports save the current bounded view.
- Added Supabase and Google authentication clients to supporting-service candidates. The explanation tab can summarize mapped React and route connections. No external API, model, Node installation or third-party runtime dependency was added.

Validation with the user's original ZIP (kept outside Git): 266 files / 5,167,505 uncompressed bytes; 115 JS/TS files structurally scanned, including all 32 JSX/TSX modules; 25 structural route references; 57 map roots total. The 34 older heuristic route candidates include unrelated get() calls, so these counts are not a completeness ratio. The SQL reader inspected 44 SQL files. The final generated workspace graph contains 612 nodes / 1,389 references, and the reachable feature graph contained 470 nodes / 834 connections. Counts describe recognized syntax, not working features.

Verification: 72 automated tests pass, including the local HTTP integration test, regex/division handling, JSX text opacity, typed props/generic arrows, multiline helper imports, event-value references, client shadowing, factories, RPC/Auth/storage, inferred SQL evidence, rejection of fake SQL table names, evidence-index/edge integrity and stable structural IDs after line movement. Browser uploaded the same real ZIP into v0.7.0, confirmed the 25 route / 32 React / 115 file counts, rebuilt TourCommunityPanel's focused map with no view omissions, inspected submit_tour_comment and followed its link to the exact migration line. Coverage explicitly lists computed targets and dynamic table gaps. Local screenshots/exports are ignored under reports/; no Tudela code, ZIP, report or screenshot is committed.

Limits: this is a lexical source-reference map, including conditional/callback code, not a verified call graph or complete user-journey reconstruction. React prop/event-value flow across components, namespace/re-export resolution, complex type semantics, dynamic targets, object-property clients, overloaded RPC identity, middleware behavior, migration application order, RLS/permissions and runtime outcomes remain unknown. Framework/compiler equivalence is not claimed. Bounds: JS input 256 files / 16 MiB; SQL input 128 files / 16 MiB; 60,000 tokens per JS file; 4,000 workspace nodes / 12,000 edges; feature traversal depth 6 / 240 nodes; visible SVG 120 nodes / 240 edges. Source not retained by the browser server after analysis.

Next focused milestone: resolve selected React prop/callback and hook-return references, then computed local API URL patterns, with per-connection evidence and explicit unknowns. These are the remaining barriers to following every Tudela workflow; scanning every source file does not mean understanding every behavior.

## Focused roadmap — current scope

Product purpose: upload unfamiliar software, see its features and connections, and inspect the evidence behind the map. The brief development pause is over at the user's request. Resume with the **feature interaction map as the next milestone**; do not expand into unrelated reconstruction/deployment work.

1. Feature interaction map: connect supported routes/features to handlers, helpers, data and external references; distinguish traced links from inferred shared dependencies. A shared table name is not proof of the same database or a business workflow.
2. Feature catalogue: understandable names and descriptions, linked evidence and unknowns; retain a stable identity for comparisons.
3. Broader tracing: selected JavaScript/TypeScript routes/database calls in addition to Python/SQLite; explicitly mark unsupported syntax and behavior.
4. Clickable evidence: inspect nodes and connections, open matching findings and show file/line provenance.
5. Confidence and coverage: expose traced/inferred links, unsupported files, omitted nodes and unresolved calls.
6. Export and comparison: standalone diagram/report export and added/removed/changed feature connections between reports.

Done means these work locally without paid services, with regression/browser verification and documented coverage. It does not mean every language, framework or possible application is understood. Automatic installation/execution, deeper decompilers, AI integration, cloud/labor cost estimation and automatic reconstruction are **deferred**. Historical stages below are a record, not a commitment to implement those deferred ideas now.

### Focused MVP status — v0.6.0

The feature interaction map was implemented first on resumption. All six focused capabilities now have a working, bounded implementation:

| Capability | Delivered scope |
| --- | --- |
| Feature interaction map | Routes → handlers → resolvable helpers → data-name candidates; selected Python requests/httpx host references. Data-name edges are inferred and explicitly do not establish database identity. |
| Feature catalogue | Stable feature identities, route labels, supported-operation titles/descriptions, evidence and unknowns. No business features are guessed from names alone. |
| Broader tracing | Python AST/SQLite plus conservative JS/TS token recognition for ES-module Express registrations, block-bodied callbacks/named helpers, pg Pool/Client and mysql2 pool/connection literal SQL. |
| Clickable evidence | Inspect nodes or connections with mouse/keyboard, then open the corresponding source finding; filter the map by feature. |
| Confidence/coverage | Solid traced calls, dashed inferred data-name links, explicit trace limitations, route-candidate/trace counts without claiming a completeness percentage, and omission counts. |
| Export/comparison | HTML/JSON and standalone SVG, including browser SVG download. CLI baselines compare stable features/nodes/edges; added/changed items are highlighted and removals listed. Old baselines without maps are reported as unavailable. |

Verification: 59 tests pass. Browser checked Python and TypeScript samples, feature filtering, data-node inspection/unknowns, exact evidence navigation, SVG download and complete HTML export after filtering, and an added delete route in the comparison view. CLI comparison detected one added feature, two nodes and two connections in that example. Exported SVG is valid XML and retains the full diagram. Screenshot: ignored `reports/browser-feature-map.jpg`.

Scope boundaries: JS/TS is a **bounded token recognizer**, not a full parser or type checker. CommonJS, namespace/default re-export resolution, JSX/TSX tracing, regex-literal files, class handlers, dynamic SQL/query objects, callback bodies, middleware/router-prefix effects, ORM and complex data flow remain unsupported/unknown. Input is never evaluated. No Node runtime or third-party parser is required. JS input retention is capped at 128 files / 16 MiB with 60,000 tokens per file; combined routes cap at 100, helpers at depth 3 / 12 functions and operations at 40. Graph views cap at 120 nodes / 240 edges and disclose omissions; JSON retains the generated graph. Static baselines compare code structure, not runtime behavior.

Next work should be validation on representative user-supplied packages and fixes within this scope, rather than expanding into the deferred features. No claim of universal language coverage or production certification is made.

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

### v0.5.0 — Route/helper tracing and visible navigation

Implemented:
- Retain a bounded set of Python ASTs, associate module-level decorated routes with their handler, and follow uniquely resolved same-file/imported helpers (including aliases) across source files.
- Propagate recognized SQLite connection/cursor bindings through helper parameters. Identify simple literal SELECT/INSERT/UPDATE/DELETE statements, commit requests and supported return shapes (dictionary field names, lists and database rows). String response values, database paths and SQL values are not copied into trace explanations.
- Add `route_traces`, `route_handler`, `handler_call` and `handler_operation` evidence, preserving source locations and report indices. The explanation tab prioritizes traced features over route-name-only clues.
- Explicit unknowns cover unresolved calls, dynamic/unsupported SQL, repeated/recursive helpers, decorators and tracing limits. Statements may be conditional, unreachable or fail; the analyzer does not verify control flow, permissions, transaction success or side effects beyond the supported syntax.
- Bounds: 128 files / 16 MiB of retained Python source, 100 routes, helper depth 3 / 12 functions per route, 24 helper-call references, 40 operations and 10,000 scanned syntax nodes per function. Tracing covers module-level Python and SQLite only; ORM, class-based and other-language tracing remains future work.
- Report navigation is now visible before JavaScript initializes, higher on the page and sticky while scrolling. Anchor links provide usable section navigation without scripting. The home page has labeled sample-report section links; reports show version 0.5.0.
- Built-in local `/example` sample report and `/version` endpoint. The Windows launcher selects a free port by default; the CLI falls back to a free port when default 8765 is busy, helping avoid accidentally reopening an older server. Already-running processes do not automatically update.

Verification:
- All 45 tests pass, including cross-file reads/inserts/commits/returns, update/delete cursor operations, unsupported clients/dynamic SQL, recursive helpers, shadowed names, nested uncalled functions, literal SQL values and omitted response values. Live HTTP tests cover sample report, version and ZIP upload.
- Browser verified the live home page, four visible tabs on both sample and uploaded ZIP reports, traced feature evidence, and JavaScript-free anchor navigation using a generated report with scripts removed. The final sample has 2 source files and 19 findings.
- Browser checked the final home section links, tab switching, evidence navigation and report layout. Screenshot saved locally under ignored `reports/browser-handler-tracing.jpg`.

Practical application: an initial review of unfamiliar software, a source-backed feature inventory for maintainers, and a starting point for handover, dependency review and modernization planning. It reduces discovery effort; it does not certify the application or establish a complete specification.

## Stage 5 — Optional runtime investigation (future)

Separate disposable-VM workflow with explicit user control, network capture and behavior evidence. Never execute submitted programs in the main application process. This stage is outside the initial static-analysis release.

Future setup workflow: produce a reviewable run plan (OS/architecture, pinned dependencies, services, environment-variable names, migrations and startup commands), then validate in a disposable VM. Only successful installation, startup, health checks and service checks may establish that a package runs. Stability additionally needs load, restart/recovery, backup and monitoring validation. None of those steps are performed by v0.3.0.

## Change log

- 2026-10-16: Delivered v0.8.0 selected React prop/callback and computed API target candidates. Verified the original Tudela ZIP in the browser and 96 automated tests; no paid service or runtime dependency added.

- 2026-10-16: Delivered v0.7.0 structural TS/React/Supabase and SQL RPC reference mapping, verified against the original Tudela ZIP; 72 regression tests pass. Whole-platform runtime and prop-flow completeness remain unverified.

- 2026-10-15: Resumed with the focused roadmap and delivered v0.6.0 interaction map/catalogue, selected JS/TS tracing, map inspection/filtering and SVG/baseline exports. The scoped MVP's six capabilities are implemented; unsupported syntax and runtime behavior remain explicit unknowns. 59 tests pass and browser workflows were verified.
- 2026-10-15: Delivered v0.5.0 Python/SQLite handler tracing, stronger visible-tab fallback, live sample/version UI and free-port startup. Added practical-use guidance and expanded verification to 45 tests. No runtime dependencies or paid services added.
- 2026-10-15: Delivered v0.4.0 “What this software does” tab with local evidence-linked explanations, per-claim and global unknowns, and 36 passing tests. The summaries describe clues, not a complete or verified functional specification.
- 2026-10-15: Delivered v0.3.1 report navigation: Architecture (profile/services/diagram), Evidence (filterable findings/comparison), and Coverage (binary inspection/inventory/readiness/limits). Added accessible tab relationships, arrow/Home/End keyboard navigation, no-JavaScript fallback and print styles exposing every section. HTML exports retain every section and reset the filter. Browser checks confirmed tab isolation, keyboard switching, two matching binary-import findings and full HTML export; existing 30-test regression suite passes. The Coverage tab explicitly distinguishes evidence from an exact behavioral specification.
- 2026-10-15: Delivered v0.3.0 static binary inspection and evidence-backed platform/service candidates; 30 tests pass. Automatic setup/execution and decompiler adapters remain future work. No new runtime dependencies, network services or paid features.
- 2026-10-15: Delivered v0.2.0 source-resolution/reporting increment, verified browser workflow and responsive layout, and expanded tests from 8 to 16. No paid service or new runtime dependency added.
- 2026-10-15: Created initial workbench and living documents. Configured project identity for TheFamousJC/reversium. Remote reachability and publishing depend on available network access.


Update 2026-10-17: live ChatGPT sign-in/model discovery succeeded, but the first minimal evidence request failed before an answer was displayed. No AI answer has been accepted against source evidence. Fixed assistant initialization after in-page ZIP uploads and added safe provider HTTP status/code diagnostics without raw provider messages, tokens or evidence. Reconnection after restart is required for the next live test.


## About, FAQ and report downloads - build 0.10.1 (2026-10-17)

About now explains Reversium in plain language: practical handover and maintenance uses, a simple reading workflow, optional AI and limitations. Build 0.10.1 and Open Source / 3Sci.com / 2026 are displayed. Uploaded-code explanations remain available in Software findings. FAQ has its own report button and home help button, including the assistant questions. HTML is the readable report for offline review and handover; JSON is structured findings for scripts, tools and baseline comparison. Both can contain private analysis details; neither is the original ZIP or a runnable backup.


## Contemporary interface and short control help - build 0.10.2 (2026-10-17)

Refreshed the home/report UI with light surfaces, indigo controls, compact segmented navigation, responsive typography, bordered content cards and clearer form styling. All visual assets remain local. Short explanations appear on pointer hover and keyboard focus for buttons, navigation, expandable explanations, graph inspection controls and the archive picker. Escape dismisses help; it is linked with aria-describedby, placed within the viewport and omitted from saved HTML. Reduced-motion preferences are respected. Browser verified the light report layout, wrapped navigation and Download HTML keyboard tooltip; all 107 regression checks passed.


## Guided Start flow - build 0.11.0 (2026-10-17)

Replaced the crowded home with four steps: Start (choose understanding, handover or maintenance goal), Choose ZIP, Review findings, and Save & next steps. The first two steps contain no downloads or account setup. Analysis opens on Review findings with goal-specific reading guidance; buttons lead to feature connections, gaps and the final save step. HTML/JSON downloads are only in Save & next steps after an analysis exists. AI is optional after review. Sample reports are explicitly marked as fictional demonstrations.

Browser verified the full flow against the Tudela ZIP: handover goal carried into analysis, Review findings selected on arrival, downloads hidden during review and visible in the final step. Existing regression suite: 107 passing tests. Analysis remains local/free and uploaded code is not executed.


## Non-technical Tudela walkthrough - build 0.11.1 (2026-10-17)

Walked Start to Save with the original Tudela Build 1.zip and the handover goal. The previous first result overwhelmed an owner with a large App.tsx reference list and hundreds of links. Review now leads with a bounded, evidence-linked plain-language profile, explicit uncertainty about whether the software works, and a clear recommendation to save a readable report for a developer. Detailed findings and inventory counts remain available behind expandable sections. The profile describes technology clues, not a recovered business specification.

Choose ZIP now explains compressed packages, source-code preference and local-only inspection; Analyze stays disabled until a non-empty file within 64 MiB is selected. Selected filename/size are displayed, and the report retains an escaped filename and selected goal. Back navigation retains the chosen goal. The final screen prioritizes Save readable report (HTML), labels technical JSON as optional, and assigns three actions to owner/developer with explicit done-when criteria. No checklist state is presented as runtime verification.

Browser verified the real ZIP selection (Build 1.zip, 3.1 MiB), Review default, hidden downloads before Save, evidence navigation to finding 271, and final owner/developer action list. Existing analysis remains local; no Tudela code was run and no AI evidence was shared during this usability walkthrough.

Verification: 109 tests pass, including two new checks that owner-profile clues require supported dependency/import findings, retain real evidence IDs and escape source paths. An initial Windows loopback connection reset did not recur on the full rerun; the real-ZIP browser flow passed.


## Free public sample demo (2026-10-17)

Added a GitHub Pages landing page and interactive report generated only from five fictional community-library files. Visitors can explore owner findings, inspect evidence, follow the Add book screen/callback/API/database path and save sample HTML/JSON without installing Reversium. This is a sample-only static demonstration, not online analysis of visitor ZIPs. No upload endpoint, AI sign-in, assistant request script, analytics or third-party assets are included. The local Python application is still required for analysing real packages.

The existing public repository Pages configuration already publishes the root of codex/initial-workbench. scripts/build_demo.py rebuilds index.html and demo/report.html; .nojekyll preserves the static output. Private Tudela archives, reports, tokens and test data are excluded. Browser verified the local landing-to-report navigation and the complete supported fictional feature path before publication.


## Browser-local edition — 0.12.0

Ported the existing Python analyzer through self-hosted pinned Pyodide to a module worker. Added guided own-ZIP flow, cancellation, bounded processing, sandboxed offline reports and local exports. No source execution, upload API, account or AI service. Tudela local browser verification found 266 files and 3,882 findings, matching native analysis; traced AskHerzlChat to /api/chat and ai_usage_events with existing candidate labels. GitHub Pages publication is the deployment target; public verification follows push. Browser input limit 32 MiB; static evidence is not runtime proof.

Public verification completed at https://thefamousjc.github.io/reversium/web/ on 17 October 2026: Tudela produced 266 files and 3,882 findings. Architecture workflow selection, evidence navigation, JSON and HTML downloads succeeded on GitHub Pages. All 111 automated tests passed. Private Tudela files/reports were excluded from the published repository.


## Branding and clearer navigation — 0.12.1

Build 0.12.1 adds the supplied 3Sci logo on a dark background, a Reversium by 3Sci Labs splash with Understand. Prepare. Develop., a shorter package selection instruction, direct graphical feature/file relationship controls and a visible browser AI availability explanation. Browser remains free and local; no hosted AI integration was added.


## Report navigation and AI handoff — 0.13.0

Build 0.13.0: enlarged entry CTAs; persistent inventory cards; Architecture/Coverage subsection navigation; hidden outer start/help/footer when a report is ready; embedded logo and shared product/build branding in reports and exports. Restored a browser AI tab with provider selection and editable selected-evidence request download. It is explicitly a manual handoff, not hosted OAuth/inference; no credentials collected, no automatic sharing. Local account assistant is unchanged. Direct in-browser ChatGPT connection remains an unmet request; a supported credential/service design is required.

Verified with Tudela in the browser: redundant outer header hidden, inventory visible, Architecture catalogue/import views and Coverage readiness switching passed. AI evidence preview, provider selection and request download passed without submitting to a provider. 111 tests passed.
