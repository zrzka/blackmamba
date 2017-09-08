#!python3

import io
import pep8
import re
from enum import Enum
import pyflakes.api as pyflakes
import editor
import console
from blackmamba.annotation import Annotation, Style
from itertools import groupby
from blackmamba.config import get_config_value

__all__ = ['analyze']


def _hud_alert_delay():
    return get_config_value('analyzer.hud_alert_delay', 1.0)


def _ignore_codes():
    return get_config_value('analyzer.ignore_codes', ['W391', 'W293'])


def _max_line_length():
    return get_config_value('analyzer.max_line_length', 79)


def _remove_whitespaces():
    return get_config_value('analyzer.remove_whitespaces', True)


_REMOVE_TRAILING_WHITESPACES_REGEX = re.compile('[ \t]+$', re.MULTILINE)
_REMOVE_TRAILING_LINES_REGEX = re.compile('\s+\Z', re.MULTILINE)

#
# Common for pep8 & pyflakes
#


class _Source(Enum):
    pep8 = 'PEP8'
    pyflakes = 'pyflakes'


class _AnalyzerAnnotation(Annotation):
    def __init__(self, line, text, source, style):
        super().__init__(line, text, style)
        self.source = source

    def __lt__(self, other):
        if self.source is _Source.pep8 and other.source is _Source.pyflakes:
            return True

        if self.style is Style.warning and other.style is Style.error:
            return True

        return False


#
# pep8
#

class _Pep8AnnotationReport(pep8.BaseReport):
    def __init__(self, options):
        super().__init__(options)
        self.annotations = []

    def error(self, line_number, offset, text, check):
        # If super doesn't return code, this one is ignored
        if not super().error(line_number, offset, text, check):
            return

        annotation = _AnalyzerAnnotation(self.line_offset + line_number, text, _Source.pep8, Style.warning)
        self.annotations.append(annotation)


def _pep8_annotations(text, ignore=None, max_line_length=None):
    # pep8 requires you to include \n at the end of lines
    lines = text.splitlines(True)

    style_guide = pep8.StyleGuide(reporter=_Pep8AnnotationReport, )
    options = style_guide.options

    if ignore:
        options.ignore = tuple(ignore)
    else:
        options.ignore = tuple()

    if max_line_length:
        options.max_line_length = max_line_length

    checker = pep8.Checker(None, lines, options, None)
    checker.check_all()

    return checker.report.annotations


#
# pyflakes
#

_LINE_COL_MESSAGE_REGEX = re.compile('^(\d+):(\d+): (.*)$')
_LINE_MESSAGE_REGEX = re.compile('^(\d+): (.*)$')


def _get_annotations(path, stream, style):
    l = len(path)

    annotations = []
    for line in stream.getvalue().splitlines():
        if not line.startswith(path):
            continue

        line = line[(l + 1):]  # Strip 'filename:'
        match = _LINE_COL_MESSAGE_REGEX.fullmatch(line)

        if not match:
            match = _LINE_MESSAGE_REGEX.fullmatch(line)

        if not match:
            continue

        line = int(match.group(1))

        if match.lastindex == 3:
            annotation = _AnalyzerAnnotation(
                line, 'Col {}: {}'.format(match.group(2), match.group(3)),
                _Source.pyflakes, style
            )
        else:
            annotation = _AnalyzerAnnotation(
                line, match.group(2),
                _Source.pyflakes, style
            )

        annotations.append(annotation)

    return annotations


def _pyflakes_annotations(path, text):
    warning_stream = io.StringIO()
    error_stream = io.StringIO()
    reporter = pyflakes.modReporter.Reporter(warning_stream, error_stream)

    pyflakes.check(text, path, reporter)

    warnings = _get_annotations(path, warning_stream, Style.warning)
    errors = _get_annotations(path, error_stream, Style.error)

    return warnings + errors


def _annotate(line, annotations, scroll):
    by_priority = sorted(annotations, reverse=True)

    style = by_priority[0].editor_annotation_style
    text = ',\n'.join([a.text for a in by_priority])

    editor.annotate_line(line, text, style, True, scroll=scroll)


def clear_annotations():
    editor.clear_annotations()


def _remove_trailing_whitespaces(text):
    return _REMOVE_TRAILING_WHITESPACES_REGEX.sub('', text)


def _remove_trailing_lines(text):
    return _REMOVE_TRAILING_LINES_REGEX.sub('', text)


def _editor_text():
    text = editor.get_text()

    range_end = len(text)

    if _remove_whitespaces():
        text = _remove_trailing_whitespaces(text)
        text = _remove_trailing_lines(text)
        editor.replace_text(0, range_end, text)
        # Pythonista is adding '\n' automatically, so, if we removed them
        # all we have to simulate Pythonista behavior by adding '\n'
        # for pyflakes & pep8 analysis
        return text + '\n'

    return text


def analyze():
    path = editor.get_path()

    if not path:
        return

    if not path.endswith('.py'):
        return

    editor.clear_annotations()

    text = _editor_text()

    annotations = _pep8_annotations(
        text,
        ignore=_ignore_codes(),
        max_line_length=_max_line_length()
    )

    annotations += _pyflakes_annotations(path, text)

    if not annotations:
        console.hud_alert('No Issues Found', 'iob:checkmark_32', _hud_alert_delay())
        return None

    scroll = True
    by_line = sorted(annotations, key=lambda x: x.line)
    for l, a in groupby(by_line, lambda x: x.line):
        _annotate(l, a, scroll)
        scroll = False
