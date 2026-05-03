#!/usr/bin/env bash
set -euo pipefail


export CFLAGS="-Wno-deprecated-declarations -Wno-deprecated-this-capture"
export CXXFLAGS="-Wno-deprecated-declarations -Wno-deprecated-this-capture"

export PIP_NO_CLEAN=1


# NOTE: we dont use `${EUGO_PIP_COMPILABLE_PACKAGE_OPTIONS}` here because `pip wheel` does not support `--compile`
pip3 wheel . \
  --no-cache-dir \
  --no-build-isolation \
  --no-deps \
  --no-binary :all: \
  -v -v -v \
  ${EUGO_MESONPY_COMMON_OPTIONS}
