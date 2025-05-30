# cuDNN FrontEnd(FE) API

## Introduction
The cuDNN FrontEnd(FE) API is a C++ header-only library and python frontend to the [cuDNN C backend API](https://docs.nvidia.com/deeplearning/cudnn/api/index.html#cudnn-backend-api). Both the FE and backend APIs are entry points to the same set of functionality that is commonly referred to as the "[graph API](https://docs.nvidia.com/deeplearning/cudnn/backend/latest/api/overview.html)".

While there are two entry points to the graph API (i.e. backend and frontend), it is expected that most users will use the FE API. Reasons being:

- FE API is less verbose without loss of control. All functionality accessible through the backend API is also accessible through the FE API.
- FE API adds functionality on top of the backend API, like errata filters and autotuning.

Also, for those using backend API, FE API source and samples can serve as reference implementation.

In FE v1.0 API, users can describe multiple operations that form subgraph through a persistent `cudnn_frontend::graph::Graph` object. FE v1.0 API extends the groundwork of earlier versions and introduces a new set of APIs to further simplify the workflow.  For detailed information of FE v1.0 API, please refer to the [documentation](https://docs.nvidia.com/deeplearning/cudnn/frontend/latest/).

Additionally, FE v1.0 API provides python bindings to all API through pybind11. It is recommended that new users of cuDNN start with the frontend v1.0 API. See `samples/cpp` and `samples/python` for more details on its usage.

## Usage
For c++ users, in order to include the entire library, include the cudnn_frontend header file `include/cudnn_frontend.h` into your compilation unit.

For Python users, run `import cudnn`


## Performance

Benchmarking test suites for cuDNN, covering various models and computational subgraphs, are available in the [benchmark directory](benchmark/). This section provides instructions for utilizing cuDNN as the primary backend across different environments.

## Build:

Please refer to the [frontend installation guide](https://docs.nvidia.com/deeplearning/cudnn/installation/latest/frontend.html)

### Dependencies
With the release of v1.0, we are bumping up the minimum supported cudnn version to 8.5.0

cuda can be downloaded from the [nvidia dev-zone](https://developer.nvidia.com/cuda-downloads)

cudnn can be installed from 
    - [nvidia dev-zone](https://developer.nvidia.com/cudnn)
    - [pypi wheels](https://pypi.org/project/nvidia-cudnn-cu12/)

Minimum python version needed 3.8
The python binding compilation requires development package which can be installed by running `apt-get install python-dev`.

To run the Python samples, you will need the dependencies mentioned in `requirements.txt`. This can be be installed by running:
`pip install -r requirements.txt`

### Python API

#### pip wheel installation

Download the pip wheel corresponding to your python installation.

```
pip install nvidia_cudnn_frontend
```

#### Source installation:
Install FE python API by running:
```
pip install -v git+https://github.com/NVIDIA/cudnn-frontend.git
```

Above command picks cuda and cudnn from default system paths.

To provide a custom CUDA installation path, use environment variable: `CUDAToolkit_ROOT`.  
To provide a custom CUDNN installation path, use environment variable: `CUDNN_PATH`.

#### Checking the installation
To test whether installation is successful, run:
```
pytest test/python
```

NOTE: Only v1.0 API is exposed via python bindings.

### C++ API

C++ API is header only library.

The root CMakeLists.txt can be used as reference to include the cudnn_frontend in your project's build system.

#### Building samples
The following compilation steps are only required for building the samples.

Provide CUDA installation path according to: https://cmake.org/cmake/help/latest/module/FindCUDAToolkit.html  

Provide CUDNN installation path using CUDNN_PATH env variable or cmake parameter.

CUDNN_PATH has the cudnn installation:
- Headers are in CUDNN_PATH/include.
- Libraries are in CUDNN_PATH/lib or CUDNN_PATH/lib64 or CUDNN_PATH/lib/x64.

For a in-source build,
```
mkdir build
cd build
cmake -DCUDNN_PATH=/path/to/cudnn -DCUDAToolkit_ROOT=/path/to/cuda  ../
cmake --build . -j16
bin/samples
```

To skip building samples, use `-DCUDNN_FRONTEND_BUILD_SAMPLES=OFF`.

To skip building python bindings, use `-DCUDNN_FRONTEND_BUILD_PYTHON_BINDINGS=OFF`.

To add debug symbols, use `-DCMAKE_BUILD_TYPE=Debug`.

In case, you have a stale cmake cache and want to update the cudnn/cuda paths, please delete the cmake cache (or build directory and redo the above steps).

## Debugging
For initial debugging, we recommend turning on the cudnn FE logging and checking for warnings and errors.
cuDNN Frontend API logging records execution flow through cuDNN frontend API. This functionality is disabled by default, and can be enabled through methods described in this section.

### Method 1: Using Environment Variables:
| Environment variables                             | CUDNN_FRONTEND_LOG_INFO=0 | CUDNN_FRONTEND_LOG_INFO=1 |
| ------------------------------------------------- | ------------------------- | -----------               |
| CUDNN_FRONTEND_LOG_FILE not set                   | No Logging                | No Logging                |
| CUDNN_FRONTEND_LOG_FILE set to stdout or stderr   | No Logging                | Logging to cout or cerr   |
| CUDNN_FRONTEND_LOG_FILE set to filename.txt       | No Logging                | Logging to the filename   |

### Method 2: Using API calls:
Calling `cudnn_frontend::isLoggingEnabled() = true|false` has same effect of setting the environment variable.
Calling `cudnn_frontend::getStream() = stream_name` can be used to assign the output stream directly.

For further debugging, please turn on the cudnn backend logs described here https://docs.nvidia.com/deeplearning/cudnn/latest/reference/troubleshooting.html#error-reporting-and-api-logging

## Documentation
The developer guide and API reference can be found [https://docs.nvidia.com/deeplearning/cudnn/frontend/v1.9.0/developer/overview.html](https://docs.nvidia.com/deeplearning/cudnn/latest/index.html).

## Contributing:
Please refer to our [contribution guide](CONTRIBUTING.md)

## Feedback
Support, resources, and information about cuDNN can be found online at https://developer.nvidia.com/cudnn. 

Also, bugs and RFEs can be reported in the issues section.
