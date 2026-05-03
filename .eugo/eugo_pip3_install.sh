#!/usr/bin/env bash
set -euo pipefail


export CFLAGS="-Wno-deprecated-declarations -Wno-deprecated-this-capture"
export CXXFLAGS="-Wno-deprecated-declarations -Wno-deprecated-this-capture"

export PIP_NO_CLEAN=1

# Re-rsync source to the container
rsync -av --exclude='.git' --exclude='build' --exclude='eugo_build' \
  /Users/benjaminleff/repos/eugo/cudnn-frontend-meson-python \
  /Users/benjaminleff/repos/eugo/protomolecule/__io__/tmp/eugo/cudnn-frontend-meson-python

# Then in the container:
rm -rf /tmp/eugo/cudnn-frontend-meson-python/cudnn-frontend-meson-python/eugo_build

pip3 install . \
    ${EUGO_PIP_COMPILABLE_PACKAGE_OPTIONS} \
    ${EUGO_MESONPY_COMMON_OPTIONS}

python3 -c "import cudnn; print(cudnn.__version__); print(cudnn.tensor)"

# cd /usr
# python3
# Python 3.12.7 (main, Nov 22 2024, 15:13:20) [Clang 20.0.0git ] on linux
# Type "help", "copyright", "credits" or "license" for more information.
# >>> import cudnn
# >>> cudnn.__version__
# '1.23.0'
# >>>