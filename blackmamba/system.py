import sys

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
    except:
        pass


class Available():
    '''Decorator to execute function under specific Pythonista versions.

    Examples:
        Run function only within any Pythonista version::

            @Available()
            def run_me():
                pass

        Run function only within Pythonista >= 3.1.1::

            @Available('3.1.1')
            def run_me():
                pass

        Run function only within Pythonista <= 3.2::

            @Available(None, '3.2')  # or @Available(to_version='3.2')
            def run_me():
                pass
    '''
    def __init__(self, from_version=None, to_version=None):
        if from_version and to_version:
            raise ValueError('Either from_version or to_version can be provided, not both')

        self._from_version = _version_tuple(from_version)
        self._to_version = _version_tuple(to_version)

    def _available(self):
        if not PYTHONISTA_VERSION_TUPLE:
            return False

        if self._to_version:
            return PYTHONISTA_VERSION_TUPLE <= self._to_version

        if self._from_version:
            return PYTHONISTA_VERSION_TUPLE >= self._from_version

        return True

    def __call__(self, fn, *args, **kwargs):
        def func(*args, **kwargs):
            if self._available():
                return fn(*args, **kwargs)
            return None
        return func
