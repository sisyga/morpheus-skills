#!/usr/bin/env python3
"""Generate references/morpheusml-doc.md from the Morpheus Doxygen documentation.

The MorpheusML reference is the documentation embedded in the Morpheus C++ source.
Build it with Doxygen in a Morpheus checkout, keeping formulas as LaTeX (MathJax)
instead of rendered images, then convert the topic pages with this script:

    cd path/to/morpheus
    (cat Doxyfile; echo OUTPUT_DIRECTORY=/tmp/morpheus-doxy; echo GENERATE_LATEX=NO;
     echo USE_MATHJAX=YES; echo HAVE_DOT=NO; echo SEARCHENGINE=NO) > /tmp/Doxyfile.skill
    doxygen /tmp/Doxyfile.skill
    cd path/to/morpheus-skills
    python3 tools/build_morpheusml_doc.py /tmp/morpheus-doxy/html --morpheus-version 2.4.1

Requires pandoc and BeautifulSoup (bs4).
"""

from __future__ import annotations

import argparse
import html
import re
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

DEFAULT_OUTPUT = Path("morpheus/references/morpheusml-doc.md")
# Developer template for writing new plugins, not a model element.
SKIPPED_PAGES = {"group__ExamplePlugin.html"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("doxygen_html", type=Path, help="Doxygen HTML output directory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--morpheus-version", required=True, help="Morpheus release the docs were built from"
    )
    return parser.parse_args()


def protect_math(page: str, formulas: list[str]) -> str:
    """Swap MathJax formulas for placeholders, since pandoc's HTML reader drops them."""

    def store(latex: str, display: bool) -> str:
        latex = " ".join(html.unescape(latex).split())
        formulas.append(f"\n\n$${latex}$$\n\n" if display else f"${latex}$")
        return f"MATHPLACEHOLDER{len(formulas) - 1}X"

    page = re.sub(r"\\\[(.*?)\\\]", lambda m: store(m.group(1), True), page, flags=re.S)
    page = re.sub(r"\\\((.*?)\\\)", lambda m: store(m.group(1), False), page, flags=re.S)
    # Environments such as \f{eqnarray*} appear without \( \) or \[ \] delimiters.
    return re.sub(
        r"\\begin\{(\w+\*?)\}.*?\\end\{\1\}",
        lambda m: store(m.group(0), True),
        page,
        flags=re.S,
    )


def restore_math(markdown: str, formulas: list[str]) -> str:
    markdown = re.sub(
        r"MATHPLACEHOLDER(\d+)X", lambda m: formulas[int(m.group(1))], markdown
    )
    return re.sub(r"\n{3,}", "\n\n", markdown)


def simplify_contents(soup: BeautifulSoup, contents) -> None:
    """Rewrite Doxygen-specific markup into plain HTML that converts cleanly."""
    for table in contents.select("table.memberdecls"):
        items = soup.new_tag("ul")
        for row in table.select("tr"):
            link = row.select_one("td.memItemRight a")
            if link:
                item = soup.new_tag("li")
                item.string = link.get_text(strip=True)
                items.append(item)
            description = row.select_one("td.mdescRight")
            if description and len(items):
                items.contents[-1].append(": " + description.get_text(" ", strip=True))
        heading = soup.new_tag("h2")
        heading.string = "Child elements"
        table.replace_with(heading)
        heading.insert_after(items)

    for fragment in contents.select("div.fragment, pre.fragment"):
        lines = fragment.select("div.line")
        code = "\n".join(line.get_text() for line in lines) if lines else fragment.get_text()
        code = code.strip("\n")
        pre = soup.new_tag("pre")
        tag = soup.new_tag("code", attrs={"class": "xml" if code.lstrip().startswith("<") else ""})
        tag.string = code
        pre.append(tag)
        fragment.replace_with(pre)

    # The brief description above the child list is repeated in the details.
    for more in contents.select('a[href="#details"]'):
        more.find_parent("p").decompose()

    for link in contents.select("a"):
        href = link.get("href", "")
        if not href or not href.startswith(("http://", "https://")):
            link.replace_with(NavigableString(link.get_text()) if link.get_text() else "")
    for image in contents.select("img"):
        image.decompose()


def shift_headings(contents, top_level: int = 2) -> None:
    # Doxygen's own "Detailed Description" header carries no information.
    for heading in contents.select("h2.groupheader"):
        if heading.find_parent("table") is None:
            heading.decompose()
    headings = [
        heading
        for heading in contents.find_all(re.compile(r"^h[1-6]$"))
        if heading.find_parent("table") is None
    ]
    if not headings:
        return
    offset = top_level - min(int(h.name[1]) for h in headings)
    for heading in headings:
        heading.name = f"h{min(6, int(heading.name[1]) + offset)}"
        for attribute in ("id", "class"):
            heading.attrs.pop(attribute, None)


def convert_page(path: Path) -> tuple[str, str] | None:
    formulas: list[str] = []
    soup = BeautifulSoup(protect_math(path.read_text(encoding="utf-8"), formulas), "lxml")
    title_div = soup.select_one("div.headertitle div.title")
    ingroups = title_div.select_one("div.ingroups")
    location = ingroups.get_text("", strip=False) if ingroups else ""
    locations = list(dict.fromkeys(" ".join(part.split()) for part in location.split("|")))
    if ingroups:
        ingroups.decompose()
    title = title_div.get_text(" ", strip=True)

    contents = soup.select_one("div.contents > div.contents") or soup.select_one(
        "div.contents"
    )
    shift_headings(contents)
    simplify_contents(soup, contents)

    markdown = subprocess.run(
        ["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
        input=str(contents),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    markdown = restore_math(markdown, formulas).strip()

    # Doxygen repeats the brief description as the first paragraph of the details.
    paragraphs = markdown.split("\n\n")
    if len(paragraphs) > 1 and paragraphs[0] == paragraphs[1]:
        markdown = "\n\n".join(paragraphs[1:])

    if not markdown:
        print(f"skip {title}: no documentation in the source")
        return None

    lines = [f"# {title}", ""]
    if any(locations):
        lines += ["Location: " + "; ".join(part for part in locations if part), ""]
    lines.append(markdown)
    return title, "\n".join(lines).rstrip() + "\n"


def build_document(entries: list[tuple[str, str]], version: str) -> str:
    titles = ", ".join(title for title, _ in entries)
    header = "\n".join(
        [
            "# MorpheusML Reference",
            "",
            f"Tag, plugin, and concept documentation for MorpheusML, generated from the "
            f"Morpheus {version} source. Each entry is a top-level `# <Name>` section. "
            "`Location` lists where the element is used in a model.",
            "",
            "## Contents",
            "",
            "Jump to an entry instead of reading the whole file:",
            "",
            '`grep -n "^# Gnuplotter" references/morpheusml-doc.md`',
            "",
            titles,
            "",
            "---",
            "",
        ]
    )
    return header + "\n" + "\n\n".join(body.rstrip() for _, body in entries) + "\n"


def main() -> None:
    args = parse_args()
    pages = sorted(
        path
        for path in args.doxygen_html.glob("group__*.html")
        if path.name not in SKIPPED_PAGES
    )
    if not pages:
        raise SystemExit(f"No Doxygen topic pages found in {args.doxygen_html}")

    entries = sorted(
        (entry for entry in map(convert_page, pages) if entry), key=lambda e: e[0].lower()
    )
    args.output.write_text(build_document(entries, args.morpheus_version), encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {args.output}")


if __name__ == "__main__":
    main()
