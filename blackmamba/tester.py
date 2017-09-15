#!python3

import pytest
import editor
import os
import xml.etree.ElementTree as ET
import console
from blackmamba.annotation import Annotation, Style
from blackmamba.config import get_config_value
from blackmamba.ide import save
import re

_LOG_FILE_PATH = os.path.expanduser('~/Documents/.blackmamba_pytest_log.xml')


def _hud_alert_delay():
    return get_config_value('tester.hud_alert_delay', 1.0)


def _hide_console():
    return get_config_value('tester.hide_console', True)


def _remove_log_file():
    if os.path.isfile(_LOG_FILE_PATH):
        os.remove(_LOG_FILE_PATH)


def _parse_line(file, text, line):
    # Test case line number points to the test function, not actual issue
    # If we can parse, we'll return the correct one, otherwise fallback
    # to the test function

    pattern = re.escape(file) + '\:(\d+)\:'

    match = re.search(pattern, text, re.MULTILINE)
    if match:
        return int(match.group(1))
    return line


def _parse_log_file():
    if not os.path.isfile(_LOG_FILE_PATH):
        return

    try:
        suite = ET.parse(_LOG_FILE_PATH).getroot()
    except:
        return

    if not suite.tag == 'testsuite':
        return

    result = []
    for tc in list(suite):
        if not tc.tag == 'testcase':
            continue

        for failure in list(tc):
            if not failure.tag == 'failure':
                continue

            file = tc.get('file')
            text = failure.get('message')
            line = _parse_line(file, failure.text, int(tc.get('line')))

            annotation = Annotation(line, text, Style.error)  # , os.path.basename(file))
            result.append(annotation)

    return (suite.attrib, result)


def _show_results(attrib, all_passed=True):
    x = {
        'errors': 'errored',
        'failures': 'failed',
        'skips': 'skipped'
    }

    tests = int(attrib.get('tests', 0))
    time = attrib.get('time', '?')

    messages = []

    for k, v in x.items():
        c = int(attrib.get(k, 0))

        if c > 0:
            tests -= c
            messages.append('{} {}'.format(c, v))

    messages.append('{} passed'.format(tests))

    console.hud_alert(
        ', '.join(messages) + ' in {} seconds'.format(time),
        'success' if all_passed else 'error',
        _hud_alert_delay())


def _run_unit_tests(path):
    editor.clear_annotations()

    _remove_log_file()
    pytest.main(['-q', '--junitxml={}'.format(_LOG_FILE_PATH), path])
    attrib, annotations = _parse_log_file()

    _show_results(attrib, not annotations)

    scroll = True
    for a in annotations:
        editor.annotate_line(a.line, a.text, a.editor_annotation_style, True, filename=a.filename, scroll=scroll)
        scroll = False

    if _hide_console():
        console.hide_output()


def run_script_unit_tests():
    path = editor.get_path()

    if not path:
        return

    if not path.endswith('.py'):
        return

    save(all=True)
    _run_unit_tests(path)
