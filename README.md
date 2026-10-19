# Reversium by 3Sci Labs

Understand. Prepare. Develop.

[Use Reversium in your browser](web/) to analyze your own ZIP locally, free and without installation or an account. The app does not upload or execute the package. The first visit downloads about 14 MB of application/runtime assets. Browser compressed ZIP limit: 32 MiB. [Explore sample data](demo/report.html).

## What it is for

Understand a delivery, prepare a developer handover or investigate maintenance. A prototype developed with Claude can be handed to someone working in Codex with its original code, a readable evidence-backed report and a practical checklist. This is a manual handover, not chat, account or agent-memory migration.

Reversium inventories a package, extracts supported source/binary clues, draws feature and file relationships, records evidence and unknowns, and compares deliveries. It helps you choose what to inspect and verify. It cannot tell you exactly everything a program does or certify it safe or production-ready.

## Documentation

- [Complete Help](docs/user-guide.html), available on Start and report screens.
- [Feature list PDF](output/pdf/Reversium-Feature-List.pdf): current functions, edition availability and limits.
- [Seven graphical user journeys](docs/user-journeys.html) and [journey PDF](output/pdf/Reversium-User-Journeys.pdf).
- [Purpose, sandbox, tool compatibility and lawful-use sources](docs/PRODUCT_GUIDANCE.md).
- [Commercial assessment and competitors](docs/market-position.html).
- [Running development stages](docs/DEVELOPMENT_STAGES.md) and [plain-language progress](docs/PLAIN_LANGUAGE.md).

The feature list and journey assets are generated from docs/product-catalog.json whenever Help is rebuilt. Update that catalog when capabilities change. The release gate checks build identity and generated artifact hashes; it does not replace editorial verification.

## Local application

The base analyzer requires Python 3.10+ and no third-party Python packages:

```sh
python -m reversium
```

Open the printed local address. The default is port 8765 with a free-port fallback; --port 0 requests a free port explicitly. Stop with Ctrl+C. On Windows, Start-Reversium.ps1 is an alternative launcher. Restart an existing server to load a new build. Local web ZIP limit: 64 MiB; normal archive/inspection bounds still apply.

```sh
python -m reversium your-package.zip --output reports/your-package
python -m reversium your-package.zip --output reports/review --compare reports/earlier/report.json
```

CLI output includes report.html, report.json and feature-map.svg, overwriting those names in the selected directory. Save checklist notes separately; ordinary report JSON is static analysis only. Exports can contain private code-derived details.

## Useful capabilities and boundaries

Selected Python, JavaScript/TypeScript, React and Supabase references support feature candidates, workflows and graphical maps. Solid traced references and dashed inferences stay distinct. Coverage discloses unresolved and omitted material. Views and readers are bounded; dynamic code and unsupported patterns can be missed.

File alerts flag selected integrity, disguise and suspicious-pattern signals. Green is not guaranteed safe. These checks are not antivirus or a complete vulnerability audit. Binary inspection is metadata/reference analysis, not full decompilation.

Use the report alongside Visual Studio, VS Code, repository hosting including GitHub, Supabase, Docker, Railway and other development tools. These are manual file/report workflows; no native account, editor, deployment or synchronization connectors are provided.

Online AI is an explicit reviewed text handoff to a selected provider. Embedded online ChatGPT account access remains disabled pending approval. The local optional connection has separate setup and account eligibility; successful sign-in does not guarantee inference availability. AI sharing is never required for local analysis.

## Experimental local sandbox

The browser edition never executes uploaded code. The Windows QEMU pilot runs real code in an offline disposable Linux guest, not a simulation. It supports one fixed developer-reviewed example profile, not arbitrary ZIPs. Another project needs separate reviewed preparation and acceptance checks.

After reviewing compatibility, prerequisites and [Help](docs/user-guide.html), the profile's neutral entry points are scripts/prepare_project_offline.py, scripts/prepare_project_services.py, --sandbox-project, --sandbox-project-services and scripts/test_project_cms.py. They preserve existing profile compatibility; renaming an entry point does not broaden support. Fresh isolation gates, synthetic data, deadlines and no guest NIC/host shares remain in force. Private lab files can remain after shutdown.

[Historical CMS observations](docs/SANDBOX_CMS_TEST.md) and [image test evidence/blockers](docs/CMS_PHOTO_TEST.md) describe a specific anonymized delivery. Image upload passed; the separate reviewer saw an empty queue. Image approval/publication remains unverified. [Sandbox design](docs/SANDBOX_DESIGN.md) describes the execution boundary and limits.

## Release checks

```sh
python -m unittest discover -s tests -v
node --test tests/review-tools.test.mjs tests/online-ai.test.mjs tests/runtime-evidence.test.mjs tests/service-guest.test.mjs tests/cms-transport.test.mjs tests/evidence-links.test.mjs
python scripts/build_help.py
python scripts/build_browser.py
python scripts/build_demo.py
python scripts/check_release_docs.py
```

ReportLab is needed to build documentation PDFs, not for ordinary analysis. Authorized code understanding and reverse-engineering analysis are valid product purposes; rights, licences and jurisdiction still govern each use. Reversium does not grant permission to bypass access controls or publish someone else's code.
