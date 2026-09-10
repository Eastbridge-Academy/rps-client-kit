#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<4"
# dependencies = ["pypdf==6.18.0"]
# ///
"""Compile the native LaTeX handouts and check their planned print layouts.

uv run --locked --script workshop/build_handouts.py
Requires pdfLaTeX; all sources and branding assets live in workshop/latex/.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "output/pdf"
BUILD = ROOT.parent / "output/latex"
DOCUMENTS = {
    "setup": ("00-setup", 4),
    "beginner": ("01-beginner", 5),
    "intermediate": ("02-intermediate", 6),
    "advanced": ("03-advanced", 6),
    "expert": ("04-expert", 7),
    "field-guide": ("05-house-bot-field-guide", 2),
    "facilitator": ("06-facilitator-notes", 3),
}


def compile_pdf(stem: str, expected_pages: int) -> None:
    folder = BUILD / stem
    shutil.copytree(ROOT / "latex", folder, dirs_exist_ok=True)
    tex = folder / f"{stem}.tex"
    for _ in range(2):
        result = subprocess.run(
            ["pdflatex", "-no-shell-escape", "-halt-on-error",
             "-interaction=nonstopmode", tex.name],
            cwd=folder, capture_output=True, text=True, timeout=60,
        )
        if result.returncode:
            raise RuntimeError(f"pdfLaTeX failed for {stem}:\n{result.stdout[-3500:]}")
    log = tex.with_suffix(".log").read_text()
    warnings = re.findall(r"(?:Overfull|Underfull) \\[hv]box[^\n]*", log)
    pdf = tex.with_suffix(".pdf")
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=DOCUMENTS)
    args = parser.parse_args()
    if not shutil.which("pdflatex"):
        raise SystemExit("pdfLaTeX is required. See workshop/README.md for TeX Live installation.")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, (stem, pages) in DOCUMENTS.items():
        if args.only in (None, name):
            compile_pdf(stem, pages)


if __name__ == "__main__":
    main()
