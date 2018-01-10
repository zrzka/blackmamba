#!python3
from collections import Mapping
from copy import deepcopy

__all__ = ['get_config_value']

_DEFAULTS = {
    'general': {
        'jedi': False,
        'register_key_commands': True,
        'page_line_count': 40
    },
    'update': {
        'enabled': True,
        'interval': 3600
    },
    'file_picker': {
        'ignore_folders': {
            '': ['.git'],
            '.': ['.Trash', 'Examples',
                  'site-packages', 'site-packages-2', 'site-packages-3']
        }
    },
    'analyzer': {
        'hud_alert_delay': 1.0,
        'remove_whitespaces': True,
        'flake8': [
            # 1st pass
            ['--select=E901,E999,F821,F822,F823'],
            # 2nd pass
            ['--max-complexity=10', '--max-line-length=127']
        ]
    },
    'tester': {
        'hud_alert_delay': 1.0,
        'hide_console': True
    },
    'drag_and_drop': {
        'ignore_folders': {
            '': ['.git'],
            '.': ['.Trash', 'Examples',
                  'site-packages', 'site-packages-2', 'site-packages-3', 'stash_extensions']
        }
    },
    'documentation': {
        'reuse': True,
        'frame': (630, 110, 730, 350)
    }
}

_config = dict(_DEFAULTS)


def get_config_value(key_path, default=None):
    v = _config
    try:
        for k in key_path.split('.'):
            v = v[k]
        return v
    except TypeError:
        return default
    except KeyError:
        return default


def _update(d, u):
    for k, v in u.items():
        if isinstance(d, Mapping):
            if isinstance(v, Mapping):
                d[k] = _update(d.get(k, {}), v)
            else:
                d[k] = v
        else:
            d = {k: v}
    return d


def update_config_with_dict(d):
    global _config
    _config = _update(deepcopy(_config), d)
