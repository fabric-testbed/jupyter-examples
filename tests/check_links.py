#!/usr/bin/env python3
"""
Check that all internal links in notebooks and start_here.ipynb are valid.

Validates:
- Relative file links in markdown cells (../path/to/file.ipynb)
- Image references (./figs/image.png)
- Links in start_here.ipynb point to existing notebooks

Usage:
    python tests/check_links.py                    # Check all notebooks
    python tests/check_links.py path/to/nb.ipynb   # Check specific notebook
"""

import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class LinkCheckResult:
    total_links: int = 0
    broken_links: list = field(default_factory=list)
    valid_links: int = 0

    @property
    def passed(self):
        return len(self.broken_links) == 0


# Match markdown links: [text](url) and <img src="url">
MD_LINK_PATTERN = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
IMG_SRC_PATTERN = re.compile(r'<img\s+[^>]*src=["\']([^"\']+)["\']')


def is_internal_link(url: str) -> bool:
    """Check if a link is a relative file path (not http/https/mailto)."""
    if url.startswith(("http://", "https://", "mailto:", "#", "ftp://")):
        return False
    if not url:
        return False
    return True


def resolve_link(notebook_path: Path, link: str) -> Path:
    """Resolve a relative link from a notebook's location."""
    # Strip fragment identifiers
    clean_link = link.split("#")[0].split("?")[0]
    if not clean_link:
        return None
    notebook_dir = notebook_path.parent
    return (notebook_dir / clean_link).resolve()


def extract_links_from_notebook(nb_path: Path) -> list:
    """Extract all internal links from a notebook's markdown cells."""
    try:
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

    links = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue

        source = cell.get("source", [])
        if isinstance(source, list):
            source = "".join(source)

        # Find markdown links
        for match in MD_LINK_PATTERN.finditer(source):
            text, url = match.group(1), match.group(2)
            if is_internal_link(url):
                links.append((text, url))

        # Find img src links
        for match in IMG_SRC_PATTERN.finditer(source):
            url = match.group(1)
            if is_internal_link(url):
                links.append(("(image)", url))

    return links


def check_notebook_links(nb_path: Path) -> list:
    """Check all internal links in a notebook, return list of broken ones."""
    links = extract_links_from_notebook(nb_path)
    broken = []

    for text, url in links:
        target = resolve_link(nb_path, url)
        if target is None:
            continue
        if not target.exists():
            broken.append((text, url, str(target)))

    return links, broken


def find_notebooks(root: Path) -> list:
    """Find all notebooks to check."""
    notebooks = []
    for nb_path in sorted(root.rglob("*.ipynb")):
        if ".ipynb_checkpoints" in str(nb_path):
            continue
        notebooks.append(nb_path)
    return notebooks


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if args:
        notebooks = [Path(a) for a in args]
    else:
        root = Path(__file__).parent.parent
        notebooks = find_notebooks(root)

    if not notebooks:
        print("No notebooks found to check.")
        return 0

    result = LinkCheckResult()
    files_with_broken = []

    for nb_path in notebooks:
        links, broken = check_notebook_links(nb_path)
        result.total_links += len(links)
        result.valid_links += len(links) - len(broken)

        if broken:
            files_with_broken.append(nb_path)
            print(f"\nBROKEN LINKS in: {nb_path}")
            for text, url, target in broken:
                result.broken_links.append({
                    "notebook": str(nb_path),
                    "text": text,
                    "url": url,
                    "target": target,
                })
                print(f"  [{text}]({url})")
                print(f"    -> {target} (NOT FOUND)")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Checked {len(notebooks)} notebooks")
    print(f"  Total internal links: {result.total_links}")
    print(f"  Valid: {result.valid_links}")
    print(f"  Broken: {len(result.broken_links)}")
    if files_with_broken:
        print(f"  Files with broken links: {len(files_with_broken)}")

    return 1 if result.broken_links else 0


if __name__ == "__main__":
    sys.exit(main())
