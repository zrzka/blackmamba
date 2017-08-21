#!/usr/bin/env bash

VERSION=$(python setup.py --version)
PACKAGE_PATH="dist/blackmamba-$VERSION.tar.gz"
python setup.py sdist

if [ -f "$PACKAGE_PATH" ]; then
    twine upload $PACKAGE_PATH
fi
