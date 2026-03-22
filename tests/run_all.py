#!/usr/bin/env python3
"""
Run all validation checks for the jupyter-examples repository.

Usage:
    python tests/run_all.py             # Run all checks
    python tests/run_all.py --strict    # Strict mode (warnings = failures)
"""

import subprocess
import sys
from pathlib import Path


CHECKS = [
    {
        "name": "Notebook Structure Validation",
        "script": "validate_notebooks.py",
        "description": "Validates notebook cell structure, FABlib patterns, and cleanup cells",
    },
    {
        "name": "Link Checker",
        "script": "check_links.py",
        "description": "Validates all internal links in notebooks point to existing files",
    },
    {
        "name": "Artifacts Registry",
        "script": "check_artifacts.py",
        "description": "Validates artifacts.json entries and cross-references with start_here.ipynb",
    },
]


def main():
    strict = "--strict" in sys.argv
    tests_dir = Path(__file__).parent
    python = sys.executable

    print("=" * 60)
    print("FABRIC Jupyter Examples — Validation Suite")
    print("=" * 60)

    results = []

    for check in CHECKS:
        script = tests_dir / check["script"]
        print(f"\n{'─' * 60}")
        print(f"Running: {check['name']}")
        print(f"  {check['description']}")
        print(f"{'─' * 60}")

        cmd = [python, str(script)]
        if strict:
            cmd.append("--strict")

        result = subprocess.run(cmd, capture_output=False)
        results.append({
            "name": check["name"],
            "returncode": result.returncode,
        })

    # Final summary
    print(f"\n{'=' * 60}")
    print("FINAL SUMMARY")
    print(f"{'=' * 60}")

    all_passed = True
    for r in results:
        status = "PASS" if r["returncode"] == 0 else "FAIL"
        if r["returncode"] != 0:
            all_passed = False
        print(f"  [{status}] {r['name']}")

    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
