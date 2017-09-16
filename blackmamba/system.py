#!python3
'''System info and decorators.

Note:
    This module must not introduce dependency on any other Black Mamba
    modules and must be importable on any other platform as well.
'''

import sys
import traceback
import functools

try:
    import console
except ModuleNotFoundError:
    console = None


# 3.1, 301016
# 3.1.1 beta, 311008

PYTHONISTA = sys.platform == 'ios'
'''bool: ``True`` if we're running within Pythonista or ``False``.'''

PYTHONISTA_VERSION = None
'''str: Pythonista version or ``None`` if we're not within Pythonista.'''

PYTHONISTA_BUNDLE_VERSION = None
'''int: Pythonista bundle version or ``None`` if we're not within Pythonista.'''

PYTHONISTA_VERSION_TUPLE = None
'''tuple(int): Pythonista version tuple (3, 1, 1) or ``None`` if we're not within Pythonista.'''

IOS = sys.platform == 'ios'
'''bool: ``True`` if we're running within iOS or ``False``.'''

IOS_VERSION = None
'''str: iOS version or ``None`` if we're not within iOS.'''

IOS_VERSION_TUPLE = None
'''tuple(int): iOS version tuple (11, 0) or ``None`` if we're not within iOS.'''


def _version_tuple(version):
    if not version:
        return None
    return tuple(map(int, (version.split('.'))))


if PYTHONISTA:
    import plistlib
    import os

    try:
        plist_path = os.path.abspath(os.path.join(sys.executable, '..', 'Info.plist'))
        plist = plistlib.readPlist(plist_path)

        PYTHONISTA_VERSION = plist['CFBundleShortVersionString']
        PYTHONISTA_BUNDLE_VERSION = int(plist['CFBundleVersion'])
        PYTHONISTA_VERSION_TUPLE = _version_tuple(PYTHONISTA_VERSION)
    except Exception:
        pass


if IOS:
    try:
        from objc_util import ObjCClass
        IOS_VERSION = str(ObjCClass('UIDevice').currentDevice().systemVersion())
        IOS_VERSION_TUPLE = _version_tuple(IOS_VERSION)
    except Exception:
        pass


class _Available():
    def __init__(self, from_version=None, to_version=None):
        if from_version and to_version:
            raise ValueError('Either from_version or to_version can be provided, not both')

        self._from_version = _version_tuple(from_version)
        self._to_version = _version_tuple(to_version)

    def version(self):
        raise Exception('Not implemented, return version as tuple(int)')

    def _available(self):
        current_version = self.version()
        if not current_version:
            return False

        if self._to_version:
            return current_version <= self._to_version

        if self._from_version:
            return current_version >= self._from_version

        return True

    def __call__(self, fn, *args, **kwargs):
        def func(*args, **kwargs):
            if self._available():
                return fn(*args, **kwargs)
            return None
        return func


class iOS(_Available):
    '''Decorator to execute function under specific iOS versions.

    Examples:
        Run function only within any iOS version::

            @iOS()
            def run_me():
                pass

        Run function only within iOS >= 11.0::

            @iOS('11.0')  # or @iOS(from_version='11.0')
            def run_me():
                pass

        Run function only within iOS <= 11.0::

            @iOS(None, '11.0')  # or @iOS(to_version='11.0')
            def run_me():
                pass
    '''
    def version(self):
        return IOS_VERSION_TUPLE


class Pythonista(_Available):
    '''Decorator to execute function under specific Pythonista versions.

    By default, function is not executed under application extension.
    You have to pass `appex=True` if you'd like to run some function
    under appex as well.

    Examples:
        Run function only within any Pythonista version::

            @Pythonista()
            def run_me():
                pass

        Run function only within any Pythonista version and allow appex::

            @Pythonista(appex=True)
            def run_me():
                pass

        Run function only within any Pythonista version and disallow appex::

            @Pythonista(appex=False)
            def run_me():
                pass

        Run function only within Pythonista >= 3.1.1::

            @Pythonista('3.1.1')  # or @Pythonista(from_version='3.1.1')
            def run_me():
                pass

        Run function only within Pythonista <= 3.2::

            @Pythonista(None, '3.2')  # or @Pythonista(to_version='3.2')
            def run_me():
                pass
    '''
    def __init__(self, from_version=None, to_version=None, appex=None):
        super().__init__(from_version, to_version)
        self._appex = appex

    def _available(self):
        available = super()._available()

        if available and self._appex is not None:
            import appex
            available = appex.is_running_extension() == self._appex

        return available

    def version(self):
        return PYTHONISTA_VERSION_TUPLE


def catch_exceptions(func):
    '''Catches all ``Exception`` exceptions and writes info to console.

    Use this decorator for functions handling keyboard shortcuts,
    keyboard events, ... to avoid Pythonista crash.
    '''
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            if console:
                console.set_color(1, 0, 0)
            print(traceback.format_exc())
            print('Please, file an issue at {}'.format('https://github.com/zrzka/blackmamba/issues'))
            if console:
                console.set_color()

    return new_func
