"""Build the printable event packets from reviewable Markdown sources.

uv run --group workshop python workshop/build_handouts.py
"""

from __future__ import annotations

from functools import partial
from html import escape
from pathlib import Path
import re

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Preformatted, Spacer, Table, TableStyle, PageBreak

from rps_house_bots import list_bots

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "output/pdf"
INK = colors.HexColor("#19343B")
TEAL = colors.HexColor("#196B64")
MUTED = colors.HexColor("#526466")
PALE = colors.HexColor("#EFF5F2")
GOLD = colors.HexColor("#9B7430")
STYLES = {
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10.2, leading=14, textColor=INK, spaceAfter=8),
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=23, leading=26, textColor=INK, spaceAfter=13, keepWithNext=True),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=TEAL, spaceBefore=5, spaceAfter=7, keepWithNext=True),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=8.8, leading=11.7, textColor=INK, backColor=colors.HexColor("#F4F5F4"), borderPadding=7, spaceBefore=3, spaceAfter=11),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=9, leading=12, textColor=INK, alignment=TA_LEFT),
    "small": ParagraphStyle("small", fontName="Helvetica", fontSize=9.2, leading=12.5, textColor=MUTED),
}


def inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" size="9">\1</font>', text)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)


def paragraph(text: str, style: str = "body") -> Paragraph:
    return Paragraph(inline(text).replace("\n", "<br/>"), STYLES[style])


def table(rows: list[list[str]], width: float, widths: list[float] | None = None) -> Table:
    cells = [[paragraph(text, "cell") for text in row] for row in rows]
    if widths is None:
        if len(rows[0]) == 2:
            widths = [width * .29, width * .71]
        else:
            first = width * .25
            widths = [first] + [(width - first) / (len(rows[0]) - 1)] * (len(rows[0]) - 1)
    result = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT", spaceBefore=4, spaceAfter=12)
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("LINEBELOW", (0, 0), (-1, 0), .7, TEAL),
        ("LINEBELOW", (0, 1), (-1, -1), .3, colors.HexColor("#D9E3DF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return result


def parse_page(source: str, width: float) -> list:
    lines = source.strip().splitlines()
    result = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith("```"):
            code = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                code.append(lines[index])
                index += 1
            result.append(Preformatted("\n".join(code), STYLES["code"], maxLineLength=91))
        elif line.startswith("# "):
            result.append(paragraph(line[2:], "h1"))
        elif line.startswith("## "):
            result.append(paragraph(line[3:], "h2"))
        elif line.startswith("| "):
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                row = [value.strip() for value in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", value) for value in row):
                    rows.append(row)
                index += 1
            result.append(table(rows, width))
            continue
        elif line.startswith("> "):
            box = Table([[paragraph(line[2:])]], colWidths=[width], spaceBefore=3, spaceAfter=11)
            box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE),
                                    ("LINEBEFORE", (0, 0), (0, -1), 2, TEAL),
                                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
            result.append(box)
        elif line.startswith("- "):
            result.append(paragraph("- " + line[2:]))
        else:
            prose = [line]
            while index + 1 < len(lines) and lines[index + 1].strip() and not lines[index + 1].startswith(("#", "|", "```", "> ", "- ")):
                index += 1
                prose.append(lines[index])
            result.append(paragraph(" ".join(prose)))
        index += 1
    return result


def furniture(canvas: Canvas, doc, label: str) -> None:
    width, height = doc.pagesize
    canvas.saveState()
    canvas.setFillColor(TEAL)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(doc.leftMargin, height - 31, "EASTBRIDGE  /  ARENA")
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - doc.rightMargin, height - 31, label)
    canvas.setStrokeColor(colors.HexColor("#D9E3DF"))
    canvas.setLineWidth(.4)
    canvas.line(doc.leftMargin, 32, width - doc.rightMargin, 32)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(doc.leftMargin, 21, "RPS LAB  |  CLIENT KIT 0.3.0")
    canvas.drawRightString(width - doc.rightMargin, 21, str(doc.page))
    canvas.restoreState()


def build(filename: str, label: str, pages: list[str]) -> None:
    path = OUTPUT / filename
    doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=46, rightMargin=46,
                            topMargin=56, bottomMargin=45, title=label, author="Eastbridge Academy")
    flow = []
    for index, page in enumerate(pages):
        if index:
            flow.append(PageBreak())
        flow.extend(parse_page(page, doc.width))
    decorate = partial(furniture, label=label)
    doc.build(flow, onFirstPage=decorate, onLaterPages=decorate, canvasmaker=partial(Canvas, invariant=1))
    count = len(PdfReader(path).pages)
    print(f"{path.name}: {count} pages (planned {len(pages)})")
    if count != len(pages):
        raise RuntimeError(f"Unexpected overflow in {path.name}: review the source page lengths.")


def field_guide() -> None:
    path = OUTPUT / "05-house-bot-field-guide.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=landscape(letter), leftMargin=42, rightMargin=42,
                            topMargin=52, bottomMargin=43, title="House bot field guide", author="Eastbridge Academy")
    order = {"Beginner": 0, "Intermediate": 1, "Advanced": 2, "Expert": 3, "Baseline": 4}
    bots = sorted(list_bots(), key=lambda bot: (order[bot.level], bot.slug))
    flow = []
    for page in range(2):
        if page:
            flow.append(PageBreak())
        flow.append(paragraph(f"Meet the house bots  /  {page + 1}", "h1"))
        flow.append(paragraph("Rules and hints are open. Route labels suggest a teaching path, not a universal strength ranking.", "small"))
        flow.append(Spacer(1, 9))
        rows = [["**Bot / route**", "**What it does**", "**An experiment to try**"]]
        for bot in bots[page * 8:(page + 1) * 8]:
            rows.append([f"**{bot.display_name}**\n`{bot.slug}`\n{bot.level}", bot.description, bot.hint])
        grid = table(rows, doc.width, [128, 226, doc.width - 354])
        flow.append(grid)
    decorate = partial(furniture, label="HOUSE FIELD  /  PRINT BOTH SIDES")
    doc.build(flow, onFirstPage=decorate, onLaterPages=decorate, canvasmaker=partial(Canvas, invariant=1))
    count = len(PdfReader(path).pages)
    print(f"{path.name}: {count} pages")
    if count != 2:
        raise RuntimeError("Field guide overflowed its two-page format.")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    common = (ROOT / "common.md").read_text().split("---page---")
    for number, route in enumerate(("beginner", "intermediate", "advanced", "expert"), 1):
        pages = common + (ROOT / f"{route}.md").read_text().split("---page---")
        build(f"0{number}-{route}.pdf", f"RPS WORKSHOP  /  {route.upper()}", pages)
    build("06-facilitator-notes.pdf", "RPS WORKSHOP  /  FACILITATOR", (ROOT / "facilitator.md").read_text().split("---page---"))
    field_guide()


if __name__ == "__main__":
    main()
