#!python3

from objc_util import ObjCClass
import editor

_DEFAULTS = ObjCClass('NSUserDefaults').standardUserDefaults()

_THEME = {
    'active_bar_background_color': ('bar_background', '#ffffff'),
    'inactive_bar_background_color': ('tab_background', '#f0f0f0'),
    'bar_title_color': ('tab_title', '#000000'),
    'text_color': ('default_text', '#000000'),
    'tint_color': ('tint', '#5794b0'),
    'separator_color': ('separator_line', '#b3b3b3'),
    'background_color': ('background', '#ffffff')
}


def get_theme():
    return editor.get_theme_dict()


def get_theme_value(key):
    theme = get_theme()
    if key in _THEME:
        return theme.get(_THEME[key][0], _THEME[key][1])
    return theme.get(key, None)


def get_editor_font_name():
    return str(_DEFAULTS.objectForKey_('EditorFontName'))


def get_editor_font_size():
    return int(_DEFAULTS.integerForKey_('EditorFontSize'))


def get_editor_font():
    return get_editor_font_name(), get_editor_font_size()
