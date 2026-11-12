"""Final submission check (course guideline Sec. 20). Prints PASS/FAIL per item.

Usage:  python tools/final_check.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

README_HEADINGS = ["Project Title", "Student Information", "Original Paper", "Problem Description", "Method",
                   "Fuzzy System Architecture", "Dataset", "Installation", "Requirements", "How to Run",
                   "Reproduction Experiments", "Proposed Extension", "Experimental Results", "Limitations", "References"]
results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, info: str = "") -> None:
    results.append((name, ok, info))


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout


def main() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    heads = re.findall(r"^## (.+)$", readme, re.M)
    missing = [h for h in README_HEADINGS if h not in heads]
    check("README has the 15 required headings", not missing, ", ".join(missing))
    check("README has no TODO / placeholder", "TODO" not in readme and "(filled from the CSV" not in readme)

    from report.build_report import pdf_pages
    pdf = ROOT / "report" / "report.pdf"
    check("report/report.pdf exists", pdf.exists())
    if pdf.exists():
        check("report has 8-12 pages + references", 8 <= pdf_pages(pdf) <= 15, f"{pdf_pages(pdf)} pages in total")
    html = (ROOT / "report" / "report.html").read_text(encoding="utf-8") if (ROOT / "report" / "report.html").exists() else ""
    for sec in ["Introduction", "Related Work", "Theoretical Background", "Original Method", "Reproduction Methodology",
                "Proposed Extension", "Experimental Setup", "Results", "Discussion", "Limitations", "Conclusion",
                "References", "Generative AI Usage Disclosure"]:
        check(f"report section: {sec}", sec in html)
    check("report has no unfilled placeholder", "{{" not in html)
    figs = re.findall(r'src="\.\./(results/figures/[^"]+)"', html)
    check("all report figures exist", all((ROOT / f).exists() for f in figs), f"{len(figs)} figures")

    for f in ("presentation/presentation.pdf", "presentation/presentation.pptx", "requirements.txt",
              "requirements.lock.txt", "LICENSE", "references/README.md", "demo/demo.py", "report/decisions.md"):
        check(f"{f} exists", (ROOT / f).exists())

    tracked = git("ls-files").splitlines()
    check("docs/ not in the repository", not any(t.startswith("docs/") for t in tracked))
    check("no publisher PDF / .env / raw data tracked",
          not any(re.search(r"references/papers/.*\.pdf$|\.env$|^data/raw/", t) for t in tracked))
    grep = subprocess.run(["git", "grep", "--cached", "-n", "-i", "-E",
                           r"api[_-]?key\s*[:=]|secret\s*[:=]|token\s*[:=]|password\s*[:=]|BEGIN (RSA|OPENSSH)"],
                          cwd=ROOT, capture_output=True, text=True).stdout
    check("no secrets in tracked files", grep.strip() == "", grep[:200])
    log = git("log", "--format=%an|%cn|%B")
    check("no Co-Authored-By / Claude trailers in history", not re.search(r"co-authored-by|anthropic", log, re.I))
    authors = set(re.findall(r"^([^|\n]+)\|([^|\n]+)\|", log, re.M))
    check("all commits authored and committed by the student", authors <= {("tarikoztas", "tarikoztas")}, str(authors))
    n_commits = len(git("log", "--oneline").splitlines())
    check("commit history is incremental (>= 30 commits)", n_commits >= 30, f"{n_commits} commits")

    width = max(len(r[0]) for r in results)
    for name, ok, info in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name.ljust(width)}  {info}")
    print(f"\n{sum(r[1] for r in results)}/{len(results)} checks passed")
    sys.exit(0 if all(r[1] for r in results) else 1)


if __name__ == "__main__":
    main()
