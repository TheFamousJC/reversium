# Isolated execution proposal

Status: design only, build 0.17.0. Reversium does not run software from uploaded ZIPs. The browser worker isolates the analyzer, not an application execution environment. Traffic-light review never authorizes execution.

## What is possible

A local companion could create a disposable virtual machine, expose its local application preview and return a run log to the same Reversium UI. GitHub Pages cannot create a native VM, execute arbitrary EXE/server applications or supply free remote compute. A first release should support one explicit guest platform and known runtime instead of promising to run every project.

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
