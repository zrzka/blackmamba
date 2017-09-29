#!python3

from ctypes import CFUNCTYPE, c_void_p, c_char_p
from objc_util import retain_global, ObjCInstance, UIApplication, c, ns, on_main_thread, sel, ObjCClass
from blackmamba.util.runtime import swizzle
from blackmamba.log import error, info
import blackmamba.system as system
from enum import Enum, IntEnum, IntFlag

if system.IOS:
    _UIKeyboardImpl = ObjCClass('UIKeyboardImpl')
else:
    _UIKeyboardImpl = None


def is_in_hardware_keyboard_mode():
    if not _UIKeyboardImpl:
        return False

    return _UIKeyboardImpl.sharedInstance().isInHardwareKeyboardMode()


UIKeyCommand = ObjCClass('UIKeyCommand')


class UIKeyModifier(IntFlag):
    none = 0
    alphaShift = 1 << 16  # CapsLock
    shift = 1 << 17  # Shift
    control = 1 << 18  # Control
    alternate = 1 << 19  # Option
    command = 1 << 20  # Command
    numericPad = 1 << 21  # Key on numeric keypad

    @property
    def selector_name(self):
        flags = [
            name.title()
            for name, value in UIKeyModifier.__members__.items()
            if value & self is value and not value == 0
        ]
        if flags:
            return ''.join(flags)
        else:
            return ''


class UIEventType(IntEnum):
    touches = 0
    motion = 1
    remoteControl = 2
    presses = 3
    physicalKeyboard = 4


class UIEventSubtype(IntEnum):
    none = 0


class UIEventKeyCode(IntEnum):
    right = 79
    left = 80
    down = 81
    up = 82
    enter = 40
    space = 44
    backspace = 42
    escape = 41
    leftSquareBracket = 47
    dot = 55


class UIKeyInput(str, Enum):
    leftArrow = 'UIKeyInputLeftArrow'
    rightArrow = 'UIKeyInputRightArrow'
    upArrow = 'UIKeyInputUpArrow'
    downArrow = 'UIKeyInputDownArrow'

    @property
    def selector_name(self):
        return self.name.title()


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
    '?': 'QuestionMark'
}

_key_commands = []


def _blackmamba_keyCommands(_self, _cmd):
    """Swizzled version of keyCommands(). It calls original method to
    get Pythonista shortcuts and then appends custom ones."""
    obj = ObjCInstance(_self)
    commands = list(obj.originalkeyCommands())
    commands.extend(_key_commands)
    return ns(commands).ptr


def _input_selector_name(input):
    if isinstance(input, UIKeyInput):
        return input.selector_name

    assert(isinstance(input, str))

    if len(input) == 1:
        input = input.upper()

        if (input >= 'A' and input <= 'Z') or (input >= '0' and input <= '9'):
            return input

    if input not in _UIKeyInputNames:
        raise ValueError('Unsupported key command input: {}'.format(input))

    return _UIKeyInputNames[input]


def _key_command_selector_name(input, modifier):
    assert(isinstance(modifier, UIKeyModifier))

    return 'blackMambaHandleKey{}{}'.format(
        modifier.selector_name,
        _input_selector_name(input)
    )


def _shortcut_name(input, modifier):
    return '{} {}'.format(
        modifier.selector_name,
        _input_selector_name(input)
    )


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
        kc = UIKeyCommand.keyCommandWithInput_modifierFlags_action_discoverabilityTitle_(
            ns(input), modifier_flags, selector, ns(title))
    else:
        kc = UIKeyCommand.keyCommandWithInput_modifierFlags_action_(ns(input), modifier_flags, selector)

    _key_commands.append(kc)
    return True


_key_event_handlers = []


class KeyEventHandler(object):
    def __init__(self, key_code, modifier, fn):
        self.key_code = key_code
        self.modifier = modifier
        self.fn = fn


def _blackmamba_handleKeyUIEvent(_self, _cmd, event):
    e = ObjCInstance(event)

    consume = False
    if e.type() == UIEventType.physicalKeyboard.value and e.subtype() == UIEventSubtype.none.value:
        for h in _key_event_handlers:
            if h.key_code == e._keyCode() and h.modifier.value == e._modifierFlags():
                if e._isKeyDown():
                    consume = True
                else:
                    h.fn()
                break

    if not consume:
        ObjCInstance(_self).originalhandleKeyUIEvent_(e)


@on_main_thread
def register_key_event_handler(key_code, func, *, modifier=UIKeyModifier.none):
    if not UIApplication.sharedApplication().respondsToSelector_(sel('originalhandleKeyUIEvent:')):
        swizzle('UIApplication', 'handleKeyUIEvent:', _blackmamba_handleKeyUIEvent)

    @system.catch_exceptions
    def invoke_func():
        func()

    handler = KeyEventHandler(key_code, modifier, invoke_func)
    _key_event_handlers.append(handler)
    return handler


@on_main_thread
def unregister_key_event_handler(handler):
    try:
        _key_event_handlers.remove(handler)
    except ValueError:
        pass
