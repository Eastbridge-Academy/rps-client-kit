# Two-hour RPS workshop

The Markdown pages are the reviewable source. `---page---` marks an intentional
page boundary. The four route PDFs each prepend common.md, so participants can
choose directly by experience. The field guide is generated from the same house
catalogue the CLI and arena use. Facilitator solutions are optional teaching aids.

## Build

```bash
uv sync --group workshop
uv run pytest
uv run ruff check
uv run --group workshop python workshop/build_handouts.py
uv build
uv run python workshop/build_bundle.py
```

The PDF build requires exactly the planned pages and fails on accidental
overflow. Render the PDFs and inspect every page before distributing them;
page counts alone cannot catch clipping, poor wrapping or unclear hierarchy.
Generated files are ignored under output/. Commit sources first, then rebuild
the final wheel and bundle so BUILD.json identifies a clean source commit.

The bundle builder fetches only locked runtime dependency wheels and verifies
their lockfile hashes. It excludes the PDF toolchain and development tools.
All bundled wheels must be platform-independent. Setup uses uv, an installed
Python 3.11+, a local wheelhouse and no index or automatic Python download.

Final outputs:

- output/pdf/: four route packets, two-page field guide, facilitator notes.
- output/rps-event-kit.zip: offline lab distribution with printable handouts.
- output/rps-event-kit/: the same bundle, extracted for smoke testing.

Keep event URL/league/token distribution separate from source and artifacts.
The printed defaults are examples. Test the actual server's upload, validation,
activation and completed-match path before the event.
