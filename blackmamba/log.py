#!python3

import console
from contextlib import contextmanager


@contextmanager
def _color(*color):
    if color:
        console.set_color(*color)
    yield
    if color:
        console.set_color()


def info(*args, **kwargs):
    print(*args, **kwargs)


def warn(*args, **kwargs):
    with _color(1, 0.5, 0):
        print(*args, **kwargs)


def error(*args, **kwargs):
    with _color(1, 0, 0):
        print(*args, **kwargs)
