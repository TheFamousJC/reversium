# Reversium development stages

Living document. Update completed work, verification and remaining limitations with each stage. Last updated: 2026-10-18.

## v0.10.0 — Optional account-based AI assistance

Delivered locally 2026-10-17. Resumed development after the Tudela handover rehearsal. Local ZIP inspection, diagrams and reports retain their dependency-free, offline operation. The pending v0.9 workflow view is included: one bounded screen/callback/API/database branch with evidence and explicit static-analysis limitations.

- Added an AI assistant report tab and home-screen setup wizard plus FAQ. Users select up to 30 findings, enter a question, edit the exact outgoing JSON and approve each request. No ZIP, automatic source upload, tool execution or paid API-key fallback.
- Implemented documented account ChatGPT authorization with dynamic client registration, loopback callback, PKCE, state, nonce, signed ID-token validation, granted plan scopes and account-specific model discovery. Optional `requirements-ai.txt` uses maintained PyJWT/cryptography. Tokens stay in process memory; non-token host/client/subject registration metadata stays in ignored reports/. Reconnect after expiry/restart; disconnect clears local tokens, not provider consent.
- Requests use the public Responses endpoint, store=false and stream=true. Only completed responses are accepted. Claims require selected numeric evidence IDs; invalid/missing citations, failed/incomplete/interrupted streams are rejected. Citations do not validate semantic correctness. AI answers render as plain text with local finding links.
- Assistant requests require exact Origin, Host and a per-server session capability. OAuth query codes are omitted from HTTP logs; response bodies and tokens are not logged. Remote redirects are refused. HTML exports remove the assistant panel, account identity, question, preview, answer and local session capability. JSON remains the original local analysis only.
- Wizard/FAQ disclose eligibility/plan limits, optional dependencies, external sharing, best-effort redaction, memory-only tokens, no execution, and account switching. Signing in is never required for analysis.

Validation: 107 tests passed, including consent gates, evidence bounds, citation validation, state expiry/replay rejection, real locally generated RSA signatures and terminal stream handling. Browser checked wizard, disconnected state and sample evidence selection/preview. Live ChatGPT sign-in and inference require the user's consent/account and are not yet verified; do not describe cloud operation as accepted. No private Tudela evidence was sent to OpenAI during development. Browser additionally verified the ChatGPT authorization link, disconnected send gate and editable sample evidence preview. Downloaded HTML was checked to exclude the panel, question and session capability.

Provider contract references (checked 2026-10-17): https://developers.openai.com/ and https://developers.openai.com/ . Current implementation supports RS256 ID tokens and one retained account registration; other signature algorithms fail closed. No automatic token refresh or persisted token vault is provided. Account eligibility, provider policy and plan limits remain external dependencies.

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

About now explains Reversium in plain language: practical handover and maintenance uses, a simple reading workflow, optional AI and limitations. Build 0.10.1 and 3Sci.com / 2026 are displayed. Uploaded-code explanations remain available in Software findings. FAQ has its own report button and home help button, including the assistant questions. HTML is the readable report for offline review and handover; JSON is structured findings for scripts, tools and baseline comparison. Both can contain private analysis details; neither is the original ZIP or a runnable backup.


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

Added a Static web hosting landing page and interactive report generated only from five fictional community-library files. Visitors can explore owner findings, inspect evidence, follow the Add book screen/callback/API/database path and save sample HTML/JSON without installing Reversium. This is a sample-only static demonstration, not online analysis of visitor ZIPs. No upload endpoint, AI sign-in, assistant request script, analytics or third-party assets are included. The local Python application is still required for analysing real packages.

The existing public repository Pages configuration already publishes the root of codex/initial-workbench. scripts/build_demo.py rebuilds index.html and demo/report.html; .nojekyll preserves the static output. Private Tudela archives, reports, tokens and test data are excluded. Browser verified the local landing-to-report navigation and the complete supported fictional feature path before publication.


## Browser-local edition — 0.12.0

Ported the existing Python analyzer through self-hosted pinned Pyodide to a module worker. Added guided own-ZIP flow, cancellation, bounded processing, sandboxed offline reports and local exports. No source execution, upload API, account or AI service. Tudela local browser verification found 266 files and 3,882 findings, matching native analysis; traced AskHerzlChat to /api/chat and ai_usage_events with existing candidate labels. Static web hosting publication is the deployment target; public verification follows push. Browser input limit 32 MiB; static evidence is not runtime proof.

Public verification completed at ../web/ on 17 October 2026: Tudela produced 266 files and 3,882 findings. Architecture workflow selection, evidence navigation, JSON and HTML downloads succeeded on Static web hosting. All 111 automated tests passed. Private Tudela files/reports were excluded from the published repository.


## Branding and clearer navigation — 0.12.1

Build 0.12.1 adds the supplied 3Sci logo on a dark background, a Reversium by 3Sci Labs splash with Understand. Prepare. Develop., a shorter package selection instruction, direct graphical feature/file relationship controls and a visible browser AI availability explanation. Browser remains free and local; no hosted AI integration was added.


## Report navigation and AI handoff — 0.13.0

Build 0.13.0: enlarged entry CTAs; persistent inventory cards; Architecture/Coverage subsection navigation; hidden outer start/help/footer when a report is ready; embedded logo and shared product/build branding in reports and exports. Restored a browser AI tab with provider selection and editable selected-evidence request download. It is explicitly a manual handoff, not hosted OAuth/inference; no credentials collected, no automatic sharing. Local account assistant is unchanged. Direct in-browser ChatGPT connection remains an unmet request; a supported credential/service design is required.

Verified with Tudela in the browser: redundant outer header hidden, inventory visible, Architecture catalogue/import views and Coverage readiness switching passed. AI evidence preview, provider selection and request download passed without submitting to a provider. 111 tests passed.


## Detailed Help — 0.13.1

Build 0.13.1 adds shared eight-chapter detailed Help to Start and reports, a self-contained downloadable PDF and a public guide page. Documentation covers all views, limits, evidence interpretation, file handling, local setup/CLI, exports/comparison, troubleshooting and handover. Online/local differences have their own chapter plus a concise note in AI. PDF generation is build-time only; local analysis has no added dependency.

Help verification: edition-comparison chapter opens and PDF download succeeds in the browser. The eight-page PDF was rendered and visually reviewed. Updated LinkedIn draft is saved in docs/LinkedIn-post.txt.

Help placement: Help, FAQ and About are now prominent buttons on the public landing and welcome splash, as well as the subsequent Start/ZIP screens and report tabs. First-page buttons open the relevant built-in panel.

PDF reliability fix: only sandboxed about:srcdoc reports forward downloads to the host; other embedded/browser pages download directly. Download anchors are attached for activation and URLs live for 60 seconds. Help also provides an ordinary direct public PDF link. Online ChatGPT account inference remains externally gated: official OpenAI documentation directs remotely hosted applications to the interest process; no hosted account connection or subscription access is claimed.


## Online account integration preparation

Prepared online account lifecycle behind disabled config with no provider adapter. Added in-UI connect/disconnect, exact JSON review, per-send approval, citation-linked replies, cancellation and expiry/error handling. Parent-frame broker keeps network disabled in reports. Fake-adapter tests cover validation, opt-in, stale responses and disconnect; no real provider call or credential collection. Hosted OAuth/backend and live sign-in remain dependent on OpenAI-approved deployment details.

Browser verification with fictional source confirmed pending-approval status, disabled connect/send, exact selected-evidence preview, approval reset after edits and working manual fallback. Eight fake-adapter tests pass without network calls. The regression suite hit an intermittent Windows loopback reset; the affected HTTP test file passed when run separately. No hosted account sign-in or inference was performed.


## Tudela prepared-AI verification and Windows HTTP fix — 18 October 2026

Input: the same private Tudela Build 1.zip, analyzed by the browser edition on loopback; 266 files and 3,882 findings. Selected finding IDs 1325 (POST /api/chat, server.ts:264), 1339 (recordHerzlUsage reference, server.ts:437) and 3446 (frontend API target candidate, src/App.tsx:785). Prepared JSON had exactly question/evidence and exactly those three findings, with no archive payload. Connect and Send remained disabled even after consent. Editing the preview reset consent. Manual request preparation retained the selected IDs. Clear returned to Start, emptied the file input and cleared the report iframe. No account connection or model request was attempted; the production enabled:false flag and null adapter are unchanged. This verifies preparation, not live AI inference.

Reproduced the Windows HTTP test failure while reading a 156,083-byte /example response after the server completed its HTTP/1.0 write and closed the connection. Changed the local server to HTTP/1.1 with existing byte-accurate Content-Length, allowing successful connections to stay open. Error responses explicitly close, so rejected requests with unread input cannot corrupt the next request. Added a regression that reads four approximately 1.12 MB responses intact on the same socket and checks framing/reuse. Existing origin/session rejection tests remain intact.

Validation: six consecutive full-suite runs, each 112 tests with zero failures/errors and one optional signature-verification test skipped because its dependencies are absent; eight online-AI fake-adapter tests pass. The reset did not recur in these repeated runs. Private ZIP, prepared requests and screenshots remain in ignored reports/ and are excluded from Git.


## Competitive review and practical handover tools — build 0.14.0, 18 October 2026

Reviewed current primary documentation for CodeBoarding, SonarQube Community Build, CodeQL and Joern. Published docs/market-position.html with linked sources, strengths, fit, explicit comparison limits and a prioritized zero-service-cost roadmap. Reversium's proposed position is a browser-local, no-install, model-free starting point for ZIP-based handover and maintenance discovery, combining supported feature paths, evidence, unknowns and reviewer actions. Local analysis, graphs and source links are not claimed as exclusive inventions. Competitor workflows have their own strengths; no hands-on performance or exhaustive feature benchmark is claimed.

Implemented names-only configuration clues (supported process.env, import.meta.env, os.getenv/os.environ forms and three example/template filenames), package.json script names and bounded runtime constraint declarations. Environment values and script commands are not retained by this reader. All clues link to source findings; names can be optional or matched in comments and do not prove setup requirements. Display limits and omitted references are disclosed.

Added Handover with five reviewer-owned verification actions, statuses, owners and notes; local JSON and readable-text exports. Notes are session-only, excluded from AI packets and cleared from standard HTML exports. Restoration/import is not yet implemented and remains the next priority. Added Change impact with explicit source-file metadata for structural graph nodes, bounded upstream/downstream exploration (3 hops, 120 candidates and 60,000 edge checks per direction), confidence/relationship labels and source links. Starting nodes no longer use cross-file evidence as a proxy for ownership. No runtime/breakage guarantee.

Verified the same private Tudela ZIP in-browser: 266 files, 4,004 findings (122 new setup findings), 88 clue groups. Handover JSON/text preserved the reviewer status/owner/notes. The AskHerzlChat.tsx impact view returned 13 nearby candidates with traced/inferred labels and working evidence navigation. Tests cover names-only privacy, malformed manifests, real .env exclusion, malicious script names and graph source-file metadata. Full suite: 117 tests, no failures/errors, one optional dependency check skipped. Eight offline AI lifecycle tests also pass. Updated Help and rendered/visually inspected the nine-page PDF. No paid service, model, account connection or uploaded ZIP was used.

Next: validated checklist restore with delivery identity, browser baseline comparison, broader setup fixtures and targeted impact validation. Hosted ChatGPT remains disabled with a null adapter until approval and approved transport implementation. Free analysis and current Static web hosting/archive/device bounds remain explicit.

Sources: https://www.codeboarding.org/ ; https://www.sonarsource.com/products/sonarqube/ ; CodeQL official documentation ; https://joern.io/


## Stage 0.15.0 — resume handover reviews and compare deliveries (18 October 2026)

Added local handover JSON restore with bounded input (1 MiB), strict five-task/status/text validation, preview and explicit replacement. New saves include an exact ZIP SHA-256 fingerprint, computed for archives up to 64 MiB including inventory-only members. Repacked archives have a different identity. Mismatches reject without overwriting notes. Legacy v1 checklists require a matching archive name and explicit independent delivery confirmation; they cannot prove identity. No credentials, storage service or AI is involved. Standard HTML exports clear pending note previews as well as form fields.

Added Compare reports to the browser and local report UI: bounded 32 MiB JSON import, at most 10,000 file and 200,000 finding entries, duplicate/malformed-entry rejection, file additions/removals, differing shared hashes, unavailable hash coverage and finding identity additions/removals. Line movement alone is ignored. Lists show at most 200 entries with omissions; readable comparison notes can be saved separately. Browser comparison does not compare graph relationships or establish behavior. Different analyzer versions can change findings without code changes. Checklist notes survive comparison. File pickers are brokered by the browser host for sandboxed reports; files are passed only to their own report frame. Versioned app/worker URLs avoid stale release scripts.

Tudela browser verification: original Build 1.zip, 266 files and 4,004 findings; exact-fingerprint checklist preview and restore succeeded. Wrong fingerprint rejected while owner notes remained intact. Earlier saved report comparison: zero added/removed/changed hashed files, 85 files without comparable hashes, 115 added findings and zero removed findings. Same-current-report comparison: zero file/finding changes and 84 files without comparable hashes. These counts demonstrate analyzer/coverage differences, not new Tudela behavior. Private test artifacts remain ignored under reports/.

Verification: 118 Python tests pass (one optional-dependency skip) and 12 JavaScript tests pass. The initial sandboxed test attempt was blocked by loopback permissions; rerunning with local networking enabled passed. Updated Help and PDF; visually checked the handover chapter. Core analysis and review remain free and local. Hosted ChatGPT stays disabled pending approval. Remaining scope: deeper graph comparison in the browser, broader setup-reader fixtures and targeted workflow validation.


## Stage 0.16.0 — compare feature-map relationships and candidate effects (18 October 2026)

Extended the local/browser Compare reports workflow to compare stable feature/node/relationship identities. Relationship changes include endpoints, labels, confidence, feature membership and unknowns; evidence index/line movement alone is ignored, with selected line-only unknown text normalized. Missing maps produce an unavailable result, never an invented removal. Renamed identities may appear as removal/addition. Analyzer and coverage changes remain explicit alternatives to software changes.

Added earlier/current relationship cards with focused diagrams, source locations, current finding links and separately labelled earlier references. Directly recorded feature membership is separated from a collapsed broader neighborhood, which can include unrelated features through shared graph nodes. Candidate effects are not runtime failures or proof of a complete call graph. Review includes an isolated-test next step. Comparison notes export preserves displayed results and omissions; handover annotations and AI packets remain separate.

Validated bounded maps (20,000 nodes, 40,000 edges, 1,000 features), unique identities, endpoints, text types and evidence indices. Existing report import remains 32 MiB. Display caps: 100 feature/node changes per list and 100 relationship cards, four evidence references and 20 feature names per list; omissions are disclosed. Candidate exploration per relationship side is bounded to two hops, 120 nodes and 200 edge visits. Invalid imports clear partial comparison results and disable save.

Tudela browser test: the original ZIP compared to its identical report yields zero feature/node/edge changes. A private controlled ZIP changes one .from('tours') reference in server/herzlGrounding.ts to .from('reversium_test_tours'); this is a test mutation, not a real Tudela delivery or a claimed application change. Comparing the original against this fixture shows two changed feature descriptions (POST /api/chat and UI AskHerzlChat.tsx), one removed node, one node with changed recorded membership, and one added/one removed relationship. The relationship's current source location is herzlGrounding.ts:45, confidence inferred. Direct membership identifies the chat API and AskHerzlChat screen; broader neighborhoods find 32 current and 24 earlier candidates, explicitly not confirmed effects. A separately labelled confidence-only metadata fixture produces one changed relationship with before/after confidence. Verified evidence navigation to the current Evidence tab and readable-note download. All private fixtures remain ignored under reports/; original ZIP and live Tudela are untouched.

Verification: 118 Python tests (one optional-dependency skip) and 16 JavaScript tests pass. Coverage includes additions/removals, same-ID endpoint/confidence changes, unchanged maps, line movement, malformed/duplicate/missing-endpoint/evidence cases, display truncation and dense-neighborhood bounds. Updated the two running documents, README, Help and ten-page PDF; visually checked the new chapter and browser cards. Core features remain free/local, without new dependencies or services. Hosted ChatGPT remains disabled. Further work: more precise directional impact paths, richer supported-language fixtures and runtime validation by developers.


## Stage 0.17.0 — file-alert triage and isolated-run design (18 October 2026)

Added File alerts and a result-header shortcut with traffic-light counts. Green means no signals from the supported checks, not safe-to-run. Yellow includes possible damage, active content and inspection gaps. Red means a potentially dangerous pattern/disguise requiring investigation, not confirmed malware. Reasons link to findings; color text, filters and a separate possible-damage/invalid-format filter support review. File-level checks are labelled as such rather than inventing a byte offset.

Existing per-member 4 MiB, compression ratio and total expanded limits remain in force. Members within bounds are now fully read in memory through the ZIP reader for CRC/decompression checks, including inventory-only files. Damaged members are skipped with yellow alerts and other members continue. Encrypted, capped and unsupported members stay unverified. CRC is not malicious-tampering protection or proof of a valid image/document. Unsafe paths, symlinks, duplicate entries and invalid archive structures remain blocked; error wording makes the absence of execution explicit. Nested-member contents are not recursively risk-reviewed.

Selected triage signals: active file extensions (yellow, not automatically red), passive-looking names with executable-header candidates, document/image-looking active extensions, bidirectional filename controls, download-to-interpreter pipelines, encoded PowerShell and direct decode-and-execute. Text-pattern inspection covers selected source/script suffixes and the first 256 KiB; tails, unsupported encodings and formats remain disclosed. Comments/examples can match. Risk findings retain reasons/locations rather than command contents. No antivirus database, digital-signature verification, reputation lookup, dependency vulnerability audit or runtime malware analysis is claimed. No external scanner or new dependency is used; inputs are never extracted, executed, deleted or quarantined.

Tudela test: 266 files, all 266 CRC checked, zero failed/unverified members within these bounds; 122 green, 144 yellow, zero red; 4,161 total findings including file-review signals. Browser verification confirmed yellow filtering and matching counts. These are limited static results, not a malware clearance. A separate inert fixture (simple source/script, two-byte MZ file with a disguised name, and a deliberately damaged stored member) produced one red, two yellow and one green, retained the other files, filtered damage/invalid formats and opened the current Evidence tab correctly. This fixture is not a Tudela finding; private artifacts remain ignored under reports/.

Added docs/SANDBOX_DESIGN.md and in-product Help explaining that ZIP execution is not implemented. A future local companion plus disposable VM is proposed, with networking/clipboard/host-write disabled, narrow read-only inputs, synthetic configuration, reviewed commands, resource/time bounds and teardown. Static web hosting cannot create this native environment or provide free remote compute. Windows Sandbox requires a supported existing edition/hardware; Home is unsupported. Ordinary containers are not proposed as the sole boundary for unknown programs. Reviewed current Microsoft and Docker primary documentation; no VM was launched, host settings changed or Tudela code run.

Verification: 125 Python tests pass (one optional-dependency skip), plus 16 JavaScript tests. New tests cover CRC damage/continuation, encryption, unknown formats, parser failures, pattern limits, disguises, bidi display, pattern locations/privacy, encoded execution versus harmless decoding and evidence integrity. Baseline comparison tests now account for added/removed file-review findings. Both running documents, README and eleven-page Help/PDF updated and visually checked. ChatGPT remains disabled. Secure execution remains a separate unimplemented milestone.


## Stage 0.18.0 — readable handover, setup plan and sandbox preparation (18 October 2026)

Fixed the handover contrast defect caused by the shared dark article background. Handover cards, labels, headings, descriptions and controls now use an explicit light palette, including standalone exports. Added Setup & readiness as a primary report tab with eight inventory-name evidence groups: runtimes, lockfiles, templates, migrations/seeds, build/start/test clues, deployment/container files, backup/recovery and monitoring/operations. Each group is explicitly unverified and has a next action; filename matches are neither content interpretation nor proof of successful setup. Display shows 30 filenames per group and discloses further names in JSON. Local text export preserves the full bounded inventory plan.

Updated the public comparison with documented strengths and Reversium gaps against CodeBoarding, SonarQube Community Build/Semgrep CE, OSV-Scanner and Syft, plus VM execution tools. Primary sources are linked; this is a documentation review, not a benchmark or claim about undocumented competitor features. Gaps include deeper supported-language tracing/repository workflows, established code/security rules, version-aware offline advisories, full transitive/license inventory, standard SBOM formats and tested runtime execution. Optional local integrations and fixtures are prioritized; no scanner or advisory service was added.

Implemented sandbox preparation only: --sandbox-check reads OS edition and backend executable presence; --sandbox-plan NEW_DIRECTORY refuses overwrite and writes a host check, blank offline Windows Sandbox profile, explicitly untested QEMU argv draft and instructions. No subprocess or VM is launched, ZIP copied, host folder mapped, OS feature enabled or dependency installed. The local server has a read-only /sandbox/status endpoint; the browser edition disables host inspection. Profile policy tests verify absent networking, host mappings and startup commands. These profiles are not a working Tudela runner: a trusted backend/image, actual guest boot, isolation checks, termination supervisor, runtime provisioning and ZIP input design remain required.

Host investigation: Windows Core/Home; Windows Sandbox and QEMU executables absent. Docker CLI is installed but its engine was unavailable. QEMU was also not found inside WSL. WSL Ubuntu is present but not treated as a disposable unknown-code boundary. QEMU plus a trusted Linux guest is the proposed zero-upgrade-cost route to investigate next. Actual execution remains blocked on missing prerequisites and unvalidated isolation, not on a paid service requirement. No claim of zero-risk execution is made.

Browser verification with the private Tudela ZIP: 266 files and 4,161 findings; all eight readiness groups displayed, with filename clue counts 1/1/1/44/34/3/12/4. These are inventory matches only. Verified readiness text download, disabled online host check, readable handover status/owner/notes fields and screenshot. The actual local server correctly reported the missing backends through the prerequisite button; no guest started. Sandbox profiles were generated under ignored reports/sandbox-stage1. Updated Help and visually checked the new chapter in the twelve-page PDF.

Validation: 128 Python tests pass (one optional-dependency skip), 16 JavaScript tests pass. Added tests for inventory-only evidence and secret exclusion, missing backend status, safe profile defaults and refusing directory overwrite. Both running documents, README, comparison and sandbox design updated. Core analysis remains free/local, hosted ChatGPT disabled and arbitrary ZIP execution unavailable.


## Stage 0.19.0 — offline QEMU guest and Tudela build/start pilot (18 October 2026)

Implemented the native Windows CLI QEMU supervisor, asset bootstrap and public offline dependency preparation. Pinned QEMU 11.1.0 Windows and Alpine virt 3.23.6 checksums are checked over HTTPS; extracted runtime files are rehashed. QEMU's official site refers to the Windows binary provider, which describes its builds as experimental. This is publisher checksum verification, not independent signature attestation. QEMU is extracted into ignored reports/qemu-lab without running an installer or changing PATH. Optional pycdlib 1.14.0 lives only in that lab. Existing 7-Zip is required. No paid service, Windows upgrade, feature enablement or reboot was used.

The explicit --sandbox-self-test boots only benign input. The fixed --sandbox-tudela ZIP action reruns it before creating a separate application guest; arbitrary project scripts are refused. TCG is the default, with explicit WHPX selection when already available. Both profiles passed all 14 selected checks: expected Alpine, loopback-only interface, no external routes, guest-to-host listener unreachable, no host-share mounts, readable benign input, rejected filesystem writes, no Windows mount, unchanged input image, unchanged host canary, no host connection, fresh guest without previous marker and enforced one-second termination. Every application attempt uses a fresh isolation gate with the same accelerator. This is not proof against hypervisor flaws or all possible attacks.

The enforced guest has no NIC, host shares, clipboard integration, passthrough, remote display/control or forwarded ports. Read-only raw CD media supplies the trusted OS and narrow application input. Guest state is RAM-backed, with 1 GiB RAM, two virtual CPUs, maximum 600-second application lifetime and bounded 2 MiB serial logs. Windows kill-on-close job supervision and explicit teardown stop QEMU. Pacing serial input fixed dropped commands during early tests. Enabling guest loopback fixed internal HTTP without creating external connectivity.

Tudela delivery SHA-256: 6271cf0f60c7da652bb0ee36bcbbff02a4693a0310f97dd70a11db1ec5af466b. All 266 members passed CRC inspection and no red file signals were present; this is not malware clearance. In-memory repacking omitted common environment/key/generated paths; only .env.example was omitted in this delivery. This filter cannot find every embedded secret. No source was extracted or executed on the host. Provisioning downloaded public package identifiers only: 235 compatible locked npm entries (229 distinct tarballs), plus 22 Alpine runtime APKs. npm SRI and guest APK signature trust remain enforced; lifecycle install hooks are skipped. Early APK setup failures (ephemeral live-guest rule and OpenSSL version mismatch) were resolved without --allow-untrusted.

Actual final WHPX run: Node v24.18.1 and npm 11.11.0 installed offline; libraries unpacked; Vite frontend build and TypeScript backend compile returned success. The compiled production server started with reserved .invalid HTTPS service addresses, distinct synthetic keys and HERZL simulator mode. Its production configuration guard was preserved. Guest-local GET / returned HTTP 200 with a nonempty response. Interface/route checks remained isolated afterward, input ISO hash was unchanged and the guest process stopped. No real Supabase, account, live AI key or live Tudela request was used. Earlier production startup correctly rejected missing/incorrect synthetic configuration; this blocker was recorded and resolved with the actual required variable names.

This proves build/start and one internal HTTP response, not a functioning database, login, storage, published tour, full browser journey or production readiness. No host preview was exposed. Private source-bearing ISOs, caches, logs and results remain ignored under reports/qemu-lab; teardown does not erase these host artifacts. Next: disposable database/auth/storage fixtures and a guarded preview design before any wider application support. Hosted ChatGPT stays disabled.

Updated Setup & readiness/File alerts copy, local prerequisite summary, README, sandbox design and thirteen-page Help/PDF. Browser verification confirmed build 0.19.0 and the local 14/14 historical lab record, explicitly not attached as runtime proof to the displayed sample report. Fixed the local CSP to permit only embedded data images for the existing logo. PDF sandbox chapter rendered and visually checked. Validation: 136 Python tests pass (one optional-dependency skip), 16 JavaScript tests pass. The first restricted-shell suite failed loopback permissions; the authorized local-network rerun passed. Private VM artifacts were excluded from publication.


## Stage 0.20.0 — maintained Help, product messaging and commercial focus (18 October 2026)

The shared thirteen-chapter user guide remains available on Start and every report through Help, as standalone HTML and as a downloadable PDF. Added local keyword/task search with matching chapters expanded, a no-match message and clear-to-reset behavior. Guide build metadata is generated from the application version. Added a stdlib release gate and CI step checking guide/app version, standalone and embedded HTML/script identity, PDF byte equality with the embedded download, browser engine/version/checksum and packaged guide consistency. Contributor policy requires guide changes whenever behavior changes, both running documents and browser/PDF review; the automated gate checks consistency, not semantic completeness.

Removed promotional licensing attribution and repository-hosting links from product copy, generated reports, Help/PDF, landing/demo, README and documentation. Links to product documents are relative. Historical attribution/source-link wording was normalized while retaining stage outcomes. Existing legal/dependency licence files are preserved. Hosting, repository visibility and licence terms were not changed. Added exact local server routes for the guide, market page and public PDF, including binary response support, so the direct PDF fallback works locally without a repository link. No arbitrary filesystem route was added.

Commercial assessment now focuses on agency/maintainer handover and owner/developer transitions. Official CodeBoarding, SonarQube and CAST documentation confirms adjacent offerings and overlapping capabilities; this is not proof of demand for Reversium or a competitor benchmark. Recommended experiment: five real handover pilots, at least three unfamiliar codebases, source-verified answers and measured review time/accuracy, followed by an explicitly hypothetical scoped paid service. Core analysis remains free/local. Saved an elevator pitch and a short version; claims avoid complete code understanding, guaranteed security, exclusive diagrams or impossible-to-reproduce AI results.

Development continued with Help usability, release consistency and a streaming QEMU asset digest compatible with Python 3.10 (removing the Python 3.11-only file_digest call). Known-byte SHA-256/SHA-512 tests cover the compatibility change. The sandbox isolation policy and disabled hosted ChatGPT state remain intact. Next milestone: attaching reviewed local run outcomes to the exact delivery identity, then disposable supporting services and one acceptance journey; neither is claimed delivered here.

Verification: 137 Python tests pass (one optional-dependency skip), 16 JavaScript tests pass, and the release documentation gate passes. Browser tested Start Help, matching/nonmatching/cleared searches, actual PDF download, report Help and direct local PDF route. First/last PDF chapters rendered and visually checked. Private Tudela source and VM artifacts remain ignored and excluded from publication.


## Stage 0.21.0 — attach exact-delivery sandbox evidence (18 October 2026)

Added a portable v1 sandbox-result contract and producer for the reviewed tudela-offline-build-start-v1 profile. Each application attempt after its isolation gate writes run-evidence.json plus ignored lab latest-run-evidence.json. Fixed fields contain original and filtered-copy SHA-256, omitted-member count, run ID, UTC timestamps, producer version, accelerator, Node/npm versions and explicit boolean/null outcomes for 14 isolation and 11 application/teardown checks. Source, filenames, key values, commands, raw logs and exception strings are excluded. Older private results are not silently reinterpreted. This is an unsigned, editable local record; identity matching does not authenticate execution or its producer.

Setup & readiness now leads with Runtime tests for this exact ZIP, followed by separately labelled Static setup clues. The importer is bounded to 256 KiB, validates the exact original ZIP fingerprint and fixed profile/schema, timestamps, runtime metadata, expected check keys/types and prerequisite ordering. Missing outcomes are explicit null; impossible application claims after failed isolation or prerequisites reject. Selection only previews. Explicit attachment, replacement, removal, separate JSON/text save and restoring saved JSON are available. Invalid replacements preserve the earlier attachment. No static finding, handover status or AI packet is automatically changed. The Handover tab links to the runtime review.

The report frame uses the existing parent-owned picker/download broker, with new explicit runtime result types and filenames. Applied records live in a separate JSON script element, outside static report-data. Standard technical JSON remains static. Readable HTML retains only an applied record and validates it again on load; pending previews are cleared before export. Invalid/absent saved records reset controls and visible evidence. Unknowns and trust limits are displayed prominently; the original delivery and the filtered copy with synthetic settings are never described as identical executions. No browser execution endpoint, new service, paid dependency or account requirement was added; hosted ChatGPT remains disabled.

Tightened sandbox input preparation to derive its fingerprint and filtered ZIP from one bounded in-memory snapshot (maximum 64 MiB), preventing a path replacement between inspection and repacking from binding the wrong bytes. A regression fixture replaces the original ZIP during inspection and confirms the guest copy/hash still identify the captured original bytes. No host extraction occurs.

Fresh Tudela sandbox run e63d8240088d (18:10:55–18:13:22 UTC): exact original SHA-256 6271cf0f60c7da652bb0ee36bcbbff02a4693a0310f97dd70a11db1ec5af466b; filtered-copy SHA-256 965129809652d549b50b7a45ce739518f61122cc3c550ad7221258bb07a40089; one omitted member. All 14 isolation and 11 application/teardown checks passed. WHPX, Node v24.18.1, npm 11.11.0; frontend/backend build and internal HTTP response succeeded; image unchanged and guest stopped. No guest external interface, host shares, forwarded ports, live service values or live Tudela interaction. Database/auth/storage, published-tour and interactive browser journeys remain unverified.

Browser verification with the real ZIP: 266 files and 4,161 static findings; matched preview stayed unapplied until explicit attachment; a controlled mismatched fingerprint was rejected while the original attached run stayed intact. JSON result download, remove and restore passed. A controlled failed-frontend preview showed one failure and three unrecorded later checks without overwriting the real result; HTML exported while that preview was pending retained only the real applied run. Read-only inspection confirmed the exact attached JSON, empty preview and absent AI panel; technical JSON remained static. Extracted saved-HTML evidence passed restore validation. Browser policy blocked direct file-URL reopening, so full saved-HTML browser execution was not claimed tested. No workaround for that policy was used.

The broad workspace preview was rejected by automatic approval review because it could expose private sandbox artifacts. A materially narrower public-web-assets-only preview was used instead; private inputs/results/logs were selected locally through the file chooser and never served or published. A restricted-shell snapshot test initially hit temporary-directory permissions; the authorized full local test run passed.

Updated Help/PDF with a fourteenth chapter covering generation, exact matching, filtered input, outcomes/unknowns, unsigned trust, export and removal; rendered and visually checked. Both running documents, README and current roadmap updated. Validation: 140 Python tests (one optional-dependency skip), 22 JavaScript tests and documentation release gate pass. Added browser validation tests to CI as a separate Node job. Private records, mutated fixtures, exports and VM artifacts remain ignored under reports/ and outside publication.


## Stage 0.22.0 — disposable services and API tour acceptance (18 October 2026)

Implemented a separate reviewed tudela-offline-tour-v1 profile with real PostgreSQL 17.11, Supabase Auth 2.197.0, PostgREST 16.4 and Supabase Storage 1.83.5. The provisioning script downloads pinned public artifacts only, verifies publisher/image hashes and caches signed Alpine packages; it neither uploads source nor installs services on Windows. Storage uses its actual application runtime on the signed guest Node runtime, rather than a complete vendor Docker deployment. Publisher checksums over HTTPS are not independent signature attestation. Standard database roles, grants and JWT helpers support the original Tudela migrations and policies; no application permission checks were removed.

The bounded profile uses 3 GiB guest RAM, two CPUs, a 2 GiB RAM workspace, a ten-minute application deadline and the existing 2 MiB serial limit. Fresh isolation checks run at the same memory size before application input. There is no NIC, host share, passthrough, forwarded port, remote display or host browser preview. Credentials and a locally trusted TLS certificate are generated inside the guest; certificate verification stays enabled. Database and files remain in guest RAM. Private host input images, dependency caches and logs remain ignored after termination; teardown is not secure-erasure certification.

Actual WHPX run 1eb69ba4c21f, 18:44:51–18:47:28 UTC: all 14 isolation and 26 application/service/journey/teardown checks passed. Original ZIP SHA-256 6271cf0f60c7da652bb0ee36bcbbff02a4693a0310f97dd70a11db1ec5af466b; filtered input SHA-256 b976f5f11f734854cbdde0c7466649a9503fcf6b6fee465ff2213d942f11a5a8, one omitted environment-example member. The original archive was unchanged. Node v24.18.1/npm 11.11.0, 39 selected runtime packages and the original migrations supported successful frontend/backend builds and production server startup with guest-only services.

A reviewed derivative of the supplied acceptance script logged in separate editor/reviewer users, rejected a wrong password, tested role and tenant restrictions, confirmed direct storage upload denial, uploaded an image through the media gateway, approved and published one tour with two ordered stops, and retrieved the published tour JSON and exact image bytes through the running Tudela HTTP routes. Supplied cleanup closed test tenants and suspended users. Guest isolation remained intact afterward, the input image matched and QEMU stopped. Earlier attempts exposed guest disk pressure, Auth helper ownership and missing standard Storage grants; these bootstrap issues were resolved without weakening Tudela policies or assertions.

Portable schema v2 records the distinct service profile, prepared versions, guest memory and fixed boolean/null outcomes. Existing v1 build/start records remain supported. The importer rejects inconsistent dependency claims and shows API acceptance separately from static findings. Version metadata alone is not service-health proof. The record remains editable, unsigned local reviewer evidence, not execution attestation. No CMS button-click publishing, real email/OAuth, external AI/maps, production stability or comprehensive security certification is claimed. Hosted ChatGPT remains disabled.

Help/PDF now has fifteen chapters, including preparation, execution, exact-ZIP linking, cleanup and limitations. New tests exercise generated local credentials/configuration, fixed loopback gateway targets, tampered service inputs, memory bounds and v2 evidence validation. Validation: 143 Python tests pass with one optional-dependency skip; 27 JavaScript tests pass; the documentation release gate passes. The new PDF chapter was rendered and visually checked. Browser verification passed with the real Tudela archive (266 files, 4,161 static findings): the v2 result matched its fingerprint, remained preview-only until explicit attachment, then displayed 26 passes, prepared versions, 3072 MiB memory and prominent API-only unknowns. No source finding was automatically verified. Private inputs and records remain outside public assets. Next: separately design guarded interactive CMS verification and operational recovery tests, rather than treating API acceptance as complete platform coverage.


## Stage 0.23.0 — guarded CMS browser testing (18 October 2026)

Added scripts/test_tudela_cms.py as an explicit reviewed local test profile, not a browser ZIP-execution endpoint. It repeats the 3 GiB blank-guest gate, prepares real disposable services and separate synthetic editor/reviewer accounts, and builds the original frontend for a dedicated random host-loopback HTTP origin. The guest retains no NIC, host shares, passthrough or forwarded network port. A bounded serial relay targets only the fixed guest HTTPS gateway with CA verification intact. The browser-to-host leg is loopback HTTP and differs from production TLS; no certificate-warning bypass or disabled guest TLS verification is used.

The listener requires an unpredictable private entry cookie, exact Host and mutating-request Origin, allowlisted headers, relative targets and bounded request/response bodies. Browser CSP blocks external resources/connections and framing. External redirects are refused. Guest-only header caching and explicit completion of one-shot HTTP clients reduce serial overhead. Requests are serialized and private route/status diagnostics are capped; source, auth headers and request bodies are absent from that diagnostic. No host filesystem root is served. Selected boundary checks do not certify browser, app or hypervisor security.

The manual profile has separate resource bounds: thirty-minute total guest deadline, twenty-minute preview window, two CPUs, 3 GiB RAM, bounded 2 GiB workspace and 32 MiB private serial log. Normal automated profiles keep their existing ten-minute/2 MiB bounds. /__reversium exposes a gated Stop control. Source-bearing host images, credential files, browser sessions, screenshots and logs can remain after guest teardown and are ignored from publication. A Windows invalid-pipe cleanup exception found during a forced stop was fixed and regression-tested.

First launch stopped before browser access because serial prompt text preceded the fixture marker; fixed parsing accepts the fixed marker without relying on line position. The first browser attempt reached editor creation/submission but exceeded practical serial responsiveness; it was stopped without claiming publishing success. A fresh profile with reduced transport overhead was used for the recorded journey. No Tudela business logic, migration or permission assertion was changed to obtain a pass. No automatic API acceptance script created or published the browser tour.

Manual CMS evidence is separate from portable API records: cms-result.json records setup/teardown and leaves browser_publishing_verified null; it does not overwrite the latest API evidence or attach as a false API success. The reviewed browser test report identifies the original ZIP, run and actual visible outcomes. See SANDBOX_CMS_TEST.md for completed steps, blockers and limits.

Help/PDF now contains sixteen chapters and explains local entry, disposable credentials, the different browser origin, stopping and artifact retention. New tests cover Host/Origin/cookie gates, external targets, body bounds, omitted host cookies, cached headers and Windows teardown. Final regression: 147 Python tests with one optional-dependency skip and 27 JavaScript tests passed. The PDF preview chapter was rendered and visually checked. Hosted ChatGPT remains disabled. Public artifacts contain documentation and fictional demo data only.


Recorded browser run 7eead40febda on the exact Tudela ZIP: editor signed in, used the New Tour Wizard to create Reversium Browser Test City with two ordered stops, and received Tour submitted to the review queue. Signed out and signed in as a separate reviewer; clicked Approve and Publish approved revision for the city, tour and each stop. Final CMS showed 1 published city, 1 tour, 2 stops, Revision published and zero pending items. After reviewer sign-out, the organization-specific anonymous visitor page displayed the new city, named Heritage Tour and both named stops in order. Route/status diagnostics corroborate four review submissions, four approval inserts, four successful publication calls and HTTP 200 for public content. Setup fixtures are distinguished from these browser-created records; media upload/narration/maps/walking and production behavior remain untested.

Cleanup exposed a separate form-origin rejection. Automatic approval review refused a direct shutdown API call after that rejection as an access-control bypass; it was not executed and the guest was left to the original deadline. Fixed the form with an independent unpredictable CSRF token plus the existing entry cookie, keeping exact Origin checks for guest/application writes. Invalid tokens/missing cookies reject in regression tests; a browser test of the corrected form on an unrelated mock server with no guest completed successfully. No weakened Origin policy was applied to the active guest and no API bypass was retried. External fallback thumbnails were visibly blocked; no browser image-upload pass is claimed.


Confirmed teardown at 19:38:19 UTC by the original twenty-minute preview deadline: listener closed, QEMU stopped, post-test loopback/no external route passed and input image unchanged. Run 7eead40febda started 19:16:07 UTC; filtered-copy SHA-256 f7cebd79b5a6fbe5c35bd5dbbdbc8a42ea4c45fc767e55a14c3e9c477319acef, original SHA-256 unchanged as recorded above. 291 requests relayed. Private setup result remains explicit about manual browser unknowns; separate reviewed observations and screenshots establish the limited journey. Previous v2 API evidence remains unchanged. No private source, credentials, entry URL or VM artifact was staged.
