---
name: eugo-upstream-merge
description: Merge upstream NVIDIA/cudnn-frontend into the Eugo fork eugo-inc/cudnn-frontend-meson-python (canonical branch eugo-main). Covers the fork's meson-python divergence inventory, the merge recipe, the CLAUDE.md section 7 checklist, and the protomolecule commit-pin bump. Activates on "merge upstream", "upstream sync", "cudnn-frontend sync", "catch up to NVIDIA/cudnn-frontend", "bump cudnn frontend".
---

# Upstream merge: eugo-inc/cudnn-frontend-meson-python

## What this fork is / who consumes it

Fork of NVIDIA/cudnn-frontend (header-only C++ graph API + pybind11 python
bindings). Upstream builds with CMake + setuptools and ships NO CMake config
package; PyTorch discovers the headers via find_path (CUDNN_FRONTEND_INCLUDE_DIR).
The fork exists for one reason: meson-python (mesonpy) packaging, renamed
cuda-cudnn-frontend, with all deps (cudart, cuDNN, nlohmann_json, dlpack,
pybind11) taken from the system instead of FetchContent/vendored copies.

Consumer: protomolecule dependencies/python/wave_4/cuda_cudnn_frontend.
Its meta.json pins this repo by git_commit on branch eugo-main (version.kind =
"git_commit"). Because the pin is a commit, merging upstream here and adopting
it in protomolecule are DECOUPLED steps: a merge landed on eugo-main changes nothing
downstream until the meta.json commit is bumped. The setup script also symlinks
the installed <site-packages>/cudnn/include/* into EUGO_STANDARD_PATH/include
so downstream builds (torch) find the headers.

## Canonical branch: eugo-main (org-wide convention as of 2026-07-05)

eugo-main was realigned to the main tip on 2026-07-05 (the old divergent
eugo-main is preserved at tag archive/eugo-main-stale-pre-2026-07-05).
Per the org-wide convention, eugo-main is the canonical branch. The
transition is complete: the protomolecule pin
(python/wave_4/cuda_cudnn_frontend meta.json), the GitHub default
branch, and origin HEAD all point at eugo-main, and the old main
mirror branch has been deleted.

## Divergence inventory (fork vs upstream)

- meson.build - fork-only, the entire build: header manifest
  (cudnn_frontend_native_header_files), pybind11 extension source list,
  explicit -lnvrtc/-lcuda link_args, system-dep discovery via cmake method.
- pyproject.toml - fully rewritten: build-backend mesonpy, name
  cuda-cudnn-frontend, python >=3.12. Never accept upstream's wholesale.
- cmake/FindcuDNN.cmake - fork-only symlink -> cuDNN.cmake (meson's cmake
  dependency method needs the Find<Pkg>.cmake naming convention).
- include/cudnn_frontend_utils.h - system #include <nlohmann/json.hpp>,
  marked @EUGO_CHANGE (the fork's marker convention; see CLAUDE.md 4a).
- python/cudnn/__init__.py + CMakeLists.txt - version pinned in both; the
  meson.build sed regex requires the exact __version__ = "X.Y.Z" format.
- setup.py - fork-modified legacy fallback.
- .eugo/ - build helper scripts, notably eugo_meson_sync_headers.py which
  syncs the meson.build header manifest against include/.
- CLAUDE.md, .claude/skills/, .devcontainer/, .mcp.json - fork-only.

## Merge recipe

1. git remote add upstream https://github.com/NVIDIA/cudnn-frontend.git
   (if missing); git fetch upstream.
2. Branch off eugo-main. History uses <user>/feat/MM-DD-YY-merge-upstream
   (e.g. bwl1289/feat/05-02-26-merge-upstream); CLAUDE.md 6 suggests
   merge/upstream-YYYY-MM-DD. Either works.
3. git merge upstream/main - MERGE, never rebase (preserves upstream history
   for future syncs).
4. Resolve by ownership: fork-only files (meson.build, pyproject.toml,
   FindcuDNN.cmake) always ours; upstream-owned trees (include/, python/,
   samples/, test/) generally theirs, then re-apply @EUGO_CHANGE lines.
5. Run the FULL checklist in CLAUDE.md 7 - especially:
   ./.eugo/eugo_meson_sync_headers.py (header manifest), the python/*.cpp
   source-list comm check (load-bearing), the version-regex check,
   pyproject invariants, symlink check, pip install -v . and pytest
   test/python.
6. PR to eugo-main. Use the MERGE-COMMIT method ONLY - never squash: squashing
   destroys the upstream merge parent and breaks every future sync.

## Post-merge adoption (protomolecule)

After the PR merges to eugo-main, bump the pin in
protomolecule/dependencies/python/wave_4/cuda_cudnn_frontend/meta.json
(version.commit) to the new eugo-main tip, then rebuild that wave to validate
(torch in the same wave consumes the installed headers).

## Push-before-pin warning

meta.json pins by commit SHA. Only pin commits that are already pushed and
reachable from origin/eugo-main - pinning a local or branch-only SHA breaks the
protomolecule fetch. Push first, verify on GitHub, then update the pin.

## Related skills

- eugo-build-and-test - build/install commands, smoke test, protomolecule
  consumer flow (run after resolving, for checklist items g/h).
- eugo-meson-build-review - pre-commit cut of the CLAUDE.md 7 checklist for
  build-file changes made during the merge.
- eugo-rebuild - cheapest rebuild per diff; the post-merge pin-bump recipe.
