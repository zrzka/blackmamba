#!python3

from enum import Enum


class Style(str, Enum):
    error = 'error'
    warning = 'warning'


class Annotation(object):
    def __init__(self, line, text, style, filename=None):
        self.line = line
        self.text = text
        self.style = style
        self.filename = filename
