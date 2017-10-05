#!python

import sys
import os
from contextlib import contextmanager
from blackmamba.log import debug

_BUNDLES = {
    'analyze': ['mccabe', 'flake8', 'pep8', 'pycodestyle', 'pyflakes', 'setuptools'],
    'docutils': ['docutils']
}

_BUNDLED_MODULES_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))


def _unload_modules(modules, include_bundled=False):
    from blackmamba.log import debug

    for mod_name in list(sys.modules.keys()):
        name = mod_name.split('.')[0]
        if name in modules:
            mod = sys.modules[mod_name]

            if not hasattr(mod, '__file__'):
                debug('Skipping {}, does not have __file__'.format(mod_name))
                continue

            mod_path = mod.__file__
            if mod_path.startswith(_BUNDLED_MODULES_PATH) and not include_bundled:
                debug('Skipping {}, Black Mamba bundle'.format(mod_name))
                continue

            debug('Unloading module {}'.format(mod_name))
            del sys.modules[mod_name]


def _add_bundled_modules_path():
    try:
        sys.path.index(_BUNDLED_MODULES_PATH)
    except ValueError:
        sys.path.insert(1, _BUNDLED_MODULES_PATH)


def _remove_bundled_modules_path():
    try:
        sys.path.remove(_BUNDLED_MODULES_PATH)
    except ValueError:
        pass


def load(name):
    debug('Loading bundle {}'.format(name))
    _unload_modules(_BUNDLES[name], False)
    _add_bundled_modules_path()


def unload(name):
    debug('Unloading bundle {}'.format(name))
    _remove_bundled_modules_path()
    _unload_modules(_BUNDLES[name], True)


@contextmanager
def bundle(name, unload_bundle=False):
    load(name)
    yield name
    if unload_bundle:
        unload(name)
