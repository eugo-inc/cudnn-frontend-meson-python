# CLAUDE.md

Fork of [`NVIDIA/cudnn-frontend`](https://github.com/NVIDIA/cudnn-frontend)
existing for ONE reason: a **Meson** build (package `cuda-cudnn-frontend`;
upstream is CMake+setuptools `nvidia-cudnn-frontend`). Python >= 3.12.
Dependencies (`cudart`, `cuDNN`, `dlpack`, `nlohmann_json`, `pybind11`) come
from the **system** — never FetchContent, never vendored.

## Hard stops

- NEVER rebase onto upstream (`git rebase`, `git pull --rebase`) -> always
  `git merge upstream/main`, even when asked for "the cleanest way".
- NEVER accept upstream's root `pyproject.toml` -> it reintroduces
  `setuptools.build_meta`; ours stays `mesonpy`. (Cherry-picking
  backend-agnostic metadata — `description`, `keywords`, `classifiers`,
  optional-dependencies — is fine if `[build-system]`, `name`,
  `requires-python`, `license`, `[project.urls]` stay ours.)
- NEVER `git checkout --theirs meson.build` -> it has no upstream counterpart,
  so a conflict there means something is wrong; investigate.
- NEVER skip the §7 checklist or bypass it with `git push --no-verify` ->
  type-checks don't catch missing headers; only a real `pip install -v .` does.
- NEVER add `.cu`/`.cuh` compilation to meson -> keep the extension_module
  source list `.cpp`-only; the C++ side is header-only.

Fork-only files — on merge conflict always keep ours: `meson.build` (entire
build; a merge conflict here = investigate), `pyproject.toml`,
`cmake/FindcuDNN.cmake` (symlink -> `cuDNN.cmake`; required because CMake
looks up `Find<Pkg>.cmake` by convention), `setup.py` (legacy fallback; fork
drops `PYBIND11_FINDPYTHON` + `FETCHCONTENT_SOURCE_DIR_DLPACK`, uses
`CMakeExtension("cudnn/_compiled_module")`).

## Layout in one breath

`include/` and `python/`, `python/pygraph/` are upstream (headers and pybind11
sources churn every release); `python/cudnn/__init__.py` is upstream with a
fork-pinned `__version__`; `meson.build` / `pyproject.toml` /
`cmake/FindcuDNN.cmake` are fork-only; `CMakeLists.txt` has a fork-pinned
`project(... VERSION)` at line 3 that must match `__version__` — update both
together. `tools/cudnn_repro/` is a separate self-contained setuptools CLI —
out of scope; §7(d) applies only to the ROOT `pyproject.toml`.

## Build & test

```bash
pip install -v .        # mesonpy -> meson.build
pytest test/python
```

Env required: `CUDAToolkit_ROOT`, `CUDNN_PATH`. Gotchas: `-lcuda` links a stub
at build time (driver provides `libcuda.so.1` at runtime); nlohmann/json is
system-provided — don't re-enable `CUDNN_FRONTEND_SKIP_JSON_LIB` plumbing.

## `@EUGO_CHANGE` markers

Every fork edit inside a file with upstream lineage gets a marker; unmarked
resolved lines will be treated as upstream content by the next merge and
silently overwritten. Trailing `# @EUGO_CHANGE: <reason>` (or `//` in C++);
multi-line blocks bracketed `# @EUGO_CHANGE BEGIN: <reason>` /
`# @EUGO_CHANGE END`. Reference example:
[include/cudnn_frontend_utils.h:40](include/cudnn_frontend_utils.h#L40).
Carve-outs: 100% fork-only files get NO markers ever (`meson.build`,
`pyproject.toml`, `cmake/FindcuDNN.cmake`, `CLAUDE.md`) — the file's existence
is the marker; new headers mirrored into the meson manifest are the fork's job,
not deviations — no marker; trivial whitespace needs none.

## Version pin — the sed contract

`python/cudnn/__init__.py` must keep `__version__ = "X.Y.Z"` — double quotes,
own line — because the sed at [meson.build:11-15](meson.build#L11-L15)
requires that exact shape (broke three times: `bf1da5b`, `332ac51`,
`be6863b`). Decide per-merge whether to bump to upstream's value; bumping ->
also bump `project(... VERSION)` at CMakeLists.txt line 3 (§7(c) verifies the
match). Watch
`symbols_to_import` (~lines 18-44): missing pybind11 re-exports surface as
`AttributeError` at import.

## Merge workflow

```bash
git remote -v                       # expect origin (eugo-inc) + upstream (NVIDIA)
git fetch upstream
git checkout eugo-main && git pull
git checkout -b merge/upstream-$(date +%Y-%m-%d)
git merge upstream/main             # merge, NEVER rebase
git status --short | grep -E '^(UU|AA|DD|AU|UA|DU|UD)'   # true conflicts only; leave plain M/A/D alone
# resolve each, git add it, re-check no UU lines remain, then run ALL of §7
```

## §7 MANDATORY post-merge checklist

Run every item in order; report pass/fail per item to the user BEFORE
suggesting `git push` or a PR. An item fails -> fix, then re-run only the
affected tail (e.g. header fix -> re-run (a), (g), (h)).

- **(a) Header manifest sync** — every `include/**/*.h` appears in
  `cudnn_frontend_native_header_files` ([meson.build:80](meson.build#L80)):
  `./.eugo/eugo_meson_sync_headers.py --check` (exit 1 = drift); apply mode
  appends new entries at block end — move them into their logical group by
  hand. Manifest is audit trail, not load-bearing (install_subdir ships the
  whole tree) — keep it accurate anyway. Script unavailable -> comm-diff
  `find include -name '*.h'` against `grep -oE "'include/[^']+\.h'" meson.build`.
- **(b) Python source sync** — every `python/*.cpp` + `python/pygraph/*.cpp`
  is in the `py.extension_module` list
  ([meson.build:193-206](meson.build#L193-L206)). This list IS load-bearing —
  a missing entry silently drops bindings:
  `comm -23 <(ls python/*.cpp python/pygraph/*.cpp | sort) <(grep -oE "'python/[^']+\.cpp'" meson.build | tr -d "'" | sort)`
  must print nothing.
- **(c) Version regex + pin match** —
  `sed -n 's/^__version__[[:space:]]*=[[:space:]]*"\([^"]*\)"/\1/p' python/cudnn/__init__.py`
  must print a version. Empty -> fix `__init__.py` formatting, NOT the regex
  (meson.build's own sed uses GNU `\s`; the POSIX form here is the portable
  local check — the difference is intentional). The same value must appear in
  `project(... VERSION ...)` at CMakeLists.txt line 3; mismatch -> update both
  together.
- **(d) pyproject invariants** —
  `grep -E "build-backend|^name|setuptools" pyproject.toml` shows
  `build-backend = 'mesonpy'`, `name = "cuda-cudnn-frontend"`, zero setuptools.
- **(e) Symlink** — `test -L cmake/FindcuDNN.cmake && readlink cmake/FindcuDNN.cmake`
  prints `cuDNN.cmake`.
- **(f) Re-exports valid** — each `symbols_to_import` symbol exists in
  upstream's pybind11 sources; add new upstream symbols, drop removed ones.
  Check (must print nothing):
  `for s in $(sed -n '/symbols_to_import/,/\]/p' python/cudnn/__init__.py | grep -oE '"[^"]+"' | tr -d '"'); do grep -qr "$s" python/*.cpp python/pygraph/*.cpp || echo "MISSING $s"; done`
- **(g) Build** — `pip install -v .` completes (missing headers surface here).
- **(h) Tests** — `pytest test/python` green.
- **(i) Markers** — every conflict you resolved in an upstream-lineage file
  carries `@EUGO_CHANGE`:
  `git diff upstream/main..HEAD -- '<file>' | grep -E '^\+' | grep -v '@EUGO_CHANGE' | head`
  -> each hit gets a marker or gets reverted.
- **(j) Report** — checklist summary to the user; then `git add` remaining
  files, `git commit` (default merge message fine),
  `git push -u origin merge/upstream-<date>`, open PR.

## Past incidents — symptom -> fix

- `__version__` sed prints nothing after merge -> formatting drift; restore the
  exact quoted-own-line shape.
- `ImportError: undefined symbol: nvrtcCreateProgram` -> upstream added an
  `experimental/*_shim.h` (they rely on dynamic loading; we don't). Fix: add
  `'-lnvrtc'` to the extension's `link_args`. Adding `nvrtc` to the `cuda`
  dependency's `components:` does NOT work — legacy `FindCUDA.cmake` silently
  drops it. Any NEW `*_shim.h` upstream adds likely needs a link addition too.
- `import cudnn` silently broken / empty namespace package -> the
  "double-cudnn" layout (`subdir: 'cudnn/cudnn/'` + install_dir ending in
  `/cudnn`). Correct: `subdir: 'cudnn/'`, `install_dir: py.get_install_dir()`;
  headers' `install_subdir('include', ... / 'cudnn')` is correct as-is (torch
  reads `<site-packages>/cudnn/include/` via `CUDNN_FRONTEND_INCLUDE_DIR`).
  meson.build comments mark this — don't reintroduce.
- Meson rpath deprecation warnings -> move every `-Wl,-rpath,X` from
  `link_args` into one colon-separated `install_rpath:` property;
  `--enable-new-dtags` / `--as-needed` stay in link_args.
- Whole new `include/` subtrees (`experimental/`, `generated/`) missed at (a)
  -> run the comm diffs blindly, never eyeball.
- History: system-nlohmann switch `dda2a36`; symlink workaround `c4d881f`;
  initial Meson port `0d82e12` (once forgotten, re-added).
