#!python3
'''Black Mamba configuration module.

Note:
    This module must not introduce dependency on any other Black Mamba
    modules and must be importable on any other platform as well.
'''

from collections import Mapping
from copy import deepcopy

__all__ = ['get_config_value']

_DEFAULTS = {
    'general': {
        'register_key_commands': True,
        'page_line_count': 40
    },
    'project': {
        'index': {
            'rate': 60,
            'auto_save': True
        }
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
        'ignore_codes': None,
        'max_line_length': 127,
        'remove_whitespaces': True
    },
    'tester': {
        'hud_alert_delay': 1.0,
        'hide_console': True
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
