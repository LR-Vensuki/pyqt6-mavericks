"""PyQt6 -> PyQt5: шим для старых macOS, где Qt6 не запускается (ему нужна 10.14+).

Пишешь обычный PyQt6-код: здесь он работает поверх PyQt5 (Qt 5.8 на Mavericks),
на нормальной системе тот же код идёт на настоящем PyQt6 без правок.
"""
import importlib
import importlib.abc
import importlib.util
import sys
import warnings

# PyQt5-sip ворчит на модули, собранные старым sip (PyQt5 5.8) — это не ошибка
warnings.filterwarnings('ignore', 'sipPyTypeDict', DeprecationWarning)

import PyQt5  # noqa: F401  (нет PyQt5 -> сразу понятная ошибка)

try:
    import sip  # noqa: F401  мост для PyQt5 5.8 (см. shim/sip.py) — до любого PyQt5.QtXxx
except ImportError:
    pass

# Модули, которые в Qt6 выделились из других: имя -> (модуль PyQt5, какие имена взять)
_MOVED = {
    'QtSvgWidgets': ('QtSvg', ('QSvgWidget', 'QGraphicsSvgItem')),
    'QtOpenGLWidgets': ('QtWidgets', ('QOpenGLWidget',)),
}


class _Finder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """PyQt6.QtXxx, для которого тут нет своего файла, берётся из PyQt5.QtXxx."""

    def find_spec(self, name, path=None, target=None):
        pkg, _, mod = name.partition('.')
        if pkg == __name__ and mod and '.' not in mod:
            if importlib.util.find_spec('PyQt5.' + _MOVED.get(mod, (mod,))[0]):
                return importlib.util.spec_from_loader(name, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        from ._compat import fix
        mod = module.__name__.partition('.')[2]
        src_name, names = _MOVED.get(mod, (mod, None))
        src = importlib.import_module('PyQt5.' + src_name)
        for n in names or [n for n in dir(src) if not n.startswith('_')]:
            setattr(module, n, getattr(src, n))
        fix(vars(module))


sys.meta_path.append(_Finder())
