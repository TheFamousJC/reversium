# reviewed example application CMS photograph workflow test - 19 October 2026

Project names in historical notes have been anonymized. Recorded counts, fingerprints, outcomes and limitations describe a specific reviewed example, not arbitrary code packages.

Documentation build 0.23.1. This is a bounded local browser test of the photograph workflow, using synthetic raster test artwork rather than a camera photograph. It does not establish all image formats, rights policies or production durability.

## Identity and isolation

Original reviewed example application ZIP SHA-256: `6271cf0f60c7da652bb0ee36bcbbff02a4693a0310f97dd70a11db1ec5af466b`. The archive was unchanged. Completed browser run 157411ce697d used a fresh disposable organization, separate editor/reviewer accounts and real local PostgreSQL/Auth/REST/Storage services inside the offline QEMU/WHPX guest. All 14 fresh isolation checks passed at 3 GiB guest RAM before application input. No live credentials, guest NIC, host shares, public listener or paid service was introduced. The host preview is gated loopback HTTP relayed over serial to a fixed guest HTTPS gateway; guest TLS validation remains enabled.

The supplied fixture is tests/fixtures/media/photo-cms-fixture.png: 192 by 128 pixels, 2,064 bytes, SHA-256 `f8456805dd5e401c572eefebb378a3076995b4774ed9991a92c6d29100024fea`. It contains geometric test artwork and no personal data. The successful upload used the supplied filename photo-cms-fixture.png. Its metadata is Own work, creator Reversium QA and public credit Reversium QA - synthetic test image. No third-party licence or photograph ownership was assumed.

## Browser observations

| Step | Evidence | Result |
| --- | --- | --- |
| Editor authentication | Synthetic editor reaches the new organization in Tour CMS | Passed |
| Missing rights | Selecting a PNG with rights unset shows Choose the image rights status before uploading | Passed |
| Missing credit | Own work selected, but credit empty: Enter the exact public image credit before uploading | Passed |

The two validation failures were observed in earlier browser attempt c7c93153f072 against the same original ZIP. Private route/status diagnostics showed no media POST during either validation failure. These are UI validation observations, not a claim that every malicious request is rejected server-side. Subsequent observations are recorded below; approval and public display were not established.

Attempt c7c93153f072 then encountered a serial-transfer failure on the valid 2,064-byte upload. No completed media POST was recorded, so this is not a failed reviewed example application upload assertion; a partial request cannot be ruled out. That guest stopped and its input image remained unchanged. The relay was changed to transfer larger request packets in bounded shell-safe chunks with a SHA-256 check inside the guest. Regression tests reconstruct the exact bytes, reject tampered packets and refuse oversized files before reading. A separate fresh guest is required for the final photo journey.

Attempt e82c0f8b4204 started successfully but returned generic relay errors for ordinary pages. It was stopped using the corrected browser control; post-test isolation, unchanged input and stopped-guest checks passed. A direct/chunked HTTP preflight and private guest-only error diagnostics were added before exposing any later browser entry. These startup/transport records establish no image-approval or publication result.

## Startup blocker and test limits

Initial attempt 2ac688367435 exited unexpectedly after disposable services reported healthy, before reviewed example application migrations completed. Input remained unchanged and the guest stopped. No photograph result was claimed from that attempt; the cause was not established. A fresh isolation gate and guest were used for the browser attempt.

The relay has a 2 MiB request/response limit, lower than reviewed example application's advertised 8 MB upload limit. Serial transfer is slow. This small PNG does not establish large JPEG/EXIF handling, malicious-file resistance, all licence options, media rejection/appeal behavior, external URL importing, production uptime or storage durability. Host private input images, credentials, screenshots and logs may remain after guest RAM is discarded. They are excluded from publication. Manual browser observations remain separate from automatic API evidence.


## File-selection blocker

Run 10ab07b3d5ac passed both real-guest HTTP preflights (ordinary request and chunked larger request) and opened the CMS. Its browser file-selection/upload operation then stalled for approximately twenty minutes; the supervised preview expired at its existing deadline. No completed media POST was recorded in this run; that log alone cannot exclude a partial request. Post-test isolation, input hash and stopped-guest checks passed. This does not establish an application upload failure, reviewer approval or public-image visibility. A further retry uses a bounded chooser-opening call and an explicit timeout on file selection, with the supplied public synthetic fixture. It is needed to separate browser automation from the software behavior.

## Completed browser attempt: upload passed, review blocked

Run 157411ce697d ran from 07:09:18 to 07:26:47 UTC. Both ordinary and chunked HTTP preflights passed before the private browser entry was exposed. The browser file picker still took approximately six minutes despite an explicit ten-second automation timeout; this is a browser-automation blocker, not evidence of reviewed example application processing time.

| Step | Evidence | Result |
| --- | --- | --- |
| Valid PNG upload | POST /api/admin/media returned 201; CMS displayed Image uploaded and awaiting media approval | Passed |
| Attach image and submit package | Editor submitted Reversium Photo Test City with Photograph Test Stop; CMS displayed Tour submitted to the review queue and three pending content items | Passed |
| Separate reviewer login | Reviewer signed in; working organization value matched the editor organization | Passed |
| Reviewer sees submitted work | Review & Publish displayed Content proposals (0), Photographs (0), The review queue is clear and No uploaded media is waiting for approval | Blocked |
| Approve media and publish image-bearing tour | No reviewable item was available; no approval or publication action was substituted through APIs | Not verified |
| Anonymous public image, credit and exact bytes | Not reached for this new upload | Not verified |

The queue discrepancy remains unexplained. HTTP 200 table responses establish successful transport, not that rows were returned or permission rules were correct. Possible account/session state, query filtering, service-policy or preview behavior needs investigation in a fresh bounded run. Reloading the CMS timed out; that did not resolve the discrepancy. No access policy, reviewer privilege or reviewed example application business logic was changed to make this test pass. Previous API image acceptance and previous text-only CMS publishing remain separate evidence and do not close this gap.

The protected browser Stop preview and guest control returned Preview stopping. The final record reports 163 relayed requests, post-test no-external-route check passed, input image unchanged and guest process stopped. Filtered-copy SHA-256: e394bbe46bceeff9b51a7f8688b5a294147bfb51ad01e005c3073a4961dadcea. Original ZIP fingerprint is above. The automated record keeps browser publishing unverified (null); these manual observations do not alter it.

Private evidence: photo-tour-submitted-0231.png and photo-reviewer-empty-0231.png, bounded route/status diagnostics and latest-cms-preview.json. These remain outside published assets. The synthetic fixture and this redacted report are distributable. Next investigation: compare editor/reviewer content and media visibility using normal authorized CMS sessions, inspect query scope and policy behavior, then repeat media approval and anonymous image/credit verification. Do not bypass the empty queue by directly publishing database rows.
