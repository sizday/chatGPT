import os
import sys
import inspect
import re
import importlib

from pathlib import Path

from typing import Any


def import_action_impl_module(rel_action_class) -> Any:
    """Import module where action class is implemented"""
    # Suppose that package name == name of action class:
    pack_name = rel_action_class.__name__
    project_root = Path(os.path.basename(__file__)).resolve().parent
    pack_path = str(project_root / pack_name)
    mod_path = str(project_root / pack_name / pack_name)

    impinfo_path = project_root / pack_name / pack_name / f'Robin.Files.{pack_name}-Python.robin-impinfo'

    if pack_path not in sys.path:
        sys.path.append(pack_path)

    if mod_path not in sys.path:
        sys.path.append(mod_path)

    return importlib.import_module(f'{pack_name}.action')


def get_impl_module_globals(rel_action_class) -> dict:

    action_mod = import_action_impl_module(rel_action_class)

    globs = {
            attr_name: attr \
                for attr_name, attr in action_mod.__dict__.items() \
                    if not (attr_name.startswith('__') or attr_name.startswith('_'))
        }
    
    return globs
