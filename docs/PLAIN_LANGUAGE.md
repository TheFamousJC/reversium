# Reversium, explained without technical background

Project names in historical notes have been anonymized. Recorded counts, fingerprints, outcomes and limitations describe a specific reviewed example, not arbitrary code packages.

Living explanation. Last updated: 2026-10-18.

## Optional help inside Reversium — version 0.10.0

The new AI assistant sits in the same report interface. A three-step wizard helps you connect your own eligible ChatGPT account, choose findings and review exactly what you would share before sending a question. Answers appear beside your report, with links back to selected evidence and a separate list of unknowns. A FAQ explains privacy, setup, limits and troubleshooting.

The local analyzer stays free and works without an account or internet. AI is optional and uses your account's eligibility and plan limits. OpenAI sign-in briefly uses a provider screen; Reversium never asks for your ChatGPT password or a paid API key. Your ZIP is not automatically uploaded. Finding descriptions and file paths may still be private, so inspect and edit the preview. Redaction can miss secrets.

Connecting alone shares no software evidence. Each Send requires fresh approval; the assistant cannot install software, execute commands or edit files. Its citations only establish which selected finding it references, not that the explanation is true. Local tools and actual tests remain the way to confirm behavior.

Tokens remain in memory and disappear on disconnect or restart. Local registration identifiers are retained to reconnect the same account. Saved report exports exclude assistant conversation and account details. Disconnecting locally does not revoke OpenAI-side authorization; use ChatGPT settings for that.

The interface and safety checks have been tested locally. A real account sign-in and cloud answer still need user acceptance. We have not sent reviewed example application's private source findings to the provider. The earlier local reviewed example application rehearsal did verify administrator provisioning, draft import and a published five-stop tour in a separate local database; its private handover report retains the results and remaining gaps.

## Following more reviewed example application workflows in version 0.8.0

The map can now follow selected actions passed between React screens. For example, the chat screen's send action connects to the callback supplied by the main app, then to the `/api/chat` request and supported backend/data references. A CMS save action can connect to a callback returned by its content-management helper and then to the database code. Click a box or line to inspect the source evidence.

It also follows some addresses built from local constants or passed into request helpers. The staff screen's helper calls fetch with a variable URL; the report can now show which caller supplied the staff endpoint and which HTTP method it requested. Evidence includes both the caller and the helper. Different callers are kept separate so a read action is not accidentally described as a write action.

On your original ZIP, the report shows 172 possible prop bindings and 52 resolved API-target contexts. A context is one caller/path/method combination; it is not a unique service or a verified working feature. The number of source files and starting points is unchanged: 115 JS/TS files, 25 route references and 32 React/JSX modules. We checked the chat and staff maps in the browser, followed the chat prop link to its exact source line, inspected both staff caller/helper locations, and passed 96 automated checks.

A passed action can still have several possible providers, and the program might choose among them while running. Reversium displays those possibilities rather than choosing one. State-setting callbacks, more complex property forwarding and addresses controlled by environment settings can remain unknown. A recognized API path also does not prove the same server will handle it after deployment. None of reviewed example application's code or requests are run by the analysis.

Large maps can exceed display or tracing limits. The App and CMS views disclose these; a smaller selected workflow is easier to inspect. JSON keeps the generated reference data. Reversium remains local and free, without an AI service, account, Node installation or API key. Your ZIP and private report are not published with Reversium's code.

## What changed after testing your reviewed example application ZIP

Version 0.7.0 maps much more of reviewed example application than the first report. It reads all 115 JavaScript/TypeScript files in that ZIP, including 32 files containing React screen/component code. It recognizes 25 web-route references, rather than drawing only the narration endpoint. The map offers 57 starting points: those routes and React modules. These are starting points for investigation, not 57 proven business features.

For example, selecting TourCommunityPanel shows references from the community screen to helpers for comments and likes, then to named Supabase database routines. The map can also connect those routine names to table operations written in database migration files. Click a box or line to see its evidence and the source file/line. Old migration definitions can appear alongside newer ones; Reversium does not know which versions were applied to your real database.

Select a feature to rebuild its focused map. This brings in connections that were outside the overview's display limit. The view reports any omitted boxes/lines. Solid lines mean source references were recognized; dashed lines mean a possible connection based on a data name or route path. Neither means that the action succeeded or is available to a visitor.

At the v0.7.0 stage, screen-to-screen callbacks and constructed addresses were major gaps. Version 0.8.0 adds the selected patterns described above. More complex forwarding, state changes and dynamic table names remain unknown; reading every code file is still different from proving every workflow.

Everything stays local and free. Reversium does not start reviewed example application, contact Supabase or Google, install reviewed example application's dependencies, or send your archive to an AI service. Your analyzed software may still need paid services when you run it independently. We tested the real ZIP in the browser, checked a focused community map and its database evidence links, and passed 72 automated checks.

## Why use this instead of asking ChatGPT?

ChatGPT may explain an unfamiliar program more fluently and recognize patterns Reversium misses. Reversium's purpose is a repeatable local inspection: the same rules, file-and-line evidence, inspectable diagrams, saved reports and comparisons after code changes, without an account or model/API charge. The useful combination is an evidence-backed map for checking facts and a human or assistant for interpreting them. Reversium does not yet replace a thorough code review or runtime testing.

## Our focused plan

Reversium's job is to help you upload unfamiliar software, see its features and connections, and check the evidence. Development has resumed. **The feature interaction map is the next milestone.**

The focused feature list is: an interaction diagram, a plain-language feature catalogue, selected JavaScript/TypeScript tracing alongside Python, clickable evidence, visible confidence/coverage, and map export/comparison. The diagram should show a route leading to its handler and helpers, then to data or an outside service. Features that may share data can appear connected through that data, with uncertainty clearly labeled. Matching names alone do not prove a shared database or a complete workflow.

We are deferring automatic installation/running, deeper decompilation, AI, cost estimates and automatic rebuilding. Keeping that boundary makes the product useful without growing into an unlimited reconstruction project.

The next milestone has now been delivered in version 0.6.0. The focused workflow is available: feature catalogue, interaction map, selected Python and JavaScript/TypeScript tracing, clickable evidence, uncertainty/coverage, and map export/comparison. This means the supported patterns work; it does not mean every application or framework is understood.

## How the feature interaction map works

Open Architecture after analyzing a ZIP, or try either local sample on the home page. The map connects a feature's route to its handler, its helper functions, and recognizable data operations. For example, a contacts listing and a contacts insert can point to the same table-name candidate. Solid lines show references traced in supported code. Dashed lines show inferred data-name connections: matching table names might belong to different databases, so this does not prove the features share real data.

Choose a feature to rebuild a focused view of its connections. Select a box or line to see the evidence and unknowns, then follow a source link into Evidence. The catalogue below the map gives short descriptions such as “Read contacts records,” grounded in recognized SQL operations. It does not invent a CRM or other business purpose from a route name.

Download map SVG saves the current diagram view, subject to its displayed limits. HTML/JSON exports retain the full generated map data even when you filtered the screen; HTML rebuilds its overview when reopened. CLI exports also write `feature-map.svg`. To compare versions, use `python -m reversium newer.zip --compare older-report.json --output reports/newer`. Added map items are green, changed items amber, and removals are listed. A baseline without a map is marked unavailable rather than interpreted as an empty application.

The Python sample uses SQLite. The JavaScript/TypeScript sample uses selected Express and PostgreSQL patterns; MySQL calls through selected mysql2 patterns are also recognized. The JavaScript reader uses local rules, not a complete compiler, and does not need Node or install packages. Unsupported syntax, dynamic queries, middleware effects and many frameworks remain unknown. The program being inspected is never run.

## Who is this for, and what do I need?

This is for a developer taking over unfamiliar code, a consultant assessing a legacy package, a technical lead planning a migration, or a software owner preparing a handover. You need a ZIP you are allowed to inspect, Python 3.10 or newer (or the bundled runtime through the Windows launcher), and questions you want answered. No cloud account or API key is needed.

A non-programmer can use the overview to ask better questions. A developer should review the evidence before using it to change or deploy software. A useful first question is: “Which routes read or change this data, and where is that code?”

We verified both sample maps in the browser, map filtering and evidence inspection, SVG/HTML export and a comparison with an added delete feature. Fifty-nine automated tests pass. The focused MVP is ready for trying representative packages; gaps in coverage must still be reviewed.

## What it does today

Reversium helps you understand a software package. You give it a ZIP file, and it makes a list of what is inside. For selected kinds of readable code, it identifies named building blocks, references to other software and possible web addresses or application routes.

It presents a report and a diagram. Each finding includes the file and line where it was found, so someone can check the evidence. The diagram connects files to software names they mention. It does not prove that those connections are used when the program runs.

The latest version can also connect some references to other files inside the same ZIP. Each reference is labeled: internal means a matching local file was found; external means a package was declared; unresolved means there is not enough information; ambiguous means more than one file could match. These are clues for review, not proof of what happens when the software runs.

For Python, it recognizes some possible web routes and data-model classes. It also reads common dependency lists for Python, JavaScript and Go. The inventory says which files received deeper inspection and which were only listed.

## How to use it

Install Python 3.10 or newer, open a terminal in the Reversium folder and run `python -m reversium`. A browser page opens. Choose your ZIP and click Analyze archive. To create saved reports directly, run `python -m reversium your-package.zip --output reports/my-project`.

On Windows you can also run `./Start-Reversium.ps1`. Reports now open on “What this software does,” a plain-language overview of what the findings suggest. Architecture shows the likely platform, supporting services and diagram; Evidence shows the findings and search box; Coverage shows the inventory, binary inspection status, readiness and limitations. Use the arrow keys while a tab is focused to switch tabs.

Each explanation includes “Still unknown” and a link to its supporting finding. Click that link to open the exact evidence, even if a search filter previously hid it. The overview shows up to 16 groups; additional findings remain available in Evidence. If the tool lacks enough evidence, it says so instead of inventing a purpose.

The latest version follows some Python web handlers into helper functions, including helpers in other files. When it recognizes SQLite operations, it can explain that code reads, adds, updates or deletes records, asks to save pending changes, or returns rows or named response fields. For example, the local sample links a request for contacts to the helper that reads the contacts table. The evidence includes both the handler and the data operation.

This is still a code trace, not a successful test run. The code might run only in certain conditions, be unused or fail. Unsupported calls and dynamically built database queries stay unknown. Class-based handlers and database frameworks beyond the supported patterns remain unknown; the newer TS/React/Supabase reference reader is described above.

If tabs were missing, start the current version with `./Start-Reversium.ps1` and use the new browser address it opens. The launcher now chooses a free local port, so an older server on port 8765 does not keep serving the old interface. Look for version 0.8.0 at the top. The home page offers sample links for all four sections; after analyzing a ZIP, report navigation stays visible near the top and while scrolling. Without JavaScript, the links still move between visible sections.

## What is the practical application?

Use Reversium when you receive unfamiliar software and need an evidence-backed starting point. A maintainer can locate a route and the database operation behind it. Someone taking over a legacy system can inventory files, dependencies and possible features. A team planning a migration can find components and supporting services that need investigation before estimating a rebuild.

The useful output is a map of what was found, where it was found, and what must still be checked. It saves initial discovery work. It does not yet run the submitted system, prove all business rules, certify security or produce a stable rebuilt application.

In Evidence, type in Filter evidence to find a file, name or reference type. Download JSON saves structured results for later comparison; Download HTML saves a report you can open in a browser. Both downloads include all sections and findings, even when another tab or filter is active. Printed reports show every section. On a narrow screen, slide the diagram or table sideways to see the remaining columns.

To compare two versions, save the first JSON report, then run `python -m reversium new-package.zip --compare reports/old/report.json --output reports/new`. The new report lists added and removed files and findings. It can identify changed readable files when both versions were inspected. It does not yet compare how programs behave, and comparison currently starts from the terminal.

## What we checked

We tested the source example, both report formats, and desktop-size and narrow phone-size layouts. For binary analysis, we uploaded a second example containing source, settings and synthetic program headers. The browser showed 8 files, 5 binary candidates and 27 findings. It correctly showed one broken file as partial, identified likely supporting services, and filtered the two imported-library findings. The new explanation tab shows 11 groups for that example. We checked its evidence links, the honest unknown state for a package without useful program evidence, and the saved HTML export. Thirty-six automated checks passed. These tests use examples; they do not promise every software package is fully understood.

For version 0.5.0, the checks expanded to 45 passing tests. We also checked real browser ZIP upload, visible report tabs, the local sample, and navigation with report scripts removed. The sample’s two files produce 19 findings and explain a read operation and an insert/save operation with source links. Those statements describe supported code paths, not confirmed runtime outcomes.

## Privacy and cost

The work happens on your computer. There are no subscriptions, accounts or paid AI requests. You still supply the computer, electricity and time. Reports may reveal private file names and software details, so check them before sharing.

## What the report cannot promise

A list of ingredients is not the same as understanding every recipe. Reversium cannot yet explain every business rule, recreate an application automatically or promise a reliable rebuilding price. Some findings are educated pattern matches; the report labels them as such. Missing findings do not prove a feature is absent.

It now inspects some compiled programs without running them. It can recognize formats, show certain operating-system or processor clues, and list some referenced libraries or classes. Findings point to positions inside the file, called byte offsets. A broken file can still provide partial clues, which the report labels. It does not use a decompiler to reconstruct source code.

For Android and Java packages, it can list the inner package directory without opening the contained programs. Large, compressed or unsupported files may still be listed without their contents being inspected. A reader status of “complete” means the supported inspection finished; it does not mean the program is complete, safe or ready to run.

## Can it tell me what the software platform is?

It can identify likely ingredients and broad types. For example, references to FastAPI and Python can suggest a Python web API, while a Windows binary header can identify a Windows target and processor type. It shows the supporting file or byte position for those clues.

It cannot reliably conclude that an unknown package is a complete CRM, accounting system or other specific business product from these clues alone. Understanding the exact purpose, features and completeness still requires reviewing behavior and requirements. When it lacks evidence, it says the purpose is unknown.

## Can it tell me exactly what the program does?

Not for an arbitrary ZIP. The “What this software does” tab now turns supported clues into short explanations of possible behavior. For example, a database reference suggests the application may keep records, but does not prove it actually stores anything. A web entry-point name does not prove what it returns or who can use it. Binary strings are not treated as proof of a feature. All explanations use rules on your own computer, with no paid AI service.

These are not a complete description of every feature or business rule. Missing services or files, configuration, dynamically loaded code and obfuscation can hide important behavior. Every explanation includes what remains unknown, and the tab lists further questions and ways to check the interpretation.

For a small, complete source program, careful code review may explain its behavior precisely. For a larger platform, a dependable functional description needs deeper source tracing, requirements review and isolated tests. Even running it only demonstrates the scenarios actually exercised. Reversium does not yet generate a comprehensive functional specification or run those tests; the Coverage tab makes this limit explicit.

## Can it set up and run the ZIP?

Not yet. Reversium currently inspects the package; it does not install dependencies, run installation scripts or start the submitted software. The planned approach is to prepare a setup plan and validate it in a separate disposable virtual computer, with test configuration and data. A package can be missing source files, licenses, private services or credentials, so automatic startup cannot be promised for every ZIP.

## Can it tell me which supporting platforms I need?

It now lists evidence of some supporting services, such as PostgreSQL databases, Redis caches, message brokers and selected external integrations. It reads known client-library names and simple container-image declarations. A reference might belong to a development tool or an optional feature, so the report does not call every service mandatory.

To run a stable version, someone must still confirm service versions and settings, credentials, database setup, resource needs, backups, monitoring and recovery behavior. Reversium shows these as open questions. It does not yet size or test a deployment. Reversium itself remains local and free; services required by the original application may have their own costs or access requirements.

## What comes next

We will expand readable-code and compiled-program analysis, then add optional local decompilers for deeper inspection. Later, optional local AI can help draft explanations, and adjustable planning tools can estimate rebuilding work and running costs. Those estimates will show the assumptions behind them. Isolated setup and startup checks remain a separate future stage.

## Keeping this explanation current

Whenever a feature becomes available, update what the tool does today and remove any promise it still cannot meet. Keep planned capabilities separate from working capabilities.


Update 2026-10-17: live ChatGPT sign-in/model discovery succeeded, but the first minimal evidence request failed before an answer was displayed. No AI answer has been accepted against source evidence. Fixed assistant initialization after in-page ZIP uploads and added safe provider HTTP status/code diagnostics without raw provider messages, tokens or evidence. Reconnection after restart is required for the next live test.


## About, FAQ and report downloads - build 0.10.1 (2026-10-17)

About now explains Reversium in plain language: practical handover and maintenance uses, a simple reading workflow, optional AI and limitations. Build 0.10.1 and 3Sci.com / 2026 are displayed. Uploaded-code explanations remain available in Software findings. FAQ has its own report button and home help button, including the assistant questions. HTML is the readable report for offline review and handover; JSON is structured findings for scripts, tools and baseline comparison. Both can contain private analysis details; neither is the original ZIP or a runnable backup.


## Contemporary interface and short control help - build 0.10.2 (2026-10-17)

Refreshed the home/report UI with light surfaces, indigo controls, compact segmented navigation, responsive typography, bordered content cards and clearer form styling. All visual assets remain local. Short explanations appear on pointer hover and keyboard focus for buttons, navigation, expandable explanations, graph inspection controls and the archive picker. Escape dismisses help; it is linked with aria-describedby, placed within the viewport and omitted from saved HTML. Reduced-motion preferences are respected. Browser verified the light report layout, wrapped navigation and Download HTML keyboard tooltip; all 107 regression checks passed.


## Guided Start flow - build 0.11.0 (2026-10-17)

Replaced the crowded home with four steps: Start (choose understanding, handover or maintenance goal), Choose ZIP, Review findings, and Save & next steps. The first two steps contain no downloads or account setup. Analysis opens on Review findings with goal-specific reading guidance; buttons lead to feature connections, gaps and the final save step. HTML/JSON downloads are only in Save & next steps after an analysis exists. AI is optional after review. Sample reports are explicitly marked as fictional demonstrations.

Browser verified the full flow against the reviewed example application ZIP: handover goal carried into analysis, Review findings selected on arrival, downloads hidden during review and visible in the final step. Existing regression suite: 107 passing tests. Analysis remains local/free and uploaded code is not executed.


## Non-technical reviewed example application walkthrough - build 0.11.1 (2026-10-17)

Walked Start to Save with the original reviewed example application Build 1.zip and the handover goal. The previous first result overwhelmed an owner with a large App.tsx reference list and hundreds of links. Review now leads with a bounded, evidence-linked plain-language profile, explicit uncertainty about whether the software works, and a clear recommendation to save a readable report for a developer. Detailed findings and inventory counts remain available behind expandable sections. The profile describes technology clues, not a recovered business specification.

Choose ZIP now explains compressed packages, source-code preference and local-only inspection; Analyze stays disabled until a non-empty file within 64 MiB is selected. Selected filename/size are displayed, and the report retains an escaped filename and selected goal. Back navigation retains the chosen goal. The final screen prioritizes Save readable report (HTML), labels technical JSON as optional, and assigns three actions to owner/developer with explicit done-when criteria. No checklist state is presented as runtime verification.

Browser verified the real ZIP selection (Build 1.zip, 3.1 MiB), Review default, hidden downloads before Save, evidence navigation to finding 271, and final owner/developer action list. Existing analysis remains local; no reviewed example application code was run and no AI evidence was shared during this usability walkthrough.


## Free public sample demo (2026-10-17)

Added a Static web hosting landing page and interactive report generated only from five fictional community-library files. Visitors can explore owner findings, inspect evidence, follow the Add book screen/callback/API/database path and save sample HTML/JSON without installing Reversium. This is a sample-only static demonstration, not online analysis of visitor ZIPs. No upload endpoint, AI sign-in, assistant request script, analytics or third-party assets are included. The local Python application is still required for analysing real packages.

The existing public repository Pages configuration already publishes the root of codex/initial-workbench. scripts/build_demo.py rebuilds index.html and demo/report.html; .nojekyll preserves the static output. Private reviewed example application archives, reports, tokens and test data are excluded. Browser verified the local landing-to-report navigation and the complete supported fictional feature path before publication.


## Use Reversium without installing it

You can open the browser edition, choose a question and select your own ZIP. Your computer reads it and produces the familiar findings, feature connections, evidence and gaps. It does not upload your ZIP. repository hosting supplies the app files and sees normal website connection information. Clear or close the page when finished; saved reports remain your responsibility. The browser edition has no ChatGPT connection and no sign-in. Larger ZIPs above 32 MiB need the local application. reviewed example application produced the same file and finding counts in browser and local analysis. This helps investigate a handover; it does not prove that the software works.

Public verification completed at ../web/ on 17 October 2026: reviewed example application produced 266 files and 3,882 findings. Architecture workflow selection, evidence navigation, JSON and HTML downloads succeeded on Static web hosting. All 111 automated tests passed. Private reviewed example application files/reports were excluded from the published repository.


## Branding and clearer navigation — 0.12.1

Reversium now welcomes you with the 3Sci logo and a Start exploring button. Choose your question, then your source-code package. In Architecture, use Show graphical feature map or Show file relationships. The optional AI assistant is in the local application; the browser version explains this under Where is AI? Files still stay on your device.


## Report navigation and AI handoff — 0.13.0

The report now takes the place of the Start screen after analysis. Inventory numbers remain visible. Use Architecture and Coverage buttons to change subsections without scrolling past other sections. Branding and build number travel with saved reports. AI · choose provider lets you choose ChatGPT, Claude, Gemini or another AI, select up to 20 findings and review/download a request. You must paste and submit it yourself; nothing is automatically shared. This is not a live AI connection. The existing account connection remains in the local app.

Verified with reviewed example application in the browser: redundant outer header hidden, inventory visible, Architecture catalogue/import views and Coverage readiness switching passed. AI evidence preview, provider selection and request download passed without submitting to a provider. 111 tests passed.


## Detailed Help — 0.13.1

Choose Help on Start or inside any report for the full user guide. Expand a chapter or download the PDF without sharing your ZIP. The Online and local editions chapter explains how each version runs, its size limit and the different AI options. A short comparison also appears in AI, so opening a provider website is not mistaken for connecting an account.

Help verification: edition-comparison chapter opens and PDF download succeeds in the browser. The eight-page PDF was rendered and visually reviewed. Updated LinkedIn draft is saved in docs/LinkedIn-post.txt.

Help placement: Help, FAQ and About are now prominent buttons on the public landing and welcome splash, as well as the subsequent Start/ZIP screens and report tabs. First-page buttons open the relevant built-in panel.

PDF reliability fix: only sandboxed about:srcdoc reports forward downloads to the host; other embedded/browser pages download directly. Download anchors are attached for activation and URLs live for 60 seconds. Help also provides an ordinary direct public PDF link. Online ChatGPT account inference remains externally gated: official OpenAI documentation directs remotely hosted applications to the interest process; no hosted account connection or subscription access is claimed.


## Online account integration preparation

The online AI tab now shows the planned account connection and answer area, clearly marked as awaiting approval. You can prepare and review selected evidence, but cannot connect or send yet. The existing manual handoff remains usable. Once an approved connection is implemented and tested, answers can appear here without exporting a request. This preparation does not enable ChatGPT subscription access.

Browser verification with fictional source confirmed pending-approval status, disabled connect/send, exact selected-evidence preview, approval reset after edits and working manual fallback. Eight fake-adapter tests pass without network calls. The regression suite hit an intermittent Windows loopback reset; the affected HTTP test file passed when run separately. No hosted account sign-in or inference was performed.


## reviewed example application check and local reliability fix — 18 October 2026

We tested the prepared online AI controls using the real reviewed example application ZIP. The browser found the expected 266 files and 3,882 findings. We selected three chat-related clues and confirmed that the review contained only the question and those selected clues. Editing the request removed the approval tick. Connection and Send stayed unavailable while approval is pending. The manual option still prepared the same selected clues, and Clear removed the file selection and displayed report. Nothing was submitted to ChatGPT.

We also reproduced and fixed a local-server connection problem on Windows: the connection could close while a larger report was still being read. Successful responses now reuse a correctly sized HTTP connection; errors close it deliberately. Six complete test runs finished without the reset, including a new check that transfers several large responses over one connection. One optional identity-signature check was skipped because its extra libraries are not installed. The eight simulated AI lifecycle checks also pass. Live ChatGPT access remains disabled and still needs approval plus provider-specific integration and verification.


## A clearer purpose and two practical tools — 0.14.0

Reversium is aimed at the moment you inherit a software package and need a trustworthy starting point. It is not competing to be the deepest security scanner or a complete architecture-recovery tool. The public comparison explains where CodeBoarding, SonarQube, CodeQL and Joern are useful and why Reversium focuses on private, no-install handover discovery. The combination is distinctive; individual features such as diagrams or local analysis are not exclusive to Reversium.

Use the new Handover tab to see setup clues with evidence: configuration variable names, available script names and declared runtime constraints. Secret values and command bodies are not included by this reader. Names do not prove a setting is required or a script is safe. Assign owners, record what was checked and save the checklist as JSON or readable notes. Your notes stay in this page until you save them; they are not automatically sent to AI. Ordinary HTML/JSON analysis exports do not preserve the review notes. Saved checklist import is not available yet.

Use Change impact to choose a file and inspect nearby upstream/downstream references. It can help decide what to read or test before changing code. It does not predict every broken feature. Source links, candidate labels and limits remain visible. The first reviewed example application test used an overly broad evidence-based starting point; explicit file metadata now gives a tighter view, including 13 nearby candidates for its chat screen.

The same reviewed example application archive still has 266 files. It now produces 4,004 findings because 122 setup clues have been added, grouped into 88 setup entries. Both handover downloads and impact evidence navigation were checked in the browser. The updated user guide has nine chapters. All core features remain free and local with no added service subscription or model requirement. Hosted ChatGPT access stays disabled while approval is pending.


## Resume a review and compare deliveries — build 0.15.0

You can now save a handover checklist, return to the same ZIP later, and restore your owners, statuses and notes. Open Handover, choose the saved checklist, review its preview and press Replace. New saves check the exact ZIP fingerprint first. A different or repacked ZIP will not match. Older checklists only carry a package name: the warning asks you to confirm the delivery yourself before replacing notes. Save before closing; nothing is stored automatically. A reviewer marking something verified is still a human annotation, not an automated test result.

Open Compare reports and choose an earlier report JSON to see which files or recorded clues differ. Files that were not hashed are clearly marked unverified. Save comparison notes to keep the displayed results; long lists disclose omitted entries. Comparing does not erase your handover work. Neither your ZIP, report nor checklist is uploaded or sent to AI.

We tested this with reviewed example application. A matching checklist restored and a wrong fingerprint was rejected. Its older report showed 115 extra clues under the newer reader, without changed shared file hashes. That does not mean reviewed example application gained 115 features: improved analysis can find more in the same files. Comparing the current report with itself found no changes. Some files still lack content hashes, and this browser view does not compare graph connections or prove what works at runtime. ChatGPT account access remains disabled until approved.


## See which software connections changed — build 0.16.0

Compare reports now includes feature-map changes. After analyzing your current ZIP, choose an earlier report in Compare reports. You can see which recorded features, code blocks and relationships were added, removed or changed. Each relationship card shows what was recorded earlier, what is recorded now, a small diagram and the source references. Current references open the current evidence; earlier locations belong to the earlier saved report.

The useful question is: “What should my developer check after this change?” Directly recorded feature names appear first. Broader candidate connections can be expanded separately: shared code or table names can connect otherwise unrelated features. These are leads for investigation, not a list of things that definitely broke. Missing maps, uninspected behavior and truncated searches stay clearly marked. Save comparison notes if you want to keep the displayed review.

We tested with reviewed example application. Comparing identical reports found no map changes. In a disposable test copy we renamed one table reference, without touching the original or live platform. The comparison identified a changed data-read connection and pointed directly to the chat API and AskHerzlChat screen for investigation. We also tested a clearly labelled confidence-only change. Neither result proves that a user-facing feature failed or that the database changed: a developer still needs to inspect the source and test the workflow separately.

This remains free and local. Your ZIP and reports are not uploaded, and no AI connection is needed. The guide explains the limits and how to read the comparison. ChatGPT access is still disabled pending approval.


## Traffic-light file alerts — build 0.17.0

There is now a File alerts tab and a shortcut showing the counts above the inventory. Green means the supported checks found no warning signs; it never means guaranteed safe. Yellow means possible damage, an executable/script that needs review, or something Reversium could not inspect fully. Red means a potentially dangerous pattern or misleading filename worth investigating; it is not a declaration that a file is malware.

Click a color to filter the list, or choose Possible damage / invalid format. Each alert explains its reason and links to evidence. The integrity summary tells you how many ZIP members passed CRC, failed, or were not checked. CRC catches some accidental damage; a malicious file can still have a valid CRC. Unsupported, encrypted, nested and oversized files leave gaps, and suspicious code examples can cause alerts.

reviewed example application's 266 members passed the bounded CRC read. Its results were zero red, 144 yellow and 122 green. Most yellow results concern inspection limits or active formats; these are not 144 corrupted files. We separately tested an intentionally damaged file and a suspicious-looking executable name in an inert sample ZIP, and confirmed that alerts and evidence navigation work without running anything. No file is sent to an external scanning service, deleted or quarantined. These checks do not replace antivirus or a developer's security review.

A sandbox to try the software is possible, but it needs a local companion and a disposable virtual machine; the online Static web hosting edition cannot supply arbitrary native execution. We documented an offline-first design with no live credentials, restricted sharing, reviewed setup commands and a stop control. Windows Sandbox needs a supported Windows edition and hardware; a Linux VM is another route. Offline mode may prevent dependency installation or external services from working. This run feature is not built yet, and no isolation system guarantees zero risk. Traffic lights never grant permission to execute a ZIP.


## Readable handover and a practical setup plan — build 0.18.0

The handover cards now have a white background, dark text and readable fields. We checked this using reviewed example application in the browser. A new Setup & readiness tab organizes eight questions: runtime versions, dependency lockfiles, example configuration, database migrations/data, build/start/test clues, deployment files, backup/recovery and monitoring. Expand a group to see matching filenames, then save the setup review plan for your developer. A file being present does not mean it works; missing filename clues do not prove that a capability is absent.

The market comparison now makes our gaps explicit. Tools such as CodeBoarding offer deeper architecture/repository workflows; SonarQube and Semgrep offer established code/security checks; OSV-Scanner provides vulnerability matching; Syft produces standard software bills of materials. Reversium does not yet provide equivalent depth, complete dependency/license inventories or verified runtime execution. Sensible free next steps are local scanner-result import, offline vulnerability data, standard inventory formats and more tracing fixtures. These are future options, not features quietly switched on.

We have built the first sandbox preparation step, not a running sandbox. The local application can check prerequisites and write offline starter profiles. Nothing is launched and no ZIP is placed inside them. This computer has Windows Home, so Windows Sandbox is not available; QEMU is also absent, and Docker's engine was unavailable. WSL is not being used as the safety boundary. A free Linux guest running under QEMU is the next route to investigate without paying for a Windows upgrade or cloud service. It still needs a trusted guest image, tested isolation, a stop/timeout mechanism and reviewed dependencies before trying reviewed example application.

reviewed example application's new readiness plan and download were checked in the browser. The local prerequisite button correctly reports missing backends, while the online edition explains that it cannot inspect host programs. Files remain local and no AI is required. No software from the ZIP was executed during this stage.


## Trying reviewed example application inside a disposable Linux computer — build 0.19.0

We now have an experimental free local sandbox for the reviewed reviewed example application package. Think of it as a temporary Linux computer inside your Windows computer. We obtained QEMU and Alpine Linux from official or officially referred sources and checked their published file checksums. No Windows upgrade, paid cloud machine or change to Windows features was needed. This is currently a developer command-line feature; the online site still analyzes ZIPs without running them.

Before introducing reviewed example application, we ran 14 checks on an empty guest. They confirmed the selected setup had no external network connection or shared host folders, could read but not change its input files, could not contact our host test service, lost its temporary marker when replaced with a fresh guest, and stopped when its deadline expired. All passed, including with the faster hardware acceleration already available here. These checks reduce specific risks; they cannot promise that a virtual machine has no security weaknesses.

We then used a separate guest to install verified public libraries offline and build reviewed example application. Its frontend and backend compiled successfully. The production server started and its home page returned a successful HTTP response inside the guest. We used fake keys and reserved invalid service addresses, with no live account or database connection. reviewed example application's own production configuration checks remained in place. The guest was stopped afterward and its input image was unchanged.

That is useful evidence that this delivery can build and start on Linux. It does not yet prove that users can sign in, save data, upload media or publish a tour. Those need disposable database, account and storage services, followed by a proper user-journey test. We deliberately have not exposed the guest website in your browser or connected it to live reviewed example application.

The local setup commands are in Help and README. They download public packages, not upload your ZIP. Common environment and key files are omitted from the guest copy, but this cannot guarantee that code contains no embedded secrets. Private input copies and logs remain in the ignored reports/qemu-lab folder after the temporary computer stops; do not share or commit them. The original ZIP and live platform were untouched. Reversium remains free and local, and ChatGPT access remains disabled while approval is pending.


## A maintained guide and a clearer purpose — build 0.20.0

Help now contains a searchable guide with thirteen chapters, available before you upload anything and again in your report. Type a word such as handover, evidence, AI or sandbox to open the relevant chapters. Clear the search to see the whole guide. You can keep a PDF copy, and its build number tells you which version it describes. The release process now checks that the website, built-in guide and downloadable PDF agree; the developer must also update the instructions when features change.

We simplified the product attribution and removed repository links from the interface and documentation. Product-document links stay within the site. Existing legal notices and licence terms remain intact; this is a presentation change, not a change to hosting or account access. The PDF's direct link also works in the local application.

There may be a business here, especially when an agency inherits a project or an owner changes developers. The useful outcome is a clearer handover: what the files show, how supported features connect and which questions a developer must verify. Other tools already sell architecture and quality checks, so diagrams alone do not make Reversium unique. We have not yet proved that customers will pay. The commercial assessment proposes five real handover trials and a small assisted-review service before adding subscription or billing features. Analysis stays free and local.

Our pitch is: taking over software should not start with guesswork. Reversium turns an unfamiliar package into an evidence-backed handover and a practical plan for the next developer, while keeping the ZIP on your device. AI can help explain code and use tools too; Reversium's proposed value is a repeatable process with evidence, comparisons and visible gaps.

Next we plan to connect a developer-reviewed test outcome to the exact ZIP it tested, then work toward a complete isolated user journey with disposable supporting services. These are next steps, not completed features. The current sandbox still proves only the narrow reviewed example application build/start experiment; hosted ChatGPT remains disabled pending approval.


## Connect a real test to the right delivery — build 0.21.0

You can now attach a sandbox result to the exact ZIP you analyzed. Open Setup & readiness, choose the local run-evidence.json (or latest-run-evidence.json), review its preview and choose Attach this reviewed test record. A fingerprint mismatch refuses the attachment, even if the filenames are identical. Renaming the same ZIP is fine; changing or repacking it gives a different identity. A bad replacement does not erase the record already attached.

The screen keeps three things distinct: recorded test outcomes, static setup clues found in the files, and what remains unknown. Each outcome says pass, failure or not recorded. It shows both the original ZIP fingerprint and the filtered copy that actually ran, including how many members were omitted. The reviewed example application test used synthetic settings; it was not connected to live accounts or databases. Passing a build or internal page request does not prove that login, storage or publishing a tour works.

We repeated the isolated reviewed example application test and generated a real record. All 14 selected isolation checks and 11 application/cleanup checks passed. We then analyzed the real ZIP in the browser, attached that record, refused a deliberately wrong fingerprint and checked save/remove/restore. A separate controlled failed-build preview clearly showed failure and unrecorded later checks; it was only a test fixture, not a reviewed example application failure. The exported report kept the real attached record and excluded that pending preview.

Save linked test record (JSON) keeps the record for later use; Save readable test summary gives you text notes. Readable report HTML retains an explicitly attached record, while technical report JSON remains the original static analysis. Closing the page does not automatically save your attachment. Existing handover statuses and AI requests are unchanged. The records contain limited metadata and outcomes, not source code, passwords or raw logs.

There is a trust limit: someone can edit a JSON record. Matching the ZIP identifies the delivery it claims to describe, not who made the record or whether every claim is true. Review the original private logs when needed. We inspected the exported HTML and validated its saved record, but the testing browser blocked opening downloaded local HTML files, so that particular reopening action was not browser-tested. The live browser attachment and saved-JSON restoration were tested.

Help now includes a fourteenth chapter explaining the workflow, its limits and saving choices. Everything remains free and local; no new account or paid service is needed. The browser still does not run the uploaded program. Private sandbox files and live reviewed example application remain separate.


## Build 0.22.0 — a real disposable publishing test

The local sandbox can now create its own temporary database, login service and file store. They run inside the isolated virtual computer, using invented test users and new local credentials. No live reviewed example application database, account or storage is used. There is no internet connection from that virtual computer and no preview port exposed to your computer.

We tested the actual reviewed example application package: it built, started, logged in an editor and a reviewer, rejected a wrong password, checked access restrictions, uploaded an image, approved and published a tour with two stops, then read back the public tour and the exact image. All 14 isolation checks and 26 application checks passed. Cleanup closed the test tenants and suspended the test users; stopping the guest discarded its temporary database and files.

This was an end-to-end API test: the test script performed the requests behind the screens. We have not yet clicked through the CMS publishing screens, tested real emails or external sign-in, live maps or AI, or demonstrated production reliability. A successful test is useful evidence for this particular package and journey, not a promise that every feature works.

After the existing local sandbox preparation, run python scripts/prepare_project_services.py, then python -m reversium --sandbox-project-services "path/to/your-package.zip" --sandbox-accelerator whpx if WHPX is already available. Help explains the prerequisites and slower default emulation option. This profile needs 3 GiB guest memory, local disk space and public dependency downloads, but no paid hosting or API account. It is a reviewed reviewed example application profile, not a general run-any-program feature.

In Setup & readiness, select reports/qemu-lab/latest-run-evidence.json and review it before attaching. Reversium matches the exact original ZIP fingerprint, shows what passed and what remains unknown, and keeps runtime checks separate from file analysis. The result is an editable local record, not an independently signed certificate. Source-bearing input images, caches and logs remain privately on the host after the guest stops; do not distribute them. Help and its downloadable PDF now cover this workflow.


## Build 0.23.0 — testing the actual CMS screens

We can now open a temporary local reviewed example application preview and test its buttons, rather than treating a successful test script as proof that the screens work. A separate editor and reviewer use invented accounts in a new temporary organization. Services and accounts are prepared before the browser journey; that setup is not itself a browser test.

The virtual computer still has no internet/network adapter and no access to host folders. A small private local relay carries browser requests through its supervised serial connection. It opens only on this computer, requires the private entry link, and blocks external browser connections. Maps and other outside services may therefore be unavailable intentionally. This experimental preview is slower than a normal deployment and is not a production or security guarantee.

The first attempt exposed problems with preview setup and response speed. We corrected the transport and repeated the journey in a fresh guest, without editing reviewed example application's application logic or connecting to live. The detailed CMS test report records the visible successes and any remaining blockers, separately from the previous API results. A machine-created setup record never labels manual publishing as automatically verified.

The command and stopping instructions are in Help: python scripts/test_project_cms.py "path/to/your-package.zip" --accelerator whpx where supported. The preview has a twenty-minute window within a thirty-minute total guest limit. Open /__reversium on its own local address to stop it. The guest's database and files are temporary; private files, screenshots and browser session data can remain on the host. Keep the account file and entry link private. No paid service or live credentials are needed.


The actual browser publishing test passed. The editor created a city and two stops, then submitted them. A different reviewer approved and published the city, tour and both stops. The CMS showed one published tour with two stops and nothing left waiting for review. After signing out, we opened the visitor page for that temporary organization and saw the exact tour and both stops in order. This is stronger evidence than seeing preloaded demonstration content.

Two preview limitations were recorded: the serial connection needed performance fixes, and the original Stop form was rejected by its own security check. A direct shutdown call was blocked by automatic approval review, so that route was not used; the test guest was left to its preset deadline. We fixed and browser-tested the form on a separate mock server, with no guest attached. External thumbnails did not load under isolation. We did not test image uploading through the CMS, narration, real maps/GPS, outside sign-in or production reliability. The earlier API image test remains separate evidence.

The original preview stopped automatically at its deadline. We confirmed that the guest and local listener had stopped and that its input image was unchanged. The completed publishing test, remaining gaps and cleanup outcome are now recorded together.


## Build 0.23.1 — what happened when we tested pictures

We used a small invented image, temporary accounts and a separate local copy of reviewed example application. The editor screens required image rights and a public credit. They accepted the picture and confirmed that the tour containing it had been submitted for review.

The reviewer then saw an empty queue in the same organization. That is a real blocker: we could not approve or publish the picture through the screens. We have not yet proved that a visitor can see this picture or its credit. Earlier tests that sent requests directly do not replace this missing screen test.

We improved the local connection so image bytes arrive in checked pieces. Selecting the file through browser automation was still intermittently very slow. These problems and the successful steps are recorded in the photograph test report. Help and its PDF explain how to repeat the test and distinguish upload from publication.

The protected Stop button shut down the temporary guest. Its input stayed unchanged and the isolation checks passed afterward. No live accounts, paid service or outside connection were used. Private test files and screenshots stay out of the published site. Next we need to find why the reviewer cannot see the submitted work, then repeat approval and visitor checks using normal authorized accounts.


## Build 0.24.0 - guidance for your code package (19 October 2026)

The guide now speaks about your ZIP or code package, rather than a particular test customer's application. Historical examples are anonymous and still say what passed and what failed. The pitch includes a common situation: you built with one AI coding tool, such as Claude, and the next developer uses another, such as Codex. Reversium helps pass the code, explanations and unanswered questions; it does not move chats or accounts.

Help explains that ordinary analysis reads files. The experimental local sandbox runs real code in a disposable virtual computer, but only with a fixed reviewed example profile. It is not a simulator or a button that can run any uploaded ZIP. A developer needs to prepare and review other applications. It can work alongside your editor, repository, backend or hosting tools through files and reports; it does not connect or deploy to them automatically.

A new feature-list PDF explains what each function does, where it is available and its limits. Seven graphical journeys show practical routes through the product. Both PDFs and the diagrams are available in Help, including before you analyze a package. Their build number is checked with each release. When a feature changes we must update the shared catalog and rebuild, so the documents continue to describe the product honestly.

The market assessment identifies a possible business in helping agencies and developers take over unfamiliar projects. That is an opportunity to test with real paid handovers, not proven demand or revenue. The authorized reverse-engineering wording has legal sources and clearly leaves rights, restrictions and local law to each actual use.

Final verification: 152 Python tests passed with one optional-dependency skip; 30 JavaScript tests passed. The documentation release gate passed. All four feature-list pages, seven journey pages and seventeen guide pages were rendered and visually checked. Both new PDF buttons downloaded files matching their generated build; Help showed seven journeys and 28 steps before analysis and after opening a sample report. A generic article-style contrast conflict was found and fixed. Browser download automation stalled for an extended period despite producing the files; that tool delay is not an application performance benchmark. No guest or live service was run for this documentation release.


## Build 0.24.1 - checking the buttons properly

We checked the main Start controls and used a fictional package to test the analysis flow. The updated Help, chapters, diagrams and three PDF downloads worked when served from the exact browser build on this computer. The PDF contents matched the release files. Report navigation, subsection buttons, filters and exports also worked in the tested sample.

One real problem appeared: an evidence link inside the feature map sent the report back to Start. We fixed how newly created links are handled and added a regression check. Build 0.24.1 includes that correction.

The online site still showed the older 0.23.1 build during these checks. Its two new PDF links returned not found because publication had not finished. A free publication retry was requested, but the jobs remained queued. A successful local test is not a successful online release; do not announce the new build as live until its version and PDF files are checked there.

Final local follow-up verification: the actual dynamically rendered map link opened Evidence and finding-19 without navigating the iframe. All three 0.24.1 report PDF downloads matched the generated files byte-for-byte. HTML/JSON/SVG export and reviewed AI request download worked; no AI provider was contacted, and account connection remained intentionally disabled. The report Clear control returned to Start. Python: 152 tests with one optional-dependency skip. JavaScript: 34 tests passed. Documentation release checks passed. Publication remains separately subject to the hosting queue.
