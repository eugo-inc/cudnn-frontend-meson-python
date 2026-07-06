---
name: eugo-rebuild
description: Decide what level of rebuild a change to cudnn-frontend-meson-python actually requires and pick the cheapest correct option - docs-only (nothing), pure-python (reinstall), build-file (configure gate then full), headers/cpp (full build), and when the protomolecule meta.json commit pin must be bumped. Activates on "do I need to rebuild", "rebuild cudnn frontend", "incremental cudnn build", "configure check", "bump the cudnn frontend pin", "is this a python-only change".
---

# eugo-rebuild: cheapest correct rebuild

Walk the diff (`git diff --name-only`) and take the FIRST matching row.

| Files changed | Action |
|---------------|--------|
| Docs only: README, CLAUDE.md, `.claude/`, `.github/`, `samples/`, `benchmark/`, `tools/` | Nothing. These do not enter the wheel build. |
| `test/` only | No build. Run `pytest test/python` (needs a GPU). |
| Pure python: `python/cudnn/*.py` | Reinstall: `pip install -v .` (mesonpy copies `.py` verbatim; no compile). If the `__version__` line moved, FIRST verify the sed still extracts it (see eugo-meson-build-review). |
| `meson.build`, `pyproject.toml`, `cmake/cuDNN.cmake`, `cmake/FindcuDNN.cmake` | Configure gate FIRST: `./.eugo/eugo_meson_setup.sh` (~seconds; catches dep-discovery and version-extraction breakage). Then full build. |
| Headers: `include/**` added/removed/edited | Full build (headers compile into the extension). On add/remove also run `./.eugo/eugo_meson_sync_headers.py` to keep the meson.build manifest honest. |
| Extension sources: `python/*.cpp`, `python/pygraph/*.cpp` | Full build. New files MUST be added to the `py.extension_module` source list (load-bearing - missing entries silently drop bindings). |
| Mixed / unsure | Configure gate, then full build. |

## The two build levels

```bash
# Configure gate (cheap, no compile)
./.eugo/eugo_meson_setup.sh

# Full build + install (canonical)
pip3 install . ${EUGO_PIP_COMPILABLE_PACKAGE_OPTIONS} ${EUGO_MESONPY_COMMON_OPTIONS}
# (outside the harness env: pip install -v . with CUDAToolkit_ROOT/CUDNN_PATH set)
```

After any full build, run the smoke test from the eugo-build-and-test skill
(import cudnn from outside the repo dir).

## When protomolecule must be rebuilt / pin-bumped

protomolecule's `dependencies/python/wave_4/cuda_cudnn_frontend/meta.json`
pins this repo by `version.commit` on branch eugo-main. Consequences:

- Landing a change on eugo-main changes NOTHING downstream until the pin is bumped.
- Bump when the change should ship: set `version.commit` to the new eugo-main tip,
  then rebuild that protomolecule wave (torch consumes the installed headers
  via `CUDNN_FRONTEND_INCLUDE_PATH`, so a header-affecting bump must be
  validated by a torch build, not just this package's install).
- PUSH BEFORE PIN: only pin SHAs already reachable from origin/eugo-main - a
  local-only SHA breaks the protomolecule fetch.

## Related

- eugo-build-and-test (commands, smoke test), eugo-meson-build-review
  (pre-commit checks), eugo-upstream-merge (post-merge full checklist).
