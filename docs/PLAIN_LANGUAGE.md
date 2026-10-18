# Reversium, explained without technical background

Living explanation. Last updated: 2026-10-16.

## Optional help inside Reversium — version 0.10.0

The new AI assistant sits in the same report interface. A three-step wizard helps you connect your own eligible ChatGPT account, choose findings and review exactly what you would share before sending a question. Answers appear beside your report, with links back to selected evidence and a separate list of unknowns. A FAQ explains privacy, setup, limits and troubleshooting.

The local analyzer stays free and works without an account or internet. AI is optional and uses your account's eligibility and plan limits. OpenAI sign-in briefly uses a provider screen; Reversium never asks for your ChatGPT password or a paid API key. Your ZIP is not automatically uploaded. Finding descriptions and file paths may still be private, so inspect and edit the preview. Redaction can miss secrets.

Connecting alone shares no software evidence. Each Send requires fresh approval; the assistant cannot install software, execute commands or edit files. Its citations only establish which selected finding it references, not that the explanation is true. Local tools and actual tests remain the way to confirm behavior.

Tokens remain in memory and disappear on disconnect or restart. Local registration identifiers are retained to reconnect the same account. Saved report exports exclude assistant conversation and account details. Disconnecting locally does not revoke OpenAI-side authorization; use ChatGPT settings for that.

The interface and safety checks have been tested locally. A real account sign-in and cloud answer still need user acceptance. We have not sent Tudela's private source findings to the provider. The earlier local Tudela rehearsal did verify administrator provisioning, draft import and a published five-stop tour in a separate local database; its private handover report retains the results and remaining gaps.

## Following more Tudela workflows in version 0.8.0

The map can now follow selected actions passed between React screens. For example, the chat screen's send action connects to the callback supplied by the main app, then to the `/api/chat` request and supported backend/data references. A CMS save action can connect to a callback returned by its content-management helper and then to the database code. Click a box or line to inspect the source evidence.

It also follows some addresses built from local constants or passed into request helpers. The staff screen's helper calls fetch with a variable URL; the report can now show which caller supplied the staff endpoint and which HTTP method it requested. Evidence includes both the caller and the helper. Different callers are kept separate so a read action is not accidentally described as a write action.

On your original ZIP, the report shows 172 possible prop bindings and 52 resolved API-target contexts. A context is one caller/path/method combination; it is not a unique service or a verified working feature. The number of source files and starting points is unchanged: 115 JS/TS files, 25 route references and 32 React/JSX modules. We checked the chat and staff maps in the browser, followed the chat prop link to its exact source line, inspected both staff caller/helper locations, and passed 96 automated checks.

A passed action can still have several possible providers, and the program might choose among them while running. Reversium displays those possibilities rather than choosing one. State-setting callbacks, more complex property forwarding and addresses controlled by environment settings can remain unknown. A recognized API path also does not prove the same server will handle it after deployment. None of Tudela's code or requests are run by the analysis.

Large maps can exceed display or tracing limits. The App and CMS views disclose these; a smaller selected workflow is easier to inspect. JSON keeps the generated reference data. Reversium remains local and free, without an AI service, account, Node installation or API key. Your ZIP and private report are not published with Reversium's code.

## What changed after testing your Tudela ZIP

Version 0.7.0 maps much more of Tudela than the first report. It reads all 115 JavaScript/TypeScript files in that ZIP, including 32 files containing React screen/component code. It recognizes 25 web-route references, rather than drawing only the narration endpoint. The map offers 57 starting points: those routes and React modules. These are starting points for investigation, not 57 proven business features.

For example, selecting TourCommunityPanel shows references from the community screen to helpers for comments and likes, then to named Supabase database routines. The map can also connect those routine names to table operations written in database migration files. Click a box or line to see its evidence and the source file/line. Old migration definitions can appear alongside newer ones; Reversium does not know which versions were applied to your real database.

Select a feature to rebuild its focused map. This brings in connections that were outside the overview's display limit. The view reports any omitted boxes/lines. Solid lines mean source references were recognized; dashed lines mean a possible connection based on a data name or route path. Neither means that the action succeeded or is available to a visitor.

At the v0.7.0 stage, screen-to-screen callbacks and constructed addresses were major gaps. Version 0.8.0 adds the selected patterns described above. More complex forwarding, state changes and dynamic table names remain unknown; reading every code file is still different from proving every workflow.

Everything stays local and free. Reversium does not start Tudela, contact Supabase or Google, install Tudela's dependencies, or send your archive to an AI service. Your analyzed software may still need paid services when you run it independently. We tested the real ZIP in the browser, checked a focused community map and its database evidence links, and passed 72 automated checks.

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


## Free public sample demo (2026-10-17)

Added a GitHub Pages landing page and interactive report generated only from five fictional community-library files. Visitors can explore owner findings, inspect evidence, follow the Add book screen/callback/API/database path and save sample HTML/JSON without installing Reversium. This is a sample-only static demonstration, not online analysis of visitor ZIPs. No upload endpoint, AI sign-in, assistant request script, analytics or third-party assets are included. The local Python application is still required for analysing real packages.

The existing public repository Pages configuration already publishes the root of codex/initial-workbench. scripts/build_demo.py rebuilds index.html and demo/report.html; .nojekyll preserves the static output. Private Tudela archives, reports, tokens and test data are excluded. Browser verified the local landing-to-report navigation and the complete supported fictional feature path before publication.


## Use Reversium without installing it

You can open the browser edition, choose a question and select your own ZIP. Your computer reads it and produces the familiar findings, feature connections, evidence and gaps. It does not upload your ZIP. GitHub supplies the app files and sees normal website connection information. Clear or close the page when finished; saved reports remain your responsibility. The browser edition has no ChatGPT connection and no sign-in. Larger ZIPs above 32 MiB need the local application. Tudela produced the same file and finding counts in browser and local analysis. This helps investigate a handover; it does not prove that the software works.

Public verification completed at https://thefamousjc.github.io/reversium/web/ on 17 October 2026: Tudela produced 266 files and 3,882 findings. Architecture workflow selection, evidence navigation, JSON and HTML downloads succeeded on GitHub Pages. All 111 automated tests passed. Private Tudela files/reports were excluded from the published repository.


## Branding and clearer navigation — 0.12.1

Reversium now welcomes you with the 3Sci logo and a Start exploring button. Choose your question, then your source-code package. In Architecture, use Show graphical feature map or Show file relationships. The optional AI assistant is in the local application; the browser version explains this under Where is AI? Files still stay on your device.


## Report navigation and AI handoff — 0.13.0

The report now takes the place of the Start screen after analysis. Inventory numbers remain visible. Use Architecture and Coverage buttons to change subsections without scrolling past other sections. Branding and build number travel with saved reports. AI · choose provider lets you choose ChatGPT, Claude, Gemini or another AI, select up to 20 findings and review/download a request. You must paste and submit it yourself; nothing is automatically shared. This is not a live AI connection. The existing account connection remains in the local app.

Verified with Tudela in the browser: redundant outer header hidden, inventory visible, Architecture catalogue/import views and Coverage readiness switching passed. AI evidence preview, provider selection and request download passed without submitting to a provider. 111 tests passed.


## Detailed Help — 0.13.1

Choose Help on Start or inside any report for the full user guide. Expand a chapter or download the PDF without sharing your ZIP. The Online and local editions chapter explains how each version runs, its size limit and the different AI options. A short comparison also appears in AI, so opening a provider website is not mistaken for connecting an account.

Help verification: edition-comparison chapter opens and PDF download succeeds in the browser. The eight-page PDF was rendered and visually reviewed. Updated LinkedIn draft is saved in docs/LinkedIn-post.txt.

Help placement: Help, FAQ and About are now prominent buttons on the public landing and welcome splash, as well as the subsequent Start/ZIP screens and report tabs. First-page buttons open the relevant built-in panel.

PDF reliability fix: only sandboxed about:srcdoc reports forward downloads to the host; other embedded/browser pages download directly. Download anchors are attached for activation and URLs live for 60 seconds. Help also provides an ordinary direct public PDF link. Online ChatGPT account inference remains externally gated: official OpenAI documentation directs remotely hosted applications to the interest process; no hosted account connection or subscription access is claimed.


## Online account integration preparation

The online AI tab now shows the planned account connection and answer area, clearly marked as awaiting approval. You can prepare and review selected evidence, but cannot connect or send yet. The existing manual handoff remains usable. Once an approved connection is implemented and tested, answers can appear here without exporting a request. This preparation does not enable ChatGPT subscription access.

Browser verification with fictional source confirmed pending-approval status, disabled connect/send, exact selected-evidence preview, approval reset after edits and working manual fallback. Eight fake-adapter tests pass without network calls. The regression suite hit an intermittent Windows loopback reset; the affected HTTP test file passed when run separately. No hosted account sign-in or inference was performed.
