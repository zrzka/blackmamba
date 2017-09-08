#!python3

from enum import Enum


class Style(Enum):
    '''Value represents value for style parameter in editor.annotate_line function.'''
    error = 'error'
    warning = 'warning'


class Annotation(object):
    def __init__(self, line, text, style, filename=None):
        self.line = line
        self.text = text
        self.style = style
        self.filename = filename

    @property
    def editor_annotation_style(self):
        return self.style.value
