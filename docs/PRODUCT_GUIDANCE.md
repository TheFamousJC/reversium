# Reversium: purpose, lawful use and commercial outlook

Reviewed 19 October 2026 / Build 0.24.0. Product assessment based on the implementation and linked primary sources. No customer study, competitor benchmark, legal opinion or revenue forecast is claimed.

## A useful description

Reversium helps owners and developers understand and hand over an unfamiliar code package. It organizes supported code clues, relationship diagrams, setup questions and evidence into a reviewable report. For example, a project begun with Claude can be handed to a developer working in Codex with its original authorized code package, report and saved checklist. This does not migrate tool sessions, conversations, hidden prompts, agent memory or secrets.

## May we say reverse engineering?

A defensible description is: **Reversium supports authorized code understanding and reverse-engineering analysis of code structures and relationships.** That describes a legitimate purpose, not blanket legal permission or full binary reconstruction. The product does not fully decompile programs or bypass access controls.

Whether a particular use is lawful depends on rights, licence terms, confidentiality, personal data, purpose and jurisdiction. Use code you own or are authorized to inspect; sharing findings can need separate permission. In the US, section 1201 includes anti-circumvention restrictions and a limited interoperability exception, not a universal right to reverse engineer. In the UK, lawful observation/study/testing and conditional decompilation are distinct exceptions. Some restrictions may be unenforceable where mandatory exceptions apply; a general product description cannot decide a specific case. For restricted third-party work, obtain advice in the relevant jurisdiction.

Sources: [US 17 USC 1201, especially (a) and (f)](https://www.law.cornell.edu/uscode/text/17/1201), [UK section 50BA](https://www.legislation.gov.uk/ukpga/1988/48/section/50BA), [UK section 50B](https://www.legislation.gov.uk/ukpga/1988/48/section/50B), [EU software directive, Articles 5 and 6](https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX%3A32009L0024). These are examples, not a worldwide survey.

## Does the sandbox run or simulate the code?

It runs real build/start/test commands in a disposable local QEMU Linux guest. It is for testing observed behavior without using live accounts or production data. It does not simulate success. Browser analysis only reads files and never executes your code package.

Current scope is one fixed developer-reviewed example profile on Windows, with fresh isolation checks, synthetic settings and optional real disposable database/login/storage services. It is not an automatic runner for arbitrary ZIPs. Other projects need separate reviewed preparation and acceptance checks; unsupported packages may fail. A guarded loopback serial preview supports selected browser observations without giving the guest a NIC or host shares. Some services cannot work offline. Isolation and a successful journey are not security or production-readiness certification.

Record exact delivery identity, outcomes and blockers. Previous API and text-content browser checks passed for the example package; the later image upload passed but the reviewer saw an empty queue, leaving photo approval/public display unverified. Stopping discards guest RAM, but private host images, logs, caches and browser sessions can remain.

## Use alongside existing tools

| Tool or service | Practical use now | What is not implemented |
| --- | --- | --- |
| Visual Studio, VS Code or another editor | Use report file/line references to inspect the original source in your editor | Native extension, live editing, debugger or synchronization |
| GitHub or another repository host | Export an authorized source ZIP; save report JSON; compare later deliveries | Account connection, branch watching, pull-request automation or project pushing |
| Supabase | Inspect selected table/RPC/Auth/storage references and SQL clues | Live project login, permission validation, migration application or health checks in ordinary analysis |
| Docker | Review supported deployment/container filename clues with a developer | Automatic container execution; Docker is not this sandbox boundary |
| Railway or another host | Use setup questions and reports to prepare a separate deployment review | Hosting account connection, deployment, bill calculation or uptime assurance |
| Claude, Codex or another AI coding tool | Share an explicitly reviewed handover/report subset with the next developer or assistant | Automatic conversation, memory, prompt or credential migration |

These are file/report workflows, not native connectors. Reversium's core analysis is free; separate provider subscriptions, hosting and hardware follow their own terms and costs.

## Is it commercially viable?

There is a plausible niche, not proven product demand. The strongest initial buyer is an agency or maintainer taking over a small unfamiliar project, especially after an AI-assisted prototype or a change of developer. The paid outcome would be a faster, reliable handover decision and verified setup plan, not simply a diagram.

[CodeBoarding](https://codeboarding.org/pricing) sells architecture/change visualization and editor/CI workflows. [SonarQube](https://www.sonarsource.com/plans-and-pricing/) sells quality/security tooling. [CodeScene](https://codescene.com/pricing) sells code health, technical-debt and team workflows. Those offerings demonstrate an adjacent commercial category, not willingness to pay for Reversium. Competitors already combine deterministic analysis, diagrams and AI; privacy and evidence should not be advertised as unique without a measured comparison.

Reversium's proposed position is a free, device-local, package-first handover workflow readable by owners and developers, with explicit gaps and comparisons. Current weaknesses include limited semantic coverage, no native editor/repository/deployment connectors, no general sandbox, an unresolved reviewer-queue pilot blocker, and no measured accuracy, repeatability or customer ROI benchmark. Free alternatives and AI coding agents are strong substitutes. Zero hosting budget does not mean zero engineering, support, legal or maintenance cost.

Keep the analyzer free. First test paid human-assisted handover reviews, training or supported local deployment; these are business hypotheses, not launched services. Do not assume a recurring subscription is justified yet. Check dependency and distribution rights before any commercial release; deleting branding text does not change existing licences or ownership.

## Validation before more broad development

Run five authorized handovers from at least three unrelated codebases. Have a second developer answer the same questions with and without Reversium: main feature path, required services, setup steps, important gaps and next change. Measure task time, source-verified correctness, missed requirements, misleading claims, report usefulness and support effort. Ask for a paid pilot commitment rather than praise. Suggested decision gate: at least three reviewers independently use the output, two buyers commit to a paid review, and delivered value exceeds support effort without hiding unsupported claims. These are proposed targets, not measured results.
