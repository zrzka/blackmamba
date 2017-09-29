#!python3

import os
import urllib
import webbrowser
import ui
from blackmamba.log import error


def script_exists(script_name, full_path=False):
    if not full_path:
        script_name = os.path.join(os.path.expanduser('~/Documents'), script_name)
    return os.path.exists(script_name)


def run_script(script_name, full_path=False, delay=None):
    if not full_path and script_name.startswith('/'):
        script_name = script_name[1:]

    if not script_exists(script_name, full_path):
        error('run_script: script does not exist {}'.format(script_name))
        return

    if full_path:
        docs_root = os.path.expanduser('~/Documents/')
        script_name = script_name[len(docs_root):]

    encoded_name = urllib.parse.quote_plus(script_name, safe='', encoding=None, errors=None)
    url = 'pythonista://{}?action=run'.format(encoded_name)

    if delay:
        def make_open_url(url):
            def open():
                webbrowser.open(url)
            return open

        ui.delay(make_open_url(url), 1.0)
    else:
        webbrowser.open(url)
