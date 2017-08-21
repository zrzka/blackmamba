#!python3

import collections
from ctypes import *
from objc_util import *
from blackmamba.runtime import swizzle
from blackmamba.uikit import *

#
# TODO
#
#  - replace _key_commands global with something more robust
#  - find a way how to provide module/state specific key commands, ie. do not
#    show editor key command if editor is not first responder, ... see
#    _zrzka_keyCommands function for more details
#

# Keep it ordered to avoid different selector names for the same input & flags
UIKeyModifierNames = collections.OrderedDict([
    (UIKeyModifierAlphaShift, 'CapsLock'),
    (UIKeyModifierShift, 'Shift'),
    (UIKeyModifierControl, 'Control'),
    (UIKeyModifierAlternate, 'Option'),
    (UIKeyModifierCommand, 'Command'),
    (UIKeyModifierNumericPad, 'NumericPad')
])

UIKeyInputNames = {
    '/': 'Slash',
    '.': 'Dot',
    ',': 'Comma',
    '+': 'Plus',
    '-': 'Minus',
    ' ': 'Space',
    '_': 'Underscore'
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
    
    if not len(input) == 1:
        raise ValueError('Key command input must be one character')

    input = input.upper()

    if (input >= 'A' and input <= 'Z') or (input >= '0' and input <= '9'):
        return input

    if input not in UIKeyInputNames:
        raise ValueError('Unsupported key command input: {}'.format(input))

    return UIKeyInputNames[input]


def _key_command_selector_name(input, modifier_flags):
    """Generates ObjC selector for given input (key) and
    modifier_flags (command, option, ...)."""
    s = 'blackMambaHandleKey'

    input = _normalize_input(input)

    for mod, name in UIKeyModifierNames.items():
        if modifier_flags & mod == mod:
            s += name
    
    s += input
    return s


@on_main_thread
def register_key_command(input, modifier_flags, function, title=None):
    if not UIApplication.sharedApplication().respondsToSelector_(sel('originalkeyCommands')):
        swizzle('UIApplication', 'keyCommands', _blackmamba_keyCommands)
            
    selector_name = _key_command_selector_name(input, modifier_flags)
    selector = sel(selector_name)
    obj = UIApplication.sharedApplication().keyWindow()
    
    print('Registering key command {} ({})'.format(selector_name, function))
    
    if not callable(function):
        print('Skipping, provided function is not callable')
        return False
    
    if obj.respondsToSelector_(selector):
        print('Skipping, method {} already registered'.format(selector_name))
        return False

    def key_command_action(_sel, _cmd, sender):
        try:
            function()
        except Exception as ex:
            print('Exception in {} method'.format(selector_name))
            print(ex)

    IMPTYPE = CFUNCTYPE(None, c_void_p, c_void_p, c_void_p)
    imp = IMPTYPE(key_command_action)
    retain_global(imp)

    cls = c.object_getClass(obj.ptr)
    type_encoding = c_char_p('v@:@'.encode('utf-8'))
    did_add = c.class_addMethod(cls, selector, imp, type_encoding)
    if not did_add:
        print('Failed to add key command method {}'.format(selector_name))
        return False

    if title:
        kc = UIKeyCommand.keyCommandWithInput_modifierFlags_action_discoverabilityTitle_(ns(input), modifier_flags, selector, ns(title))
    else:
        kc = UIKeyCommand.keyCommandWithInput_modifierFlags_action_(ns(input), modifier_flags, selector)

    _key_commands.append(kc)
    return True

