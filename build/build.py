#!/usr/bin/env python3
"""Build the website from cv.md (single source of truth).

Parses cv.md, generates publication / award / invited-talk lists, injects
them into website/index.html and website/ja.html between BUILD markers,
converts cv.md to cv.html with pandoc, renders assets/cv.pdf with
weasyprint, and writes the deployable site to _site/.

Runs in GitHub Actions (see .github/workflows/deploy.yml).
Requires: python3, pandoc. Optional: weasyprint (for the PDF).

Annotations recognized inside cv.md entries:
  <!-- ja: ... -->    Japanese text used on ja.html instead of the English.
  <!-- web:hide -->   Exclude the entry from the website (kept in CV/PDF).
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"


# ---------- cv.md parsing ----------

def read_sections(text):
    """Return {heading: body} for each '## HEADING' section."""
    sections = {}
    parts = re.split(r"^## +(.+?)\s*$", text, flags=re.M)
    for i in range(1, len(parts) - 1, 2):
        sections[parts[i].strip()] = parts[i + 1]
    return sections


def split_annotations(text):
    """Extract ja/web:hide annotations; return (clean_text, ja_text, hidden)."""
    ja = None
    m = re.search(r"<!--\s*ja:\s*(.*?)\s*-->", text)
    if m:
        ja = m.group(1)
    hidden = re.search(r"<!--\s*web:hide\s*-->", text) is not None
    clean = re.sub(r"<!--.*?-->", "", text).strip()
    return clean, ja, hidden


def parse_numbered_list(body):
    """Parse '1. item' lines; return list of (text, ja, hidden)."""
    items = []
    for m in re.finditer(r"^\d+\.\s+(.+?)\s*$", body, flags=re.M):
        items.append(split_annotations(m.group(1)))
    return items


def parse_table_rows(body):
    """Parse two-column pipe-table rows; return list of (year, text, ja, hidden)."""
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or not cells[0] or set(cells[0]) <= set(":- "):
            continue
        text, ja, hidden = split_annotations(cells[1])
        rows.append((cells[0], text, ja, hidden))
    return rows


# ---------- HTML rendering ----------

def md_inline(text):
    """Escape HTML, then convert *italics* and bold the author's name."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"\bMori Y\b", "<strong>Mori Y</strong>", text)
    return text


def pub_year(citation):
    years = re.findall(r"\b(?:19|20)\d{2}\b", citation)
    return years[-1] if years else None


def render_pub(citation):
    year = pub_year(citation)
    badge = f'<span class="pub-year">{year}</span> ' if year else ""
    return f"      <li>{badge}{md_inline(citation)}</li>"


def render_row(year, text, css_class):
    return (f'      <li><span class="{css_class}">{year}</span> '
            f"{md_inline(text)}</li>")


def build_fragments(sections, lang):
    """Return {marker_key: html_fragment} for one language."""
    def pick(text, ja):
        return ja if (lang == "ja" and ja) else text

    pubs = [p for p in parse_numbered_list(
        sections["PEER-REVIEWED PUBLICATIONS"]) if not p[2]]
    first = [render_pub(pick(t, ja)) for t, ja, _ in pubs
             if t.startswith("Mori Y")]
    co = [render_pub(pick(t, ja)) for t, ja, _ in pubs
          if not t.startswith("Mori Y")]

    awards = [render_row(y, pick(t, ja), "award-year")
              for y, t, ja, h in parse_table_rows(
                  sections["AWARDS AND HONORS"]) if not h]
    talks = [render_row(y, pick(t, ja), "award-year")
             for y, t, ja, h in parse_table_rows(
                 sections["INVITED TALKS"]) if not h]

    if not (first and co and awards and talks):
        sys.exit("build.py: a generated list is empty — check cv.md headings")

    return {
        "pubs-first": "\n".join(first),
        "pubs-co": "\n".join(co),
        "awards": "\n".join(awards),
        "talks": "\n".join(talks),
    }


def inject(html, key, fragment, page):
    pattern = re.compile(
        rf"(<!-- BUILD:{key} -->).*?(<!-- /BUILD:{key} -->)", re.S)
    if not pattern.search(html):
        sys.exit(f"build.py: marker BUILD:{key} missing in {page}")
    return pattern.sub(lambda m: f"{m.group(1)}\n{fragment}\n      {m.group(2)}",
                       html)


# ---------- cv.html / cv.pdf ----------

def build_cv_html():
    out = SITE / "cv.html"
    subprocess.run(
        ["pandoc", str(ROOT / "cv.md"), "-f", "markdown", "-t", "html5",
         "--standalone", "--metadata", "pagetitle=Yuichiro Mori — Curriculum Vitae",
         "-o", str(out)],
        check=True, cwd=ROOT)
    html = out.read_text(encoding="utf-8")
    extra = ("<style>body{max-width:800px;margin:0 auto;padding:2rem 1.5rem;"
             'font-family:"Segoe UI",system-ui,sans-serif;line-height:1.55;}'
             ".site-back{font-size:0.9rem;margin-bottom:1.5rem;}"
             "@media print{.site-back{display:none;}}</style>")
    back = ('<p class="site-back"><a href="index.html">&larr; Back to '
            "yuichiromori56.github.io</a></p>")
    html = html.replace("</head>", extra + "\n</head>", 1)
    html = re.sub(r"<body[^>]*>", lambda m: m.group(0) + "\n" + back, html, 1)
    out.write_text(html, encoding="utf-8")


def build_cv_pdf():
    if shutil.which("weasyprint") is None:
        print("build.py: weasyprint not found — skipping cv.pdf")
        return
    subprocess.run(
        ["weasyprint", str(SITE / "cv.html"),
         str(SITE / "assets" / "cv.pdf"),
         "-s", str(ROOT / "build" / "pdf.css")],
        check=True, cwd=SITE)


# ---------- main ----------

def main():
    cv = (ROOT / "cv.md").read_text(encoding="utf-8")
    sections = read_sections(cv)

    if SITE.exists():
        shutil.rmtree(SITE)
    shutil.copytree(ROOT / "website", SITE)
    shutil.copy(ROOT / "cv.css", SITE / "cv.css")

    for page, lang in [("index.html", "en"), ("ja.html", "ja")]:
        path = SITE / page
        html = path.read_text(encoding="utf-8")
        for key, fragment in build_fragments(sections, lang).items():
            html = inject(html, key, fragment, page)
        path.write_text(html, encoding="utf-8")

    build_cv_html()
    build_cv_pdf()
    print("build.py: site written to _site/")


if __name__ == "__main__":
    main()
