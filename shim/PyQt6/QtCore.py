from PyQt5.QtCore import *  # noqa: F401,F403
from ._compat import fix as _fix

_fix(globals())
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # в Qt6 включено всегда
