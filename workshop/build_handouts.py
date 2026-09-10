#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<4"
# dependencies = ["pypdf==6.18.0", "eastbridge-rps-client-kit"]
# [tool.uv.sources]
# eastbridge-rps-client-kit = { path = ".." }
# ///
"""Typeset the workshop in the Eastbridge Academy LaTeX house style.

uv run --locked --script workshop/build_handouts.py
Requires pdfLaTeX; all branding assets are included in the source checkout.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess

from pypdf import PdfReader
from rps_house_bots import list_bots

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "output/pdf"
BUILD = ROOT.parent / "output/latex"
ROUTES = ("beginner", "intermediate", "advanced", "expert")
SUBTITLES = {
    "A bot in the arena": "Getting started",
    "What your bot sees": "Inside bot.py",
    "Can you beat random play?": "Randomness and prediction",
    "Practice matches": "Scores and local testing",
    "Route A: find a pattern": "Route A / Beginner",
    "Route B: count the moves": "Route B / Intermediate",
    "Route C: Markov models": "Route C / Advanced",
    "Route D: combine several strategies": "Route D / Expert",
}


def escape(text: str) -> str:
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
                    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
                    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(replacements.get(char, char) for char in text)


def inline(text: str) -> str:
    # Protect code and math before formatting prose; literal quotes and underscores
    # in the participant commands must not be interpreted as typographic markup.
    pieces = re.split(r"(`[^`]+`|\$[^$\n]+\$|\*\*[^*]+\*\*|\*[^*]+\*|https?://[^\s]+)", text)
    result = []
    for piece in pieces:
        if piece.startswith("`") and piece.endswith("`"):
            result.append(r"\code{" + escape(piece[1:-1]) + "}")
        elif piece.startswith("$") and piece.endswith("$"):
            result.append(piece)
        elif piece.startswith("**") and piece.endswith("**"):
            result.append(r"\textbf{" + inline(piece[2:-2]) + "}")
        elif piece.startswith("*") and piece.endswith("*"):
            result.append(r"\emph{" + escape(piece[1:-1]) + "}")
        elif piece.startswith(("https://", "http://")):
            url = piece.rstrip(".,;")
            result.append(r"\url{" + url + "}" + piece[len(url):])
        else:
            # Smart quotation marks in prose only; listings keep straight quotes.
            prose = escape(piece)
            prose = re.sub(r'"([^"\n]+)"', lambda match: r"\enquote{" + match[1] + "}", prose)
            result.append(prose)
    return "".join(result)


def make_table(rows: list[list[str]]) -> str:
    columns = len(rows[0])
    worksheet = any(all(not row[column] for row in rows[1:])
                    for column in range(1, columns))
    if columns == 2:
        spec = r"@{}L{.28\linewidth}Y@{}"
    elif worksheet:
        spec = r"@{}L{.25\linewidth}" + "Y" * (columns - 1) + "@{}"
    else:
        spec = "@{}" + "Y" * columns + "@{}"
    lines = [r"\par\smallskip\begingroup\small", r"\setlength{\tabcolsep}{5pt}",
             r"\renewcommand{\arraystretch}{1.17}", r"\begin{tabularx}{\linewidth}{" + spec + "}", r"\toprule"]
    for index, row in enumerate(rows):
        cells = [inline(cell) for cell in row]
        if index == 0:
            cells = [r"\textbf{" + cell + "}" for cell in cells]
        if worksheet and index > 0:
            cells[0] = r"\rule{0pt}{22pt}" + cells[0]
        lines.append(" & ".join(cells) + r" \\")
        if index == 0:
            lines.append(r"\midrule")
    lines += [r"\bottomrule", r"\end{tabularx}\endgroup\par\smallskip"]
    return "\n".join(lines)


def parse_page(source: str) -> str:
    lines = source.strip().splitlines()
    result = []
    index = 0
    first_paragraph = True
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith("```"):
            language = line[3:]
            code = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                code.append(lines[index])
                index += 1
            if index == len(lines):
                raise ValueError("Unclosed fenced block")
            if language == "math":
                result.append("\\[\n" + "\n".join(code) + "\n\\]")
            else:
                style = {"python": "python", "bash": "shell", "text": "plaincode"}[language]
                options = f"style={style}" + (",numbers=none" if len(code) <= 2 else "")
                result.append(r"\begin{lstlisting}[" + options + "]\n" + "\n".join(code) + "\n" + r"\end{lstlisting}")
        elif line.startswith("# "):
            title = line[2:]
            if title in SUBTITLES:
                display = title.split(": ", 1)[-1].capitalize() if title.startswith("Route ") else title
                result.append(r"\workshoptitle{" + inline(display) + "}{" + inline(SUBTITLES[title]) + "}")
            else:
                result.append(r"\section*{" + inline(title) + "}")
        elif line.startswith("## "):
            heading = line[3:]
            step = re.match(r"((?:Step|Experiment) \d+): (.+)", heading)
            if step:
                result.append(r"\lessonstep{" + inline(step[1]) + "}{" + inline(step[2]) + "}")
            else:
                result.append(r"\subsection*{" + inline(heading) + "}")
        elif line.startswith("| "):
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                row = [value.strip() for value in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", value) for value in row):
                    rows.append(row)
                index += 1
            result.append(make_table(rows))
            continue
        elif line.startswith("> "):
            text = line[2:]
            kind = "summit" if text.startswith(("**Challenge:", "**Paper challenge:")) else "checkpoint"
            result.append(r"\begin{" + kind + "}\n" + inline(text) + "\n" + r"\end{" + kind + "}")
        elif line.startswith("- "):
            items = []
            while index < len(lines) and lines[index].startswith("- "):
                items.append(r"\item " + inline(lines[index][2:]))
                index += 1
            result.append("\\begin{itemize}\n" + "\n".join(items) + "\n\\end{itemize}")
            continue
        else:
            prose = [line]
            while index + 1 < len(lines) and lines[index + 1].strip() and not lines[index + 1].startswith(("#", "|", "```", "> ", "- ")):
                index += 1
                prose.append(lines[index])
            body = inline(" ".join(prose)) + "\n\\par"
            if first_paragraph:
                body = "\\begin{context}\n" + body + "\n\\end{context}"
                first_paragraph = False
            result.append(body)
        index += 1
    return "\n\n".join(result)


def compile_pdf(stem: str, label: str, body: str, expected_pages: int, *, landscape: bool = False) -> None:
    folder = BUILD / stem
    folder.mkdir(parents=True, exist_ok=True)
    for asset in (ROOT / "latex").iterdir():
        shutil.copy2(asset, folder / asset.name)
    options = "11pt,landscape" if landscape else "11pt"
    preamble = (r"\documentclass[" + options + "]{article}\n"
                + r"\newcommand{\routelabel}{" + escape(label) + "}\n"
                + "\\usepackage{eastbridge-handout}\n"
                + ("\\geometry{landscape,left=.75in,right=.75in,top=1in,bottom=.75in}\n"
                   "\\setlength{\\headwidth}{\\textwidth}\n" if landscape else "")
                + r"\hypersetup{pdftitle={RPS Workshop: " + escape(label) + "}}\n"
                + "\\begin{document}\n\\thispagestyle{plain}\n")
    tex = folder / f"{stem}.tex"
    tex.write_text(preamble + body + "\n\\end{document}\n")
    for _ in range(2):
        result = subprocess.run(["pdflatex", "-no-shell-escape", "-halt-on-error", "-interaction=nonstopmode", tex.name],
                                cwd=folder, capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise RuntimeError(f"pdfLaTeX failed for {stem}:\n{result.stdout[-3500:]}")
    log = (folder / f"{stem}.log").read_text()
    warnings = re.findall(r"(?:Overfull|Underfull) \\[hv]box[^\n]*", log)
    pdf = folder / f"{stem}.pdf"
    count = len(PdfReader(pdf).pages)
    problems = [warning for warning in warnings if warning.startswith("Overfull")]
    problems += re.findall(r"Missing character:[^\n]*", log)
    if count != expected_pages:
        problems.append(f"Expected {expected_pages} planned pages; rendered {count}")
    if problems:
        raise RuntimeError(f"Layout check failed for {stem}:\n" + "\n".join(problems)
                           + f"\nInspect {pdf} and {tex.with_suffix('.log')}")
    shutil.copy2(pdf, OUTPUT / pdf.name)
    print(f"{stem}: {count} pages (target {expected_pages}); {len(warnings)} box warnings")
    for warning in warnings:
        print("  " + warning)


def packet(route: str, number: int) -> None:
    common = (ROOT / "common.md").read_text().split("---page---")
    pages = common + (ROOT / f"{route}.md").read_text().split("---page---")
    compile_pdf(f"0{number}-{route}", route.title(), "\n\\clearpage\n".join(parse_page(page) for page in pages), len(pages))


def field_guide() -> None:
    order = {"Beginner": 0, "Intermediate": 1, "Advanced": 2, "Expert": 3, "Baseline": 4}
    bots = sorted(list_bots(), key=lambda bot: (order[bot.level], bot.slug))
    pages = []
    for page in range(2):
        lines = [r"\workshoptitle{Meet the house bots}{" + ("Patterns and personalities" if page == 0 else "Memory, adaptation and a baseline") + "}",
                 r"{\small The route labels point to the relevant exercises. Try the hints below if you get stuck predicting a bot.\par}",
                 r"\smallskip\begingroup\small\setlength{\tabcolsep}{7pt}\renewcommand{\arraystretch}{1.2}",
                 r"\begin{tabularx}{\linewidth}{@{}L{.21\linewidth}L{.31\linewidth}Y@{}}",
                 r"\toprule\textbf{Bot / route} & \textbf{What it does} & \textbf{An experiment to try} \\\midrule"]
        for bot in bots[page * 8:(page + 1) * 8]:
            name = "Cycle RPS" if bot.slug == "cycle_rps" else bot.display_name
            card = r"\textbf{" + escape(name) + r"}\newline{\scriptsize\texttt{" + escape(bot.slug) + r"}}\newline{\footnotesize\color{myblue}" + escape(bot.level) + "}"
            lines.append(card + " & " + inline(bot.description) + " & " + inline(bot.hint) + r" \\[4pt]")
            if bot != bots[page * 8:(page + 1) * 8][-1]:
                lines.append(r"\addlinespace[3pt]")
        lines += [r"\bottomrule\end{tabularx}\endgroup"]
        pages.append("\n".join(lines))
    compile_pdf("05-house-bot-field-guide", "House bot field guide", "\n\\clearpage\n".join(pages), 2, landscape=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=(*ROUTES, "field-guide", "facilitator"))
    args = parser.parse_args()
    if not shutil.which("pdflatex"):
        raise SystemExit("pdfLaTeX is required. See workshop/README.md for TeX Live installation.")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for number, route in enumerate(ROUTES, 1):
        if args.only in (None, route):
            packet(route, number)
    if args.only in (None, "field-guide"):
        field_guide()
    if args.only in (None, "facilitator"):
        pages = (ROOT / "facilitator.md").read_text().split("---page---")
        compile_pdf("06-facilitator-notes", "Facilitator notes", "\n\\clearpage\n".join(parse_page(page) for page in pages), len(pages))


if __name__ == "__main__":
    main()
