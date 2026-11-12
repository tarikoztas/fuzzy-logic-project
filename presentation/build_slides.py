"""Build the presentation from one slide specification (presentation/slides_content.py):
  * presentation/slides.html  (16:9)  ->  presentation/presentation.pdf  (headless Edge/Chrome)
  * presentation/presentation.pptx   (python-pptx), with speaker notes

Numbers on the slides come from the same CSV-based values as the report.

Usage:  python presentation/build_slides.py
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from report.build_report import pdf_pages, print_pdf  # noqa: E402

OUT = ROOT / "presentation"
INK, MUTED, ACCENT, ORANGE = "#1f1f1e", "#6b6a63", "#2a78d6", "#eb6834"

CSS = f"""
@page {{ size: 338.67mm 190.5mm; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: "Segoe UI", Calibri, Arial, sans-serif; color: {INK}; background: #fff; }}
.slide {{ width: 338.67mm; height: 190.5mm; padding: 13mm 17mm 11mm; page-break-after: always; position: relative; overflow: hidden; }}
.slide:last-child {{ page-break-after: auto; }}
h1 {{ font-size: 25pt; margin: 0 0 6mm; font-weight: 600; color: {INK}; }}
h1 .sec {{ display: block; font-size: 10.5pt; font-weight: 600; color: {ACCENT}; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 2mm; }}
.body {{ display: flex; gap: 9mm; height: 140mm; }}
.col {{ flex: 1; min-width: 0; }}
.col.img {{ flex: 1.25; display: flex; flex-direction: column; justify-content: center; align-items: center; }}
.col.img img {{ max-width: 100%; max-height: 128mm; object-fit: contain; }}
.cap {{ font-size: 9.5pt; color: {MUTED}; margin-top: 2mm; text-align: center; }}
ul {{ margin: 0; padding-left: 6mm; }}
li {{ font-size: 15pt; line-height: 1.32; margin-bottom: 2.6mm; }}
li li {{ font-size: 13pt; margin-bottom: 1mm; }}
table {{ border-collapse: collapse; font-size: 11.5pt; width: 100%; }}
th, td {{ border-bottom: 1px solid #ddd; padding: 1.6mm 2.4mm; text-align: center; }}
th {{ border-bottom: 2px solid {INK}; font-weight: 600; }}
td:first-child, th:first-child {{ text-align: left; }}
.foot {{ position: absolute; bottom: 5mm; left: 17mm; right: 17mm; font-size: 8.5pt; color: {MUTED}; display: flex; justify-content: space-between; }}
.title-slide {{ display: flex; flex-direction: column; justify-content: center; height: 100%; }}
.title-slide h1 {{ font-size: 31pt; line-height: 1.15; }}
.title-slide .sub {{ font-size: 15pt; color: {MUTED}; margin-top: 4mm; }}
.big {{ font-size: 40pt; font-weight: 600; color: {ACCENT}; }}
.note {{ color: {ORANGE}; }}
"""


def esc(s: str) -> str:
    return html.escape(s, quote=False).replace("**", "")


def bullets_html(items) -> str:
    out = "<ul>"
    for it in items:
        if isinstance(it, (list, tuple)):
            out += bullets_html(it)
        else:
            out += f"<li>{inline(it)}</li>"
    return out + "</ul>"


def inline(s: str) -> str:
    """Escape, then **bold** -> <b>."""
    parts = html.escape(s, quote=False).split("**")
    return "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts))


def table_html(t) -> str:
    head = "".join(f"<th>{esc(str(c))}</th>" for c in t["columns"])
    rows = "".join("<tr>" + "".join(f"<td>{esc(str(v))}</td>" for v in r) + "</tr>" for r in t["rows"])
    cap = f'<div class="cap">{esc(t.get("caption", ""))}</div>' if t.get("caption") else ""
    return f"<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>{cap}"


def slide_html(i: int, n: int, s: dict) -> str:
    if s.get("kind") == "title":
        return (f'<section class="slide"><div class="title-slide"><h1>{inline(s["title"])}</h1>'
                f'<div class="sub">{inline(s.get("subtitle", ""))}</div></div></section>')
    left = bullets_html(s.get("bullets", []))
    if s.get("table"):
        left += table_html(s["table"])
    right = ""
    if s.get("image"):
        rel = Path("..") / s["image"]
        cap = f'<div class="cap">{esc(s.get("caption", ""))}</div>' if s.get("caption") else ""
        right = f'<div class="col img"><img src="{rel.as_posix()}">{cap}</div>'
    style = ' style="flex:0.8"' if right and s.get("narrow_text") else ""
    sec = f'<span class="sec">{esc(s.get("section", ""))}</span>' if s.get("section") else ""
    return (f'<section class="slide"><h1>{sec}{inline(s["title"])}</h1><div class="body">'
            f'<div class="col"{style}>{left}</div>{right}</div>'
            f'<div class="foot"><span>T. Öztaş — Fuzzy Logic term project</span><span>{i}/{n}</span></div></section>')


def build_html(slides: list[dict]) -> Path:
    body = "".join(slide_html(i + 1, len(slides), s) for i, s in enumerate(slides))
    path = OUT / "slides.html"
    path.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>ASRFCM Reproduction</title>'
                    f"<style>{CSS}</style></head><body>{body}</body></html>", encoding="utf-8")
    return path


def build_pptx(slides: list[dict]) -> Path:
    from pptx import Presentation
    from pptx.util import Inches, Pt

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]

    def add_text(slide, text_items, left, top, width, height, size=20):
        tb = slide.shapes.add_textbox(left, top, width, height)
        tf = tb.text_frame
        tf.word_wrap = True
        first = True

        def add(items, level):
            nonlocal first
            for it in items:
                if isinstance(it, (list, tuple)):
                    add(it, level + 1)
                    continue
                p = tf.paragraphs[0] if first else tf.add_paragraph()
                first = False
                p.text = ("• " if level == 0 else "– ") + it.replace("**", "")
                p.level = level
                p.font.size = Pt(size - 3 * level)
        add(text_items, 0)
        return tb

    for s in slides:
        sl = prs.slides.add_slide(blank)
        if s.get("kind") == "title":
            add_text(sl, [s["title"]], Inches(0.8), Inches(2.4), Inches(11.7), Inches(1.6), 34)
            add_text(sl, [s.get("subtitle", "")], Inches(0.8), Inches(4.2), Inches(11.7), Inches(1.2), 18)
        else:
            t = sl.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(12), Inches(0.9))
            t.text_frame.text = s["title"].replace("**", "")
            t.text_frame.paragraphs[0].font.size = Pt(30)
            t.text_frame.paragraphs[0].font.bold = True
            has_img = bool(s.get("image"))
            text_w = Inches(5.6) if has_img else Inches(12)
            if s.get("bullets"):
                add_text(sl, s["bullets"], Inches(0.6), Inches(1.4), text_w, Inches(3.2 if s.get("table") else 5.6), 18)
            if s.get("table"):
                tbl = s["table"]
                rows, cols = len(tbl["rows"]) + 1, len(tbl["columns"])
                top = Inches(4.3) if s.get("bullets") else Inches(1.5)
                shape = sl.shapes.add_table(rows, cols, Inches(0.6), top, text_w, Inches(0.32 * rows))
                for j, c in enumerate(tbl["columns"]):
                    shape.table.cell(0, j).text = str(c)
                for i, r in enumerate(tbl["rows"], 1):
                    for j, v in enumerate(r):
                        shape.table.cell(i, j).text = str(v)
                for cell in (shape.table.cell(i, j) for i in range(rows) for j in range(cols)):
                    for p in cell.text_frame.paragraphs:
                        p.font.size = Pt(11)
            if has_img:
                img = ROOT / s["image"]
                sl.shapes.add_picture(str(img), Inches(6.5), Inches(1.4), width=Inches(6.4))
        if s.get("notes"):
            sl.notes_slide.notes_text_frame.text = s["notes"]
    path = OUT / "presentation.pptx"
    prs.save(path)
    return path


def main() -> None:
    from presentation.slides_content import slides

    spec = slides()
    html_path = build_html(spec)
    pdf = OUT / "presentation.pdf"
    print_pdf(html_path, pdf)
    print(f"presentation.pdf: {pdf_pages(pdf)} slides")
    print(f"saved {build_pptx(spec).relative_to(ROOT)}")
    notes = OUT / "speaker_notes.md"
    notes.write_text("# Speaker notes\n\n" + "\n\n".join(f"## {i + 1}. {s['title'].replace('**', '')}\n\n{s.get('notes', '')}"
                                                      for i, s in enumerate(spec)), encoding="utf-8")
    print(f"saved {notes.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
