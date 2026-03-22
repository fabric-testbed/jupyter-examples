#!/usr/bin/env python3
"""
Validate artifacts.json consistency with the actual directory structure.

Checks:
- Every entry in artifacts.json has a corresponding directory
- Every example directory has an entry in artifacts.json (optional, with --strict)
- Required fields are present in each entry
- No duplicate keys or locations
- Cross-reference with start_here.ipynb links

Usage:
    python tests/check_artifacts.py             # Basic validation
    python tests/check_artifacts.py --strict    # Also check for missing entries
"""

import json
import sys
import re
from pathlib import Path
from collections import Counter


REQUIRED_FIELDS = ["title", "description_short", "location", "tags", "visibility", "authors"]

# Known example directories under fabric_examples/fablib_api/
# that should have artifacts.json entries
FABLIB_API_DIR = "fabric_examples/fablib_api"
COMPLEX_RECIPES_DIR = "fabric_examples/complex_recipes"


def load_artifacts(root: Path) -> dict:
    """Load artifacts.json."""
    artifacts_path = root / "artifacts.json"
    if not artifacts_path.exists():
        print("ERROR: artifacts.json not found")
        sys.exit(1)

    with open(artifacts_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_entry(key: str, entry: dict, root: Path) -> list:
    """Validate a single artifacts.json entry."""
    errors = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"[{key}] Missing required field: {field}")
        elif not entry[field] and field != "description_long":
            if field in ("title", "description_short", "location"):
                errors.append(f"[{key}] Empty required field: {field}")

    # Check location exists
    location = entry.get("location", "")
    if location:
        loc_path = root / location
        if not loc_path.exists():
            errors.append(f"[{key}] Location does not exist: {location}")
        elif not loc_path.is_dir():
            errors.append(f"[{key}] Location is not a directory: {location}")

    # Check tags is a list
    tags = entry.get("tags", [])
    if not isinstance(tags, list):
        errors.append(f"[{key}] Tags must be a list")

    # Check authors is a list
    authors = entry.get("authors", [])
    if not isinstance(authors, list):
        errors.append(f"[{key}] Authors must be a list")
    elif not authors:
        errors.append(f"[{key}] Authors list is empty")

    # Check visibility
    visibility = entry.get("visibility", "")
    if visibility and visibility not in ("public", "private"):
        errors.append(f"[{key}] Invalid visibility: {visibility} (expected public or private)")

    return errors


def find_example_dirs(root: Path) -> set:
    """Find all example directories that contain notebooks."""
    example_dirs = set()

    for category_dir in [FABLIB_API_DIR, COMPLEX_RECIPES_DIR]:
        category_path = root / category_dir
        if not category_path.exists():
            continue

        for subdir in category_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("."):
                # Check if it contains at least one notebook
                notebooks = list(subdir.glob("*.ipynb"))
                if notebooks:
                    rel_path = str(subdir.relative_to(root))
                    example_dirs.add(rel_path)

    return example_dirs


def extract_start_here_links(root: Path) -> set:
    """Extract notebook paths from start_here.ipynb."""
    start_here = root / "start_here.ipynb"
    if not start_here.exists():
        return set()

    with open(start_here, "r", encoding="utf-8") as f:
        nb = json.load(f)

    links = set()
    link_pattern = re.compile(r'\]\(\./([^)]+\.ipynb)\)')

    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        source = cell.get("source", [])
        if isinstance(source, list):
            source = "".join(source)

        for match in link_pattern.finditer(source):
            links.add(match.group(1))

    return links


def main():
    strict = "--strict" in sys.argv
    root = Path(__file__).parent.parent

    artifacts = load_artifacts(root)
    errors = []
    warnings = []

    # Check for duplicate locations
    locations = [entry.get("location", "") for entry in artifacts.values()]
    location_counts = Counter(locations)
    for loc, count in location_counts.items():
        if count > 1 and loc:
            errors.append(f"Duplicate location '{loc}' appears {count} times")

    # Validate each entry
    for key, entry in artifacts.items():
        entry_errors = validate_entry(key, entry, root)
        errors.extend(entry_errors)

    # Check for example dirs missing from artifacts.json
    if strict:
        artifact_locations = {entry.get("location", "") for entry in artifacts.values()}
        example_dirs = find_example_dirs(root)

        for dir_path in sorted(example_dirs):
            if dir_path not in artifact_locations:
                # Check if any artifact location is a parent
                has_parent = any(dir_path.startswith(loc) for loc in artifact_locations if loc)
                if not has_parent:
                    warnings.append(f"Directory '{dir_path}' has notebooks but no artifacts.json entry")

    # Cross-reference with start_here.ipynb
    start_here_links = extract_start_here_links(root)
    for link in sorted(start_here_links):
        link_path = root / link
        if not link_path.exists():
            warnings.append(f"start_here.ipynb links to non-existent: {link}")

    # Print results
    if errors:
        print("ERRORS:")
        for err in errors:
            print(f"  {err}")

    if warnings:
        print("\nWARNINGS:")
        for warn in warnings:
            print(f"  {warn}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Validated {len(artifacts)} artifact entries")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    if start_here_links:
        print(f"  start_here.ipynb links checked: {len(start_here_links)}")

    if strict and warnings:
        return 1
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
