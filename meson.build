# === @begin: General ===
project(
    'cuda-cudnn-frontend',
    'c', 'cpp',
    default_options: [
        'c_std=gnu17',
        'cpp_std=gnu++23',
        'buildtype=release',
    ],
    meson_version: '>=1.3.0',
    version: run_command([
        'sed', '-n',
        's/^__version__\\s*=\\s*"\([^"]*\)"/\\1/p',
        meson.project_source_root() / 'python' / 'cudnn' / '__init__.py'
    ], check: true).stdout().strip()
)
# === @end: General ===


# === @begin: Meson modules imports ===
fs = import('fs')
py = import('python').find_installation(pure: false, modules: ['pybind11'])
cmake = import('cmake')
# === @end: Meson modules imports ===



# === @begin: Project-wide settings ===
add_project_arguments(
    # From root, find the `include` directory
    '-I' + meson.project_source_root() / 'include',
    # From root, find the `python/pygraph` directory
    '-I' + meson.project_source_root() / 'python' / 'pygraph',
    language: ['c', 'cpp']
)
# === @end: Project-wide settings ===


# === @begin: Dependencies ===
# By default, `meson` prefers `cudart_static` and we don't want to alter that.
# https://docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/index.html#cudart-none-shared-static-cudart
#
# Actually, only `cudart` and headers are used from CUDAToolkit via this dependency. All other
# components and libraries are ignored. Moreover, this package doesn't involve any CUDA code
# compilation (no `.cu`/`.cuh` files). So instead of meson's native cuda dependency
# (`cuda = dependency('cuda')`), we use the `cmake` method to find the `cudart` library.
# We deliberately use `cudart` (dynamic version) and not `cudart_static` (passing `static: false`)
# because we don't want to link against the static version of the library.
#
# Why we DON'T pass `'nvrtc'` here as a component:
#   meson's `dependency('CUDA', method: 'cmake', ...)` invokes the LEGACY CMake `find_package(CUDA)`
#   module (`FindCUDA.cmake`), which only supports a small fixed component set (cudart, CUFFT,
#   CUBLAS, etc.) and does NOT recognize `nvrtc`. Meson silently drops unknown components instead
#   of erroring. Result: passing `components: ['cudart', 'nvrtc']` here links `libcudart.so` only —
#   nvrtc is never linked, and `import cudnn` fails at runtime with
#   `undefined symbol: nvrtcCreateProgram`.
#
#   We instead link `-lnvrtc` explicitly in `link_args:` of the python extension below (mirrors how
#   `-lcuda` is handled). The cleaner long-term fix would be to switch to the modern
#   `dependency('CUDAToolkit', method: 'cmake', ...)` which DOES support `nvrtc` as a component,
#   but that changes the cudart-finding path too and we haven't validated it end-to-end yet.
cuda = dependency('CUDA', method: 'cmake', components: ['cudart'], static: false)

# Find cudnn backend using their cmake file.
# We created a symlink to `cuDNN.cmake` in the `cmake` directory to our custom `FindcuDNN.cmake` file (it's a naming convention forced by CMake)
cudnn_backend = dependency('cuDNN', cmake_module_path: meson.project_source_root() / 'cmake')

# Find our system installed `dlpack` using their cmake file and modules.
dlpack = dependency('dlpack', method: 'cmake', modules: ['dlpack::dlpack'])

# `CUDNN_FRONTEND_SKIP_JSON_LIB` is not needed because we always use system-provided version
nlohmann_json = dependency('nlohmann_json', method: 'cmake')

# Find the `pybind11` package using their built in approach: https://mesonbuild.com/Dependencies.html#pybind11:~:text=pkg%2Dconfig.-,Pybind11,-(added%201.1.0)
pybind11 = dependency('Pybind11')
# === @end: Dependencies ===


# === @begin: Native ===
cudnn_frontend_native_header_files = files(
    'include/cudnn_frontend_Reorder_Tensor.h',
    'include/cudnn_frontend_Operation.h',
    'include/cudnn_frontend_EngineConfigGenerator.h',
    'include/cudnn_frontend.h',
    'include/cudnn_frontend_OperationGraph.h',
    'include/cudnn_frontend_find_plan.h',
    'include/cudnn_frontend_Rng.h',
    'include/cudnn_frontend_MatMulDesc.h',
    'include/cudnn_frontend_get_plan.h',
    'include/cudnn_frontend_Tensor.h',
    'include/cudnn_frontend_Filters.h',
    'include/cudnn_frontend_VariantPack.h',
    'include/cudnn_frontend_ReductionDesc.h',
    'include/cudnn_frontend_utils.h',
    'include/cudnn_frontend_ConvDesc.h',
    'include/cudnn_frontend_Engine.h',
    'include/cudnn_frontend_PointWiseDesc.h',
    'include/cudnn_frontend_Heuristics.h',
    'include/cudnn_frontend_EngineConfig.h',
    'include/cudnn_frontend/node_interface.h',
    'include/cudnn_frontend/graph_interface.h',
    'include/cudnn_frontend/cudnn_interface.h',
    'include/cudnn_frontend/graph_helpers.h',
    'include/cudnn_frontend/context.h',
    'include/cudnn_frontend/plans.h',
    'include/cudnn_frontend/utils/attn_score_modifiers.h',
    'include/cudnn_frontend/utils/serialize.h',
    'include/cudnn_frontend/backend/execution_helpers.h',
    'include/cudnn_frontend/backend/kernel_cache.h',
    'include/cudnn_frontend/backend/plan_helpers.h',
    'include/cudnn_frontend/backend/backend_descriptor.h',
    'include/cudnn_frontend/backend/device_properties.h',
    'include/cudnn_frontend/graph_properties.h',
    'include/cudnn_frontend/node/softmax.h',
    'include/cudnn_frontend/node/matmul.h',
    'include/cudnn_frontend/node/resample.h',
    'include/cudnn_frontend/node/dbn_weight.h',
    'include/cudnn_frontend/node/rmsnorm.h',
    'include/cudnn_frontend/node/adaptive_layernorm.h',
    'include/cudnn_frontend/node/conv_dgrad.h',
    'include/cudnn_frontend/node/scaled_dot_product_flash_attention.h',
    'include/cudnn_frontend/node/conv_fprop.h',
    'include/cudnn_frontend/node/batchnorm_inference.h',
    'include/cudnn_frontend/node/batchnorm.h',
    'include/cudnn_frontend/node/layernorm.h',
    'include/cudnn_frontend/node/block_scale_quantize.h',
    'include/cudnn_frontend/node/block_scale_dequantize.h',
    'include/cudnn_frontend/node/genstats.h',
    'include/cudnn_frontend/node/instancenorm.h',
    'include/cudnn_frontend/node/slice.h',
    'include/cudnn_frontend/node/diagonal_band_mask.h',
    'include/cudnn_frontend/node/sdpa_fp8_bwd.h',
    'include/cudnn_frontend/node/sdpa_support_surface.h',
    'include/cudnn_frontend/node/concatenate.h',
    'include/cudnn_frontend/node/matmul_fp8.h',
    'include/cudnn_frontend/node/moe_grouped_matmul.h',
    'include/cudnn_frontend/node/moe_grouped_matmul_bwd.h',
    'include/cudnn_frontend/node/rng.h',
    'include/cudnn_frontend/node/paged_cache_load.h',
    'include/cudnn_frontend/node/reshape.h',
    'include/cudnn_frontend/node/bn_finalize.h',
    'include/cudnn_frontend/node/dbn.h',
    'include/cudnn_frontend/node/conv_wgrad.h',
    'include/cudnn_frontend/node/pointwise.h',
    'include/cudnn_frontend/node/reduction.h',
    'include/cudnn_frontend/node/dln.h',
    'include/cudnn_frontend/node/transpose.h',
    'include/cudnn_frontend/experimental/attention_utils.h',
    'include/cudnn_frontend/experimental/nvrtc_shim.h',
    'include/cudnn_frontend/experimental/oss_engine_interface.h',
    'include/cudnn_frontend/experimental/sm100_rms_norm_silu_engine.h',
    'include/cudnn_frontend/experimental/sm100_rms_norm_silu_knobs.h',
    'include/cudnn_frontend/experimental/sm100_sdpa_prefill_engine.h',
    'include/cudnn_frontend/experimental/sm90_sdpa_prefill_engine.h',
    'include/cudnn_frontend/generated/rms_norm_silu/sm100/ln_fwd_silu_kernel.h',
    'include/cudnn_frontend/generated/rms_norm_silu/sm100/ln_headers.h',
    'include/cudnn_frontend/generated/sdpa/sm100/prefill/full_seqlens/d128_fprop_kernel.h',
    'include/cudnn_frontend/generated/sdpa/sm100/prefill/full_seqlens/d64_fprop_kernel.h',
    'include/cudnn_frontend/generated/sdpa/sm90/prefill/full_seqlens/d128_fprop_kernel.h',
    'include/cudnn_frontend/generated/sdpa/sm90/prefill/full_seqlens/d64_fprop_kernel.h',
    'include/cudnn_frontend/knobs.h',
    'include/cudnn_backend_base.h',
    'include/cudnn_frontend_version.h',
    'include/cudnn_frontend_EngineFallbackList.h',
    'include/cudnn_frontend_shim.h',
    'include/cudnn_frontend_Resample.h',
    'include/cudnn_frontend_Errata.h',
    'include/cudnn_frontend_ExecutionPlan.h',
    'include/cudnn_frontend_ExecutionPlanCache.h',
    'include/cudnn_frontend_Logging.h',
)

# Pip doesn't allow you to install any file outside python managed prefixes, like `site-packages` or `dist-packages`.
# So we install the headers into `site-packages/cudnn/include` directory.
# To use them system-wide, we symlink them in our `setup` script.
install_subdir(
    'include',
    install_dir: py.get_install_dir() / 'cudnn',
    install_tag: 'python-runtime',
    follow_symlinks: true,
    # exclude_directories: ['cudnn_frontend/thirdparty/nlohmann'] # TODO+ slava they are including these now but not sure if its a mistake on their part
)

cudnn_frontend_native = include_directories('include')
cudnn_frontend_native_dep = declare_dependency(
  include_directories: cudnn_frontend_native,
  dependencies: [cuda, cudnn_backend]
)
# === @end: Native ===


# === @begin: Python, compilable ===
py.extension_module(
    '_compiled_module',
    [
        # python/
        'python/pycudnn.cpp',
        'python/properties.cpp',

        # python/pygraph
        'python/pygraph/norm.cpp',
        'python/pygraph/pointwise.cpp',
        'python/pygraph/pygraph.cpp',
        'python/pygraph/sdpa.cpp',
    ],
    dependencies: [
        cuda,
        cudnn_backend,
        dlpack,
        nlohmann_json,
        pybind11,
        cudnn_frontend_native_dep
    ],
    # ----------------------------------------------------------------------------------------------
    # NOTE: We deliberately do NOT define `NV_CUDNN_FRONTEND_USE_DYNAMIC_LOADING`, even though
    # upstream's `python/CMakeLists.txt:81` sets it. Read this before changing.
    #
    # What the define does (see `include/cudnn_frontend_shim.h`):
    #   - WITH it set: every cuDNN/cudart/libcuda call routes through dlopen+dlsym at runtime. The
    #     compiled `_compiled_module.so` has NO `DT_NEEDED` entries for cuDNN/cudart/libcuda, and
    #     every cuDNN call dispatches via a global handle (`cudnn_dlhandle`) that the consumer is
    #     expected to set by calling the `_set_dlhandle_cudnn(handle)` python binding (see
    #     `python/cudnn/__init__.py:202`).
    #   - WITHOUT it set: every cuDNN/cudart/libcuda call is a direct call resolved at link time
    #     via PLT/GOT. The compiled `.so` has standard `DT_NEEDED` entries; whatever cuDNN was on
    #     `CUDNN_PATH` at build time is the cuDNN that gets loaded at runtime.
    #
    # Why we choose WITHOUT it for our fork:
    #   1. Our build env has exactly one CUDA + one cuDNN installed. Build-time cuDNN == runtime
    #      cuDNN, so the multi-version tolerance the dynamic-loading path provides is moot for us.
    #   2. The PLT/GOT path skips one extra memory load + indirect call per cuDNN op vs the
    #      `static void *fptr = dlsym(...)` cache path. The delta is ~1ns per call — negligible
    #      for cuDNN ops (hundreds of ns to ms) — but free wins are free wins, and the simpler
    #      mental model (just link it) is worth keeping when nothing forces us off it.
    #   3. The upstream wheel ships to PyPI where it cannot link any specific cuDNN; that is what
    #      forces upstream to use dynamic loading. Our wheel ships to a controlled internal env,
    #      so we don't have that constraint.
    #
    # !!! DANGER — read before flipping this off if you ever set the define !!!
    #   The `_set_dlhandle_cudnn(handle)` python binding is compiled UNCONDITIONALLY (see
    #   `python/pycudnn.cpp:77-92`). Without our define, calling it silently sets a global that
    #   NOTHING reads — every cuDNN call still goes through the build-time-linked cuDNN, ignoring
    #   the handle the caller passed in. So:
    #     - If anything downstream (torch, an internal wrapper, etc.) calls `_set_dlhandle_cudnn`
    #       expecting it to actually route subsequent cuDNN calls through that specific handle,
    #       OUR BUILD SILENTLY BREAKS THAT EXPECTATION. There is no error, no warning — calls
    #       just go to the wrong cuDNN.
    #     - Mitigation: as long as the handle the consumer would pass in points at the SAME
    #       cuDNN library we linked against at build time, behavior is identical to the
    #       "with the define" case. This is true today because (1) torch and our build use the
    #       same cuDNN install in our env, and (2) we have not seen any consumer rely on the
    #       handle indirection.
    #     - If you ever start shipping this wheel to a context where build-time cuDNN diverges
    #       from runtime cuDNN, or you take on a consumer that relies on `_set_dlhandle_cudnn`
    #       to swap in its own cuDNN, you MUST add this define back (`cpp_args:
    #       ['-DNV_CUDNN_FRONTEND_USE_DYNAMIC_LOADING']`) AND drop `-lcuda` AND `-lnvrtc` from
    #       `link_args` (both become redundant once driver/nvrtc calls go through dlopen) AND
    #       audit every direct `cudnn*` symbol use in our pybind .cpp files.
    #
    # cpp_args: ['-DNV_CUDNN_FRONTEND_USE_DYNAMIC_LOADING'],
    # ----------------------------------------------------------------------------------------------

    # Nvidia upstream does the same but for unknown reason PyPi-published wheel still exposes all symbols.
    gnu_symbol_visibility: 'hidden',

    # Mirrors upstream `python/CMakeLists.txt:111-113` (with one deliberate fork deviation on `--as-needed`).
    # Note: rpath entries live in `install_rpath:` (below), not here — meson 1.11+ warns and a
    # future release will hard-error on `-Wl,-rpath,...` passed via `link_args`.
    link_args: [
        # `-lcuda`: links the GPU driver lib directly. `libcuda.so` is a build-time stub from the
        # CUDA toolkit's `stubs/` dir; the real `libcuda.so.1` is provided at runtime by the NVIDIA
        # driver. `meson`'s cuda finder only links cudart, not libcuda, hence explicit here.
        # REQUIRED in our config because we don't define `NV_CUDNN_FRONTEND_USE_DYNAMIC_LOADING`
        # (see the long block above) — driver symbols (`cuInit`, `cuMemAlloc`, …) are direct calls,
        # so they need a real link-time dependency. If you ever add the define back, this line
        # becomes redundant (the shim dlopens `libcuda.so.1` at runtime instead).
        '-lcuda',
        # `-lnvrtc`: links libnvrtc (NVIDIA Runtime Compilation, used for runtime kernel JIT in
        # `include/cudnn_frontend/experimental/nvrtc_shim.h`, transitively pulled in via
        # `oss_engine_interface.h`). Same story as `-lcuda`: meson's `dependency('CUDA', ...)` uses
        # the legacy `FindCUDA.cmake` module which doesn't recognize `nvrtc` as a component
        # (see the long comment on the `cuda` dep at the top of this file), so we link it
        # explicitly here. REQUIRED because we don't define `NV_CUDNN_FRONTEND_USE_DYNAMIC_LOADING`
        # — without that define, `NV_FE_CALL_TO_NVRTC` expands to direct `nvrtcCreateProgram(...)`
        # calls that need link-time symbol resolution, and `import cudnn` fails with
        # `undefined symbol: nvrtcCreateProgram` if this is missing. If you ever add the define
        # back, this line becomes redundant (the shim dlopens `libnvrtc.so` at runtime instead).
        '-lnvrtc',
        '-Wl,--as-needed',                           # drop DT_NEEDED entries for libs whose symbols we don't actually reference. @EUGO_CHANGE: upstream uses `--no-as-needed` (which keeps every NEEDED entry, useful when libs are dlopen'd); we override to `--as-needed` so the .so doesn't carry phantom dependencies.
        '-Wl,--enable-new-dtags',                    # emit DT_RUNPATH instead of legacy DT_RPATH. Difference: RUNPATH is searched *after* LD_LIBRARY_PATH (so users can override), RPATH is searched *before* (so they can't).
    ],

    # Runtime library search paths baked into the `.so`'s DT_RUNPATH (because of `--enable-new-dtags` above).
    # Mirrors upstream `python/CMakeLists.txt:113`. Each entry is relative to the `.so`'s own location:
    #   - `$ORIGIN`                       : the .so's own directory — finds anything co-installed alongside `_compiled_module.so`.
    #   - `$ORIGIN/../lib`                : `<wheel>/lib/` layout for shared libs that live one dir up.
    #   - `$ORIGIN/../nvidia/cudnn/lib`   : the pip-installed `nvidia-cudnn` wheel's lib dir (`pip install nvidia-cudnn-cuXX`).
    # Use `install_rpath:` (not `-Wl,-rpath` in `link_args`) so meson doesn't warn / future-error.
    install_rpath: '$ORIGIN:$ORIGIN/../lib:$ORIGIN/../nvidia/cudnn/lib',
    install: true,
    # Install the .so as a SIBLING of `__init__.py` inside the top-level `cudnn/` package — i.e.
    # `<site-packages>/cudnn/_compiled_module.*.so`. This matches upstream's wheel layout and is
    # required because [python/cudnn/__init__.py:15] does
    # `importlib.import_module("._compiled_module", package=__name__)`, which only resolves when
    # the .so and the `__init__.py` live in the same directory.
    #
    # DO NOT change to `'cudnn/cudnn/'` — that produces a "double cudnn" path
    # (`<site-packages>/cudnn/cudnn/_compiled_module.so`) that turns `cudnn` into an empty
    # PEP-420 namespace package and silently breaks `import cudnn` and every `from cudnn.X import …`.
    subdir: 'cudnn/',
)
# === @end: Python, compilable ===


# === @begin: Python, pure ===
# `install_subdir(SRC, install_dir: D)` copies the source directory itself (its basename) into D.
# So with SRC = 'python/cudnn/' and D = `<site-packages>`, the result is `<site-packages>/cudnn/`
# containing `__init__.py`, `api_base.py`, etc. — sibling to the `_compiled_module.so` installed
# above. This is the layout `import cudnn` and `from cudnn.X import …` expect.
#
# DO NOT pass `install_dir: py.get_install_dir() / 'cudnn'` here — that double-nests the package
# under `<site-packages>/cudnn/cudnn/` (see the long comment on `subdir:` above for why that breaks).
install_subdir(
    'python/cudnn/',

    install_dir: py.get_install_dir(),
    install_tag: 'python-runtime',
    follow_symlinks: true,
)
# === @end: Python, pure ===


# === @begin: CMake Configuration ===
# IMPORTANT: we are not generating the `-targets.cmake` as it's not yet supported by `meson`
# and we don't need it because our cudnn frontend is only used by torch, where we pass `CUDNN_FRONTEND_INCLUDE_DIR=EUGO_STANDARD_PATH/include`.
# Some minor consequences are that:
# 1. `find_package(CUDNN_FRONTEND)` will work in cmake.
# 2. But, it may not define the `targets` in the same way as upstream cmake version does which may potentially break builds of downstream packages who depend on this original behavior.
# Similar to other features introduced to meson in the previous year, we expect meson to add native support for this, so we won't have to introduce it ourselves.
# https://mesonbuild.com/CMake-module.html#cmakeconfigure_package_config_file
# cmake.configure_package_config_file(
#     name: 'cudnn_frontend', # This must be `cudnn_frontend` and not `cuda_cudnn_frontend` to match the upstream naming convention (and not our naming convention)
#     input: 'cudnn_frontend-config.cmake.in',
#     configuration: configuration_data(),
#     install_dir: py.get_install_dir() / 'cudnn' / 'cmake',
# )
