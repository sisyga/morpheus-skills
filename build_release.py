#!/usr/bin/env python3
"""Build morpheus.zip for Claude Desktop skill upload.

The repo keeps XML examples in subfolders (references/CPM/, references/PDE/, etc.)
for easy editing. This script flattens them into per-category markdown files for
the release ZIP, since Claude Desktop skills don't support nested subdirectories.

Repo structure (editable):
    morpheus/
    ├── SKILL.md
    ├── references/
    │   ├── CPM/*.xml
    │   ├── PDE/*.xml
    │   ├── ODE/*.xml
    │   ├── Multiscale/*.xml
    │   ├── Miscellaneous/*.xml
    │   ├── model_template.txt
    │   └── morpheusml_doc.txt
    └── assets/
        └── *.tif

Release ZIP (flat):
    morpheus/
    ├── SKILL.md
    ├── LICENSE.txt
    ├── references/
    │   ├── cpm-examples.md
    │   ├── pde-examples.md
    │   ├── ode-examples.md
    │   ├── multiscale-examples.md
    │   ├── miscellaneous-examples.md
    │   ├── model_template.txt
    │   └── morpheusml_doc.txt
    └── assets/
        └── *.tif

Usage:
    python build_release.py
"""

import os
import zipfile

SKILL_DIR = "morpheus"
OUTPUT = "morpheus.zip"

CATEGORIES = {
    "CPM": "Cellular Potts Model (CPM) Examples",
    "PDE": "Partial Differential Equation (PDE) Examples",
    "ODE": "Ordinary Differential Equation (ODE) Examples",
    "Multiscale": "Multiscale Model Examples",
    "Miscellaneous": "Miscellaneous Examples",
}


def merge_category_to_markdown(category, title):
    """Read all XML files in a category subfolder and return a single markdown string."""
    src_dir = os.path.join(SKILL_DIR, "references", category)
    if not os.path.isdir(src_dir):
        return None

    xml_files = sorted(f for f in os.listdir(src_dir) if f.endswith(".xml"))
    if not xml_files:
        return None

    parts = [
        f"# {title}\n",
        f"Reference MorpheusML v4 XML models for {category.lower()} simulations.\n",
        "---\n",
    ]
    for xf in xml_files:
        name = xf.replace(".xml", "")
        filepath = os.path.join(src_dir, xf)
        with open(filepath, "r", encoding="utf-8") as fh:
            content = fh.read()
        parts.append(f"## {name}\n")
        parts.append("```xml")
        parts.append(content.rstrip())
        parts.append("```\n")

    return "\n".join(parts)


def build():
    if not os.path.isdir(SKILL_DIR):
        print(f"Error: '{SKILL_DIR}/' directory not found. Run from the repo root.")
        raise SystemExit(1)

    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Add SKILL.md and LICENSE.txt
        zf.write(
            os.path.join(SKILL_DIR, "SKILL.md"),
            "morpheus/SKILL.md",
        )
        zf.write(
            os.path.join(SKILL_DIR, "LICENSE.txt"),
            "morpheus/LICENSE.txt",
        )

        # 2. Add flat reference files (template + docs)
        for fname in ("model_template.txt", "morpheusml_doc.txt"):
            src = os.path.join(SKILL_DIR, "references", fname)
            if os.path.isfile(src):
                zf.write(src, f"morpheus/references/{fname}")

        # 3. Merge each XML category into a markdown file
        for category, title in CATEGORIES.items():
            md_content = merge_category_to_markdown(category, title)
            if md_content:
                arcname = f"morpheus/references/{category.lower()}-examples.md"
                zf.writestr(arcname, md_content)
                xml_count = md_content.count("\n## ")
                print(f"  {arcname}: {xml_count} models merged")

        # 4. Add assets (TIFs, etc.) — flat, no subdirectories
        assets_dir = os.path.join(SKILL_DIR, "assets")
        if os.path.isdir(assets_dir):
            for fname in sorted(os.listdir(assets_dir)):
                src = os.path.join(assets_dir, fname)
                if os.path.isfile(src):
                    zf.write(src, f"morpheus/assets/{fname}")

    # Report
    with zipfile.ZipFile(OUTPUT, "r") as zf:
        names = zf.namelist()
        count = len(names)
        size_kb = sum(i.compress_size for i in zf.infolist()) // 1024

    print(f"\nCreated {OUTPUT} ({count} files, {size_kb} KB)")


if __name__ == "__main__":
    build()
