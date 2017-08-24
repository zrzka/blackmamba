#!python3

import io
import pep8
import re
from enum import Enum
import pyflakes.api as pyflakes
import editor
import console
import blackmamba.settings as settings
from itertools import groupby

#
# Common for pep8 & pyflakes
#


class _Style(Enum):
    '''Value represents value for style parameter in editor.annotate_line function.'''
    error = 'error'
    warning = 'warning'
    

class _Source(Enum):
    pep8 = 'PEP8'
    pyflakes = 'pyflakes'
    

class _Annotation(object):
    def __init__(self, line, text, source, style):
        self.line = line
        self.text = text
        self.source = source
        self.style = style
                
    @property
    def editor_annotation_style(self):
        return self.style.value
        
    def __lt__(self, other):
        if self.source is _Source.pep8 and other.source is _Source.pyflakes:
            return True
            
        if self.style is _Style.warning and other.style is _Style.error:
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
            
        annotation = _Annotation(self.line_offset + line_number, text, _Source.pep8, _Style.warning)
        self.annotations.append(annotation)
        
        
def _pep8_annotations(text, ignore=None, max_line_length=None):
    # pep8 requires you to include \n at the end of lines
    lines = text.splitlines(True)
    
    # ignore
    # max_line_length
    
    style_guide = pep8.StyleGuide(reporter=_Pep8AnnotationReport, )
    options = style_guide.options
    
    if ignore:
        options.ignore += ignore
        
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
            
        line = line[(l+1):]  # Strip 'filename:'
        match = _LINE_COL_MESSAGE_REGEX.fullmatch(line)
        
        if not match:
            match = _LINE_MESSAGE_REGEX.fullmatch(line)
        
        if not match:
            continue
        
        line = int(match.group(1))
        
        if match.lastindex == 3:
            annotation = _Annotation(
                line, 'Col {}: {}'.format(match.group(2), match.group(3)),
                _Source.pyflakes, style
            )
        else:
            annotation = _Annotation(
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
    
    warnings = _get_annotations(path, warning_stream, _Style.warning)
    errors = _get_annotations(path, error_stream, _Style.error)
    
    return warnings + errors

        
def _annotate(line, annotations, scroll):
    by_priority = sorted(annotations, reverse=True)

    style = by_priority[0].editor_annotation_style
    text = ',\n'.join([a.text for a in by_priority])
            
    editor.annotate_line(line, text, style, True, scroll=scroll)
    
    
def clear_annotations():
    editor.clear_annotations()
    

def analyze():
    path = editor.get_path()
    
    if not path:
        return
        
    if not path.endswith('.py'):
        return
    
    editor.clear_annotations()
        
    text = editor.get_text()
    annotations = _pep8_annotations(
        text,
        ignore=settings.ANALYZER_PEP8_IGNORE,
        max_line_length=settings.ANALYZER_PEP8_MAX_LINE_LENGTH
    )
    
    annotations += _pyflakes_annotations(path, text)
    
    if not annotations:
        console.hud_alert('No Issues Found', 'iob:checkmark_32', settings.ANALYZER_HUD_DELAY)
        return None
    
    scroll = True
    by_line = sorted(annotations, key=lambda x: x.line)
    for l, a in groupby(by_line, lambda x: x.line):
        _annotate(l, a, scroll)
        scroll = False

