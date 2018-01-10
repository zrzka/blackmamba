#!python3

"""Logging module.

**This module must not introduce dependency on any other Black Mamba
modules and must be importable on any other platform**.

Why custom module instead of the bundled one? Several reasons:

* not to interfere with Pythonista logging settings,
* unable to convince Pythonista to use my colors,
* etc.

Default log level is INFO. You can use `blackmamba.log.set_level`
to change effective log level. Available log levels are:

* `ERROR`
* `WARNING`
* `INFO`
* `DEBUG`
* `NOTSET`

If you'd like to silent Black Mamba messages, it's recommended to set log
level to `ERROR`::

    import blackmamba.log as log
    log.set_level(log.ERROR)
"""

try:
    import console
except ImportError:
    console = None

ERROR = 40
"""Only errors are logged."""

WARNING = 30
"""Only warnings and errors are logged."""

INFO = 20
"""Informational messages, warnings and errors are logged."""

DEBUG = 10
"""Debug, information messages, warnings and errors are logged."""

NOTSET = 0
"""All messages are logged."""

_level = INFO

_COLORS = {
    WARNING: (1, 0.5, 0),
    ERROR: (1, 0, 0)
}


def get_level() -> int:
    """Return effective log level.

    Returns:
        Effective log level.
    """
    return _level


def set_level(level: int):
    """Set effective log level.

    Args:
        level: Log level to set.
    """
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
    """Log message with `DEBUG` level.

    Args:
        args: Passed to `print`.
        kwargs: Passed to `print`.
    """
    _log(DEBUG, *args, **kwargs)


def info(*args, **kwargs):
    """Log message with `INFO` level.

    Args:
        args: Passed to `print`.
        kwargs: Passed to `print`.
    """
    _log(INFO, *args, **kwargs)


def warn(*args, **kwargs):
    """Log message with `WARNING` level.

    Args:
        args: Passed to `print`.
        kwargs: Passed to `print`.
    """
    _log(WARNING, *args, **kwargs)


def error(*args, **kwargs):
    """Log message with `ERROR` level.

    Args:
        args: Passed to `print`.
        kwargs: Passed to `print`.
    """
    _log(ERROR, *args, **kwargs)


def issue(*args, **kwargs):
    error(*args, **kwargs)
    error('Please, file an issue at {}'.format('https://github.com/zrzka/blackmamba/issues'))
