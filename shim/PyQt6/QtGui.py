from PyQt5.QtGui import *  # noqa: F401,F403
from PyQt5.QtWidgets import (  # noqa: F401  в Qt6 эти классы переехали в QtGui
    QAction, QActionGroup, QFileSystemModel, QShortcut, QUndoCommand, QUndoGroup, QUndoStack)
from . import QtCore as _QtCore  # noqa: F401
from ._compat import fix as _fix

_fix(globals())
