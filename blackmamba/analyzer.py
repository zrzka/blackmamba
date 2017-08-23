#!python3

import pyflakes.api as pyflakes
import editor
import io
import re
import console

_LINE_COL_MESSAGE_REGEX = re.compile('^(\d+):(\d+): (.*)$')
_LINE_MESSAGE_REGEX = re.compile('^(\d+): (.*)$')

def _filter_stream(path, stream):
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
            column = int(match.group(2))
            message = match.group(3)
        else:
            column = None
            message = match.group(2)
        
        annotations.append((line, column, message))
        
    return annotations


def _annotate(line, column, message, style, expand, path):
    if column is not None:
        message = '{}: {}'.format(column, message)
        
    editor.annotate_line(line, message, style, expand, filename=path)


def analyze():
    path = editor.get_path()
    
    # Nothing opened, silently skip
    if not path:
        return
    
    # Not a Python file, silently skip
    if not path.endswith('.py'):
        return
    
    editor.clear_annotations(path)
                
    text = editor.get_text()
    
    warning_stream = io.StringIO()
    error_stream = io.StringIO()
    reporter = pyflakes.modReporter.Reporter(warning_stream, error_stream)
    
    count = pyflakes.check(text, path, reporter)
    
    if count == 0:
        console.hud_alert('No Issues Found', 'iob:checkmark_32', 1.0)
        return None

    warnings = _filter_stream(path, warning_stream)
    errors = _filter_stream(path, error_stream)
            
    for (line, col, message) in errors:
        _annotate(line, col, message, 'error', True, path)
        
    for (line, col, message) in warnings:
        _annotate(line, col, message, 'warning', True, path)

    title = ''
    
    if len(errors):
        title += '{} error(s)'.format(len(errors))
        
    if len(warnings):
        title += '{}{} warning(s)'.format(
            ', ' if len(title) else '',
            len(warnings))
        
    if title:
        title += ' found'
    else:
        title = '{} Issue(s) Found'.format(count)
                                                            
    console.hud_alert(title, 'iob:alert_32', 1.0)

