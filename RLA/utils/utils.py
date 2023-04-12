import functools
from typing import Callable
import yaml

import functools
import warnings
import platform
from RLA.const import *


def get_sys_type():
    systype = platform.system()
    if systype.find('Windows') != -1:
        return PLATFORM_TYPE.WIN
    elif systype.find('Linux') != -1:
        return PLATFORM_TYPE.LINUX
    else:
        return PLATFORM_TYPE.OTHER

def get_dir_seperator():
    sys_flag = get_sys_type()
    if sys_flag == PLATFORM_TYPE.WIN:
        return '\\'
    elif sys_flag == PLATFORM_TYPE.LINUX:
        return '/'
    elif sys_flag == PLATFORM_TYPE.OTHER:
        print("[WARN] unrecognizable system type: ", sys_flag, "use default dir seperator")
        return '/'
    else:
        raise NotImplementedError("[ERROR] undefined system flag", sys_flag)


def deprecated_alias(**aliases):
    def deco(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            rename_kwargs(f.__name__, kwargs, aliases)
            return f(*args, **kwargs)
        return wrapper
    return deco

def rename_kwargs(func_name, kwargs, aliases):
    for alias, new in aliases.items():
        if alias in kwargs:
            if new in kwargs:
                raise TypeError('{} received both {} and {}'.format(
                    func_name, alias, new))
            warnings.warn('{} is deprecated; use {}'.format(alias, new),
                          DeprecationWarning,
                          3)
            kwargs[new] = kwargs.pop(alias)


def load_yaml(path):
    fs = open(path, encoding="UTF-8")
    try:
        private_config = yaml.load(fs)
    except TypeError:
        private_config = yaml.safe_load(fs)
    return private_config

def optional_set(new_val, old_val):
    return new_val if new_val is not None else old_val