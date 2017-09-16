#!python3

import collections
from ctypes import CFUNCTYPE, c_void_p, c_char_p
from objc_util import retain_global, ObjCInstance, UIApplication, c, ns, on_main_thread, sel, ObjCClass
from blackmamba.runtime import swizzle
from blackmamba.log import error, info
import blackmamba.system as system

_UIKeyCommand = ObjCClass('UIKeyCommand')

# UIKeyModifierFlags

UIKeyModifierAlphaShift = 1 << 16  # CapsLock
UIKeyModifierShift = 1 << 17  # Shift
UIKeyModifierControl = 1 << 18  # Control
UIKeyModifierAlternate = 1 << 19  # Option
UIKeyModifierCommand = 1 << 20  # Command
UIKeyModifierNumericPad = 1 << 21  # Key is located on the numeric keypad

UIKeyInputLeftArrow = 'UIKeyInputLeftArrow'
UIKeyInputRightArrow = 'UIKeyInputRightArrow'
UIKeyInputUpArrow = 'UIKeyInputUpArrow'
UIKeyInputDownArrow = 'UIKeyInputDownArrow'


# Keep it ordered to avoid different selector names for the same input & flags
_UIKeyModifierNames = collections.OrderedDict([
    (UIKeyModifierAlphaShift, 'CapsLock'),
    (UIKeyModifierShift, 'Shift'),
    (UIKeyModifierControl, 'Control'),
    (UIKeyModifierAlternate, 'Option'),
    (UIKeyModifierCommand, 'Command'),
    (UIKeyModifierNumericPad, 'NumericPad')
])

_UIKeyInputNames = {
    '/': 'Slash',
    '.': 'Dot',
    ',': 'Comma',
    '+': 'Plus',
    '-': 'Minus',
    ' ': 'Space',
    '_': 'Underscore',
    '\t': 'Tab',
    '[': 'LeftSquareBracket',
    ']': 'RightSquareBracket',
    UIKeyInputLeftArrow: 'Left',
    UIKeyInputRightArrow: 'Right',
    UIKeyInputUpArrow: 'Up',
    UIKeyInputDownArrow: 'Down'
}

_key_commands = []


def _blackmamba_keyCommands(_self, _cmd):
    """Swizzled version of keyCommands(). It calls original method to
    get Pythonista shortcuts and then appends custom ones."""
    obj = ObjCInstance(_self)
    commands = list(obj.originalkeyCommands())
    commands.extend(_key_commands)
    return ns(commands).ptr


def _normalize_input(input):
    """Converts key command input to upper cased string and replaces
    special characters (like /) with name. If the input can't be
    normalized, ValueError is thrown."""

    if len(input) == 1:
        input = input.upper()

        if (input >= 'A' and input <= 'Z') or (input >= '0' and input <= '9'):
            return input

    if input not in _UIKeyInputNames:
        raise ValueError('Unsupported key command input: {}'.format(input))

    return _UIKeyInputNames[input]


def _key_command_selector_name(input, modifier_flags):
    """Generates ObjC selector for given input (key) and
    modifier_flags (command, option, ...)."""
    s = 'blackMambaHandleKey'

    input = _normalize_input(input)

    for mod, name in _UIKeyModifierNames.items():
        if modifier_flags & mod == mod:
            s += name

    s += input
    return s


def _shortcut_name(input, modifier_flags):
    modifier_names = [name for mod, name in _UIKeyModifierNames.items() if modifier_flags & mod == mod]

    if modifier_names:
        return '{} {}'.format(' '.join(modifier_names), input)

    return input


@system.Pythonista(appex=False)
@on_main_thread
def register_key_command(input, modifier_flags, function, title=None):
    if not UIApplication.sharedApplication().respondsToSelector_(sel('originalkeyCommands')):
        swizzle('UIApplication', 'keyCommands', _blackmamba_keyCommands)

    selector_name = _key_command_selector_name(input, modifier_flags)
    selector = sel(selector_name)
    obj = UIApplication.sharedApplication().keyWindow()

    info('Registering key command "{}" ({})'.format(
        _shortcut_name(input, modifier_flags),
        title or 'No discoverability title'
    ))

    if not callable(function):
        error('Skipping, provided function is not callable')
        return False

    if obj.respondsToSelector_(selector):
        error('Skipping, method {} already registered'.format(selector_name))
        return False

    def key_command_action(_sel, _cmd, sender):
        function()

    IMPTYPE = CFUNCTYPE(None, c_void_p, c_void_p, c_void_p)
    imp = IMPTYPE(key_command_action)
    retain_global(imp)

    cls = c.object_getClass(obj.ptr)
    type_encoding = c_char_p('v@:@'.encode('utf-8'))
    did_add = c.class_addMethod(cls, selector, imp, type_encoding)
    if not did_add:
        error('Failed to add key command method {}'.format(selector_name))
        return False

    if title:
        kc = _UIKeyCommand.keyCommandWithInput_modifierFlags_action_discoverabilityTitle_(
            ns(input), modifier_flags, selector, ns(title))
    else:
        kc = _UIKeyCommand.keyCommandWithInput_modifierFlags_action_(ns(input), modifier_flags, selector)

    _key_commands.append(kc)
    return True
