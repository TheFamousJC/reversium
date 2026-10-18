# Isolated execution proposal

Status: preparation stage implemented in 0.18.0; VM execution remains unimplemented. Reversium does not run software from uploaded ZIPs. The browser worker isolates the analyzer, not an application execution environment. Traffic-light review never authorizes execution.

## What is possible

A local companion could create a disposable virtual machine, expose its local application preview and return a run log to the same Reversium UI. Static web hosting cannot create a native VM, execute arbitrary EXE/server applications or supply free remote compute. A first release should support one explicit guest platform and known runtime instead of promising to run every project.

Windows Sandbox is a candidate on an existing supported Windows Pro, Enterprise or Education machine, with virtualization available and the feature enabled. Home is unsupported. It is not a universal zero-cost entitlement: a user without the required edition or hardware needs another option. A Linux guest with a suitable local VM engine is a possible alternative; guest OS, runtime and dependency licenses must be checked. Ordinary containers are useful for trusted development, but are not the proposed sole boundary for unknown programs.

## Proposed isolation and approval boundary

1. Inspect the ZIP first. Preserve existing unsafe-path, symlink, duplicate-path, size and decompression limits. Reject blocked archives; unresolved red/yellow signals require source review. The light is never an execution gate by itself.
2. Provision a fresh disposable VM from a trusted, pinned image. No privileged host access, Docker socket, host credentials, clipboard, microphone, camera or broad writable folder mounts. Map only a dedicated input staging location read-only, or import a read-only disk containing the reviewed ZIP. Even read-only inputs can disclose their contents to the guest.
3. Disable networking initially, including access to live databases, local-network services and cloud metadata. Dependency downloads need a separate reviewed provisioning process with explicit destinations; no automatic retry that silently enables networking. Offline mode may block setup entirely.
4. Show the developer proposed commands, runtime versions, required services and unresolved requirements before execution. Never auto-run archive scripts, package installation hooks, privileged operations or guessed commands. Use synthetic configuration and disposable database/auth data; never copy production environment values.
5. Enforce guest CPU/memory/disk limits, a time limit and termination control. Do not expose guest ports to the LAN. An eventual browser preview needs a dedicated origin/session boundary and explicit local forwarding; guest pages remain untrusted content.
6. Capture exit codes and bounded logs. Redact secrets where possible; logs can still contain private data and must be reviewed before export. Record which behaviors were actually tested and distinguish setup failure from missing features.
7. Destroy the disposable guest after the run. Export only explicitly reviewed artifacts; never automatically copy arbitrary guest files to host locations.

## Development stages and acceptance checks

- Stage 1: capability detection and user-visible setup plan; no execution. Test unsupported hosts and missing prerequisites.
- Stage 2: boot and destroy a blank offline guest, verify network/clipboard/mount policies and timeout/cancel handling. No user software.
- Stage 3: run a tiny known fixture with synthetic inputs. Confirm it cannot reach a test host service or write outside its intended guest storage.
- Stage 4: manually approved application setup on a copy of Tudela with synthetic services, then a bounded workflow test. Missing dependencies, offline setup and operating-system differences must remain visible.
- Stage 5: optional reviewed network/provisioning profiles and guarded preview routing, with isolation regression tests before enabling public use.

No VM provides a guarantee of zero risk. A compromised host or hypervisor, unsafe sharing configuration, secret exposure and unreviewed network access remain possible. Secure execution is a separate development milestone, not part of the static traffic-light feature.

## Primary sources reviewed 18 October 2026

- [Windows Sandbox overview and supported editions](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/)
- [Windows Sandbox configuration: networking, sharing and redirection](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)
- [Docker Engine security and isolation considerations](https://docs.docker.com/engine/security/)


## Implemented preparation stage (0.18.0)

`python -m reversium --sandbox-check` reads OS edition and executable availability without starting processes. `python -m reversium --sandbox-plan reports/new-sandbox-plan` creates a new directory (refuses overwrite) with a host check, a blank offline Windows Sandbox configuration, an explicitly untested QEMU argv draft and instructions. No ZIP is copied, no files are mapped, and no guest or archive command is run. The local server exposes read-only prerequisite status; the online UI cannot inspect host capabilities.

On the development machine: Windows Core/Home, Windows Sandbox executable not found, QEMU not found. Docker CLI exists but its engine was unavailable; QEMU was also not found inside WSL. WSL Ubuntu exists but is not treated as a disposable unknown-code boundary. No optional Windows features were enabled and no backend or guest image installed. The first usable no-upgrade path to investigate is QEMU plus a trusted Linux guest, with network devices absent and no host shares. Software-emulated TCG is a possible draft profile, with performance and compatibility unverified.

Prepared profiles are not a working Tudela sandbox. Next: obtain and verify a trusted backend/image, boot a blank guest, verify network/share isolation and termination, then design a narrow ZIP input channel and reviewed offline runtime provisioning. A timeout supervisor, reproducible guest image, tested teardown and guarded preview are still missing. Do not execute the draft as proof of isolation.


## Implemented experimental QEMU pilot (0.19.0, 18 October 2026)

The previous sections record the preparation stages. This build adds an explicit native Windows CLI supervisor, not a browser execution endpoint or a general unknown-ZIP runner. Existing Windows Home works without an OS upgrade. QEMU was extracted into the ignored workspace lab; no installer, PATH change, Windows feature enablement, Docker engine or WSL boundary was used. TCG is the portable software-emulation default. WHPX was already available on this machine; it is an explicit opt-in (`--sandbox-accelerator whpx`) with the same fresh isolation gate and no fallback.

### Asset provenance

- QEMU 11.1.0 Windows build `qemu-w64-setup-20260811.exe`, from the Stefan Weil provider linked by [QEMU's download page](https://www.qemu.org/download/#windows), with the provider's SHA-512 pinned in `reversium/qemu_lab.py`.
- Alpine Linux virtual ISO `alpine-virt-3.23.6-x86_64.iso`, from the [official release directory](https://dl-cdn.alpinelinux.org/alpine/v3.23/releases/x86_64/), with its published SHA-256 pinned. Kernel and initramfs are extracted from that ISO. Extracted runtime files are hashed locally and rechecked before execution.
- These are publisher checksums obtained over HTTPS, not independent signature attestation. The Windows provider describes its QEMU builds as experimental. No malware-free or zero-risk claim is made.
- Optional `pycdlib==1.14.0` is installed into the ignored lab only for ISO authoring. Ordinary Reversium analysis does not require it.

### Actual enforced profile

QEMU has no NIC (`-nic none`), host shares, clipboard integration, USB passthrough, remote monitor, VNC/SPICE or port forwarding. It uses direct trusted-kernel boot, a read-only raw Alpine CD and a separate read-only raw input CD. There is no writable persistent guest disk. Guest state is RAM-backed; limits are 1 GiB guest RAM, two virtual CPUs, a 2 MiB serial log cap and a maximum 600-second application deadline. A Windows kill-on-close job and explicit teardown supervise QEMU. Guest output is data, never host shell commands. CPU emulation can be slow; deadlines remain bounded.

Guest loopback is enabled so internal services can communicate; no external interface or default route is added. Host-side provisioning fetches public Alpine packages and compatible Linux/x64/musl tarballs identified by the delivery lockfile. It sends public package identifiers, never the source ZIP. Packages are not installed and project scripts are not run on the host. Offline guest APK installation retains signature trust; npm tarballs must match lockfile SRI. Tarballs are unpacked only inside the guest, without npm lifecycle hooks.

### Isolation acceptance checks before application input

All 14 selected checks passed with TCG and with WHPX: expected Alpine version; loopback-only interface; no external route; guest HTTP to a host test listener fails; no host-share filesystem mounts; benign probe CD mounts; probe is readable; filesystem write is rejected; no Windows host mount; input ISO hash unchanged; host canary unchanged; host listener receives no connection; a fresh guest lacks the previous RAM marker; a forced one-second deadline stops QEMU. Every application probe repeats these checks using its selected accelerator, before loading the application bundle. Failures prevent application startup.

These checks test this configuration and selected behaviors. They are not a hypervisor penetration test, raw-block-device attack test or proof against emulator/kernel vulnerabilities, compromised host tools or all secret leakage. Read-only media and discarded guest memory do not erase retained host artifacts.

### Narrow Tudela profile and private artifacts

The pilot refuses red file-review signals or members without completed bounded CRC checks. Repacking stays in memory on the host. Common `.env*`, key, credential and generated dependency/Git paths are omitted; this is not a complete embedded-secret detector. Only the reviewed Tudela build/start script profile is supported. The original ZIP is unchanged. Application input and logs stay under ignored `reports/qemu-lab/runs/`; they can contain private code and must not be published. Public reports contain test summaries only.

The exact delivery tested has SHA-256 `6271cf0f60c7da652bb0ee36bcbbff02a4693a0310f97dd70a11db1ec5af466b`. Its guest input uses 235 compatible locked npm entries and 22 runtime APKs. Early setup attempts exposed a live-Alpine nonrepository-package rule and an OpenSSL package version mismatch; both were resolved without disabling package signatures. TCG compiled the frontend and backend, but its startup check failed while guest loopback was down. Enabling guest-only loopback fixed that setup defect. A subsequent attempt correctly refused incomplete production configuration; production checks were preserved, with later experiments using reserved `.invalid` HTTPS addresses, distinct synthetic keys and simulator mode. No real Supabase, OpenAI or other live credentials were supplied.

Remaining scope: disposable database/auth/storage fixtures, migration tests, authenticated and published-tour journeys, guarded preview origin/forwarding, broader reviewed project profiles, signed asset attestation and additional host platforms. No paid cloud service is required for this pilot. Hosted ChatGPT remains disabled.

Primary runtime references: [QEMU invocation options](https://www.qemu.org/docs/master/system/qemu-manpage.html), [WHPX requirements](https://www.qemu.org/docs/master/system/whpx.html), [Windows binary provider](https://qemu.weilnetz.de/w64/).


Final WHPX outcome: Node v24.18.1/npm 11.11.0, frontend build and backend compilation succeeded. The compiled production server returned guest-local HTTP 200 for GET /, with a nonempty body. No external route remained afterward, the input image hash matched and QEMU stopped. This is only build/start acceptance; no database, authentication, storage or published-tour workflow was verified. Private result/log: ignored lab run tudela-a460bf0f19d4.


## Portable exact-delivery evidence (0.21.0)

Application probes now emit run-evidence.json and a latest-run-evidence.json alias in the private lab. A fixed allowlisted contract records original ZIP and filtered-copy SHA-256, omitted count, profile/run/version/time metadata and explicit true/false/null outcomes. No raw logs, source paths, credentials or arbitrary exception strings enter this portable file. Input copying hashes and repacks the same bounded immutable snapshot. Setup & readiness can preview and explicitly attach the record only to matching archive_sha256, separately from static findings. This is not signature verification or an authenticated runtime attestation. Manual JSON editing remains possible and is disclosed. HTML exports preserve applied evidence separately; static JSON and AI packets do not include it. The unchanged offline guest boundary and synthetic configuration still apply. The fresh Tudela result passed 14 isolation and 11 application/teardown checks; no wider service/workflow acceptance is established.
