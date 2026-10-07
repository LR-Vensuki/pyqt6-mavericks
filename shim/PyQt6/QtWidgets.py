from PyQt5.QtWidgets import *  # noqa: F401,F403
from . import QtGui as _QtGui  # noqa: F401  (заодно патчит события, шрифты и т.д.)
from ._compat import fix as _fix

_fix(globals())
