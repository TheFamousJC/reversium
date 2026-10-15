# Reversium, explained without technical background

Living explanation. Last updated: 2026-10-15.

## What it does today

Reversium helps you understand a software package. You give it a ZIP file, and it makes a list of what is inside. For selected kinds of readable code, it identifies named building blocks, references to other software and possible web addresses or application routes.

It presents a report and a diagram. Each finding includes the file and line where it was found, so someone can check the evidence. The diagram connects files to software names they mention. It does not prove that those connections are used when the program runs.

The latest version can also connect some references to other files inside the same ZIP. Each reference is labeled: internal means a matching local file was found; external means a package was declared; unresolved means there is not enough information; ambiguous means more than one file could match. These are clues for review, not proof of what happens when the software runs.

For Python, it recognizes some possible web routes and data-model classes. It also reads common dependency lists for Python, JavaScript and Go. The inventory says which files received deeper inspection and which were only listed.

## How to use it

Install Python 3.10 or newer, open a terminal in the Reversium folder and run `python -m reversium`. A browser page opens. Choose your ZIP and click Analyze archive. To create saved reports directly, run `python -m reversium your-package.zip --output reports/my-project`.

On Windows you can also run `./Start-Reversium.ps1`. In a report, type in Filter evidence to find a file, name or reference type. Download JSON saves structured results for later comparison; Download HTML saves a report you can open in a browser. Both downloads include all findings, even when a filter is active. On a narrow screen, slide the diagram or table sideways to see the remaining columns.

To compare two versions, save the first JSON report, then run `python -m reversium new-package.zip --compare reports/old/report.json --output reports/new`. The new report lists added and removed files and findings. It can identify changed readable files when both versions were inspected. It does not yet compare how programs behave, and comparison currently starts from the terminal.

## What we checked

We tested the source example, both report formats, and desktop-size and narrow phone-size layouts. For binary analysis, we uploaded a second example containing source, settings and synthetic program headers. The browser showed 8 files, 5 binary candidates and 27 findings. It correctly showed one broken file as partial, identified likely supporting services, and filtered the two imported-library findings. Thirty automated checks passed. These tests use examples; they do not promise every software package is fully understood.

## Privacy and cost

The work happens on your computer. There are no subscriptions, accounts or paid AI requests. You still supply the computer, electricity and time. Reports may reveal private file names and software details, so check them before sharing.

## What the report cannot promise

A list of ingredients is not the same as understanding every recipe. Reversium cannot yet explain every business rule, recreate an application automatically or promise a reliable rebuilding price. Some findings are educated pattern matches; the report labels them as such. Missing findings do not prove a feature is absent.

It now inspects some compiled programs without running them. It can recognize formats, show certain operating-system or processor clues, and list some referenced libraries or classes. Findings point to positions inside the file, called byte offsets. A broken file can still provide partial clues, which the report labels. It does not use a decompiler to reconstruct source code.

For Android and Java packages, it can list the inner package directory without opening the contained programs. Large, compressed or unsupported files may still be listed without their contents being inspected. A reader status of “complete” means the supported inspection finished; it does not mean the program is complete, safe or ready to run.

## Can it tell me what the software platform is?

It can identify likely ingredients and broad types. For example, references to FastAPI and Python can suggest a Python web API, while a Windows binary header can identify a Windows target and processor type. It shows the supporting file or byte position for those clues.

It cannot reliably conclude that an unknown package is a complete CRM, accounting system or other specific business product from these clues alone. Understanding the exact purpose, features and completeness still requires reviewing behavior and requirements. When it lacks evidence, it says the purpose is unknown.

## Can it set up and run the ZIP?

Not yet. Reversium currently inspects the package; it does not install dependencies, run installation scripts or start the submitted software. The planned approach is to prepare a setup plan and validate it in a separate disposable virtual computer, with test configuration and data. A package can be missing source files, licenses, private services or credentials, so automatic startup cannot be promised for every ZIP.

## Can it tell me which supporting platforms I need?

It now lists evidence of some supporting services, such as PostgreSQL databases, Redis caches, message brokers and selected external integrations. It reads known client-library names and simple container-image declarations. A reference might belong to a development tool or an optional feature, so the report does not call every service mandatory.

To run a stable version, someone must still confirm service versions and settings, credentials, database setup, resource needs, backups, monitoring and recovery behavior. Reversium shows these as open questions. It does not yet size or test a deployment. Reversium itself remains local and free; services required by the original application may have their own costs or access requirements.

## What comes next

We will expand readable-code and compiled-program analysis, then add optional local decompilers for deeper inspection. Later, optional local AI can help draft explanations, and adjustable planning tools can estimate rebuilding work and running costs. Those estimates will show the assumptions behind them. Isolated setup and startup checks remain a separate future stage.

## Keeping this explanation current

Whenever a feature becomes available, update what the tool does today and remove any promise it still cannot meet. Keep planned capabilities separate from working capabilities.
