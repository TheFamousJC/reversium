# reviewed example application CMS browser test — 18 October 2026

Project names in historical notes have been anonymized. Recorded counts, fingerprints, outcomes and limitations describe a specific reviewed example, not arbitrary code packages.

Build 0.23.0. This report distinguishes browser actions from sandbox setup and earlier API acceptance. It is a bounded test of one delivery, not production or security certification.

## Delivery and environment

Original ZIP SHA-256: `6271cf0f60c7da652bb0ee36bcbbff02a4693a0310f97dd70a11db1ec5af466b` (266 files). The original archive was unchanged. A filtered copy omitted the environment-example member. Source and private credentials were not published.

The reviewed Windows QEMU/WHPX guest used Alpine, Node v24.18.1/npm 11.11.0, PostgreSQL 17.11, Auth 2.197.0, PostgREST 16.4 and Storage 1.83.5. The original migrations and application business logic were retained. Before application input, all 14 selected isolation checks passed at 3 GiB guest memory.

The guest had no NIC, host shares, passthrough or forwarded network port. A temporary gated HTTP listener on host loopback relayed requests over serial to a fixed guest HTTPS gateway. The frontend was built for that preview origin; guest TLS validation remained enabled. Browser external connections were blocked. This is a distinct test configuration, not the live platform.

## Preparation rather than browser evidence

Services, empty database, migrations, a disposable organization and separate editor/reviewer accounts were prepared by the test harness. This is not evidence that staff provisioning or migrations work through the CMS UI. No API acceptance script was used to create or publish the browser test tour.

## Observations

Manual browser run: 7eead40febda. Machine-produced cms-result.json records only setup/teardown; it never automatically claims a successful browser publishing journey.

| Step | Observed evidence | Result |
| --- | --- | --- |
| Editor sign-in | Separate synthetic editor reaches Tour CMS for Disposable Browser Test | Passed |
| Create destination | New Tour Wizard accepts city/country, overview and manual coordinates | Passed |
| Add stops | Wizard review shows Browser Test Stop One and Two in entered order | Passed |
| Submit package | CMS says “Tour submitted to the review queue”; one shared destination, two shared stops, four items awaiting action | Passed |
| Reviewer sign-in | Separate reviewer account reaches the same organization; editing tools are absent | Passed |
| City approval/publication | Approved revision exposes Publish approved revision; CMS then reports Revision published and removes city proposal | Passed |
| Tour and stop approval/publication | Reviewer clicks approve and publish for tour and both stops; final CMS reports 1 published city, 1 tour, 2 stops, zero pending items and Revision published | Passed |
| Anonymous visitor check | After reviewer sign-out, the organization-specific visitor page shows the new city, its Heritage Tour and both named stops in order | Passed |

The route/status diagnostic independently records successful browser-initiated city/tour/stop writes, four submit_content_for_review calls, four approval inserts and four publication calls. The organization-specific public-content HTTP request returned 200; the visible browser tour confirms both stops. It contains no request bodies or authorization values. Screenshots remain private under reports/.

The browser journey passed for this minimal two-stop tour. The CMS displayed one published city, one tour, two stops and zero pending items. The public visitor page was signed out and showed the exact test names, rather than the bundled demonstration cities. No direct database edits or API-script substitutes completed any of these content steps.

## Blockers and limits

The first launch could not parse the account fixture after a serial shell prompt; parsing was corrected and that guest stopped. The first browser attempt reached the editor wizard and submission but the serial preview became unresponsive to queued requests. It was stopped without claiming publishing success. Repeated headers and idle Node connections were removed from the transport path, and private bounded route/status diagnostics were added. These are preview issues, not established reviewed example application defects.

The documented CMS address is /cms; the visitor screen's account menu did not provide an obvious CMS entry in this test. Before this disposable organization has published content, the visitor app can show bundled demonstration cities. Those cities must not be mistaken for successful database publication.

The original Stop form was rejected by the preview origin check. A direct API shutdown attempt was rejected by automatic approval review as an access-control bypass and was not executed. The existing guest was left to its original deadline. The form was corrected to require a separate unpredictable CSRF confirmation plus the entry cookie, while application mutations retain exact Origin checks. Missing-cookie and invalid-token requests reject; the corrected form completed in a separate browser test on a mock server with no guest attached. This does not retroactively claim the original Stop click worked.

External geocoding/maps, fonts and live AI/email/OAuth remain intentionally unavailable or untested. Coordinates were entered manually. External fallback thumbnails appeared broken under the isolation policy; no photographs were uploaded through this browser journey. The browser journey does not establish media upload, real narration, GPS walking, production stability, backup/restore or complete security. Earlier API image round-trip results remain separate evidence.

## Reproduce and stop

Follow the CMS preview chapter in Help. Run python scripts/test_project_cms.py "path/to/your-package.zip" --accelerator whpx where supported; open the private entry URL and use only its disposable accounts. Open /__reversium on that same origin to stop the preview. Host input images, private credential files, browser session data, screenshots and logs can remain after guest RAM is discarded. Do not distribute them.


## Final teardown and retained evidence

Run 7eead40febda started at 2026-10-18T19:16:07Z and finished at 19:38:19Z. Its twenty-minute preview deadline stopped the listener and QEMU. Post-test guest loopback/no-route, unchanged input image and stopped guest checks passed. Setup/teardown recorded success; browser_publishing_verified remains null in the generated record, because the browser observations belong to this separate reviewed report.

Filtered-copy SHA-256: `f7cebd79b5a6fbe5c35bd5dbbdbc8a42ea4c45fc767e55a14c3e9c477319acef`; this differs from the original delivery identity above. The preview relayed 291 requests. The earlier v2 API result for run 1eb69ba4c21f was preserved unchanged. Private artifacts remain local and ignored; source-bearing media and logs were not published. No guest, preview listener or live-platform connection remains running.


[Photograph follow-up](CMS_PHOTO_TEST.md): upload passed; reviewer queue empty. The earlier publishing result does not establish photograph publication.
