# Two-hour RPS workshop

The handouts are authored directly in **latex/*.tex**. Edit those files, then
compile them with the small uv-runnable builder. There is no Markdown conversion
step. The level handouts share `latex/shared/theory.tex` and `mechanics.tex`;
setup and practice are in their own PDF for a separate print pile.

The PDFs use the Eastbridge Academy house style: Computer Modern text and
mathematics, the Academy logo, Solarized accents, framed checkpoints, Python
listings and booktabs tables. The reusable preamble is
`latex/eastbridge-handout.sty`, adapted from `courses/resources/template.tex`
and `projects/chess-bot/week1.tex`. The original vector logo is bundled, so
neither the courses checkout nor an external font download is needed.

## Build

Install TeX Live / MacTeX with `pdflatex` on PATH. On Debian or Ubuntu, the
required packages are `texlive-latex-extra texlive-fonts-recommended lmodern`.
Participants receive finished PDFs and do not need TeX.

```bash
uv sync --locked
uv run pytest
uv run ruff check
uv run --locked --script workshop/build_handouts.py
uv build
uv run --script workshop/smoke_install.py
uv run --locked --script workshop/build_bundle.py
```

The builder copies the LaTeX sources into `output/latex/`, runs pdfLaTeX twice
with shell escape disabled, and checks page counts, overflow and missing glyphs.
Use `--only setup`, a level name, `field-guide` or `facilitator` to compile one
handout. Logs and intermediate files remain under `output/latex/` for review.
The planned page counts live in `DOCUMENTS` in the builder; change them only
when deliberately changing the print layout.

The three standalone Python scripts declare Python requirements and dependencies
in PEP 723 headers. The two builders have checked-in script lockfiles.
`build_handouts.py` depends only on pypdf; it does not install the client kit.
Scripts can be invoked by absolute path from another directory.

Render and inspect every page before distributing it. In particular, check
numbered code, wrapped commands and mathematics at full size. Page counts alone
cannot catch clipping or poor spacing. Generated artifacts are ignored under
`output/`. Commit sources first, then rebuild the final wheel and ZIP so
`BUILD.json` identifies a clean source commit.

The house-bot guide is also editable LaTeX. When a bot changes, update its row
alongside the catalogue in `rps_house_bots/__init__.py`. The reference solutions
remain in `solutions/`; the test suite executes the beginner handout's actual
cycle-prediction listing as well as the reference models.

## Print and distribute

Seven PDFs, **33 pages total**:

- **00 Setup and practice — 4 pages:** lab setup and submission, macOS/Linux,
  Windows, then practice and scoring. Print separately from the levels.
- **01 Beginner — 5 pages:** randomness, bot mechanics, simple patterns.
- **02 Intermediate — 6 pages:** randomness, bot mechanics, counts and windows.
- **03 Advanced — 6 pages:** randomness, bot mechanics, Markov models.
- **04 Expert — 7 pages:** randomness, bot mechanics, portfolios and match utility.
- **05 House-bot field guide — 2 pages:** all 16 opponents, hints and a quick reference.
- **06 Facilitator notes — 3 pages:** preparation, schedule, checks and answers.

`output/rps-event-kit.zip` contains all PDFs, the client wheel and locked
runtime dependency wheels, setup script and reference bots. Download the
[published event ZIP](https://github.com/Eastbridge-Academy/rps-client-kit/releases/latest/download/rps-event-kit.zip)
for lab accounts or personal laptops; see the [participant README](../README.md).
The event token is distributed by the facilitator, separately from the kit.

The bundle builder verifies dependency wheel hashes against uv.lock and rejects
platform-specific wheels. It excludes development and PDF tools. The offline
setup requires uv and an installed Python 3.11+; personal-laptop instructions
cover installing those tools first. Finished bundles include source provenance
and file checksums.

CI exercises fresh wheel installations on Windows, macOS and Linux, and the
extracted event ZIP on Linux and Windows. To check a published wheel or Git tag,
pass its URL to `smoke_install.py`; it uses temporary environments and leaves
participant projects alone. See [verification.md](verification.md) for results
and the physical lab checks.
