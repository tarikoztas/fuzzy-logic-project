"""Build the report: fill report_template.html (+ report_results_template.html) with
numbers and tables computed from results/tables/*.csv, write report.html, print
it to report.pdf with a headless Chromium browser (Edge or Chrome), check the
page count, and update the result blocks of README.md.

No number in the report body is typed by hand: every {{placeholder}} is computed
here from a CSV produced by the experiment scripts (paper-reported values come
from results/tables/paper_reported_*.csv and are labelled as such).

The Turkish version (--lang tr) uses report_template_tr.html and report_results_template_tr.html
with the same placeholders and the same numbers, and writes report_tr.html / report_tr.pdf.

Usage:  python report/build_report.py [--lang en|tr] [--no-pdf]
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

REPORT = ROOT / "report"
TABLES = ROOT / "results" / "tables"
BROWSERS = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "msedge", "google-chrome", "chromium", "chromium-browser"]


def csv(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLES / name)


def f2(x: float) -> str:
    return f"{x:.2f}"


def html_table(df: pd.DataFrame, caption: str, wide: bool = False, left_cols: int = 1) -> str:
    cls = ' class="wide"' if wide else ""
    head = "".join(f'<th{" class=\"l\"" if i < left_cols else ""}>{c}</th>' for i, c in enumerate(df.columns))
    body = ""
    for _, r in df.iterrows():
        body += "<tr>" + "".join(f'<td{" class=\"l\"" if i < left_cols else ""}>{v}</td>'
                                 for i, v in enumerate(r.values)) + "</tr>"
    return f"<table{cls}><caption>{caption}</caption><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def mean_std(s: pd.Series) -> str:
    return f"{s.mean():.2f} ± {s.std(ddof=0):.2f}"


def browser() -> str | None:
    for b in BROWSERS:
        if Path(b).exists() or shutil.which(b):
            return b
    return None


def print_pdf(html: Path, pdf: Path) -> None:
    exe = browser()
    if exe is None:
        raise SystemExit("no Edge/Chrome found for PDF printing")
    subprocess.run([exe, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--no-margins",
                    f"--print-to-pdf={pdf}", html.as_uri()], check=True, capture_output=True, timeout=180)


def pdf_pages(pdf: Path) -> int:
    data = pdf.read_bytes()
    return len(re.findall(rb"/Type\s*/Page[^s]", data))


def render(template: str, values: dict[str, str]) -> str:
    def sub(m):
        key = m.group(1)
        if key not in values:
            raise KeyError(f"no value for placeholder {{{{{key}}}}}")
        return str(values[key])
    return re.sub(r"\{\{([A-Za-z0-9_]+)\}\}", sub, template)


def replace_block(text: str, name: str, content: str) -> str:
    pat = re.compile(rf"(<!-- BEGIN:{name} -->)(.*?)(<!-- END:{name} -->)", re.S)
    return pat.sub(lambda m: m.group(1) + "\n" + content + "\n" + m.group(3), text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--lang", choices=["en", "tr"], default="en")
    args = ap.parse_args()
    from report.report_values import compute  # local module with all values and tables

    sfx = "" if args.lang == "en" else f"_{args.lang}"
    values, readme_blocks = compute(args.lang)
    tpl = (REPORT / f"report_template{sfx}.html").read_text(encoding="utf-8")
    rest = (REPORT / f"report_results_template{sfx}.html").read_text(encoding="utf-8")
    values["RESULTS_AND_REST"] = render(rest, values)
    html = render(tpl, values)
    from report.report_values_extra import renumber_citations
    html = renumber_citations(html)
    if args.lang == "tr":
        # Turkish typography: the percent sign precedes the number (%5, %79.85)
        html = re.sub(r"(?<![\w%.])(\d[\d.,/–]*\d|\d)&nbsp;%", r"%\1", html)
        html = html.replace("Table&nbsp;", "Tablo&nbsp;").replace("Fig.&nbsp;", "Şekil&nbsp;").replace("Section&nbsp;", "Bölüm&nbsp;")
    out = REPORT / f"report{sfx}.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")

    if args.lang == "en":
        readme = ROOT / "README.md"
        text = readme.read_text(encoding="utf-8")
        for name, content in readme_blocks.items():
            text = replace_block(text, name, content)
        readme.write_text(text, encoding="utf-8")
        print("updated README result blocks")

    if args.no_pdf:
        return
    pdf = REPORT / f"report{sfx}.pdf"
    print_pdf(out, pdf)
    # page count without references and disclosure (guideline: 8-12 pages excluding references)
    cut = html.index('<h2 class="refs">')
    body_only = html[:cut] + "</div></body></html>"
    tmp_html = REPORT / f"_body_only{sfx}.html"
    tmp_pdf = REPORT / f"_body_only{sfx}.pdf"
    tmp_html.write_text(body_only, encoding="utf-8")
    print_pdf(tmp_html, tmp_pdf)
    n_all, n_body = pdf_pages(pdf), pdf_pages(tmp_pdf)
    tmp_html.unlink()
    tmp_pdf.unlink()
    print(f"{pdf.name}: {n_all} pages in total, {n_body} pages without references/disclosure")
    if not 8 <= n_body <= 12:
        print("WARNING: body length outside the 8-12 page requirement")


if __name__ == "__main__":
    main()
