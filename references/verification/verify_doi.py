"""Verify DOIs against Crossref: prints title, authors, year, venue, vol/issue/pages as JSON lines."""
import json, sys, time, urllib.request, urllib.parse

def fetch(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    req = urllib.request.Request(url, headers={"User-Agent": "fuzzy-course-project-doi-check/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        m = json.load(r)["message"]
    year = None
    for k in ("published-print", "issued", "published-online"):
        if m.get(k, {}).get("date-parts"):
            year = m[k]["date-parts"][0][0]; break
    authors = [f"{a.get('given','')} {a.get('family','')}".strip() for a in m.get("author", [])]
    return {"doi": doi, "title": (m.get("title") or [""])[0], "authors": authors,
            "year": year, "venue": (m.get("container-title") or [""])[0],
            "volume": m.get("volume"), "issue": m.get("issue"), "pages": m.get("page"),
            "article": m.get("article-number")}

if __name__ == "__main__":
    for doi in [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip() and not l.startswith("#")]:
        try:
            print(json.dumps(fetch(doi), ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"doi": doi, "error": str(e)}))
        time.sleep(0.3)
