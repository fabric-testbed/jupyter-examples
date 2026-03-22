#!/usr/bin/env python3
"""
Validate Jupyter notebooks against the project notebook specification.

Checks:
- Standard FABlib import pattern
- Presence of cleanup cell (slice.delete())
- Markdown title cell (H1 header)
- Step numbering in markdown headers
- Output cells are cleared
- Notebook metadata (kernel spec)

Usage:
    python tests/validate_notebooks.py                    # Validate all notebooks
    python tests/validate_notebooks.py path/to/nb.ipynb   # Validate specific notebook
    python tests/validate_notebooks.py --strict            # Fail on warnings too
"""

import json
import sys
import re
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    notebook: str
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    @property
    def passed(self):
        return len(self.errors) == 0

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


FABLIB_IMPORT_PATTERN = re.compile(
    r"from\s+fabrictestbed_extensions\.fablib\.fablib\s+import\s+FablibManager\s+as\s+fablib_manager"
)

FABLIB_INIT_PATTERN = re.compile(r"fablib\s*=\s*fablib_manager\(\)")

SLICE_DELETE_PATTERN = re.compile(r"slice\.delete\(\)")

H1_PATTERN = re.compile(r"^#\s+.+", re.MULTILINE)

STEP_PATTERN = re.compile(r"^##\s+Step\s+\d+", re.MULTILINE)

# Directories to skip (not standard FABlib examples)
SKIP_DIRS = {
    "public_demos",
    "acceptance_testing",
    "testing_and_debugging",
    "native_api",
    ".ipynb_checkpoints",
}


def load_notebook(path: Path) -> dict:
    """Load a notebook JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_cell_source(cell: dict) -> str:
    """Extract source text from a cell."""
    source = cell.get("source", [])
    if isinstance(source, list):
        return "".join(source)
    return source


def get_cell_type(cell: dict) -> str:
    return cell.get("cell_type", "")


def has_output(cell: dict) -> bool:
    """Check if a code cell has non-empty outputs."""
    outputs = cell.get("outputs", [])
    return len(outputs) > 0


def validate_notebook(path: Path) -> ValidationResult:
    """Validate a single notebook against the spec."""
    result = ValidationResult(notebook=str(path))

    try:
        nb = load_notebook(path)
    except json.JSONDecodeError as e:
        result.error(f"Invalid JSON: {e}")
        return result
    except Exception as e:
        result.error(f"Cannot read notebook: {e}")
        return result

    cells = nb.get("cells", [])
    if not cells:
        result.error("Notebook has no cells")
        return result

    # Check 1: First cell should be markdown with H1 title
    first_cell = cells[0]
    if get_cell_type(first_cell) != "markdown":
        result.error("First cell must be markdown (title/description)")
    else:
        source = get_cell_source(first_cell)
        if not H1_PATTERN.search(source):
            result.error("First markdown cell must contain an H1 header (# Title)")

    # Check 2: FABlib import pattern
    code_cells = [c for c in cells if get_cell_type(c) == "code"]
    all_code = "\n".join(get_cell_source(c) for c in code_cells)

    has_fablib_import = FABLIB_IMPORT_PATTERN.search(all_code)
    has_fablib_init = FABLIB_INIT_PATTERN.search(all_code)

    if has_fablib_import and not has_fablib_init:
        result.warn("Has FABlib import but missing 'fablib = fablib_manager()' initialization")

    # Check for non-standard import patterns
    if "import fablib" in all_code.lower() and not has_fablib_import:
        alt_import = re.search(r"(?:from|import).*fablib.*", all_code)
        if alt_import:
            result.warn(f"Non-standard FABlib import: {alt_import.group().strip()}")

    # Check 3: Cleanup cell (slice.delete())
    if has_fablib_import or "new_slice" in all_code:
        if not SLICE_DELETE_PATTERN.search(all_code):
            result.warn("No slice.delete() found — notebooks that create slices should clean up")

        # Check if delete is in the last code cell
        if code_cells and SLICE_DELETE_PATTERN.search(all_code):
            last_code = get_cell_source(code_cells[-1])
            if not SLICE_DELETE_PATTERN.search(last_code):
                result.warn("slice.delete() should be in the last code cell")

    # Check 4: Output cells should be cleared
    cells_with_output = []
    for i, cell in enumerate(cells):
        if get_cell_type(cell) == "code" and has_output(cell):
            cells_with_output.append(i + 1)

    if cells_with_output:
        if len(cells_with_output) <= 5:
            result.warn(f"Code cells with uncleared output: cells {cells_with_output}")
        else:
            result.warn(
                f"Code cells with uncleared output: {len(cells_with_output)} cells "
                f"(first: {cells_with_output[:3]}...)"
            )

    # Check 5: Notebook metadata
    metadata = nb.get("metadata", {})
    kernelspec = metadata.get("kernelspec", {})
    if kernelspec:
        language = kernelspec.get("language", "")
        if language and language != "python":
            result.error(f"Unexpected kernel language: {language} (expected python)")

    # Check 6: Step numbering
    markdown_cells = [c for c in cells if get_cell_type(c) == "markdown"]
    all_markdown = "\n".join(get_cell_source(c) for c in markdown_cells)
    steps = STEP_PATTERN.findall(all_markdown)
    if steps:
        # Extract step numbers and check they're sequential
        step_nums = []
        for step in steps:
            match = re.search(r"Step\s+(\d+)", step)
            if match:
                step_nums.append(int(match.group(1)))
        if step_nums:
            expected = list(range(step_nums[0], step_nums[0] + len(step_nums)))
            if step_nums != expected:
                result.warn(f"Step numbers not sequential: {step_nums}")

    # Check 7: Empty code cells
    empty_code = sum(1 for c in code_cells if not get_cell_source(c).strip())
    if empty_code:
        result.warn(f"{empty_code} empty code cell(s)")

    return result


def find_notebooks(root: Path) -> list:
    """Find all notebooks to validate."""
    notebooks = []
    for nb_path in sorted(root.rglob("*.ipynb")):
        # Skip checkpoints
        if ".ipynb_checkpoints" in str(nb_path):
            continue
        # Skip certain directories
        if any(skip in nb_path.parts for skip in SKIP_DIRS):
            continue
        notebooks.append(nb_path)
    return notebooks


def main():
    strict = "--strict" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if args:
        notebooks = [Path(a) for a in args]
    else:
        root = Path(__file__).parent.parent
        notebooks = find_notebooks(root)

    if not notebooks:
        print("No notebooks found to validate.")
        return 0

    results = []
    for nb_path in notebooks:
        result = validate_notebook(nb_path)
        results.append(result)

    # Print results
    errors_total = 0
    warnings_total = 0
    failed = []

    for result in results:
        if result.errors or result.warnings:
            print(f"\n{'FAIL' if result.errors else 'WARN'}: {result.notebook}")
            for err in result.errors:
                print(f"  ERROR: {err}")
            for warn in result.warnings:
                print(f"  WARNING: {warn}")

        errors_total += len(result.errors)
        warnings_total += len(result.warnings)
        if result.errors:
            failed.append(result.notebook)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Validated {len(results)} notebooks")
    print(f"  Passed: {len(results) - len(failed)}")
    print(f"  Failed: {len(failed)}")
    print(f"  Errors: {errors_total}")
    print(f"  Warnings: {warnings_total}")

    if strict and warnings_total > 0:
        print("\n(strict mode: warnings treated as failures)")
        return 1

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
