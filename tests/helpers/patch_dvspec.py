# type: ignore
from pkgutil import iter_modules
from typing import Callable
import importlib

import dvspec


# Replace unimplemented methods from dvspec by methods from the test module
def replace_module_method(module, method_name_string: str, replacement_method: Callable) -> None:
    try:
        getattr(module, method_name_string)
        setattr(module, method_name_string, replacement_method)
    except AttributeError:
        pass


def replace_method_in_dvspec(method_name_string: str, replacement_method: Callable) -> None:
    for dvspec_submodule_info in iter_modules(dvspec.__path__):
        dvspec_submodule = importlib.import_module(dvspec.__name__ + '.' + dvspec_submodule_info.name)
        replace_module_method(dvspec_submodule, method_name_string, replacement_method)
