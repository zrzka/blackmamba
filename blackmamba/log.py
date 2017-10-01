#!python3
"""
Logging module.

Why custom module instead of :mod:`logging`? Several reasons:

* not to interfere with Pythonista logging settings,
* unable to convince Pythonista to use my colors,
* etc.

Default log level is ``INFO``. You can use :func:`blackmamba.log.set_level`
to change effective log level. Available log levels are:

* ``ERROR``
* ``WARNING``
* ``INFO``
* ``DEBUG``
* ``NOTSET``

If you'd like to silent Black Mamba messages, it's recommended to set log
level to ``ERROR``.

.. code-block:: python

    import blackmamba.log as log

    log.set_level(log.ERROR)

.. warning:: This module must not introduce dependency on any other Black Mamba
    modules and must be importable on any other platform.

Reference
=========
"""

try:
    import console
except ImportError:
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
    """
    Return effective log level.

    :return: Effective log level
    """
    return _level


def set_level(level):
    """
    Set effective log level.

    :param level: Level to set
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
    """
    Log message with DEBUG level.

    :param args: Passed to :func:`print`
    :param kwargs: Passed to :func:`print`
    """
    _log(DEBUG, *args, **kwargs)


def info(*args, **kwargs):
    """
    Log message with INFO level.

    :param args: Passed to :func:`print`
    :param kwargs: Passed to :func:`print`
    """
    _log(INFO, *args, **kwargs)


def warn(*args, **kwargs):
    """
    Log message with WARNING level.

    :param args: Passed to :func:`print`
    :param kwargs: Passed to :func:`print`
    """
    _log(WARNING, *args, **kwargs)


def error(*args, **kwargs):
    """
    Log message with ERROR level.

    :param args: Passed to :func:`print`
    :param kwargs: Passed to :func:`print`
    """
    _log(ERROR, *args, **kwargs)
