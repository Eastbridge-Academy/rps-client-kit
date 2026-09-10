# Two-hour RPS workshop

The Markdown pages are the reviewable source. `---page---` marks an intentional
page boundary. The four route PDFs each prepend the four pages of common.md, so
participants can choose directly by experience. The field guide is generated
from the same house catalogue the CLI and arena use. Facilitator solutions are
optional teaching aids.

The PDFs use the Eastbridge Academy LaTeX house style: Computer Modern serif
text and mathematics, the Academy logo, Solarized accents, framed checkpoints,
Python listings and booktabs tables. The reusable preamble is in
latex/eastbridge-handout.sty. It follows courses/resources/template.tex and
projects/chess-bot/week1.tex; latex/eastbridge-logo.pdf is the Academy's original
vector artwork, copied from courses/resources/eastbridge-logo.pdf. Neither the
courses checkout nor an external font download is required for a build.

## Build

Install TeX Live / MacTeX with `pdflatex` on PATH. On Debian or Ubuntu, the
required packages are `texlive-latex-extra texlive-fonts-recommended lmodern`.
Only the person building the PDFs needs TeX; participants receive finished PDFs.

```bash
uv sync --group workshop
uv run pytest
uv run ruff check
uv run --group workshop python workshop/build_handouts.py
uv build
uv run python workshop/build_bundle.py
```

The PDF build requires exactly the planned pages and fails on accidental
overflow or missing glyphs. It runs pdfLaTeX twice with shell escape disabled;
generated TeX, logs and intermediate PDFs remain in output/latex/ for review.
Use `--only beginner` (or another route, `field-guide`, `facilitator`) to iterate
on one document. Inline `$...$` and fenced `math` blocks use LaTeX mathematics;
inline code and Python/shell listings preserve literal quotes and underscores.

Render the PDFs and inspect every page before distributing them;
page counts alone cannot catch clipping, poor wrapping or unclear hierarchy.
Generated files are ignored under output/. Commit sources first, then rebuild
the final wheel and bundle so BUILD.json identifies a clean source commit.

The bundle builder fetches only locked runtime dependency wheels and verifies
their lockfile hashes. It excludes the PDF toolchain and development tools.
All bundled wheels must be platform-independent. Setup uses uv, an installed
Python 3.11+, a local wheelhouse and no index or automatic Python download.

See [the verification record](verification.md) for exercised platforms, Arena
integration evidence and the remaining check on the physical lab image.

Final outputs:

- output/pdf/: four route packets (7, 8, 8 and 9 pages), a two-page landscape
  field guide and three pages of facilitator notes; 37 pages in total.
- output/rps-event-kit.zip: offline lab distribution with printable handouts.
- output/rps-event-kit/: the same bundle, extracted for smoke testing.

Keep event URL/league/token distribution separate from source and artifacts.
The printed defaults are examples. Test the actual server's upload, validation,
activation and completed-match path before the event.
