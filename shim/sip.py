"""Мост для PyQt5 < 5.11 (например 5.8 для Mavericks): он ищет модуль «sip»,
а под новый Python есть только PyQt5.sip из пакета PyQt5-sip. ABI у них один (v12),
отличается только имя капсулы с C-API — перевешиваем её под старое имя.
"""
import ctypes
import sys

_self = sys.modules[__name__]
from PyQt5 import sip as _sip  # noqa: E402  (регистрирует себя и как «sip» — ниже вернём мост)
from PyQt5.sip import *  # noqa: F401,F403,E402

_get = ctypes.pythonapi.PyCapsule_GetPointer
_get.restype, _get.argtypes = ctypes.c_void_p, [ctypes.py_object, ctypes.c_char_p]
_new = ctypes.pythonapi.PyCapsule_New
_new.restype, _new.argtypes = ctypes.py_object, [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
_NAME = ctypes.create_string_buffer(b'sip._C_API')  # строка должна жить, пока жива капсула
_C_API = _new(_get(_sip._C_API, b'PyQt5.sip._C_API'), _NAME, None)
sys.modules[__name__] = _self
