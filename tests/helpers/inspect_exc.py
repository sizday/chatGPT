"""Тест пропущенного импорта для исключений, которые не видны при синтаксической проверке"""
from .utils import \
    import_action_impl_module as _import_action_impl_module, \
    get_impl_module_globals as _get_impl_module_globals

import inspect

import re

EXC_USAGE_PATTERN = r'\braise\b[\s]*([^\s\(]*)' # \b means "word boundary"

def inspect_undefined_exceptions(rel_action_class):
    impl_module = _import_action_impl_module(rel_action_class)
    mod_as_text = inspect.getsource(impl_module)
    found = re.findall(EXC_USAGE_PATTERN, mod_as_text)
    missed = []
    if found:
        # get globals
        globs = _get_impl_module_globals(rel_action_class)
        for exc_name in found:
            exc_cls = globs.get(exc_name)
            if exc_cls is None:
                try:
                    # Фильтруем встроенный типы, которые не требуют явного импорта:
                    eval(exc_name)
                except NameError:
                    missed.append(exc_name)
    
    assert len(missed) == 0, \
        f'Missed import for exception: {",".join(missed)} in module {impl_module}'
            

