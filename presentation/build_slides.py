"""Build the presentation from one slide specification (presentation/slides_content.py):
  * presentation/slides[_tr].html (16:9) -> presentation/presentation[_tr].pdf  (headless Edge/Chrome)
  * presentation/presentation[_tr].pptx (python-pptx), with speaker notes
  * presentation/speaker_notes[_tr].md

Numbers on the slides come from the same CSV-based values as the report.

Layout: a header (section label + title), a content area in which the content block
is centred vertically (and the columns are centred against each other), and a footer.
The same geometry is used for the PPTX, so both outputs look alike.

Slide keys: kind ("title"), section, title, bullets (nested lists = sub-bullets),
table {columns, rows, caption}, image, caption, callouts [(value, label), ...],
narrow_text (text column narrower than the image), notes.

Usage:  python presentation/build_slides.py [--lang en|tr]
"""
from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from report.build_report import pdf_pages, print_pdf  # noqa: E402

OUT = ROOT / "presentation"
INK, MUTED, ACCENT, ACCENT_DARK, ORANGE = "#1f1f1e", "#5f5e58", "#2a78d6", "#174a8b", "#eb6834"
TINT, RULE, ZEBRA = "#eaf2fc", "#d9d8d2", "#f6f6f3"

FOOTER = {"en": "T. Öztaş · Fuzzy Logic term project · İÜC Computer Engineering",
          "tr": "T. Öztaş · Bulanık Mantık dönem projesi · İÜC Bilgisayar Mühendisliği"}

# geometry (mm) shared by HTML and PPTX
W, H = 338.67, 190.5
PAD_X, HEAD_TOP, BODY_TOP, BODY_BOTTOM = 17.0, 9.0, 38.0, 14.0

CSS = f"""
@page {{ size: {W}mm {H}mm; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: "Segoe UI", Calibri, Arial, sans-serif; color: {INK}; background: #fff; }}
.slide {{ width: {W}mm; height: {H}mm; position: relative; overflow: hidden; page-break-after: always; background: #fff; }}
.slide:last-child {{ page-break-after: auto; }}
.topbar {{ position: absolute; top: 0; left: 0; right: 0; height: 2.6mm; background: {ACCENT}; }}
.topbar::after {{ content: ""; position: absolute; right: 0; top: 0; width: 30%; height: 100%; background: {ORANGE}; }}
.head {{ position: absolute; top: {HEAD_TOP}mm; left: {PAD_X}mm; right: {PAD_X}mm; }}
.sec {{ display: inline-block; font-size: 10pt; font-weight: 700; color: {ACCENT}; letter-spacing: .08em;
        text-transform: uppercase; margin-bottom: 1.6mm; }}
.head h1 {{ font-size: 24pt; margin: 0; font-weight: 650; line-height: 1.15; color: {INK}; }}
.head .rule {{ width: 22mm; height: 1.1mm; background: {ACCENT}; margin-top: 3mm; border-radius: .6mm; }}
.content {{ position: absolute; top: {BODY_TOP}mm; bottom: {BODY_BOTTOM}mm; left: {PAD_X}mm; right: {PAD_X}mm;
            display: flex; flex-direction: column; justify-content: center; }}
.row {{ display: flex; gap: 10mm; align-items: center; min-height: 0; }}
.col {{ flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; gap: 4mm; }}
.col.narrow {{ flex: 0.8; }}
.col.only {{ max-width: 262mm; margin: 0 auto; }}
.col.only > ul > li {{ font-size: 17.5pt; margin-bottom: 3.4mm; }}
.col.only li li {{ font-size: 14pt; }}
.col.img {{ flex: 1.25; align-items: center; }}
.col.img img {{ max-width: 100%; max-height: 118mm; object-fit: contain; }}
.cap {{ font-size: 9.5pt; color: {MUTED}; margin-top: 1.5mm; text-align: center; }}
ul {{ margin: 0; padding-left: 6mm; }}
li {{ font-size: 15pt; line-height: 1.3; margin-bottom: 2.4mm; }}
li::marker {{ color: {ACCENT}; }}
li li {{ font-size: 12.5pt; margin-bottom: 1mm; color: {MUTED}; }}
li li::marker {{ color: {MUTED}; }}
b {{ color: {ACCENT_DARK}; }}
table {{ border-collapse: separate; border-spacing: 0; font-size: 11.5pt; width: 100%; border-radius: 2mm; overflow: hidden;
         border: 1px solid {RULE}; }}
th {{ background: {TINT}; color: {ACCENT_DARK}; font-weight: 700; padding: 2mm 2.6mm; text-align: center;
      border-bottom: 1.5px solid {ACCENT}; }}
td {{ padding: 1.6mm 2.6mm; text-align: center; border-bottom: 1px solid {RULE}; }}
tbody tr:nth-child(even) td {{ background: {ZEBRA}; }}
tbody tr:last-child td {{ border-bottom: none; }}
td:first-child, th:first-child {{ text-align: left; font-weight: 600; }}
.callouts {{ display: flex; gap: 6mm; }}
.callout {{ flex: 1; background: {TINT}; border-left: 2mm solid {ACCENT}; border-radius: 2mm; padding: 3mm 4mm; }}
.callout.warn {{ background: #fdeee6; border-left-color: {ORANGE}; }}
.callout .v {{ font-size: 25pt; font-weight: 700; color: {ACCENT_DARK}; line-height: 1.1; }}
.callout.warn .v {{ color: #b2461b; }}
.callout .l {{ font-size: 10.5pt; color: {MUTED}; margin-top: 1mm; line-height: 1.25; }}
.foot {{ position: absolute; bottom: 4.5mm; left: {PAD_X}mm; right: {PAD_X}mm; font-size: 8.5pt; color: {MUTED};
         display: flex; justify-content: space-between; border-top: 1px solid {RULE}; padding-top: 1.8mm; }}
.title-slide {{ position: absolute; inset: 0; display: flex; }}
.title-slide .band {{ width: 14mm; background: linear-gradient({ACCENT}, {ACCENT_DARK}); }}
.title-slide .band2 {{ width: 3mm; background: {ORANGE}; }}
.title-slide .inner {{ flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 0 26mm 0 20mm; }}
.title-slide .kicker {{ font-size: 12pt; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: {ACCENT}; }}
.title-slide h1 {{ font-size: 30pt; line-height: 1.18; margin: 4mm 0 6mm; font-weight: 650; }}
.title-slide .sub {{ font-size: 14pt; color: {MUTED}; line-height: 1.5; border-top: 1px solid {RULE}; padding-top: 5mm; }}
"""


def inline(s: str) -> str:
    """Escape, then **bold** -> <b>."""
    parts = html.escape(str(s), quote=False).split("**")
    return "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts))


def bullets_html(items) -> str:
    out = "<ul>"
    for it in items:
        out += bullets_html(it) if isinstance(it, (list, tuple)) else f"<li>{inline(it)}</li>"
    return out + "</ul>"


def table_html(t) -> str:
    head = "".join(f"<th>{inline(c)}</th>" for c in t["columns"])
    rows = "".join("<tr>" + "".join(f"<td>{inline(v)}</td>" for v in r) + "</tr>" for r in t["rows"])
    cap = f'<div class="cap">{inline(t["caption"])}</div>' if t.get("caption") else ""
    return f"<div><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>{cap}</div>"


def callouts_html(cs) -> str:
    boxes = "".join(f'<div class="callout{" warn" if len(c) > 2 and c[2] == "warn" else ""}">'
                    f'<div class="v">{inline(c[0])}</div><div class="l">{inline(c[1])}</div></div>' for c in cs)
    return f'<div class="callouts">{boxes}</div>'


def slide_html(i: int, n: int, s: dict, lang: str) -> str:
    if s.get("kind") == "title":
        return (f'<section class="slide"><div class="title-slide"><div class="band"></div><div class="band2"></div>'
                f'<div class="inner"><div class="kicker">{inline(s.get("kicker", ""))}</div><h1>{inline(s["title"])}</h1>'
                f'<div class="sub">{s.get("subtitle_html") or inline(s.get("subtitle", ""))}</div></div></div></section>')
    text = ""
    if s.get("bullets"):
        text += bullets_html(s["bullets"])
    if s.get("callouts"):
        text += callouts_html(s["callouts"])
    if s.get("table"):
        text += table_html(s["table"])
    img = ""
    if s.get("image"):
        rel = Path("..") / s["image"]
        cap = f'<div class="cap">{inline(s["caption"])}</div>' if s.get("caption") else ""
        img = f'<div class="col img"><img src="{rel.as_posix()}">{cap}</div>'
    tcls = "col narrow" if img and s.get("narrow_text") else ("col" if img else "col only")
    textcol = f'<div class="{tcls}">{text}</div>' if text else ""
    sec = f'<div class="sec">{inline(s.get("section", ""))}</div>' if s.get("section") else ""
    return (f'<section class="slide"><div class="topbar"></div>'
            f'<div class="head">{sec}<h1>{inline(s["title"])}</h1><div class="rule"></div></div>'
            f'<div class="content"><div class="row">{textcol}{img}</div></div>'
            f'<div class="foot"><span>{FOOTER[lang]}</span><span>{i} / {n}</span></div></section>')


def build_html(slides: list[dict], lang: str) -> Path:
    body = "".join(slide_html(i + 1, len(slides), s, lang) for i, s in enumerate(slides))
    suffix = "" if lang == "en" else f"_{lang}"
    path = OUT / f"slides{suffix}.html"
    path.write_text(f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>ASRFCM Reproduction</title>'
                    f"<style>{CSS}</style></head><body>{body}</body></html>", encoding="utf-8")
    return path


# ----------------------------------------------------------------------------- PPTX
def _rgb(hexs: str):
    from pptx.dml.color import RGBColor
    return RGBColor.from_string(hexs.lstrip("#"))


def _plain(s) -> str:
    return str(s).replace("**", "")


def _lines(items, chars: int) -> float:
    """Rough number of rendered lines of a bullet list for a text box `chars` characters wide."""
    n = 0.0
    for it in items:
        if isinstance(it, (list, tuple)):
            n += _lines(it, int(chars * 1.15)) * 0.85
        else:
            n += max(1, -(-len(_plain(it)) // chars)) + 0.25
    return n


def _row_heights(t: dict, w: float) -> list[float]:
    """Row heights (mm) of a PPTX table: wrapped lines per cell at 11 pt (~1.95 mm per character)."""
    cols = len(t["columns"])
    cw = w / cols - 3.0
    hs = []
    for r in [t["columns"]] + list(t["rows"]):
        lines = max(max(1, -(-len(_plain(v)) * 1.95 // cw)) for v in r)
        hs.append(3.4 + 4.8 * lines)
    return hs


def build_pptx(slides: list[dict], lang: str) -> Path:
    from PIL import Image
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    from pptx.util import Emu, Mm, Pt

    prs = Presentation()
    prs.slide_width, prs.slide_height = Mm(W), Mm(H)
    blank = prs.slide_layouts[6]
    font = "Segoe UI"

    def box(sl, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE):
        shp = sl.shapes.add_shape(shape, Mm(x), Mm(y), Mm(w), Mm(h))
        if fill:
            shp.fill.solid(); shp.fill.fore_color.rgb = _rgb(fill)
        else:
            shp.fill.background()
        if line:
            shp.line.color.rgb = _rgb(line)
        else:
            shp.line.fill.background()
        shp.shadow.inherit = False
        return shp

    def text(sl, x, y, w, h, runs, size, color=INK, bold=False, anchor=MSO_ANCHOR.TOP, align=PP_ALIGN.LEFT):
        tb = sl.shapes.add_textbox(Mm(x), Mm(y), Mm(w), Mm(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = Mm(1)
        p = tf.paragraphs[0]
        p.alignment = align
        _runs(p, runs, size, color, bold)
        return tb

    def _runs(p, s, size, color, bold):
        for k, part in enumerate(str(s).split("**")):
            if not part:
                continue
            r = p.add_run()
            r.text = part
            r.font.size, r.font.name = Pt(size), font
            r.font.bold = bold or bool(k % 2)
            r.font.color.rgb = _rgb(ACCENT_DARK if k % 2 and color == INK else color)

    def bullets(sl, items, x, y, w, h, size=17):
        tb = sl.shapes.add_textbox(Mm(x), Mm(y), Mm(w), Mm(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        first = [True]

        def add(its, level):
            for it in its:
                if isinstance(it, (list, tuple)):
                    add(it, level + 1); continue
                p = tf.paragraphs[0] if first[0] else tf.add_paragraph()
                first[0] = False
                p.space_after = Pt(5 if level == 0 else 2)
                mark = p.add_run()
                mark.text = ("●  " if level == 0 else "–  ")
                mark.font.size, mark.font.name = Pt(size - 6 if level == 0 else size - 3), font
                mark.font.color.rgb = _rgb(ACCENT if level == 0 else MUTED)
                if level:
                    p.level = 1
                _runs(p, it, size - 3 * level, INK if level == 0 else MUTED, False)
        add(items, 0)
        return tb

    def table(sl, t, x, y, w):
        rows, cols = len(t["rows"]) + 1, len(t["columns"])
        hs = _row_heights(t, w)
        shp = sl.shapes.add_table(rows, cols, Mm(x), Mm(y), Mm(w), Mm(sum(hs)))
        tbl = shp.table
        for i, h in enumerate(hs):
            tbl.rows[i].height = Mm(h)
        for j in range(cols):
            tbl.columns[j].width = Emu(int(Mm(w) / cols))
        for i in range(rows):
            for j in range(cols):
                c = tbl.cell(i, j)
                val = t["columns"][j] if i == 0 else t["rows"][i - 1][j]
                c.text = ""
                p = c.text_frame.paragraphs[0]
                p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
                _runs(p, val, 11, ACCENT_DARK if i == 0 else INK, i == 0 or j == 0)
                c.vertical_anchor = MSO_ANCHOR.MIDDLE
                c.margin_top = c.margin_bottom = Mm(0.8)
                c.fill.solid()
                c.fill.fore_color.rgb = _rgb(TINT if i == 0 else (ZEBRA if i % 2 == 0 else "#ffffff"))
        return sum(hs)

    for idx, s in enumerate(slides, 1):
        sl = prs.slides.add_slide(blank)
        if s.get("kind") == "title":
            box(sl, 0, 0, 14, H, ACCENT)
            box(sl, 14, 0, 3, H, ORANGE)
            text(sl, 37, 38, W - 63, 10, s.get("kicker", "").upper(), 13, ACCENT, True)
            text(sl, 37, 50, W - 63, 60, s["title"], 30, INK, True, MSO_ANCHOR.MIDDLE)
            box(sl, 37, 116, W - 63, 0.4, RULE)
            text(sl, 37, 120, W - 63, 40, _plain(s.get("subtitle", "")), 14, MUTED)
        else:
            box(sl, 0, 0, W * 0.7, 2.6, ACCENT)
            box(sl, W * 0.7, 0, W * 0.3, 2.6, ORANGE)
            if s.get("section"):
                text(sl, PAD_X, HEAD_TOP - 1, 200, 7, _plain(s["section"]).upper(), 10, ACCENT, True)
            text(sl, PAD_X, HEAD_TOP + 5, W - 2 * PAD_X, 14, s["title"], 24, INK, True)
            box(sl, PAD_X + 1, HEAD_TOP + 21.5, 22, 1.1, ACCENT)
            box(sl, PAD_X, H - 8.6, W - 2 * PAD_X, 0.3, RULE)
            text(sl, PAD_X, H - 8, 200, 6, FOOTER[lang], 8.5, MUTED)
            text(sl, W - PAD_X - 30, H - 8, 30, 6, f"{idx} / {len(slides)}", 8.5, MUTED, align=PP_ALIGN.RIGHT)

            top, bottom = BODY_TOP, H - BODY_BOTTOM
            area_h = bottom - top
            has_img = bool(s.get("image"))
            full_w = W - 2 * PAD_X
            if has_img:
                tw = full_w * (0.8 / 2.05 if s.get("narrow_text") else 1 / 2.25)
                if not (s.get("bullets") or s.get("table") or s.get("callouts")):
                    tw = 0
                iw_area = full_w - tw - (10 if tw else 0)
            else:
                tw, iw_area = min(full_w, 262.0), 0
            # estimate the height of the text column, then centre it vertically
            parts = []
            only = not has_img
            fs = 19 if only else 17
            chars = max(20, int(tw / (3.05 if only else 2.75)))
            x0 = PAD_X + (full_w - tw) / 2 if only else PAD_X
            if s.get("bullets"):
                parts.append(("bullets", min(area_h, _lines(s["bullets"], chars) * (8.6 if only else 7.6) + 2)))
            if s.get("callouts"):
                parts.append(("callouts", 24))
            if s.get("table"):
                parts.append(("table", sum(_row_heights(s["table"], tw)) + (6 if s["table"].get("caption") else 0)))
            gap = 4
            total = sum(h for _, h in parts) + gap * max(0, len(parts) - 1)
            y = top + max(0, (area_h - total) / 2)
            for kind, h in parts:
                if kind == "bullets":
                    bullets(sl, s["bullets"], x0, y, tw, h, fs)
                elif kind == "callouts":
                    cs = s["callouts"]
                    cw = (tw - 6 * (len(cs) - 1)) / len(cs)
                    for k, c in enumerate(cs):
                        warn = len(c) > 2 and c[2] == "warn"
                        cx = x0 + k * (cw + 6)
                        box(sl, cx, y, cw, h, "#fdeee6" if warn else TINT)
                        box(sl, cx, y, 2, h, ORANGE if warn else ACCENT)
                        text(sl, cx + 4, y + 2, cw - 6, 11, c[0], 22, "#b2461b" if warn else ACCENT_DARK, True)
                        text(sl, cx + 4, y + 13, cw - 6, h - 13, _plain(c[1]), 10, MUTED)
                else:
                    th = table(sl, s["table"], x0, y, tw)
                    if s["table"].get("caption"):
                        text(sl, x0, y + th + 0.5, tw, 6, _plain(s["table"]["caption"]), 9, MUTED,
                             align=PP_ALIGN.CENTER)
                y += h + gap
            if has_img:
                img_path = ROOT / s["image"]
                with Image.open(img_path) as im:
                    ar = im.height / im.width
                cap_h = 7 if s.get("caption") else 0
                iw = iw_area
                ih = iw * ar
                if ih > area_h - cap_h:
                    ih = area_h - cap_h
                    iw = ih / ar
                ix = PAD_X + (tw + 10 if tw else 0) + (iw_area - iw) / 2
                iy = top + (area_h - ih - cap_h) / 2
                sl.shapes.add_picture(str(img_path), Mm(ix), Mm(iy), Mm(iw), Mm(ih))
                if s.get("caption"):
                    text(sl, ix - 10, iy + ih + 0.5, iw + 20, 6, _plain(s["caption"]), 9, MUTED, align=PP_ALIGN.CENTER)
        if s.get("notes"):
            sl.notes_slide.notes_text_frame.text = s["notes"]
    suffix = "" if lang == "en" else f"_{lang}"
    path = OUT / f"presentation{suffix}.pptx"
    prs.save(path)
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["en", "tr"], default="en")
    lang = ap.parse_args().lang
    from presentation.slides_content import slides

    spec = slides(lang)
    suffix = "" if lang == "en" else f"_{lang}"
    html_path = build_html(spec, lang)
    pdf = OUT / f"presentation{suffix}.pdf"
    print_pdf(html_path, pdf)
    print(f"{pdf.name}: {pdf_pages(pdf)} slides")
    print(f"saved {build_pptx(spec, lang).relative_to(ROOT)}")
    head = "# Speaker notes" if lang == "en" else "# Konuşmacı notları"
    notes = OUT / f"speaker_notes{suffix}.md"
    notes.write_text(head + "\n\n" + "\n\n".join(
        f"## {i + 1}. {_plain(s['title'])}\n\n{s.get('notes', '')}" for i, s in enumerate(spec)), encoding="utf-8")
    print(f"saved {notes.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
