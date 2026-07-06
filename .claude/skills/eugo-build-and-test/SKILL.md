---
name: eugo-build-and-test
description: Build, install, and smoke-test the cuda-cudnn-frontend meson-python wheel - the local meson-setup fast gate, the canonical pip install, the import-cudnn smoke checks, and how the protomolecule package (python/wave_4/cuda_cudnn_frontend) actually builds and ships it (git-commit pin, pip options, the header symlink into /usr/local/include that torch consumes). Activates on "build cudnn frontend", "install cuda-cudnn-frontend", "pip install cudnn frontend", "smoke test cudnn", "meson setup cudnn frontend", "build the cudnn wheel", "diagnose cudnn frontend build failure".
---

# Build & test: cuda-cudnn-frontend

The repo playbook is CLAUDE.md - sections 3 (local build & test), 7(g)/(h)
(build/test gates), and 8 (past incidents / failure modes). Read those before
debugging; this skill adds the eugo-container commands and the
protomolecule-consumer side, and does not duplicate the playbook.

## What a build produces

mesonpy wheel `cuda-cudnn-frontend` (upstream PyPI name is
`nvidia-cudnn-frontend` - any requirement on that name means this package).
Healthy install layout in `<site-packages>/cudnn/`:
- `__init__.py` + pure-python from `python/cudnn/` (version comes from its
  `__version__` line via the sed in meson.build)
- `_compiled_module.*.so` (the pybind11 extension; the only compiled artifact)
- `include/` - the full `include/` header tree, shipped inside the package
A `<site-packages>/cudnn/cudnn/` nesting means the double-cudnn layout bug is
back (CLAUDE.md section 8) - `import cudnn` silently becomes a namespace pkg.

## Requirements

- Env: `CUDAToolkit_ROOT`, `CUDNN_PATH` (CLAUDE.md section 3).
- All deps from the system: cudart, cuDNN, nlohmann_json, dlpack, pybind11.
  `-lcuda` links the driver stub; `-lnvrtc` is explicit in link_args.
- `ldd` showing `libcuda.so.1 => not found` on a GPU-less build box is
  EXPECTED (driver-provided at runtime), not a failure.

## Build (eugo container)

```bash
# 1. Fast gate (~seconds): dep discovery + version extraction, no compile
./.eugo/eugo_meson_setup.sh          # meson setup --wipe --reconfigure eugo_build
./.eugo/eugo_meson_compile.sh        # compile the extension in eugo_build

# 2. Canonical install (harness env: ben_life_easy.sh defines the options)
pip3 install . ${EUGO_PIP_COMPILABLE_PACKAGE_OPTIONS} ${EUGO_MESONPY_COMMON_OPTIONS}
# Outside the harness env, plain `pip install -v .` works given the env above.

# 3. Wheel (pip wheel does not support --compile, hence no COMPILABLE opts)
./.eugo/eugo_pip3_wheel.sh
```

Note: `.eugo/eugo_pip3_install.sh` starts with a machine-specific
laptop-to-container rsync preamble - in a container, run only its pip line.

## Smoke test (MUST pass; run from OUTSIDE the repo dir)

```bash
cd /tmp && python3 -c "import cudnn; print(cudnn.__version__); print(cudnn.backend_version()); print(cudnn.tensor)"
```

This catches the double-cudnn namespace bug, missing pybind11 symbol
re-exports (`AttributeError` - check `symbols_to_import` in
`python/cudnn/__init__.py`), and unresolved extension symbols (`ImportError:
undefined symbol: nvrtc*` means `-lnvrtc` regressed; CLAUDE.md section 8).
`pytest test/python` is the full gate but needs a real GPU + driver.

## How eugo actually ships it (protomolecule)

Package: `protomolecule/dependencies/python/wave_4/cuda_cudnn_frontend`.
- `meta.json` pins THIS repo by `version.commit` (git_commit on branch eugo-main);
  `build_flow: [mesonpy, meson]`. Nothing ships downstream until that pin is
  bumped to a pushed eugo-main SHA (see eugo-rebuild).
- `setup` runs `pip3 install "<name> @ <git pin>"` with
  `EUGO_PIP_COMPILABLE_PACKAGE_OPTIONS` + `EUGO_PIP_TARGET_FLAG` +
  `EUGO_MESONPY_COMMON_OPTIONS` (release, gnu++ std, cmake_prefix_path,
  wrap_mode=nofallback, out-of-source build dir).
- Post-install it symlinks `<site-packages>/cudnn/include/*` into
  `${EUGO_STANDARD_PATH}/include` (= /usr/local/include).
- Downstream contract: torch (same wave) builds with
  `-DUSE_SYSTEM_CUDNN_FRONTEND=ON` and
  `-DCUDNN_FRONTEND_INCLUDE_PATH="${EUGO_STANDARD_PATH}/include/"` - so a
  broken header install here surfaces as a TORCH build failure, not ours.
  Verify: `ls -l /usr/local/include/cudnn_frontend.h` resolves.

## Related

- Skills: eugo-rebuild (what to rebuild for a given diff),
  eugo-meson-build-review (pre-commit build-file checklist),
  eugo-upstream-merge (sync recipe), meson (generic meson mechanics).
- CLAUDE.md sections 3, 7, 8 - the authoritative playbook.
