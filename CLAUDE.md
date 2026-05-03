# CLAUDE.md

This file is loaded into every Claude Code session in this repo. Its purpose is to make merging from upstream `NVIDIA/cudnn-frontend` reliable, and to give a fast orientation for general dev work.

## 1. Fork purpose & invariants

This repo is a fork of [`NVIDIA/cudnn-frontend`](https://github.com/NVIDIA/cudnn-frontend). The fork exists for **one reason**: to provide a **Meson** build system (renamed package: `cuda-cudnn-frontend`, upstream is `nvidia-cudnn-frontend`). Upstream uses CMake + setuptools.

Hard invariants — do not change without explicit user direction:
- Build backend is `mesonpy`. **Never** accept upstream's `pyproject.toml` during a merge — it would re-introduce `setuptools.build_meta`.
- Python ≥3.12 is required.
- Dependencies (`cudart`, `cuDNN`, `dlpack`, `nlohmann_json`, `pybind11`) come from the **system**, not from FetchContent or vendored copies.
- **We integrate upstream by merging, not rebasing.** Use `git merge upstream/main` (see §6).

## 2. Repo layout

| Path | Owner | Notes |
|---|---|---|
| `include/` | upstream | Header-only C++ frontend. Files added/removed here every release. |
| `python/cudnn/` | upstream (mostly) | Pure-python package. The `__version__` line is fork-pinned. |
| `python/`, `python/pygraph/` | upstream | pybind11 sources. |
| [meson.build](meson.build) | **fork** | The build. Carries an explicit header list + cpp source list. |
| [pyproject.toml](pyproject.toml) | **fork** | mesonpy config. |
| [cmake/FindcuDNN.cmake](cmake/FindcuDNN.cmake) | **fork** | Symlink → `cuDNN.cmake`; lets meson find cuDNN via the CMake `Find<Pkg>.cmake` module convention. |
| [setup.py](setup.py) | fork-modified | Legacy CMake build helper, kept as fallback. |
| [CMakeLists.txt](CMakeLists.txt) | upstream + fork-pinned version | Project version is pinned to match `__version__`. |
| `test/python/` | upstream | pytest suite. |
| `samples/`, `benchmark/`, `tools/` | upstream | Examples — do not affect the build. |
| `tools/cudnn_repro/` | upstream | A *separate, self-contained* CLI package with its own `pyproject.toml` using setuptools. **Out of scope for the main fork's build.** §7(d)'s checks apply only to the **root** `pyproject.toml`. |

## 3. Local dev — build & test

```bash
# Build & install (drives mesonpy → meson.build)
pip install -v .

# Run the python tests
pytest test/python
```

Required environment:
- `CUDAToolkit_ROOT` — CUDA install root.
- `CUDNN_PATH` — cuDNN install root.

The Meson `cuDNN` finder relies on the symlink `cmake/FindcuDNN.cmake → cuDNN.cmake` (the symlink is required because CMake looks for `Find<Pkg>.cmake` by convention while the real implementation lives in `cuDNN.cmake`). If the symlink is broken, dependency resolution at [meson.build:51](meson.build#L51) fails.

Common gotchas:
- `libcuda.so.1` is provided by the NVIDIA driver at runtime; at build time we link `-lcuda` against a stub ([meson.build:188](meson.build#L188)).
- nlohmann/json is system-provided — do not re-enable upstream's `CUDNN_FRONTEND_SKIP_JSON_LIB` plumbing.
- The fork doesn't compile any `.cu`/`.cuh` files. Don't add CUDA compilation to meson.

## 4. Fork-only files — NEVER overwrite from upstream

During a merge conflict on these, **always keep ours** (`git checkout --ours <file>` or manual resolution preserving fork content):

- [meson.build](meson.build) — entire file is fork-only; should never appear in `git status` after a merge unless something is wrong.
- [cmake/FindcuDNN.cmake](cmake/FindcuDNN.cmake) — symlink to `cmake/cuDNN.cmake`.
- [pyproject.toml](pyproject.toml) — fork rewrites this completely (mesonpy backend, `cuda-cudnn-frontend` name, fork authors). Never accept upstream wholesale. **Selective pull-in is fine**: build-backend-agnostic metadata (e.g. `description`, `keywords`, `classifiers`, `[project.optional-dependencies]`) can be cherry-picked from upstream as long as the `[build-system]` block, `name`, `requires-python`, `license`, and `[project.urls]` stay ours.
- [setup.py](setup.py) — fork removes `PYBIND11_FINDPYTHON` and `FETCHCONTENT_SOURCE_DIR_DLPACK` handling, and changes `CMakeExtension("cudnn._compiled_module")` → `CMakeExtension("cudnn/_compiled_module")`. Resolve in fork's favor.

## 4a. The `@EUGO_CHANGE` marker — MANDATORY on every fork edit

**Every fork modification to upstream content must be marked with an `@EUGO_CHANGE` comment.** This makes future upstream merges auditable: a reviewer (or `grep`) can find every fork deviation in seconds, and a merger knows which conflict-resolution lines are intentional fork behavior vs accidental drift.

### Format

Inline trailing comment with a short reason:

| Language | Syntax |
|---|---|
| C / C++ | `... // @EUGO_CHANGE: <reason>` |
| Python / TOML / Meson / CMake / shell | `... # @EUGO_CHANGE: <reason>` |
| Markdown / YAML / etc. | `<!-- @EUGO_CHANGE: <reason> -->` |

For multi-line additions, bracket the block:
```
# @EUGO_CHANGE BEGIN: <reason>
... lines ...
# @EUGO_CHANGE END
```

Existing reference example: [include/cudnn_frontend_utils.h:40](include/cudnn_frontend_utils.h#L40) —
```cpp
#include <nlohmann/json.hpp> // @EUGO_CHANGE: Changed to use our system version of nlohmann
```

### When to mark

- **Always mark**: any line we add, change, or comment-out inside a file that has any upstream lineage. Examples: edits to [setup.py](setup.py), the version pin in [CMakeLists.txt](CMakeLists.txt), the `__version__` line in [python/cudnn/__init__.py](python/cudnn/__init__.py), header includes added to upstream `.h`/`.cpp` files, Python symbol re-export changes in `__init__.py`.

### When NOT to mark

- **Files that are 100% fork-only get no markers, ever** — not even for "merge audit" blocks. This applies to [meson.build](meson.build), [pyproject.toml](pyproject.toml), [cmake/FindcuDNN.cmake](cmake/FindcuDNN.cmake), and `CLAUDE.md` itself. The file's existence is the marker; per-line annotations inside these files are noise. New headers we add to the `cudnn_frontend_native_header_files` list when upstream introduces them are *not* deviations — they're the fork's job to mirror upstream's reality. No marker.
- Trivial whitespace/formatting touches do not need markers.

### Enforcement

The §7 checklist below assumes any non-trivial edit you make during a merge is marked. If you resolve a conflict in an upstream-lineage file without an `@EUGO_CHANGE` marker on the resolved lines, a future merge will treat those lines as upstream content and may silently overwrite them.

## 5. Fork-modified files — careful three-way merge

- [python/cudnn/__init__.py](python/cudnn/__init__.py)
  - Fork pins `__version__ = "1.14.0"`. Decide per-merge whether to bump to upstream's value.
  - **Critical**: the line must remain `__version__ = "X.Y.Z"` with double quotes on its own line. The sed regex at [meson.build:11-15](meson.build#L11-L15) requires this exact format. Past breakages: commits `bf1da5b`, `332ac51`, `be6863b`.
  - Watch `symbols_to_import` (around lines 18-44) — upstream may add/remove pybind11 symbol re-exports. Missing symbols surface as `AttributeError` at import time.
- [CMakeLists.txt](CMakeLists.txt) — fork pins `project(cudnn_frontend VERSION X.Y.Z)` at line 3 to match `__version__`. Update both together.

## 6. Upstream merge workflow

**We merge, we do not rebase.** Do not propose `git rebase upstream/main` or `git pull --rebase` — preserve upstream's history as merge commits so the relationship between fork and upstream stays auditable. If a session asks for "the cleanest way to pull in upstream", the answer is still `git merge`.

```bash
# Sanity: confirm both remotes are wired up
git remote -v   # expect: origin (eugo-inc) and upstream (NVIDIA)
# If upstream is missing:
# git remote add upstream https://github.com/NVIDIA/cudnn-frontend.git

git fetch upstream
git checkout main && git pull
git checkout -b merge/upstream-$(date +%Y-%m-%d)
git merge upstream/main          # <- merge, NEVER rebase
```

If there are conflicts, identify the *actually-conflicted* files (not all the auto-merged ones) with:
```bash
git status --short | grep -E '^(UU|AA|DD|AU|UA|DU|UD)'
```
The plain `M`/`A`/`D` lines in `git status` are auto-merged or upstream-only changes — leave them alone.

After editing each conflicted file to resolve, run `git add <file>` so git marks it resolved, then re-check `git status` is clean of `UU` lines. **Then execute the §7 checklist in full** before `git commit` (the merge commit) and any `git push`.

## 7. MANDATORY upstream-merge checklist

After resolving merge conflicts, Claude must run every item in this checklist, in order, and report pass/fail for each before suggesting `git push` or opening a PR. Do not skip steps. Do not declare the merge done until item (i) is complete.

- [ ] **(a) Header list sync** — every `.h` under `include/` appears in `cudnn_frontend_native_header_files` at [meson.build:65](meson.build#L65):
  ```bash
  # Headers in tree but missing from meson.build (need to ADD):
  comm -23 \
    <(cd include && find . -name '*.h' | sed 's|^\./|include/|' | sort) \
    <(grep -oE "'include/[^']+\.h'" meson.build | tr -d "'" | sort)
  # Headers in meson.build but no longer in tree (need to REMOVE):
  comm -13 \
    <(cd include && find . -name '*.h' | sed 's|^\./|include/|' | sort) \
    <(grep -oE "'include/[^']+\.h'" meson.build | tr -d "'" | sort)
  ```
  Both outputs must be empty. Edit `meson.build`'s `cudnn_frontend_native_header_files = files(...)` block: append additions (group new top-level subtrees like `experimental/`, `generated/` together for readability), delete removals.

  **Note**: this list is a *manifest*, not load-bearing for the build. The actual install happens via `install_subdir('include', ...)` at [meson.build:144](meson.build#L144), which copies the entire `include/` tree regardless. Drift here won't break `pip install`, but the manifest's whole point is to be an audit trail of what we ship — keep it accurate.

- [ ] **(b) Python binding source sync** — every `.cpp` in `python/` and `python/pygraph/` appears in the `py.extension_module` source list at [meson.build:163-173](meson.build#L163-L173). Unlike (a), this list **is** load-bearing — missing entries silently drop bindings:
  ```bash
  comm -23 \
    <(ls python/*.cpp python/pygraph/*.cpp | sort) \
    <(grep -oE "'python/[^']+\.cpp'" meson.build | tr -d "'" | sort)
  ```
  Output must be empty. Add new sources upstream introduced.

- [ ] **(c) Version regex still matches**:
  ```bash
  sed -n 's/^__version__[[:space:]]*=[[:space:]]*"\([^"]*\)"/\1/p' python/cudnn/__init__.py
  ```
  Must print a non-empty version string. If it doesn't, fix `__init__.py` formatting (not the regex). Note: meson.build uses `\s` (GNU sed) instead of `[[:space:]]` — the POSIX form above is portable to macOS BSD sed for local checks.

- [ ] **(d) `pyproject.toml` invariants intact**: `build-backend = 'mesonpy'`, `name = "cuda-cudnn-frontend"`, no `setuptools` or `setuptools.build_meta` references:
  ```bash
  grep -E "build-backend|^name|setuptools" pyproject.toml
  ```

- [ ] **(e) cuDNN cmake symlink intact**:
  ```bash
  test -L cmake/FindcuDNN.cmake && readlink cmake/FindcuDNN.cmake
  ```
  Must print `cuDNN.cmake`.

- [ ] **(f) `__init__.py` symbol re-exports valid** — read [python/cudnn/__init__.py:18-44](python/cudnn/__init__.py#L18-L44) (`symbols_to_import`) and confirm each symbol exists in upstream's pybind11 sources. New upstream symbols may need to be added; removed ones must be dropped.

- [ ] **(g) Build passes**: `pip install -v .` completes without error. Header-list mistakes show up here as missing-file errors from meson.

- [ ] **(h) Tests pass**: `pytest test/python` is green.

- [ ] **(i) `@EUGO_CHANGE` markers present on every fork edit** — for each conflict you resolved in an upstream-lineage file, confirm the resolved lines carry an `@EUGO_CHANGE` marker (per §4a). Quick audit:
  ```bash
  git diff upstream/main..HEAD -- '<modified-file>' | grep -E '^\+' | grep -v '@EUGO_CHANGE' | head
  ```
  Any added line without a marker should either get one or be reverted.

- [ ] **(j) Report** — post a checklist summary back to the user (which boxes passed, which were skipped and why) before suggesting `git push`.

If any item fails: fix the cause, then re-run **only the affected tail** of the checklist. For example, a header-list fix requires re-running (a), (g), (h).

After (j), the merge is mergeable: `git add` any remaining resolved files, then `git commit` (default merge commit message is fine), then `git push -u origin merge/upstream-<date>` and open the PR.

## 8. Past incidents

- Version regex broke after `__init__.py` formatting drift → `bf1da5b`, `332ac51`, `be6863b`.
- Switched FetchContent nlohmann → system nlohmann → `dda2a36`.
- cuDNN cmake symlink workaround introduced → `c4d881f`.
- Initial Meson port commit (forgotten then re-added) → `0d82e12`.
- Upstream merge introduced two **new top-level subtrees** in `include/` (`experimental/`, `generated/`) — easy to miss on §7(a) if you only think of "individual new headers." Always run the `comm` diffs blindly rather than trusting a glance.
- "Double-cudnn" wheel install layout bug: meson.build originally had `subdir: 'cudnn/cudnn/'` for the extension and `install_dir: py.get_install_dir() / 'cudnn'` for `install_subdir('python/cudnn/', ...)`. Together those produced `<site-packages>/cudnn/cudnn/` — making `cudnn` an empty PEP-420 namespace package and silently breaking `import cudnn` and `from cudnn.X import …`. Fix: `subdir: 'cudnn/'` and `install_dir: py.get_install_dir()` respectively. The headers' `install_subdir('include', install_dir: py.get_install_dir() / 'cudnn')` is correct as-is — it produces `<site-packages>/cudnn/include/` which is what torch reads via `CUDNN_FRONTEND_INCLUDE_DIR`. Inline comments in meson.build call this out; don't reintroduce it on a future merge.
- Missing `nvrtc` link → `ImportError: undefined symbol: nvrtcCreateProgram`. Triggered when upstream introduced [include/cudnn_frontend/experimental/nvrtc_shim.h](include/cudnn_frontend/experimental/nvrtc_shim.h) (transitively pulled in via `oss_engine_interface.h`). Without `NV_CUDNN_FRONTEND_USE_DYNAMIC_LOADING` (which we don't set, see meson.build comment block on the python extension), the `NV_FE_CALL_TO_NVRTC` macro expands to direct `nvrtcCreateProgram(...)` calls and needs `-lnvrtc`. **First-attempt fix that did NOT work**: adding `'nvrtc'` to the `components: [...]` list of the `cuda` cmake dependency. Reason: meson's `dependency('CUDA', method: 'cmake', ...)` invokes the legacy `find_package(CUDA)` (`FindCUDA.cmake`), which does not recognize `nvrtc` as a component and silently drops it. **Working fix**: add `'-lnvrtc'` to `link_args:` of the python extension (mirrors the `-lcuda` pattern). Cleaner long-term option: switch to `dependency('CUDAToolkit', method: 'cmake', ...)` which does support `nvrtc` as a component — not yet validated end-to-end. Generally: any new `*_shim.h` upstream adds in `experimental/` likely needs a corresponding link-time addition for us, since upstream's wheel relies on dynamic loading and we don't.
- Meson rpath warnings (will become hard errors in a future release): `'-Wl,-rpath,$ORIGIN[/...]'` passed via `link_args:` triggers "Please do not define rpath with a linker argument, use install_rpath or build_rpath properties instead." Fix: move all `-Wl,-rpath,X` entries into a single `install_rpath: 'A:B:C'` property (colon-separated) on the `extension_module` call. The `-Wl,--enable-new-dtags` and `-Wl,--as-needed` link_args are unrelated and stay where they are.

## 9. What NOT to do

- Don't rebase onto upstream. Use `git merge upstream/main`. See §6.
- Don't accept upstream's `pyproject.toml` wholesale — deletes the mesonpy backend.
- Don't `git checkout --theirs meson.build` — it has no upstream counterpart, so a conflict means something is wrong; investigate.
- Don't bypass the §7 checklist by `git push --no-verify` or by skipping `pip install -v .`. Type-checks alone don't catch missing-header errors — only an actual meson build does.
- Don't add CUDA `.cu`/`.cuh` compilation to meson.build — the project is header-only on the C++ side.
