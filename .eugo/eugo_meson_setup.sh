#!/usr/bin/env bash
set -euo pipefail


export CFLAGS="-Wno-deprecated-declarations -Wno-deprecated-this-capture -Wno-unused-const-variable"
export CXXFLAGS="-Wno-deprecated-declarations -Wno-deprecated-this-capture -Wno-unused-const-variable"


# NOTE: use `--wipe` to clear the build dir
meson setup --wipe --reconfigure eugo_build
