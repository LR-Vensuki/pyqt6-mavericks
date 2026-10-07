"""uic: Designer из Qt6 пишет Qt::AlignmentFlag::AlignCenter, а uic из PyQt5 ждёт Qt::AlignCenter."""
import io
import os
import re

from PyQt5 import uic as _uic
from PyQt5.uic import *  # noqa: F401,F403
from PyQt5.uic import objcreator as _objcreator

# uic из PyQt5 5.8 открывает плагины в режиме 'rU', которого нет с Python 3.11
_objcreator.open = lambda file, mode='r', *a, **k: open(file, mode.replace('U', ''), *a, **k)


def _short(m):
    return m.group(1) + re.sub(rb'(\w+)::\w+::(\w+)', rb'\1::\2', m.group(2))


def _read(uifile):
    if hasattr(uifile, 'read'):
        data = uifile.read()
    else:
        with open(uifile, 'rb') as f:
            data = f.read()
    if isinstance(data, str):
        data = data.encode('utf-8')
    return io.BytesIO(re.sub(rb'(<(?:enum|set)>)([^<]*)', _short, data))


def loadUi(uifile, baseinstance=None, package='', resource_suffix='_rc'):
    data = _read(uifile)
    if hasattr(uifile, 'read'):
        return _uic.loadUi(data, baseinstance, package, resource_suffix)
    from PyQt5.uic.Loader.loader import DynamicUILoader
    # как PyQt5.uic.loadUi, но относительные пути к иконкам — от папки .ui, а не от BytesIO
    loader = DynamicUILoader(package)
    set_base_dir = loader.wprops.set_base_dir
    loader.wprops.set_base_dir = lambda _: set_base_dir(os.path.dirname(str(uifile)))
    return loader.loadUi(data, baseinstance, resource_suffix)


def loadUiType(uifile, from_imports=False, resource_suffix='_rc', import_from='.'):
    return _uic.loadUiType(_read(uifile), from_imports, resource_suffix, import_from)
