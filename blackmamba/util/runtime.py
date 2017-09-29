#!python3

from objc_util import on_main_thread, c, parse_types, ObjCClass, sel, retain_global
from ctypes import CFUNCTYPE, c_void_p, c_char_p, c_ulong, c_int, Structure, cast, POINTER
from blackmamba.log import error

SWIZZLED_SELECTOR_PREFIX = 'original'


method_exchangeImplementations = c.method_exchangeImplementations
method_exchangeImplementations.argtypes = [c_void_p, c_void_p]
method_exchangeImplementations.restype = c_void_p


@on_main_thread
def add_method(cls_name, selector_name, fn, type_encoding):
    cls = ObjCClass(cls_name).ptr

    selector = sel(selector_name)

    if c.class_getInstanceMethod(cls, selector):
        error('Failed to add method, class {} already provides method {}'.format(cls_name, selector_name))
        return

    parsed_types = parse_types(type_encoding)
    restype = parsed_types[0]
    argtypes = parsed_types[1]

    IMPTYPE = CFUNCTYPE(restype, *argtypes)
    imp = IMPTYPE(fn)
    retain_global(imp)

    did_add = c.class_addMethod(cls, selector, imp, c_char_p(type_encoding.encode('utf-8')))
    if not did_add:
        error('Failed to add class method')

    return did_add


@on_main_thread
def swizzle(cls_name, selector_name, fn):
    cls = ObjCClass(cls_name).ptr

    new_selector_name = SWIZZLED_SELECTOR_PREFIX + selector_name
    new_selector = sel(new_selector_name)

    if c.class_getInstanceMethod(cls, new_selector):
        error('Skipping swizzling, already responds to {} selector'.format(new_selector_name))
        return

    selector = sel(selector_name)
    method = c.class_getInstanceMethod(cls, selector)
    if not method:
        error('Failed to get {} instance method'.format(selector_name))
        return

    type_encoding = c.method_getTypeEncoding(method)
    parsed_types = parse_types(type_encoding)
    restype = parsed_types[0]
    argtypes = parsed_types[1]

    IMPTYPE = CFUNCTYPE(restype, *argtypes)
    imp = IMPTYPE(fn)
    retain_global(imp)

    did_add = c.class_addMethod(cls, new_selector, imp, type_encoding)

    if not did_add:
        error('Failed to add {} method'.format(new_selector_name))
        return

    new_method = c.class_getInstanceMethod(cls, new_selector)
    method_exchangeImplementations(method, new_method)


#
# https://clang.llvm.org/docs/Block-ABI-Apple.html
#

_BLOCK_HAS_COPY_DISPOSE = 1 << 25
_BLOCK_HAS_CTOR = 1 << 26
_BLOCK_IS_GLOBAL = 1 << 28
_BLOCK_HAS_STRET = 1 << 29
_BLOCK_HAS_SIGNATURE = 1 << 30


class _BlockDescriptor(Structure):
    _fields_ = [('reserved', c_ulong),
                ('size', c_ulong),
                ('copy_helper', c_void_p),     # flags & (1<<25)
                ('dispose_helper', c_void_p),  # flags & (1<<25)
                ('signature', c_char_p)]       # flags & (1<<30)


class _Block(Structure):
    _fields_ = [('isa', c_void_p),
                ('flags', c_int),
                ('reserved', c_int),
                ('invoke', c_void_p),
                ('descriptor', _BlockDescriptor)]


class ObjCBlockPointer():
    def __init__(self, block_ptr, restype=None, argtypes=None):
        self._block_ptr = block_ptr
        self._block = cast(self._block_ptr, POINTER(_Block))

        if not argtypes:
            argtypes = []

        if self._regular_calling_convention():
            # First arg is pointer to block, hide it from user
            argtypes.insert(0, c_void_p)

        if self._has_signature():
            # TODO - Validate restype & argtypes against signature
            #      - Signature is not always populated
            pass

        self._func = None

        if self._regular_calling_convention():
            IMPTYPE = CFUNCTYPE(restype, *argtypes)
            self._func = IMPTYPE(self._block.contents.invoke)

    def _flags(self):
        return self._block.contents.flags

    def _has_signature(self):
        has_signature = {
            (0 << 29): False,
            (1 << 29): False,
            (2 << 29): True,
            (3 << 29): True
        }

        return has_signature.get(self._flags() & (3 << 29), False)

    def _signature(self):
        if not self._has_signature():
            return None

        flags = self._flags()

        if flags & _BLOCK_HAS_COPY_DISPOSE:
            signature = self._block.contents.descriptor.signature
        else:
            signature = self._block.contents.descriptor.copy_helper

        return signature

    def _regular_calling_convention(self):
        flags = self._flags() & (3 << 29)
        return flags == (2 << 29)

    def _stret_calling_convention(self):
        flags = self._flags() & (3 << 29)
        return flags == (3 << 29)

    def __call__(self, *args):
        if self._regular_calling_convention():
            # First arg is pointer to block, hide it from user
            return self._func(self._block_ptr, *args)

        error('Not implemented calling convention, block not called')
