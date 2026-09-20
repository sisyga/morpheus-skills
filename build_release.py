#!/usr/bin/env python3
"""Build a Morpheus skill release.

The default release is lean: it converts the tracked reference documents to Markdown
and merges each tracked XML category into one Markdown reference. Pass ``--model-repo``
to additionally package a searchable, pinned snapshot of the public Morpheus model
repository for offline use.

Generated release layout:
    morpheus/
    |-- SKILL.md
    |-- LICENSE.txt
    |-- agents/openai.yaml
    `-- references/
        |-- model-template.md
        |-- morpheusml-doc.md
        |-- cpm-examples.md
        |-- pde-examples.md
        |-- ode-examples.md
        |-- multiscale-examples.md
        `-- miscellaneous-examples.md

The optional offline-full release also contains ``examples-summary.md``,
``examples-index.md``, ``examples-manifest.json``, and one folder per model under
``references/examples/``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

SKILL_DIR = Path("morpheus")
DEFAULT_OUTPUT = Path("morpheus.zip")
GENERATED_REFERENCES_DIR = Path("references")
GENERATED_EXAMPLES_DIR = GENERATED_REFERENCES_DIR / "examples"

CATEGORIES = {
    "CPM": "Cellular Potts Model (CPM) Examples",
    "PDE": "Partial Differential Equation (PDE) Examples",
    "ODE": "Ordinary Differential Equation (ODE) Examples",
    "Multiscale": "Multiscale Model Examples",
    "Miscellaneous": "Miscellaneous Examples",
}

TXT_TO_MD = {
    "model_template.txt": "model-template.md",
    "morpheusml_doc.txt": "morpheusml-doc.md",
}

TEXT_EXTENSIONS = {
    ".bib",
    ".csv",
    ".json",
    ".md",
    ".markdown",
    ".svg",
    ".tex",
    ".tsv",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

VIDEO_EXTENSIONS = {
    ".avi",
    ".gif",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".webm",
    ".wmv",
}

MAX_SUMMARY_CHARS = 320


@dataclass
class ReleaseFile:
    source: Path
    arcname: str
    size_bytes: int


@dataclass
class ModelEntry:
    key: str
    title: str
    source_path: str
    collection: str
    category_path: str
    model_id: str | None
    main_xml: str
    xml_files: list[str]
    copied_files: list[str]
    skipped_files: list[str]
    morpheusml_versions: list[str]
    authors: list[str]
    contributors: list[str]
    tags: list[str]
    summary: str
    description_source: str
    overview_path: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model-repo",
        help=(
            "Optionally include a searchable offline corpus from a local checkout "
            "or snapshot of morpheus.lab/model-repo"
        ),
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output zip path",
    )
    parser.add_argument(
        "--max-binary-mb",
        type=float,
        default=25.0,
        help="Skip non-text attachments larger than this many megabytes",
    )
    return parser.parse_args()


def merge_category_to_markdown(category: str, title: str) -> str | None:
    """Merge the tracked XML files for one category into a Markdown reference."""
    source_dir = SKILL_DIR / "references" / category
    if not source_dir.is_dir():
        return None

    xml_files = sorted(source_dir.glob("*.xml"))
    if not xml_files:
        return None

    parts = [
        f"# {title}\n",
        f"Reference MorpheusML v4 XML models for {category.lower()} simulations.\n",
        "---\n",
    ]
    for xml_path in xml_files:
        parts.extend(
            [
                f"## {xml_path.stem}\n",
                "```xml",
                xml_path.read_text(encoding="utf-8").rstrip(),
                "```\n",
            ]
        )

    return "\n".join(parts)


def strip_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_yaml_value(raw: str) -> str | list[str]:
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        reader = csv.reader([inner], skipinitialspace=True)
        return [strip_yaml_scalar(item) for item in next(reader)]
    return strip_yaml_scalar(raw)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return {}, text

    data: dict[str, Any] = {}
    frontmatter = lines[1:end_idx]
    i = 0
    while i < len(frontmatter):
        line = frontmatter[i]
        if not line.strip() or line.lstrip().startswith("#") or line.startswith("  "):
            i += 1
            continue

        match = re.match(r"([A-Za-z0-9_]+):\s*(.*)$", line)
        if not match:
            i += 1
            continue

        key, raw = match.groups()
        if raw:
            data[key] = parse_yaml_value(raw)
            i += 1
            continue

        items: list[str] = []
        j = i + 1
        while j < len(frontmatter):
            nested = frontmatter[j]
            stripped = nested.lstrip()
            if stripped.startswith("- "):
                items.append(strip_yaml_scalar(stripped[2:]))
                j += 1
                continue
            if not nested.strip() or nested.startswith("  "):
                j += 1
                continue
            break
        if items:
            data[key] = items
        i = j

    body = "\n".join(lines[end_idx + 1 :]).strip()
    return data, body


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def markdown_summary(markdown_text: str) -> str:
    cleaned = re.sub(r"```.*?```", " ", markdown_text, flags=re.S)
    cleaned = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    paragraphs = [
        collapse_whitespace(block)
        for block in re.split(r"\n\s*\n", cleaned)
        if collapse_whitespace(block) and not collapse_whitespace(block).startswith("#")
    ]
    if not paragraphs:
        return ""
    summary = paragraphs[0]
    if len(summary) <= MAX_SUMMARY_CHARS:
        return summary
    return summary[: MAX_SUMMARY_CHARS - 3].rstrip() + "..."


def parse_xml_metadata(path: Path) -> dict[str, str]:
    metadata = {"version": "", "title": "", "details": ""}
    try:
        root = ET.parse(path).getroot()
        metadata["version"] = root.attrib.get("version", "")
        description = root.find("Description")
        if description is not None:
            title = description.find("Title")
            details = description.find("Details")
            metadata["title"] = (title.text or "").strip() if title is not None and title.text else ""
            metadata["details"] = (
                collapse_whitespace(details.text) if details is not None and details.text else ""
            )
        return metadata
    except ET.ParseError:
        text = path.read_text(encoding="utf-8", errors="replace")
        version_match = re.search(r'<MorpheusModel[^>]*version="([^"]+)"', text)
        title_match = re.search(r"<Title>(.*?)</Title>", text, flags=re.S)
        details_match = re.search(r"<Details>(.*?)</Details>", text, flags=re.S)
        metadata["version"] = version_match.group(1) if version_match else ""
        metadata["title"] = collapse_whitespace(title_match.group(1)) if title_match else ""
        metadata["details"] = collapse_whitespace(details_match.group(1)) if details_match else ""
        return metadata


def determine_main_xml(xml_files: list[Path]) -> Path:
    def sort_key(path: Path) -> tuple[int, str]:
        name = path.name.lower()
        if name.endswith("_main.xml"):
            priority = 0
        elif name == "model.xml":
            priority = 1
        elif name.startswith("_"):
            priority = 2
        else:
            priority = 3
        return priority, name

    return sorted(xml_files, key=sort_key)[0]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "model"


def build_model_key(relative_dir: Path, model_id: str | None, used_keys: set[str]) -> str:
    if model_id:
        candidate = model_id
    else:
        digest = hashlib.sha1(relative_dir.as_posix().encode("utf-8")).hexdigest()[:8]
        candidate = f"{slugify(relative_dir.name)}-{digest}"

    unique_candidate = candidate
    suffix = 2
    while unique_candidate in used_keys:
        unique_candidate = f"{candidate}-{suffix}"
        suffix += 1
    used_keys.add(unique_candidate)
    return unique_candidate


def format_list(values: list[str]) -> str:
    return ", ".join(values) if values else "None"


def build_overview(entry: ModelEntry, source_commit: str | None) -> str:
    lines = [
        f"# {entry.title}",
        "",
        f"- Model key: `{entry.key}`",
        f"- Source path: `{entry.source_path}`",
        f"- Collection: `{entry.collection}`",
        f"- Category path: `{entry.category_path or entry.collection}`",
        f"- Main XML: `references/examples/{entry.key}/{entry.main_xml}`",
        f"- Morpheus model ID: `{entry.model_id}`" if entry.model_id else "- Morpheus model ID: None",
        f"- MorpheusML versions: `{', '.join(entry.morpheusml_versions) or 'unknown'}`",
        f"- Authors: {format_list(entry.authors)}",
        f"- Contributors: {format_list(entry.contributors)}",
        f"- Tags: {format_list(entry.tags)}",
        f"- Copied files: `{len(entry.copied_files)}`",
    ]
    if source_commit:
        lines.append(f"- Source snapshot: `{source_commit}`")
    if entry.skipped_files:
        skipped = ", ".join(f"`{name}`" for name in entry.skipped_files)
        lines.append(f"- Skipped oversized files: {skipped}")

    lines.extend(
        [
            "",
            "## Summary",
            "",
            entry.summary or "No summary available.",
            "",
            "## Open Next",
            "",
            f"- `references/examples/{entry.key}/{entry.main_xml}`",
        ]
    )

    extra_files = [name for name in entry.copied_files if name != entry.main_xml]
    if extra_files:
        lines.append("")
        lines.append("## Additional Files")
        lines.append("")
        lines.extend(f"- `references/examples/{entry.key}/{name}`" for name in extra_files)

    return "\n".join(lines) + "\n"


def detect_source_commit(model_repo_dir: Path) -> str | None:
    try:
        top_level = subprocess.run(
            ["git", "-C", str(model_repo_dir), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        if Path(top_level.stdout.strip()).resolve() != model_repo_dir.resolve():
            return None
        result = subprocess.run(
            ["git", "-C", str(model_repo_dir), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def is_video_file(path: Path) -> bool:
    return path.suffix.lower() in VIDEO_EXTENSIONS


def collect_model_entries(model_repo_dir: Path, max_binary_bytes: int) -> tuple[list[ModelEntry], list[ReleaseFile], str | None]:
    used_keys: set[str] = set()
    entries: list[ModelEntry] = []
    release_files: list[ReleaseFile] = []
    source_commit = detect_source_commit(model_repo_dir)

    for current_root, dirnames, filenames in os.walk(model_repo_dir):
        dirnames[:] = [name for name in dirnames if name != ".git"]
        xml_names = sorted(name for name in filenames if name.lower().endswith(".xml"))
        if not xml_names:
            continue

        model_dir = Path(current_root)
        relative_dir = model_dir.relative_to(model_repo_dir)
        xml_files = [model_dir / name for name in xml_names]
        main_xml_path = determine_main_xml(xml_files)

        metadata_path = model_dir / "index.md"
        frontmatter: dict[str, Any] = {}
        metadata_body = ""
        if metadata_path.is_file():
            frontmatter, metadata_body = parse_frontmatter(metadata_path.read_text(encoding="utf-8", errors="replace"))

        xml_metadata = [parse_xml_metadata(path) for path in xml_files]
        versions = sorted({item["version"] for item in xml_metadata if item["version"]})
        main_metadata = parse_xml_metadata(main_xml_path)

        model_id = frontmatter.get("MorpheusModelID")
        if isinstance(model_id, list):
            model_id = model_id[0] if model_id else None
        model_id = str(model_id) if model_id else None

        title = frontmatter.get("title")
        if isinstance(title, list):
            title = title[0] if title else ""
        title = str(title).strip() if title else ""
        if not title:
            title = main_metadata["title"] or relative_dir.name

        authors = frontmatter.get("authors")
        if isinstance(authors, str):
            authors = [authors]
        authors = authors if isinstance(authors, list) else []

        contributors = frontmatter.get("contributors")
        if isinstance(contributors, str):
            contributors = [contributors]
        contributors = contributors if isinstance(contributors, list) else []

        tags = frontmatter.get("tags")
        if isinstance(tags, str):
            tags = [tags]
        tags = tags if isinstance(tags, list) else []

        summary = markdown_summary(metadata_body) or main_metadata["details"]
        description_source = "index.md" if metadata_body else "xml"

        key = build_model_key(relative_dir, model_id, used_keys)
        copied_files: list[str] = []
        skipped_files: list[str] = []
        release_dir = GENERATED_EXAMPLES_DIR / key

        for file_path in sorted(path for path in model_dir.iterdir() if path.is_file()):
            relative_name = file_path.name
            if is_video_file(file_path):
                skipped_files.append(relative_name)
                continue
            if not is_text_file(file_path) and file_path.stat().st_size > max_binary_bytes:
                skipped_files.append(relative_name)
                continue

            copied_files.append(relative_name)
            release_files.append(
                ReleaseFile(
                    source=file_path,
                    arcname=(Path("morpheus") / release_dir / relative_name).as_posix(),
                    size_bytes=file_path.stat().st_size,
                )
            )

        collection = relative_dir.parts[0]
        category_path = " > ".join(relative_dir.parts[1:-1])
        entry = ModelEntry(
            key=key,
            title=title,
            source_path=relative_dir.as_posix(),
            collection=collection,
            category_path=category_path,
            model_id=model_id,
            main_xml=main_xml_path.name,
            xml_files=xml_names,
            copied_files=copied_files,
            skipped_files=skipped_files,
            morpheusml_versions=versions,
            authors=authors,
            contributors=contributors,
            tags=tags,
            summary=summary,
            description_source=description_source,
            overview_path=(release_dir / "overview.md").as_posix(),
        )
        entries.append(entry)

    entries.sort(key=lambda item: (item.collection, item.category_path, item.title.lower()))
    return entries, release_files, source_commit


def build_examples_summary(entries: list[ModelEntry], model_repo_dir: Path, source_commit: str | None) -> str:
    collection_counts = Counter(entry.collection for entry in entries)
    version_counts = Counter(version for entry in entries for version in entry.morpheusml_versions)
    skipped_count = sum(len(entry.skipped_files) for entry in entries)

    lines = [
        "# Examples Summary",
        "",
        f"- Source path: `{model_repo_dir.as_posix()}`",
        f"- Source snapshot: `{source_commit}`" if source_commit else "- Source snapshot: unavailable",
        f"- Total models: `{len(entries)}`",
        f"- Models with skipped oversized files: `{sum(1 for entry in entries if entry.skipped_files)}`",
        f"- Total skipped oversized files: `{skipped_count}`",
        "",
        "## Collections",
        "",
    ]
    lines.extend(f"- `{name}`: `{count}`" for name, count in sorted(collection_counts.items()))

    lines.extend(["", "## MorpheusML Versions", ""])
    if version_counts:
        lines.extend(f"- `version {name}`: `{count}`" for name, count in sorted(version_counts.items()))
    else:
        lines.append("- No version metadata detected.")

    return "\n".join(lines) + "\n"


def build_examples_index(entries: list[ModelEntry]) -> str:
    lines = [
        "# Examples Index",
        "",
        "Search this file first by title, model ID, collection, organism, tags, or keyword.",
        "Then open the corresponding `overview.md` and XML files in `references/examples/<model-key>/`.",
        "",
    ]

    current_collection = None
    for entry in entries:
        if entry.collection != current_collection:
            current_collection = entry.collection
            lines.extend([f"## {current_collection}", ""])

        tag_text = format_list(entry.tags[:8])
        version_text = ", ".join(entry.morpheusml_versions) if entry.morpheusml_versions else "unknown"
        model_id = entry.model_id or "none"
        lines.append(
            f"- `{entry.key}` | `{entry.title}` | id: `{model_id}` | "
            f"path: `{entry.source_path}` | versions: `{version_text}` | "
            f"tags: {tag_text} | open: `{entry.overview_path}`"
        )

    return "\n".join(lines) + "\n"


def build_examples_manifest(entries: list[ModelEntry], model_repo_dir: Path, source_commit: str | None) -> str:
    payload = {
        "source_path": model_repo_dir.as_posix(),
        "source_commit": source_commit,
        "model_count": len(entries),
        "models": [asdict(entry) for entry in entries],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def add_local_file(zf: zipfile.ZipFile, source: Path, arcname: str) -> None:
    zf.write(source, arcname)
    print(f"  {arcname}")


def add_tree_if_present(zf: zipfile.ZipFile, source_dir: Path, target_root: Path) -> None:
    if not source_dir.is_dir():
        return

    for path in sorted(p for p in source_dir.rglob("*") if p.is_file()):
        relative = path.relative_to(source_dir)
        add_local_file(zf, path, (target_root / relative).as_posix())


def build() -> None:
    args = parse_args()
    output_path = Path(args.output)
    max_binary_bytes = int(args.max_binary_mb * 1024 * 1024)

    if not SKILL_DIR.is_dir():
        raise SystemExit(f"Error: '{SKILL_DIR}/' directory not found. Run from the repo root.")

    entries: list[ModelEntry] = []
    example_files: list[ReleaseFile] = []
    source_commit: str | None = None
    model_repo_dir: Path | None = None
    if args.model_repo:
        model_repo_dir = Path(args.model_repo)
        if not model_repo_dir.is_dir():
            raise SystemExit(f"Error: model corpus not found at '{model_repo_dir}'.")

        entries, example_files, source_commit = collect_model_entries(
            model_repo_dir, max_binary_bytes
        )
        if not entries:
            raise SystemExit(
                f"Error: no model directories with XML files found under '{model_repo_dir}'."
            )

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        add_local_file(zf, SKILL_DIR / "SKILL.md", "morpheus/SKILL.md")
        add_local_file(zf, SKILL_DIR / "LICENSE.txt", "morpheus/LICENSE.txt")

        for txt_name, md_name in TXT_TO_MD.items():
            source = SKILL_DIR / "references" / txt_name
            if source.is_file():
                add_local_file(zf, source, f"morpheus/references/{md_name}")

        for category, title in CATEGORIES.items():
            markdown = merge_category_to_markdown(category, title)
            if markdown:
                arcname = f"morpheus/references/{category.lower()}-examples.md"
                zf.writestr(arcname, markdown)
                print(f"  {arcname}")

        add_tree_if_present(zf, SKILL_DIR / "agents", Path("morpheus/agents"))
        add_tree_if_present(zf, SKILL_DIR / "assets", Path("morpheus/assets"))

        if model_repo_dir is not None:
            examples_summary = build_examples_summary(entries, model_repo_dir, source_commit)
            examples_index = build_examples_index(entries)
            examples_manifest = build_examples_manifest(entries, model_repo_dir, source_commit)

            zf.writestr("morpheus/references/examples-summary.md", examples_summary)
            print("  morpheus/references/examples-summary.md")
            zf.writestr("morpheus/references/examples-index.md", examples_index)
            print("  morpheus/references/examples-index.md")
            zf.writestr("morpheus/references/examples-manifest.json", examples_manifest)
            print("  morpheus/references/examples-manifest.json")

        for entry in entries:
            overview = build_overview(entry, source_commit)
            zf.writestr((Path("morpheus") / entry.overview_path).as_posix(), overview)
            print(f"  {(Path('morpheus') / entry.overview_path).as_posix()}")

        for file_info in example_files:
            add_local_file(zf, file_info.source, file_info.arcname)

    with zipfile.ZipFile(output_path, "r") as zf:
        file_count = len(zf.namelist())
        size_kb = sum(info.compress_size for info in zf.infolist()) // 1024

    print(f"\nCreated {output_path} ({file_count} files, {size_kb} KB)")


if __name__ == "__main__":
    build()
