#!python3

"""Keyboard shortcuts.

Key commands
============

Key command is kind of global shortcut in Pythonista. They're visible if you
hold down ``Cmd`` key for example. Black Mamba does use key commands for
shortcuts like toggle comments, etc.

Related functions:

    * `UIKeyModifier`
    * `UIKeyInput`
    * `register_key_command`

Following example shows how to print *Hallo* with ``Cmd H`` keyboard shortcut::

    from blackmamba.uikit.keyboard import (
        register_key_command, UIKeyModifier
    )

    def hallo():
        print('Hallo')

    register_key_command(
        'h',
        UIKeyModifier.command,
        hallo,
        'Print Hallo'  # Optional discoverability title (hold down Cmd)
    )

Key event handlers
==================

Key event handler is kind of local keyboard shortcut. They're not visible
if you hold down ``Cmd`` key. Designed to be used in custom dialogs.

Related functions:

    * `UIKeyModifier`
    * `UIEventKeyCode`
    * `register_key_event_handler`
    * `unregister_key_event_handler`

Following example shows how to close dialog with ``Cmd .`` keyboard shortcut::

    from blackmamba.uikit.keyboard import (
        register_key_event_handler, UIEventKeyCode, UIKeyModifier,
        unregister_key_event_handlers
    )

    class MyView(ui.View):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            def close_me():
                self.close()

            self._handlers = [
                register_key_event_handler(UIEventKeyCode.dot, close_me, modifier=UIKeyModifier.command)
            ]

        def will_close(self):
            unregister_key_event_handlers(self._handlers)
"""
from ctypes import CFUNCTYPE, c_void_p, c_char_p
from objc_util import retain_global, ObjCInstance, UIApplication, c, ns, on_main_thread, sel, ObjCClass
from blackmamba.util.runtime import swizzle
from blackmamba.log import error, info
import blackmamba.system as system
from enum import Enum, IntEnum
from typing import Union, Callable, List


if system.IOS:
    _UIKeyboardImpl = ObjCClass('UIKeyboardImpl')
else:
    _UIKeyboardImpl = None


def is_in_hardware_keyboard_mode() -> bool:
    """Check if HW keyboard is connected.

    Returns:
        `True` if HW keyboard is connected.
    """
    if not _UIKeyboardImpl:
        return False

    return _UIKeyboardImpl.sharedInstance().isInHardwareKeyboardMode()


UIKeyCommand = ObjCClass('UIKeyCommand')


class UIKeyModifier(IntEnum):
    """Key modifiers.

    Modifiers can be combined like::

        UIKeyModifier.command | UIKeyModifier.shift

    See also:

        * `register_key_command`
        * `register_key_event_handler`
    """

    none = 0
    """No modifier key."""

    alphaShift = 1 << 16  # CapsLock
    """Caps Lock key."""

    shift = 1 << 17  # Shift
    """Shift key."""

    control = 1 << 18  # Control
    """Control key."""

    alternate = 1 << 19  # Option
    """Option key."""

    command = 1 << 20  # Command
    """Command key."""

    numericPad = 1 << 21  # Key on numeric keypad
    """Key is on numberic pad."""


class UIEventType(IntEnum):
    touches = 0
    motion = 1
    remoteControl = 2
    presses = 3
    physicalKeyboard = 4


class UIEventSubtype(IntEnum):
    none = 0


class UIEventKeyCode(IntEnum):
    """Event key codes.

    Not all key codes are listed / included here. Feel free to create pull request with more
    key codes if you'd like to use them.

    See also:

        * `register_key_event_handler`
    """

    right = 79
    """Right arrow key."""

    left = 80
    """Left arrow key."""

    down = 81
    """Down arrow key."""

    up = 82
    """Up arrow key."""

    enter = 40
    """Enter key."""

    space = 44
    """Space key."""

    backspace = 42
    """Backspace key."""

    escape = 41
    """Escape key."""

    leftSquareBracket = 47
    """Left square bracket."""

    dot = 55
    """Dot key."""


class UIKeyInput(str, Enum):
    """Enumeration of special key input values.

    See also:

        * `register_key_command`
    """

    leftArrow = 'UIKeyInputLeftArrow'
    """Left arrow."""

    rightArrow = 'UIKeyInputRightArrow'
    """Right arrow."""

    upArrow = 'UIKeyInputUpArrow'
    """Up arrow."""

    downArrow = 'UIKeyInputDownArrow'
    """Down arrow."""

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
    commands = list(obj.originalkeyCommands() or [])
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


def _modifier_selector_name(modifier):
    _names = {
        UIKeyModifier.alphaShift: 'AlphaShift',
        UIKeyModifier.shift: 'Shift',
        UIKeyModifier.control: 'Control',
        UIKeyModifier.alternate: 'Alternate',
        UIKeyModifier.command: 'Command',
        UIKeyModifier.numericPad: 'NumericPad'
    }

    if isinstance(modifier, UIKeyModifier):
        modifier = modifier.value

    flags = [
        name
        for mod, name in _names.items()
        if mod.value & modifier
    ]

    if flags:
        return ''.join(flags)
    else:
        return ''


def _key_command_selector_name(input, modifier):
    return 'blackMambaHandleKey{}{}'.format(
        _modifier_selector_name(modifier),
        _input_selector_name(input)
    )


def _shortcut_name(input, modifier):
    return '{} {}'.format(
        _modifier_selector_name(modifier),
        _input_selector_name(input)
    )


@system.Pythonista(appex=False)
@on_main_thread
def _register_key_command(input, modifier_flags, function, title=None):
    if not UIApplication.sharedApplication().respondsToSelector_(sel('originalkeyCommands')):
        swizzle('UIApplication', 'keyCommands', _blackmamba_keyCommands)

    selector_name = _key_command_selector_name(input, modifier_flags)
    selector = sel(selector_name)
    obj = UIApplication.sharedApplication()

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

    if isinstance(modifier_flags, UIKeyModifier):
        modifier_flags = modifier_flags.value

    if title:
        kc = UIKeyCommand.keyCommandWithInput_modifierFlags_action_discoverabilityTitle_(
            ns(input), modifier_flags, selector, ns(title))
    else:
        kc = UIKeyCommand.keyCommandWithInput_modifierFlags_action_(ns(input), modifier_flags, selector)

    _key_commands.append(kc)
    return True


def register_key_command(input: Union[str, UIKeyInput], modifier_flags: UIKeyModifier,
                         function: Callable[[], None], title: str=None) -> bool:
    """Register key command.

    .. note:: There's no function to unregister key commands.

    Args:
        input: String like ``A`` or special `UIKeyInput` value
        modifier_flags: Modifier flags
        function: Function to call
        title: Discoverability title

    Returns:
        `True` if key command was registered.
    """
    return _register_key_command(input, modifier_flags, function, title)


_key_event_handlers = []


class KeyEventHandler(object):
    """Key event handler object.

    .. note:: Use it only and only for key event deregistration (`unregister_key_event_handler`).

    Attributes:
        key_code (UIEventKeyCode): Key code
        modifier (UIKeyModifier): Modifier flags
        fn (Callable): Function to call
    """
    def __init__(self, key_code: UIEventKeyCode, modifier: UIKeyModifier, fn: Callable[[], None]):
        if isinstance(key_code, UIEventKeyCode):
            self.key_code = key_code.value
        else:
            self.key_code = key_code
        if isinstance(modifier, UIKeyModifier):
            self.modifier = modifier.value
        else:
            self.modifier = modifier
        self.fn = fn


def _blackmamba_handleKeyUIEvent(_self, _cmd, event):
    e = ObjCInstance(event)

    if e.type() == UIEventType.physicalKeyboard.value and e.subtype() == UIEventSubtype.none.value:
        for h in _key_event_handlers:
            if h.key_code == e._keyCode() and h.modifier == e._modifierFlags():
                if not e._isKeyDown():
                    h.fn()
                return

    ObjCInstance(_self).originalhandleKeyUIEvent_(e)


@on_main_thread
def _register_key_event_handler(key_code, func, *, modifier=UIKeyModifier.none):
    if not UIApplication.sharedApplication().respondsToSelector_(sel('originalhandleKeyUIEvent:')):
        swizzle('UIApplication', 'handleKeyUIEvent:', _blackmamba_handleKeyUIEvent)

    @system.catch_exceptions
    def invoke_func():
        func()

    handler = KeyEventHandler(key_code, modifier, invoke_func)
    _key_event_handlers.append(handler)
    return handler


def register_key_event_handler(key_code: UIEventKeyCode, func: Callable[[], None],
                               *, modifier: UIKeyModifier=UIKeyModifier.none) -> KeyEventHandler:
    """Register key event handler.

    Usable in dialogs for example. Do not forget to unregister key event
    handler in ``will_close`` function of your ``ui.View``.

    Args:
        key_code: Key code
        func: Function to call
        modifier: Modifier flags

    Returns:
        `KeyEventHandler` to use in `unregister_key_event_handler`.
    """
    return _register_key_event_handler(key_code, func, modifier=modifier)


@on_main_thread
def _unregister_key_event_handler(handler):
    try:
        _key_event_handlers.remove(handler)
    except ValueError:
        pass


def unregister_key_event_handler(handler: KeyEventHandler):
    """Unregister key event handler.

    It is safe to call this function multiple times with the same handler. Handler
    is silently ignored if it's not registered.

    Args:
        handler: Key event handler to unregister
    """
    _unregister_key_event_handler(handler)


def unregister_key_event_handlers(handlers: List[KeyEventHandler]):
    """Unregister list of key event handlers.

    Convenience function, it just calls `unregister_key_event_handler` for every handler.

    Args:
        handlers: List of handlers
    """
    for handler in handlers:
        unregister_key_event_handler(handler)
