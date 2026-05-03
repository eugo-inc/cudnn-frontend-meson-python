#!/usr/bin/env python3
"""Sync the `cudnn_frontend_native_header_files = files(...)` list in meson.build
to match the actual .h files under include/.

Usage:
  ./.eugo/eugo_meson_sync_headers.py             # apply changes (default)
  ./.eugo/eugo_meson_sync_headers.py --check     # exit nonzero if drift; no writes

See CLAUDE.md §7(a). The header list is a manifest, not load-bearing for the
build (install_subdir handles everything in include/), but keeping it accurate
makes upstream merges auditable: anyone reading meson.build can see exactly
which headers we ship.

Behavior of apply mode:
  - Existing entries that still exist on disk: kept in their original order
    (so human-curated grouping is preserved).
  - Headers on disk but missing from the list: appended at the end of the block.
  - Headers in the list but missing from disk: removed in place.
  - Comments on header lines (e.g. "# TODO+...") are NOT preserved when the
    line is rewritten, but lines we don't touch keep all their formatting.

Exit codes:
  0  in sync, or applied successfully
  1  drift exists (only in --check mode)
  2  bad CLI argument
  3  could not locate the files() block in meson.build
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MESON_FILE = REPO_ROOT / "meson.build"
INCLUDE_DIR = REPO_ROOT / "include"

BLOCK_START = re.compile(r"^cudnn_frontend_native_header_files\s*=\s*files\(\s*$")
BLOCK_END = re.compile(r"^\)\s*$")
HEADER_LINE = re.compile(r"'(include/[^']+\.h)'")


def actual_headers() -> list[str]:
    """All .h files under include/, sorted, as `include/...` repo-relative paths."""
    return sorted(
        str(p.relative_to(REPO_ROOT)).replace("\\", "/")
        for p in INCLUDE_DIR.rglob("*.h")
    )


def parse_block(text: str) -> tuple[list[str], int, int]:
    """Find the files() block. Returns (in-order paths, block_start_line, block_end_line).

    Lines that start with `#` (after whitespace) are skipped — commented-out
    headers are NOT considered listed.
    """
    lines = text.splitlines()
    start = end = -1
    paths: list[str] = []
    for i, line in enumerate(lines):
        if start < 0:
            if BLOCK_START.match(line):
                start = i
            continue
        if BLOCK_END.match(line):
            end = i
            break
        if line.lstrip().startswith("#"):
            continue
        m = HEADER_LINE.search(line)
        if m:
            paths.append(m.group(1))
    if start < 0 or end < 0:
        sys.stderr.write(
            "ERROR: could not find `cudnn_frontend_native_header_files = files(...)` "
            "block in meson.build\n"
        )
        sys.exit(3)
    return paths, start, end


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="print drift and exit nonzero if any; do not modify meson.build",
    )
    args = parser.parse_args()

    text = MESON_FILE.read_text()
    actual = actual_headers()
    current, block_start, block_end = parse_block(text)

    actual_set = set(actual)
    current_set = set(current)
    additions = sorted(actual_set - current_set)
    removals = sorted(current_set - actual_set)

    if not additions and not removals:
        print("✓ in sync (0 additions, 0 removals)")
        return 0

    print("Drift detected in cudnn_frontend_native_header_files:")
    if additions:
        print(f"  {len(additions)} additions:")
        for p in additions:
            print(f"    + {p}")
    if removals:
        print(f"  {len(removals)} removals:")
        for p in removals:
            print(f"    - {p}")

    if args.check:
        print("\nRun without --check to apply.")
        return 1

    # Rebuild the block:
    #   1. Keep existing entries that still exist on disk, in their original order.
    #   2. Append additions.
    new_paths = [p for p in current if p in actual_set] + additions

    lines = text.splitlines()
    rebuilt = (
        [lines[block_start]]                          # `cudnn_frontend_native_header_files = files(`
        + [f"    '{p}'," for p in new_paths]
        + [lines[block_end]]                          # `)`
    )
    new_lines = lines[:block_start] + rebuilt + lines[block_end + 1 :]
    new_text = "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")

    MESON_FILE.write_text(new_text)
    print(f"\n✓ applied: rewrote {block_end - block_start - 1} → {len(new_paths)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
