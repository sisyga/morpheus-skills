#!/usr/bin/env python3
"""Validate the structure and integrity of a generated Morpheus skill ZIP."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import BadZipFile, ZipFile

REQUIRED_FILES = {
    "morpheus/SKILL.md",
    "morpheus/LICENSE.txt",
    "morpheus/agents/openai.yaml",
    "morpheus/references/model-template.md",
    "morpheus/references/morpheusml-doc.md",
    "morpheus/references/cpm-examples.md",
    "morpheus/references/pde-examples.md",
    "morpheus/references/ode-examples.md",
    "morpheus/references/multiscale-examples.md",
    "morpheus/references/miscellaneous-examples.md",
}

OFFLINE_INDEX_FILES = {
    "morpheus/references/examples-summary.md",
    "morpheus/references/examples-index.md",
    "morpheus/references/examples-manifest.json",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Release ZIP to validate")
    parser.add_argument(
        "--profile",
        choices=("lean", "offline-full"),
        default="lean",
        help="Expected release profile",
    )
    return parser.parse_args()


def validate(archive_path: Path, profile: str) -> None:
    try:
        with ZipFile(archive_path) as archive:
            corrupt_file = archive.testzip()
            if corrupt_file:
                raise SystemExit(f"Corrupt file in release archive: {corrupt_file}")

            names = set(archive.namelist())
            missing = sorted(REQUIRED_FILES - names)
            if missing:
                raise SystemExit(f"Missing required release files: {missing}")

            for reference in sorted(REQUIRED_FILES):
                if reference.endswith("-examples.md"):
                    text = archive.read(reference).decode("utf-8")
                    if "```xml" not in text:
                        raise SystemExit(f"Generated reference contains no XML: {reference}")

            corpus_files = {
                name for name in names if name.startswith("morpheus/references/examples/")
            }
            if profile == "lean":
                unexpected = sorted((OFFLINE_INDEX_FILES & names) | corpus_files)
                if unexpected:
                    raise SystemExit(
                        f"Lean release unexpectedly contains offline corpus files: {unexpected[:5]}"
                    )
            else:
                missing_indexes = sorted(OFFLINE_INDEX_FILES - names)
                if missing_indexes:
                    raise SystemExit(
                        f"Offline-full release is missing corpus indexes: {missing_indexes}"
                    )
                if not corpus_files:
                    raise SystemExit("Offline-full release contains no model corpus files")
    except BadZipFile as exc:
        raise SystemExit(f"Invalid release ZIP: {archive_path}") from exc

    print(f"Validated {profile} release: {archive_path} ({len(names)} files)")


def main() -> None:
    args = parse_args()
    validate(args.archive, args.profile)


if __name__ == "__main__":
    main()
