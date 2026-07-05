---
name: eugo-meson-build-review
description: Pre-commit review checklist for build-file changes in cudnn-frontend-meson-python - meson.build, pyproject.toml, cmake/, setup.py. Verifies the header manifest, the load-bearing extension source list, the version-sed contract, pyproject/mesonpy invariants, the FindcuDNN symlink, @EUGO_CHANGE marker discipline, and the link/rpath/install flags that must not regress. Activates on "review meson changes", "check meson.build", "pre-commit build review", "validate pyproject", "EUGO_CHANGE markers", "header manifest drift".
---

# Meson build review (pre-commit)

Run this before committing any change to meson.build, pyproject.toml,
`cmake/`, or setup.py. Backbone is CLAUDE.md sections 4 (fork-only files),
4a (@EUGO_CHANGE), 7 (checklist) and 8 (past incidents) - this skill is the
condensed pre-commit cut of it; defer to CLAUDE.md when they disagree.

## Mechanical checks (all must pass)

```bash
# 1. Header manifest in sync with include/ (audit trail; not load-bearing -
#    install_subdir ships the whole tree regardless, but keep it honest)
./.eugo/eugo_meson_sync_headers.py --check

# 2. Extension source list - LOAD-BEARING; a missing .cpp silently drops bindings
comm -23 <(ls python/*.cpp python/pygraph/*.cpp | sort) \
         <(grep -oE "'python/[^']+\.cpp'" meson.build | tr -d "'" | sort)   # must be empty

# 3. Version extraction contract (meson.build runs sed over __init__.py)
sed -n 's/^__version__[[:space:]]*=[[:space:]]*"\([^"]*\)"/\1/p' python/cudnn/__init__.py
# must print a version; if empty, fix __init__.py formatting, NOT the regex

# 4. pyproject invariants
grep -E "build-backend|^name|requires-python|setuptools" pyproject.toml
# expect: mesonpy backend, name cuda-cudnn-frontend, >=3.12, NO setuptools hits

# 5. cuDNN finder symlink (meson's cmake method needs Find<Pkg>.cmake naming)
test -L cmake/FindcuDNN.cmake && readlink cmake/FindcuDNN.cmake   # -> cuDNN.cmake
```

## @EUGO_CHANGE discipline (CLAUDE.md 4a)

- Every edit inside an upstream-lineage file (setup.py, CMakeLists.txt,
  `include/`, `python/`) carries an inline `# @EUGO_CHANGE: <why>` marker
  (or a BEGIN/END block for multi-line additions).
- Fork-only files get NO markers, ever: meson.build, pyproject.toml,
  cmake/FindcuDNN.cmake, CLAUDE.md, `.claude/`, `.eugo/`. Existence is the
  marker; per-line annotations there are noise.
- Version pin edits touch TWO files together: `python/cudnn/__init__.py`
  (`__version__`) and CMakeLists.txt (`project(... VERSION ...)`).

## Invariants that must not regress (each has burned us; CLAUDE.md 8)

- `wrap_mode=nofallback` stays; all deps (cudart, cuDNN, nlohmann_json,
  dlpack, pybind11) come from the system - no subprojects, no FetchContent,
  no re-enabling upstream's `CUDNN_FRONTEND_SKIP_JSON_LIB` plumbing.
- Never define `NV_CUDNN_FRONTEND_USE_DYNAMIC_LOADING` - we hard-link
  deliberately (see the comment block on the extension in meson.build).
- `-lcuda` and `-lnvrtc` stay in the extension's `link_args`. Do NOT move
  nvrtc into the `cuda` dependency's `components:` - the legacy
  `find_package(CUDA)` path silently drops it (past ImportError incident).
  New upstream `experimental/*_shim.h` headers likely need a new `-l<lib>`.
- rpaths live ONLY in `install_rpath: '$ORIGIN:$ORIGIN/../lib:$ORIGIN/../nvidia/cudnn/lib'`
  - never `-Wl,-rpath,...` in link_args (meson will hard-error in future).
- Wheel layout: extension `subdir: 'cudnn/'`; `install_subdir('python/cudnn/',
  install_dir: py.get_install_dir())`; headers
  `install_subdir('include', install_dir: py.get_install_dir() / 'cudnn')`.
  Any drift risks the double-cudnn namespace bug or breaks the protomolecule
  header symlink that torch's `CUDNN_FRONTEND_INCLUDE_PATH` reads.
- No `.cu`/`.cuh` compilation, no CUDA language in `project()` - the C++
  side is header-only.

## Verify before commit

Configure gate + full install + import smoke, per the eugo-build-and-test
skill. A meson.build mistake that survives the mechanical checks (e.g. a
mis-listed header) surfaces as a missing-file error at `meson setup` or as
an ImportError at the smoke test - type-level review alone catches neither.

## Related

- eugo-build-and-test, eugo-rebuild, eugo-upstream-merge (run the full
  CLAUDE.md section 7 checklist there, of which this is a subset), meson.
