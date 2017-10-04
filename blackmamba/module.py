#!python

import sys
import os


_BUNDLED_MODULES = [
    'mccabe', 'flake8', 'docutils', 'pep8', 'pycodestyle', 'pyflakes', 'setuptools'
]


def _bundled_modules_path():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))


def _setup_bundled_modules_path():
    path = _bundled_modules_path()
    try:
        sys.path.index(path)
    except ValueError:
        sys.path.insert(0, path)


def _unload_modules(modules_to_unload, force=False):
    from blackmamba.log import debug

    lib = _bundled_modules_path()
    for mod_name in list(sys.modules.keys()):
        name = mod_name.split('.')[0]
        if name in modules_to_unload:
            mod = sys.modules[mod_name]

            if not hasattr(mod, '__file__'):
                continue

            mod_path = mod.__file__

            if mod_path.startswith(lib) and not force:
                debug('Skipping {}'.format(mod_name))
                continue

            if not os.access(mod_path, os.W_OK):
                continue

            debug('Unloading module {}'.format(mod_name))
            del sys.modules[mod_name]


def preflight(force=False):
    _unload_modules(_BUNDLED_MODULES, force)
    _setup_bundled_modules_path()
