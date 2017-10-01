#!/usr/bin/env bash

if [ -d build ]; then
    rm -rf build
fi
sphinx-autobuild -b html --open-browser --delay 1 source build/html
