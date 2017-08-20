#!python3

from objc_util import on_main_thread, c, parse_types, ObjCClass, sel, retain_global
from ctypes import CFUNCTYPE, c_void_p

SWIZZLED_SELECTOR_PREFIX = 'original'


method_exchangeImplementations = c.method_exchangeImplementations
method_exchangeImplementations.argtypes = [c_void_p, c_void_p]
method_exchangeImplementations.restype = c_void_p


@on_main_thread
def swizzle(cls_name, selector_name, fn):
    cls = ObjCClass(cls_name).ptr
    
    new_selector_name = SWIZZLED_SELECTOR_PREFIX + selector_name
    new_selector = sel(new_selector_name)

    if c.class_getInstanceMethod(cls, new_selector):
        print('Skipping swizzling, already responds to {} selector'.format(new_selector_name))
        return
        
    selector = sel(selector_name)
    method = c.class_getInstanceMethod(cls, selector)
    if not method:
        print('Failed to get {} instance method'.format(selector_name))
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
        print('Failed to add {} method'.format(new_selector_name))
        return

    new_method = c.class_getInstanceMethod(cls, new_selector)
    method_exchangeImplementations(method, new_method)

