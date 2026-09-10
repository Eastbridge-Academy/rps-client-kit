# Event-kit verification, September 10, 2026

The local 0.3.0 participant deliverable is prepared for review. These checks do
not mean a public release or production deployment has happened.

## Exercised paths

- macOS ARM64, Python 3.13.5: full kit suite, **70 passing tests**; Ruff passes.
- Linux ARM64, Python 3.11.14, Debian Bookworm container: offline wheel install,
  starter tests, validation, 501-throw practice, full JSON export, source
  packaging and extracted-archive validation all pass with Docker networking
  disabled. The complete tests/ suite also passes on this platform (the final
  certificate-diagnostic tests were added afterwards and passed on macOS).
- Setup works in a path containing spaces and preserves participant edits on
  rerun. Bundle hashes and submission archive contents were checked. The bundle
  contains 21 universal wheels, including the kit; no compiler or PDF toolchain
  is installed on participant machines.
- The advanced reference bot scored 475 wins, 12 losses and 14 draws against
  Double Take at practice seed 42 in the ARM64 smoke run, with no errors.
  This illustrates the model; it is not a universal performance guarantee.
- The reference-model tests check incremental counts against complete rebuilds,
  delayed scoring of portfolio proposals, setup resets, balanced first-order
  versus deterministic second-order structure, exact payoff arithmetic and the
  finite-horizon objective. All five reference bots complete 501-throw series
  against all 16 house personalities, twice with reset state.
- All **37 PDF pages** were rendered and visually reviewed after the Eastbridge
  house-style pass: beginner 7 pages, intermediate 8, advanced 8, expert 9,
  house guide 2, facilitator notes 3. Each route includes the same four-page
  foundation. Page counts, print bounds and missing-glyph checks pass; all six
  pdfLaTeX builds have zero overfull or underfull box warnings.
- The typesetter uses the original Academy vector logo, Computer Modern text
  and mathematics, the chess handouts' Solarized palette, framed checkpoints,
  highlighted code and booktabs tables. The 11-point body stays readable while
  deliberate page breaks keep the exercises together. Display equations and
  literal Python/shell quotes were checked in the rendered pages.
- The source archive includes the LaTeX preamble and logo; it can be built
  without the courses checkout. The participant wheel excludes the typesetter,
  and the offline bundle includes finished PDFs. ReportLab is no longer needed.
- Both GitHub workflow files parse as YAML and both shell scripts pass syntax
  checks. CI now covers Python 3.11, 3.12 and 3.13 and builds review artifacts;
  hosted CI itself has not run because these commits have not been pushed.

## Arena integration

The matching Arena work passes **113 API tests and 44 worker tests**, including
the isolated Docker stack smoke. An additional participant workflow test passes
doctor, two same-name submissions, version-2 activation, imported helper-package
execution, actual previous-throw outcome assertions, and a complete 17-bot round
with four workers (136 matches at its snapshotted 51-throw configuration).

Separately, the real sandbox engine ran the expanded 16-bot field through
**720 matches of 501 throws: 360,720 throws, zero errors and zero timeouts**.
Every pair played both seats at seeds 1729, 12345 and 8675309. Reversed seats
preserve each bot's seed and produced exactly mirrored scores; those reversals
are symmetry checks, not independent statistical samples.

The dev API, scheduler and worker were rebuilt with the matching 0.3.0 contract.
The existing 13-bot rehearsal was preserved, remained unpaused, and completed a
full round after the update. The new three bots are available in the catalogue
but were not silently added to that existing league. Runtime health is healthy.

## Organizer checks still needed

Run workshop/smoke_bundle.sh on the actual Raspberry Pi lab image before the
session. ARM64 container coverage verifies architecture and Python compatibility;
it is not a measurement of physical Pi startup time, CPU speed or RAM usage.
Windows instructions have not been exercised on a Windows host.

Choose and deploy the intended event server, publish the reviewed kit if desired,
and give participants its URL, active league slug and submit token. Perform one
designated submission against that server before opening the room. The public
production instance has not been changed by this participant-preparation work.

For dev.arena.eastbrid.ge, the existing mkcert CA must be trusted by Python via
SSL_CERT_FILE. The doctor reports this case specifically. The bundle does not
contain that machine's CA certificate or any event credentials.

Existing upstream RQ datetime and macOS fork deprecation warnings remain in the
backend tests; the test runs have no failures. Local practice uses a whole-match
deadline; the server's per-move timeout remains a distinct check.
