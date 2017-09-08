#!python3
'''Logging module.

Note:
    This module must not introduce dependency on any other Black Mamba
    modules and must be importable on any other platform as well.

Todo:
    * Add exception logging support
'''

try:
    import console
except:
    console = None

ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0

_level = INFO

_COLORS = {
    WARNING: (1, 0.5, 0),
    ERROR: (1, 0, 0)
}


def get_level():
    return _level


def set_level(level):
    global _level
    _level = level


def _log(level, *args, **kwargs):
    if _level > level:
        return

    color = _COLORS.get(level, None)
    if console and color:
        console.set_color(*color)

    print(*args, **kwargs)

    if console and color:
        console.set_color()


def debug(*args, **kwargs):
    _log(DEBUG, *args, **kwargs)


def info(*args, **kwargs):
    _log(INFO, *args, **kwargs)


def warn(*args, **kwargs):
    _log(WARNING, *args, **kwargs)


def error(*args, **kwargs):
    _log(ERROR, *args, **kwargs)
