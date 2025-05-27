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
# Actually, only `cudart` and headers are used from CUDAToolkit. All other components and libraries are ignored.
# Moreover, this package doesn't involve any CUDA code compilation (i.e., .cu and .cuh files).
# So instead of using meson's native cuda dependency version (i.e. `cuda = dependency('cuda')`), we use the `cmake` method to find the `cudart` library.
# We deliberately use `cudart` (dynamic version) and not `cudart_static` (and pass `static: false`) because we don't want to link against static version of the library.
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
    'include/cudnn_frontend/graph_properties.h',
    'include/cudnn_frontend/node/softmax.h',
    'include/cudnn_frontend/node/matmul.h',
    'include/cudnn_frontend/node/resample.h',
    'include/cudnn_frontend/node/dbn_weight.h',
    'include/cudnn_frontend/node/rmsnorm.h',
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
    'include/cudnn_frontend/node/sdpa_fp8_bwd.h',
    'include/cudnn_frontend/node/sdpa_fp8.h',
    'include/cudnn_frontend/node/concatenate.h',
    'include/cudnn_frontend/node/matmul_fp8.h',
    'include/cudnn_frontend/node/rng.h',
    'include/cudnn_frontend/node/paged_cache_load.h',
    'include/cudnn_frontend/node/reshape.h',
    'include/cudnn_frontend/node/bn_finalize.h',
    'include/cudnn_frontend/node/dbn.h',
    'include/cudnn_frontend/node/conv_wgrad.h',
    'include/cudnn_frontend/node/pointwise.h',
    'include/cudnn_frontend/node/reduction.h',
    'include/cudnn_frontend/node/dln.h',
    'include/cudnn_frontend/knobs.h',
    'include/cudnn_backend_base.h',
    'include/cudnn_frontend_version.h',
    'include/cudnn_frontend_EngineFallbackList.h',
    'include/cudnn_frontend_shim.h',
    'include/cudnn_frontend_Resample.h',
    'include/cudnn_frontend_Errata.h',
    'include/cudnn_frontend_ExecutionPlan.h',
    'include/cudnn_frontend_ExecutionPlanCache.h',
    'include/cudnn_frontend_Logging.h'
)

# Pip doesn't allow you to install any file outside python managed prefixes, like `site-packages` or `dist-packages`.
# So we install the headers into `site-packages/cudnn/include` directory.
# To use them system-wide, we symlink them in our `setup` script.
install_subdir(
    'include',
    install_dir: py.get_install_dir() / 'cudnn',
    install_tag: 'python-runtime',
    follow_symlinks: true,
    exclude_directories: ['cudnn_frontend/thirdparty/nlohmann']
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
        'python/pycudnn.cpp',
        'python/properties.cpp',

        'python/pygraph/pygraph.cpp',
        'python/pygraph/norm.cpp',
        'python/pygraph/sdpa.cpp',
        'python/pygraph/pointwise.cpp'
    ],
    install: true,
    subdir: 'cudnn/',
    dependencies: [
        cuda,
        cudnn_backend,
        dlpack,
        nlohmann_json,
        pybind11,
        cudnn_frontend_native_dep
    ],
    # Nvidia upstream does the same but for unknown reason PyPi-published wheel still exposes all symbols.
    gnu_symbol_visibility: 'hidden',

    # This library is one of a few which requires direct interaction with the GPU driver, so we need to link this library explicitly.
    # `meson` fails to find that in their `cuda` finder, so we do it here. Noteworthy, `libcuda.so.1` doesn't exist at buildtime, it only
    # becomes inserted by NVIDIA driver runtime. At buildtime, we just have stubs library (`libcuda.so`) allowing to build but useless at runtime.
    link_args: ['-lcuda']
)
# === @end: Python, compilable ===


# === @begin: Python, pure ===
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