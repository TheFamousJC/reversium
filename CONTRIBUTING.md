# Contributing

Use Python 3.10+. Keep the core dependency-free, local and usable without accounts or AI. Do not execute submitted code. Preserve bounded reads and evidence provenance. New analyzers must disclose language coverage and distinguish observations from heuristics.

Run `python -m unittest discover -s tests -v` before submitting changes. Add meaningful fixtures for analyzer or security behavior. Do not commit private archives or reports. Update both living documents under `docs/` when behavior or stages change.

Record issues with a reproducible fixture and propose changes through the project maintainer. Verify licenses before adding dependencies, rules or model weights.

Release documentation policy: update scripts/build_help.py whenever user-visible behavior changes. Rebuild Help, PDF, browser and demo, run scripts/check_release_docs.py, and verify the changed guide chapters in the browser and PDF before publication. Update both running documents for every release.
