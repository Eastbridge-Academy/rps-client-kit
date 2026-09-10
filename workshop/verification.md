# Event-kit verification, September 10, 2026

## Version 0.3.1: handouts and personal laptops

- All seven native LaTeX handouts compile with zero box or missing-glyph
  warnings. All **33 pages** were rendered and visually reviewed, including
  Windows commands, two-digit listing numbers and the expert mathematics.
- Setup and practice are now a separate four-page handout. Level packets are
  5, 6, 6 and 7 pages and begin with theory and bot mechanics. The house guide
  remains two landscape pages; facilitator notes take three pages.
- macOS ARM64: **70 tests pass**, Ruff passes, and fresh project and uv-tool
  installs exercise validation, 3,006 recorded practice throws, packaging and
  preserved edits. The beginner test executes its actual native LaTeX listing.
- The event ZIP includes seven PDFs and 21 portable wheels. Offline setup,
  manifest hashes, 1,503 recorded throws, extracted submission validation,
  paths containing spaces and preservation of participant edits pass locally.
- CI also builds the PDFs and ZIP on Linux and tests the extracted ZIP on
  Windows with the handout's PowerShell installation commands. The Windows
  check invokes the executable directly, without script activation. All seven
  jobs pass: [CI for 79a2852](https://github.com/Eastbridge-Academy/rps-client-kit/actions/runs/34505062382).
- A final PDF text-extraction check verifies literal double hyphens in inline
  commands. The typewriter font disables ligatures so `--version` and `--force`
  remain copyable command options. Prose keeps its normal ligatures.
- This release changes documentation and distribution; bot and SDK behavior
  remain as in 0.3.0. The physical Raspberry Pi lab-image check still applies.

The sections below retain the earlier 0.3.0 rehearsal evidence. Server state
and remaining deployment tasks there describe that rehearsal, not current prod.

## Version 0.3.0 rehearsal record

This record covers version 0.3.0. GitHub builds the release assets from the
version tag and records the source commit and file hashes in each event
bundle's BUILD.json.

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
- A subsequent prose edit covered all six handouts, the house-bot catalogue,
  the bundle README and the reference-bot instructions. It replaced repeated
  warnings and abstract teaching slogans with explanations and exercises about
  the actual bots. Code blocks and displayed equations match the preceding
  version exactly. All 37 revised pages were rendered and inspected, with the
  same page counts and zero box warnings; the 70 kit tests and Ruff pass.
- Hosted GitHub test jobs pass on Linux with Python 3.11, 3.12 and 3.13, and on
  macOS and Windows with Python 3.12. Each runs all 70 tests, Ruff, a package
  build, and fresh project and uv-tool installs from the resulting wheel.
  Each installation check exercises starter tests, validation, 3,006 practice
  throws, JSON exports, submission packaging and preserved edits in paths with
  spaces. The Windows run checks the executable without PowerShell activation.
  Results: [CI run for 397bf51](https://github.com/Eastbridge-Academy/rps-client-kit/actions/runs/34484341911).
- The hosted workshop build creates the six PDFs and event ZIP, then exercises
  offline installation and participant commands. Both workflow files parse as
  YAML and both shell scripts pass syntax checks.

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

Choose and deploy the intended event server and give participants its URL,
active league slug and submit token. Perform one
designated submission against that server before opening the room. The public
production instance has not been changed by this participant-preparation work.

For dev.arena.eastbrid.ge, the existing mkcert CA must be trusted by Python via
SSL_CERT_FILE. The doctor reports this case specifically. The bundle does not
contain that machine's CA certificate or any event credentials.

Existing upstream RQ datetime and macOS fork deprecation warnings remain in the
backend tests; the test runs have no failures. Local practice uses a whole-match
deadline; the server's per-move timeout remains a distinct check.
