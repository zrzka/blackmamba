#!python3

import console
from contextlib import contextmanager


ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0

level = INFO


@contextmanager
def _color(*color):
    if color:
        console.set_color(*color)
    yield
    if color:
        console.set_color()


def info(*args, **kwargs):
    if level > INFO:
        return

    print(*args, **kwargs)


def warn(*args, **kwargs):
    if level > WARNING:
        return

    with _color(1, 0.5, 0):
        print(*args, **kwargs)


def error(*args, **kwargs):
    with _color(1, 0, 0):
        print(*args, **kwargs)
