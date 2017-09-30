#!/usr/bin/env bash

if [ -d build ]; then
    rm -rf build
fi
sphinx-autobuild -b html source build/html
