#!python3

import collections
from ctypes import *
from objc_util import *
from objc_util import parse_types
import toggle_comments
import tabs

#
# TODO
#
#  - replace _key_commands global with something more robust
#  - find a way how to provide module/state specific key commands, ie. do not
#    show editor key command if editor is not first responder, ... see
#    _zrzka_keyCommands function for more details
#

UIKeyModifierAlphaShift = 1 << 16 # CapsLock
UIKeyModifierShift      = 1 << 17 # Shift
UIKeyModifierControl    = 1 << 18 # Control
UIKeyModifierAlternate  = 1 << 19 # Option
UIKeyModifierCommand    = 1 << 20 # Command
UIKeyModifierNumericPad = 1 << 21 # Key is located on the numeric keypad

# Keep it ordered to avoid different selector names for the same input & flags
UIKeyModifierNames = collections.OrderedDict([
	(UIKeyModifierAlphaShift, 'CapsLock'),
	(UIKeyModifierShift, 'Shift'),
	(UIKeyModifierControl, 'Control'),
	(UIKeyModifierAlternate, 'Option'),
	(UIKeyModifierCommand, 'Command'),
	(UIKeyModifierNumericPad, 'NumericPad')])
		
UIKeyInputNames = {
	'/': 'Slash',
	'.': 'Dot',
	',': 'Comma',
	'+': 'Plus',
	'-': 'Minus',
	' ': 'Space',
	'_': 'Underscore'
}

PYTHONISTA_SCOPE_GLOBAL = 'global'
PYTHONISTA_SCOPE_EDITOR = 'editor'

UIKeyCommand = ObjCClass('UIKeyCommand')

_key_commands = {
	PYTHONISTA_SCOPE_GLOBAL: [],
	PYTHONISTA_SCOPE_EDITOR: []
}


def _pythonista_scope(key_commands):
	for kc in key_commands:
		if kc.input() == 'L' and kc.modifierFlags() == UIKeyModifierCommand: # Cmd-L Show/Hide Outline
			return PYTHONISTA_SCOPE_EDITOR
	return PYTHONISTA_SCOPE_GLOBAL


def _zrzka_keyCommands(_self, _cmd):
	"""Swizzled version of keyCommands(). It calls original method to get Pythonista shortcuts and then appends custom ones."""
	obj = ObjCInstance(_self)
	commands = list(obj.zrzkaKeyCommands())
	commands.extend(_key_commands[PYTHONISTA_SCOPE_GLOBAL])
	commands.extend(_key_commands[PYTHONISTA_SCOPE_EDITOR])	
	return ns(commands).ptr

	
def _normalize_input(input):
	"""Converts key command input to upper cased string and replaces special characters (like `/`) with name. If the input can't be normalized, `ValueError` is thrown."""	
	if not len(input) == 1:
		raise ValueError('Key command input must be one character')
		
	input = input.upper()
	
	if (input >= 'A' and input <= 'Z') or (input >= '0' and input <= '9'):
		return input

	if input not in UIKeyInputNames:
		raise ValueError('Unsupported key command input: {}'.format(input))		
		
	return UIKeyInputNames[input]
			
	
def _key_command_selector(input, modifier_flags):
	"""Generates ObjC selector for given `input` (key) and `modifier_flags` (command, option, ...)."""	
	s = 'zrzkaHandleKey'
	
	input = _normalize_input(input)
		
	for mod, name in UIKeyModifierNames.items():
		if modifier_flags & mod == mod:			
			s += name
			
	s += input	
	return sel(s)


def _key_window():
	return UIApplication.sharedApplication().keyWindow()
	

@on_main_thread
def _register_key_command(scope, input, modifier_flags, function, title=None):
	if not callable(function):
		raise ValueError('Provided `function` is not callable')
		
	selector = _key_command_selector(input, modifier_flags)
	obj = _key_window()
	
	if obj.respondsToSelector_(selector):
		print('Skipping, selector already registered')
		return False
		
	def key_command_action(_sel, _cmd, sender):
		function()
					
	IMPTYPE = CFUNCTYPE(None, c_void_p, c_void_p, c_void_p)
	imp = IMPTYPE(key_command_action)
	retain_global(imp)
	
	cls = c.object_getClass(obj.ptr)
	did_add = c.class_addMethod(cls, selector, imp, c_char_p('v@:@'.encode('utf-8')))
	if not did_add:
		print('Failed to add key command action selector')
		return False
	
	if not title:
		kc = UIKeyCommand.keyCommandWithInput_modifierFlags_action_(ns(input), modifier_flags, selector)
	else:
		kc = UIKeyCommand.keyCommandWithInput_modifierFlags_action_discoverabilityTitle_(ns(input), modifier_flags, selector, ns(title))
		
	_key_commands[scope].append(kc)
	return False	

																								
@on_main_thread	
def _swizzle_key_commands():
	obj = _key_window()
	cls = c.object_getClass(obj.ptr)
			
	#
	# Add 'zrzkaKeyCommands' and swizzle it with `keyCommands`
	#	

	selector = sel('keyCommands')	
	new_selector = sel('zrzkaKeyCommands')
	
	if obj.respondsToSelector_(new_selector):
		print('Skipping swizzling, already responds to zrzkaKeyCommands selector')
		return
		
	method = c.class_getInstanceMethod(cls, selector)
	if not method:
		print('Failed to get keyCommands instance method')
		return
		
	type_encoding = c.method_getTypeEncoding(method)
	
	parsed_types = parse_types(type_encoding)	
	restype = parsed_types[0]
	argtypes = parsed_types[1]
	
	IMPTYPE = CFUNCTYPE(restype, *argtypes)
	imp = IMPTYPE(_zrzka_keyCommands)
	retain_global(imp)

	new_selector = sel('zrzkaKeyCommands')
	did_add = c.class_addMethod(cls, new_selector, imp, type_encoding)
	
	if not did_add:
		print('Failed to add zrzkaKeyCommands method')
		return
	
	method_exchangeImplementations = c.method_exchangeImplementations
	method_exchangeImplementations.argtypes = [c_void_p, c_void_p]
	method_exchangeImplementations.restype = c_void_p
		
	new_method = c.class_getInstanceMethod(cls, new_selector)
	method_exchangeImplementations(method, new_method)

		
def register():
	_swizzle_key_commands()
	
	commands = {
		PYTHONISTA_SCOPE_GLOBAL: [
		],
		PYTHONISTA_SCOPE_EDITOR: [
			('/', UIKeyModifierCommand, toggle_comments.toggle_comments, 'Toggle Comments'),
			('N', UIKeyModifierCommand, tabs.new_file, 'New File'),
			('N', UIKeyModifierCommand | UIKeyModifierShift, tabs.new_tab, 'New Tab'),
			('0', UIKeyModifierCommand | UIKeyModifierShift, tabs.toggle_navigator, 'Toggle Navigator'),
			('W', UIKeyModifierCommand, tabs.close_current_tab, 'Close Tab'),
			('W', UIKeyModifierCommand | UIKeyModifierShift, tabs.close_all_tabs_except_current_one, 'Close Tabs Except Current One')
		]
	}
	
	for scope, commands in commands.items():
		for command in commands:
			_register_key_command(scope, *command)

