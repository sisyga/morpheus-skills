#!/usr/bin/env python3
"""Build morpheus.zip for Claude Desktop skill upload.

Creates a ZIP with the correct structure:
    morpheus/
    ├── SKILL.md
    ├── LICENSE.txt
    └── references/
        └── ...

Usage:
    python build_release.py
"""

import os
import zipfile

SKILL_DIR = "morpheus"
OUTPUT = "morpheus.zip"


def build():
    if not os.path.isdir(SKILL_DIR):
        print(f"Error: '{SKILL_DIR}/' directory not found. Run from the repo root.")
        raise SystemExit(1)

    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(SKILL_DIR):
            for f in files:
                filepath = os.path.join(root, f)
                arcname = filepath.replace(os.sep, "/")
                zf.write(filepath, arcname)

    with zipfile.ZipFile(OUTPUT, "r") as zf:
        count = len(zf.namelist())
        size_kb = sum(i.compress_size for i in zf.infolist()) // 1024

    print(f"Created {OUTPUT} ({count} files, {size_kb} KB)")


if __name__ == "__main__":
    build()
